'''
Created on Jan 25, 2012

@author: Miguel Urco
'''

import plplot
import numpy

def cmap1_init(colormap="gray"):
    
    ncolor = None
    rgb_lvl = None
    
    # Routine for defining a specific color map 1 in HLS space.
    # if gray is true, use basic grayscale variation from half-dark to light.
    # otherwise use false color variation from blue (240 deg) to red (360 deg).

    # Independent variable of control points.
    i = numpy.array((0., 1.))
    if colormap=="gray":
        ncolor = 256
        # Hue for control points.  Doesn't matter since saturation is zero.
        h = numpy.array((0., 0.))
        # Lightness ranging from half-dark (for interest) to light.
        l = numpy.array((0.5, 1.))
        # Gray scale has zero saturation
        s = numpy.array((0., 0.))
        
        # number of cmap1 colours is 256 in this case.
        plplot.plscmap1n(ncolor)
        # Interpolate between control points to set up cmap1.
        plplot.plscmap1l(0, i, h, l, s)
        
        return None
        
    if colormap=="br_black":
        ncolor = 256
        # Hue ranges from blue (240 deg) to red (0 or 360 deg)
        h = numpy.array((240., 0.))
        # Lightness and saturation are constant (values taken from C example).
        l = numpy.array((0.6, 0.6))
        s = numpy.array((0.8, 0.8))

        # number of cmap1 colours is 256 in this case.
        plplot.plscmap1n(ncolor)
        # Interpolate between control points to set up cmap1.
        plplot.plscmap1l(0, i, h, l, s)
        
        return None
    
    if colormap=="tricolor":
        ncolor = 3
        # Hue ranges from blue (240 deg) to red (0 or 360 deg)
        h = numpy.array((240., 0.))
        # Lightness and saturation are constant (values taken from C example).
        l = numpy.array((0.6, 0.6))
        s = numpy.array((0.8, 0.8))

        # number of cmap1 colours is 256 in this case.
        plplot.plscmap1n(ncolor)
        # Interpolate between control points to set up cmap1.
        plplot.plscmap1l(0, i, h, l, s)
        
        return None
    
    if colormap == 'rgb' or colormap == 'rgb666':
        
        color_sz = 6
        ncolor = color_sz*color_sz*color_sz
        pos = numpy.zeros((ncolor))
        r = numpy.zeros((ncolor))
        g = numpy.zeros((ncolor))
        b = numpy.zeros((ncolor))
        ind = 0
        for ri in range(color_sz):
            for gi in range(color_sz):
                for bi in range(color_sz):
                    r[ind] = ri/(color_sz-1.0)
                    g[ind] = gi/(color_sz-1.0)
                    b[ind] = bi/(color_sz-1.0)
                    pos[ind] = ind/(ncolor-1.0)
                    ind += 1
        rgb_lvl = [6,6,6]  #Levels for RGB colors
        
    if colormap == 'rgb676':
        ncolor = 6*7*6
        pos = numpy.zeros((ncolor))
        r = numpy.zeros((ncolor))
        g = numpy.zeros((ncolor))
        b = numpy.zeros((ncolor))
        ind = 0
        for ri in range(8):
            for gi in range(8):
                for bi in range(4):
                    r[ind] = ri/(6-1.0)
                    g[ind] = gi/(7-1.0)
                    b[ind] = bi/(6-1.0)
                    pos[ind] = ind/(ncolor-1.0)
                    ind += 1
        rgb_lvl = [6,7,6]  #Levels for RGB colors
    
    if colormap == 'rgb685':
        ncolor = 6*8*5
        pos = numpy.zeros((ncolor))
        r = numpy.zeros((ncolor))
        g = numpy.zeros((ncolor))
        b = numpy.zeros((ncolor))
        ind = 0
        for ri in range(8):
            for gi in range(8):
                for bi in range(4):
                    r[ind] = ri/(6-1.0)
                    g[ind] = gi/(8-1.0)
                    b[ind] = bi/(5-1.0)
                    pos[ind] = ind/(ncolor-1.0)
                    ind += 1
        rgb_lvl = [6,8,5]  #Levels for RGB colors
                    
    if colormap == 'rgb884':
        ncolor = 8*8*4
        pos = numpy.zeros((ncolor))
        r = numpy.zeros((ncolor))
        g = numpy.zeros((ncolor))
        b = numpy.zeros((ncolor))
        ind = 0
        for ri in range(8):
            for gi in range(8):
                for bi in range(4):
                    r[ind] = ri/(8-1.0)
                    g[ind] = gi/(8-1.0)
                    b[ind] = bi/(4-1.0)
                    pos[ind] = ind/(ncolor-1.0)
                    ind += 1
        rgb_lvl = [8,8,4]  #Levels for RGB colors
    
    if ncolor == None:
        raise ValueError, "The colormap selected is not valid"
    
    plplot.plscmap1n(ncolor)
    plplot.plscmap1l(1, pos, r, g, b)
    
    return rgb_lvl

