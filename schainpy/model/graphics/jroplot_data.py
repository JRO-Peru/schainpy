
import os
import time
import glob
import datetime
from multiprocessing import Process

import zmq
import numpy
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.ticker import FuncFormatter, LinearLocator, MultipleLocator

from schainpy.model.proc.jroproc_base import Operation
from schainpy.utils import log

jet_values = matplotlib.pyplot.get_cmap('jet', 100)(numpy.arange(100))[10:90]
blu_values = matplotlib.pyplot.get_cmap(
    'seismic_r', 20)(numpy.arange(20))[10:15]
ncmap = matplotlib.colors.LinearSegmentedColormap.from_list(
    'jro', numpy.vstack((blu_values, jet_values)))
matplotlib.pyplot.register_cmap(cmap=ncmap)

CMAPS = [plt.get_cmap(s) for s in ('jro', 'jet', 'viridis', 'plasma', 'inferno', 'Greys', 'seismic', 'bwr', 'coolwarm')]


def figpause(interval):
    backend = plt.rcParams['backend']
    if backend in matplotlib.rcsetup.interactive_bk:
        figManager = matplotlib._pylab_helpers.Gcf.get_active()
        if figManager is not None:
            canvas = figManager.canvas
            if canvas.figure.stale:
                canvas.draw()
            canvas.start_event_loop(interval)
            return

def popup(message):
    fig = plt.figure(figsize=(12, 9), facecolor='r')
    fig.text(0.5, 0.5, message, ha='center', va='center', size='20', weight='heavy', color='w')    
    fig.show()
    figpause(1000)



