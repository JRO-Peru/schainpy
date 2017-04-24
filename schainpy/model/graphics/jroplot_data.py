
import os
import zmq
import time
import numpy
import datetime
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.ticker import FuncFormatter, LinearLocator
from multiprocessing import Process

from schainpy.model.proc.jroproc_base import Operation

#plt.ion()

func = lambda x, pos: ('%s') %(datetime.datetime.utcfromtimestamp(x).strftime('%H:%M'))

d1970 = datetime.datetime(1970,1,1)

class PlotData(Operation, Process):

    CODE = 'Figure'
    colormap = 'jet'
    __MAXNUMX = 80
    __MAXNUMY = 80
    __missing = 1E30

    def __init__(self, **kwargs):

        Operation.__init__(self)
        Process.__init__(self)
        self.mp = False
        self.dataOut = None
        self.isConfig = False
        self.figure = None
        self.axes = []
        self.localtime = kwargs.pop('localtime', True)
        self.show = kwargs.get('show', True)
        self.save = kwargs.get('save', False)
        self.colormap = kwargs.get('colormap', self.colormap)
        self.showprofile = kwargs.get('showprofile', False)
        self.title = kwargs.get('wintitle', '')
        self.xaxis = kwargs.get('xaxis', 'time')
        self.zmin = kwargs.get('zmin', None)
        self.zmax = kwargs.get('zmax', None)
        self.xmin = kwargs.get('xmin', None)
        self.xmax = kwargs.get('xmax', None)
        self.xrange = kwargs.get('xrange', 24)
        self.ymin = kwargs.get('ymin', None)
        self.ymax = kwargs.get('ymax', None)

    def fill_gaps(self, x_buffer, y_buffer, z_buffer):

        if x_buffer.shape[0] < 2:
            return x_buffer, y_buffer, z_buffer

        deltas = x_buffer[1:] - x_buffer[0:-1]
        x_median = np.median(deltas)

        index = np.where(deltas > 5*x_median)

        if len(index[0]) != 0:
            z_buffer[::,index[0],::] = self.__missing
            z_buffer = np.ma.masked_inside(z_buffer,
                                           0.99*self.__missing,
                                           1.01*self.__missing)

        return x_buffer, y_buffer, z_buffer

    def decimate(self):

        dx = int(len(self.x)/self.__MAXNUMX) + 1
        dy = int(len(self.y)/self.__MAXNUMY) + 1

        x = self.x[::dx]
        y = self.y[::dy]
        z = self.z[::, ::dx, ::dy]

        return x, y, z

    def __plot(self):

        print 'plotting...{}'.format(self.CODE)

        self.plot()
        self.figure.suptitle('{} {}'.format(self.title, self.CODE.upper()))

        if self.save:
            figname = os.path.join(self.save, '{}_{}.png'.format(self.CODE,
                                                                 datetime.datetime.utcfromtimestamp(self.times[-1]).strftime('%y%m%d_%H%M%S')))
            print 'Saving figure: {}'.format(figname)
            self.figure.savefig(figname)

        self.figure.canvas.draw()

    def plot(self):

        print 'plotting...{}'.format(self.CODE.upper())
        return

    def run(self):

        print '[Starting] {}'.format(self.name)
        context = zmq.Context()
        receiver = context.socket(zmq.SUB)
        receiver.setsockopt(zmq.SUBSCRIBE, '')
        receiver.setsockopt(zmq.CONFLATE, True)
        receiver.connect("ipc:///tmp/zmq.plots")

        while True:
            try:
            #if True:
                self.data = receiver.recv_pyobj(flags=zmq.NOBLOCK)
                self.dataOut = self.data['dataOut']
                self.times = self.data['times']
                self.times.sort()
                self.min_time = self.times[0]
                self.max_time = self.times[-1]

                if self.isConfig is False:
                    self.setup()
                    self.isConfig = True

                self.__plot()

                if 'ENDED' in self.data:
                    #self.setup()
                    #self.__plot()
                    pass

            except zmq.Again as e:
                print 'Waiting for data...'
                plt.pause(5)
                #time.sleep(3)

    def close(self):
        if self.dataOut:
            self._plot()


