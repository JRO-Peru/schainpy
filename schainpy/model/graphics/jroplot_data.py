
import os
import zmq
import time
import numpy
import datetime
import numpy as np
import matplotlib
import glob
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.ticker import FuncFormatter, LinearLocator
from multiprocessing import Process

from schainpy.model.proc.jroproc_base import Operation

plt.ion()

func = lambda x, pos: ('%s') %(datetime.datetime.fromtimestamp(x).strftime('%H:%M'))

d1970 = datetime.datetime(1970,1,1)

class PlotData(Operation, Process):

    CODE = 'Figure'
    colormap = 'jro'
    CONFLATE = False
    __MAXNUMX = 80
    __missing = 1E30

    def __init__(self, **kwargs):

        Operation.__init__(self, plot=True, **kwargs)
        Process.__init__(self)
        self.kwargs['code'] = self.CODE
        self.mp = False
        self.dataOut = None
        self.isConfig = False
        self.figure = None
        self.axes = []
        self.localtime = kwargs.pop('localtime', True)
        self.show = kwargs.get('show', True)
        self.save = kwargs.get('save', False)
        self.colormap = kwargs.get('colormap', self.colormap)
        self.colormap_coh = kwargs.get('colormap_coh', 'jet')
        self.colormap_phase = kwargs.get('colormap_phase', 'RdBu_r')
        self.showprofile = kwargs.get('showprofile', True)
        self.title = kwargs.get('wintitle', '')
        self.xaxis = kwargs.get('xaxis', 'frequency')
        self.zmin = kwargs.get('zmin', None)
        self.zmax = kwargs.get('zmax', None)
        self.xmin = kwargs.get('xmin', None)
        self.xmax = kwargs.get('xmax', None)
        self.xrange = kwargs.get('xrange', 24)
        self.ymin = kwargs.get('ymin', None)
        self.ymax = kwargs.get('ymax', None)
        self.__MAXNUMY = kwargs.get('decimation', 80)
        self.throttle_value = 5
        self.times = []
        #self.interactive = self.kwargs['parent']

        '''
        this new parameter is created to plot data from varius channels at different figures
        1. crear una lista de figuras donde se puedan plotear las figuras,
        2. dar las opciones de configuracion a cada figura, estas opciones son iguales para ambas figuras
        3. probar?
        '''
        self.ind_plt_ch = kwargs.get('ind_plt_ch', False)
        self.figurelist = None


    def fill_gaps(self, x_buffer, y_buffer, z_buffer):

        if x_buffer.shape[0] < 2:
            return x_buffer, y_buffer, z_buffer

        deltas = x_buffer[1:] - x_buffer[0:-1]
        x_median = np.median(deltas)

        index = np.where(deltas > 5*x_median)

        if len(index[0]) != 0:
            z_buffer[::, index[0], ::] = self.__missing
            z_buffer = np.ma.masked_inside(z_buffer,
                                           0.99*self.__missing,
                                           1.01*self.__missing)

        return x_buffer, y_buffer, z_buffer

    def decimate(self):

        # dx = int(len(self.x)/self.__MAXNUMX) + 1
        dy = int(len(self.y)/self.__MAXNUMY) + 1

        # x = self.x[::dx]
        x = self.x
        y = self.y[::dy]
        z = self.z[::, ::, ::dy]

        return x, y, z

    '''
    JM:
    elimana las otras imagenes generadas debido a que lso workers no llegan en orden y le pueden
    poner otro tiempo a la figura q no necesariamente es el ultimo.
    Solo se realiza cuando termina la imagen.
    Problemas:
    -Aun no encuentro.
    '''
    def deleteanotherfiles(self):
        figurenames=[]
        for n, eachfigure in enumerate(self.figurelist):
            #add specific name for each channel in channelList
            ghostfigname = os.path.join(self.save, '{}_{}_{}'.format(self.titles[n].replace(' ',''),self.CODE,
                                                                 datetime.datetime.fromtimestamp(self.saveTime).strftime('%y%m%d')))
            figname = os.path.join(self.save, '{}_{}_{}.png'.format(self.titles[n].replace(' ',''),self.CODE,
                                                                 datetime.datetime.fromtimestamp(self.saveTime).strftime('%y%m%d_%H%M%S')))

            for ghostfigure in glob.glob(ghostfigname+'*'): #ghostfigure will adopt all posible names of figures
                if ghostfigure != figname:
                    os.remove(ghostfigure)
                    print 'Removing GhostFigures:' , figname

    def __plot(self):

        print 'plotting...{}'.format(self.CODE)
        if self.ind_plt_ch is False : #standard
            if self.show:
                self.figure.show()
            self.plot()
            plt.tight_layout()
            self.figure.canvas.manager.set_window_title('{} {} - {}'.format(self.title, self.CODE.upper(),
                                                                        datetime.datetime.fromtimestamp(self.max_time).strftime('%Y/%m/%d')))
        else :
            for n, eachfigure in enumerate(self.figurelist):
                if self.show:
                    eachfigure.show()

                self.plot() # ok? como elijo que figura?
                #eachfigure.subplots_adjust(left=0.2)
                #eachfigure.subplots_adjuccst(right=0.2)
                eachfigure.tight_layout() # ajuste de cada subplot
                eachfigure.canvas.manager.set_window_title('{} {} - {}'.format(self.title[n], self.CODE.upper(),
                                                                            datetime.datetime.fromtimestamp(self.max_time).strftime('%Y/%m/%d')))

        # if self.save:
        #     if self.ind_plt_ch is False : #standard
        #         figname = os.path.join(self.save, '{}_{}.png'.format(self.CODE,
        #                                                              datetime.datetime.fromtimestamp(self.saveTime).strftime('%y%m%d_%H%M%S')))
        #         print 'Saving figure: {}'.format(figname)
        #         self.figure.savefig(figname)
        #     else :
        #         for n, eachfigure in enumerate(self.figurelist):
        #             #add specific name for each channel in channelList
        #             figname = os.path.join(self.save, '{}_{}_{}.png'.format(self.titles[n],self.CODE,
        #                                                                  datetime.datetime.fromtimestamp(self.saveTime).strftime('%y%m%d_%H%M%S')))
        #
        #             print 'Saving figure: {}'.format(figname)
        #             eachfigure.savefig(figname)

        if self.ind_plt_ch is False :
            self.figure.canvas.draw()
        else :
            for eachfigure in self.figurelist:
                eachfigure.canvas.draw()

        if self.save:
            if self.ind_plt_ch is False : #standard
                figname = os.path.join(self.save, '{}_{}.png'.format(self.CODE,
                                                                     datetime.datetime.fromtimestamp(self.saveTime).strftime('%y%m%d_%H%M%S')))
                print 'Saving figure: {}'.format(figname)
                self.figure.savefig(figname)
            else :
                for n, eachfigure in enumerate(self.figurelist):
                    #add specific name for each channel in channelList
                    figname = os.path.join(self.save, '{}_{}_{}.png'.format(self.titles[n].replace(' ',''),self.CODE,
                                                                         datetime.datetime.fromtimestamp(self.saveTime).strftime('%y%m%d_%H%M%S')))

                    print 'Saving figure: {}'.format(figname)
                    eachfigure.savefig(figname)


    def plot(self):

        print 'plotting...{}'.format(self.CODE.upper())
        return

    def run(self):

        print '[Starting] {}'.format(self.name)

        context = zmq.Context()
        receiver = context.socket(zmq.SUB)
        receiver.setsockopt(zmq.SUBSCRIBE, '')
        receiver.setsockopt(zmq.CONFLATE, self.CONFLATE)

        if 'server' in self.kwargs['parent']:
            receiver.connect('ipc:///tmp/{}.plots'.format(self.kwargs['parent']['server']))
        else:
            receiver.connect("ipc:///tmp/zmq.plots")

        seconds_passed = 0

        while True:
            try:
                self.data = receiver.recv_pyobj(flags=zmq.NOBLOCK)#flags=zmq.NOBLOCK
                self.started = self.data['STARTED']
                self.dataOut = self.data['dataOut']

                if (len(self.times) < len(self.data['times']) and not self.started and self.data['ENDED']):
                    continue

                self.times = self.data['times']
                self.times.sort()
                self.throttle_value = self.data['throttle']
                self.min_time = self.times[0]
                self.max_time = self.times[-1]

                if self.isConfig is False:
                    print 'setting up'
                    self.setup()
                    self.isConfig = True
                    self.__plot()

                if self.data['ENDED'] is True:
                    print '********GRAPHIC ENDED********'
                    self.ended = True
                    self.isConfig = False
                    self.__plot()
                    self.deleteanotherfiles() #CLPDG
                elif seconds_passed >= self.data['throttle']:
                    print 'passed', seconds_passed
                    self.__plot()
                    seconds_passed = 0

            except zmq.Again as e:
                print 'Waiting for data...'
                plt.pause(2)
                seconds_passed += 2

    def close(self):
        if self.dataOut:
            self.__plot()