class PlotData(Operation, Process):
    '''
    Base class for Schain plotting operations
    '''

    CODE = 'Figure'
    colormap = 'jro'
    bgcolor = 'white'
    CONFLATE = False    
    __missing = 1E30

    __attrs__ = ['show', 'save', 'xmin', 'xmax', 'ymin', 'ymax', 'zmin', 'zmax',
                 'zlimits', 'xlabel', 'ylabel', 'xaxis','cb_label', 'title',
                 'colorbar', 'bgcolor', 'width', 'height', 'localtime', 'oneFigure',
                 'showprofile', 'decimation']

    def __init__(self, **kwargs):

        Operation.__init__(self, plot=True, **kwargs)
        Process.__init__(self)
        
        self.kwargs['code'] = self.CODE
        self.mp = False
        self.data = None
        self.isConfig = False
        self.figures = []
        self.axes = []
        self.cb_axes = []
        self.localtime = kwargs.pop('localtime', True)
        self.show = kwargs.get('show', True)
        self.save = kwargs.get('save', False)
        self.colormap = kwargs.get('colormap', self.colormap)
        self.colormap_coh = kwargs.get('colormap_coh', 'jet')
        self.colormap_phase = kwargs.get('colormap_phase', 'RdBu_r')
        self.colormaps = kwargs.get('colormaps', None)
        self.bgcolor = kwargs.get('bgcolor', self.bgcolor)
        self.showprofile = kwargs.get('showprofile', False)
        self.title = kwargs.get('wintitle', self.CODE.upper())
        self.cb_label = kwargs.get('cb_label', None)
        self.cb_labels = kwargs.get('cb_labels', None)
        self.xaxis = kwargs.get('xaxis', 'frequency')
        self.zmin = kwargs.get('zmin', None)
        self.zmax = kwargs.get('zmax', None)
        self.zlimits = kwargs.get('zlimits', None)
        self.xmin = kwargs.get('xmin', None)
        self.xmax = kwargs.get('xmax', None)
        self.xrange = kwargs.get('xrange', 24)
        self.ymin = kwargs.get('ymin', None)
        self.ymax = kwargs.get('ymax', None)
        self.xlabel = kwargs.get('xlabel', None)
        self.decimation = kwargs.get('decimation', None)
        self.showSNR = kwargs.get('showSNR', False)
        self.oneFigure = kwargs.get('oneFigure', True)
        self.width = kwargs.get('width', None)
        self.height = kwargs.get('height', None)
        self.colorbar = kwargs.get('colorbar', True)
        self.factors = kwargs.get('factors', [1, 1, 1, 1, 1, 1, 1, 1])
        self.titles = kwargs.get('titles', [])
        self.polar = False

    def __fmtTime(self, x, pos):
        '''
        '''

        return '{}'.format(self.getDateTime(x).strftime('%H:%M'))

    def __setup(self):
        '''
        Common setup for all figures, here figures and axes are created
        '''

        if self.CODE not in self.data:
            raise ValueError(log.error('Missing data for {}'.format(self.CODE),
                                       self.name))

        self.setup()

        self.time_label = 'LT' if self.localtime else 'UTC'
        if self.data.localtime:
            self.getDateTime = datetime.datetime.fromtimestamp
        else:
            self.getDateTime = datetime.datetime.utcfromtimestamp

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
            if self.show:
                fig.show()

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

        self.setup()

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
        raise(NotImplementedError, 'Implement this method in child class')

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
            xmin = self.min_time
        else:
            if self.xaxis is 'time':
                dt = self.getDateTime(self.min_time)
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
                dt = self.getDateTime(self.max_time)
                xmax = (dt.replace(hour=int(self.xmax), minute=59, second=59) -
                        datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=1)).total_seconds()
                if self.data.localtime:
                    xmax += time.timezone
            else:
                xmax = self.xmax

        ymin = self.ymin if self.ymin else numpy.nanmin(self.y)
        ymax = self.ymax if self.ymax else numpy.nanmax(self.y)

        Y = numpy.array([5, 10, 20, 50, 100, 200, 500, 1000, 2000])
        i = 1 if numpy.where(ymax-ymin < Y)[0][0] < 0 else numpy.where(ymax-ymin < Y)[0][0]
        ystep = Y[i] / 5

        for n, ax in enumerate(self.axes):
            if ax.firsttime:
                ax.set_facecolor(self.bgcolor)
                ax.yaxis.set_major_locator(MultipleLocator(ystep))
                if self.xaxis is 'time':
                    ax.xaxis.set_major_formatter(FuncFormatter(self.__fmtTime))
                    ax.xaxis.set_major_locator(LinearLocator(9))
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

            if not self.polar:
                ax.set_xlim(xmin, xmax)
                ax.set_ylim(ymin, ymax)
                ax.set_title('{} - {} {}'.format(
                    self.titles[n],
                    self.getDateTime(self.max_time).strftime('%H:%M:%S'),
                    self.time_label),
                    size=8)
            else:
                ax.set_title('{}'.format(self.titles[n]), size=8)
                ax.set_ylim(0, 90)
                ax.set_yticks(numpy.arange(0, 90, 20))
                ax.yaxis.labelpad = 40

    def __plot(self):
        '''
        '''
        log.success('Plotting', self.name)

        try:
            self.plot()
            self.format()
        except:
            log.warning('{} Plot could not be updated... check data'.format(self.CODE), self.name)

        for n, fig in enumerate(self.figures):
            if self.nrows == 0 or self.nplots == 0:
                log.warning('No data', self.name)
                fig.text(0.5, 0.5, 'No Data', fontsize='large', ha='center')
                fig.canvas.manager.set_window_title(self.CODE)
                continue

            fig.tight_layout()
            fig.canvas.manager.set_window_title('{} - {}'.format(self.title,
                                                                 self.getDateTime(self.max_time).strftime('%Y/%m/%d')))
            fig.canvas.draw()

            if self.save and self.data.ended:                
                channels = range(self.nrows)
                if self.oneFigure:
                    label = ''
                else:
                    label = '_{}'.format(channels[n])
                figname = os.path.join(
                    self.save,
                    '{}{}_{}.png'.format(
                        self.CODE,
                        label,
                        self.getDateTime(self.saveTime).strftime(
                            '%Y%m%d_%H%M%S'),                        
                    )
                )
                log.log('Saving figure: {}'.format(figname), self.name)
                fig.savefig(figname)

    def plot(self):
        '''
        '''
        raise(NotImplementedError, 'Implement this method in child class')

    def run(self):

        log.success('Starting', self.name)

        context = zmq.Context()
        receiver = context.socket(zmq.SUB)
        receiver.setsockopt(zmq.SUBSCRIBE, '')
        receiver.setsockopt(zmq.CONFLATE, self.CONFLATE)

        if 'server' in self.kwargs['parent']:
            receiver.connect(
                'ipc:///tmp/{}.plots'.format(self.kwargs['parent']['server']))
        else:
            receiver.connect("ipc:///tmp/zmq.plots")

        while True:
            try:
                self.data = receiver.recv_pyobj(flags=zmq.NOBLOCK)
                if self.data.localtime and self.localtime:
                    self.times = self.data.times
                elif self.data.localtime and not self.localtime:
                    self.times = self.data.times + time.timezone
                elif not self.data.localtime and self.localtime:
                    self.times = self.data.times - time.timezone
                else:
                    self.times = self.data.times

                self.min_time = self.times[0]
                self.max_time = self.times[-1]

                if self.isConfig is False:
                    self.__setup()
                    self.isConfig = True

                self.__plot()

            except zmq.Again as e:
                log.log('Waiting for data...')
                if self.data:
                    figpause(self.data.throttle)
                else:
                    time.sleep(2)

    def close(self):
        if self.data:
            self.__plot()