class BasicGraph():
    """
    
    """
    
    hasRange = False
    
    xrange = None
    yrange = None
    zrange = None
    
    xlabel = None
    ylabel = None
    title = None
    
    legends = None
    
    __name = None
    __subpage = None
    __szchar = None
    
    __colormap = None
    __colbox  = None
    __colleg = None    
     
    __xpos = None
    __ypos = None
    
    __xopt = None #"bcnst"
    __yopt = None #"bcnstv"
      
    __xlpos = None
    __ylpos = None
    
    __xrangeIsTime = None
    
    #Advanced
    __xg = None
    __yg = None
    
    def __init__(self):
        """
        
        """
        pass
     
    def hasNotXrange(self):
        
        if self.xrange == None:
            return 1
        
        return 0

    def hasNotYrange(self):
        
        if self.yrange == None:
            return 1
        
        return 0

    def hasNotZrange(self):
        
        if self.zrange == None:
            return 1
        
        return 0
    def setName(self, name):
        self.__name = name
        
    def setScreenPos(self, xpos, ypos):
        self.__xpos = xpos
        self.__ypos = ypos
    
    def setScreenPosbyWidth(self, xoff, yoff, xw, yw):
        self.__xpos = [xoff, xoff + xw]
        self.__ypos = [yoff, yoff + yw]
        
    def setSubpage(self, subpage):
        self.__subpage = subpage
        
    def setSzchar(self, szchar):
        self.__szchar = szchar
        
    def setOpt(self, xopt, yopt):
        self.__xopt = xopt
        self.__yopt = yopt

    def setRanges(self, xrange, yrange, zrange=None):
        """
        """
        self.xrange = xrange
        
        self.yrange = yrange
        
        if zrange != None:
            self.zrange = zrange
    
    def setColormap(self, colormap=None):
        
        if colormap == None:
            colormap = self.__colormap
            
        cmap1_init(colormap)
        
    def plotBox(self):
        """
        
        """
        plplot.plvpor(self.__xpos[0], self.__xpos[1], self.__ypos[0], self.__ypos[1])
        plplot.plwind(self.xrange[0], self.xrange[1], self.yrange[0], self.yrange[1])
        plplot.plbox(self.__xopt, 0.0, 0, self.__yopt, 0.0, 0)
        plplot.pllab(self.xlabel, self.ylabel, self.title)
      
    def setup(self, title=None, xlabel=None, ylabel=None, colormap=None):
        """
        """
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.__colormap = colormap
    
    def initSubpage(self):
        
        if plplot.plgdev() == '':
            raise ValueError, "Plot device has not been initialize"
        
        plplot.pladv(self.__subpage)
        plplot.plschr(0.0, self.__szchar)
        
        if self.__xrangeIsTime:
            plplot.pltimefmt("%H:%M")
            
        self.setColormap()
        self.initPlot()
    
    def initPlot(self):
        """
        
        """
        if plplot.plgdev() == '':
            raise ValueError, "Plot device has not been initialize"
        
        xrange = self.xrange
        if xrange == None:
            xrange = [0., 1.]
        
        yrange = self.yrange
        if yrange == None:
            yrange = [0., 1.]
        
        plplot.plvpor(self.__xpos[0], self.__xpos[1], self.__ypos[0], self.__ypos[1])
        plplot.plwind(xrange[0], xrange[1], yrange[0], yrange[1])
        plplot.plbox(self.__xopt, 0.0, 0, self.__yopt, 0.0, 0)
        plplot.pllab(self.xlabel, self.ylabel, self.title)
    
    def colorbarPlot(self):
        data = numpy.arange(256)
        data = numpy.reshape(data, (1,-1))
        
        self.plotBox()
        plplot.plimage(data,
                       self.xrange[0],
                       self.xrange[1],
                       self.yrange[0],
                       self.yrange[1],
                       0.,
                       255.,
                       self.xrange[0],
                       self.xrange[1],
                       self.yrange[0],
                       self.yrange[1],)
        
    def basicXYPlot(self, x, y):
        self.plotBox()
        plplot.plline(x, y)
    
    def basicXYwithErrorPlot(self):
        pass
    
    def basicLineTimePlot(self):
        pass
    
    def basicPcolorPlot(self, data, xmin, xmax, ymin, ymax, zmin, zmax):
        """
        """
        
        self.plotBox()
        plplot.plimage(data, xmin, xmax, ymin, ymax, zmin, zmax, xmin, xmax, ymin, ymax)

        
    def __getBoxpltr(self, x, y, deltax=None, deltay=None):        
        
        if not(len(x)>1 and len(y)>1):
            raise ValueError, "x axis and y axis are empty"
        
        if deltax == None: deltax = x[-1] - x[-2]
        if deltay == None: deltay = y[-1] - y[-2]
        
        x1 = numpy.append(x, x[-1] + deltax)
        y1 = numpy.append(y, y[-1] + deltay)
        
        xg = (numpy.multiply.outer(x1, numpy.ones(len(y1))))
        yg = (numpy.multiply.outer(numpy.ones(len(x1)), y1))
        
        self.__xg = xg
        self.__yg = yg
        
    def advPcolorPlot(self, data, x, y, zmin=0., zmax=0.):
        """
        """
        
        if self.__xg == None and self.__yg == None:
            self.__getBoxpltr(x, y)
        
        plplot.plimagefr(data, x[0], x[-1], y[0], y[-1], 0., 0., zmin, zmax, plplot.pltr2, self.__xg, self.__yg)


