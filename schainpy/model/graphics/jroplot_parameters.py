import os
import datetime
import numpy
import inspect
from figure import Figure, isRealtime, isTimeInHourRange
from plotting_codes import *


class FitGauPlot(Figure):

    isConfig = None
    __nsubplots = None

    WIDTHPROF = None
    HEIGHTPROF = None
    PREFIX = 'fitgau'

    def __init__(self, **kwargs):
        Figure.__init__(self, **kwargs)
        self.isConfig = False
        self.__nsubplots = 1

        self.WIDTH = 250
        self.HEIGHT = 250
        self.WIDTHPROF = 120
        self.HEIGHTPROF = 0
        self.counter_imagwr = 0

        self.PLOT_CODE = SPEC_CODE

        self.FTP_WEI = None
        self.EXP_CODE = None
        self.SUB_EXP_CODE = None
        self.PLOT_POS = None

        self.__xfilter_ena = False
        self.__yfilter_ena = False

    def getSubplots(self):

        ncol = int(numpy.sqrt(self.nplots)+0.9)
        nrow = int(self.nplots*1./ncol + 0.9)

        return nrow, ncol

    def setup(self, id, nplots, wintitle, showprofile=True, show=True):

        self.__showprofile = showprofile
        self.nplots = nplots

        ncolspan = 1
        colspan = 1
        if showprofile:
            ncolspan = 3
            colspan = 2
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

    def run(self, dataOut, id, wintitle="", channelList=None, showprofile=True,
            xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None,
            save=False, figpath='./', figfile=None, show=True, ftp=False, wr_period=1,
            server=None, folder=None, username=None, password=None,
            ftp_wei=0, exp_code=0, sub_exp_code=0, plot_pos=0, realtime=False,
            xaxis="frequency", colormap='jet', normFactor=None , GauSelector = 1):

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
        if realtime:
            if not(isRealtime(utcdatatime = dataOut.utctime)):
                print 'Skipping this plot function'
                return

        if channelList == None:
            channelIndexList = dataOut.channelIndexList
        else:
            channelIndexList = []
            for channel in channelList:
                if channel not in dataOut.channelList:
                    raise ValueError, "Channel %d is not in dataOut.channelList" %channel
                channelIndexList.append(dataOut.channelList.index(channel))

#         if normFactor is None:
#             factor = dataOut.normFactor
#         else:
#             factor = normFactor
        if xaxis == "frequency":
            x = dataOut.spc_range[0]
            xlabel = "Frequency (kHz)"

        elif xaxis == "time":
            x = dataOut.spc_range[1]
            xlabel = "Time (ms)"

        else:
            x = dataOut.spc_range[2]
            xlabel = "Velocity (m/s)"

        ylabel = "Range (Km)"

        y = dataOut.getHeiRange()

        z = dataOut.GauSPC[:,GauSelector,:,:] #GauSelector]    #dataOut.data_spc/factor
        print 'GausSPC', z[0,32,10:40]
        z = numpy.where(numpy.isfinite(z), z, numpy.NAN)
        zdB = 10*numpy.log10(z)

        avg = numpy.average(z, axis=1)
        avgdB = 10*numpy.log10(avg)

        noise = dataOut.spc_noise
        noisedB = 10*numpy.log10(noise)

        thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.getTimeRange()[0])
        title = wintitle + " Spectra"
        if ((dataOut.azimuth!=None) and (dataOut.zenith!=None)):
            title = title + '_' + 'azimuth,zenith=%2.2f,%2.2f'%(dataOut.azimuth, dataOut.zenith)

        if not self.isConfig:

            nplots = len(channelIndexList)

            self.setup(id=id,
                       nplots=nplots,
                       wintitle=wintitle,
                       showprofile=showprofile,
                       show=show)

            if xmin == None: xmin = numpy.nanmin(x)
            if xmax == None: xmax = numpy.nanmax(x)
            if ymin == None: ymin = numpy.nanmin(y)
            if ymax == None: ymax = numpy.nanmax(y)
            if zmin == None: zmin = numpy.floor(numpy.nanmin(noisedB)) - 3
            if zmax == None: zmax = numpy.ceil(numpy.nanmax(avgdB)) + 3

            self.FTP_WEI = ftp_wei
            self.EXP_CODE = exp_code
            self.SUB_EXP_CODE = sub_exp_code
            self.PLOT_POS = plot_pos

            self.isConfig = True

        self.setWinTitle(title)

        for i in range(self.nplots):
            index = channelIndexList[i]
            str_datetime = '%s %s'%(thisDatetime.strftime("%Y/%m/%d"),thisDatetime.strftime("%H:%M:%S"))
            title = "Channel %d: %4.2fdB: %s" %(dataOut.channelList[index], noisedB[index], str_datetime)
            if len(dataOut.beam.codeList) != 0:
                title = "Ch%d:%4.2fdB,%2.2f,%2.2f:%s" %(dataOut.channelList[index], noisedB[index], dataOut.beam.azimuthList[index], dataOut.beam.zenithList[index], str_datetime)

            axes = self.axesList[i*self.__nsubplots]
            axes.pcolor(x, y, zdB[index,:,:],
                        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, zmin=zmin, zmax=zmax,
                        xlabel=xlabel, ylabel=ylabel, title=title, colormap=colormap,
                        ticksize=9, cblabel='')

            if self.__showprofile:
                axes = self.axesList[i*self.__nsubplots +1]
                axes.pline(avgdB[index,:], y,
                        xmin=zmin, xmax=zmax, ymin=ymin, ymax=ymax,
                        xlabel='dB', ylabel='', title='',
                        ytick_visible=False,
                        grid='x')

                noiseline = numpy.repeat(noisedB[index], len(y))
                axes.addpline(noiseline, y, idline=1, color="black", linestyle="dashed", lw=2)

        self.draw()

        if figfile == None:
            str_datetime = thisDatetime.strftime("%Y%m%d_%H%M%S")
            name = str_datetime
            if ((dataOut.azimuth!=None) and (dataOut.zenith!=None)):
                name = name + '_az' + '_%2.2f'%(dataOut.azimuth) + '_zn' + '_%2.2f'%(dataOut.zenith)
            figfile = self.getFilename(name)

        self.save(figpath=figpath,
                  figfile=figfile,
                  save=save,
                  ftp=ftp,
                  wr_period=wr_period,
                  thisDatetime=thisDatetime)