class PlotSpectraData(PlotData):
    '''
    Plot for Spectra data
    '''

    CODE = 'spc'
    colormap = 'jro'

    def setup(self):
        self.nplots = len(self.data.channels)
        self.ncols = int(numpy.sqrt(self.nplots) + 0.9)
        self.nrows = int((1.0 * self.nplots / self.ncols) + 0.9)
        self.width = 3.4 * self.ncols
        self.height = 3 * self.nrows
        self.cb_label = 'dB'
        if self.showprofile:
            self.width += 0.8 * self.ncols

        self.ylabel = 'Range [km]'

    def plot(self):
        if self.xaxis == "frequency":
            x = self.data.xrange[0]
            self.xlabel = "Frequency (kHz)"
        elif self.xaxis == "time":
            x = self.data.xrange[1]
            self.xlabel = "Time (ms)"
        else:
            x = self.data.xrange[2]
            self.xlabel = "Velocity (m/s)"

        if self.CODE == 'spc_mean':
            x = self.data.xrange[2]
            self.xlabel = "Velocity (m/s)"

        self.titles = []

        y = self.data.heights
        self.y = y
        z = self.data['spc']

        for n, ax in enumerate(self.axes):
            noise = self.data['noise'][n][-1]
            if self.CODE == 'spc_mean':
                mean = self.data['mean'][n][-1]
            if ax.firsttime:
                self.xmax = self.xmax if self.xmax else numpy.nanmax(x)
                self.xmin = self.xmin if self.xmin else -self.xmax
                self.zmin = self.zmin if self.zmin else numpy.nanmin(z)
                self.zmax = self.zmax if self.zmax else numpy.nanmax(z)
                ax.plt = ax.pcolormesh(x, y, z[n].T,
                                       vmin=self.zmin,
                                       vmax=self.zmax,
                                       cmap=plt.get_cmap(self.colormap)
                                       )

                if self.showprofile:
                    ax.plt_profile = self.pf_axes[n].plot(
                        self.data['rti'][n][-1], y)[0]
                    ax.plt_noise = self.pf_axes[n].plot(numpy.repeat(noise, len(y)), y,
                                                        color="k", linestyle="dashed", lw=1)[0]
                if self.CODE == 'spc_mean':
                    ax.plt_mean = ax.plot(mean, y, color='k')[0]
            else:
                ax.plt.set_array(z[n].T.ravel())
                if self.showprofile:
                    ax.plt_profile.set_data(self.data['rti'][n][-1], y)
                    ax.plt_noise.set_data(numpy.repeat(noise, len(y)), y)
                if self.CODE == 'spc_mean':
                    ax.plt_mean.set_data(mean, y)

            self.titles.append('CH {}: {:3.2f}dB'.format(n, noise))
            self.saveTime = self.max_time