class Graph():
    """
    """
    
    graphObjDict = {}
    
    def __init__(self):
        raise

class Spectrum(Graph):
    
    
    showColorbar = False
    showPowerProfile = True
    
    __szchar = 0.7
    
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
        
class CrossSpectrum(Graph):
    
    def __init__(self):
        pass
    
    def setup(self):
        pass
    
    def plotData(self):
        pass
    
class Graph2():
    
    def __init__(self):
        """
        Initiation of variables
        
        Variables:
        
            type:
            windowsize:
            cmap:        colormap
            showcmap:    show the colormap selected on the graphic
        
        """
        
        self.id = None
        self.subpage = None
        self.type = None
        self.windowsize = None
        
        self.szchar = 0.6
        self.title = None
        self.xlabel = None
        self.ylabel = None
        
        self.showGraph2 = None
        self.cmap = None
        self.showcmap = None
        
        self.xrangeIsTime = False
        
        self.xrange = ()
        self.yrange = ()
        self.zrange = ()
        
        self.xscreen = ()
        self.yscreen = ()
        
        self.xcmapscreen = ()
        self.ycmapscreen = ()
        
        self.x2screen = ()
        self.y2screen = ()
                
    
    def setup(self, id, type=0, windowsize=1., title="", xlabel="", ylabel="", showGraph2=None, cmap="jet", showcmap=False, xrangeIsTime=False):
        """
        Inputs:
            type:    This variable indicates the kind of graphic. Instantaneous data or background data
                
                    0: real instantaneous data, like spectrum
                    1: background data, like spectrogram (RTI)
                    2: complex instantaneous data, like cross-spectrum
                    
            windowsize      :    Float. Size of window. It can be full window (1), half window (0.5) or 1 1/2 window (1.5)    
            cmap            :    Set the colormap to use
            showcmap        :    Show the colormap used on the graphic.
        
        
        Variables affected:
            
        """
        