class PlotSpectraData(PlotData):

    CODE = 'spc'
    colormap = 'jro'
    CONFLATE = False

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
                if n >= self.dataOut.nChannels:
                    break
                ax = plt.subplot2grid((self.nrows, self.ncols*ncolspan), (y, x*ncolspan), 1, colspan)
                if self.showprofile:
                    ax.ax_profile = plt.subplot2grid((self.nrows, self.ncols*ncolspan), (y, x*ncolspan+colspan), 1, 1)

                ax.firsttime = True
                self.axes.append(ax)
                n += 1

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

                ax.set_ylabel(self.ylabel)
                ax.set_xlabel(xlabel)

                ax.firsttime = False

                if self.showprofile:
                    ax.plot_profile= ax.ax_profile.plot(self.data['rti'][self.max_time][n], y)[0]
                    ax.ax_profile.set_xlim(self.zmin, self.zmax)
                    ax.ax_profile.set_ylim(self.ymin, self.ymax)
                    ax.ax_profile.set_xlabel('dB')
                    ax.ax_profile.grid(b=True, axis='x')
                    ax.plot_noise = ax.ax_profile.plot(numpy.repeat(self.data['noise'][self.max_time][n], len(y)), y,
                                                       color="k", linestyle="dashed", lw=2)[0]
                    [tick.set_visible(False) for tick in ax.ax_profile.get_yticklabels()]
            else:
                ax.plot.set_array(z[n].T.ravel())
                if self.showprofile:
                    ax.plot_profile.set_data(self.data['rti'][self.max_time][n], y)
                    ax.plot_noise.set_data(numpy.repeat(self.data['noise'][self.max_time][n], len(y)), y)

            ax.set_title('{} - Noise: {:.2f} dB'.format(self.titles[n], self.data['noise'][self.max_time][n]),
                         size=8)
            self.saveTime = self.max_time


