import numpy
import datetime
import time
from schainPlot import *

class CrossSpc(Figure):
    overplot = 0
    xw = 900
    yw = 650
    showprofile = False
    signalA = None
    signalB = None
    coherence = None
    phase = None
    
    def __init__(self, idfigure, nframes, wintitle, driver, colormap, colorbar, showprofile):
        Figure.__init__(self,idfigure, nframes, wintitle, self.xw, self.yw, self.overplot, driver, colormap, colorbar)
        
        self.showprofile = showprofile
        self.signalA = None
        self.signalB = None
        self.coherence = None
        self.phase = None
    
    def getSubplots(self):
        nrows = self.nframes 
        ncolumns = 1
        return nrows, ncolumns
    
    def setParms(self, data, x, y, xmin, xmax, ymin, ymax, minvalue, maxvalue, *args):
        
        if xmin == None: xmin = numpy.min(x)
        if xmax == None: xmax = numpy.max(x)
        if ymin == None: ymin = numpy.min(y)
        if ymax == None: ymax = numpy.max(y)
        if minvalue == None: minvalue = 20.
        if maxvalue == None: maxvalue = 90.
        
        self.signalA = self.data[0]
        self.signalB = self.data[1]
        self.coherence = self.data[2]
        self.phase = self.data[3]
        
        self.xmin = xmin
        self.xmax = xmax
        self.minrange = ymin
        self.maxrange = ymax
        self.ymin = ymin
        self.ymax = ymax
        self.minvalue = minvalue
        self.maxvalue = maxvalue
    
    def changeXRange(self, *args):
        pass
    
    def createFrames(self):
        self.frameObjList = []
        
        for frame in range(self.nframes):
            frameObj = CrossSpcFrame(self.drvObj,frame + 1, self.colorbar, self.showprofile)
            self.frameObjList.append(frameObj)


class CrossSpcFrame(Frame):
    xi = None
    xw = None
    yi = None
    yw = None
    alpha = None
    def __init__(self):
        self.drvObj = drvObj
        self.idframe = idframe
        self.nplots = 4
        
        if showprofile:
            self.nplots += 4
        
        self.colorbar = colorbar
        self.showprofile = showprofile
        self.xi = 0.
        self.xw = 0.
        self.yi = 0.
        self.yw = 0.
        self.alpha = 1.
        
        self.createPlots()
    
    def createPlots(self):
        plotObjList = []
        idplot = 0 
        counter_plot = 0
        for i in range(self.nplots):
            xi, yi, xw, yw = self.getScreenPos(idplot)
            plotObj = SpcPlot(self.drvObj, self.idframe, idplot, xi, yi, xw, yw, self.colorbar)
            plotObjList.append(plotObj)
            
            if self.showprofile:
                xi, yi, xw, yw = self.getScreenPosGraph1(idplot)
                type = "pwbox"
                title = ""
                xlabel = "dB"
                ylabel = ""
                idplot += 1
                plotObj = Plot1D(self.drvObj, self.idframe, idplot, xi, yi, xw, yw, type, title, xlabel, ylabel)
                plotObjList.append(plotObj)
            idplot += 1
            
        self.plotObjList = plotObjList
    
#    def getScreenPos(self,idplot):
#        pass
    
    def getScreenPos(self, diplot):
        
        xi = self.xi
        xw = self.xw
        
        if self.showprofile:
            width = 0.55
            xw += width
        
        
        
        
        self.xi = 0.15 + idplot*self.alpha
        
        if self.showprofile:
            width = 0.55
            self.xw += width     
        
        else:
            width = 0.65
            self.xw += width 
        
        if self.colorbar:
            self.xw = self.xw - 0.06
        
        
        self.alpha = self.xw
        
        yi = 0.20; yw = 0.75
            
        return xi, yi, xw, yw
    
    def getScreenPosGraph1(self):
        if self.colorbar:
            xi = self.xw + 0.08
        else:
            xi = self.xw + 0.05
        
        xw = xi + 0.2
        
        self.alpha = xw
        
        if self.colorbar:
            self.xi = 0.65 + 0.08
        else:
            self.xi = 0.75 + 0.05
        
        xw = xi + 0.2
        
        yi = 0.2; yw = 0.75
        
        return xi, yi, xw, yw
    
    def plot(self,x, y, data):
        plotObj = self.plotObjList[0]
        plotObj.plot(x,y,data)
        
        if self.showprofile:
            plotObj = self.plotObjList[1]
            avg_data = numpy.average(data, axis=0)
            plotObj.plot(avg_data,y)


