import numpy
import datetime
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
    ymin = None
    ymax = None
    minvalue = None
    maxvalue = None
    deltax = None
    deltay = None
    frameObjList = []
    figuretitle = ""
    xrangestep = None
    
    def __init__(self,idfigure, nframes, wintitle, xw=600, yw=800, overplot=0, driver='plplot', colormap=None, colorbar= True, *args):
        
        self.drvObj = Driver(driver, idfigure, xw, yw, wintitle, overplot, colormap, colorbar)
        self.driver = driver
        self.idfigure = idfigure
        self.xw = xw
        self.yw = yw
        self.nframes = nframes
        self.wintitle = wintitle
        self.colormap = colormap
        self.overplot = overplot
        self.colorbar = colorbar
#        self.showGraph1 = args[0]
#        self.showGraph2 = args[1]  
        
        self.drvObj.driver.setFigure()
        self.drvObj.driver.setColormap(colormap)
        
        
    
    def __openDriver(self):
        self.drvObj.driver.openDriver()
        
    def __initFigure(self):
        nrows, ncolumns = self.getSubplots()
        self.drvObj.driver.openFigure()
        self.drvObj.driver.setFigTitle(self.figuretitle)
        self.drvObj.driver.setSubPlots(nrows, ncolumns)
    
    def __isOutOfXRange(self,x):
        try:
            if ((x>=self.xmin) and (x<self.xmax)):
                return 0
        except:
            return 0
        
        return 1
    
    def changeXRange(self,x):
        
        pass
    
    def __refresh(self):
        self.drvObj.driver.refresh()
    
    def createFrames(self):
        raise ValueError, "No implemented"
    
    def plot1DArray(self, data1D, x=None, channelList=None, xmin=None, xmax=None, minvalue=None, maxvalue=None, figuretitle=None, save=False, gpath='./'):
        
        nx, ny  = data1D.shape
        
        if channelList == None:
            channelList = range(nx)
            
        if x == None:
            x = numpy.arange(data1D.size)
        
        if figuretitle == None:
            self.figuretitle = ""
        else:
            self.figuretitle = figuretitle 

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
            self.changeXRange(x)
            
            if self.__isFigureOpen:
                self.driverObj.closePage()
                self.__isFigureOpen = False
        
        
        self.__initFigure()

        for channel in channelList:
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

    
    def plotPcolor(self,data, 
                    x=None, 
                    y=None, 
                    channelList=None, 
                    xmin=None, 
                    xmax=None, 
                    ymin=None, 
                    ymax=None,
                    minvalue=None, 
                    maxvalue=None, 
                    figuretitle=None,
                    xrangestep=None, 
                    save=False, 
                    gpath='./',
                    clearData=False,
                    *args):

        
        if figuretitle == None:
            self.figuretitle = ""
        else:
            self.figuretitle = figuretitle 
        
        

        if not(self.__isDriverOpen):
            self.__openDriver()
            self.__isDriverOpen = True
            
        if not(self.__isConfig):
            
            self.setParms(data,x,y,xmin,xmax,ymin,ymax,minvalue,maxvalue,xrangestep)
           
            self.createFrames()
            self.__isConfig = True
        
        if (self.__isOutOfXRange(x)):
            
            if not(self.changeXRange(x)):
                return 0
            
            self.__isFigureOpen = False
        
        if not(self.__isFigureOpen):

            
            self.__initFigure()
            self.__isFigureOpen = True
        
            for channel in channelList:
                if len(args) != 0: value = args[0][channel]
                else: value = args
                
                frameObj = self.frameObjList[channel]
                frameObj.init(self.xmin,
                              self.xmax,
                              self.ymin,
                              self.ymax,
                              self.minvalue,
                              self.maxvalue,
                              self.deltax,
                              self.deltay,
                              self.colorbar,
                              value)
        
        for channel in channelList:
            dataCh = data[channel,:]
            frameObj = self.frameObjList[channel]
            frameObj.plot(x, y, dataCh)
            

        self.__refresh()
        if clearData == True:
            self.__isFigureOpen = False
            

    
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

    def getScreenPosGraph1(self):
        raise ValueError, "No implemented"
    
    def getScreenPos(self, nplot):
        
        if nplot == 0:
            xi, yi, xw, yw = self.getScreenPosMainPlot()
        
        if nplot == 1:
            xi, yi, xw, yw = self.getScreenPosGraph1()
            
        return xi, yi, xw, yw
    
    
    def init(self, xmin, xmax, ymin, ymax, minvalue, maxvalue, deltax=None, deltay=None, colorbar=False, *args):   
         
        for plotObj in self.plotObjList:
            plotObj.setBox(xmin, xmax, ymin, ymax, minvalue, maxvalue, deltax, deltay, colorbar, *args)
            plotObj.plotBox()



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
    colorbar = None
    cbxpos = None
    cbypos = None
    
    def __init__(self, drvObj, idframe, idplot, xi, yi, xw, yw):
        self.drvObj = drvObj
        self.idframe = idframe
        self.idplot = idplot
        self.xi = xi
        self.yi = yi
        self.xw = xw
        self.yw = yw


    def plotBox(self):
        
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
        
        if self.colorbar:
            self.drvObj.driver.plotColorbar(self.minvalue, self.maxvalue, self.cbxpos,self.cbypos)
    
    def plotPcolor(self, x, y, z, deltax, deltay, getGrid):
        
        self.drvObj.driver.pcolor(self.idframe, 
                                  self.xpos, 
                                  self.ypos, 
                                  z, 
                                  x, 
                                  y, 
                                  self.xmin, 
                                  self.xmax, 
                                  self.ymin, 
                                  self.ymax, 
                                  self.minvalue, 
                                  self.maxvalue, 
                                  deltax, 
                                  deltay, 
                                  getGrid,
                                  self.xaxisastime,
                                  self.timefmt)
        
    def plotBasicLine(self,x, y, color):
        """
        Inputs:
            x:
            
            y:
            
            color: 
        """
        self.drvObj.driver.basicLine(self.idframe, self.xpos, self.ypos, x, y, self.xmin, self.xmax, self.ymin, self.ymax, color)
        