class PlotCrossSpectraData(PlotData):

    CODE = 'cspc'
    zmin_coh = None
    zmax_coh = None
    zmin_phase = None
    zmax_phase = None
    CONFLATE = False

    def setup(self):

        ncolspan = 1
        colspan = 1
        self.ncols = 2
        self.nrows = self.dataOut.nPairs
        self.width = 3.6*self.ncols
        self.height = 3.2*self.nrows

        self.ylabel = 'Range [Km]'
        self.titles = ['Channel {}'.format(x) for x in self.dataOut.channelList]

        if self.figure is None:
            self.figure = plt.figure(figsize=(self.width, self.height),
                                     edgecolor='k',
                                     facecolor='w')
        else:
            self.figure.clf()

        for y in range(self.nrows):
            for x in range(self.ncols):
                ax = plt.subplot2grid((self.nrows, self.ncols), (y, x), 1, 1)
                ax.firsttime = True
                self.axes.append(ax)

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
        z_coh = self.data['cspc_coh']
        z_phase = self.data['cspc_phase']

        for n in range(self.nrows):
            ax = self.axes[2*n]
            ax1 = self.axes[2*n+1]
            if ax.firsttime:
                self.xmax = self.xmax if self.xmax else np.nanmax(x)
                self.xmin = self.xmin if self.xmin else -self.xmax
                self.ymin = self.ymin if self.ymin else np.nanmin(y)
                self.ymax = self.ymax if self.ymax else np.nanmax(y)
                self.zmin_coh = self.zmin_coh if self.zmin_coh else 0.0
                self.zmax_coh = self.zmax_coh if self.zmax_coh else 1.0
                self.zmin_phase = self.zmin_phase if self.zmin_phase else -180
                self.zmax_phase = self.zmax_phase if self.zmax_phase else 180

                ax.plot = ax.pcolormesh(x, y, z_coh[n].T,
                                        vmin=self.zmin_coh,
                                        vmax=self.zmax_coh,
                                        cmap=plt.get_cmap(self.colormap_coh)
                                       )
                divider = make_axes_locatable(ax)
                cax = divider.new_horizontal(size='3%', pad=0.05)
                self.figure.add_axes(cax)
                plt.colorbar(ax.plot, cax)

                ax.set_xlim(self.xmin, self.xmax)
                ax.set_ylim(self.ymin, self.ymax)

                ax.set_ylabel(self.ylabel)
                ax.set_xlabel(xlabel)
                ax.firsttime = False

                ax1.plot = ax1.pcolormesh(x, y, z_phase[n].T,
                                        vmin=self.zmin_phase,
                                        vmax=self.zmax_phase,
                                        cmap=plt.get_cmap(self.colormap_phase)
                                       )
                divider = make_axes_locatable(ax1)
                cax = divider.new_horizontal(size='3%', pad=0.05)
                self.figure.add_axes(cax)
                plt.colorbar(ax1.plot, cax)

                ax1.set_xlim(self.xmin, self.xmax)
                ax1.set_ylim(self.ymin, self.ymax)

                ax1.set_ylabel(self.ylabel)
                ax1.set_xlabel(xlabel)
                ax1.firsttime = False
            else:
                ax.plot.set_array(z_coh[n].T.ravel())
                ax1.plot.set_array(z_phase[n].T.ravel())

            ax.set_title('Coherence Ch{} * Ch{}'.format(self.dataOut.pairsList[n][0], self.dataOut.pairsList[n][1]), size=8)
            ax1.set_title('Phase Ch{} * Ch{}'.format(self.dataOut.pairsList[n][0], self.dataOut.pairsList[n][1]), size=8)
            self.saveTime = self.max_time