class MomentsPlot(Figure):

    isConfig = None
    __nsubplots = None

    WIDTHPROF = None
    HEIGHTPROF = None
    PREFIX = 'prm'

    def __init__(self, **kwargs):
        Figure.__init__(self, **kwargs)
        self.isConfig = False
        self.__nsubplots = 1

        self.WIDTH = 280
        self.HEIGHT = 250
        self.WIDTHPROF = 120
        self.HEIGHTPROF = 0
        self.counter_imagwr = 0

        self.PLOT_CODE = MOMENTS_CODE

        self.FTP_WEI = None
        self.EXP_CODE = None
        self.SUB_EXP_CODE = None
        self.PLOT_POS = None

    def getSubplots(self):

        ncol = int(numpy.sqrt(self.nplots)+0.9)
        nrow = int(self.nplots*1./ncol + 0.9)

        return nrow, ncol

    def setup(self, id, nplots, wintitle, showprofile=True, show=True):

        self.__showprofile = showprofile
        self.nplots = nplots

        ncolspan = 1
        colspan = 1
        if showprofile:
            ncolspan = 3
            colspan = 2
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

    def run(self, dataOut, id, wintitle="", channelList=None, showprofile=True,
            xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None,
            save=False, figpath='./', figfile=None, show=True, ftp=False, wr_period=1,
            server=None, folder=None, username=None, password=None,
            ftp_wei=0, exp_code=0, sub_exp_code=0, plot_pos=0, realtime=False):

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

        if dataOut.flagNoData:
            return None

        if realtime:
            if not(isRealtime(utcdatatime = dataOut.utctime)):
                print 'Skipping this plot function'
                return

        if channelList == None:
            channelIndexList = dataOut.channelIndexList
        else:
            channelIndexList = []
            for channel in channelList:
                if channel not in dataOut.channelList:
                    raise ValueError, "Channel %d is not in dataOut.channelList"
                channelIndexList.append(dataOut.channelList.index(channel))

        factor = dataOut.normFactor
        x = dataOut.abscissaList
        y = dataOut.heightList

        z = dataOut.data_pre[channelIndexList,:,:]/factor
        z = numpy.where(numpy.isfinite(z), z, numpy.NAN)
        avg = numpy.average(z, axis=1)
        noise = dataOut.noise/factor

        zdB = 10*numpy.log10(z)
        avgdB = 10*numpy.log10(avg)
        noisedB = 10*numpy.log10(noise)

        #thisDatetime = dataOut.datatime
        thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.getTimeRange()[0])
        title = wintitle + " Parameters"
        xlabel = "Velocity (m/s)"
        ylabel = "Range (Km)"

        update_figfile = False

        if not self.isConfig:

            nplots = len(channelIndexList)

            self.setup(id=id,
                       nplots=nplots,
                       wintitle=wintitle,
                       showprofile=showprofile,
                       show=show)

            if xmin == None: xmin = numpy.nanmin(x)
            if xmax == None: xmax = numpy.nanmax(x)
            if ymin == None: ymin = numpy.nanmin(y)
            if ymax == None: ymax = numpy.nanmax(y)
            if zmin == None: zmin = numpy.nanmin(avgdB)*0.9
            if zmax == None: zmax = numpy.nanmax(avgdB)*0.9

            self.FTP_WEI = ftp_wei
            self.EXP_CODE = exp_code
            self.SUB_EXP_CODE = sub_exp_code
            self.PLOT_POS = plot_pos

            self.isConfig = True
            update_figfile = True

        self.setWinTitle(title)

        for i in range(self.nplots):
            str_datetime = '%s %s'%(thisDatetime.strftime("%Y/%m/%d"),thisDatetime.strftime("%H:%M:%S"))
            title = "Channel %d: %4.2fdB: %s" %(dataOut.channelList[i], noisedB[i], str_datetime)
            axes = self.axesList[i*self.__nsubplots]
            axes.pcolor(x, y, zdB[i,:,:],
                        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, zmin=zmin, zmax=zmax,
                        xlabel=xlabel, ylabel=ylabel, title=title,
                        ticksize=9, cblabel='')
                        #Mean Line
            mean = dataOut.data_param[i, 1, :]
            axes.addpline(mean, y, idline=0, color="black", linestyle="solid", lw=1)

            if self.__showprofile:
                axes = self.axesList[i*self.__nsubplots +1]
                axes.pline(avgdB[i], y,
                        xmin=zmin, xmax=zmax, ymin=ymin, ymax=ymax,
                        xlabel='dB', ylabel='', title='',
                        ytick_visible=False,
                        grid='x')

                noiseline = numpy.repeat(noisedB[i], len(y))
                axes.addpline(noiseline, y, idline=1, color="black", linestyle="dashed", lw=2)

        self.draw()

        self.save(figpath=figpath,
                  figfile=figfile,
                  save=save,
                  ftp=ftp,
                  wr_period=wr_period,
                  thisDatetime=thisDatetime)



class SkyMapPlot(Figure):

    __isConfig = None
    __nsubplots = None

    WIDTHPROF = None
    HEIGHTPROF = None
    PREFIX = 'mmap'

    def __init__(self, **kwargs):
        Figure.__init__(self, **kwargs)
        self.isConfig = False
        self.__nsubplots = 1

#         self.WIDTH = 280
#         self.HEIGHT = 250
        self.WIDTH = 600
        self.HEIGHT = 600
        self.WIDTHPROF = 120
        self.HEIGHTPROF = 0
        self.counter_imagwr = 0

        self.PLOT_CODE = MSKYMAP_CODE

        self.FTP_WEI = None
        self.EXP_CODE = None
        self.SUB_EXP_CODE = None
        self.PLOT_POS = None

    def getSubplots(self):

        ncol = int(numpy.sqrt(self.nplots)+0.9)
        nrow = int(self.nplots*1./ncol + 0.9)

        return nrow, ncol

    def setup(self, id, nplots, wintitle, showprofile=False, show=True):

        self.__showprofile = showprofile
        self.nplots = nplots

        ncolspan = 1
        colspan = 1

        self.createFigure(id = id,
                          wintitle = wintitle,
                          widthplot = self.WIDTH, #+ self.WIDTHPROF,
                          heightplot = self.HEIGHT,# + self.HEIGHTPROF,
                          show=show)

        nrow, ncol = 1,1
        counter = 0
        x = 0
        y = 0
        self.addAxes(1, 1, 0, 0, 1, 1, True)

    def run(self, dataOut, id, wintitle="", channelList=None, showprofile=False,
            tmin=0, tmax=24, timerange=None,
            save=False, figpath='./', figfile=None, show=True, ftp=False, wr_period=1,
            server=None, folder=None, username=None, password=None,
            ftp_wei=0, exp_code=0, sub_exp_code=0, plot_pos=0, realtime=False):

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

        arrayParameters = dataOut.data_param
        error = arrayParameters[:,-1]
        indValid = numpy.where(error == 0)[0]
        finalMeteor = arrayParameters[indValid,:]
        finalAzimuth = finalMeteor[:,3]
        finalZenith = finalMeteor[:,4]

        x = finalAzimuth*numpy.pi/180
        y = finalZenith
        x1 = [dataOut.ltctime, dataOut.ltctime]

        #thisDatetime = dataOut.datatime
        thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.ltctime)
        title = wintitle + " Parameters"
        xlabel = "Zonal Zenith Angle (deg) "
        ylabel = "Meridional Zenith Angle (deg)"
        update_figfile = False

        if not self.isConfig:

            nplots = 1

            self.setup(id=id,
                       nplots=nplots,
                       wintitle=wintitle,
                       showprofile=showprofile,
                       show=show)

            if self.xmin is None and self.xmax is None:
                self.xmin, self.xmax = self.getTimeLim(x1, tmin, tmax, timerange)

            if timerange != None:
                self.timerange = timerange
            else:
                self.timerange = self.xmax - self.xmin

            self.FTP_WEI = ftp_wei
            self.EXP_CODE = exp_code
            self.SUB_EXP_CODE = sub_exp_code
            self.PLOT_POS = plot_pos
            self.name = thisDatetime.strftime("%Y%m%d_%H%M%S")
            self.firstdate = '%s %s'%(thisDatetime.strftime("%Y/%m/%d"),thisDatetime.strftime("%H:%M:%S"))
            self.isConfig = True
            update_figfile = True

        self.setWinTitle(title)

        i = 0
        str_datetime = '%s %s'%(thisDatetime.strftime("%Y/%m/%d"),thisDatetime.strftime("%H:%M:%S"))

        axes = self.axesList[i*self.__nsubplots]
        nevents = axes.x_buffer.shape[0] + x.shape[0]
        title = "Meteor Detection Sky Map\n %s - %s \n Number of events: %5.0f\n" %(self.firstdate,str_datetime,nevents)
        axes.polar(x, y,
                    title=title, xlabel=xlabel, ylabel=ylabel,
                    ticksize=9, cblabel='')

        self.draw()

        self.save(figpath=figpath,
                  figfile=figfile,
                  save=save,
                  ftp=ftp,
                  wr_period=wr_period,
                  thisDatetime=thisDatetime,
                  update_figfile=update_figfile)

        if dataOut.ltctime >= self.xmax:
            self.isConfigmagwr = wr_period
            self.isConfig = False
            update_figfile = True
            axes.__firsttime = True
            self.xmin += self.timerange
            self.xmax += self.timerange




