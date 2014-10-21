import os
import datetime
import numpy

from figure import Figure, isRealtime

class MomentsPlot(Figure):
    
    isConfig = None
    __nsubplots = None
    
    WIDTHPROF = None
    HEIGHTPROF = None
    PREFIX = 'prm'
    
    def __init__(self):
        
        self.isConfig = False
        self.__nsubplots = 1
        
        self.WIDTH = 280
        self.HEIGHT = 250
        self.WIDTHPROF = 120
        self.HEIGHTPROF = 0
        self.counter_imagwr = 0
        
        self.PLOT_CODE = 1
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
            save=False, figpath='', figfile=None, show=True, ftp=False, wr_period=1,
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
        x = dataOut.abscissaRange
        y = dataOut.heightRange
        
        z = dataOut.data_pre[channelIndexList,:,:]/factor
        z = numpy.where(numpy.isfinite(z), z, numpy.NAN) 
        avg = numpy.average(z, axis=1)
        noise = dataOut.noise/factor
        
        zdB = 10*numpy.log10(z)
        avgdB = 10*numpy.log10(avg)
        noisedB = 10*numpy.log10(noise)
        
        #thisDatetime = dataOut.datatime
        thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.getTimeRange()[1])
        title = wintitle + " Parameters" 
        xlabel = "Velocity (m/s)"
        ylabel = "Range (Km)"
        
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
        
        self.setWinTitle(title)
            
        for i in range(self.nplots):
            str_datetime = '%s %s'%(thisDatetime.strftime("%Y/%m/%d"),thisDatetime.strftime("%H:%M:%S"))
            title = "Channel %d: %4.2fdB: %s" %(dataOut.channelList[i]+1, noisedB[i], str_datetime)
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
        
        if figfile == None:
            str_datetime = thisDatetime.strftime("%Y%m%d_%H%M%S")
            figfile = self.getFilename(name = str_datetime)
        
        if figpath != '':
            self.counter_imagwr += 1
            if (self.counter_imagwr>=wr_period):
                # store png plot to local folder
                self.saveFigure(figpath, figfile)
                # store png plot to FTP server according to RT-Web format 
                name = self.getNameToFtp(thisDatetime, self.FTP_WEI, self.EXP_CODE, self.SUB_EXP_CODE, self.PLOT_CODE, self.PLOT_POS)
                ftp_filename = os.path.join(figpath, name)
                self.saveFigure(figpath, ftp_filename)                
                self.counter_imagwr = 0

class SkyMapPlot(Figure):
    
    __isConfig = None
    __nsubplots = None
    
    WIDTHPROF = None
    HEIGHTPROF = None
    PREFIX = 'prm'
    
    def __init__(self):
        
        self.__isConfig = False
        self.__nsubplots = 1
        
#         self.WIDTH = 280
#         self.HEIGHT = 250
        self.WIDTH = 600
        self.HEIGHT = 600
        self.WIDTHPROF = 120
        self.HEIGHTPROF = 0
        self.counter_imagwr = 0
        
        self.PLOT_CODE = 1
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
        
        arrayParameters = dataOut.data_param
        error = arrayParameters[:,-1]
        indValid = numpy.where(error == 0)[0]
        finalMeteor = arrayParameters[indValid,:]
        finalAzimuth = finalMeteor[:,4]
        finalZenith = finalMeteor[:,5]
         
        x = finalAzimuth*numpy.pi/180
        y = finalZenith
        

        #thisDatetime = dataOut.datatime
        thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.getTimeRange()[1])
        title = wintitle + " Parameters" 
        xlabel = "Zonal Zenith Angle (deg) "
        ylabel = "Meridional Zenith Angle (deg)"
        
        if not self.__isConfig:
            
            nplots = 1
            
            self.setup(id=id,
                       nplots=nplots,
                       wintitle=wintitle,
                       showprofile=showprofile,
                       show=show)

            self.FTP_WEI = ftp_wei
            self.EXP_CODE = exp_code
            self.SUB_EXP_CODE = sub_exp_code
            self.PLOT_POS = plot_pos
            self.name = thisDatetime.strftime("%Y%m%d_%H%M%S")
            self.firstdate = '%s %s'%(thisDatetime.strftime("%Y/%m/%d"),thisDatetime.strftime("%H:%M:%S"))
            self.__isConfig = True
        
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
        
        if save:
            
            self.counter_imagwr += 1
            if (self.counter_imagwr==wr_period):
                
                if figfile == None:
                    figfile = self.getFilename(name = self.name)
                self.saveFigure(figpath, figfile)       
                
                if ftp:
                    #provisionalmente envia archivos en el formato de la web en tiempo real
                    name = self.getNameToFtp(thisDatetime, self.FTP_WEI, self.EXP_CODE, self.SUB_EXP_CODE, self.PLOT_CODE, self.PLOT_POS)
                    path = '%s%03d' %(self.PREFIX, self.id)
                    ftp_file = os.path.join(path,'ftp','%s.png'%name)
                    self.saveFigure(figpath, ftp_file)
                    ftp_filename = os.path.join(figpath,ftp_file)
                    
                    
                    try:
                        self.sendByFTP(ftp_filename, server, folder, username, password)
                    except:
                        self.counter_imagwr = 0
                        raise ValueError, 'Error FTP'
                
                self.counter_imagwr = 0
               
                                