class PlotSpectraMeanData(PlotSpectraData):

    CODE = 'spc_mean'
    colormap = 'jet'

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
        z = self.data['spc']
        mean = self.data['mean'][self.max_time]

        for n, ax in enumerate(self.axes):

            if ax.firsttime:
                self.xmax = self.xmax if self.xmax else np.nanmax(x)
                self.xmin = self.xmin if self.xmin else -self.xmax
                self.ymin = self.ymin if self.ymin else np.nanmin(y)
                self.ymax = self.ymax if self.ymax else np.nanmax(y)
                self.zmin = self.zmin if self.zmin else np.nanmin(z)
                self.zmax = self.zmax if self.zmax else np.nanmax(z)
                ax.plt = ax.pcolormesh(x, y, z[n].T,
                                       vmin=self.zmin,
                                       vmax=self.zmax,
                                       cmap=plt.get_cmap(self.colormap)
                                       )
                ax.plt_dop = ax.plot(mean[n], y,
                                     color='k')[0]

                divider = make_axes_locatable(ax)
                cax = divider.new_horizontal(size='3%', pad=0.05)
                self.figure.add_axes(cax)
                plt.colorbar(ax.plt, cax)

                ax.set_xlim(self.xmin, self.xmax)
                ax.set_ylim(self.ymin, self.ymax)

                ax.set_ylabel(self.ylabel)
                ax.set_xlabel(xlabel)

                ax.firsttime = False

                if self.showprofile:
                    ax.plt_profile= ax.ax_profile.plot(self.data['rti'][self.max_time][n], y)[0]
                    ax.ax_profile.set_xlim(self.zmin, self.zmax)
                    ax.ax_profile.set_ylim(self.ymin, self.ymax)
                    ax.ax_profile.set_xlabel('dB')
                    ax.ax_profile.grid(b=True, axis='x')
                    ax.plt_noise = ax.ax_profile.plot(numpy.repeat(self.data['noise'][self.max_time][n], len(y)), y,
                                                       color="k", linestyle="dashed", lw=2)[0]
                    [tick.set_visible(False) for tick in ax.ax_profile.get_yticklabels()]
            else:
                ax.plt.set_array(z[n].T.ravel())
                ax.plt_dop.set_data(mean[n], y)
                if self.showprofile:
                    ax.plt_profile.set_data(self.data['rti'][self.max_time][n], y)
                    ax.plt_noise.set_data(numpy.repeat(self.data['noise'][self.max_time][n], len(y)), y)

            ax.set_title('{} - Noise: {:.2f} dB'.format(self.titles[n], self.data['noise'][self.max_time][n]),
                         size=8)
            self.saveTime = self.max_time