class SpcFigure(Figure):
    overplot = 0
    xw = 900
    yw = 650
    showprofile = False
    
    def __init__(self, idfigure, nframes, wintitle, driver, colormap, colorbar, showprofile):
        Figure.__init__(self,idfigure, nframes, wintitle, self.xw, self.yw, self.overplot, driver, colormap, colorbar)
        
        self.showprofile = showprofile
    
    def getSubplots(self):
        ncolumns = int(numpy.sqrt(self.nframes)+0.9)
        nrows = int(self.nframes*1./ncolumns + 0.9)
        
        return nrows, ncolumns
    
    def setParms(self, data, x, y, xmin, xmax, ymin, ymax, minvalue, maxvalue, *args):
        
        if xmin == None: xmin = numpy.min(x)
        if xmax == None: xmax = numpy.max(x)
        if ymin == None: ymin = numpy.min(y)
        if ymax == None: ymax = numpy.max(y)
        if minvalue == None: minvalue = 20.
        if maxvalue == None: maxvalue = 90.
        
        self.xmin = xmin
        self.xmax = xmax
        self.minrange = ymin
        self.maxrange = ymax
        self.ymin = ymin
        self.ymax = ymax
        self.minvalue = minvalue
        self.maxvalue = maxvalue
        
    
    def changeXRange(self, *args):
        pass
    
    def createFrames(self):
        
        self.frameObjList = []
        
        for frame in range(self.nframes):
            frameObj = SpcFrame(self.drvObj,frame + 1, self.colorbar, self.showprofile)
            self.frameObjList.append(frameObj)
    
class SpcFrame(Frame):
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
        plotObj = SpcPlot(self.drvObj, self.idframe, idplot, xi, yi, xw, yw, self.colorbar)
        plotObjList.append(plotObj)
        
        if self.showprofile:
            idplot = 1
            xi, yi, xw, yw = self.getScreenPos(idplot)
            type = "pwbox"
            title = ""
            xlabel = "dB"
            ylabel = ""
            szchar = 0.70
            plotObj = Plot1D(self.drvObj, self.idframe, idplot, xi, yi, xw, yw, type, title, xlabel, ylabel, szchar)
            plotObjList.append(plotObj)
        
        self.plotObjList = plotObjList
    
    def getScreenPosMainPlot(self):
        xi = 0.15
        
        if self.showprofile:
            xw = 0.55     
        
        else:
            xw = 0.65 
        
        if self.colorbar:
            xw = xw - 0.06
        
        yi = 0.20; yw = 0.75
            
        return xi, yi, xw, yw
    
    def getScreenPosGraph1(self):
        if self.colorbar:
            xi = 0.65 + 0.08
        else:
            xi = 0.75 + 0.05
        
        xw = xi + 0.2
        
        yi = 0.2; yw = 0.75
        
        return xi, yi, xw, yw
    
    def plot(self,x, y, data):
        plotObj = self.plotObjList[0]
        plotObj.plot(x,y,data)
        
        if self.showprofile:
            plotObj = self.plotObjList[1]
            avg_data = numpy.average(data, axis=0)
            plotObj.plot(avg_data,y)