#        if windowsize == 1.:
#            self.xscreen = (0.12, 0.96)
#            self.yscreen = (0.14, 0.94)
#        
#        elif windowsize == 0.5:
#            self.xscreen = (0.12, 0.52)
#            self.yscreen = (0.14, 0.94)
#                
#        elif windowsize == 1.5:
#            self.xscreen = (-0.44, 0.96)
#            self.yscreen = (0.14, 0.94)
#            
#        else:
#            raise ValueError, "type of graphic has not been properly set"
        
        if showGraph2 == None:
            if type == 0:
                showGraph2 = True
            
            if type == 1:
                showGraph2 = True
            
            if type == 2:
                showGraph2 = True
        
        xscreen = (0.12, 0.98)
        yscreen = (0.14, 0.94)
        xcmapscreen = (0., 0.)
        ycmapscreen = (0.14, 0.94)
        x2screen = (0., 0.)
        y2screen = (0.14, 0.94)
            
        if type == 0:
            
            #showGraph2 <> PowerProfile
            if showGraph2 and showcmap:
                xscreen = (0.12, 0.62)
                xcmapscreen = (0.64, 0.70)
                x2screen = (0.75, 0.98)
                
            elif showGraph2:
                xscreen = (0.12, 0.67)
                xcmapscreen = (0., 0.)
                x2screen = (0.7, 0.98)
            
            elif showcmap:
                xscreen = (0.12, 0.85)
                xcmapscreen = (0.87, 0.93)
                x2screen = (0., 0.)   
        
        if type == 1:
            xscreen = (0.06, 0.98)
            yscreen = (0.16, 0.84)
            #showGraph2 <> Phase
            if showGraph2 and showcmap:
                xscreen = (0.06, 0.75)
                xcmapscreen = (0.76, 0.80)
                x2screen = (0.82, 0.98)
                
            elif showGraph2:
                xscreen = (0.06, 0.80)
                xcmapscreen = (0., 0.)
                x2screen = (0.82, 0.98)
            
            elif showcmap:
                xscreen = (0.06, 0.92)
                xcmapscreen = (0.93, 0.96)
                x2screen = (0., 0.)
        
        if type == 2:
            if showGraph2 and showcmap:
                xscreen = (0.12, 0.46)
                xcmapscreen = (0.48, 0.54)
                x2screen = (0.56, 0.98)
                
            elif showGraph2:
                xscreen = (0.12, 0.54)
                xcmapscreen = (0., 0.)
                x2screen = (0.56, 0.98)
            
            elif showcmap:
                xscreen = (0.12, 0.85)
                xcmapscreen = (0.87, 0.93)
                x2screen = (0., 0.)
        
        if type == 3:
            xscreen = (0.12, 0.52)
            x2screen = (0.76, 0.96)
        
        if type == 4:
            xscreen = (-0.44, 0.96)
            x2screen = (0.76, 0.96)
        
        
        self.id = id
        self.subpage = id + 1
        self.type = type
        self.windowsize = windowsize
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.showGraph2 = showGraph2
        self.cmap = cmap
        self.showcmap = showcmap
        self.xrangeIsTime = xrangeIsTime
        
        self.xscreen = xscreen
        self.yscreen = yscreen
        self.x2screen = x2screen
        self.y2screen = y2screen
        self.xcmapscreen = xcmapscreen
        self.ycmapscreen = ycmapscreen        
        
    def setRanges(self, xrange=(), yrange=(), zrange=()):
        """
        Inputs:
            xrange
            yrange
            zrange
        
        Variables affected:
            self.xrange
            self.yrange
            self.zrange
            
        """
        
        self.xrange = xrange
        self.yrange = yrange
        self.zrange = zrange
    
    def setsubPage(self, subpage):
        """
        """
        self.subpage = subpage

    def plotColorbar(self):
        
        if not(self.showcmap):
            return 0
        
        colors = numpy.arange(255)
        colors = numpy.reshape(colors, (1,255))
        
        plplot.plvpor(self.xcmapscreen[0], self.xcmapscreen[1], self.ycmapscreen[0], self.ycmapscreen[1])
        plplot.plwind(0., 1., self.zrange[0], self.zrange[1])
        plplot.plbox("bc",0.0,0,"bc",0.0,0)
        plplot.pllab("", "", "dBs")
        plplot.plimage(colors, 0., 1., self.zrange[0], self.zrange[1], 0., 255., 0., 1., self.zrange[0], self.zrange[1])
        
        return 1
        
    def plotPowerProfile(self, power, ymin, ymax):
        
        if not(self.showGraph2):
            return 0
            
        ny = power.shape[0]
        yscale = (ymax - ymin) / ny
        y = ymin + yscale*numpy.arange(ny)
        
        plplot.plvpor(self.x2screen[0], self.x2screen[1], self.y2screen[0], self.y2screen[1])
        plplot.plwind(self.zrange[0], self.zrange[1], self.yrange[0], self.yrange[1])
        plplot.plbox("bcnst",0.0,0,"bc",0.0,0)
        plplot.pllsty(2)
        plplot.plbox("bcnstg",0.0,0,"bc",0.0,0)
        plplot.pllsty(1)
        plplot.pllab("dB", "", "Power Profile")
        plplot.plline(power, y)
        #plplot.plflush()
        
        return 1
    
    def plotSpectrum(self, data,  xmin=0.0, xmax=1.0, ymin=0.0, ymax=1.0, zmin=None, zmax=None):
        """
        
        """
        if zmin == None: zmin = numpy.nanmin(data)
        if zmax == None: zmax = numpy.nanmax(data)
        
        if self.xrange == (): self.xrange = (xmin, xmax)
        if self.yrange == (): self.yrange = (ymin, ymax)
        if self.zrange == (): self.zrange = (zmin, zmax)
        
        plplot.pladv(self.subpage)
        plplot.plschr(0.0,self.szchar)
        
        power = numpy.average(data, axis=0)
        
        self.plotPowerProfile(power, ymin, ymax)
        self.plotColorbar()
        
        if self.xrangeIsTime:
            plplot.pltimefmt("%H:%M")
        
        plplot.plvpor(self.xscreen[0], self.xscreen[1], self.yscreen[0], self.yscreen[1])
        plplot.plwind(self.xrange[0], self.xrange[1], self.yrange[0], self.yrange[1])
        plplot.plbox("bcnst",0.0,0,"bcnstv",0.0,0)
        plplot.pllab(self.xlabel, self.ylabel, self.title)
        plplot.plimage(data, xmin, xmax, ymin, ymax, zmin, zmax, xmin, xmax, ymin, ymax)
        #plplot.plflush()
    
    def plotSpectrogram(self, data, xmin=0.0, xmax=1.0, ymin=0.0, ymax=1.0, zmin=0.0, zmax=1.0):
        """
        
        """
    
        if zmin == None: zmin = numpy.nanmin(data)
        if zmax == None: zmax = numpy.nanmax(data)
        
        if self.xrange == (): self.xrange = (xmin, xmax)
        if self.yrange == (): self.yrange = (ymin, ymax)
        if self.zrange == (): self.zrange = (zmin, zmax)
        
        plplot.pladv(self.subpage)
        
        plplot.plschr(0.0,self.szchar+0.3)
        
        power = numpy.average(data, axis=0)
        
        self.plotPowerProfile(power, ymin, ymax)
        self.plotColorbar()
        
        if self.xrangeIsTime:
            plplot.pltimefmt("%H:%M")
        
        plplot.plvpor(self.xscreen[0], self.xscreen[1], self.yscreen[0], self.yscreen[1])
        plplot.plwind(self.xrange[0], self.xrange[1], self.yrange[0], self.yrange[1])
        plplot.plbox("bcnst", 0.0, 0, "bcnstv", 0.0, 0)
        
        plplot.pllab(self.xlabel, self.ylabel, self.title)
        plplot.plimage(data, xmin, xmax, ymin, ymax, zmin, zmax, xmin, xmax, ymin, ymax)
        #plplot.plflush()