class PlotRTIData(PlotData):

    CODE = 'rti'
    colormap = 'jro'

    def setup(self):
        self.ncols = 1
        self.nrows = self.dataOut.nChannels
        self.width = 10
        self.height = 2.2*self.nrows if self.nrows<6 else 12
        if self.nrows==1:
            self.height += 1
        self.ylabel = 'Range [Km]'
        self.titles = ['Channel {}'.format(x) for x in self.dataOut.channelList]

        '''
        Logica:
        1) Si la variable ind_plt_ch es True, va a crear mas de 1 figura
        2) guardamos "Figures" en una lista y "axes" en otra, quizas se deberia guardar el
        axis dentro de "Figures" como un diccionario.
        '''
        if self.ind_plt_ch is False: #standard mode

            if self.figure is None: #solo para la priemra vez
                self.figure = plt.figure(figsize=(self.width, self.height),
                                         edgecolor='k',
                                         facecolor='w')
            else:
                self.figure.clf()
                self.axes = []


            for n in range(self.nrows):
                ax = self.figure.add_subplot(self.nrows, self.ncols, n+1)
                #ax = self.figure(n+1)
                ax.firsttime = True
                self.axes.append(ax)

        else : #append one figure foreach channel in channelList
            if self.figurelist == None:
                self.figurelist = []
                for n in range(self.nrows):
                    self.figure = plt.figure(figsize=(self.width, self.height),
                                             edgecolor='k',
                                             facecolor='w')
                    #add always one subplot
                    self.figurelist.append(self.figure)

            else : # cada dia nuevo limpia el axes, pero mantiene el figure
                for eachfigure in self.figurelist:
                    eachfigure.clf() # eliminaria todas las figuras de la lista?
                    self.axes = []

            for eachfigure in self.figurelist:
                ax = eachfigure.add_subplot(1,1,1) #solo 1 axis por figura
                #ax = self.figure(n+1)
                ax.firsttime = True
                #Cada figura tiene un distinto puntero
                self.axes.append(ax)
                #plt.close(eachfigure)


    def plot(self):

        if self.ind_plt_ch is False: #standard mode
            self.x = np.array(self.times)
            self.y = self.dataOut.getHeiRange()
            self.z = []

            for ch in range(self.nrows):
                self.z.append([self.data[self.CODE][t][ch] for t in self.times])

            self.z = np.array(self.z)
            for n, ax in enumerate(self.axes):
                x, y, z = self.fill_gaps(*self.decimate())
                xmin = self.min_time
                xmax = xmin+self.xrange*60*60
                self.zmin = self.zmin if self.zmin else np.min(self.z)
                self.zmax = self.zmax if self.zmax else np.max(self.z)
                if ax.firsttime:
                    self.ymin = self.ymin if self.ymin else np.nanmin(self.y)
                    self.ymax = self.ymax if self.ymax else np.nanmax(self.y)
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
                    ax.xaxis.set_major_formatter(FuncFormatter(func))
                    ax.xaxis.set_major_locator(LinearLocator(6))
                    ax.set_ylabel(self.ylabel)
                    if self.xmin is None:
                        xmin = self.min_time
                    else:
                        xmin = (datetime.datetime.combine(self.dataOut.datatime.date(),
                                                         datetime.time(self.xmin, 0, 0))-d1970).total_seconds()
                    ax.set_xlim(xmin, xmax)
                    ax.firsttime = False
                else:
                    ax.collections.remove(ax.collections[0])
                    ax.set_xlim(xmin, xmax)
                    plot = ax.pcolormesh(x, y, z[n].T,
                                         vmin=self.zmin,
                                         vmax=self.zmax,
                                         cmap=plt.get_cmap(self.colormap)
                                        )
                ax.set_title('{} {}'.format(self.titles[n],
                                            datetime.datetime.fromtimestamp(self.max_time).strftime('%y/%m/%d %H:%M:%S')),
                             size=8)

                self.saveTime = self.min_time
        else :
            self.x = np.array(self.times)
            self.y = self.dataOut.getHeiRange()
            self.z = []

            for ch in range(self.nrows):
                self.z.append([self.data[self.CODE][t][ch] for t in self.times])

            self.z = np.array(self.z)
            for n, eachfigure in enumerate(self.figurelist): #estaba ax in axes

                x, y, z = self.fill_gaps(*self.decimate())
                xmin = self.min_time
                xmax = xmin+self.xrange*60*60
                self.zmin = self.zmin if self.zmin else np.min(self.z)
                self.zmax = self.zmax if self.zmax else np.max(self.z)
                if self.axes[n].firsttime:
                    self.ymin = self.ymin if self.ymin else np.nanmin(self.y)
                    self.ymax = self.ymax if self.ymax else np.nanmax(self.y)
                    plot = self.axes[n].pcolormesh(x, y, z[n].T,
                                         vmin=self.zmin,
                                         vmax=self.zmax,
                                         cmap=plt.get_cmap(self.colormap)
                                        )
                    divider = make_axes_locatable(self.axes[n])
                    cax = divider.new_horizontal(size='2%', pad=0.05)
                    eachfigure.add_axes(cax)
                    #self.figure2.add_axes(cax)
                    plt.colorbar(plot, cax)
                    self.axes[n].set_ylim(self.ymin, self.ymax)

                    self.axes[n].xaxis.set_major_formatter(FuncFormatter(func))
                    self.axes[n].xaxis.set_major_locator(LinearLocator(6))

                    self.axes[n].set_ylabel(self.ylabel)

                    if self.xmin is None:
                        xmin = self.min_time
                    else:
                        xmin = (datetime.datetime.combine(self.dataOut.datatime.date(),
                                                         datetime.time(self.xmin, 0, 0))-d1970).total_seconds()

                    self.axes[n].set_xlim(xmin, xmax)
                    self.axes[n].firsttime = False
                else:
                    self.axes[n].collections.remove(self.axes[n].collections[0])
                    self.axes[n].set_xlim(xmin, xmax)
                    plot = self.axes[n].pcolormesh(x, y, z[n].T,
                                         vmin=self.zmin,
                                         vmax=self.zmax,
                                         cmap=plt.get_cmap(self.colormap)
                                        )
                self.axes[n].set_title('{} {}'.format(self.titles[n],
                                            datetime.datetime.fromtimestamp(self.max_time).strftime('%y/%m/%d %H:%M:%S')),
                             size=8)

                self.saveTime = self.min_time


