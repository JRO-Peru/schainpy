# Copyright (c) 2012-2020 Jicamarca Radio Observatory
# All rights reserved.
#
# Distributed under the terms of the BSD 3-clause license.
"""Base class to create plot operations

"""

import os
import sys
import zmq
import time
import numpy
import datetime
from collections import deque
from functools import wraps
from threading import Thread
import matplotlib

if 'BACKEND' in os.environ:
    matplotlib.use(os.environ['BACKEND'])
elif 'linux' in sys.platform:
    matplotlib.use("TkAgg")
elif 'darwin' in sys.platform:
    matplotlib.use('MacOSX')
else:
    from schainpy.utils import log
    log.warning('Using default Backend="Agg"', 'INFO')
    matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.ticker import FuncFormatter, LinearLocator, MultipleLocator

from schainpy.model.data.jrodata import PlotterData
from schainpy.model.proc.jroproc_base import ProcessingUnit, Operation, MPDecorator
from schainpy.utils import log

jet_values = matplotlib.pyplot.get_cmap('jet', 100)(numpy.arange(100))[10:90]
blu_values = matplotlib.pyplot.get_cmap(
    'seismic_r', 20)(numpy.arange(20))[10:15]
ncmap = matplotlib.colors.LinearSegmentedColormap.from_list(
    'jro', numpy.vstack((blu_values, jet_values)))
matplotlib.pyplot.register_cmap(cmap=ncmap)

CMAPS = [plt.get_cmap(s) for s in ('jro', 'jet', 'viridis',
                                   'plasma', 'inferno', 'Greys', 'seismic', 'bwr', 'coolwarm')]

EARTH_RADIUS = 6.3710e3

def ll2xy(lat1, lon1, lat2, lon2):

    p = 0.017453292519943295
    a = 0.5 - numpy.cos((lat2 - lat1) * p)/2 + numpy.cos(lat1 * p) * \
        numpy.cos(lat2 * p) * (1 - numpy.cos((lon2 - lon1) * p)) / 2
    r = 12742 * numpy.arcsin(numpy.sqrt(a))
    theta = numpy.arctan2(numpy.sin((lon2-lon1)*p)*numpy.cos(lat2*p), numpy.cos(lat1*p)
                          * numpy.sin(lat2*p)-numpy.sin(lat1*p)*numpy.cos(lat2*p)*numpy.cos((lon2-lon1)*p))
    theta = -theta + numpy.pi/2
    return r*numpy.cos(theta), r*numpy.sin(theta)


def km2deg(km):
    '''
    Convert distance in km to degrees
    '''

    return numpy.rad2deg(km/EARTH_RADIUS)


def figpause(interval):
    backend = plt.rcParams['backend']
    if backend in matplotlib.rcsetup.interactive_bk:
        figManager = matplotlib._pylab_helpers.Gcf.get_active()
        if figManager is not None:
            canvas = figManager.canvas
            if canvas.figure.stale:
                canvas.draw()
            try:
                canvas.start_event_loop(interval)
            except:
                pass
            return

def popup(message):
    '''
    '''

    fig = plt.figure(figsize=(12, 8), facecolor='r')
    text = '\n'.join([s.strip() for s in message.split(':')])
    fig.text(0.01, 0.5, text, ha='left', va='center',
             size='20', weight='heavy', color='w')
    fig.show()
    figpause(1000)