class PlotData():
    '''
    classdocs
    '''
    
    __INST_XSIZE = 300
    __INST_YSIZE = 280
    __BACKGR_XSIZE = 900
    __BACKGR_YSIZE = 150
    __SPACE = 100 
    
    def __init__(self):
        '''
        Constructor
        '''
        
        self.nx = None
        self.ny = None
        self.xsize = None
        self.ysize = None
        
        self.objGraphList = []

    def getNumSubPages(self):
        
        nT0 = 0
        nT1 = 0
        nT2 = 0
        nT10 = 0
        nT11 = 0
        
        for thisObj in self.objGraphList:
            if thisObj.type == 0:
                nT0 += 1
                continue
            
            if thisObj.type == 1:
                nT1 += 1
                continue
            
            if thisObj.type == 2:
                nT2 += 1
                continue
            
            if thisObj.type == 10:
                nT10 += 1
                continue
            
            if thisObj.type == 11:
                nT11 += 1
                continue
        
        nSpectrum = nT0 + nT2
        
        if (nSpectrum > 0) and nT1*nT10*nT11 == 0:
            
            if nSpectrum in [1,2]: nx = 1
            elif nSpectrum in [3,4,5,6]: nx = 2
            else: nx = 3
            
            if nSpectrum in [1]: ny = 1
            elif nSpectrum in [2,3,4]: ny = 2
            else: ny = 3
        
        elif nT1 > 0 and nT0*nT10*nT11 == 0:
            nx = 1
            ny = nT1
        
        elif nT10 == nT11 and nT0*nT1 == 0:
            nx = nT10
            ny = 2
            
        else:
            raise ValueError, "number of instantaneous and background graphics are not consistent"
        
        self.nx = nx
        self.ny = ny
        
        return nx, ny
    
    def getSizeScreen(self):
            
        nx, ny = self.nx, self.ny
        
        if nx == None or ny == None:
            raise ValueError, "The number of subpages have been set yet, please use the getNumSubPages method for this."
        
        nT0 = 0
        nT1 = 0
        nT2 = 0
        nT10 = 0
        nT11 = 0
        
        for thisObj in self.objGraphList:
            if thisObj.type == 0:
                nT0 += 1
                continue
            
            if thisObj.type == 1:
                nT1 += 1
                continue
            
            if thisObj.type == 2:
                nT2 += 1
                continue
            
            if thisObj.type == 10:
                nT10 += 1
                continue
            
            if thisObj.type == 11:
                nT11 += 1
                continue
        
        if (nT0 > 0 or nT2 > 0) and nT1 > 0:
            raise ValueError, "Different type of graphics have been selected"
        
        if nT0 > 0 or nT2 > 0:
            xsize = ny*self.__INST_XSIZE
            ysize = nx*self.__INST_YSIZE
        
        elif nT1 > 0:
            xsize = nx*self.__BACKGR_XSIZE
            ysize = ny*self.__BACKGR_YSIZE
                    
        elif nT10 == nT11:
            xsize = self.__INST_XSIZE + self.__BACKGR_XSIZE + self.__SPACE
            ysize = nx*self.__BACKGR_YSIZE
        else:
            raise ValueError, "number of instantaneous and background graphics are not consistent"
        
        self.xsize = xsize
        self.ysize = ysize
        
        return xsize, ysize
    
    def setup(self, sizescreen="800x600", save=False, gpath="", filename=""):
        """
        """
        
        self.sizecreen = sizescreen
        self.save = save
        self.gpath = gpath
        self.filename = filename    
    
    def addGraph(self, type=0, xlabel="", ylabel="", title="", showGraph2=False, showcmap=False, cmap="jet", windowsize=1.):
        """
        type:    This variable indicates the kind of graphics. Instantaneous data or background data
                
                0: real instantaneous data, like a spectrum
                1: background data, like a spectrogram (RTI)
                2: complex instantaneous data, like cross-spectrum
                
        
        windowsize:    Float. Size of window. It can be::
                1.0:    full window (1)
                0.5:    half window
                1.5:    1 1/2 window (1.5)
                
        If some graps have already been set with one graphic type the next ones should be of the same type 
        """
        
        id = len(self.objGraphList)
        
        objGraph = Graph2()
        objGraph.setup(id, type, windowsize, title, xlabel, ylabel, showGraph2, cmap, showcmap)
        
        self.objGraphList.append(objGraph)
        
        return id
    
    def getGraphFromId(self, id):
        """
        
        """
        if id >= len(self.objGraphList):
            return None
        
        return self.objGraphList[id]
        
    def setRanges(self, id=0, xrange=(), yrange=(), zrange=()):
        """
        
        """
        thisGraphObj = self.getGraphFromId(id)
        thisGraphObj.setmargins(xrange, yrange, zrange)


    def addText(self, id, xpos=0, ypos=0, text=""):
        """
        
        """
        thisGraphObj = self.getGraphFromId(id)
        
        plplot.pladv(thisGraphObj.subpage)
        plplot.plmtex("b", 5, xpos, ypos, text)
    
    def plotData(self, id, data, xmin=0.0, xmax=1.0, ymin=0.0, ymax=1.0, zmin=None, zmax=None):
        
        thisGraphObj = self.getGraphFromId(id)
        
        if thisGraphObj == None:
            return 0
        
        plplot.plcol0(1)
        if thisGraphObj.type in [0,2]:
            thisGraphObj.plotSpectrum(data, xmin, xmax, ymin, ymax, zmin, zmax)
            return 1
            
        if thisGraphObj.type in [1]:
            thisGraphObj.plotSpectrogram(data, xmin, xmax, ymin, ymax, zmin, zmax)
            return 1
            
        return 0
        
    def iniPlot(self, nx=None, ny=None):
        """
        
        """
        if nx == None or ny == None:
            nx, ny = self.getNumSubPages()
        
        self.getSizeScreen()
        
        plplot.plsetopt("geometry", "%dx%d" %(self.xsize, self.ysize))
        plplot.plsdev("xcairo")
        plplot.plscolbg(255,255,255)
        plplot.plscol0(1,0,0,0)
        plplot.plinit()
        plplot.plssub(nx, ny)
        plplot.pladv(0)
        
        #plplot.plspause(0)
    
    def end(self):
        plplot.plflush()
        plplot.plend()
        
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
    specObj.setup(1, "Spectrum", "Frequency", "Range", "br_black", True, True)
    specObj.plotData(data)
    
    data = numpy.random.uniform(-50,50,(nx,ny))
    
    spec2Obj = Spectrum()
    spec2Obj.setup(2, "Spectrum", "Frequency", "Range", "br_black", True, True)
    spec2Obj.plotData(data)
    
    plplot.plend()
    exit(0)
    
    objPlot = PlotData()
    objPlot.addGraph(1, "Frequency", "Height", "Channel A")
    objPlot.addGraph(1, "Frequency", "Height", "Channel B", showGraph2=True)
    objPlot.addGraph(1, "Frequency", "Height", "Channel C", showcmap=True)
#    
#    objPlot.addGraph(1, "Frequency", "Height", "Cross A-B")
#    objPlot.addGraph(1, "Frequency", "Height", "Cross A-C", showGraph2=True)
#    objPlot.addGraph(1, "Frequency", "Height", "Cross A-D", showcmap=True)
#    
    objPlot.addGraph(1, "Frequency", "Height", "Channel D", showcmap=True, showGraph2=True)
    objPlot.addGraph(1, "Frequency", "Height", "Cross A-E", showcmap=True, showGraph2=True)
    
    objPlot.iniPlot()
    
    for id in range(10):
        objPlot.plotData(id, data)
    
    objPlot.end()