class PlotSpectraData(PlotData):

    CODE = 'spc'
    colormap = 'jro'

    def setup(self):

        ncolspan = 1
        colspan = 1
        self.ncols = int(numpy.sqrt(self.dataOut.nChannels)+0.9)
        self.nrows = int(self.dataOut.nChannels*1./self.ncols + 0.9)
        self.width = 3.6*self.ncols
        self.height = 3.2*self.nrows
        if self.showprofile:
            ncolspan = 3
            colspan = 2
            self.width += 1.2*self.ncols

        self.ylabel = 'Range [Km]'
        self.titles = ['Channel {}'.format(x) for x in self.dataOut.channelList]

        if self.figure is None:
            self.figure = plt.figure(figsize=(self.width, self.height),
                                     edgecolor='k',
                                     facecolor='w')
        else:
            self.figure.clf()

        n = 0
        for y in range(self.nrows):
            for x in range(self.ncols):
                if n>=self.dataOut.nChannels:
                    break
                ax = plt.subplot2grid((self.nrows, self.ncols*ncolspan), (y, x*ncolspan), 1, colspan)
                if self.showprofile:
                    ax.ax_profile = plt.subplot2grid((self.nrows, self.ncols*ncolspan), (y, x*ncolspan+colspan), 1, 1)

                ax.firsttime = True
                self.axes.append(ax)
                n += 1

        self.figure.subplots_adjust(wspace=0.9, hspace=0.5)
        self.figure.show()

    def plot(self):

        if self.xaxis == "frequency":
            x = self.dataOut.getFreqRange(1)/1000.
            xlabel = "Frequency (kHz)"
        elif self.xaxis == "time":
            x = self.dataOut.getAcfRange(1)
            xlabel = "Time (ms)"
        else:
            x = self.dataOut.getVelRange(1)
            xlabel = "Velocity (m/s)"

        y = self.dataOut.getHeiRange()
        z = self.data[self.CODE]

        for n, ax in enumerate(self.axes):

            if ax.firsttime:
                self.xmax = self.xmax if self.xmax else np.nanmax(x)
                self.xmin = self.xmin if self.xmin else -self.xmax
                self.ymin = self.ymin if self.ymin else np.nanmin(y)
                self.ymax = self.ymax if self.ymax else np.nanmax(y)
                self.zmin = self.zmin if self.zmin else np.nanmin(z)
                self.zmax = self.zmax if self.zmax else np.nanmax(z)
                ax.plot = ax.pcolormesh(x, y, z[n].T,
                                        vmin=self.zmin,
                                        vmax=self.zmax,
                                        cmap=plt.get_cmap(self.colormap)
                                       )
                divider = make_axes_locatable(ax)
                cax = divider.new_horizontal(size='3%', pad=0.05)
                self.figure.add_axes(cax)
                plt.colorbar(ax.plot, cax)

                ax.set_xlim(self.xmin, self.xmax)
                ax.set_ylim(self.ymin, self.ymax)

                ax.xaxis.set_major_locator(LinearLocator(5))
                #ax.yaxis.set_major_locator(LinearLocator(4))

                ax.set_ylabel(self.ylabel)
                ax.set_xlabel(xlabel)

                ax.firsttime = False

                if self.showprofile:
                    ax.plot_profile= ax.ax_profile.plot(self.data['rti'][self.max_time][n], y)[0]
                    ax.ax_profile.set_xlim(self.zmin, self.zmax)
                    ax.ax_profile.set_ylim(self.ymin, self.ymax)
                    ax.ax_profile.set_xlabel('dB')
                    ax.ax_profile.grid(b=True, axis='x')
                    [tick.set_visible(False) for tick in ax.ax_profile.get_yticklabels()]
                    noise = 10*numpy.log10(self.data['rti'][self.max_time][n]/self.dataOut.normFactor)
                    ax.ax_profile.vlines(noise, self.ymin, self.ymax, colors="k", linestyle="dashed", lw=2)
            else:
                ax.plot.set_array(z[n].T.ravel())
                ax.set_title('{} {}'.format(self.titles[n],
                                            datetime.datetime.utcfromtimestamp(self.max_time).strftime('%y/%m/%d %H:%M:%S')),
                             size=8)
                if self.showprofile:
                    ax.plot_profile.set_data(self.data['rti'][self.max_time][n], y)


