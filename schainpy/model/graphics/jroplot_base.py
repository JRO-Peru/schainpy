
import os
import sys
import zmq
import time
import numpy
import datetime
from functools import wraps
from threading import Thread
import matplotlib

if 'BACKEND' in os.environ:
    matplotlib.use(os.environ['BACKEND'])
elif 'linux' in sys.platform:
    matplotlib.use("TkAgg")
elif 'darwin' in sys.platform:
    matplotlib.use('WxAgg')
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
    '''
    Base class for Schain plotting operations
    '''

    CODE = 'Figure'
    colormap = 'jet'
    bgcolor = 'white'
    __missing = 1E30

    __attrs__ = ['show', 'save', 'xmin', 'xmax', 'ymin', 'ymax', 'zmin', 'zmax',
                 'zlimits', 'xlabel', 'ylabel', 'xaxis', 'cb_label', 'title',
                 'colorbar', 'bgcolor', 'width', 'height', 'localtime', 'oneFigure',
                 'showprofile', 'decimation', 'pause']

    def __init__(self):

        Operation.__init__(self)
        self.isConfig = False
        self.isPlotConfig = False
        self.save_counter = 1
        self.sender_counter = 1
        self.data = None

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
        self.save_period = kwargs.get('save_period', 2)
        self.ftp = kwargs.get('ftp', False)
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
        self.xrange = kwargs.get('xrange', 24)
        self.xscale = kwargs.get('xscale', None)
        self.ymin = kwargs.get('ymin', None)
        self.ymax = kwargs.get('ymax', None)
        self.yscale = kwargs.get('yscale', None)
        self.xlabel = kwargs.get('xlabel', None)
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
        self.save_labels = kwargs.get('save_labels', None)
        self.realtime = kwargs.get('realtime', True)
        self.buffering = kwargs.get('buffering', True)
        self.throttle = kwargs.get('throttle', 2)
        self.exp_code = kwargs.get('exp_code', None)
        self.plot_server = kwargs.get('plot_server', False)
        self.sender_period = kwargs.get('sender_period', 2)
        self.__throttle_plot = apply_throttle(self.throttle)
        self.data = PlotterData(
            self.CODE, self.throttle, self.exp_code, self.buffering, snr=self.showSNR)
        
        if self.plot_server:
            if not self.plot_server.startswith('tcp://'):
                self.plot_server = 'tcp://{}'.format(self.plot_server)
            log.success(
                'Sending to server: {}'.format(self.plot_server),
                self.name
            )
        if 'plot_name' in kwargs:
            self.plot_name = kwargs['plot_name']

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
                
        for fig in self.figures:
            fig.canvas.mpl_connect('key_press_event', self.OnKeyPress)
            fig.canvas.mpl_connect('scroll_event', self.OnBtnScroll)
            fig.canvas.mpl_connect('button_press_event', self.onBtnPress)
            fig.canvas.mpl_connect('motion_notify_event', self.onMotion)
            fig.canvas.mpl_connect('button_release_event', self.onBtnRelease)

    def OnKeyPress(self, event):
        '''
        Event for pressing keys (up, down) change colormap
        '''
        ax = event.inaxes
        if ax in self.axes:
            if event.key == 'down':
                ax.index += 1
            elif event.key == 'up':
                ax.index -= 1
            if ax.index < 0:
                ax.index = len(CMAPS) - 1
            elif ax.index == len(CMAPS):
                ax.index = 0
            cmap = CMAPS[ax.index]
            ax.cbar.set_cmap(cmap)
            ax.cbar.draw_all()
            ax.plt.set_cmap(cmap)
            ax.cbar.patch.figure.canvas.draw()
            self.colormap = cmap.name

    def OnBtnScroll(self, event):
        '''
        Event for scrolling, scale figure
        '''
        cb_ax = event.inaxes
        if cb_ax in [ax.cbar.ax for ax in self.axes if ax.cbar]:
            ax = [ax for ax in self.axes if cb_ax == ax.cbar.ax][0]
            pt = ax.cbar.ax.bbox.get_points()[:, 1]
            nrm = ax.cbar.norm
            vmin, vmax, p0, p1, pS = (
                nrm.vmin, nrm.vmax, pt[0], pt[1], event.y)
            scale = 2 if event.step == 1 else 0.5
            point = vmin + (vmax - vmin) / (p1 - p0) * (pS - p0)
            ax.cbar.norm.vmin = point - scale * (point - vmin)
            ax.cbar.norm.vmax = point - scale * (point - vmax)
            ax.plt.set_norm(ax.cbar.norm)
            ax.cbar.draw_all()
            ax.cbar.patch.figure.canvas.draw()

    def onBtnPress(self, event):
        '''
        Event for mouse button press
        '''
        cb_ax = event.inaxes
        if cb_ax is None:
            return

        if cb_ax in [ax.cbar.ax for ax in self.axes if ax.cbar]:
            cb_ax.press = event.x, event.y
        else:
            cb_ax.press = None

    def onMotion(self, event):
        '''
        Event for move inside colorbar
        '''
        cb_ax = event.inaxes
        if cb_ax is None:
            return
        if cb_ax not in [ax.cbar.ax for ax in self.axes if ax.cbar]:
            return
        if cb_ax.press is None:
            return

        ax = [ax for ax in self.axes if cb_ax == ax.cbar.ax][0]
        xprev, yprev = cb_ax.press
        dx = event.x - xprev
        dy = event.y - yprev
        cb_ax.press = event.x, event.y
        scale = ax.cbar.norm.vmax - ax.cbar.norm.vmin
        perc = 0.03

        if event.button == 1:
            ax.cbar.norm.vmin -= (perc * scale) * numpy.sign(dy)
            ax.cbar.norm.vmax -= (perc * scale) * numpy.sign(dy)
        elif event.button == 3:
            ax.cbar.norm.vmin -= (perc * scale) * numpy.sign(dy)
            ax.cbar.norm.vmax += (perc * scale) * numpy.sign(dy)

        ax.cbar.draw_all()
        ax.plt.set_norm(ax.cbar.norm)
        ax.cbar.patch.figure.canvas.draw()

    def onBtnRelease(self, event):
        '''
        Event for mouse button release
        '''
        cb_ax = event.inaxes
        if cb_ax is not None:
            cb_ax.press = None

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

        if self.xmin is None:
            xmin = self.data.min_time
        else:
            if self.xaxis is 'time':
                dt = self.getDateTime(self.data.min_time)
                xmin = (dt.replace(hour=int(self.xmin), minute=0, second=0) -
                        datetime.datetime(1970, 1, 1)).total_seconds()
                if self.data.localtime:
                    xmin += time.timezone
            else:
                xmin = self.xmin

        if self.xmax is None:
            xmax = xmin + self.xrange * 60 * 60
        else:
            if self.xaxis is 'time':
                dt = self.getDateTime(self.data.max_time)
                xmax = (dt.replace(hour=int(self.xmax), minute=59, second=59) -
                        datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=1)).total_seconds()
                if self.data.localtime:
                    xmax += time.timezone
            else:
                xmax = self.xmax
        
        ymin = self.ymin if self.ymin else numpy.nanmin(self.y)
        ymax = self.ymax if self.ymax else numpy.nanmax(self.y)
        #Y = numpy.array([1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000])
        
        #i = 1 if numpy.where(
        #    abs(ymax-ymin) <= Y)[0][0] < 0 else numpy.where(abs(ymax-ymin) <= Y)[0][0]
        #ystep = Y[i] / 10.
        dig = int(numpy.log10(ymax))
        if dig == 0:
            digD = len(str(ymax)) - 2
            ydec = ymax*(10**digD)

            dig = int(numpy.log10(ydec))
            ystep = ((ydec + (10**(dig)))//10**(dig))*(10**(dig))
            ystep = ystep/5
            ystep = ystep/(10**digD)

        else:        
            ystep = ((ymax + (10**(dig)))//10**(dig))*(10**(dig))
            ystep = ystep/5
            
        if self.xaxis is not 'time':
            
            dig = int(numpy.log10(xmax))
            
            if dig <= 0:
                digD = len(str(xmax)) - 2
                xdec = xmax*(10**digD)

                dig = int(numpy.log10(xdec))
                xstep = ((xdec + (10**(dig)))//10**(dig))*(10**(dig))
                xstep = xstep*0.5
                xstep = xstep/(10**digD)
                
            else:        
                xstep = ((xmax + (10**(dig)))//10**(dig))*(10**(dig))
                xstep = xstep/5
            
        for n, ax in enumerate(self.axes):
            if ax.firsttime:
                ax.set_facecolor(self.bgcolor)
                ax.yaxis.set_major_locator(MultipleLocator(ystep))
                if self.xscale:
                    ax.xaxis.set_major_formatter(FuncFormatter(
                        lambda x, pos: '{0:g}'.format(x*self.xscale)))
                if self.xscale:
                    ax.yaxis.set_major_formatter(FuncFormatter(
                        lambda x, pos: '{0:g}'.format(x*self.yscale)))
                if self.xaxis is 'time':
                    ax.xaxis.set_major_formatter(FuncFormatter(self.__fmtTime))
                    ax.xaxis.set_major_locator(LinearLocator(9))
                else:
                    ax.xaxis.set_major_locator(MultipleLocator(xstep))
                if self.xlabel is not None:
                    ax.set_xlabel(self.xlabel)
                ax.set_ylabel(self.ylabel)
                ax.firsttime = False
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
            if self.grid:
                ax.grid(True)

            if not self.polar:
                ax.set_xlim(xmin, xmax)
                ax.set_ylim(ymin, ymax)
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

    def clear_figures(self):
        '''
        Reset axes for redraw plots
        '''

        for ax in self.axes:
            ax.clear()
            ax.firsttime = True
            if ax.cbar:
                ax.cbar.remove()

    def __plot(self):
        '''
        Main function to plot, format and save figures
        '''

        try:
            self.plot()
            self.format()
        except Exception as e:
           log.warning('{} Plot could not be updated... check data'.format(
               self.CODE), self.name)
           log.error(str(e), '')
           return

        for n, fig in enumerate(self.figures):
            if self.nrows == 0 or self.nplots == 0:
                log.warning('No data', self.name)
                fig.text(0.5, 0.5, 'No Data', fontsize='large', ha='center')
                fig.canvas.manager.set_window_title(self.CODE)
                continue

            fig.tight_layout()
            fig.canvas.manager.set_window_title('{} - {}'.format(self.title,
                                                                 self.getDateTime(self.data.max_time).strftime('%Y/%m/%d')))
            fig.canvas.draw()
            if self.show:
                fig.show()
                figpause(0.1)

            if self.save:
                self.save_figure(n)
        
        if self.plot_server:
            self.send_to_server()
            # t = Thread(target=self.send_to_server)
            # t.start()

    def save_figure(self, n):
        '''
        '''

        if self.save_counter < self.save_period:
            self.save_counter += 1
            return

        self.save_counter = 1

        fig = self.figures[n]

        if self.save_labels:
            labels = self.save_labels
        else:
            labels = list(range(self.nrows))

        if self.oneFigure:
            label = ''
        else:
            label = '-{}'.format(labels[n])
        figname = os.path.join(
            self.save,
            self.CODE,
            '{}{}_{}.png'.format(
                self.CODE,
                label,
                self.getDateTime(self.data.max_time).strftime(
                    '%Y%m%d_%H%M%S'
                    ),
                )
            )
        log.log('Saving figure: {}'.format(figname), self.name)
        if not os.path.isdir(os.path.dirname(figname)):
            os.makedirs(os.path.dirname(figname))
        fig.savefig(figname)

        if self.realtime:
            figname = os.path.join(
                self.save,
                '{}{}_{}.png'.format(
                    self.CODE,
                    label,
                    self.getDateTime(self.data.min_time).strftime(
                        '%Y%m%d'
                        ),
                    )
                )
            fig.savefig(figname)

    def send_to_server(self):
        '''
        '''

        if self.sender_counter < self.sender_period:
            self.sender_counter += 1

        self.sender_counter = 1
        self.data.meta['titles'] = self.titles
        retries = 2
        while True:
            self.socket.send_string(self.data.jsonify(self.plot_name, self.plot_type))
            socks = dict(self.poll.poll(5000))
            if socks.get(self.socket) == zmq.POLLIN:
                reply = self.socket.recv_string()
                if reply == 'ok':
                    log.log("Response from server ok", self.name)
                    break
                else:
                    log.warning(
                        "Malformed reply from server: {}".format(reply), self.name)

            else:
                log.warning(
                    "No response from server, retrying...", self.name)
            self.socket.setsockopt(zmq.LINGER, 0)
            self.socket.close()
            self.poll.unregister(self.socket)
            retries -= 1
            if retries == 0:
                log.error(
                    "Server seems to be offline, abandoning", self.name)
                self.socket = self.context.socket(zmq.REQ)
                self.socket.connect(self.plot_server)
                self.poll.register(self.socket, zmq.POLLIN)
                time.sleep(1)
                break
            self.socket = self.context.socket(zmq.REQ)
            self.socket.connect(self.plot_server)
            self.poll.register(self.socket, zmq.POLLIN)
            time.sleep(0.5)

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
        Must be defined in the child class
        '''
        raise NotImplementedError
    
    def run(self, dataOut, **kwargs):
        '''
        Main plotting routine
        '''
        
        if self.isConfig is False:
            self.__setup(**kwargs)
            if dataOut.type == 'Parameters':
                t = dataOut.utctimeInit
            else:
                t = dataOut.utctime            

            if dataOut.useLocalTime:
                self.getDateTime = datetime.datetime.fromtimestamp
                if not self.localtime:
                    t += time.timezone
            else:
                self.getDateTime = datetime.datetime.utcfromtimestamp
                if self.localtime:
                    t -= time.timezone
            
            if self.xmin is None:
                self.tmin = t
            else:
                self.tmin = (
                    self.getDateTime(t).replace(
                        hour=self.xmin, 
                        minute=0, 
                        second=0) - self.getDateTime(0)).total_seconds()

            self.data.setup()
            self.isConfig = True
            if self.plot_server:
                self.context = zmq.Context()
                self.socket = self.context.socket(zmq.REQ)
                self.socket.connect(self.plot_server)
                self.poll = zmq.Poller()
                self.poll.register(self.socket, zmq.POLLIN)

        if dataOut.type == 'Parameters':
            tm = dataOut.utctimeInit
        else:
            tm = dataOut.utctime

        if not dataOut.useLocalTime and self.localtime:
            tm -= time.timezone
        if dataOut.useLocalTime and not self.localtime:
            tm += time.timezone

        if self.xaxis is 'time' and self.data and (tm - self.tmin) >= self.xrange*60*60:    
            self.save_counter = self.save_period
            self.__plot()
            self.xmin += self.xrange
            if self.xmin >= 24:
                self.xmin -= 24
            self.tmin += self.xrange*60*60
            self.data.setup()
            self.clear_figures()

        self.data.update(dataOut, tm)

        if self.isPlotConfig is False:
            self.__setup_plot()
            self.isPlotConfig = True

        if self.realtime:
            self.__plot()
        else:
            self.__throttle_plot(self.__plot)#, coerce=coerce)

    def close(self):

        if self.data:
            self.save_counter = self.save_period
            self.__plot()
        if self.data and self.pause:
            figpause(10)