class PlotCrossSpectraData(PlotData):

    CODE = 'cspc'
    zmin_coh = None
    zmax_coh = None
    zmin_phase = None
    zmax_phase = None

    def setup(self):

        self.ncols = 4
        self.nrows = len(self.data.pairs)
        self.nplots = self.nrows * 4
        self.width = 3.4 * self.ncols
        self.height = 3 * self.nrows
        self.ylabel = 'Range [km]'
        self.showprofile = False

    def plot(self):

        if self.xaxis == "frequency":
            x = self.data.xrange[0]
            self.xlabel = "Frequency (kHz)"
        elif self.xaxis == "time":
            x = self.data.xrange[1]
            self.xlabel = "Time (ms)"
        else:
            x = self.data.xrange[2]
            self.xlabel = "Velocity (m/s)"

        self.titles = []

        y = self.data.heights
        self.y = y
        spc = self.data['spc']
        cspc = self.data['cspc']

        for n in range(self.nrows):
            noise = self.data['noise'][n][-1]
            pair = self.data.pairs[n]
            ax = self.axes[4 * n]
            ax3 = self.axes[4 * n + 3]
            if ax.firsttime:
                self.xmax = self.xmax if self.xmax else numpy.nanmax(x)
                self.xmin = self.xmin if self.xmin else -self.xmax
                self.zmin = self.zmin if self.zmin else numpy.nanmin(spc)
                self.zmax = self.zmax if self.zmax else numpy.nanmax(spc)
                ax.plt = ax.pcolormesh(x, y, spc[pair[0]].T,
                                       vmin=self.zmin,
                                       vmax=self.zmax,
                                       cmap=plt.get_cmap(self.colormap)
                                       )
            else:
                ax.plt.set_array(spc[pair[0]].T.ravel())
            self.titles.append('CH {}: {:3.2f}dB'.format(n, noise))

            ax = self.axes[4 * n + 1]
            if ax.firsttime:
                ax.plt = ax.pcolormesh(x, y, spc[pair[1]].T,
                                       vmin=self.zmin,
                                       vmax=self.zmax,
                                       cmap=plt.get_cmap(self.colormap)
                                       )
            else:
                ax.plt.set_array(spc[pair[1]].T.ravel())
            self.titles.append('CH {}: {:3.2f}dB'.format(n, noise))

            out = cspc[n] / numpy.sqrt(spc[pair[0]] * spc[pair[1]])
            coh = numpy.abs(out)
            phase = numpy.arctan2(out.imag, out.real) * 180 / numpy.pi

            ax = self.axes[4 * n + 2]
            if ax.firsttime:
                ax.plt = ax.pcolormesh(x, y, coh.T,
                                       vmin=0,
                                       vmax=1,
                                       cmap=plt.get_cmap(self.colormap_coh)
                                       )
            else:
                ax.plt.set_array(coh.T.ravel())
            self.titles.append(
                'Coherence Ch{} * Ch{}'.format(pair[0], pair[1]))

            ax = self.axes[4 * n + 3]
            if ax.firsttime:
                ax.plt = ax.pcolormesh(x, y, phase.T,
                                       vmin=-180,
                                       vmax=180,
                                       cmap=plt.get_cmap(self.colormap_phase)
                                       )
            else:
                ax.plt.set_array(phase.T.ravel())
            self.titles.append('Phase CH{} * CH{}'.format(pair[0], pair[1]))

            self.saveTime = self.max_time


class PlotSpectraMeanData(PlotSpectraData):
    '''
    Plot for Spectra and Mean
    '''
    CODE = 'spc_mean'
    colormap = 'jro'