class PlotCOHData(PlotRTIData):

    CODE = 'coh'

    def setup(self):

        self.ncols = 1
        self.nrows = self.dataOut.nPairs
        self.width = 10
        self.height = 2.2*self.nrows if self.nrows<6 else 12
        if self.nrows==1:
            self.height += 1
        self.ylabel = 'Range [Km]'
        self.titles = ['{} Ch{} * Ch{}'.format(self.CODE.upper(), x[0], x[1]) for x in self.dataOut.pairsList]

        if self.figure is None:
            self.figure = plt.figure(figsize=(self.width, self.height),
                                     edgecolor='k',
                                     facecolor='w')
        else:
            self.figure.clf()
            self.axes = []

        for n in range(self.nrows):
            ax = self.figure.add_subplot(self.nrows, self.ncols, n+1)
            ax.firsttime = True
            self.axes.append(ax)


class PlotNoiseData(PlotData):
    CODE = 'noise'

    def setup(self):

        self.ncols = 1
        self.nrows = 1
        self.width = 10
        self.height = 3.2
        self.ylabel = 'Intensity [dB]'
        self.titles = ['Noise']

        if self.figure is None:
            self.figure = plt.figure(figsize=(self.width, self.height),
                                     edgecolor='k',
                                     facecolor='w')
        else:
            self.figure.clf()
            self.axes = []

        self.ax = self.figure.add_subplot(self.nrows, self.ncols, 1)
        self.ax.firsttime = True

    def plot(self):

        x = self.times
        xmin = self.min_time
        xmax = xmin+self.xrange*60*60
        if self.ax.firsttime:
            for ch in self.dataOut.channelList:
                y = [self.data[self.CODE][t][ch] for t in self.times]
                self.ax.plot(x, y, lw=1, label='Ch{}'.format(ch))
            self.ax.firsttime = False
            self.ax.xaxis.set_major_formatter(FuncFormatter(func))
            self.ax.xaxis.set_major_locator(LinearLocator(6))
            self.ax.set_ylabel(self.ylabel)
            plt.legend()
        else:
            for ch in self.dataOut.channelList:
                y = [self.data[self.CODE][t][ch] for t in self.times]
                self.ax.lines[ch].set_data(x, y)

        self.ax.set_xlim(xmin, xmax)
        self.ax.set_ylim(min(y)-5, max(y)+5)
        self.saveTime = self.min_time


