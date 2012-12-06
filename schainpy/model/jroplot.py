import numpy
import time, datetime
from graphics.figure import  * 

class CrossSpectraPlot(Figure):
    
    __isConfig = None
    __nsubplots = None
    
    WIDTHPROF = None
    HEIGHTPROF = None
    PREFIX = 'spc'
    
    def __init__(self):
        
        self.__isConfig = False
        self.__nsubplots = 4
        
        self.WIDTH = 300
        self.HEIGHT = 400
        self.WIDTHPROF = 0
        self.HEIGHTPROF = 0
        
    def getSubplots(self):
        
        ncol = 4
        nrow = self.nplots
        
        return nrow, ncol
    
    def setup(self, idfigure, nplots, wintitle, showprofile=True):
               
        self.__showprofile = showprofile
        self.nplots = nplots
        
        ncolspan = 1
        colspan = 1
        
        self.createFigure(idfigure = idfigure,
                          wintitle = wintitle,
                          widthplot = self.WIDTH + self.WIDTHPROF,
                          heightplot = self.HEIGHT + self.HEIGHTPROF)
        
        nrow, ncol = self.getSubplots()
        
        counter = 0
        for y in range(nrow):
            for x in range(ncol):                
                self.addAxes(nrow, ncol*ncolspan, y, x*ncolspan, colspan, 1)
                
                counter += 1
    
    def run(self, dataOut, idfigure, wintitle="", pairsList=None, showprofile='True',
            xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None,
            save=False, figpath='./', figfile=None):
        
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
        
        if pairIndexList == []:
            return
        
        x = dataOut.getVelRange(1)
        y = dataOut.getHeiRange()
        z = 10.*numpy.log10(dataOut.data_spc[:,:,:])
        avg = numpy.average(numpy.abs(z), axis=1)
        
        noise = dataOut.getNoise()
        
        if not self.__isConfig:
            
            nplots = len(pairsIndexList)
            
            self.setup(idfigure=idfigure,
                       nplots=nplots,
                       wintitle=wintitle,
                       showprofile=showprofile)
            
            if xmin == None: xmin = numpy.nanmin(x)
            if xmax == None: xmax = numpy.nanmax(x)
            if ymin == None: ymin = numpy.nanmin(y)
            if ymax == None: ymax = numpy.nanmax(y)
            if zmin == None: zmin = numpy.nanmin(avg)*0.9
            if zmax == None: zmax = numpy.nanmax(avg)*0.9
            
            self.__isConfig = True
            
        thisDatetime = dataOut.datatime
        title = "Spectra: %s" %(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
        xlabel = "Velocity (m/s)"
        ylabel = "Range (Km)"
        
        self.setWinTitle(title)
            
        for i in range(self.nplots):
            pair = dataOut.pairsList[pairsIndexList[i]]
            
            title = "Channel %d: %4.2fdB" %(pair[0], noise[pair[0]])
            z = 10.*numpy.log10(dataOut.data_spc[pair[0],:,:])
            axes0 = self.axesList[i*self.__nsubplots]
            axes0.pcolor(x, y, z,
                        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, zmin=zmin, zmax=zmax,
                        xlabel=xlabel, ylabel=ylabel, title=title,
                        ticksize=9, cblabel='')
            
            title = "Channel %d: %4.2fdB" %(pair[1], noise[pair[1]])
            z = 10.*numpy.log10(dataOut.data_spc[pair[1],:,:])
            axes0 = self.axesList[i*self.__nsubplots+1]
            axes0.pcolor(x, y, z,
                        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, zmin=zmin, zmax=zmax,
                        xlabel=xlabel, ylabel=ylabel, title=title,
                        ticksize=9, cblabel='')

            coherenceComplex = dataOut.data_cspc[pairsIndexList[i],:,:]/numpy.sqrt(dataOut.data_spc[pair[0],:,:]*dataOut.data_spc[pair[1],:,:])
            coherence = numpy.abs(coherenceComplex)
            phase = numpy.arctan(-1*coherenceComplex.imag/coherenceComplex.real)*180/numpy.pi
            
            
            title = "Coherence %d%d" %(pair[0], pair[1])
            axes0 = self.axesList[i*self.__nsubplots+2]
            axes0.pcolor(x, y, coherence,
                        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, zmin=-1, zmax=1,
                        xlabel=xlabel, ylabel=ylabel, title=title,
                        ticksize=9, cblabel='')
            
            title = "Phase %d%d" %(pair[0], pair[1])
            axes0 = self.axesList[i*self.__nsubplots+3]
            axes0.pcolor(x, y, phase,
                        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, zmin=-180, zmax=180,
                        xlabel=xlabel, ylabel=ylabel, title=title,
                        ticksize=9, cblabel='')


            
        self.draw()
        
        if save:
            date = thisDatetime.strftime("%Y%m%d")
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
        
        self.__timerange = 24*60*60
        self.__isConfig = False
        self.__nsubplots = 1
        
        self.WIDTH = 800
        self.HEIGHT = 200
        self.WIDTHPROF = 120
        self.HEIGHTPROF = 0
        
    def getSubplots(self):
        
        ncol = 1
        nrow = self.nplots
        
        return nrow, ncol
    
    def setup(self, idfigure, nplots, wintitle, showprofile=True):
               
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
                          heightplot = self.HEIGHT + self.HEIGHTPROF)
        
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
    
    def __getTimeLim(self, x, xmin, xmax):
        
        thisdatetime = datetime.datetime.utcfromtimestamp(numpy.min(x))
        thisdate = datetime.datetime.combine(thisdatetime.date(), datetime.time(0,0,0))
        
        ####################################################
        #If the x is out of xrange
        if xmax < (thisdatetime - thisdate).seconds/(60*60.):
            xmin = None
            xmax = None
        
        if xmin == None:
            td = thisdatetime - thisdate
            xmin = td.seconds/(60*60.)
            
        if xmax == None:
            xmax = xmin + self.__timerange/(60*60.)
        
        mindt = thisdate + datetime.timedelta(0,0,0,0,0, xmin)
        tmin = time.mktime(mindt.timetuple())
        
        maxdt = thisdate + datetime.timedelta(0,0,0,0,0, xmax)
        tmax = time.mktime(maxdt.timetuple())
        
        self.__timerange = tmax - tmin
        
        return tmin, tmax
    
    def run(self, dataOut, idfigure, wintitle="", channelList=None, showprofile='True',
            xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None,
            timerange=None,
            save=False, figpath='./', figfile=None):
        
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
            self.__timerange = timerange
        
        tmin = None
        tmax = None
        x = dataOut.getTimeRange()
        y = dataOut.getHeiRange()
        z = 10.*numpy.log10(dataOut.data_spc[channelIndexList,:,:])
        avg = numpy.average(z, axis=1)
        
        noise = dataOut.getNoise()
            
        if not self.__isConfig:
            
            nplots = len(channelIndexList)
            
            self.setup(idfigure=idfigure,
                       nplots=nplots,
                       wintitle=wintitle,
                       showprofile=showprofile)
            
            tmin, tmax = self.__getTimeLim(x, xmin, xmax)
            if ymin == None: ymin = numpy.nanmin(y)
            if ymax == None: ymax = numpy.nanmax(y)
            if zmin == None: zmin = numpy.nanmin(avg)*0.9
            if zmax == None: zmax = numpy.nanmax(avg)*0.9
            
            self.__isConfig = True
            
        thisDatetime = dataOut.datatime
        title = "RTI: %s" %(thisDatetime.strftime("%d-%b-%Y"))
        xlabel = "Velocity (m/s)"
        ylabel = "Range (Km)"
        
        self.setWinTitle(title)
            
        for i in range(self.nplots):
            title = "Channel %d: %s" %(dataOut.channelList[i], thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
            axes = self.axesList[i*self.__nsubplots]
            z = avg[i].reshape((1,-1))
            axes.pcolor(x, y, z,
                        xmin=tmin, xmax=tmax, ymin=ymin, ymax=ymax, zmin=zmin, zmax=zmax,
                        xlabel=xlabel, ylabel=ylabel, title=title, rti=True, XAxisAsTime=True,
                        ticksize=9, cblabel='', cbsize="1%")
            
            if self.__showprofile:
                axes = self.axesList[i*self.__nsubplots +1]
                axes.pline(avg[i], y,
                        xmin=zmin, xmax=zmax, ymin=ymin, ymax=ymax,
                        xlabel='dB', ylabel='', title='',
                        ytick_visible=False,
                        grid='x')
            
        self.draw()
        
        if save:
            date = thisDatetime.strftime("%Y%m%d")
            if figfile == None:
                figfile = self.getFilename(name = date)
            
            self.saveFigure(figpath, figfile)
            
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
        
        self.WIDTH = 300
        self.HEIGHT = 400
        self.WIDTHPROF = 120
        self.HEIGHTPROF = 0
        
    def getSubplots(self):
        
        ncol = int(numpy.sqrt(self.nplots)+0.9)
        nrow = int(self.nplots*1./ncol + 0.9)
        
        return nrow, ncol
    
    def setup(self, idfigure, nplots, wintitle, showprofile=True):
               
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
                          heightplot = self.HEIGHT + self.HEIGHTPROF)
        
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
            save=False, figpath='./', figfile=None):
        
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
        
        x = dataOut.getVelRange(1)
        y = dataOut.getHeiRange()
        z = 10.*numpy.log10(dataOut.data_spc[channelIndexList,:,:])
        avg = numpy.average(z, axis=1)
        
        noise = dataOut.getNoise()
        
        if not self.__isConfig:
            
            nplots = len(channelIndexList)
            
            self.setup(idfigure=idfigure,
                       nplots=nplots,
                       wintitle=wintitle,
                       showprofile=showprofile)
            
            if xmin == None: xmin = numpy.nanmin(x)
            if xmax == None: xmax = numpy.nanmax(x)
            if ymin == None: ymin = numpy.nanmin(y)
            if ymax == None: ymax = numpy.nanmax(y)
            if zmin == None: zmin = numpy.nanmin(avg)*0.9
            if zmax == None: zmax = numpy.nanmax(avg)*0.9
            
            self.__isConfig = True
            
        thisDatetime = dataOut.datatime
        title = "Spectra: %s" %(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
        xlabel = "Velocity (m/s)"
        ylabel = "Range (Km)"
        
        self.setWinTitle(title)
            
        for i in range(self.nplots):
            title = "Channel %d: %4.2fdB" %(dataOut.channelList[i], noise[i])
            axes = self.axesList[i*self.__nsubplots]
            axes.pcolor(x, y, z[i,:,:],
                        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, zmin=zmin, zmax=zmax,
                        xlabel=xlabel, ylabel=ylabel, title=title,
                        ticksize=9, cblabel='')
            
            if self.__showprofile:
                axes = self.axesList[i*self.__nsubplots +1]
                axes.pline(avg[i], y,
                        xmin=zmin, xmax=zmax, ymin=ymin, ymax=ymax,
                        xlabel='dB', ylabel='', title='',
                        ytick_visible=False,
                        grid='x')
            
        self.draw()
        
        if save:
            date = thisDatetime.strftime("%Y%m%d")
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
    
    def setup(self, idfigure, nplots, wintitle):
        
        self.createFigure(idfigure, wintitle)
        
        nrow,ncol = self.getSubplots()
        colspan = 3
        rowspan = 1
        
        for i in range(nplots):
            self.addAxes(nrow, ncol, i, 0, colspan, rowspan)
            
        self.nplots = nplots
    
    def run(self, dataOut, idfigure, wintitle="", channelList=None,
            xmin=None, xmax=None, ymin=None, ymax=None, save=False, filename=None):
        
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
        y = dataOut.data[channelList,:] * numpy.conjugate(dataOut.data[channelList,:])
        y = y.real
        
        noise = dataOut.getNoise()
        
        if not self.__isConfig:
            nplots = len(channelList)
            
            self.setup(idfigure=idfigure,
                       nplots=nplots,
                       wintitle=wintitle)
            
            if xmin == None: xmin = numpy.nanmin(x)
            if xmax == None: xmax = numpy.nanmax(x)
            if ymin == None: ymin = numpy.nanmin(y)
            if ymax == None: ymax = numpy.nanmax(y)
                
            self.__isConfig = True
        
        
        thisDatetime = dataOut.datatime
        title = "Scope: %s" %(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
        xlabel = "Range (Km)"
        ylabel = "Intensity"
        
        self.setWinTitle(title)
        
        for i in range(len(self.axesList)):
            title = "Channel %d: %4.2fdB" %(i, noise[i])
            axes = self.axesList[i]
            ychannel = y[i,:]
            axes.pline(x, ychannel,
                        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,
                        xlabel=xlabel, ylabel=ylabel, title=title)
        
        self.draw()
            
        if save:
            self.saveFigure(filename)
        