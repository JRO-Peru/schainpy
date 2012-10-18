import numpy
from schainPlot import *
#from schainPlotLib import Driver

class ScopeFigure(Figure):
    overplot = 0
    xw = 700
    yw = 650
    colorbar = None
#    frameObjList = []
    
    def __init__(self,idfigure,nframes,wintitle,driver):
        colormap = None
        colorbar = False
        addGraph = 0
        args=(addGraph, addGraph)
        
        
        self.idfigure = idfigure
        self.nframes = nframes
        self.wintitle = wintitle
#        self.xw = 
#        self.yw = 
#        self.overplot = 
        self.driver = driver
        self.colorbar = colorbar
        self.colormap = colormap
        
        self.drvObj = Driver(self.driver, self.idfigure, self.xw, self.yw, self.wintitle, self.overplot, self.colorbar, self.colormap)
        self.drvObj.driver.setFigure()
    
#        Figure.__init__(self,idfigure,nframes,wintitle,self.xw,self.yw,self.overplot,driver,colorbar,colormap,*args)
    
    def getSubplots(self):
        nrows = self.nframes 
        ncolumns = 1
        return nrows, ncolumns

    def createFrames(self):
        for frame in range(self.nframes):
            frameObj = ScopeFrame(self.drvObj,frame + 1)
            self.frameObjList.append(frameObj)
            
    
class ScopeFrame(Frame):
#    plotObjList = []
    xlabel = ""
    ylabel = ""
    title = ""
    def __init__(self,drvObj,idframe):
        self.drvObj = drvObj
        self.idframe = idframe
        self.nplots = 1 #nplots/frame
        self.createPlots()
#        Frame.__init__(self, drvObj, idframe)

    def getScreenPosMainPlot(self):#cada Frame determina las coordenadas de los plots
        xi = 0.07; xw = 0.9 
        yi = 0.20; yw = 0.75
        return xi,yi,xw,yw

    def createPlots(self):
        plotObjList = []
        for idplot in range(self.nplots):
            xi, yi, xw, yw = self.getScreenPos(idplot)
            plotObj = Plot1D(self.drvObj, self.idframe, idplot, xi, yi, xw, yw)
            plotObjList.append(plotObj)
        self.plotObjList = plotObjList
#            self.plotObjList.append(plotObj)

    def plot(self, x, y, z=None):
        for plotObj in self.plotObjList:
            plotObj.plot(x, y)
            

class Plot1D(Plot):
    
    def __init__(self, drvObj, idframe, idplot, xi, yi, xw, yw):
        self.drvObj = drvObj
        self.idframe = idframe
        self.idplot = idplot
        self.xi = xi
        self.yi = yi
        self.xw = xw
        self.yw = yw
        self.xpos = [self.xi,self.xw]
        self.ypos = [self.yi,self.yw]
        self.xaxisastime = False
        self.timefmt = None
        self.xopt = "bcnst"
        self.yopt = "bcnstv"
        self.szchar = 1.0
        self.title = "Channel %d"%self.idframe
        self.xlabel = "x-axis"
        self.ylabel = "y-axis"


    def plot(self,x,y):
        if y.dtype == "complex128":
            color="blue"
            self.plotBasicLine(x, y.real, color)
            color="red"
            self.plotBasicLine(x, y.imag, color)
        else:
            color="blue"
            self.plotBasicLine(x, y, color)
