import numpy
import time, datetime, os
from graphics.figure import  * 
def isRealtime(utcdatatime):
    utcnow = time.mktime(datetime.datetime.utcnow().timetuple())
    delta = utcnow - utcdatatime # abs
    if delta >= 5*60.:
        return False
    return True

class CrossSpectraPlot(Figure):
    
    __isConfig = None
    __nsubplots = None
    
    WIDTH = None
    HEIGHT = None
    WIDTHPROF = None
    HEIGHTPROF = None
    PREFIX = 'cspc'
    
    def __init__(self):
        
        self.__isConfig = False
        self.__nsubplots = 4
        
        self.WIDTH = 250
        self.HEIGHT = 250
        self.WIDTHPROF = 0
        self.HEIGHTPROF = 0
        
    def getSubplots(self):
        
        ncol = 4
        nrow = self.nplots
        
        return nrow, ncol
    
    def setup(self, idfigure, nplots, wintitle, showprofile=True, show=True):
               
        self.__showprofile = showprofile
        self.nplots = nplots
        
        ncolspan = 1
        colspan = 1
        
        self.createFigure(idfigure = idfigure,
                          wintitle = wintitle,
                          widthplot = self.WIDTH + self.WIDTHPROF,
                          heightplot = self.HEIGHT + self.HEIGHTPROF,
                          show=True)
        
        nrow, ncol = self.getSubplots()
        
        counter = 0
        for y in range(nrow):
            for x in range(ncol):                
                self.addAxes(nrow, ncol*ncolspan, y, x*ncolspan, colspan, 1)
                
                counter += 1
    
    def run(self, dataOut, idfigure, wintitle="", pairsList=None, showprofile='True',
            xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None,
            save=False, figpath='./', figfile=None,
            power_cmap='jet', coherence_cmap='jet', phase_cmap='RdBu_r', show=True):
        
        """
        
        Input:
            dataOut         :
            idfigure        :
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
        
        if pairsList == None:
            pairsIndexList = dataOut.pairsIndexList
        else:
            pairsIndexList = []
            for pair in pairsList:
                if pair not in dataOut.pairsList:
                    raise ValueError, "Pair %s is not in dataOut.pairsList" %(pair)
                pairsIndexList.append(dataOut.pairsList.index(pair))
        
        if pairsIndexList == []:
            return
        
        if len(pairsIndexList) > 4:
            pairsIndexList = pairsIndexList[0:4]
        factor = dataOut.normFactor
        x = dataOut.getVelRange(1)
        y = dataOut.getHeiRange()
        z = dataOut.data_spc[:,:,:]/factor
#        z = numpy.where(numpy.isfinite(z), z, numpy.NAN)
        avg = numpy.abs(numpy.average(z, axis=1))
        noise = dataOut.getNoise()/factor
        
        zdB = 10*numpy.log10(z)
        avgdB = 10*numpy.log10(avg)
        noisedB = 10*numpy.log10(noise)
        
        
        thisDatetime = dataOut.datatime
        title = "Cross-Spectra: %s" %(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
        xlabel = "Velocity (m/s)"
        ylabel = "Range (Km)"
        
        if not self.__isConfig:
            
            nplots = len(pairsIndexList)
            
            self.setup(idfigure=idfigure,
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
            
            self.__isConfig = True
        
        self.setWinTitle(title)
            
        for i in range(self.nplots):
            pair = dataOut.pairsList[pairsIndexList[i]]
            
            title = "Channel %d: %4.2fdB" %(pair[0], noisedB[pair[0]])
            zdB = 10.*numpy.log10(dataOut.data_spc[pair[0],:,:]/factor)
            axes0 = self.axesList[i*self.__nsubplots]
            axes0.pcolor(x, y, zdB,
                        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, zmin=zmin, zmax=zmax,
                        xlabel=xlabel, ylabel=ylabel, title=title,
                        ticksize=9, colormap=power_cmap, cblabel='')
            
            title = "Channel %d: %4.2fdB" %(pair[1], noisedB[pair[1]])
            zdB = 10.*numpy.log10(dataOut.data_spc[pair[1],:,:]/factor)
            axes0 = self.axesList[i*self.__nsubplots+1]
            axes0.pcolor(x, y, zdB,
                        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, zmin=zmin, zmax=zmax,
                        xlabel=xlabel, ylabel=ylabel, title=title,
                        ticksize=9, colormap=power_cmap, cblabel='')

            coherenceComplex = dataOut.data_cspc[pairsIndexList[i],:,:]/numpy.sqrt(dataOut.data_spc[pair[0],:,:]*dataOut.data_spc[pair[1],:,:])
            coherence = numpy.abs(coherenceComplex)
#            phase = numpy.arctan(-1*coherenceComplex.imag/coherenceComplex.real)*180/numpy.pi
            phase = numpy.arctan2(coherenceComplex.imag, coherenceComplex.real)*180/numpy.pi
            
            title = "Coherence %d%d" %(pair[0], pair[1])
            axes0 = self.axesList[i*self.__nsubplots+2]
            axes0.pcolor(x, y, coherence,
                        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, zmin=0, zmax=1,
                        xlabel=xlabel, ylabel=ylabel, title=title,
                        ticksize=9, colormap=coherence_cmap, cblabel='')
            
            title = "Phase %d%d" %(pair[0], pair[1])
            axes0 = self.axesList[i*self.__nsubplots+3]
            axes0.pcolor(x, y, phase,
                        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, zmin=-180, zmax=180,
                        xlabel=xlabel, ylabel=ylabel, title=title,
                        ticksize=9, colormap=phase_cmap, cblabel='')


            
        self.draw()
        
        if save:
            date = thisDatetime.strftime("%Y%m%d_%H%M%S")
            if figfile == None:
                figfile = self.getFilename(name = date)
            
            self.saveFigure(figpath, figfile)


class RTIPlot(Figure):
    
    __isConfig = None
    __nsubplots = None
    
    WIDTHPROF = None
    HEIGHTPROF = None
    PREFIX = 'rti'
    
    def __init__(self):
        
        self.timerange = 2*60*60
        self.__isConfig = False
        self.__nsubplots = 1
        
        self.WIDTH = 800
        self.HEIGHT = 150
        self.WIDTHPROF = 120
        self.HEIGHTPROF = 0
        self.counterftp = 0
        
    def getSubplots(self):
        
        ncol = 1
        nrow = self.nplots
        
        return nrow, ncol
    
    def setup(self, idfigure, nplots, wintitle, showprofile=True, show=True):
               
        self.__showprofile = showprofile
        self.nplots = nplots
        
        ncolspan = 1
        colspan = 1
        if showprofile:
            ncolspan = 7
            colspan = 6
            self.__nsubplots = 2
            
        self.createFigure(idfigure = idfigure,
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
    
    def run(self, dataOut, idfigure, wintitle="", channelList=None, showprofile='True',
            xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None,
            timerange=None,
            save=False, figpath='./', figfile=None, ftp=False, ftpratio=1, show=True):
        
        """
        
        Input:
            dataOut         :
            idfigure        :
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
        factor = dataOut.normFactor
        x = dataOut.getTimeRange()
        y = dataOut.getHeiRange()
        
        z = dataOut.data_spc[channelIndexList,:,:]/factor
        z = numpy.where(numpy.isfinite(z), z, numpy.NAN) 
        avg = numpy.average(z, axis=1)
        
        avgdB = 10.*numpy.log10(avg)

        
        thisDatetime = dataOut.datatime
        title = "RTI: %s" %(thisDatetime.strftime("%d-%b-%Y"))
        xlabel = ""
        ylabel = "Range (Km)"
        
        if not self.__isConfig:
            
            nplots = len(channelIndexList)
            
            self.setup(idfigure=idfigure,
                       nplots=nplots,
                       wintitle=wintitle,
                       showprofile=showprofile,
                       show=show)
            
            tmin, tmax = self.getTimeLim(x, xmin, xmax)
            if ymin == None: ymin = numpy.nanmin(y)
            if ymax == None: ymax = numpy.nanmax(y)
            if zmin == None: zmin = numpy.nanmin(avgdB)*0.9
            if zmax == None: zmax = numpy.nanmax(avgdB)*0.9
            
            self.name = thisDatetime.strftime("%Y%m%d_%H%M%S")
            self.__isConfig = True
        
        
        self.setWinTitle(title)
            
        for i in range(self.nplots):
            title = "Channel %d: %s" %(dataOut.channelList[i], thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
            axes = self.axesList[i*self.__nsubplots]
            zdB = avgdB[i].reshape((1,-1))
            axes.pcolorbuffer(x, y, zdB,
                        xmin=tmin, xmax=tmax, ymin=ymin, ymax=ymax, zmin=zmin, zmax=zmax,
                        xlabel=xlabel, ylabel=ylabel, title=title, rti=True, XAxisAsTime=True,
                        ticksize=9, cblabel='', cbsize="1%")
            
            if self.__showprofile:
                axes = self.axesList[i*self.__nsubplots +1]
                axes.pline(avgdB[i], y,
                        xmin=zmin, xmax=zmax, ymin=ymin, ymax=ymax,
                        xlabel='dB', ylabel='', title='',
                        ytick_visible=False,
                        grid='x')
            
        self.draw()
        
        if save:
            
            if figfile == None:
                figfile = self.getFilename(name = self.name)
            
            self.saveFigure(figpath, figfile)
            
            self.counterftp += 1
            if (ftp and (self.counterftp==ftpratio)):
                figfilename = os.path.join(figpath,figfile)
                self.sendByFTP(figfilename)
                self.counterftp = 0
            
        if x[1] + (x[1]-x[0]) >= self.axesList[0].xmax:
            self.__isConfig = False
        
class SpectraPlot(Figure):
    
    __isConfig = None
    __nsubplots = None
    
    WIDTHPROF = None
    HEIGHTPROF = None
    PREFIX = 'spc'
    
    def __init__(self):
        
        self.__isConfig = False
        self.__nsubplots = 1
        
        self.WIDTH = 230
        self.HEIGHT = 250
        self.WIDTHPROF = 120
        self.HEIGHTPROF = 0
        
    def getSubplots(self):
        
        ncol = int(numpy.sqrt(self.nplots)+0.9)
        nrow = int(self.nplots*1./ncol + 0.9)
        
        return nrow, ncol
    
    def setup(self, idfigure, nplots, wintitle, showprofile=True, show=True):
               
        self.__showprofile = showprofile
        self.nplots = nplots
        
        ncolspan = 1
        colspan = 1
        if showprofile:
            ncolspan = 3
            colspan = 2
            self.__nsubplots = 2
        
        self.createFigure(idfigure = idfigure,
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
    
    def run(self, dataOut, idfigure, wintitle="", channelList=None, showprofile='True',
            xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None,
            save=False, figpath='./', figfile=None, show=True):
        
        """
        
        Input:
            dataOut         :
            idfigure        :
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
        factor = dataOut.normFactor
        x = dataOut.getVelRange(1)
        y = dataOut.getHeiRange()
        
        z = dataOut.data_spc[channelIndexList,:,:]/factor
        z = numpy.where(numpy.isfinite(z), z, numpy.NAN) 
        avg = numpy.average(z, axis=1)
        noise = dataOut.getNoise()/factor
        
        zdB = 10*numpy.log10(z)
        avgdB = 10*numpy.log10(avg)
        noisedB = 10*numpy.log10(noise)
        
        thisDatetime = dataOut.datatime
        title = "Spectra: %s" %(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
        xlabel = "Velocity (m/s)"
        ylabel = "Range (Km)"
        
        if not self.__isConfig:
            
            nplots = len(channelIndexList)
            
            self.setup(idfigure=idfigure,
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
            
            self.__isConfig = True
        
        self.setWinTitle(title)
            
        for i in range(self.nplots):
            title = "Channel %d: %4.2fdB" %(dataOut.channelList[i], noisedB[i])
            axes = self.axesList[i*self.__nsubplots]
            axes.pcolor(x, y, zdB[i,:,:],
                        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, zmin=zmin, zmax=zmax,
                        xlabel=xlabel, ylabel=ylabel, title=title,
                        ticksize=9, cblabel='')
            
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
        
        if save:
            date = thisDatetime.strftime("%Y%m%d_%H%M%S")
            if figfile == None:
                figfile = self.getFilename(name = date)
            
            self.saveFigure(figpath, figfile)

class Scope(Figure):
    
    __isConfig = None
    
    def __init__(self):
        
        self.__isConfig = False
        self.WIDTH = 600
        self.HEIGHT = 200
    
    def getSubplots(self):
        
        nrow = self.nplots
        ncol = 3
        return nrow, ncol
    
    def setup(self, idfigure, nplots, wintitle, show):
        
        self.nplots = nplots
        
        self.createFigure(idfigure=idfigure, 
                          wintitle=wintitle, 
                          show=show)
        
        nrow,ncol = self.getSubplots()
        colspan = 3
        rowspan = 1
        
        for i in range(nplots):
            self.addAxes(nrow, ncol, i, 0, colspan, rowspan)
            
        
    
    def run(self, dataOut, idfigure, wintitle="", channelList=None,
            xmin=None, xmax=None, ymin=None, ymax=None, save=False,
            figpath='./', figfile=None, show=True):
        
        """
        
        Input:
            dataOut         :
            idfigure        :
            wintitle        :
            channelList     :
            xmin            :    None,
            xmax            :    None,
            ymin            :    None,
            ymax            :    None,
        """
        
        if channelList == None:
            channelIndexList = dataOut.channelIndexList
        else:
            channelIndexList = []
            for channel in channelList:
                if channel not in dataOut.channelList:
                    raise ValueError, "Channel %d is not in dataOut.channelList"
                channelIndexList.append(dataOut.channelList.index(channel))
        
        x = dataOut.heightList
        y = dataOut.data[channelIndexList,:] * numpy.conjugate(dataOut.data[channelIndexList,:])
        y = y.real
        
        thisDatetime = dataOut.datatime
        title = "Scope: %s" %(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
        xlabel = "Range (Km)"
        ylabel = "Intensity"
        
        if not self.__isConfig:
            nplots = len(channelIndexList)
            
            self.setup(idfigure=idfigure,
                       nplots=nplots,
                       wintitle=wintitle,
                       show=show)
            
            if xmin == None: xmin = numpy.nanmin(x)
            if xmax == None: xmax = numpy.nanmax(x)
            if ymin == None: ymin = numpy.nanmin(y)
            if ymax == None: ymax = numpy.nanmax(y)
                
            self.__isConfig = True
        
        self.setWinTitle(title)
        
        for i in range(len(self.axesList)):
            title = "Channel %d" %(i)
            axes = self.axesList[i]
            ychannel = y[i,:]
            axes.pline(x, ychannel,
                        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,
                        xlabel=xlabel, ylabel=ylabel, title=title)
        
        self.draw()
            
        if save:
            date = thisDatetime.strftime("%Y%m%d_%H%M%S")
            if figfile == None:
                figfile = self.getFilename(name = date)
            
            self.saveFigure(figpath, figfile)

class PowerProfilePlot(Figure):
    __isConfig = None
    __nsubplots = None
    
    WIDTHPROF = None
    HEIGHTPROF = None
    PREFIX = 'spcprofile'
    
    def __init__(self):
        self.__isConfig = False
        self.__nsubplots = 1
        
        self.WIDTH = 300
        self.HEIGHT = 500
    
    def getSubplots(self):
        ncol = 1
        nrow = 1
        
        return nrow, ncol
    
    def setup(self, idfigure, nplots, wintitle, show):
        
        self.nplots = nplots
        
        ncolspan = 1
        colspan = 1
        
        self.createFigure(idfigure = idfigure,
                          wintitle = wintitle,
                          widthplot = self.WIDTH,
                          heightplot = self.HEIGHT,
                          show=show)
        
        nrow, ncol = self.getSubplots()
        
        counter = 0
        for y in range(nrow):
            for x in range(ncol):                
                self.addAxes(nrow, ncol*ncolspan, y, x*ncolspan, colspan, 1)
    
    def run(self, dataOut, idfigure, wintitle="", channelList=None,
            xmin=None, xmax=None, ymin=None, ymax=None,
            save=False, figpath='./', figfile=None, show=True):
        
        if channelList == None:
            channelIndexList = dataOut.channelIndexList
            channelList = dataOut.channelList
        else:
            channelIndexList = []
            for channel in channelList:
                if channel not in dataOut.channelList:
                    raise ValueError, "Channel %d is not in dataOut.channelList"
                channelIndexList.append(dataOut.channelList.index(channel))
                
        factor = dataOut.normFactor
        y = dataOut.getHeiRange()        
        x = dataOut.data_spc[channelIndexList,:,:]/factor
        x = numpy.where(numpy.isfinite(x), x, numpy.NAN) 
        avg = numpy.average(x, axis=1)
        
        avgdB = 10*numpy.log10(avg)
        
        thisDatetime = dataOut.datatime
        title = "Power Profile"
        xlabel = "dB"
        ylabel = "Range (Km)"
        
        if not self.__isConfig:
            
            nplots = 1
            
            self.setup(idfigure=idfigure,
                       nplots=nplots,
                       wintitle=wintitle,
                       show=show)
            
            if ymin == None: ymin = numpy.nanmin(y)
            if ymax == None: ymax = numpy.nanmax(y)
            if xmin == None: xmin = numpy.nanmin(avgdB)*0.9
            if xmax == None: xmax = numpy.nanmax(avgdB)*0.9
            
            self.__isConfig = True
        
        self.setWinTitle(title)
        
        
        title = "Power Profile: %s" %(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
        axes = self.axesList[0]
        
        legendlabels = ["channel %d"%x for x in channelList]
        axes.pmultiline(avgdB, y,
                xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,
                xlabel=xlabel, ylabel=ylabel, title=title, legendlabels=legendlabels,
                ytick_visible=True, nxticks=5,
                grid='x')
        
        self.draw()
        
        if save:
            date = thisDatetime.strftime("%Y%m%d")
            if figfile == None:
                figfile = self.getFilename(name = date)
            
            self.saveFigure(figpath, figfile)

class CoherenceMap(Figure):
    __isConfig = None
    __nsubplots = None
    
    WIDTHPROF = None
    HEIGHTPROF = None
    PREFIX = 'cmap'

    def __init__(self):
        self.timerange = 2*60*60
        self.__isConfig = False
        self.__nsubplots = 1
        
        self.WIDTH = 800
        self.HEIGHT = 150
        self.WIDTHPROF = 120
        self.HEIGHTPROF = 0
        self.counterftp = 0
    
    def getSubplots(self):
        ncol = 1
        nrow = self.nplots*2
        
        return nrow, ncol
    
    def setup(self, idfigure, nplots, wintitle, showprofile=True, show=True):
        self.__showprofile = showprofile
        self.nplots = nplots
        
        ncolspan = 1
        colspan = 1
        if showprofile:
            ncolspan = 7
            colspan = 6
            self.__nsubplots = 2
            
        self.createFigure(idfigure = idfigure,
                          wintitle = wintitle,
                          widthplot = self.WIDTH + self.WIDTHPROF,
                          heightplot = self.HEIGHT + self.HEIGHTPROF,
                          show=True)
        
        nrow, ncol = self.getSubplots()
        
        for y in range(nrow):
            for x in range(ncol):
                
                self.addAxes(nrow, ncol*ncolspan, y, x*ncolspan, colspan, 1)
                
                if showprofile:
                    self.addAxes(nrow, ncol*ncolspan, y, x*ncolspan+colspan, 1, 1)
    
    def run(self, dataOut, idfigure, wintitle="", pairsList=None, showprofile='True',
            xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None,
            timerange=None,
            save=False, figpath='./', figfile=None, ftp=False, ftpratio=1,
            coherence_cmap='jet', phase_cmap='RdBu_r', show=True):
                
        if pairsList == None:
            pairsIndexList = dataOut.pairsIndexList
        else:
            pairsIndexList = []
            for pair in pairsList:
                if pair not in dataOut.pairsList:
                    raise ValueError, "Pair %s is not in dataOut.pairsList" %(pair)
                pairsIndexList.append(dataOut.pairsList.index(pair))
        
        if timerange != None:
            self.timerange = timerange
        
        if pairsIndexList == []:
            return
        
        if len(pairsIndexList) > 4:
            pairsIndexList = pairsIndexList[0:4]
            
        tmin = None
        tmax = None
        x = dataOut.getTimeRange()
        y = dataOut.getHeiRange()
        
        thisDatetime = dataOut.datatime
        title = "CoherenceMap: %s" %(thisDatetime.strftime("%d-%b-%Y"))
        xlabel = ""
        ylabel = "Range (Km)"
        
        if not self.__isConfig:    
            nplots = len(pairsIndexList)
            self.setup(idfigure=idfigure,
                       nplots=nplots,
                       wintitle=wintitle,
                       showprofile=showprofile,
                       show=show)
            
            tmin, tmax = self.getTimeLim(x, xmin, xmax)
            if ymin == None: ymin = numpy.nanmin(y)
            if ymax == None: ymax = numpy.nanmax(y)
            
            self.name = thisDatetime.strftime("%Y%m%d_%H%M%S")
            
            self.__isConfig = True
        
        self.setWinTitle(title)
        
        for i in range(self.nplots):
            
            pair = dataOut.pairsList[pairsIndexList[i]]
            coherenceComplex = dataOut.data_cspc[pairsIndexList[i],:,:]/numpy.sqrt(dataOut.data_spc[pair[0],:,:]*dataOut.data_spc[pair[1],:,:])
            avgcoherenceComplex = numpy.average(coherenceComplex, axis=0)
            coherence = numpy.abs(avgcoherenceComplex)
#            coherence = numpy.abs(coherenceComplex)            
#            avg = numpy.average(coherence, axis=0)
            
            z = coherence.reshape((1,-1))

            counter = 0
            
            title = "Coherence %d%d: %s" %(pair[0], pair[1], thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
            axes = self.axesList[i*self.__nsubplots*2]
            axes.pcolorbuffer(x, y, z,
                        xmin=tmin, xmax=tmax, ymin=ymin, ymax=ymax, zmin=0, zmax=1,
                        xlabel=xlabel, ylabel=ylabel, title=title, rti=True, XAxisAsTime=True,
                        ticksize=9, cblabel='', colormap=coherence_cmap, cbsize="1%")
            
            if self.__showprofile:
                counter += 1
                axes = self.axesList[i*self.__nsubplots*2 + counter]
                axes.pline(coherence, y,
                        xmin=0, xmax=1, ymin=ymin, ymax=ymax,
                        xlabel='', ylabel='', title='', ticksize=7,
                        ytick_visible=False, nxticks=5,
                        grid='x')
            
            counter += 1
#            phase = numpy.arctan(-1*coherenceComplex.imag/coherenceComplex.real)*180/numpy.pi
            phase = numpy.arctan2(avgcoherenceComplex.imag, avgcoherenceComplex.real)*180/numpy.pi
#            avg = numpy.average(phase, axis=0)
            z = phase.reshape((1,-1))
            
            title = "Phase %d%d: %s" %(pair[0], pair[1], thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
            axes = self.axesList[i*self.__nsubplots*2 + counter]
            axes.pcolorbuffer(x, y, z,
                        xmin=tmin, xmax=tmax, ymin=ymin, ymax=ymax, zmin=-180, zmax=180,
                        xlabel=xlabel, ylabel=ylabel, title=title, rti=True, XAxisAsTime=True,
                        ticksize=9, cblabel='', colormap=phase_cmap, cbsize="1%")
            
            if self.__showprofile:
                counter += 1
                axes = self.axesList[i*self.__nsubplots*2 + counter]
                axes.pline(phase, y,
                        xmin=-180, xmax=180, ymin=ymin, ymax=ymax,
                        xlabel='', ylabel='', title='', ticksize=7,
                        ytick_visible=False, nxticks=4,
                        grid='x')
            
        self.draw()
        
        if save:
            
            if figfile == None:
                figfile = self.getFilename(name = self.name)
            
            self.saveFigure(figpath, figfile)
            
            self.counterftp += 1
            if (ftp and (self.counterftp==ftpratio)):
                figfilename = os.path.join(figpath,figfile)
                self.sendByFTP(figfilename)
                self.counterftp = 0
            
        if x[1] + (x[1]-x[0]) >= self.axesList[0].xmax:
            self.__isConfig = False

class RTIfromNoise(Figure):
    
    __isConfig = None
    __nsubplots = None

    PREFIX = 'rtinoise'
    
    def __init__(self):
        
        self.timerange = 24*60*60
        self.__isConfig = False
        self.__nsubplots = 1
        
        self.WIDTH = 820
        self.HEIGHT = 200
        self.WIDTHPROF = 120
        self.HEIGHTPROF = 0
        self.xdata = None
        self.ydata = None
        
    def getSubplots(self):
        
        ncol = 1
        nrow = 1
        
        return nrow, ncol
    
    def setup(self, idfigure, nplots, wintitle, showprofile=True, show=True):
               
        self.__showprofile = showprofile
        self.nplots = nplots
        
        ncolspan = 7
        colspan = 6
        self.__nsubplots = 2
        
        self.createFigure(idfigure = idfigure,
                          wintitle = wintitle,
                          widthplot = self.WIDTH+self.WIDTHPROF,
                          heightplot = self.HEIGHT+self.HEIGHTPROF,
                          show=show)
        
        nrow, ncol = self.getSubplots()
        
        self.addAxes(nrow, ncol*ncolspan, 0, 0, colspan, 1)
        
                        
    def run(self, dataOut, idfigure, wintitle="", channelList=None, showprofile='True',
            xmin=None, xmax=None, ymin=None, ymax=None,
            timerange=None,
            save=False, figpath='./', figfile=None, show=True):
        
        if channelList == None:
            channelIndexList = dataOut.channelIndexList
            channelList = dataOut.channelList
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
        x = dataOut.getTimeRange()
        y = dataOut.getHeiRange()
        factor = dataOut.normFactor
        noise = dataOut.getNoise()/factor
        noisedB = 10*numpy.log10(noise)
        
        thisDatetime = dataOut.datatime
        title = "RTI Noise: %s" %(thisDatetime.strftime("%d-%b-%Y"))
        xlabel = ""
        ylabel = "Range (Km)"
        
        if not self.__isConfig:
            
            nplots = 1
            
            self.setup(idfigure=idfigure,
                       nplots=nplots,
                       wintitle=wintitle,
                       showprofile=showprofile,
                       show=show)
            
            tmin, tmax = self.getTimeLim(x, xmin, xmax)
            if ymin == None: ymin = numpy.nanmin(noisedB)
            if ymax == None: ymax = numpy.nanmax(noisedB)
            
            self.name = thisDatetime.strftime("%Y%m%d_%H%M%S")
            self.__isConfig = True
        
            self.xdata = numpy.array([])
            self.ydata = numpy.array([])
        
        self.setWinTitle(title)
            
        
        title = "RTI Noise %s" %(thisDatetime.strftime("%d-%b-%Y"))
        
        legendlabels = ["channel %d"%idchannel for idchannel in channelList]
        axes = self.axesList[0]
        
        self.xdata = numpy.hstack((self.xdata, x[0:1]))
        
        if len(self.ydata)==0:
            self.ydata = noisedB[channelIndexList].reshape(-1,1)
        else:
            self.ydata = numpy.hstack((self.ydata, noisedB[channelIndexList].reshape(-1,1)))
        
        
        axes.pmultilineyaxis(x=self.xdata, y=self.ydata,
                    xmin=tmin, xmax=tmax, ymin=ymin, ymax=ymax,
                    xlabel=xlabel, ylabel=ylabel, title=title, legendlabels=legendlabels, marker='x', markersize=8, linestyle="solid",
                    XAxisAsTime=True
                    )
            
        self.draw()
        
        if save:
            
            if figfile == None:
                figfile = self.getFilename(name = self.name)
            
            self.saveFigure(figpath, figfile)
            
        if x[1] + (x[1]-x[0]) >= self.axesList[0].xmax:
            self.__isConfig = False
            del self.xdata
            del self.ydata


class SpectraHeisScope(Figure):
    
    
    __isConfig = None
    __nsubplots = None
    
    WIDTHPROF = None
    HEIGHTPROF = None
    PREFIX = 'spc'
    
    def __init__(self):
        
        self.__isConfig = False
        self.__nsubplots = 1
        
        self.WIDTH = 230
        self.HEIGHT = 250
        self.WIDTHPROF = 120
        self.HEIGHTPROF = 0
        self.counterftp = 0
        
    def getSubplots(self):
        
        ncol = int(numpy.sqrt(self.nplots)+0.9)
        nrow = int(self.nplots*1./ncol + 0.9)
        
        return nrow, ncol
    
    def setup(self, idfigure, nplots, wintitle, show):
        
        showprofile = False
        self.__showprofile = showprofile
        self.nplots = nplots
        
        ncolspan = 1
        colspan = 1
        if showprofile:
            ncolspan = 3
            colspan = 2
            self.__nsubplots = 2
        
        self.createFigure(idfigure = idfigure,
                          wintitle = wintitle,
                          widthplot = self.WIDTH + self.WIDTHPROF,
                          heightplot = self.HEIGHT + self.HEIGHTPROF,
                          show = show)
        
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

#    __isConfig = None    
#    def __init__(self):
#        
#        self.__isConfig = False
#        self.WIDTH = 600
#        self.HEIGHT = 200
#    
#    def getSubplots(self):
#        
#        nrow = self.nplots
#        ncol = 3
#        return nrow, ncol
#    
#    def setup(self, idfigure, nplots, wintitle):
#        
#        self.nplots = nplots
#        
#        self.createFigure(idfigure, wintitle)
#        
#        nrow,ncol = self.getSubplots()
#        colspan = 3
#        rowspan = 1
#        
#        for i in range(nplots):
#            self.addAxes(nrow, ncol, i, 0, colspan, rowspan)
    
    def run(self, dataOut, idfigure, wintitle="", channelList=None,
            xmin=None, xmax=None, ymin=None, ymax=None, save=False,
            figpath='./', figfile=None, ftp=False, ftpratio=1, show=True):
        
        """
        
        Input:
            dataOut         :
            idfigure        :
            wintitle        :
            channelList     :
            xmin            :    None,
            xmax            :    None,
            ymin            :    None,
            ymax            :    None,
        """
        
        if dataOut.realtime:
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
        
#        x = dataOut.heightList
        c   =  3E8 
        deltaHeight = dataOut.heightList[1] - dataOut.heightList[0]
        #deberia cambiar para el caso de 1Mhz y 100KHz
        x = numpy.arange(-1*dataOut.nHeights/2.,dataOut.nHeights/2.)*(c/(2*deltaHeight*dataOut.nHeights*1000))
        x= x/(10000.0)
#        y = dataOut.data[channelIndexList,:] * numpy.conjugate(dataOut.data[channelIndexList,:])
#        y = y.real
        datadB = 10.*numpy.log10(dataOut.data_spc)
        y = datadB
        
        thisDatetime = dataOut.datatime
        title = "Scope: %s" %(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
        xlabel = "Frequency x 10000"
        ylabel = "Intensity (dB)"
        
        if not self.__isConfig:
            nplots = len(channelIndexList)
            
            self.setup(idfigure=idfigure,
                       nplots=nplots,
                       wintitle=wintitle,
                       show=show)
            
            if xmin == None: xmin = numpy.nanmin(x)
            if xmax == None: xmax = numpy.nanmax(x)
            if ymin == None: ymin = numpy.nanmin(y)
            if ymax == None: ymax = numpy.nanmax(y)
                
            self.__isConfig = True
        
        self.setWinTitle(title)
        
        for i in range(len(self.axesList)):
            ychannel = y[i,:]
            title = "Channel %d - peak:%.2f" %(i,numpy.max(ychannel))
            axes = self.axesList[i]
            axes.pline(x, ychannel,
                        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,
                        xlabel=xlabel, ylabel=ylabel, title=title, grid='both')
        
        
        self.draw()
            
        if save:
            date = thisDatetime.strftime("%Y%m%d_%H%M%S")
            if figfile == None:
                figfile = self.getFilename(name = date)
            
            self.saveFigure(figpath, figfile)
            
            self.counterftp += 1
            if (ftp and (self.counterftp==ftpratio)):
                figfilename = os.path.join(figpath,figfile)
                self.sendByFTP(figfilename)
                self.counterftp = 0


class RTIfromSpectraHeis(Figure):
    
    __isConfig = None
    __nsubplots = None

    PREFIX = 'rtinoise'
    
    def __init__(self):
        
        self.timerange = 24*60*60
        self.__isConfig = False
        self.__nsubplots = 1
        
        self.WIDTH = 820
        self.HEIGHT = 200
        self.WIDTHPROF = 120
        self.HEIGHTPROF = 0
        self.counterftp = 0
        self.xdata = None
        self.ydata = None
        
    def getSubplots(self):
        
        ncol = 1
        nrow = 1
        
        return nrow, ncol
    
    def setup(self, idfigure, nplots, wintitle, showprofile=True, show=True):
               
        self.__showprofile = showprofile
        self.nplots = nplots
        
        ncolspan = 7
        colspan = 6
        self.__nsubplots = 2
        
        self.createFigure(idfigure = idfigure,
                          wintitle = wintitle,
                          widthplot = self.WIDTH+self.WIDTHPROF,
                          heightplot = self.HEIGHT+self.HEIGHTPROF,
                          show = show)
        
        nrow, ncol = self.getSubplots()
        
        self.addAxes(nrow, ncol*ncolspan, 0, 0, colspan, 1)
        
                        
    def run(self, dataOut, idfigure, wintitle="", channelList=None, showprofile='True',
            xmin=None, xmax=None, ymin=None, ymax=None,
            timerange=None,
            save=False, figpath='./', figfile=None, ftp=False, ftpratio=1, show=True):
        
        if channelList == None:
            channelIndexList = dataOut.channelIndexList
            channelList = dataOut.channelList
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
        x = dataOut.getTimeRange()
        y = dataOut.getHeiRange()
        
        factor = 1
        data = dataOut.data_spc/factor
        data = numpy.average(data,axis=1)
        datadB = 10*numpy.log10(data)
        
#        factor = dataOut.normFactor
#        noise = dataOut.getNoise()/factor
#        noisedB = 10*numpy.log10(noise)
        
        thisDatetime = dataOut.datatime
        title = "RTI: %s" %(thisDatetime.strftime("%d-%b-%Y"))
        xlabel = "Local Time"
        ylabel = "Intensity (dB)"
        
        if not self.__isConfig:
            
            nplots = 1
            
            self.setup(idfigure=idfigure,
                       nplots=nplots,
                       wintitle=wintitle,
                       showprofile=showprofile,
                       show=show)
            
            tmin, tmax = self.getTimeLim(x, xmin, xmax)
            if ymin == None: ymin = numpy.nanmin(datadB)
            if ymax == None: ymax = numpy.nanmax(datadB)
            
            self.name = thisDatetime.strftime("%Y%m%d_%H%M%S")
            self.__isConfig = True
        
            self.xdata = numpy.array([])
            self.ydata = numpy.array([])
        
        self.setWinTitle(title)
            
        
#        title = "RTI %s" %(thisDatetime.strftime("%d-%b-%Y"))
        title = "RTI-Noise - %s" %(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
        
        legendlabels = ["channel %d"%idchannel for idchannel in channelList]
        axes = self.axesList[0]
        
        self.xdata = numpy.hstack((self.xdata, x[0:1]))
        
        if len(self.ydata)==0:
            self.ydata = datadB[channelIndexList].reshape(-1,1)
        else:
            self.ydata = numpy.hstack((self.ydata, datadB[channelIndexList].reshape(-1,1)))
        
        
        axes.pmultilineyaxis(x=self.xdata, y=self.ydata,
                    xmin=tmin, xmax=tmax, ymin=ymin, ymax=ymax,
                    xlabel=xlabel, ylabel=ylabel, title=title, legendlabels=legendlabels, marker='.', markersize=8, linestyle="solid", grid='both',
                    XAxisAsTime=True
                    )
            
        self.draw()
        
        if save:
            
            if figfile == None:
                figfile = self.getFilename(name = self.name)
            
            self.saveFigure(figpath, figfile)
            
            self.counterftp += 1
            if (ftp and (self.counterftp==ftpratio)):
                figfilename = os.path.join(figpath,figfile)
                self.sendByFTP(figfilename)
                self.counterftp = 0
            
        if x[1] + (x[1]-x[0]) >= self.axesList[0].xmax:
            self.__isConfig = False
            del self.xdata
            del self.ydata


               