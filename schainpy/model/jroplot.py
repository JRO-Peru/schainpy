import numpy
import datetime
from graphics.figure import  * 

class SpectraPlot(Figure):
    
    __isConfig = None
    
    def __init__(self):
        
        self.__isConfig = False
        self.WIDTH = 300
        self.HEIGHT = 400
        
    def getSubplots(self):
        
        ncol = int(numpy.sqrt(self.nplots)+0.9)
        nrow = int(self.nplots*1./ncol + 0.9)
        return nrow, ncol
        
    def setAxesWithOutProfiles(self, nrow, ncol):
        
        colspan = 1
        rowspan = 1
        counter = 0
        
        for y in range(nrow):
            for x in range(ncol):
                if counter < self.nplots:
                    self.addAxes(nrow, ncol, y, x, colspan, rowspan)
                counter += 1
    
    def setAxesWithProfiles(self, nrow, ncol):
        
        colspan = 1
        rowspan = 1
        factor = 2
        ncol = ncol*factor
        counter = 0
        
        for y in range(nrow):
            for x in range(ncol):
                if counter < self.nplots*factor:
#                    plt.subplot2grid((nrow, ncol), (y, x), colspan=colspan, rowspan=rowspan)
                    self.addAxes(nrow, ncol, y, x, colspan, rowspan)
                counter += 1
    
    def setup(self, idfigure, nplots, wintitle, showprofile=True):
        
        self.init(idfigure, nplots, wintitle)
        
        nrow, ncol = self.getSubplots()
        
        if showprofile:
            self.setAxesWithProfiles(nrow, ncol) 
        else:
            self.setAxesWithOutProfiles(nrow, ncol)
    
    def run(self, dataOut, idfigure, wintitle="", channelList=None, showprofile=False,
            xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None):
        
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
            channelList = dataOut.channelList
        
        x = dataOut.getVelRange(1)
        y = dataOut.heightList
        z = 10.*numpy.log10(dataOut.data_spc[channelList,:,:])
        
        noise = dataOut.getNoise()
        
        if not self.__isConfig:
            
            nplots = len(channelList)
            
            self.setup(idfigure=idfigure,
                       nplots=nplots,
                       wintitle=wintitle,
                       showprofile=showprofile)
            
            if xmin == None: xmin = numpy.nanmin(x)
            if xmax == None: xmax = numpy.nanmax(x)
            if ymin == None: ymin = numpy.nanmin(y)
            if ymax == None: ymax = numpy.nanmax(y)
            if zmin == None: zmin = numpy.nanmin(z)*0.9
            if zmax == None: zmax = numpy.nanmax(z)*0.9
            
            self.__isConfig = True
            
        thisDatetime = datetime.datetime.fromtimestamp(dataOut.utctime)
        title = "Spectra: %s" %(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
        xlabel = "Velocity (m/s)"
        ylabel = "Range (Km)"
        
        self.setWinTitle(title)
        
        for i in range(self.nplots):
            title = "Channel %d: %4.2fdB" %(channelList[i], noise[i])
            zchannel = z[i,:,:]
            
            axes = self.axesList[i]
            axes.pcolor(x, y, zchannel,
                        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, zmin=zmin, zmax=zmax,
                        xlabel=xlabel, ylabel=ylabel, title=title,
                        ticksize=9, cblabel='dB')
            
        self.draw()

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
        
        self.init(idfigure, nplots, wintitle)
        
        nrow,ncol = self.getSubplots()
        colspan = 3
        rowspan = 1
        
        for i in range(nplots):
            self.addAxes(nrow, ncol, i, 0, colspan, rowspan)
    
    def run(self, dataOut, idfigure, wintitle="", channelList=None,
            xmin=None, xmax=None, ymin=None, ymax=None):
        
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
            channelList = dataOut.channelList
        
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
        
        
        thisDatetime = datetime.datetime.fromtimestamp(dataOut.utctime)
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
            
        
        