class PlotRTIData(PlotData):
    '''
    Plot for RTI data
    '''

    CODE = 'rti'
    colormap = 'jro'

    def setup(self):
        self.xaxis = 'time'
        self.ncols = 1
        self.nrows = len(self.data.channels)
        self.nplots = len(self.data.channels)
        self.ylabel = 'Range [km]'
        self.cb_label = 'dB'
        self.titles = ['{} Channel {}'.format(
            self.CODE.upper(), x) for x in range(self.nrows)]

    def plot(self):
        self.x = self.times
        self.y = self.data.heights
        self.z = self.data[self.CODE]
        self.z = numpy.ma.masked_invalid(self.z)

        if self.decimation is None:
            x, y, z = self.fill_gaps(self.x, self.y, self.z)
        else:
            x, y, z = self.fill_gaps(*self.decimate())

        for n, ax in enumerate(self.axes):            
            self.zmin = self.zmin if self.zmin else numpy.min(self.z)
            self.zmax = self.zmax if self.zmax else numpy.max(self.z)
            if ax.firsttime:
                ax.plt = ax.pcolormesh(x, y, z[n].T,
                                       vmin=self.zmin,
                                       vmax=self.zmax,
                                       cmap=plt.get_cmap(self.colormap)
                                       )
                if self.showprofile:
                    ax.plot_profile = self.pf_axes[n].plot(
                        self.data['rti'][n][-1], self.y)[0]
                    ax.plot_noise = self.pf_axes[n].plot(numpy.repeat(self.data['noise'][n][-1], len(self.y)), self.y,
                                                         color="k", linestyle="dashed", lw=1)[0]
            else:
                ax.collections.remove(ax.collections[0])
                ax.plt = ax.pcolormesh(x, y, z[n].T,
                                       vmin=self.zmin,
                                       vmax=self.zmax,
                                       cmap=plt.get_cmap(self.colormap)
                                       )
                if self.showprofile:
                    ax.plot_profile.set_data(self.data['rti'][n][-1], self.y)
                    ax.plot_noise.set_data(numpy.repeat(
                        self.data['noise'][n][-1], len(self.y)), self.y)

        self.saveTime = self.min_time


class PlotCOHData(PlotRTIData):
    '''
    Plot for Coherence data
    '''

    CODE = 'coh'

    def setup(self):
        self.xaxis = 'time'
        self.ncols = 1
        self.nrows = len(self.data.pairs)
        self.nplots = len(self.data.pairs)
        self.ylabel = 'Range [km]'
        if self.CODE == 'coh':
            self.cb_label = ''
            self.titles = [
                'Coherence Map Ch{} * Ch{}'.format(x[0], x[1]) for x in self.data.pairs]
        else:
            self.cb_label = 'Degrees'
            self.titles = [
                'Phase Map Ch{} * Ch{}'.format(x[0], x[1]) for x in self.data.pairs]


class PlotPHASEData(PlotCOHData):
    '''
    Plot for Phase map data
    '''

    CODE = 'phase'
    colormap = 'seismic'


class PlotNoiseData(PlotData):
    '''
    Plot for noise 
    '''

    CODE = 'noise'

    def setup(self):
        self.xaxis = 'time'
        self.ncols = 1
        self.nrows = 1
        self.nplots = 1
        self.ylabel = 'Intensity [dB]'
        self.titles = ['Noise']
        self.colorbar = False

    def plot(self):

        x = self.times
        xmin = self.min_time
        xmax = xmin + self.xrange * 60 * 60
        Y = self.data[self.CODE]

        if self.axes[0].firsttime:
            for ch in self.data.channels:
                y = Y[ch]
                self.axes[0].plot(x, y, lw=1, label='Ch{}'.format(ch))
            plt.legend()
        else:
            for ch in self.data.channels:
                y = Y[ch]
                self.axes[0].lines[ch].set_data(x, y)

        self.ymin = numpy.nanmin(Y) - 5
        self.ymax = numpy.nanmax(Y) + 5
        self.saveTime = self.min_time


class PlotSNRData(PlotRTIData):
    '''
    Plot for SNR Data
    '''

    CODE = 'snr'
    colormap = 'jet'


