
import os
import time
import numpy
import datetime
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.ticker import FuncFormatter, LinearLocator

from schainpy.model.proc.jroproc_base import Operation

func = lambda x, pos: ('%s') %(datetime.datetime.utcfromtimestamp(x).strftime('%H:%M'))

d1970 = datetime.datetime(1970,1,1)


class PlotData(Operation):

    __MAXNUMX = 80
    __MAXNUMY = 80
    __missing = 1E30

    def __init__(self):

        Operation.__init__(self)
        self.xmin = None
        self.xmax = None
        self.newdataOut = None
        self.dataOut = None
        self.isConfig = False
        self.figure = None

    def setup(self, dataOut,  **kwargs):

        self.first = True
        self.plottype = kwargs.pop('plottype', 'rti')
        self.localtime = kwargs.pop('localtime', True)
        self.show = kwargs.pop('show', True)
        self.save = kwargs.pop('save', False)
        self.pause = kwargs.pop('pause', False)
        self.time = []
        self.nblock = 0
        self.z = []
        self.data = [{} for __ in dataOut.channelList]
        self.axes = []  
        self.colormap = kwargs.get('colormap', 'jet')
        self.title = kwargs.get('wintitle', self.plottype.upper())
        self.xaxis = kwargs.get('xaxis', None)
        self.zmin = kwargs.get('zmin', None)
        self.zmax = kwargs.get('zmax', None)

        xmin = kwargs.get('xmin', 0)
        xmax = kwargs.get('xmax', xmin+4)

        dt = dataOut.datatime.date()
        dtmin = datetime.datetime.combine(dt, datetime.time(xmin, 0, 0))
        dtmax = datetime.datetime.combine(dt, datetime.time(xmax, 59, 59))

        self.xmin = (dtmin-d1970).total_seconds()
        self.xmax = (dtmax-d1970).total_seconds()

        if self.plottype in ('rti',):
            self.ncols = 1
            self.nrows = dataOut.nChannels
            self.width = 8
            self.height = 2.2*self.nrows
            self.ylabel = 'Range [Km]'
            self.y = dataOut.getHeiRange()

        self.ymin = kwargs.get('ymin', min(self.y))
        self.ymax = kwargs.get('ymax', max(self.y))

        if self.figure is None:
            self.figure = plt.figure()
        else:
            self.figure.clf()

        for n in range(dataOut.nChannels):
            ax = self.figure.add_subplot(self.nrows, self.ncols, n+1)
            ax.firsttime = True
            self.axes.append(ax)

        self.figure.set_size_inches (self.width, self.height)

    def fill_gaps(self, x_buffer, y_buffer, z_buffer):

        if x_buffer.shape[0] < 2:
            return x_buffer, y_buffer, z_buffer

        deltas = x_buffer[1:] - x_buffer[0:-1]
        x_median = np.median(deltas)

        index = np.where(deltas > 5*x_median)

        if len(index[0]) != 0:
            z_buffer[index[0],::] = self.__missing
            z_buffer = np.ma.masked_inside(z_buffer,
                                           0.99*self.__missing,
                                           1.01*self.__missing)

        return x_buffer, y_buffer, z_buffer

    def plot(self):

        dt = datetime.datetime.utcfromtimestamp(self.time[-2])
        
        if self.plottype=='rti':
            self.time.sort()
            for ch in self.dataOut.channelList:
                self.z.append([self.data[ch][t] for t in self.time])
            self.x = np.array(self.time)
            self.z = np.array(self.z)
            self.plot_rti()

        for n, ax in enumerate(self.axes):            
            
            if self.xaxis=='time':
                ax.xaxis.set_major_formatter(FuncFormatter(func))
                ax.xaxis.set_major_locator(LinearLocator(6))

            ax.yaxis.set_major_locator(LinearLocator(4))

            ax.set_ylabel(self.ylabel)
            ax.set_ylim(self.ymin, self.ymax)
            ax.set_xlim(self.xmin, self.xmax)
            
            ax.set_title('Channel {} {}'.format(
                                        self.dataOut.channelList[n],
                                        dt.strftime('%y/%m/%d %H:%M:%S'), 
                                        size=6))

        if self.save:
            figname = os.path.join(self.save, 'rti_{}.png'.format(dt.strftime('%y%m%d_%H%M%S')))
            print 'Saving figure: {}'.format(figname)
            self.figure.savefig(figname)

        self.figure.canvas.draw()
        if self.show:
            self.figure.show()
        if self.pause:
            raw_input('Press <ENTER> to continue')

    def plot_rti(self):

        for n, ax in enumerate(self.axes):
            x, y, z = self.fill_gaps(self.x, self.y, self.z[n])
            if ax.firsttime:
                zmin = self.zmin if self.zmin else np.nanmin(self.z)
                zmax = self.zmax if self.zmax else np.nanmax(self.z)
                plot = ax.pcolormesh(x, y, z.T,
                                     vmin=zmin,
                                     vmax=zmax,
                                     cmap=plt.get_cmap(self.colormap)
                                    )
                divider = make_axes_locatable(ax)
                cax = divider.new_horizontal(size='3%', pad=0.05)
                self.figure.add_axes(cax)
                plt.colorbar(plot, cax)
                ax.firsttime = False
            else:                
                plot = ax.pcolormesh(x, y, z.T,
                                               vmin=zmin,
                                               vmax=zmax,
                                               cmap=plt.get_cmap(self.colormap)
                                               )            

        self.figure.suptitle(self.title)
        self.figure.subplots_adjust(wspace=None, hspace=0.5)

    def update(self):

        self.nblock += 1
        self.time.append(self.dataOut.ltctime)
        if self.plottype=='rti':
            for ch in self.dataOut.channelList:
                self.data[ch][self.dataOut.ltctime] = self.dataOut.getPower()[ch]

    def run(self, dataOut, **kwargs):

        self.dataOut = dataOut

        if not self.isConfig:
            self.setup(dataOut, **kwargs)
            self.isConfig = True

        self.update()        

        if dataOut.ltctime>=self.xmax:
            self.plot()
            self.isConfig = False

    def close(self):
        
        self.plot()
        