class WindProfilerPlot(Figure):

    __isConfig = None
    __nsubplots = None

    WIDTHPROF = None
    HEIGHTPROF = None
    PREFIX = 'wind'

    def __init__(self, **kwargs):
        Figure.__init__(self, **kwargs)
        self.timerange = None
        self.isConfig = False
        self.__nsubplots = 1

        self.WIDTH = 800
        self.HEIGHT = 300
        self.WIDTHPROF = 120
        self.HEIGHTPROF = 0
        self.counter_imagwr = 0

        self.PLOT_CODE = WIND_CODE

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

        self.createFigure(id = id,
                          wintitle = wintitle,
                          widthplot = self.WIDTH + self.WIDTHPROF,
                          heightplot = self.HEIGHT + self.HEIGHTPROF,
                          show=show)

        nrow, ncol = self.getSubplots()

        counter = 0
        for y in range(nrow):
            if counter >= self.nplots:
                break

            self.addAxes(nrow, ncol*ncolspan, y, 0, colspan, 1)
            counter += 1

    def run(self, dataOut, id, wintitle="", channelList=None, showprofile='False',
            xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None,
            zmax_ver = None, zmin_ver = None, SNRmin = None, SNRmax = None,
            timerange=None, SNRthresh = None,
            save=False, figpath='./', lastone=0,figfile=None, ftp=False, wr_period=1, show=True,
            server=None, folder=None, username=None, password=None,
            ftp_wei=0, exp_code=0, sub_exp_code=0, plot_pos=0):
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

#         if timerange is not None:
#             self.timerange = timerange
#
#         tmin = None
#         tmax = None

        x = dataOut.getTimeRange1(dataOut.paramInterval)
        y = dataOut.heightList
        z = dataOut.data_output.copy()
        print ' '
        print 'Xvel',z[0]
        print ' '
        print 'Yvel',z[1]
        print ' '
        nplots = z.shape[0]    #Number of wind dimensions estimated
        nplotsw = nplots


        #If there is a SNR function defined
        if dataOut.data_SNR is not None:
            nplots += 1
            SNR = dataOut.data_SNR
            SNRavg = numpy.average(SNR, axis=0)

            SNRdB = 10*numpy.log10(SNR)
            SNRavgdB = 10*numpy.log10(SNRavg)

            if SNRthresh == None: SNRthresh = -5.0
            ind = numpy.where(SNRavg < 10**(SNRthresh/10))[0]

            for i in range(nplotsw):
                z[i,ind] = numpy.nan

        thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.ltctime)
        #thisDatetime = datetime.datetime.now()
        title = wintitle + "Wind"
        xlabel = ""
        ylabel = "Height (km)"
        update_figfile = False

        if not self.isConfig:

            self.setup(id=id,
                       nplots=nplots,
                       wintitle=wintitle,
                       showprofile=showprofile,
                       show=show)

            if timerange is not None:
                self.timerange = timerange

            self.xmin, self.xmax = self.getTimeLim(x, xmin, xmax, timerange)

            if ymin == None: ymin = numpy.nanmin(y)
            if ymax == None: ymax = numpy.nanmax(y)

            if zmax == None: zmax = numpy.nanmax(abs(z[range(2),:]))
            #if numpy.isnan(zmax): zmax = 50
            if zmin == None: zmin = -zmax

            if nplotsw == 3:
                if zmax_ver == None: zmax_ver = numpy.nanmax(abs(z[2,:]))
                if zmin_ver == None: zmin_ver = -zmax_ver

            if dataOut.data_SNR is not None:
                if SNRmin == None:  SNRmin = numpy.nanmin(SNRavgdB)
                if SNRmax == None:  SNRmax = numpy.nanmax(SNRavgdB)


            self.FTP_WEI = ftp_wei
            self.EXP_CODE = exp_code
            self.SUB_EXP_CODE = sub_exp_code
            self.PLOT_POS = plot_pos

            self.name = thisDatetime.strftime("%Y%m%d_%H%M%S")
            self.isConfig = True
            self.figfile = figfile
            update_figfile = True

        self.setWinTitle(title)

        if ((self.xmax - x[1]) < (x[1]-x[0])):
            x[1] = self.xmax

        strWind = ['Zonal', 'Meridional', 'Vertical']
        strCb = ['Velocity (m/s)','Velocity (m/s)','Velocity (cm/s)']
        zmaxVector = [zmax, zmax, zmax_ver]
        zminVector = [zmin, zmin, zmin_ver]
        windFactor = [1,1,100]

        for i in range(nplotsw):

            title = "%s Wind: %s" %(strWind[i], thisDatetime.strftime("%Y/%m/%d %H:%M:%S"))
            axes = self.axesList[i*self.__nsubplots]

            z1 = z[i,:].reshape((1,-1))*windFactor[i]
            #z1=numpy.ma.masked_where(z1==0.,z1)

            axes.pcolorbuffer(x, y, z1,
                        xmin=self.xmin, xmax=self.xmax, ymin=ymin, ymax=ymax, zmin=zminVector[i], zmax=zmaxVector[i],
                        xlabel=xlabel, ylabel=ylabel, title=title, rti=True, XAxisAsTime=True,
                        ticksize=9, cblabel=strCb[i], cbsize="1%", colormap="seismic" )

        if dataOut.data_SNR is not None:
            i += 1
            title = "Signal Noise Ratio (SNR): %s" %(thisDatetime.strftime("%Y/%m/%d %H:%M:%S"))
            axes = self.axesList[i*self.__nsubplots]
            SNRavgdB = SNRavgdB.reshape((1,-1))
            axes.pcolorbuffer(x, y, SNRavgdB,
                        xmin=self.xmin, xmax=self.xmax, ymin=ymin, ymax=ymax, zmin=SNRmin, zmax=SNRmax,
                        xlabel=xlabel, ylabel=ylabel, title=title, rti=True, XAxisAsTime=True,
                        ticksize=9, cblabel='', cbsize="1%", colormap="jet")

        self.draw()

        self.save(figpath=figpath,
                  figfile=figfile,
                  save=save,
                  ftp=ftp,
                  wr_period=wr_period,
                  thisDatetime=thisDatetime,
                  update_figfile=update_figfile)

        if dataOut.ltctime + dataOut.paramInterval >= self.xmax:
            self.counter_imagwr = wr_period
            self.isConfig = False
            update_figfile = True