class WindProfilerPlot(Figure):
     
    __isConfig = None
    __nsubplots = None
     
    WIDTHPROF = None
    HEIGHTPROF = None
    PREFIX = 'wind'
     
    def __init__(self):
         
        self.timerange = 2*60*60
        self.isConfig = False
        self.__nsubplots = 1
        
        self.WIDTH = 800
        self.HEIGHT = 150
        self.WIDTHPROF = 120
        self.HEIGHTPROF = 0
        self.counter_imagwr = 0
        
        self.PLOT_CODE = 0
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
            zmax_ver = None, zmin_ver = None, SNRmin = None, SNRmax = None,
            timerange=None, SNRthresh = None,
            save=False, figpath='', lastone=0,figfile=None, ftp=False, wr_period=1, show=True,
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
         
        if channelList == None:
            channelIndexList = dataOut.channelIndexList
        else:
            channelIndexList = []
            for channel in channelList:
                if channel not in dataOut.channelList:
                    raise ValueError, "Channel %d is not in dataOut.channelList"
                channelIndexList.append(dataOut.channelList.index(channel))
         
        if timerange != None:
            self.timerange = timerange
         
        tmin = None
        tmax = None
 
        x = dataOut.getTimeRange1()
        y = dataOut.heightRange
            
        z = dataOut.winds
        nplots = z.shape[0]    #Number of wind dimensions estimated
        nplotsw = nplots
         
        #If there is a SNR function defined
        if dataOut.SNR != None:
            nplots += 1
            SNR = dataOut.SNR
            SNRavg = numpy.average(SNR, axis=0)
             
            SNRdB = 10*numpy.log10(SNR)
            SNRavgdB = 10*numpy.log10(SNRavg)
             
            if SNRthresh == None: SNRthresh = -5.0
            ind = numpy.where(SNRavg < 10**(SNRthresh/10))[0]
         
            for i in range(nplotsw):
                z[i,ind] = numpy.nan
 
 
        showprofile = False 
#        thisDatetime = dataOut.datatime
        thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.getTimeRange()[1])
        title = wintitle + "Wind"
        xlabel = ""
        ylabel = "Range (Km)"
         
        if not self.__isConfig:
             
             
             
            self.setup(id=id,
                       nplots=nplots,
                       wintitle=wintitle,
                       showprofile=showprofile,
                       show=show)
             
            self.xmin, self.xmax = self.getTimeLim(x, xmin, xmax, timerange)
 
            if ymin == None: ymin = numpy.nanmin(y)
            if ymax == None: ymax = numpy.nanmax(y)
                  
            if zmax == None: zmax = numpy.nanmax(abs(z[range(2),:]))
            #if numpy.isnan(zmax): zmax = 50
            if zmin == None: zmin = -zmax
             
            if nplotsw == 3:
                if zmax_ver == None: zmax_ver = numpy.nanmax(abs(z[2,:]))
                if zmin_ver == None: zmin_ver = -zmax_ver
             
            if dataOut.SNR != None:
                if SNRmin == None:  SNRmin = numpy.nanmin(SNRavgdB)
                if SNRmax == None:  SNRmax = numpy.nanmax(SNRavgdB) 
             
            self.FTP_WEI = ftp_wei
            self.EXP_CODE = exp_code
            self.SUB_EXP_CODE = sub_exp_code
            self.PLOT_POS = plot_pos
             
            self.name = thisDatetime.strftime("%Y%m%d_%H%M%S")
            self.__isConfig = True
         
         
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
 
            axes.pcolorbuffer(x, y, z1,
                        xmin=self.xmin, xmax=self.xmax, ymin=ymin, ymax=ymax, zmin=zminVector[i], zmax=zmaxVector[i],
                        xlabel=xlabel, ylabel=ylabel, title=title, rti=True, XAxisAsTime=True,
                        ticksize=9, cblabel=strCb[i], cbsize="1%", colormap="RdBu_r" )
                     
        if dataOut.SNR != None:
            i += 1              
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
            self.__isConfig = False
         
         
        if self.figfile == None:
            str_datetime = thisDatetime.strftime("%Y%m%d_%H%M%S")
            self.figfile = self.getFilename(name = str_datetime)
         
        if figpath != '':
             
            self.counter_imagwr += 1
            if (self.counter_imagwr>=wr_period):
                # store png plot to local folder
                self.saveFigure(figpath, self.figfile)
                # store png plot to FTP server according to RT-Web format 
                name = self.getNameToFtp(thisDatetime, self.FTP_WEI, self.EXP_CODE, self.SUB_EXP_CODE, self.PLOT_CODE, self.PLOT_POS)
                ftp_filename = os.path.join(figpath, name)
                self.saveFigure(figpath, ftp_filename)
                 
                self.counter_imagwr = 0
                 
           