class PlotDOPData(PlotRTIData):
    '''
    Plot for DOPPLER Data
    '''

    CODE = 'dop'
    colormap = 'jet'


class PlotSkyMapData(PlotData):
    '''
    Plot for meteors detection data
    '''

    CODE = 'param'

    def setup(self):

        self.ncols = 1
        self.nrows = 1
        self.width = 7.2
        self.height = 7.2
        self.nplots = 1
        self.xlabel = 'Zonal Zenith Angle (deg)'
        self.ylabel = 'Meridional Zenith Angle (deg)'
        self.polar = True
        self.ymin = -180
        self.ymax = 180
        self.colorbar = False

    def plot(self):

        arrayParameters = numpy.concatenate(self.data['param'])
        error = arrayParameters[:, -1]
        indValid = numpy.where(error == 0)[0]
        finalMeteor = arrayParameters[indValid, :]
        finalAzimuth = finalMeteor[:, 3]
        finalZenith = finalMeteor[:, 4]

        x = finalAzimuth * numpy.pi / 180
        y = finalZenith

        ax = self.axes[0]

        if ax.firsttime:
            ax.plot = ax.plot(x, y, 'bo', markersize=5)[0]
        else:
            ax.plot.set_data(x, y)

        dt1 = self.getDateTime(self.min_time).strftime('%y/%m/%d %H:%M:%S')
        dt2 = self.getDateTime(self.max_time).strftime('%y/%m/%d %H:%M:%S')
        title = 'Meteor Detection Sky Map\n %s - %s \n Number of events: %5.0f\n' % (dt1,
                                                                                     dt2,
                                                                                     len(x))
        self.titles[0] = title
        self.saveTime = self.max_time


class PlotParamData(PlotRTIData):
    '''
    Plot for data_param object
    '''

    CODE = 'param'
    colormap = 'seismic'

    def setup(self):
        self.xaxis = 'time'
        self.ncols = 1
        self.nrows = self.data.shape(self.CODE)[0]
        self.nplots = self.nrows
        if self.showSNR:
            self.nrows += 1
            self.nplots += 1

        self.ylabel = 'Height [km]'
        if not self.titles:
            self.titles = self.data.parameters \
                if self.data.parameters else ['Param {}'.format(x) for x in xrange(self.nrows)]
            if self.showSNR:
                self.titles.append('SNR')

    def plot(self):
        self.data.normalize_heights()
        self.x = self.times
        self.y = self.data.heights
        if self.showSNR:
            self.z = numpy.concatenate(
                (self.data[self.CODE], self.data['snr'])
            )
        else:
            self.z = self.data[self.CODE]

        self.z = numpy.ma.masked_invalid(self.z)

        if self.decimation is None:
            x, y, z = self.fill_gaps(self.x, self.y, self.z)
        else:
            x, y, z = self.fill_gaps(*self.decimate())

        for n, ax in enumerate(self.axes):
            
            self.zmax = self.zmax if self.zmax is not None else numpy.max(
                self.z[n])
            self.zmin = self.zmin if self.zmin is not None else numpy.min(
                self.z[n])

            if ax.firsttime:
                if self.zlimits is not None:
                    self.zmin, self.zmax = self.zlimits[n]

                ax.plt = ax.pcolormesh(x, y, z[n].T * self.factors[n],
                                       vmin=self.zmin,
                                       vmax=self.zmax,
                                       cmap=self.cmaps[n]
                                       )
            else:
                if self.zlimits is not None:
                    self.zmin, self.zmax = self.zlimits[n]
                ax.collections.remove(ax.collections[0])
                ax.plt = ax.pcolormesh(x, y, z[n].T * self.factors[n],
                                       vmin=self.zmin,
                                       vmax=self.zmax,
                                       cmap=self.cmaps[n]
                                       )

        self.saveTime = self.min_time


class PlotOutputData(PlotParamData):
    '''
    Plot data_output object
    '''

    CODE = 'output'
    colormap = 'seismic'