class ParametersPlot(Figure):

    __isConfig = None
    __nsubplots = None

    WIDTHPROF = None
    HEIGHTPROF = None
    PREFIX = 'param'

    nplots = None
    nchan = None

    def __init__(self, **kwargs):
        Figure.__init__(self, **kwargs)
        self.timerange = None
        self.isConfig = False
        self.__nsubplots = 1

        self.WIDTH = 800
        self.HEIGHT = 180
        self.WIDTHPROF = 120
        self.HEIGHTPROF = 0
        self.counter_imagwr = 0

        self.PLOT_CODE = RTI_CODE

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

    def setup(self, id, nplots, wintitle, show=True):

        self.nplots = nplots

        ncolspan = 1
        colspan = 1

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

                counter += 1

    def run(self, dataOut, id, wintitle="", channelList=None, paramIndex = 0, colormap="jet",
            xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None, timerange=None,
            showSNR=False, SNRthresh = -numpy.inf, SNRmin=None, SNRmax=None,
            save=False, figpath='./', lastone=0,figfile=None, ftp=False, wr_period=1, show=True,
            server=None, folder=None, username=None, password=None,
            ftp_wei=0, exp_code=0, sub_exp_code=0, plot_pos=0, HEIGHT=None):
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
        
        if HEIGHT is not None:
            self.HEIGHT = HEIGHT
        
        
        if not isTimeInHourRange(dataOut.datatime, xmin, xmax):
            return

        if channelList == None:
            channelIndexList = range(dataOut.data_param.shape[0])
        else:
            channelIndexList = []
            for channel in channelList:
                if channel not in dataOut.channelList:
                    raise ValueError, "Channel %d is not in dataOut.channelList"
                channelIndexList.append(dataOut.channelList.index(channel))

        x = dataOut.getTimeRange1(dataOut.paramInterval)
        y = dataOut.getHeiRange()

        if dataOut.data_param.ndim == 3:
            z = dataOut.data_param[channelIndexList,paramIndex,:]
        else:
            z = dataOut.data_param[channelIndexList,:]

        if showSNR:
            #SNR data
            SNRarray = dataOut.data_SNR[channelIndexList,:]
            SNRdB = 10*numpy.log10(SNRarray)
            ind = numpy.where(SNRdB < SNRthresh)
            z[ind] = numpy.nan

        thisDatetime = dataOut.datatime
#         thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.getTimeRange()[0])
        title = wintitle + " Parameters Plot" #: %s" %(thisDatetime.strftime("%d-%b-%Y"))
        xlabel = ""
        ylabel = "Range (Km)"

        update_figfile = False

        if not self.isConfig:

            nchan = len(channelIndexList)
            self.nchan = nchan
            self.plotFact = 1
            nplots = nchan

            if showSNR:
                nplots = nchan*2
                self.plotFact = 2
                if SNRmin == None:  SNRmin = numpy.nanmin(SNRdB)
                if SNRmax == None:  SNRmax = numpy.nanmax(SNRdB)

            self.setup(id=id,
                       nplots=nplots,
                       wintitle=wintitle,
                       show=show)

            if timerange != None:
                self.timerange = timerange

            self.xmin, self.xmax = self.getTimeLim(x, xmin, xmax, timerange)

            if ymin == None: ymin = numpy.nanmin(y)
            if ymax == None: ymax = numpy.nanmax(y)
            if zmin == None: zmin = numpy.nanmin(z)
            if zmax == None: zmax = numpy.nanmax(z)

            self.FTP_WEI = ftp_wei
            self.EXP_CODE = exp_code
            self.SUB_EXP_CODE = sub_exp_code
            self.PLOT_POS = plot_pos

            self.name = thisDatetime.strftime("%Y%m%d_%H%M%S")
            self.isConfig = True
            self.figfile = figfile
            update_figfile = True

        self.setWinTitle(title)

        for i in range(self.nchan):
            index = channelIndexList[i]
            title = "Channel %d: %s" %(dataOut.channelList[index], thisDatetime.strftime("%Y/%m/%d %H:%M:%S"))
            axes = self.axesList[i*self.plotFact]
            z1 = z[i,:].reshape((1,-1))
            axes.pcolorbuffer(x, y, z1,
                        xmin=self.xmin, xmax=self.xmax, ymin=ymin, ymax=ymax, zmin=zmin, zmax=zmax,
                        xlabel=xlabel, ylabel=ylabel, title=title, rti=True, XAxisAsTime=True,
                        ticksize=9, cblabel='', cbsize="1%",colormap=colormap)

            if showSNR:
                title = "Channel %d SNR: %s" %(dataOut.channelList[index], thisDatetime.strftime("%Y/%m/%d %H:%M:%S"))
                axes = self.axesList[i*self.plotFact + 1]
                SNRdB1 = SNRdB[i,:].reshape((1,-1))
                axes.pcolorbuffer(x, y, SNRdB1,
                        xmin=self.xmin, xmax=self.xmax, ymin=ymin, ymax=ymax, zmin=SNRmin, zmax=SNRmax,
                        xlabel=xlabel, ylabel=ylabel, title=title, rti=True, XAxisAsTime=True,
                        ticksize=9, cblabel='', cbsize="1%",colormap='jet')


        self.draw()

        if dataOut.ltctime >= self.xmax:
            self.counter_imagwr = wr_period
            self.isConfig = False
            update_figfile = True

        self.save(figpath=figpath,
                  figfile=figfile,
                  save=save,
                  ftp=ftp,
                  wr_period=wr_period,
                  thisDatetime=thisDatetime,
                  update_figfile=update_figfile)



class Parameters1Plot(Figure):

    __isConfig = None
    __nsubplots = None

    WIDTHPROF = None
    HEIGHTPROF = None
    PREFIX = 'prm'

    def __init__(self, **kwargs):
        Figure.__init__(self, **kwargs)
        self.timerange = 2*60*60
        self.isConfig = False
        self.__nsubplots = 1

        self.WIDTH = 800
        self.HEIGHT = 180
        self.WIDTHPROF = 120
        self.HEIGHTPROF = 0
        self.counter_imagwr = 0

        self.PLOT_CODE = PARMS_CODE

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

    def run(self, dataOut, id, wintitle="", channelList=None, showprofile=False,
            xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None,timerange=None,
            parameterIndex = None, onlyPositive = False,
            SNRthresh = -numpy.inf, SNR = True, SNRmin = None, SNRmax = None, onlySNR = False,
            DOP = True,
            zlabel = "", parameterName = "", parameterObject = "data_param",
            save=False, figpath='./', lastone=0,figfile=None, ftp=False, wr_period=1, show=True,
            server=None, folder=None, username=None, password=None,
            ftp_wei=0, exp_code=0, sub_exp_code=0, plot_pos=0):
        #print inspect.getargspec(self.run).args
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

        data_param = getattr(dataOut, parameterObject)

        if channelList == None:
            channelIndexList = numpy.arange(data_param.shape[0])
        else:
            channelIndexList = numpy.array(channelList)

        nchan = len(channelIndexList) #Number of channels being plotted

        if nchan < 1:
            return

        nGraphsByChannel = 0

        if SNR:
            nGraphsByChannel += 1
        if DOP:
            nGraphsByChannel += 1

        if nGraphsByChannel < 1:
            return

        nplots = nGraphsByChannel*nchan

        if timerange is not None:
            self.timerange = timerange

        #tmin = None
        #tmax = None
        if parameterIndex == None:
            parameterIndex = 1

        x = dataOut.getTimeRange1(dataOut.paramInterval)
        y = dataOut.heightList
        z = data_param[channelIndexList,parameterIndex,:].copy()

        zRange = dataOut.abscissaList
#         nChannels = z.shape[0]    #Number of wind dimensions estimated
#        thisDatetime = dataOut.datatime

        if dataOut.data_SNR is not None:
            SNRarray = dataOut.data_SNR[channelIndexList,:]
            SNRdB = 10*numpy.log10(SNRarray)