class PlotWindProfilerData(PlotRTIData):

    CODE = 'wind'
    colormap = 'seismic'

    def setup(self):
        self.ncols = 1
        self.nrows = self.dataOut.data_output.shape[0]
        self.width = 10
        self.height = 2.2*self.nrows
        self.ylabel = 'Height [Km]'
        self.titles = ['Zonal Wind' ,'Meridional Wind', 'Vertical Wind']
        self.clabels = ['Velocity (m/s)','Velocity (m/s)','Velocity (cm/s)']
        self.windFactor = [1, 1, 100]

        if self.figure is None:
            self.figure = plt.figure(figsize=(self.width, self.height),
                                     edgecolor='k',
                                     facecolor='w')
        else:
            self.figure.clf()
            self.axes = []

        for n in range(self.nrows):
            ax = self.figure.add_subplot(self.nrows, self.ncols, n+1)
            ax.firsttime = True
            self.axes.append(ax)

    def plot(self):

        self.x = np.array(self.times)
        self.y = self.dataOut.heightList
        self.z = []

        for ch in range(self.nrows):
            self.z.append([self.data['output'][t][ch] for t in self.times])

        self.z = np.array(self.z)
        self.z = numpy.ma.masked_invalid(self.z)

        cmap=plt.get_cmap(self.colormap)
        cmap.set_bad('black', 1.)

        for n, ax in enumerate(self.axes):
            x, y, z = self.fill_gaps(*self.decimate())
            xmin = self.min_time
            xmax = xmin+self.xrange*60*60
            if ax.firsttime:
                self.ymin = self.ymin if self.ymin else np.nanmin(self.y)
                self.ymax = self.ymax if self.ymax else np.nanmax(self.y)
                self.zmax = self.zmax if self.zmax else numpy.nanmax(abs(self.z[:-1, :]))
                self.zmin = self.zmin if self.zmin else -self.zmax

                plot = ax.pcolormesh(x, y, z[n].T*self.windFactor[n],
                                     vmin=self.zmin,
                                     vmax=self.zmax,
                                     cmap=cmap
                                    )
                divider = make_axes_locatable(ax)
                cax = divider.new_horizontal(size='2%', pad=0.05)
                self.figure.add_axes(cax)
                cb = plt.colorbar(plot, cax)
                cb.set_label(self.clabels[n])
                ax.set_ylim(self.ymin, self.ymax)

                ax.xaxis.set_major_formatter(FuncFormatter(func))
                ax.xaxis.set_major_locator(LinearLocator(6))

                ax.set_ylabel(self.ylabel)

                ax.set_xlim(xmin, xmax)
                ax.firsttime = False
            else:
                ax.collections.remove(ax.collections[0])
                ax.set_xlim(xmin, xmax)
                plot = ax.pcolormesh(x, y, z[n].T*self.windFactor[n],
                                     vmin=self.zmin,
                                     vmax=self.zmax,
                                     cmap=plt.get_cmap(self.colormap)
                                    )
            ax.set_title('{} {}'.format(self.titles[n],
                                        datetime.datetime.fromtimestamp(self.max_time).strftime('%y/%m/%d %H:%M:%S')),
                         size=8)

            self.saveTime = self.min_time


