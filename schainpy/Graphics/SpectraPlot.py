import numpy
import plplot

from BasicGraph import *

class Spectrum:
    
    graphObjDict = {}
    showColorbar = False
    showPowerProfile = True
    
    __szchar = 0.7
    __xrange = None
    __yrange = None
    __zrange = None
    specObj = BasicGraph()

    
    def __init__(self):
        
        key = "spec"
        
        specObj = BasicGraph()
        specObj.setName(key)
           
        self.graphObjDict[key] = specObj
        
    
    def setup(self, subpage, title="", xlabel="", ylabel="", colormap="jet", showColorbar=False, showPowerProfile=False):
        """
        """
        
        xi = 0.12; xw = 0.78; xf = xi + xw
        yi = 0.14; yw = 0.80; yf = yi + yw
        
        xcmapi = xcmapf = 0.; xpowi = xpowf = 0.
        
        key = "spec"
        specObj = self.graphObjDict[key]
        specObj.setSubpage(subpage)
        specObj.setSzchar(self.__szchar)
        specObj.setOpt("bcnts","bcnts")
        specObj.setup(title,
                      xlabel,
                      ylabel,
                      colormap)
        
        if showColorbar:
            key = "colorbar"
            
            cmapObj = BasicGraph()
            cmapObj.setName(key)
            cmapObj.setSubpage(subpage)
            cmapObj.setSzchar(self.__szchar)
            cmapObj.setOpt("bc","bcmt")
            cmapObj.setup(title="dBs",
                          xlabel="",
                          ylabel="",
                          colormap=colormap)
            
            self.graphObjDict[key] = cmapObj
            
            xcmapi = 0.
            xcmapw = 0.05
            xw -= xcmapw
        
        if showPowerProfile:
            key = "powerprof"
            
            powObj = BasicGraph()
            powObj.setName(key)
            powObj.setSubpage(subpage)
            powObj.setSzchar(self.__szchar)
            plplot.pllsty(2)
            powObj.setOpt("bcntg","bc")
            plplot.pllsty(1)
            powObj.setup(title="Power Profile",
                         xlabel="dBs",
                         ylabel="")
            
            self.graphObjDict[key] = powObj
            
            xpowi = 0.
            xpoww = 0.24
            xw -= xpoww
        
        xf = xi + xw
        yf = yi + yw
        xcmapf = xf
        
        specObj.setScreenPos([xi, xf], [yi, yf])
        
        if showColorbar:
            xcmapi = xf + 0.02
            xcmapf = xcmapi + xcmapw
            cmapObj.setScreenPos([xcmapi, xcmapf], [yi, yf])
            
        if showPowerProfile:
            xpowi = xcmapf + 0.06
            xpowf = xpowi + xpoww
            powObj.setScreenPos([xpowi, xpowf], [yi, yf])
                
        
#        specObj.initSubpage()
#        
#        if showColorbar:
#            cmapObj.initPlot()
#            
#        if showPowerProfile:
#            powObj.initPlot()
            
        self.showColorbar = showColorbar
        self.showPowerProfile = showPowerProfile
    
    def setRanges(self, xrange, yrange, zrange):
        
        key = "spec"
        specObj = self.graphObjDict[key]
        specObj.setRanges(xrange, yrange, zrange)
        
        keyList = self.graphObjDict.keys()
        
        key = "colorbar"
        if key in keyList:
            cmapObj = self.graphObjDict[key]
            cmapObj.setRanges([0., 1.], zrange)
        
        key = "powerprof"
        if key in keyList:
            powObj = self.graphObjDict[key]
            powObj.setRanges(zrange, yrange)
    
    def plotData(self, data , xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None):
        
        key = "spec"
        specObj = self.graphObjDict[key]
        specObj.initSubpage()
        
        if xmin == None:
            xmin = 0.
        
        if xmax == None:
            xmax = 1.

        if ymin == None:
            ymin = 0.
        
        if ymax == None:
            ymax = 1.
        
        if zmin == None:
            zmin = numpy.nanmin(data)
        
        if zmax == None:
            zmax = numpy.nanmax(data)
    
        if not(specObj.hasRange):
            self.setRanges([xmin, xmax], [ymin,ymax], [zmin,zmax])
        
        specObj.basicPcolorPlot(data, xmin, xmax, ymin, ymax, specObj.zrange[0], specObj.zrange[1])
        
        if self.showColorbar:
            key = "colorbar"
            cmapObj = self.graphObjDict[key]
            cmapObj.colorbarPlot()
        
        if self.showPowerProfile:
            power = numpy.average(data, axis=1)
            
            step = (ymax - ymin)/(power.shape[0]-1)
            heis = numpy.arange(ymin, ymax + step, step)
            
            key = "powerprof"
            powObj = self.graphObjDict[key]
            powObj.basicXYPlot(power, heis)
        
class CrossSpectrum:
    graphObjDict = {}
    showColorbar = False
    showPowerProfile = True
    
    __szchar = 0.7
    __showPhase = False
    __xrange = None
    __yrange = None
    __zrange = None
    m_BasicGraph= BasicGraph()

    def __init__(self):
        pass

    def setup(self, subpage, title, xlabel, ylabel, colormap, showColorbar, showPowerProfile):
        pass

    def setRanges(self, xrange, yrange, zrange):
        pass

    def plotData(self, data, xmin, xmax, ymin, ymax, zmin, zmax):
        pass

if __name__ == '__main__':
    
    import numpy
    plplot.plsetopt("geometry", "%dx%d" %(350*2, 300*2))
    plplot.plsdev("xcairo")
    plplot.plscolbg(255,255,255)
    plplot.plscol0(1,0,0,0)
    plplot.plinit()
    plplot.plssub(2, 2)
    
    nx = 64
    ny = 100
    
    data = numpy.random.uniform(-50,50,(nx,ny))
    
    specObj = Spectrum()
    specObj.setup(1, "Spectrum", "Frequency", "Range", "br_green", False, False)
    specObj.plotData(data)
    
    data = numpy.random.uniform(-50,50,(nx,ny))
    
    spec2Obj = Spectrum()
    spec2Obj.setup(2, "Spectrum", "Frequency", "Range", "br_green", True, True)
    spec2Obj.plotData(data)
    
    plplot.plend()
    exit(0)