#             SNRavgdB = 10*numpy.log10(SNRavg)
            ind = numpy.where(SNRdB < 10**(SNRthresh/10))
            z[ind] = numpy.nan

        thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.getTimeRange()[0])
        title = wintitle + " Parameters Plot" #: %s" %(thisDatetime.strftime("%d-%b-%Y"))
        xlabel = ""
        ylabel = "Range (Km)"

        if (SNR and not onlySNR): nplots = 2*nplots

        if onlyPositive:
            colormap = "jet"
            zmin = 0
        else: colormap = "RdBu_r"

        if not self.isConfig:

            self.setup(id=id,
                       nplots=nplots,
                       wintitle=wintitle,
                       showprofile=showprofile,
                       show=show)

            self.xmin, self.xmax = self.getTimeLim(x, xmin, xmax, timerange)

            if ymin == None: ymin = numpy.nanmin(y)
            if ymax == None: ymax = numpy.nanmax(y)
            if zmin == None: zmin = numpy.nanmin(zRange)
            if zmax == None: zmax = numpy.nanmax(zRange)

            if SNR:
                if SNRmin == None:  SNRmin = numpy.nanmin(SNRdB)
                if SNRmax == None:  SNRmax = numpy.nanmax(SNRdB)

            self.FTP_WEI = ftp_wei
            self.EXP_CODE = exp_code
            self.SUB_EXP_CODE = sub_exp_code
            self.PLOT_POS = plot_pos

            self.name = thisDatetime.strftime("%Y%m%d_%H%M%S")
            self.isConfig = True
            self.figfile = figfile

        self.setWinTitle(title)

        if ((self.xmax - x[1]) < (x[1]-x[0])):
            x[1] = self.xmax

        for i in range(nchan):

            if (SNR and not onlySNR): j = 2*i
            else: j = i

            j = nGraphsByChannel*i

            if ((dataOut.azimuth!=None) and (dataOut.zenith!=None)):
                title = title + '_' + 'azimuth,zenith=%2.2f,%2.2f'%(dataOut.azimuth, dataOut.zenith)

            if not onlySNR:
                axes = self.axesList[j*self.__nsubplots]
                z1 = z[i,:].reshape((1,-1))
                axes.pcolorbuffer(x, y, z1,
                        xmin=self.xmin, xmax=self.xmax, ymin=ymin, ymax=ymax, zmin=zmin, zmax=zmax,
                        xlabel=xlabel, ylabel=ylabel, title=title, rti=True, XAxisAsTime=True,colormap=colormap,
                        ticksize=9, cblabel=zlabel, cbsize="1%")

            if DOP:
                title = "%s Channel %d: %s" %(parameterName, channelIndexList[i], thisDatetime.strftime("%Y/%m/%d %H:%M:%S"))

                if ((dataOut.azimuth!=None) and (dataOut.zenith!=None)):
                    title = title + '_' + 'azimuth,zenith=%2.2f,%2.2f'%(dataOut.azimuth, dataOut.zenith)
                axes = self.axesList[j]
                z1 = z[i,:].reshape((1,-1))
                axes.pcolorbuffer(x, y, z1,
                            xmin=self.xmin, xmax=self.xmax, ymin=ymin, ymax=ymax, zmin=zmin, zmax=zmax,
                            xlabel=xlabel, ylabel=ylabel, title=title, rti=True, XAxisAsTime=True,colormap=colormap,
                            ticksize=9, cblabel=zlabel, cbsize="1%")

            if SNR:
                title = "Channel %d Signal Noise Ratio (SNR): %s" %(channelIndexList[i], thisDatetime.strftime("%Y/%m/%d %H:%M:%S"))
                axes = self.axesList[(j)*self.__nsubplots]
                if not onlySNR:
                    axes = self.axesList[(j + 1)*self.__nsubplots]

                axes = self.axesList[(j + nGraphsByChannel-1)]

                z1 = SNRdB[i,:].reshape((1,-1))
                axes.pcolorbuffer(x, y, z1,
                        xmin=self.xmin, xmax=self.xmax, ymin=ymin, ymax=ymax, zmin=SNRmin, zmax=SNRmax,
                        xlabel=xlabel, ylabel=ylabel, title=title, rti=True, XAxisAsTime=True,colormap="jet",
                        ticksize=9, cblabel=zlabel, cbsize="1%")



        self.draw()

        if x[1] >= self.axesList[0].xmax:
            self.counter_imagwr = wr_period
            self.isConfig = False
            self.figfile = None

        self.save(figpath=figpath,
                  figfile=figfile,
                  save=save,
                  ftp=ftp,
                  wr_period=wr_period,
                  thisDatetime=thisDatetime,
                  update_figfile=False)

class SpectralFittingPlot(Figure):

    __isConfig = None
    __nsubplots = None

    WIDTHPROF = None
    HEIGHTPROF = None
    PREFIX = 'prm'


    N = None
    ippSeconds = None

    def __init__(self, **kwargs):
        Figure.__init__(self, **kwargs)
        self.isConfig = False
        self.__nsubplots = 1

        self.PLOT_CODE = SPECFIT_CODE

        self.WIDTH = 450
        self.HEIGHT = 250
        self.WIDTHPROF = 0
        self.HEIGHTPROF = 0

    def getSubplots(self):

        ncol = int(numpy.sqrt(self.nplots)+0.9)
        nrow = int(self.nplots*1./ncol + 0.9)

        return nrow, ncol

    def setup(self, id, nplots, wintitle, showprofile=False, show=True):

        showprofile = False
        self.__showprofile = showprofile
        self.nplots = nplots

        ncolspan = 5
        colspan = 4
        if showprofile:
            ncolspan = 5
            colspan = 4
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

    def run(self, dataOut, id, cutHeight=None, fit=False, wintitle="", channelList=None, showprofile=True,
            xmin=None, xmax=None, ymin=None, ymax=None,
            save=False, figpath='./', figfile=None, show=True):

        """

        Input:
            dataOut         :
            id        :
            wintitle        :
            channelList     :
            showProfile     :
            xmin            :    None,
            xmax            :    None,
            zmin            :    None,
            zmax            :    None
        """

        if cutHeight==None:
            h=270
        heightindex = numpy.abs(cutHeight - dataOut.heightList).argmin()
        cutHeight = dataOut.heightList[heightindex]

        factor = dataOut.normFactor
        x = dataOut.abscissaList[:-1]
        #y = dataOut.getHeiRange()

        z = dataOut.data_pre[:,:,heightindex]/factor
        z = numpy.where(numpy.isfinite(z), z, numpy.NAN)
        avg = numpy.average(z, axis=1)
        listChannels = z.shape[0]

        #Reconstruct Function
        if fit==True:
            groupArray = dataOut.groupList
            listChannels = groupArray.reshape((groupArray.size))
            listChannels.sort()
            spcFitLine = numpy.zeros(z.shape)
            constants = dataOut.constants

            nGroups = groupArray.shape[0]
            nChannels = groupArray.shape[1]
            nProfiles = z.shape[1]

            for f in range(nGroups):
                groupChann = groupArray[f,:]
                p = dataOut.data_param[f,:,heightindex]
#                 p = numpy.array([ 89.343967,0.14036615,0.17086219,18.89835291,1.58388365,1.55099167])
                fitLineAux = dataOut.library.modelFunction(p, constants)*nProfiles
                fitLineAux = fitLineAux.reshape((nChannels,nProfiles))
                spcFitLine[groupChann,:] = fitLineAux
