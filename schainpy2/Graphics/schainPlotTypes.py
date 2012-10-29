import numpy
import datetime
import time
from schainPlot import *
#from schainPlotLib import Driver


class RTIFigure(Figure):
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
    xrangestepinsecs = None
    
    
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
        self.drvObj.driver.setColormap(colormap)
    
    def getSubplots(self):
        nrows = self.nframes 
        ncolumns = 1
        return nrows, ncolumns
    
    def setParms(self, data, x, y, xmin, xmax, ymin, ymax, minvalue, maxvalue, xrangestep):
        
        self.starttime = xmin
        self.endtime = xmax
        
        cdatetime = datetime.datetime.utcfromtimestamp(x) #siempre en localtime
        
        mindatetime = datetime.datetime(cdatetime.year,cdatetime.month,cdatetime.day,self.starttime.hour,self.starttime.minute,self.starttime.second)
        if ((xrangestep == 0) or (xrangestep == None)):
            maxdatetime = datetime.datetime(cdatetime.year,cdatetime.month,cdatetime.day,self.endtime.hour,self.endtime.minute,self.endtime.second)
            self.xrangestepinsecs = time.mktime(maxdatetime.timetuple()) - time.mktime(mindatetime.timetuple())
            npoints = 1000.
        if xrangestep == 1:
            maxdatetime = mindatetime + datetime.timedelta(hours=1)
            self.xrangestepinsecs = 60*60.
            npoints = 500.
        if xrangestep == 2:
            maxdatetime = mindatetime + datetime.timedelta(minutes=1)
            self.xrangestepinsecs = 60.
            npoints = 250.
        if xrangestep == 3:
            maxdatetime = mindatetime + datetime.timedelta(seconds=1)
            self.xrangestepinsecs = 1.
            npoints = 125.
            
        xmin = time.mktime(mindatetime.timetuple())
        xmax = time.mktime(maxdatetime.timetuple())
        
        deltax = (xmax-xmin) / npoints
        
        
        if ymin == None: ymin = numpy.min(y)
        if ymax == None: ymax = numpy.max(y)
        
        if minvalue == None: minvalue = 0.
        if maxvalue == None: maxvalue = 50.
        
        self.xmin = xmin
        self.xmax = xmax
        self.minrange = ymin
        self.maxrange = ymax
        self.ymin = ymin
        self.ymax = ymax
        self.minvalue = minvalue
        self.maxvalue = maxvalue
        self.xrangestep = xrangestep
        self.deltax = deltax
        
    
    def changeXRange(self,x):
        
        cdatetime = datetime.datetime.utcfromtimestamp(x) #siempre en localtime
        
        if ((cdatetime.time()>=self.starttime) and (cdatetime.time()<self.endtime)):
            if self.xrangestep == 1:
                mindatetime = datetime.datetime(cdatetime.year,cdatetime.month,cdatetime.day,cdatetime.hour,self.starttime.minute,self.starttime.second)
                
            if self.xrangestep == 2:
                mindatetime = datetime.datetime(cdatetime.year,cdatetime.month,cdatetime.day,cdatetime.hour,cdatetime.minute,self.starttime.second)
                
            if self.xrangestep == 3:
                mindatetime = datetime.datetime(cdatetime.year,cdatetime.month,cdatetime.day,cdatetime.hour,cdatetime.minute,cdatetime.second)

#            mindatetime = datetime.datetime(cdatetime.year,cdatetime.month,cdatetime.day,self.starttime.hour,self.starttime.minute,self.starttime.second)
            self.xmin = time.mktime(mindatetime.timetuple()) - time.timezone
            self.xmax = self.xmin + self.xrangestepinsecs
            
            self.figuretitle = "%s: %s - %s"%(self.figuretitle,
                                              datetime.datetime.utcfromtimestamp(self.xmin).strftime("%d-%b-%Y %H:%M:%S"), 
                                              datetime.datetime.utcfromtimestamp(self.xmax).strftime("%d-%b-%Y %H:%M:%S"))
        
        
            return 1
        
        return 0
        
    
    def createFrames(self):
        for frame in range(self.nframes):
            frameObj = RTIFrame(self.drvObj,frame + 1, self.colorbar, self.showprofile)
            self.frameObjList.append(frameObj)

class RTIFrame(Frame):
    def __init__(self,drvObj,idframe,colorbar,showprofile):
        self.drvObj = drvObj
        self.idframe = idframe
        self.nplots = 1
        
        if showprofile:
            self.nplots += 1
        
        self.colorbar = colorbar
        self.showprofile = showprofile
        self.createPlots()
    
    def createPlots(self):
        plotObjList = []
        
        idplot = 0
        xi, yi, xw, yw = self.getScreenPos(idplot)
        plotObj = RTIPlot(self.drvObj, self.idframe, idplot, xi, yi, xw, yw, self.colorbar)
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
    
    def plot(self, currenttime, range, data):
#        for plotObj in self.plotObjList:
#            plotObj.plot(currenttime, range, data)
            
        plotObj = self.plotObjList[0]
        plotObj.plot(currenttime,range,data)
        
        if self.showprofile:
            plotObj = self.plotObjList[1]
            plotObj.plot(data,range)
    

class RTIPlot(Plot):
    deltax = None
    deltay = None
    xrange = [None,None]
    xminpos = None
    xmaxpos = None
    xg = None
    yg = None
    
    def __init__(self,drvObj, idframe, idplot, xi, yi, xw, yw, colorbar):
        self.drvObj = drvObj
        self.idframe = idframe
        self.idplot = idplot
        self.xi = xi
        self.yi = yi
        self.xw = xw
        self.yw = yw
        self.colorbar = colorbar
        
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
        self.xlabel = "Local Time"
        self.ylabel = "Range (Km)"

    
    def plotBox(self, xmin, xmax, ymin, ymax, minvalue, maxvalue, deltax=None, deltay=None):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.minvalue = minvalue
        self.maxvalue = maxvalue
        self.deltax = deltax
        self.deltay = deltay
        
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
            self.drvObj.driver.plotColorbar(minvalue, maxvalue, self.cbxpos,self.cbypos)
            

    
    def plot(self, currenttime, range, data):
        
        if self.xmaxpos == None:
            self.xmaxpos = currenttime
            
        if currenttime >= self.xmaxpos:
            
            self.xminpos = currenttime
            self.xmaxpos = currenttime + self.deltax           
            x = [currenttime]
            y = range
            z = numpy.reshape(data, (1,-1))
            getGrid = True
            
            self.plotPcolor(x, y, z, self.deltax, self.deltay, getGrid)
            

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
