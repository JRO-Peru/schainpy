'''
Created on Jul 9, 2014

@author: roj-idl71
'''
import os
import datetime
import numpy
from schainpy.model.proc.jroproc_base import ProcessingUnit, Operation, MPDecorator  #YONG
from schainpy.utils import log
from .figure import Figure


@MPDecorator
class Scope_(Figure):

    isConfig = None

    def __init__(self):#, **kwargs):          #YONG
        Figure.__init__(self)#, **kwargs)
        self.isConfig = False
        self.WIDTH = 300
        self.HEIGHT = 200
        self.counter_imagwr = 0

    def getSubplots(self):

        nrow = self.nplots
        ncol = 3
        return nrow, ncol

    def setup(self, id, nplots, wintitle, show):

        self.nplots = nplots

        self.createFigure(id=id,
                          wintitle=wintitle,
                          show=show)

        nrow,ncol = self.getSubplots()
        colspan = 3
        rowspan = 1

        for i in range(nplots):
            self.addAxes(nrow, ncol, i, 0, colspan, rowspan)

    def plot_iq(self, x, y, id, channelIndexList, thisDatetime, wintitle, show, xmin, xmax, ymin, ymax):
        yreal = y[channelIndexList,:].real
        yimag = y[channelIndexList,:].imag

        title = wintitle + " Scope: %s" %(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
        xlabel = "Range (Km)"
        ylabel = "Intensity - IQ"

        if not self.isConfig:
            nplots = len(channelIndexList)

            self.setup(id=id,
                       nplots=nplots,
                       wintitle='',
                       show=show)

            if xmin == None: xmin = numpy.nanmin(x)
            if xmax == None: xmax = numpy.nanmax(x)
            if ymin == None: ymin = min(numpy.nanmin(yreal),numpy.nanmin(yimag))
            if ymax == None: ymax = max(numpy.nanmax(yreal),numpy.nanmax(yimag))

            self.isConfig = True

        self.setWinTitle(title)

        for i in range(len(self.axesList)):
            title = "Channel %d" %(i)
            axes = self.axesList[i]

            axes.pline(x, yreal[i,:],
                        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,
                        xlabel=xlabel, ylabel=ylabel, title=title)

            axes.addpline(x, yimag[i,:], idline=1, color="red", linestyle="solid", lw=2)

    def plot_power(self, x, y, id, channelIndexList, thisDatetime, wintitle, show, xmin, xmax, ymin, ymax):
        y = y[channelIndexList,:] * numpy.conjugate(y[channelIndexList,:])
        yreal = y.real

        title = wintitle + " Scope: %s" %(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
        xlabel = "Range (Km)"
        ylabel = "Intensity"

        if not self.isConfig:
            nplots = len(channelIndexList)

            self.setup(id=id,
                       nplots=nplots,
                       wintitle='',
                       show=show)

            if xmin == None: xmin = numpy.nanmin(x)
            if xmax == None: xmax = numpy.nanmax(x)
            if ymin == None: ymin = numpy.nanmin(yreal)
            if ymax == None: ymax = numpy.nanmax(yreal)


            self.isConfig = True

        self.setWinTitle(title)

        for i in range(len(self.axesList)):
            title = "Channel %d" %(i)
            axes = self.axesList[i]
            ychannel = yreal[i,:]
            axes.pline(x, ychannel,
                        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,
                        xlabel=xlabel, ylabel=ylabel, title=title)

    def plot_weatherpower(self, x, y, id, channelIndexList, thisDatetime, wintitle, show, xmin, xmax, ymin, ymax):

        #x = x[channelIndexList,:]
        y = y[channelIndexList,:].real
        y = 10*numpy.log10(y)
        title = wintitle + " Scope: %s" %(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
        xlabel = "Range (Km)"
        ylabel = "Intensity"

        if not self.isConfig:
            nplots = len(channelIndexList)

            self.setup(id=id,
                       nplots=nplots,
                       wintitle='',
                       show=show)

            if xmin == None: xmin = numpy.nanmin(x)
            if xmax == None: xmax = numpy.nanmax(x)
            if ymin == None: ymin = numpy.nanmin(y)
            if ymax == None: ymax = numpy.nanmax(y)
            #print (xmin,xmax)

            self.isConfig = True

        self.setWinTitle(title)

        for i in range(len(self.axesList)):
            title = "Channel %d" %(i)
            axes = self.axesList[i]
            #print(numpy.nanmax(x))
            ychannel    = y[i,:]
            #ychannel = yreal[i,:]
            axes.pline(x, ychannel,
                        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,
                        xlabel=xlabel, ylabel=ylabel, title=title)

    def plot_weathervelocity(self, x, y, id, channelIndexList, thisDatetime, wintitle, show, xmin, xmax, ymin, ymax):
        #print(channelIndexList)
        x = x[channelIndexList,:]

        title = wintitle + " Scope: %s" %(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
        xlabel = "Velocity (m/s)"
        ylabel = "Range (Km)"

        if not self.isConfig:
            nplots = len(channelIndexList)

            self.setup(id=id,
                       nplots=nplots,
                       wintitle='',
                       show=show)

            if xmin == None: xmin = numpy.nanmin(x)
            if xmax == None: xmax = numpy.nanmax(x)
            if ymin == None: ymin = numpy.nanmin(y)
            if ymax == None: ymax = numpy.nanmax(y)
            print (xmin,xmax)

            self.isConfig = True

        self.setWinTitle(title)

        for i in range(len(self.axesList)):
            title = "Channel %d" %(i)
            axes = self.axesList[i]
            #print(numpy.nanmax(x))
            xchannel    = x[i,:]
            #ychannel = yreal[i,:]
            axes.pline(xchannel, y,
                        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,
                        xlabel=xlabel, ylabel=ylabel, title=title)


    def run(self, dataOut, id, wintitle="", channelList=None,
            xmin=None, xmax=None, ymin=None, ymax=None, save=False,
            figpath='./', figfile=None, show=True, wr_period=1,
            ftp=False, server=None, folder=None, username=None, password=None, type='power', **kwargs):

        """

        Input:
            dataOut         :
            id        :
            wintitle        :
            channelList     :
            xmin            :    None,
            xmax            :    None,
            ymin            :    None,
            ymax            :    None,
        """
        if dataOut.flagNoData:
            return dataOut

        if channelList == None:
            channelIndexList = dataOut.channelIndexList
        else:
            channelIndexList = []
            for channel in channelList:
                if channel not in dataOut.channelList:
                    raise ValueError("Channel %d is not in dataOut.channelList")
                channelIndexList.append(dataOut.channelList.index(channel))

        thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.getTimeRange()[0])
        #print("***************** PLOTEO **************************")
        #print(dataOut.nProfiles)
        #print(dataOut.heightList.shape)
        #print(dataOut.data.shape)
        if dataOut.flagDataAsBlock:

            for i in range(dataOut.nProfiles):

                wintitle1 = wintitle + " [Profile = %d] " %i

                if type == "power":
                    self.plot_power(dataOut.heightList,
                                    dataOut.data[:,i,:],
                                    id,
                                    channelIndexList,
                                    thisDatetime,
                                    wintitle1,
                                    show,
                                    xmin,
                                    xmax,
                                    ymin,
                                    ymax)

                if type == "weatherpower":
                    self.plot_weatherpower(dataOut.heightList,
                                    dataOut.data[:,i,:],
                                    id,
                                    channelIndexList,
                                    thisDatetime,
                                    wintitle,
                                    show,
                                    xmin,
                                    xmax,
                                    ymin,
                                    ymax)

                if type == "weathervelocity":
                    self.plot_weathervelocity(dataOut.data_velocity[:,i,:],
                                    dataOut.heightList,
                                    id,
                                    channelIndexList,
                                    thisDatetime,
                                    wintitle1,
                                    show,
                                    xmin,
                                    xmax,
                                    ymin,
                                    ymax)

                if type == "iq":
                    self.plot_iq(dataOut.heightList,
                                 dataOut.data[:,i,:],
                                 id,
                                 channelIndexList,
                                 thisDatetime,
                                 wintitle1,
                                 show,
                                 xmin,
                                 xmax,
                                 ymin,
                                 ymax)

                self.draw()

                str_datetime = thisDatetime.strftime("%Y%m%d_%H%M%S")
                figfile = self.getFilename(name = str_datetime) + "_" + str(i)

                self.save(figpath=figpath,
                          figfile=figfile,
                          save=save,
                          ftp=ftp,
                          wr_period=wr_period,
                          thisDatetime=thisDatetime)

        else:
            wintitle += " [Profile = %d] " %dataOut.profileIndex

            if type == "power":
                self.plot_power(dataOut.heightList,
                                dataOut.data,
                                id,
                                channelIndexList,
                                thisDatetime,
                                wintitle,
                                show,
                                xmin,
                                xmax,
                                ymin,
                                ymax)

            if type == "iq":
                self.plot_iq(dataOut.heightList,
                             dataOut.data,
                             id,
                             channelIndexList,
                             thisDatetime,
                             wintitle,
                             show,
                             xmin,
                             xmax,
                             ymin,
                             ymax)

            if type== "weatherpower":
                self.plot_weatherpower(dataOut.heightList,
                                dataOut.data,
                                id,
                                channelIndexList,
                                thisDatetime,
                                wintitle,
                                show,
                                xmin,
                                xmax,
                                ymin,
                                ymax)
            if type== "weathervelocity":
                self.plot_weathervelocity(dataOut.data_velocity,
                                dataOut.heightList,
                                id,
                                channelIndexList,
                                thisDatetime,
                                wintitle,
                                show,
                                xmin,
                                xmax,
                                ymin,
                                ymax)

        self.draw()

        str_datetime = thisDatetime.strftime("%Y%m%d_%H%M%S") + "_" + str(dataOut.profileIndex)
        figfile = self.getFilename(name = str_datetime)

        self.save(figpath=figpath,
                  figfile=figfile,
                  save=save,
                  ftp=ftp,
                  wr_period=wr_period,
                  thisDatetime=thisDatetime)

        return dataOut



@MPDecorator
class TimePlot_(Figure):

    __isConfig = None
    __nsubplots = None

    WIDTHPROF = None
    HEIGHTPROF = None
    PREFIX = 'time'

    def __init__(self):

        Figure.__init__(self)
        self.timerange = None
        self.isConfig = False
        self.__nsubplots = 1

        self.WIDTH = 800
        self.HEIGHT = 250
        self.WIDTHPROF = 120
        self.HEIGHTPROF = 0
        self.counter_imagwr = 0

        self.PLOT_CODE = RTIVOLT_CODE

        self.FTP_WEI = None
        self.EXP_CODE = None
        self.SUB_EXP_CODE = None
        self.PLOT_POS = None
        self.tmin = None
        self.tmax = None

        self.xmin = None
        self.xmax = None

        self.figfile = None

    def getSubplots(self):

        ncol = 1
        nrow = self.nplots

        return nrow, ncol

    def setup(self, id, nplots, wintitle, showprofile=True, show=True):

        self.__showprofile = showprofile
        self.nplots = nplots

        ncolspan = 1
        colspan = 1
        if showprofile:
            ncolspan = 7
            colspan = 6
            self.__nsubplots = 2

        self.createFigure(id = id,
                          wintitle = wintitle,
                          widthplot = self.WIDTH + self.WIDTHPROF,
                          heightplot = self.HEIGHT + self.HEIGHTPROF,
                          show=show)

        nrow, ncol = self.getSubplots()

        counter = 0
        for y in range(nrow):
            for x in range(ncol):

                if counter >= self.nplots:
                    break

                self.addAxes(nrow, ncol*ncolspan, y, x*ncolspan, colspan, 1)

                if showprofile:
                    self.addAxes(nrow, ncol*ncolspan, y, x*ncolspan+colspan, 1, 1)

                counter += 1

    def run(self, dataOut, id, wintitle="", channelList=None, showprofile='True',
            xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None,type="intensity",
            timerange=None, colormap='jet',
            save=False, figpath='./', lastone=0,figfile=None, ftp=False, wr_period=1, show=True,
            server=None, folder=None, username=None, password=None,
            ftp_wei=0, exp_code=0, sub_exp_code=0, plot_pos=0, normFactor=None, HEIGHT=None):

        """

        Input:
            dataOut         :
            id        :
            wintitle        :
            channelList     :
            showProfile     :
            xmin            :    None,
            xmax            :    None,
            ymin            :    None,
            ymax            :    None,
            zmin            :    None,
            zmax            :    None
        """
        print("estoy aqui :D")
        if dataOut.flagNoData:
            return dataOut

        #colormap = kwargs.get('colormap', 'jet')
        if HEIGHT is not None:
            self.HEIGHT  = HEIGHT

        if not isTimeInHourRange(dataOut.datatime, xmin, xmax):
            return

        if channelList == None:
            channelIndexList = dataOut.channelIndexList
        else:
            channelIndexList = []
            for channel in channelList:
                if channel not in dataOut.channelList:
                    raise ValueError("Channel %d is not in dataOut.channelList")
                channelIndexList.append(dataOut.channelList.index(channel))

        if normFactor is None:
            factor = dataOut.normFactor
        else:
            factor = normFactor

        #factor = dataOut.normFactor
        x = dataOut.getTimeRange()
        y = dataOut.getHeiRange()
        if type=="intensity":
            z = dataOut.data_intensity/factor
            z = numpy.where(numpy.isfinite(z), z, numpy.NAN)
            avgdB = numpy.average(z, axis=1)
            avgdB = 10.*numpy.log10(avg)
        else:
            z= dataOut.data_velocity
            avgdB = numpy.average(z, axis=1)

        # avgdB = dataOut.getPower()


        thisDatetime = dataOut.datatime
        #thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.getTimeRange()[0])
        title = wintitle + " RTI" #: %s" %(thisDatetime.strftime("%d-%b-%Y"))
        xlabel = ""
        ylabel = "Range (Km)"

        update_figfile = False

        if self.xmax is not None and dataOut.ltctime >= self.xmax: #yong
            self.counter_imagwr = wr_period
            self.isConfig = False
            update_figfile = True

        if not self.isConfig:

            nplots = len(channelIndexList)

            self.setup(id=id,
                       nplots=nplots,
                       wintitle=wintitle,
                       showprofile=showprofile,
                       show=show)

            if timerange != None:
                self.timerange = timerange

            self.xmin, self.xmax = self.getTimeLim(x, xmin, xmax, timerange)

            noise = dataOut.noise/factor
            noisedB = 10*numpy.log10(noise)

            if ymin == None: ymin = numpy.nanmin(y)
            if ymax == None: ymax = numpy.nanmax(y)
            if zmin == None: zmin = numpy.floor(numpy.nanmin(noisedB)) - 3
            if zmax == None: zmax = numpy.ceil(numpy.nanmax(avgdB)) + 3

            self.FTP_WEI = ftp_wei
            self.EXP_CODE = exp_code
            self.SUB_EXP_CODE = sub_exp_code
            self.PLOT_POS = plot_pos

            self.name = thisDatetime.strftime("%Y%m%d_%H%M%S")
            self.isConfig = True
            self.figfile = figfile
            update_figfile = True

        self.setWinTitle(title)

        for i in range(self.nplots):
            index = channelIndexList[i]
            title = "Channel %d: %s" %(dataOut.channelList[index], thisDatetime.strftime("%Y/%m/%d %H:%M:%S"))
            if ((dataOut.azimuth!=None) and (dataOut.zenith!=None)):
                title = title + '_' + 'azimuth,zenith=%2.2f,%2.2f'%(dataOut.azimuth, dataOut.zenith)
            axes = self.axesList[i*self.__nsubplots]
            zdB = avgdB[index].reshape((1,-1))
            axes.pcolorbuffer(x, y, zdB,
                        xmin=self.xmin, xmax=self.xmax, ymin=ymin, ymax=ymax, zmin=zmin, zmax=zmax,
                        xlabel=xlabel, ylabel=ylabel, title=title, rti=True, XAxisAsTime=True,
                        ticksize=9, cblabel='', cbsize="1%", colormap=colormap)

            if self.__showprofile:
                axes = self.axesList[i*self.__nsubplots +1]
                axes.pline(avgdB[index], y,
                        xmin=zmin, xmax=zmax, ymin=ymin, ymax=ymax,
                        xlabel='dB', ylabel='', title='',
                        ytick_visible=False,
                        grid='x')

        self.draw()

        self.save(figpath=figpath,
                  figfile=figfile,
                  save=save,
                  ftp=ftp,
                  wr_period=wr_period,
                  thisDatetime=thisDatetime,
                  update_figfile=update_figfile)
        return dataOut