#             spcFitLine = spcFitLine/factor

            z = z[listChannels,:]
            spcFitLine = spcFitLine[listChannels,:]
            spcFitLinedB = 10*numpy.log10(spcFitLine)

        zdB = 10*numpy.log10(z)
        #thisDatetime = dataOut.datatime
        thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.getTimeRange()[0])
        title = wintitle + " Doppler Spectra: %s" %(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
        xlabel = "Velocity (m/s)"
        ylabel = "Spectrum"

        if not self.isConfig:

            nplots = listChannels.size

            self.setup(id=id,
                       nplots=nplots,
                       wintitle=wintitle,
                       showprofile=showprofile,
                       show=show)

            if xmin == None: xmin = numpy.nanmin(x)
            if xmax == None: xmax = numpy.nanmax(x)
            if ymin == None: ymin = numpy.nanmin(zdB)
            if ymax == None: ymax = numpy.nanmax(zdB)+2

            self.isConfig = True

        self.setWinTitle(title)
        for i in range(self.nplots):
#             title = "Channel %d: %4.2fdB" %(dataOut.channelList[i]+1, noisedB[i])
            title = "Height %4.1f km\nChannel %d:" %(cutHeight, listChannels[i])
            axes = self.axesList[i*self.__nsubplots]
            if fit == False:
                axes.pline(x, zdB[i,:],
                            xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,
                            xlabel=xlabel, ylabel=ylabel, title=title
                            )
            if fit == True:
                fitline=spcFitLinedB[i,:]
                y=numpy.vstack([zdB[i,:],fitline] )
                legendlabels=['Data','Fitting']
                axes.pmultilineyaxis(x, y,
                            xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,
                            xlabel=xlabel, ylabel=ylabel, title=title,
                            legendlabels=legendlabels, marker=None,
                            linestyle='solid', grid='both')

        self.draw()

        self.save(figpath=figpath,
                  figfile=figfile,
                  save=save,
                  ftp=ftp,
                  wr_period=wr_period,
                  thisDatetime=thisDatetime)


class EWDriftsPlot(Figure):

    __isConfig = None
    __nsubplots = None

    WIDTHPROF = None
    HEIGHTPROF = None
    PREFIX = 'drift'

    def __init__(self, **kwargs):
        Figure.__init__(self, **kwargs)
        self.timerange = 2*60*60
        self.isConfig = False
        self.__nsubplots = 1

        self.WIDTH = 800
        self.HEIGHT = 150
        self.WIDTHPROF = 120
        self.HEIGHTPROF = 0
        self.counter_imagwr = 0

        self.PLOT_CODE = EWDRIFT_CODE

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

        self.createFigure(id = id,
                          wintitle = wintitle,
                          widthplot = self.WIDTH + self.WIDTHPROF,
                          heightplot = self.HEIGHT + self.HEIGHTPROF,
                          show=show)

        nrow, ncol = self.getSubplots()

        counter = 0
        for y in range(nrow):
            if counter >= self.nplots:
                break

            self.addAxes(nrow, ncol*ncolspan, y, 0, colspan, 1)
            counter += 1

    def run(self, dataOut, id, wintitle="", channelList=None,
            xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None,
            zmaxVertical = None, zminVertical = None, zmaxZonal = None, zminZonal = None,
            timerange=None, SNRthresh = -numpy.inf, SNRmin = None, SNRmax = None, SNR_1 = False,
            save=False, figpath='./', lastone=0,figfile=None, ftp=False, wr_period=1, show=True,
            server=None, folder=None, username=None, password=None,
            ftp_wei=0, exp_code=0, sub_exp_code=0, plot_pos=0):
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

        if timerange is not None:
            self.timerange = timerange

        tmin = None
        tmax = None

        x = dataOut.getTimeRange1(dataOut.outputInterval)
#         y = dataOut.heightList
        y = dataOut.heightList

        z = dataOut.data_output
        nplots = z.shape[0]    #Number of wind dimensions estimated
        nplotsw = nplots

        #If there is a SNR function defined
        if dataOut.data_SNR is not None:
            nplots += 1
            SNR = dataOut.data_SNR

            if SNR_1:
                SNR += 1

            SNRavg = numpy.average(SNR, axis=0)

            SNRdB = 10*numpy.log10(SNR)
            SNRavgdB = 10*numpy.log10(SNRavg)

            ind = numpy.where(SNRavg < 10**(SNRthresh/10))[0]

            for i in range(nplotsw):
                z[i,ind] = numpy.nan


        showprofile = False
#        thisDatetime = dataOut.datatime
        thisDatetime = datetime.datetime.utcfromtimestamp(x[1])
        title = wintitle + " EW Drifts"
        xlabel = ""
        ylabel = "Height (Km)"

        if not self.isConfig:

            self.setup(id=id,
                       nplots=nplots,
                       wintitle=wintitle,
                       showprofile=showprofile,
                       show=show)

            self.xmin, self.xmax = self.getTimeLim(x, xmin, xmax, timerange)

            if ymin == None: ymin = numpy.nanmin(y)
            if ymax == None: ymax = numpy.nanmax(y)

            if zmaxZonal == None: zmaxZonal = numpy.nanmax(abs(z[0,:]))
            if zminZonal == None: zminZonal = -zmaxZonal
            if zmaxVertical == None: zmaxVertical = numpy.nanmax(abs(z[1,:]))
            if zminVertical == None: zminVertical = -zmaxVertical

            if dataOut.data_SNR is not None:
                if SNRmin == None:  SNRmin = numpy.nanmin(SNRavgdB)
                if SNRmax == None:  SNRmax = numpy.nanmax(SNRavgdB)

            self.FTP_WEI = ftp_wei
            self.EXP_CODE = exp_code
            self.SUB_EXP_CODE = sub_exp_code
            self.PLOT_POS = plot_pos

            self.name = thisDatetime.strftime("%Y%m%d_%H%M%S")
            self.isConfig = True


        self.setWinTitle(title)

        if ((self.xmax - x[1]) < (x[1]-x[0])):
            x[1] = self.xmax

        strWind = ['Zonal','Vertical']
        strCb = 'Velocity (m/s)'
        zmaxVector = [zmaxZonal, zmaxVertical]
        zminVector = [zminZonal, zminVertical]

        for i in range(nplotsw):

            title = "%s Drifts: %s" %(strWind[i], thisDatetime.strftime("%Y/%m/%d %H:%M:%S"))
            axes = self.axesList[i*self.__nsubplots]

            z1 = z[i,:].reshape((1,-1))

            axes.pcolorbuffer(x, y, z1,
                        xmin=self.xmin, xmax=self.xmax, ymin=ymin, ymax=ymax, zmin=zminVector[i], zmax=zmaxVector[i],
                        xlabel=xlabel, ylabel=ylabel, title=title, rti=True, XAxisAsTime=True,
                        ticksize=9, cblabel=strCb, cbsize="1%", colormap="RdBu_r")

        if dataOut.data_SNR is not None:
            i += 1
            if SNR_1:
                title = "Signal Noise Ratio + 1 (SNR+1): %s" %(thisDatetime.strftime("%Y/%m/%d %H:%M:%S"))
            else:
                title = "Signal Noise Ratio (SNR): %s" %(thisDatetime.strftime("%Y/%m/%d %H:%M:%S"))
            axes = self.axesList[i*self.__nsubplots]
            SNRavgdB = SNRavgdB.reshape((1,-1))

            axes.pcolorbuffer(x, y, SNRavgdB,
                        xmin=self.xmin, xmax=self.xmax, ymin=ymin, ymax=ymax, zmin=SNRmin, zmax=SNRmax,
                        xlabel=xlabel, ylabel=ylabel, title=title, rti=True, XAxisAsTime=True,
                        ticksize=9, cblabel='', cbsize="1%", colormap="jet")

        self.draw()

        if x[1] >= self.axesList[0].xmax:
            self.counter_imagwr = wr_period
            self.isConfig = False
            self.figfile = None




class PhasePlot(Figure):

    __isConfig = None
    __nsubplots = None

    PREFIX = 'mphase'

    def __init__(self, **kwargs):
        Figure.__init__(self, **kwargs)
        self.timerange = 24*60*60
        self.isConfig = False
        self.__nsubplots = 1
        self.counter_imagwr = 0
        self.WIDTH = 600
        self.HEIGHT = 300
        self.WIDTHPROF = 120
        self.HEIGHTPROF = 0
        self.xdata = None
        self.ydata = None

        self.PLOT_CODE = MPHASE_CODE

        self.FTP_WEI = None
        self.EXP_CODE = None
        self.SUB_EXP_CODE = None
        self.PLOT_POS = None


        self.filename_phase = None

        self.figfile = None

    def getSubplots(self):

        ncol = 1
        nrow = 1

        return nrow, ncol

    def setup(self, id, nplots, wintitle, showprofile=True, show=True):

        self.__showprofile = showprofile
        self.nplots = nplots

        ncolspan = 7
        colspan = 6
        self.__nsubplots = 2

        self.createFigure(id = id,
                          wintitle = wintitle,
                          widthplot = self.WIDTH+self.WIDTHPROF,
                          heightplot = self.HEIGHT+self.HEIGHTPROF,
                          show=show)

        nrow, ncol = self.getSubplots()

        self.addAxes(nrow, ncol*ncolspan, 0, 0, colspan, 1)


    def run(self, dataOut, id, wintitle="", pairsList=None, showprofile='True',
            xmin=None, xmax=None, ymin=None, ymax=None,
            timerange=None,
            save=False, figpath='./', figfile=None, show=True, ftp=False, wr_period=1,
            server=None, folder=None, username=None, password=None,
            ftp_wei=0, exp_code=0, sub_exp_code=0, plot_pos=0):


        tmin = None
        tmax = None
        x = dataOut.getTimeRange1(dataOut.outputInterval)
        y = dataOut.getHeiRange()


        #thisDatetime = dataOut.datatime
        thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.ltctime)
        title = wintitle + " Phase of Beacon Signal" # : %s" %(thisDatetime.strftime("%d-%b-%Y"))
        xlabel = "Local Time"
        ylabel = "Phase"


        #phase = numpy.zeros((len(pairsIndexList),len(dataOut.beacon_heiIndexList)))
        phase_beacon = dataOut.data_output
        update_figfile = False

        if not self.isConfig:

            self.nplots = phase_beacon.size

            self.setup(id=id,
                       nplots=self.nplots,
                       wintitle=wintitle,
                       showprofile=showprofile,
                       show=show)

            if timerange is not None:
                self.timerange = timerange

            self.xmin, self.xmax = self.getTimeLim(x, xmin, xmax, timerange)

            if ymin == None: ymin = numpy.nanmin(phase_beacon) - 10.0
            if ymax == None: ymax = numpy.nanmax(phase_beacon) + 10.0

            self.FTP_WEI = ftp_wei
            self.EXP_CODE = exp_code
            self.SUB_EXP_CODE = sub_exp_code
            self.PLOT_POS = plot_pos

            self.name = thisDatetime.strftime("%Y%m%d_%H%M%S")
            self.isConfig = True
            self.figfile = figfile
            self.xdata = numpy.array([])
            self.ydata = numpy.array([])

            #open file beacon phase
            path = '%s%03d' %(self.PREFIX, self.id)
            beacon_file = os.path.join(path,'%s.txt'%self.name)
            self.filename_phase = os.path.join(figpath,beacon_file)
            update_figfile = True


        #store data beacon phase
        #self.save_data(self.filename_phase, phase_beacon, thisDatetime)

        self.setWinTitle(title)


        title = "Phase Offset %s" %(thisDatetime.strftime("%Y/%m/%d %H:%M:%S"))

        legendlabels = ["phase %d"%(chan) for chan in numpy.arange(self.nplots)]

        axes = self.axesList[0]

        self.xdata = numpy.hstack((self.xdata, x[0:1]))

        if len(self.ydata)==0:
            self.ydata = phase_beacon.reshape(-1,1)
        else:
            self.ydata = numpy.hstack((self.ydata, phase_beacon.reshape(-1,1)))


        axes.pmultilineyaxis(x=self.xdata, y=self.ydata,
                    xmin=self.xmin, xmax=self.xmax, ymin=ymin, ymax=ymax,
                    xlabel=xlabel, ylabel=ylabel, title=title, legendlabels=legendlabels, marker='x', markersize=8, linestyle="solid",
                    XAxisAsTime=True, grid='both'
                    )

        self.draw()

        self.save(figpath=figpath,
          figfile=figfile,
          save=save,
          ftp=ftp,
          wr_period=wr_period,
          thisDatetime=thisDatetime,
          update_figfile=update_figfile)

        if dataOut.ltctime + dataOut.outputInterval >= self.xmax:
            self.counter_imagwr = wr_period
            self.isConfig = False
            update_figfile = True



