import numpy
import datetime
from graphics.figure import  * 

class Scope(Figure):
    __isConfig = None
    width = None
    height = None
    
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
                       wintitle="Figura 1",
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
        figuretitle = "Scope: " + dateTime
        
        self.setTitle(title=figuretitle)
        
#        self.setTextFromAxes(title=figuretitle)
        
        ylabel = "Intensity"
        
        xlabel = "Range[Km]"
        
        for i in range(len(self.axesList)):
            title = "Channel %d"%i
            axes = self.axesList[i]
            y2 = y[i,:]
            axes.pline(x, y2, self.xmin, self.xmax, self.ymin, self.ymax, xlabel, ylabel, title)
        
        self.draw()
            
        
        