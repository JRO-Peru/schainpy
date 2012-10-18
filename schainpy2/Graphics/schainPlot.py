import numpy
from schainPlotLib import Driver

class Figure:
    __isDriverOpen = False
    __isFigureOpen = False
    __isConfig = False
    drvObj = None
    idfigure = None
    nframes = None
    wintitle = None
    colormap = None
    driver = None
    overplot = None
    xmin = None
    xmax = None
    minvalue = None
    maxvalue = None
    frameObjList = []
    figtitle = ""
    
    def __init__(self,idfigure, nframes, wintitle, xw=600, yw=800, overplot=0, driver='plplot', colorbar= True, colormap=None, *args):
        self.idfigure = idfigure
        self.nframes = nframes
        self.wintitle = wintitle
        self.xw = xw
        self.yw = yw
        self.overplot = overplot
        self.colorbar = colorbar
        self.colormap = colormap
        #esta seccion deberia ser dinamica de acuerdo a len(args)
        self.showGraph1 = args[0]
        self.showGraph2 = args[1]  
        
        self.drvObj = Driver(driver, idfigure, xw, yw, wintitle, overplot, colorbar, colormap)
        
        self.drvObj.driver.setFigure()
        
    
    def __openDriver(self):
        self.drvObj.driver.openDriver()
    
#    def __openFigure(self):
#        nrows, ncolumns = self.getSubplots()
#        self.drvObj.driver.openFigure()
#        self.drvObj.driver.setTitleFig(title)
#        self.drvObj.driver.setSubPlots(nrows, ncolumns)
        
    def __initFigure(self):
        nrows, ncolumns = self.getSubplots()
        self.drvObj.driver.openFigure()
        self.drvObj.driver.setFigTitle(self.figtitle)
        self.drvObj.driver.setSubPlots(nrows, ncolumns)
    
    def __isOutOfXRange(self,x):
        return 1
    
    def __refresh(self):
        self.drvObj.driver.refresh()
    
    def createFrames(self):
        raise ValueError, "No implemented"
    
    def plot1DArray(self, data1D, x=None, channelList=None, xmin=None, xmax=None, minvalue=None, maxvalue=None, figtitle=None, save=False, gpath='./'):
        
        nx, ny  = data1D.shape
        
        if channelList == None:
            channelList = range(nx)
            
        if x == None:
            x = numpy.arange(data1D.size)
        
        if figtitle == None:
            self.figtitle = ""
        else:
            self.figtitle = figtitle 

        if not(self.__isDriverOpen):
            self.__openDriver()
            self.__isDriverOpen = True
        
        if not(self.__isConfig):
            self.xmin = xmin
            self.xmax = xmax
            self.minvalue = minvalue
            self.maxvalue = maxvalue
            
            if self.xmin == None: self.xmin = numpy.min(x)
            if self.xmax == None: self.xmax = numpy.max(x)
            if self.minvalue == None: self.minvalue = numpy.min(data1D)
            if self.maxvalue == None: self.maxvalue = numpy.max(data1D)
            
            self.createFrames()
            self.__isConfig = True
        
        if not(self.__isOutOfXRange(x)):
            self.__changeXRange(x)
            
            if self.__isFigureOpen:
                self.driverObj.closePage()
                self.__isFigureOpen = False
        
        self.__initFigure()

        for channel in channelList:
#            frametitle = self.plotTitleDict[channel]
            frameObj = self.frameObjList[channel]
            frameObj.init(xmin=self.xmin,
                          xmax=self.xmax,
                          ymin=self.minvalue,
                          ymax=self.maxvalue,
                          minvalue=self.minvalue,
                          maxvalue=self.maxvalue)
            
        for channel in channelList:
            dataCh = data1D[channel,:]
            frameObj = self.frameObjList[channel]
#            frameObj.clearData()
            frameObj.plot(x, dataCh)
            
#            frameObj.refresh()
        self.__refresh()
    

#        
#        if save:
#            self.colorplotObj.setFigure(indexPlot)
#            path = "/home/roj-idl71/tmp/"
#            now = datetime.datetime.now().timetuple()
#            file = "spc_img%02d_%03d_%02d%02d%02d.png"%(indexPlot,now[7],now[3],now[4],now[5])
#            filename = os.path.join(path,file)
#            self.colorplotObj.savePlot(indexPlot, filename)
#        
#        self.colorplotObj.closePage()
    
class Frame:
    nplots = None
    plotObjList = []
    title = ""
    def __init__(self,drvObj, idframe):
        self.drvObj = drvObj
        self.idframe = idframe
        self.createPlots()
    
    def createPlots(self):
        raise ValueError, "No implemented"
    
    def getScreenPosMainPlot(self):
        raise ValueError, "No implemented"

    def getScreenPos(self, nplot):
        
        if nplot == 0:
            xi, yi, xw, yw = self.getScreenPosMainPlot()
        return xi, yi, xw, yw
    
    
    def init(self, xmin, xmax, ymin, ymax, minvalue, maxvalue):   
         
        for plotObj in self.plotObjList:
            plotObj.plotBox(xmin, xmax, ymin, ymax, minvalue, maxvalue)
#            plotObj.setLabels() # ? evaluar si conviene colocarlo dentro del plotbox
    
    def refresh(self):
        for plotObj in self.plotObjList:
            plotObj.refresh()

class Plot:
    title = ""
    xlabel = ""
    ylabel = ""
    xaxisastime = None
    timefmt = None
    xopt = ""  
    yopt = ""
    xpos = None
    ypos = None
    szchar = None
    idframe = None
    idplot = None
    
    def __init__(self, drvObj, idframe, idplot, xi, yi, xw, yw):
        self.drvObj = drvObj
        self.idframe = idframe
        self.idplot = idplot
        self.xi = xi
        self.yi = yi
        self.xw = xw
        self.yw = yw

#    def setLabels(self):
#        self.drvObj.driver.setPlotLabels(self.xlabel, self.ylabel, self.title)

    def plotBox(self, xmin, xmax, ymin, ymax, minvalue, maxvalue):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.minvalue = minvalue
        self.maxvalue = maxvalue
        
        self.drvObj.driver.plotBox(self.idframe, 
                                   self.xpos, 
                                   self.ypos, 
                                   self.xmin, 
                                   self.xmax, 
                                   self.ymin, 
                                   self.ymax, 
                                   self.minvalue, 
                                   self.maxvalue, 
                                   self.xopt, 
                                   self.yopt, 
                                   self.szchar, 
                                   self.xaxisastime, 
                                   self.timefmt)
        
        self.drvObj.driver.setPlotLabels(self.xlabel, self.ylabel, self.title)
        
    def plotBasicLine(self,x, y, color):
        """
        Inputs:
            x:
            
            y:
            
            color: 
        """
        self.drvObj.driver.basicLine(x, y, self.xmin, self.xmax, self.ymin, self.ymax, color, self.idframe, self.xpos, self.ypos)

        
        