class SpcPlot(Plot):
    
    getGrid = True
    
    def __init__(self, drvObj, idframe, idplot, xi, yi, xw, yw, colorbar):
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
        self.xaxisastime = False
        self.timefmt = None
        self.xopt = "bcnst"
        self.yopt = "bcnstv"
        
        self.szchar = 0.7
        self.strforchannel = "Channel %d"%self.idframe
        self.xlabel = "m/s"
        self.ylabel = "Range (Km)"
    
    def setBox(self, xmin, xmax, ymin, ymax, minvalue, maxvalue, *args):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.minvalue = minvalue
        self.maxvalue = maxvalue
        self.colorbar = args[2]
        self.title = "%s - %s"%(self.strforchannel,args[3])
        
        
    
    def plot(self, x, y, data):
        z = data
        deltax = None
        deltay = None
        self.plotPcolor(x, y, z, deltax, deltay, self.getGrid)
        self.getGrid = False


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
    timefmt=None
    
    def __init__(self, idfigure, nframes, wintitle, driver, colormap="br_green", colorbar= True, showprofile=False):        
        Figure.__init__(self,idfigure, nframes, wintitle, self.xw, self.yw, self.overplot, driver, colormap, colorbar)
        
        self.showprofile = showprofile
        
    def getSubplots(self):
        nrows = self.nframes 
        ncolumns = 1
        return nrows, ncolumns
    
    def setParms(self, data, x, y, xmin, xmax, ymin, ymax, minvalue, maxvalue, xrangestep, deltax):
        
        self.starttime = xmin
        self.endtime = xmax
        
        cdatetime = datetime.datetime.utcfromtimestamp(x) 
        
        mindatetime = datetime.datetime(cdatetime.year,cdatetime.month,cdatetime.day,self.starttime.hour,self.starttime.minute,self.starttime.second)
        
        maxdatetime = mindatetime + datetime.timedelta(seconds=xrangestep)
        self.xrangestepinsecs = xrangestep
            
        xmin = time.mktime(mindatetime.timetuple())
        xmax = time.mktime(maxdatetime.timetuple())
        
        if self.xrangestepinsecs<=60.:
            self.timefmt="%H:%M:%S"
            
        if self.xrangestepinsecs>0. and self.xrangestepinsecs<=1200.:
            self.timefmt="%H:%M:%S"
            
        if self.xrangestepinsecs>1200. and self.xrangestepinsecs<=86400.:
            self.timefmt="%H:%M"
        
        if self.xrangestepinsecs>86400.:
            self.timefmt="%y:%m:%d:%H"
        
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
        
        cdatetime = datetime.datetime.utcfromtimestamp(x) 
        
        if ((cdatetime.time()>=self.starttime) and (cdatetime.time()<self.endtime)):
            
            mindatetime = datetime.datetime(cdatetime.year,cdatetime.month,cdatetime.day,cdatetime.hour,cdatetime.minute,cdatetime.second)

            self.xmin = time.mktime(mindatetime.timetuple()) - time.timezone
            self.xmax = self.xmin + self.xrangestepinsecs
            
            self.figuretitle = "%s %s : %s"%(self.figuretitle,
                                              datetime.datetime.utcfromtimestamp(self.xmin).strftime("%d-%b-%Y %H:%M:%S"), 
                                              datetime.datetime.utcfromtimestamp(self.xmax).strftime("%d-%b-%Y %H:%M:%S"))
            return 1
        
        return 0
    
    def createFrames(self):
        
        self.frameObjList = []
        
        for frame in range(self.nframes):
            frameObj = RTIFrame(self.drvObj,frame + 1, self.colorbar, self.showprofile, self.timefmt)
            self.frameObjList.append(frameObj)