class PlotSNRData(PlotRTIData):
    CODE = 'snr'
    colormap = 'jet'

class PlotDOPData(PlotRTIData):
    CODE = 'dop'
    colormap = 'jet'


class PlotPHASEData(PlotCOHData):
    CODE = 'phase'
    colormap = 'seismic'


class PlotSkyMapData(PlotData):

    CODE = 'met'

    def setup(self):

        self.ncols = 1
        self.nrows = 1
        self.width = 7.2
        self.height = 7.2

        self.xlabel = 'Zonal Zenith Angle (deg)'
        self.ylabel = 'Meridional Zenith Angle (deg)'

        if self.figure is None:
            self.figure = plt.figure(figsize=(self.width, self.height),
                                     edgecolor='k',
                                     facecolor='w')
        else:
            self.figure.clf()

        self.ax = plt.subplot2grid((self.nrows, self.ncols), (0, 0), 1, 1, polar=True)
        self.ax.firsttime = True


    def plot(self):

        arrayParameters = np.concatenate([self.data['param'][t] for t in self.times])
        error = arrayParameters[:,-1]
        indValid = numpy.where(error == 0)[0]
        finalMeteor = arrayParameters[indValid,:]
        finalAzimuth = finalMeteor[:,3]
        finalZenith = finalMeteor[:,4]

        x = finalAzimuth*numpy.pi/180
        y = finalZenith

        if self.ax.firsttime:
            self.ax.plot = self.ax.plot(x, y, 'bo', markersize=5)[0]
            self.ax.set_ylim(0,90)
            self.ax.set_yticks(numpy.arange(0,90,20))
            self.ax.set_xlabel(self.xlabel)
            self.ax.set_ylabel(self.ylabel)
            self.ax.yaxis.labelpad = 40
            self.ax.firsttime = False
        else:
            self.ax.plot.set_data(x, y)


        dt1 = datetime.datetime.fromtimestamp(self.min_time).strftime('%y/%m/%d %H:%M:%S')
        dt2 = datetime.datetime.fromtimestamp(self.max_time).strftime('%y/%m/%d %H:%M:%S')
        title = 'Meteor Detection Sky Map\n %s - %s \n Number of events: %5.0f\n' % (dt1,
                                                                                     dt2,
                                                                                     len(x))
        self.ax.set_title(title, size=8)

        self.saveTime = self.max_time
