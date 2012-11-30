import numpy
import datetime
from graphics.figure import  * 

class SpectraPlot(Figure):
    
    __isConfig = None
    
    def __init__(self):
        
        self.__isConfig = False
        self.width = 850
        self.height = 800
    
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
                    self.makeAxes(nrow, ncol, y, x, colspan, rowspan)
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
                    self.makeAxes(nrow, ncol, y, x, colspan, rowspan)
                counter += 1
    
    def setup(self, idfigure, wintitle, width, height, nplots, profile):
        
        self.init(idfigure, wintitle, width, height, nplots)
        
        nrow,ncol = self.getSubplots()
        
        if profile:
            self.setAxesWithProfiles(nrow, ncol) 
        else:
            self.setAxesWithOutProfiles(nrow, ncol)
    
    def run(self, dataOut, idfigure, wintitle="", channelList=None, xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None, profile=False):
        
        if channelList == None:
            channelList = dataOut.channelList
            
        nplots = len(channelList)
        
        z = 10.*numpy.log10(dataOut.data_spc[channelList,:,:])
        
        y = dataOut.heightList
        
        x = numpy.arange(dataOut.nFFTPoints)
        
        noise = dataOut.getNoise()
        
        if not self.__isConfig:
            self.setup(idfigure=idfigure, 
                       wintitle=wintitle,
                       width=self.width, 
                       height=self.height, 
                       nplots=nplots,
                       profile=profile)
            
            if xmin == None: xmin = numpy.min(x)
            if xmax == None: xmax = numpy.max(x)
            if ymin == None: ymin = numpy.min(y)
            if ymax == None: ymax = numpy.max(y)
            if zmin == None: zmin = numpy.min(z)
            if zmax == None: zmax = numpy.max(z)
            
            self.xmin = xmin
            self.xmax = xmax
            self.ymin = ymin
            self.ymax = ymax
            self.zmin = zmin
            self.zmax = zmax
            
            self.__isConfig = True
        
        thisDatetime = datetime.datetime.fromtimestamp(dataOut.utctime)
        dateTime = "%s"%(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
        date = "%s"%(thisDatetime.strftime("%d-%b-%Y"))
        title = "Spectra: " + dateTime
        
        self.setWinTitle(title)
        
        ylabel = "Range[Km]"
        
        xlabel = "m/s"
        
        for i in range(len(self.axesList)):
            title = "Channel %d: %4.2fdB" %(i, noise[i])
            axes = self.axesList[i]
            z2 = z[i,:,:]
            axes.pcolor(x, y, z2, self.xmin, self.xmax, self.ymin, self.ymax, self.zmin, self.zmax, xlabel, ylabel, title)
            
        self.draw()

class Scope(Figure):
    __isConfig = None
    
    def __init__(self):
        self.__isConfig = False
        self.width = 850
        self.height = 800
    
    def getSubplots(self):
        nrow = self.nplots
        ncol = 3
        return nrow, ncol
    
    def setup(self, idfigure, wintitle, width, height, nplots):
        self.init(idfigure, wintitle, width, height, nplots)
        
        nrow,ncol = self.getSubplots()
        colspan = 3
        rowspan = 1
        
        for i in range(nplots):
            self.makeAxes(nrow, ncol, i, 0, colspan, rowspan)
        
        
    
    def run(self, dataOut, idfigure, wintitle="", channelList=None, xmin=None, xmax=None, ymin=None, ymax=None):
        
        if dataOut.isEmpty():
            return None
        
        if channelList == None:
                channelList = dataOut.channelList
            
        nplots = len(channelList)
        
        y = dataOut.data[channelList,:] * numpy.conjugate(dataOut.data[channelList,:])
        y = y.real
        
        x = dataOut.heightList
        
        if not self.__isConfig:
            self.setup(idfigure=idfigure, 
                       wintitle=wintitle,
                       width=self.width, 
                       height=self.height, 
                       nplots=nplots)
            
            if xmin == None: self.xmin = numpy.min(x)
            if xmax == None: self.xmax = numpy.max(x)
            if ymin == None: self.ymin = numpy.min(y)
            if ymax == None: self.ymax = numpy.max(y)
                
            self.__isConfig = True
        
        
        
        thisDatetime = datetime.datetime.fromtimestamp(dataOut.utctime)
        dateTime = "%s"%(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
        date = "%s"%(thisDatetime.strftime("%d-%b-%Y"))
        title = "Scope: " + dateTime
        
        self.setWinTitle(title)
        
        ylabel = "Intensity"
        
        xlabel = "Range[Km]"
        
        for i in range(len(self.axesList)):
            title = "Channel %d: %4.2fdB" %(i, noise[i])
            axes = self.axesList[i]
            y2 = y[i,:]
            axes.pline(x, y2, self.xmin, self.xmax, self.ymin, self.ymax, xlabel, ylabel, title)
        
        self.draw()
            
        
        