class RTIFrame(Frame):
    def __init__(self,drvObj,idframe,colorbar,showprofile, timefmt):
        self.drvObj = drvObj
        self.idframe = idframe
        self.nplots = 1
        
        if showprofile:
            self.nplots += 1
        
        self.colorbar = colorbar
        self.showprofile = showprofile
        self.timefmt = timefmt
        self.createPlots()
    
    def createPlots(self):
        plotObjList = []
        
        idplot = 0
        xi, yi, xw, yw = self.getScreenPos(idplot)
        
        plotObj = RTIPlot(self.drvObj, self.idframe, idplot, xi, yi, xw, yw, self.colorbar, self.timefmt)
        plotObjList.append(plotObj)
        
        if self.showprofile:
            idplot = 1
            xi, yi, xw, yw = self.getScreenPos(idplot)
            type = "pwbox"
            title = ""
            xlabel = "dB"
            ylabel = ""
            szchar = 0.75
            plotObj = Plot1D(self.drvObj, self.idframe, idplot, xi, yi, xw, yw, type, title, xlabel, ylabel, szchar)
            plotObjList.append(plotObj)
        
        self.plotObjList = plotObjList

    def getScreenPosMainPlot(self):
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
            xi = 0.65 + 0.08
        else:
            xi = 0.9 + 0.05
        
        xw = xi + 0.2
        
        yi = 0.2; yw = 0.75
        
        return xi, yi, xw, yw
    
    def plot(self, currenttime, range, data):
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
    
    def __init__(self,drvObj, idframe, idplot, xi, yi, xw, yw, colorbar, timefmt):
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
        self.timefmt = timefmt
        self.xopt = "bcnstd"
        self.yopt = "bcnstv"
        
        self.szchar = 1.0
        self.title = "Channel %d"%self.idframe
        self.xlabel = "Local Time"
        self.ylabel = "Range (Km)"

    
    def setBox(self, xmin, xmax, ymin, ymax, minvalue, maxvalue, deltax=None, deltay=None, colorbar=True, *args):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.minvalue = minvalue
        self.maxvalue = maxvalue
        self.deltax = deltax
        self.deltay = deltay
        self.colorbar = colorbar
    
    def plot(self, currenttime, range, data):
        
        if self.xmaxpos == None:
            self.xmaxpos = currenttime
            
#        if currenttime >= self.xmaxpos:
            
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
        
        Figure.__init__(self,idfigure, nframes, wintitle, self.xw, self.yw, self.overplot, driver, colormap, colorbar)
        
    
    def getSubplots(self):
        nrows = self.nframes 
        ncolumns = 1
        return nrows, ncolumns

    def createFrames(self):
        
        self.frameObjList = []
        
        for frame in range(self.nframes):
            frameObj = ScopeFrame(self.drvObj,frame + 1)
            self.frameObjList.append(frameObj)
            
    
class ScopeFrame(Frame):
    xlabel = ""
    ylabel = ""
    title = ""
    szchar = 1.1
    
    def __init__(self,drvObj,idframe):
        self.drvObj = drvObj
        self.idframe = idframe
        self.nplots = 1
        self.createPlots()
#        Frame.__init__(self, drvObj, idframe)

    def getScreenPosMainPlot(self):#cada Frame determina las coordenadas de los plots
        xi = 0.08; xw = 0.9 
        yi = 0.20; yw = 0.75
        return xi,yi,xw,yw

    def createPlots(self):
        plotObjList = []
        for idplot in range(self.nplots):
            xi, yi, xw, yw = self.getScreenPos(idplot)
            type = "scopebox"
            title = "Channel %d"%self.idframe
            xlabel = "range (Km)"
            ylabel = "intensity"
            plotObj = Plot1D(self.drvObj, self.idframe, idplot, xi, yi, xw, yw, type, title, xlabel, ylabel, self.szchar)
            plotObjList.append(plotObj)
            
        self.plotObjList = plotObjList


    def plot(self, x, y, z=None):
        for plotObj in self.plotObjList:
            plotObj.plot(x, y)
            

class Plot1D(Plot):
#    type, title, xlabel, ylabel
    def __init__(self, drvObj, idframe, idplot, xi, yi, xw, yw, type, title, xlabel, ylabel, szchar):
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
        self.szchar = szchar
        self.type = type
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
            

    
    def setBox(self, xmin, xmax, ymin, ymax, minvalue, maxvalue, *args):
        if self.type == "pwbox":
            self.xmin = minvalue
            self.xmax = maxvalue
            self.ymin = ymin
            self.ymax = ymax
            self.minvalue = minvalue
            self.maxvalue = maxvalue
            
        else:
            self.xmin = xmin
            self.xmax = xmax
            self.ymin = ymin
            self.ymax = ymax
            self.minvalue = minvalue
            self.maxvalue = maxvalue
            
        self.colorbar = False

    def plot(self,x,y):
        if y.dtype == "complex128":
            color="blue"
            self.plotBasicLine(x, y.real, color)
            color="red"
            self.plotBasicLine(x, y.imag, color)
        else:
            color="blue"
            self.plotBasicLine(x, y, color)