class NSMeteorDetection1Plot(Figure):

    isConfig = None
    __nsubplots = None

    WIDTHPROF = None
    HEIGHTPROF = None
    PREFIX = 'nsm'

    zminList = None
    zmaxList = None
    cmapList = None
    titleList = None
    nPairs = None
    nChannels = None
    nParam = None

    def __init__(self, **kwargs):
        Figure.__init__(self, **kwargs)
        self.isConfig = False
        self.__nsubplots = 1

        self.WIDTH = 750
        self.HEIGHT = 250
        self.WIDTHPROF = 120
        self.HEIGHTPROF = 0
        self.counter_imagwr = 0

        self.PLOT_CODE = SPEC_CODE

        self.FTP_WEI = None
        self.EXP_CODE = None
        self.SUB_EXP_CODE = None
        self.PLOT_POS = None

        self.__xfilter_ena = False
        self.__yfilter_ena = False

    def getSubplots(self):

        ncol = 3
        nrow = int(numpy.ceil(self.nplots/3.0))

        return nrow, ncol

    def setup(self, id, nplots, wintitle, show=True):

        self.nplots = nplots

        ncolspan = 1
        colspan = 1

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

                counter += 1

    def run(self, dataOut, id, wintitle="", channelList=None, showprofile=True,
            xmin=None, xmax=None, ymin=None, ymax=None, SNRmin=None, SNRmax=None,
            vmin=None, vmax=None, wmin=None, wmax=None, mode = 'SA',
            save=False, figpath='./', figfile=None, show=True, ftp=False, wr_period=1,
            server=None, folder=None, username=None, password=None,
            ftp_wei=0, exp_code=0, sub_exp_code=0, plot_pos=0, realtime=False,
            xaxis="frequency"):

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
        #SEPARAR EN DOS PLOTS
        nParam = dataOut.data_param.shape[1] - 3

        utctime = dataOut.data_param[0,0]
        tmet = dataOut.data_param[:,1].astype(int)
        hmet = dataOut.data_param[:,2].astype(int)

        x = dataOut.abscissaList
        y = dataOut.heightList

        z = numpy.zeros((nParam, y.size, x.size - 1))
        z[:,:] = numpy.nan
        z[:,hmet,tmet] = dataOut.data_param[:,3:].T
        z[0,:,:] = 10*numpy.log10(z[0,:,:])

        xlabel = "Time (s)"
        ylabel = "Range (km)"

        thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.ltctime)

        if not self.isConfig:

            nplots = nParam

            self.setup(id=id,
                       nplots=nplots,
                       wintitle=wintitle,
                       show=show)

            if xmin is None: xmin = numpy.nanmin(x)
            if xmax is None: xmax = numpy.nanmax(x)
            if ymin is None: ymin = numpy.nanmin(y)
            if ymax is None: ymax = numpy.nanmax(y)
            if SNRmin is None: SNRmin = numpy.nanmin(z[0,:])
            if SNRmax is None: SNRmax = numpy.nanmax(z[0,:])
            if vmax is None: vmax = numpy.nanmax(numpy.abs(z[1,:]))
            if vmin is None: vmin = -vmax
            if wmin is None: wmin = 0
            if wmax is None: wmax = 50

            pairsList = dataOut.groupList
            self.nPairs = len(dataOut.groupList)

            zminList = [SNRmin, vmin, cmin] + [pmin]*self.nPairs
            zmaxList = [SNRmax, vmax, cmax] + [pmax]*self.nPairs
            titleList = ["SNR","Radial Velocity","Coherence"]
            cmapList = ["jet","RdBu_r","jet"]

            for i in range(self.nPairs):
                strAux1 = "Phase Difference "+ str(pairsList[i][0]) + str(pairsList[i][1])
                titleList = titleList + [strAux1]
                cmapList = cmapList + ["RdBu_r"]

            self.zminList = zminList
            self.zmaxList = zmaxList
            self.cmapList = cmapList
            self.titleList = titleList

            self.FTP_WEI = ftp_wei
            self.EXP_CODE = exp_code
            self.SUB_EXP_CODE = sub_exp_code
            self.PLOT_POS = plot_pos

            self.isConfig = True

        str_datetime = '%s %s'%(thisDatetime.strftime("%Y/%m/%d"),thisDatetime.strftime("%H:%M:%S"))

        for i in range(nParam):
            title = self.titleList[i] + ": " +str_datetime
            axes = self.axesList[i]
            axes.pcolor(x, y, z[i,:].T,
                        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, zmin=self.zminList[i], zmax=self.zmaxList[i],
                        xlabel=xlabel, ylabel=ylabel, title=title, colormap=self.cmapList[i],ticksize=9, cblabel='')
        self.draw()

        if figfile == None:
            str_datetime = thisDatetime.strftime("%Y%m%d_%H%M%S")
            name = str_datetime
            if ((dataOut.azimuth!=None) and (dataOut.zenith!=None)):
                name = name + '_az' + '_%2.2f'%(dataOut.azimuth) + '_zn' + '_%2.2f'%(dataOut.zenith)
            figfile = self.getFilename(name)

        self.save(figpath=figpath,
                  figfile=figfile,
                  save=save,
                  ftp=ftp,
                  wr_period=wr_period,
                  thisDatetime=thisDatetime)