class Throttle(object):
    '''
    Decorator that prevents a function from being called more than once every
    time period.
    To create a function that cannot be called more than once a minute, but
    will sleep until it can be called:
    @Throttle(minutes=1)
    def foo():
      pass

    for i in range(10):
      foo()
      print "This function has run %s times." % i
    '''

    def __init__(self, seconds=0, minutes=0, hours=0):
        self.throttle_period = datetime.timedelta(
            seconds=seconds, minutes=minutes, hours=hours
        )

        self.time_of_last_call = datetime.datetime.min

    def __call__(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            coerce = kwargs.pop('coerce', None)
            if coerce:
                self.time_of_last_call = datetime.datetime.now()
                return fn(*args, **kwargs)
            else:
                now = datetime.datetime.now()
                time_since_last_call = now - self.time_of_last_call
                time_left = self.throttle_period - time_since_last_call

                if time_left > datetime.timedelta(seconds=0):
                    return

            self.time_of_last_call = datetime.datetime.now()
            return fn(*args, **kwargs)

        return wrapper

def apply_throttle(value):

    @Throttle(seconds=value)
    def fnThrottled(fn):
        fn()

    return fnThrottled


@MPDecorator
class Plot(Operation):
    """Base class for Schain plotting operations

    This class should never be use directtly you must subclass a new operation,
    children classes must be defined as follow:

    ExamplePlot(Plot):

        CODE = 'code'
        colormap = 'jet'
        plot_type = 'pcolor' # options are ('pcolor', 'pcolorbuffer', 'scatter', 'scatterbuffer')

        def setup(self):
            pass

        def plot(self):
            pass

    """

    CODE = 'Figure'
    colormap = 'jet'
    bgcolor = 'white'
    buffering = True
    __missing = 1E30

    __attrs__ = ['show', 'save', 'ymin', 'ymax', 'zmin', 'zmax', 'title',
                 'showprofile']

    def __init__(self):

        Operation.__init__(self)
        self.isConfig = False
        self.isPlotConfig = False
        self.save_time = 0
        self.sender_time = 0
        self.data = None
        self.firsttime = True
        self.sender_queue = deque(maxlen=10)
        self.plots_adjust = {'left': 0.125, 'right': 0.9, 'bottom': 0.15, 'top': 0.9, 'wspace': 0.2, 'hspace': 0.2}

    def __fmtTime(self, x, pos):
        '''
        '''

        return '{}'.format(self.getDateTime(x).strftime('%H:%M'))

    def __setup(self, **kwargs):
        '''
        Initialize variables
        '''

        self.figures = []
        self.axes = []
        self.cb_axes = []
        self.localtime = kwargs.pop('localtime', True)
        self.show = kwargs.get('show', True)
        self.save = kwargs.get('save', False)
        self.save_period = kwargs.get('save_period', 0)
        self.colormap = kwargs.get('colormap', self.colormap)
        self.colormap_coh = kwargs.get('colormap_coh', 'jet')
        self.colormap_phase = kwargs.get('colormap_phase', 'RdBu_r')
        self.colormaps = kwargs.get('colormaps', None)
        self.bgcolor = kwargs.get('bgcolor', self.bgcolor)
        self.showprofile = kwargs.get('showprofile', False)
        self.title = kwargs.get('wintitle', self.CODE.upper())
        self.cb_label = kwargs.get('cb_label', None)
        self.cb_labels = kwargs.get('cb_labels', None)
        self.labels = kwargs.get('labels', None)
        self.xaxis = kwargs.get('xaxis', 'frequency')
        self.zmin = kwargs.get('zmin', None)
        self.zmax = kwargs.get('zmax', None)
        self.zlimits = kwargs.get('zlimits', None)
        self.xmin = kwargs.get('xmin', None)
        self.xmax = kwargs.get('xmax', None)
        self.xrange = kwargs.get('xrange', 12)
        self.xscale = kwargs.get('xscale', None)
        self.ymin = kwargs.get('ymin', None)
        self.ymax = kwargs.get('ymax', None)
        self.yscale = kwargs.get('yscale', None)
        self.xlabel = kwargs.get('xlabel', None)
        self.attr_time = kwargs.get('attr_time', 'utctime')
        self.attr_data = kwargs.get('attr_data', 'data_param')
        self.decimation = kwargs.get('decimation', None)
        self.showSNR = kwargs.get('showSNR', False)
        self.oneFigure = kwargs.get('oneFigure', True)
        self.width = kwargs.get('width', None)
        self.height = kwargs.get('height', None)
        self.colorbar = kwargs.get('colorbar', True)
        self.factors = kwargs.get('factors', [1, 1, 1, 1, 1, 1, 1, 1])
        self.channels = kwargs.get('channels', None)
        self.titles = kwargs.get('titles', [])
        self.polar = False
        self.type = kwargs.get('type', 'iq')
        self.grid = kwargs.get('grid', False)
        self.pause = kwargs.get('pause', False)
        self.save_code = kwargs.get('save_code', self.CODE)
        self.throttle = kwargs.get('throttle', 0)
        self.exp_code = kwargs.get('exp_code', None)
        self.server = kwargs.get('server', False)
        self.sender_period = kwargs.get('sender_period', 60)
        self.tag = kwargs.get('tag', '')
        self.height_index = kwargs.get('height_index', None)
        self.__throttle_plot = apply_throttle(self.throttle)
        code = self.attr_data if self.attr_data else self.CODE
        self.data = PlotterData(self.CODE, self.exp_code, self.localtime)
        
        if self.server:
            if not self.server.startswith('tcp://'):
                self.server = 'tcp://{}'.format(self.server)
            log.success(
                'Sending to server: {}'.format(self.server),
                self.name
            )

    def __setup_plot(self):
        '''
        Common setup for all figures, here figures and axes are created
        '''

        self.setup()

        self.time_label = 'LT' if self.localtime else 'UTC'        

        if self.width is None:
            self.width = 8

        self.figures = []
        self.axes = []
        self.cb_axes = []
        self.pf_axes = []
        self.cmaps = []

        size = '15%' if self.ncols == 1 else '30%'
        pad = '4%' if self.ncols == 1 else '8%'

        if self.oneFigure:
            if self.height is None:
                self.height = 1.4 * self.nrows + 1
            fig = plt.figure(figsize=(self.width, self.height),
                             edgecolor='k',
                             facecolor='w')
            self.figures.append(fig)
            for n in range(self.nplots):
                ax = fig.add_subplot(self.nrows, self.ncols,
                                     n + 1, polar=self.polar)
                ax.tick_params(labelsize=8)
                ax.firsttime = True
                ax.index = 0
                ax.press = None
                self.axes.append(ax)
                if self.showprofile:
                    cax = self.__add_axes(ax, size=size, pad=pad)
                    cax.tick_params(labelsize=8)
                    self.pf_axes.append(cax)
        else:
            if self.height is None:
                self.height = 3
            for n in range(self.nplots):
                fig = plt.figure(figsize=(self.width, self.height),
                                 edgecolor='k',
                                 facecolor='w')
                ax = fig.add_subplot(1, 1, 1, polar=self.polar)
                ax.tick_params(labelsize=8)
                ax.firsttime = True
                ax.index = 0
                ax.press = None
                self.figures.append(fig)
                self.axes.append(ax)
                if self.showprofile:
                    cax = self.__add_axes(ax, size=size, pad=pad)
                    cax.tick_params(labelsize=8)
                    self.pf_axes.append(cax)

        for n in range(self.nrows):
            if self.colormaps is not None:
                cmap = plt.get_cmap(self.colormaps[n])
            else:
                cmap = plt.get_cmap(self.colormap)
            cmap.set_bad(self.bgcolor, 1.)
            self.cmaps.append(cmap)

    def __add_axes(self, ax, size='30%', pad='8%'):
        '''
        Add new axes to the given figure
        '''
        divider = make_axes_locatable(ax)
        nax = divider.new_horizontal(size=size, pad=pad)
        ax.figure.add_axes(nax)
        return nax

    def fill_gaps(self, x_buffer, y_buffer, z_buffer):
        '''
        Create a masked array for missing data
        '''
        if x_buffer.shape[0] < 2:
            return x_buffer, y_buffer, z_buffer

        deltas = x_buffer[1:] - x_buffer[0:-1]
        x_median = numpy.median(deltas)

        index = numpy.where(deltas > 5 * x_median)

        if len(index[0]) != 0:
            z_buffer[::, index[0], ::] = self.__missing
            z_buffer = numpy.ma.masked_inside(z_buffer,
                                              0.99 * self.__missing,
                                              1.01 * self.__missing)

        return x_buffer, y_buffer, z_buffer

    def decimate(self):

        # dx = int(len(self.x)/self.__MAXNUMX) + 1
        dy = int(len(self.y) / self.decimation) + 1

        # x = self.x[::dx]
        x = self.x
        y = self.y[::dy]
        z = self.z[::, ::, ::dy]

        return x, y, z

    def format(self):
        '''
        Set min and max values, labels, ticks and titles
        '''
            
        for n, ax in enumerate(self.axes):
            if ax.firsttime:
                if self.xaxis != 'time':
                    xmin = self.xmin
                    xmax = self.xmax
                else:
                    xmin = self.tmin
                    xmax = self.tmin + self.xrange*60*60
                    ax.xaxis.set_major_formatter(FuncFormatter(self.__fmtTime))
                    ax.xaxis.set_major_locator(LinearLocator(9))
                ymin = self.ymin if self.ymin is not None else numpy.nanmin(self.y[numpy.isfinite(self.y)])
                ymax = self.ymax if self.ymax is not None else numpy.nanmax(self.y[numpy.isfinite(self.y)])
                ax.set_facecolor(self.bgcolor)
                if self.xscale:
                    ax.xaxis.set_major_formatter(FuncFormatter(
                        lambda x, pos: '{0:g}'.format(x*self.xscale)))
                if self.yscale:
                    ax.yaxis.set_major_formatter(FuncFormatter(
                        lambda x, pos: '{0:g}'.format(x*self.yscale)))
                if self.xlabel is not None:
                    ax.set_xlabel(self.xlabel)
                if self.ylabel is not None:
                    ax.set_ylabel(self.ylabel)
                if self.showprofile:
                    self.pf_axes[n].set_ylim(ymin, ymax)
                    self.pf_axes[n].set_xlim(self.zmin, self.zmax)
                    self.pf_axes[n].set_xlabel('dB')
                    self.pf_axes[n].grid(b=True, axis='x')
                    [tick.set_visible(False)
                     for tick in self.pf_axes[n].get_yticklabels()]
                if self.colorbar:
                    ax.cbar = plt.colorbar(
                        ax.plt, ax=ax, fraction=0.05, pad=0.02, aspect=10)
                    ax.cbar.ax.tick_params(labelsize=8)
                    ax.cbar.ax.press = None
                    if self.cb_label:
                        ax.cbar.set_label(self.cb_label, size=8)
                    elif self.cb_labels:
                        ax.cbar.set_label(self.cb_labels[n], size=8)
                else:
                    ax.cbar = None
                ax.set_xlim(xmin, xmax)
                ax.set_ylim(ymin, ymax)
                ax.firsttime = False
                if self.grid:
                    ax.grid(True)
            if not self.polar:
                ax.set_title('{} {} {}'.format(
                    self.titles[n],
                    self.getDateTime(self.data.max_time).strftime(
                        '%Y-%m-%d %H:%M:%S'),
                    self.time_label),
                    size=8)
            else:
                ax.set_title('{}'.format(self.titles[n]), size=8)
                ax.set_ylim(0, 90)
                ax.set_yticks(numpy.arange(0, 90, 20))
                ax.yaxis.labelpad = 40

        if self.firsttime:
            for n, fig in enumerate(self.figures):
                fig.subplots_adjust(**self.plots_adjust)
            self.firsttime = False

    def clear_figures(self):
        '''
        Reset axes for redraw plots
        '''

        for ax in self.axes+self.pf_axes+self.cb_axes:
            ax.clear()
            ax.firsttime = True
            if hasattr(ax, 'cbar') and ax.cbar:
                ax.cbar.remove()

    def __plot(self):
        '''
        Main function to plot, format and save figures
        '''

        self.plot()
        self.format()
        
        for n, fig in enumerate(self.figures):
            if self.nrows == 0 or self.nplots == 0:
                log.warning('No data', self.name)
                fig.text(0.5, 0.5, 'No Data', fontsize='large', ha='center')
                fig.canvas.manager.set_window_title(self.CODE)
                continue
            
            fig.canvas.manager.set_window_title('{} - {}'.format(self.title,
                                                                 self.getDateTime(self.data.max_time).strftime('%Y/%m/%d')))
            fig.canvas.draw()
            if self.show:
                fig.show()
                figpause(0.01)

            if self.save:
                self.save_figure(n)
        
        if self.server:
            self.send_to_server()

    def __update(self, dataOut, timestamp):
        '''
        '''

        metadata = {
            'yrange': dataOut.heightList,
            'interval': dataOut.timeInterval,
            'channels': dataOut.channelList
        }
        
        data, meta = self.update(dataOut)
        metadata.update(meta)
        self.data.update(data, timestamp, metadata)
    
    def save_figure(self, n):
        '''
        '''

        if (self.data.max_time - self.save_time) <= self.save_period:
            return

        self.save_time = self.data.max_time

        fig = self.figures[n]

        figname = os.path.join(
            self.save,
            self.save_code,
            '{}_{}.png'.format(                
                self.save_code,
                self.getDateTime(self.data.max_time).strftime(
                    '%Y%m%d_%H%M%S'
                    ),
                )
            )
        log.log('Saving figure: {}'.format(figname), self.name)
        if not os.path.isdir(os.path.dirname(figname)):
            os.makedirs(os.path.dirname(figname))
        fig.savefig(figname)

        if self.throttle == 0:
            figname = os.path.join(
                self.save,
                '{}_{}.png'.format(
                    self.save_code,
                    self.getDateTime(self.data.min_time).strftime(
                        '%Y%m%d'
                        ),
                    )
                )
            fig.savefig(figname)

    def send_to_server(self):
        '''
        '''

        if self.exp_code == None:
            log.warning('Missing `exp_code` skipping sending to server...')
        
        last_time = self.data.max_time
        interval = last_time - self.sender_time
        if interval < self.sender_period:
            return

        self.sender_time = last_time
        
        attrs = ['titles', 'zmin', 'zmax', 'tag', 'ymin', 'ymax']
        for attr in attrs:
            value = getattr(self, attr)
            if value:
                if isinstance(value, (numpy.float32, numpy.float64)):
                    value = round(float(value), 2)
                self.data.meta[attr] = value
        if self.colormap == 'jet':
            self.data.meta['colormap'] = 'Jet'
        elif 'RdBu' in self.colormap:
            self.data.meta['colormap'] = 'RdBu'
        else:
            self.data.meta['colormap'] = 'Viridis'
        self.data.meta['interval'] = int(interval)

        self.sender_queue.append(last_time)
        
        while True:
            try:
                tm = self.sender_queue.popleft()
            except IndexError:
                break
            msg = self.data.jsonify(tm, self.save_code, self.plot_type)
            self.socket.send_string(msg)
            socks = dict(self.poll.poll(2000))
            if socks.get(self.socket) == zmq.POLLIN:
                reply = self.socket.recv_string()
                if reply == 'ok':
                    log.log("Response from server ok", self.name)
                    time.sleep(0.1)
                    continue
                else:
                    log.warning(
                        "Malformed reply from server: {}".format(reply), self.name)
            else:
                log.warning(
                    "No response from server, retrying...", self.name)
            self.sender_queue.appendleft(tm)
            self.socket.setsockopt(zmq.LINGER, 0)
            self.socket.close()
            self.poll.unregister(self.socket)
            self.socket = self.context.socket(zmq.REQ)
            self.socket.connect(self.server)
            self.poll.register(self.socket, zmq.POLLIN)
            break

    def setup(self):
        '''
        This method should be implemented in the child class, the following
        attributes should be set:

        self.nrows: number of rows
        self.ncols: number of cols
        self.nplots: number of plots (channels or pairs)
        self.ylabel: label for Y axes
        self.titles: list of axes title 

        '''
        raise NotImplementedError

    def plot(self):
        '''
        Must be defined in the child class, the actual plotting method
        '''
        raise NotImplementedError

    def update(self, dataOut):
        '''
        Must be defined in the child class, update self.data with new data
        '''
        
        data = {
            self.CODE: getattr(dataOut, 'data_{}'.format(self.CODE))
        }
        meta = {}

        return data, meta
    
    def run(self, dataOut, **kwargs):
        '''
        Main plotting routine
        '''

        if self.isConfig is False:
            self.__setup(**kwargs)

            if self.localtime:
                self.getDateTime = datetime.datetime.fromtimestamp
            else:
                self.getDateTime = datetime.datetime.utcfromtimestamp

            self.data.setup()
            self.isConfig = True
            if self.server:
                self.context = zmq.Context()
                self.socket = self.context.socket(zmq.REQ)
                self.socket.connect(self.server)
                self.poll = zmq.Poller()
                self.poll.register(self.socket, zmq.POLLIN)

        tm = getattr(dataOut, self.attr_time)
        
        if self.data and 'time' in self.xaxis and (tm - self.tmin) >= self.xrange*60*60:
            self.save_time = tm
            self.__plot()
            self.tmin += self.xrange*60*60
            self.data.setup()
            self.clear_figures()

        self.__update(dataOut, tm)

        if self.isPlotConfig is False:
            self.__setup_plot()
            self.isPlotConfig = True
            if self.xaxis == 'time':
                dt = self.getDateTime(tm)
                if self.xmin is None:
                    self.tmin = tm
                    self.xmin = dt.hour    
                minutes = (self.xmin-int(self.xmin)) * 60
                seconds = (minutes - int(minutes)) * 60
                self.tmin = (dt.replace(hour=int(self.xmin), minute=int(minutes), second=int(seconds)) -
                        datetime.datetime(1970, 1, 1)).total_seconds()
                if self.localtime:
                    self.tmin += time.timezone

                if self.xmin is not None and self.xmax is not None:
                    self.xrange = self.xmax - self.xmin

        if self.throttle == 0:
            self.__plot()
        else:
            self.__throttle_plot(self.__plot)#, coerce=coerce)

    def close(self):

        if self.data and not self.data.flagNoData:
            self.save_time = self.data.max_time
            self.__plot()
        if self.data and not self.data.flagNoData and self.pause:
            figpause(10)

