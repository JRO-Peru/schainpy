
import numpy
import schainPlplotLib

class Figure:
    
    __driverObj = None
    __isDriverOpen = False
    __isFigureOpen = False
    __isConfig = False
    __width = None
    __height = None
    
    idfigure = None
    nframes = None
    wintitle = wintitle
    colormap = None
    driver = None
    overplot = None
        
    frameObjList = []
    
    def __init__(self, idfigure, nframes, wintitle, width=600, height=800, overplot=0, driver='xwin', colormap='br_green', *showGraphs):
        
        self.idfigure = idfigure
        self.nframes = nframes
        self.wintitle = wintitle
        self.colormap = colormap
        self.driver = driver
        self.overplot = overplot
        
        self.showGraphs = showGraphs
        
        self.__driverObj = Driver(driver)
    
    def __createFrames(self):
        
        for frame in range(self.nframes):
            frameObj = Frame(idFrame = frame,
                             showGraph1 = self.showGraph1,
                             showGraph2 = self.showGraph2
                             )
            
            self.frameObjList.append(frameObj)
            
    def __openDriver(self):
        
        self.__driverObj.openDriver(self.idfigure, self.wintitle, self.width, self.height)
    
    def __openFigure(self):
        
        self.__createFrames()
        nrows, ncolumns = self.getSubplots()
        
        self.__driverObj.openFigure()
        self.__driverObj.setSubPlots(nrows, ncolumns)
        
        
    def __verifyXRange(self, x):
        pass
    
    def __updateXRange(self, x):
        pass
    
    def plot1DArray(self, data1D, x=None, xmin=None, xmax=None, minvalue=None, maxvlaue=None, save=False, gpath='./'):
        
        if not(self.__isDriverOpen):
            self.__openDriver()
            self.__isDriverOpen = True
        
        if not(self.__isConfig):
            if x == None: x = numpy.arange(data1D.size)
            if xmin == None: xmin = numpy.min(x)
            if xmax == None: xmax = numpy.max(x)
            if minvalue == None: minvalue = numpy.min(data1D)
            if maxvalue == None: maxvalue = numpy.max(data1D)
            
            self.setRange(xmin=xmin, xmax=xmax, minvalue=minvalue, maxvalue=maxvalue)
            self.__isConfig = True
        
        if not(self.__verifyXRange(x)):
            self.__updateXRange(x)
            if self.__isFigureOpen:
                close_figure()
                self.__isFigureOpen = False
        
        if not(self.__isFigureOpen):
            self.__openFigure()
            self.__isFigureOpen = True
            
            for frame in channelList:
                dataCh = data1D[channel]
                frameObj = frameObjList[channel]
                frameObj.plotBox()
        
        for channel in channelList:
            dataCh = dataArray[channel]
            frameObj = frameObjList[channel]
            frameObj.plot(dataCh)
        
        if not(self.overplot):
            close_figure()
            self.__isFigureOpen = False
        
            
    def plot2DArray(self, x, y, data2D, xmin=None, xmax=None, ymin=None, ymax=None, minvalue=None, maxvalue=None, save=False, gpath='./'):
        
        if not(self.__isCOpen):
            self.__createFrames()
            self.__openFigure()
            self.__isOpen = True
        
        if not(self.__isConfig):
            self.setRange(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, minvalue=minvalue, maxvalue=maxvalue)
            
            self.__isConfig = True
            
        for channel in channelList:
            dataCh = dataArray[channel]
            frameObj = frameObjList[channel]
            frameObj.plot(dataCh)
    
    def saveFigure(self, filename):
        pass
    
    
    def getSubplots(self):
        
        raise ValueError, ''
        
class Frame:
    
    plotObjList = []
    
    def __init__(self, idFrame, showGraph1=False, showGraph2=False):
        
        self.idFrame = idFrame
        self.showGraph1 = showGraph1
        self.showGraph2 = showGraph2
        
        self.nPlots = 2
        self.createPlots()
    
    def __getScreenPosMain(self):
        left = 1.2
        bottom = 2.3
        width = 2.0
        height = 1.4
        
        return left, bottom, width, height
        
    def __getScreenPosGraph1(self):
        left = 1.2
        bottom = 2.3
        width = 2.0
        height = 1.4
        
        return left, bottom, width, height
    
    def __getScreenPosGraph2(self):
        left = 1.2
        bottom = 2.3
        width = 2.0
        height = 1.4
        
        return left, bottom, width, height
            
    def __getScreenPos(self, nplot):
        
        if nplot == 0:
            left, bottom, width, height = self.__getScreenPosMain()
        if nplot == 1:
            left, bottom, width, height = self.__getScreenPosMain()
        if nplot == 2:
            left, bottom, width, height = self.__getScreenPosMain()
        
        return left, bottom, width, height
    
    def createPlots(self):
        
        for nplot in range(self.nPlots):
            left, bottom, width, height = self.__getScreenPos(nplot)
            plotObj = Plot(left, bottom, width, height)
            
            self.plotObjList.append(plotObj)
    
    def setup(self):
        pass
    
    def plot(self, data):
        pass

class Plot:
    
    def __init__(self, left, bottom, width, height):
        
        self.left = left
        self.bottom = bottom
        self.width = width
        self.height = height
    
    def setRange(self, xrange, yrange, zrange):
        pass
    
    def setLabels(self, xlabel, ylabel, zlabel):
        pass
    
    def plotBox(self):
        pass
    
    def plotData(self):
        pass
    