class PlotRTIData(PlotData):

    CODE = 'rti'
    colormap = 'jro'

    def setup(self):

        self.ncols = 1
        self.nrows = self.dataOut.nChannels
        self.width = 10
        self.height = 2.2*self.nrows
        self.ylabel = 'Range [Km]'
        self.titles = ['Channel {}'.format(x) for x in self.dataOut.channelList]

        if self.figure is None:
            self.figure = plt.figure(figsize=(self.width, self.height),
                                     edgecolor='k',
                                     facecolor='w')
        else:
            self.figure.clf()

        for n in range(self.nrows):
            ax = self.figure.add_subplot(self.nrows, self.ncols, n+1)
            ax.firsttime = True
            self.axes.append(ax)

        self.figure.subplots_adjust(hspace=0.5)
        self.figure.show()

    def plot(self):

        self.x = np.array(self.times)
        self.y = self.dataOut.getHeiRange()
        self.z = []

        for ch in range(self.nrows):
            self.z.append([self.data[self.CODE][t][ch] for t in self.times])

        self.z = np.array(self.z)

        for n, ax in enumerate(self.axes):

            x, y, z = self.fill_gaps(*self.decimate())

            if ax.firsttime:
                self.ymin = self.ymin if self.ymin else np.nanmin(self.y)
                self.ymax = self.ymax if self.ymax else np.nanmax(self.y)
                self.zmin = self.zmin if self.zmin else np.nanmin(self.z)
                zmax = self.zmax if self.zmax else np.nanmax(self.z)
                plot = ax.pcolormesh(x, y, z[n].T,
                                     vmin=self.zmin,
                                     vmax=self.zmax,
                                     cmap=plt.get_cmap(self.colormap)
                                    )
                divider = make_axes_locatable(ax)
                cax = divider.new_horizontal(size='2%', pad=0.05)
                self.figure.add_axes(cax)
                plt.colorbar(plot, cax)
                ax.set_ylim(self.ymin, self.ymax)
                if self.xaxis=='time':
                    ax.xaxis.set_major_formatter(FuncFormatter(func))
                    ax.xaxis.set_major_locator(LinearLocator(6))

                ax.yaxis.set_major_locator(LinearLocator(4))

                ax.set_ylabel(self.ylabel)

                if self.xmin is None:
                    print 'is none'
                    xmin = self.min_time
                else:

                    xmin = (datetime.datetime.combine(self.dataOut.datatime.date(),
                                                     datetime.time(self.xmin, 0, 0))-d1970).total_seconds()

                xmax = xmin+self.xrange*60*60

                ax.set_xlim(xmin, xmax)
                ax.firsttime = False
            else:
                ax.collections.remove(ax.collections[0])
                plot = ax.pcolormesh(x, y, z[n].T,
                                     vmin=self.zmin,
                                     vmax=self.zmax,
                                     cmap=plt.get_cmap(self.colormap)
                                    )
                ax.set_title('{} {}'.format(self.titles[n],
                                            datetime.datetime.utcfromtimestamp(self.max_time).strftime('%y/%m/%d %H:%M:%S')),
                             size=8)


class PlotCOHData(PlotRTIData):

    CODE = 'coh'

    def setup(self):

        self.ncols = 1
        self.nrows = self.dataOut.nPairs
        self.width = 10
        self.height = 2.2*self.nrows
        self.ylabel = 'Range [Km]'
        self.titles = ['Channels {}'.format(x) for x in self.dataOut.pairsList]

        if self.figure is None:
            self.figure = plt.figure(figsize=(self.width, self.height),
                                     edgecolor='k',
                                     facecolor='w')
        else:
            self.figure.clf()

        for n in range(self.nrows):
            ax = self.figure.add_subplot(self.nrows, self.ncols, n+1)
            ax.firsttime = True
            self.axes.append(ax)

        self.figure.subplots_adjust(hspace=0.5)
        self.figure.show()

class PlotSNRData(PlotRTIData):

    CODE = 'coh'


class PlotPHASEData(PlotCOHData):

    CODE = 'phase'
    colormap = 'seismic'
