import nump
import datetime
import time
from schainPlot import *
#from schainPlotLib import Driver


class RTIFigure:
    overplot = 1
    xw = 700
    yw = 650
    showprofile = False
    starttime = None
    endtime = None
    minrange = None
    maxrange = None
    minvalue = None
    maxvalue = None
    
    
    def __init__(self, idfigure, nframes, wintitle, driver, colormap="br_green", colorbar= True, showprofile=False):
        self.idfigure = idfigure
        self.nframes = nframes
        self.wintitle = wintitle
        self.colormap = colormap
        self.colorbar = colorbar
        self.showprofile = showprofile
        self.driver = driver
        self.drvObj = Driver(self.driver, self.idfigure, self.xw, self.yw, self.wintitle, self.overplot, self.colormap, self.colorbar)
        self.drvObj.driver.setFigure()
    
    def getSubplots(self):
        nrows = self.nframes 
        ncolumns = 1
        return nrows, ncolumns
    
    def setParms(self, data, x, y, xmin, xmax, ymin, ymax, minvalue, maxvalue, deltax):
        
        if minvalue == None: minvalue = numpy.min(data)
        if maxvalue == None: maxvalue = numpy.max(data)
        
        utcdatetime = datetime.datetime.utcfromtimestamp(x)
        startdatetime = datetime.datetime(thisDateTime.year,thisDateTime.month,thisDateTime.day,xmin.hour,xmin.minute, xmin.second)
        enddatetime = datetime.datetime(thisDateTime.year,thisDateTime.month,thisDateTime.day,xmax.hour,xmax.minute, xmax.second)
        deltatime = 0
        if timezone == "lt": deltatime = time.timezone
        startTimeInSecs = time.mktime(startdatetime.timetuple()) - deltatime
        endTimeInSecs = time.mktime(enddatetime.timetuple()) - deltatime
        self.starttime = xmin
        self.endtime = xmax
        self.xmin = startTimeInSecs
        self.xmax = self.xmin + interval

        
        
        if ymin == None: ymin = numpy.min(y) 
        if ymin == None: ymax = numpy.max(y)
        
        starttime = None
        endtime = None
        minrange = None
        maxrange = None
        minvalue = None
        maxvalue = None
        
        
        self.xmin = s
        self.xmax = self.starttime + timeinterval
        self.ymin = minrange
        self.ymax = maxrange
        self.minvalue = minvalue
        self.maxvalue = maxvalue

    
    def createFrames(self):
        for frame in range(self.nframes):
            frameObj = ScopeFrame(self.drvObj,frame + 1)
            self.frameObjList.append(frameObj)

class RTIFrame(Frame):
    def __init__(self,drvObj,idframe,colorbar,showProfile):
        self.drvObj = drvObj
        self.idframe = idframe
        self.nplots = 1
        
        if showProfile:
            self.nplots += 1
        
        self.colorbar = colorbar
        self.showprofile = showprofile
        self.createPlots()
    
    def createPlots(self):
        plotObjList = []
        
        idplot = 0
        xi, yi, xw, yw = self.getScreenPos(idplot)
        plotObj = RTIPlot(self.drvObj, self.idframe, idplot, xi, yi, xw, yw)
        plotObjList.append(plotObj)
        
        if self.showprofile:
            idplot = 1
            xi, yi, xw, yw = self.getScreenPos(idplot)
            plotObj = Plot1D(self.drvObj, self.idframe, idplot, xi, yi, xw, yw)
            plotObjList.append(plotObj)
        
        self.plotObjList = plotObjList

    def getScreenPosMainPlot(self):#cada Frame determina las coordenadas de los plots
        xi = 0.07
        
        if self.showprofile:
            xw = 0.65     
        
        else:
            xw = 0.9 
        
        if self.colorbar:
            xw = xw - 0.06
        
        yi = 0.20; yw = 0.75
            
        return xi, yi, xw, yw
    
    def getScreenPosGraph1(self):
        if self.colorbar:
            xi = 0.65 + 0.05
        else:
            xi = 0.9 + 0.05
        
        xw = xi + 0.2
        
        yi = 0.2; yw = 0.75
        
        return xi, yi, xw, yw
    

class RTIPlot:
    def __init__(self,drvObj, idframe, idplot, xi, yi, xw, yw):
        self.drvObj = drvObj
        self.idframe = idframe
        self.idplot = idplot
        self.xi = xi
        self.yi = yi
        self.xw = xw
        self.yw = yw
        
        if self.colorbar:
            cbxi = xw + 0.03
            cbxw = cbxi + 0.03
            cbyi = yi
            cbyw = yw
            self.cbxpos = [cbxi,cbxw]
            self.cbypos = [cbyi,cbyw]
        
        self.xpos = [self.xi,self.xw]
        self.ypos = [self.yi,self.yw]
        self.xaxisastime = True
        self.timefmt = "%H:%M"
        self.xopt = "bcnstd"
        self.yopt = "bcnstv"
        
        self.szchar = 1.0
        self.title = "Channel %d"%self.idframe
        self.xlabel = "x-axis"
        self.ylabel = "y-axis"
    
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
        
        if self.colorbar:
            self.drvObj.driver.colorbar(minvalue, maxvalue, self.cbxpos,self.cbypos)
            
    
    def plot(self):
        pass





class ScopeFigure(Figure):
    overplot = 0
    xw = 700
    yw = 650
    colorbar = None
    
    def __init__(self,idfigure,nframes,wintitle,driver):
        colormap = None
        colorbar = False
        
        self.idfigure = idfigure
        self.nframes = nframes
        self.wintitle = wintitle

        self.colormap = colormap
        self.colorbar = colorbar
        self.driver = driver
        self.drvObj = Driver(self.driver, self.idfigure, self.xw, self.yw, self.wintitle, self.overplot, self.colormap, self.colorbar)
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