class NSMeteorDetection2Plot(Figure):

    isConfig = None
    __nsubplots = None

    WIDTHPROF = None
    HEIGHTPROF = None
    PREFIX = 'nsm'

    zminList = None
    zmaxList = None
    cmapList = None
    titleList = None
    nPairs = None
    nChannels = None
    nParam = None

    def __init__(self, **kwargs):
        Figure.__init__(self, **kwargs)
        self.isConfig = False
        self.__nsubplots = 1

        self.WIDTH = 750
        self.HEIGHT = 250
        self.WIDTHPROF = 120
        self.HEIGHTPROF = 0
        self.counter_imagwr = 0

        self.PLOT_CODE = SPEC_CODE

        self.FTP_WEI = None
        self.EXP_CODE = None
        self.SUB_EXP_CODE = None
        self.PLOT_POS = None

        self.__xfilter_ena = False
        self.__yfilter_ena = False

    def getSubplots(self):

        ncol = 3
        nrow = int(numpy.ceil(self.nplots/3.0))

        return nrow, ncol

    def setup(self, id, nplots, wintitle, show=True):

        self.nplots = nplots

        ncolspan = 1
        colspan = 1

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

                counter += 1

    def run(self, dataOut, id, wintitle="", channelList=None, showprofile=True,
            xmin=None, xmax=None, ymin=None, ymax=None, SNRmin=None, SNRmax=None,
            vmin=None, vmax=None, wmin=None, wmax=None, mode = 'SA',
            save=False, figpath='./', figfile=None, show=True, ftp=False, wr_period=1,
            server=None, folder=None, username=None, password=None,
            ftp_wei=0, exp_code=0, sub_exp_code=0, plot_pos=0, realtime=False,
            xaxis="frequency"):

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
        #Rebuild matrix
        utctime = dataOut.data_param[0,0]
        cmet = dataOut.data_param[:,1].astype(int)
        tmet = dataOut.data_param[:,2].astype(int)
        hmet = dataOut.data_param[:,3].astype(int)

        nParam = 3
        nChan = len(dataOut.groupList)
        x = dataOut.abscissaList
        y = dataOut.heightList

        z = numpy.full((nChan, nParam, y.size, x.size - 1),numpy.nan)
        z[cmet,:,hmet,tmet] = dataOut.data_param[:,4:]
        z[:,0,:,:] = 10*numpy.log10(z[:,0,:,:]) #logarithmic scale
        z = numpy.reshape(z, (nChan*nParam, y.size, x.size-1))

        xlabel = "Time (s)"
        ylabel = "Range (km)"

        thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.ltctime)

        if not self.isConfig:

            nplots = nParam*nChan

            self.setup(id=id,
                       nplots=nplots,
                       wintitle=wintitle,
                       show=show)

            if xmin is None: xmin = numpy.nanmin(x)
            if xmax is None: xmax = numpy.nanmax(x)
            if ymin is None: ymin = numpy.nanmin(y)
            if ymax is None: ymax = numpy.nanmax(y)
            if SNRmin is None: SNRmin = numpy.nanmin(z[0,:])
            if SNRmax is None: SNRmax = numpy.nanmax(z[0,:])
            if vmax is None: vmax = numpy.nanmax(numpy.abs(z[1,:]))
            if vmin is None: vmin = -vmax
            if wmin is None: wmin = 0
            if wmax is None: wmax = 50

            self.nChannels = nChan

            zminList = []
            zmaxList = []
            titleList = []
            cmapList = []
            for i in range(self.nChannels):
                strAux1 = "SNR Channel "+ str(i)
                strAux2 = "Radial Velocity Channel "+ str(i)
                strAux3 = "Spectral Width Channel "+ str(i)

                titleList = titleList + [strAux1,strAux2,strAux3]
                cmapList = cmapList + ["jet","RdBu_r","jet"]
                zminList = zminList + [SNRmin,vmin,wmin]
                zmaxList = zmaxList + [SNRmax,vmax,wmax]

            self.zminList = zminList
            self.zmaxList = zmaxList
            self.cmapList = cmapList
            self.titleList = titleList

            self.FTP_WEI = ftp_wei
            self.EXP_CODE = exp_code
            self.SUB_EXP_CODE = sub_exp_code
            self.PLOT_POS = plot_pos

            self.isConfig = True

        str_datetime = '%s %s'%(thisDatetime.strftime("%Y/%m/%d"),thisDatetime.strftime("%H:%M:%S"))

        for i in range(self.nplots):
            title = self.titleList[i] + ": " +str_datetime
            axes = self.axesList[i]
            axes.pcolor(x, y, z[i,:].T,
                        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, zmin=self.zminList[i], zmax=self.zmaxList[i],
                        xlabel=xlabel, ylabel=ylabel, title=title, colormap=self.cmapList[i],ticksize=9, cblabel='')
        self.draw()

        if figfile == None:
            str_datetime = thisDatetime.strftime("%Y%m%d_%H%M%S")
            name = str_datetime
            if ((dataOut.azimuth!=None) and (dataOut.zenith!=None)):
                name = name + '_az' + '_%2.2f'%(dataOut.azimuth) + '_zn' + '_%2.2f'%(dataOut.zenith)
            figfile = self.getFilename(name)

        self.save(figpath=figpath,
                  figfile=figfile,
                  save=save,
                  ftp=ftp,
                  wr_period=wr_period,
                  thisDatetime=thisDatetime)
