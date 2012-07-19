"""
Created on Feb 7, 2012

@autor $Author$
@version $Id$

"""

import numpy
import plplot

def cmap1_init(colormap="gray"):
    
    if colormap == None:
        return
        
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
        
    if colormap=="br_green":
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

def setColormap(colormap="br_green"):
        cmap1_init(colormap)
        
class BaseGraph:
    """
    
    """
    hasNotRange = True
        
    xrange = None
    yrange = None
    zrange = None
    
    xlabel = None
    ylabel = None
    title = None
    
    legends = None
    
    __name = None
    
    __colormap = None
    __colbox  = None
    __colleg = None    
     
    __xpos = None
    __ypos = None
    
    __xopt = None #"bcnst"
    __yopt = None #"bcnstv"
      
    __xlpos = None
    __ylpos = None
    
    __xrangeIsTime = False
    
    #Advanced
    __xg = None
    __yg = None
    
    def __init__(self):
        """
        
        """
        self.hasNotRange = True
        
        self.xrange = None
        self.yrange = None
        self.zrange = None
        
        self.xlabel = None
        self.ylabel = None
        self.title = None
        
        self.legends = None
        
        self.__name = None
        
        self.__colormap = None
        self.__colbox  = None
        self.__colleg = None    
         
        self.__xpos = None
        self.__ypos = None
        
        self.__xopt = None #"bcnst"
        self.__yopt = None #"bcnstv"
          
        self.__xlpos = None
        self.__ylpos = None
        
        self.__xrangeIsTime = False
        
        #Advanced
        self.__xg = None
        self.__yg = None
        
    def setName(self, name):
        self.__name = name
        
    def setScreenPos(self, xpos, ypos):
        self.__xpos = xpos
        self.__ypos = ypos
        
    def setOpt(self, xopt, yopt):
        self.__xopt = xopt
        self.__yopt = yopt
        
    def setXAxisAsTime(self):
        self.__xrangeIsTime = True

      
    def setup(self, title=None, xlabel=None, ylabel=None, colormap=None):
        """
        """
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.__colormap = colormap
          
    def plotBox(self, xmin, xmax, ymin, ymax, xopt=None, yopt=None, nolabels=False):
        """
        
        """
        if self.__xrangeIsTime:
            plplot.pltimefmt("%H:%M")
            
        plplot.plvpor(self.__xpos[0], self.__xpos[1], self.__ypos[0], self.__ypos[1])
        plplot.plwind(float(xmin),
                      float(xmax),
                      float(ymin),
                      float(ymax)
                      )
        
        if xopt == None: xopt = self.__xopt
        if yopt == None: yopt = self.__yopt 
        
        plplot.plbox(xopt, 0.0, 0, yopt, 0.0, 0)
        
        if not(nolabels):
            plplot.pllab(self.xlabel, self.ylabel, self.title)

    
    def colorbarPlot(self, xmin=0., xmax=1., ymin=0., ymax=1.):
        data = numpy.arange(256)
        data = numpy.reshape(data, (1,-1))
        
        plplot.plimage(data,
                       float(xmin),
                       float(xmax),
                       float(ymin),
                       float(ymax),
                       0.,
                       255.,
                       float(xmin),
                       float(xmax),
                       float(ymin),
                       float(ymax))
        
    def basicXYPlot(self, x, y, xmin=None, xmax=None, ymin=None, ymax=None):
        
        if xmin == None: xmin = x[0]
        if xmax == None: xmax = x[-1]
        if ymin == None: ymin = y[0]
        if ymax == None: ymax = y[-1]
        
        plplot.plline(x, y)
    
    def basicXYwithErrorPlot(self):
        pass
    
    def basicLineTimePlot(self, x, y, xmin=None, xmax=None, ymin=None, ymax=None, colline=1):
        
        if xmin == None: xmin = x[0]
        if xmax == None: xmax = x[-1]
        if ymin == None: ymin = y[0]
        if ymax == None: ymax = y[-1]
        
        plplot.plcol0(colline)
        plplot.plline(x, y)
        plplot.plcol0(1)
    
    def basicPcolorPlot(self, data, x, y, xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None):
        """
        """
        if xmin == None: xmin = x[0]
        if xmax == None: xmax = x[-1]
        if ymin == None: ymin = y[0]
        if ymax == None: ymax = y[-1]
        if zmin == None: zmin = numpy.nanmin(data)
        if zmax == None: zmax = numpy.nanmax(data)
        
        plplot.plimage(data,
                       float(x[0]),
                       float(x[-1]),
                       float(y[0]),
                       float(y[-1]),
                       float(zmin),
                       float(zmax),
                       float(xmin),
                       float(xmax),
                       float(ymin),
                       float(ymax)
                       )
        
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


class LinearPlot:
    
    linearGraphObj = BaseGraph()
    
    __szchar = 1.0
    
    __xrange = None
    
    __yrange = None
    
    __subpage = 0
    m_BaseGraph= BaseGraph()


    
    def __init__(self):
        
        
        key = "linearplot"
        self.linearGraphObj = BaseGraph()
        self.linearGraphObj.setName(key)
        
        self.__subpage = 0
        
    def __iniSubpage(self):
        
        if plplot.plgdev() == '':
            raise ValueError, "Plot device has not been initialize"
        
        plplot.pladv(self.__subpage)
        plplot.plschr(0.0, self.__szchar)
        
        setColormap()
        
    def setScreenPos(self, width='small'):
        
        if width == 'small':
            xi = 0.12; yi = 0.14; xw = 0.78; yw = 0.80
        
        if width == 'medium':
            xi = 0.07; yi = 0.10; xw = 0.90; yw = 0.60
            
        xf = xi + xw
        yf = yi + yw
        
        self.linearGraphObj.setScreenPos([xi, xf], [yi, yf])    

    def setup(self, subpage, title="", xlabel="", ylabel="", XAxisAsTime=False):
        """
        """
        
        self.linearGraphObj.setOpt("bcnts","bcntsv")
        self.linearGraphObj.setup(title,
                               xlabel,
                               ylabel
                               )
        
        self.setScreenPos(width='medium')
        
        if XAxisAsTime:
            self.linearGraphObj.setXAxisAsTime()
        
        self.__subpage = subpage
#    def setRanges(self, xrange, yrange, zrange):
#        
#        self.linearGraphObj.setRanges(xrange, yrange, zrange)
    
    def plotData(self, x, y=None, xmin=None, xmax=None, ymin=None, ymax=None, colline=1):
        """
        Inputs:
            
            x    :    Numpy array of dimension 1
            y    :    Numpy array of dimension 1
        
        """
        
        try:
            nX = numpy.shape(x)
        except:
            raise ValueError, "x is not a numpy array"
        
        if y == None: y = numpy.arange(nX)
        
        if xmin == None: xmin = x[0]
        if xmax == None: xmax = x[-1]
        if ymin == None: ymin = y[0]
        if ymax == None: ymax = y[-1]
        
        self.__iniSubpage()
        self.linearGraphObj.plotBox(xmin, xmax, ymin, ymax)
        self.linearGraphObj.basicLineTimePlot(x, y, xmin, xmax, ymin, ymax, colline)

    def plotComplexData(self, x, y, xmin=None, xmax=None, ymin=None, ymax=None, colline=1, type='power'):
        """
        Inputs:
            
            x    :    Numpy array of dimension 1
            y    :    Complex numpy array of dimension 1
        
        """
        
        try:
            nX = numpy.shape(x)
        except:
            raise ValueError, "x is not a numpy array"
        
        try:
            nY = numpy.shape(y)
        except:
            raise ValueError, "y is not a numpy array"
        
        if xmin == None: xmin = x[0]
        if xmax == None: xmax = x[-1]
        if ymin == None: ymin = y[0]
        if ymax == None: ymax = y[-1]
        
        self.__iniSubpage()
        self.linearGraphObj.plotBox(xmin, xmax, ymin, ymax)
        
        if type.lower() == 'power':
            self.linearGraphObj.basicLineTimePlot(x, abs(y), xmin, xmax, ymin, ymax, colline)
        
        if type.lower() == 'iq':
            
            self.linearGraphObj.basicLineTimePlot(x, y.real, xmin, xmax, ymin, ymax, colline)
            self.linearGraphObj.basicLineTimePlot(x, y.imag, xmin, xmax, ymin, ymax, colline+1)

class ColorPlot:
    
    colorGraphObj = BaseGraph()
    
    graphObjDict = {}
        
    __subpage = 0
    
    __showColorbar = False
    
    __showPowerProfile = True
    
    __szchar = 0.65
    
    __xrange = None
    
    __yrange = None
    
    __zrange = None
    m_BaseGraph= BaseGraph()


    
    def __init__(self):
        
        self.graphObjDict = {}
        
        self.__subpage = 0
        self.__showColorbar = False
        self.__showPowerProfile = True
        
        self.__szchar = 0.65
        self.__xrange = None
        self.__yrange = None
        self.__zrange = None
        
        key = "colorplot"
        self.colorGraphObj = BaseGraph()
        self.colorGraphObj.setName(key)

    def setup(self, subpage, title="", xlabel="Frequency", ylabel="Range", colormap="br_green", showColorbar=False, showPowerProfile=False, XAxisAsTime=False):
        """
        """
        
        self.colorGraphObj.setOpt("bcnts","bcntsv")
        self.colorGraphObj.setup(title,
                               xlabel,
                               ylabel
                               )
        
        self.__subpage = subpage
        self.__colormap = colormap
        self.__showColorbar = showColorbar
        self.__showPowerProfile = showPowerProfile        
        
        if showColorbar:
            key = "colorbar"
            
            cmapObj = BaseGraph()
            cmapObj.setName(key)
            cmapObj.setOpt("bc","bcmtv")
            cmapObj.setup(title="dBs",
                          xlabel="",
                          ylabel="",
                          colormap=colormap)
            
            self.graphObjDict[key] = cmapObj
            
        
        if showPowerProfile:
            key = "powerprof"
            
            powObj = BaseGraph()
            powObj.setName(key)
            powObj.setOpt("bcntg","bc")
            powObj.setup(title="Power Profile",
                         xlabel="dB",
                         ylabel="")
            
            self.graphObjDict[key] = powObj
            
        self.setScreenPos(width='small')
        
        if XAxisAsTime:
            self.colorGraphObj.setXAxisAsTime()
        
    def __iniSubpage(self):
        
        if plplot.plgdev() == '':
            raise ValueError, "Plot device has not been initialize"
        
        plplot.pladv(self.__subpage)
        plplot.plschr(0.0, self.__szchar)
        
        setColormap(self.__colormap)
            
    def setScreenPos(self, width='small'):
        
        if width == 'small':
            xi = 0.13; yi = 0.12; xw = 0.86; yw = 0.70; xcmapw = 0.04; xpoww = 0.25; deltaxcmap = 0.02; deltaxpow = 0.06
        
        if width == 'medium':
            xi = 0.07; yi = 0.10; xw = 0.90; yw = 0.60; xcmapw = 0.04; xpoww = 0.24; deltaxcmap = 0.02; deltaxpow = 0.06
        
        if self.__showColorbar:
            xw -= xcmapw + deltaxcmap
        
        if self.__showPowerProfile:
            xw -= xpoww + deltaxpow
                      
        xf = xi + xw
        yf = yi + yw
        xcmapf = xf
        
        self.colorGraphObj.setScreenPos([xi, xf], [yi, yf])

        if self.__showColorbar:
            xcmapi = xf + deltaxcmap
            xcmapf = xcmapi + xcmapw
            
            key = "colorbar"
            cmapObj = self.graphObjDict[key]
            cmapObj.setScreenPos([xcmapi, xcmapf], [yi, yf])
        
        if self.__showPowerProfile:
            
            xpowi = xcmapf + deltaxpow
            xpowf = xpowi + xpoww
            
            key = "powerprof"
            powObj = self.graphObjDict[key]
            powObj.setScreenPos([xpowi, xpowf], [yi, yf])    


    
    def plotData(self, data, x=None, y=None, xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None, title = ''):
        """
        Inputs:
            
            x    :    Numpy array of dimension 1
            y    :    Numpy array of dimension 1
        
        """
        
        try:
            nX, nY = numpy.shape(data)
        except:
            raise ValueError, "data is not a numpy array"
        
        if x == None: x = numpy.arange(nX)
        if y == None: y = numpy.arange(nY)
        
        if xmin == None: xmin = x[0]
        if xmax == None: xmax = x[-1]
        if ymin == None: ymin = y[0]
        if ymax == None: ymax = y[-1]
        if zmin == None: zmin = numpy.nanmin(data)
        if zmax == None: zmax = numpy.nanmax(data)
        
        plplot.plschr(0.0, self.__szchar)
        self.__iniSubpage()
        self.colorGraphObj.title =  title
        self.colorGraphObj.plotBox(xmin, xmax, ymin, ymax)
        self.colorGraphObj.basicPcolorPlot(data, x, y, xmin, xmax, ymin, ymax, zmin, zmax)
        
        if self.__showColorbar:
            
            
            key = "colorbar"
            cmapObj = self.graphObjDict[key]
            
            plplot.plschr(0.0, self.__szchar-0.05)
            cmapObj.plotBox(0., 1., zmin, zmax)
            cmapObj.colorbarPlot(0., 1., zmin, zmax)
        
        if self.__showPowerProfile:
            power = numpy.average(data, axis=0)
            
            step = (ymax - ymin)/(nY-1)
            heis = numpy.arange(ymin, ymax + step, step)
            
            key = "powerprof"
            powObj = self.graphObjDict[key]
            
            plplot.pllsty(2)
            plplot.plschr(0.0, self.__szchar-0.05)
            powObj.plotBox(zmin, zmax, ymin, ymax, nolabels=True)
            
            plplot.pllsty(1)
            plplot.plschr(0.0, self.__szchar)
            powObj.plotBox(zmin, zmax, ymin, ymax, xopt='bc', yopt='bc')
            
            plplot.plcol0(9)
            powObj.basicXYPlot(power, heis)
            plplot.plcol0(1)
    

class ColorPlotX:

    
    graphObjDict = {}
    showColorbar = False
    showPowerProfile = True
    
    __szchar = 0.7
    __xrange = None
    __yrange = None
    __zrange = None
    
    colorGraphObj = BaseGraph()
    
    def __init__(self):
        
        key = "colorplot"
        self.colorGraphObj.setName(key)
        
        self.__subpage = 0
        
        self.graphObjDict[key] = self.colorGraphObj
        
    def __iniSubpage(self):
        
        if plplot.plgdev() == '':
            raise ValueError, "Plot device has not been initialize"
        
        plplot.pladv(self.__subpage)
        plplot.plschr(0.0, self.__szchar)
        
        setColormap(self.__colormap)
    
    def setScreenPos(self, xi = 0.12, yi = 0.14, xw = 0.78, yw = 0.80, xcmapw = 0.05, xpoww = 0.24, deltaxcmap = 0.02, deltaxpow = 0.06):
        
        if self.showColorbar:
            xw -= xcmapw + deltaxcmap
        
        if self.showPowerProfile:
            xw -= xpoww + deltaxpow
        
        xf = xi + xw
        yf = yi + yw
        xcmapf = xf
        
        self.colorGraphObj.setScreenPos([xi, xf], [yi, yf])
        
        if self.showColorbar:
            xcmapi = xf + deltaxcmap
            xcmapf = xcmapi + xcmapw
            
            key = "colorbar"
            cmapObj = self.graphObjDict[key]
            cmapObj.setScreenPos([xcmapi, xcmapf], [yi, yf])
        
        if self.showPowerProfile:
            
            xpowi = xcmapf + deltaxpow
            xpowf = xpowi + xpoww
            
            key = "powerprof"
            powObj = self.graphObjDict[key]
            powObj.setScreenPos([xpowi, xpowf], [yi, yf])
    
    def setRanges(self, xrange, yrange, zrange):
        
        self.colorGraphObj.setRanges(xrange, yrange, zrange)
        
        keyList = self.graphObjDict.keys()
        
        key = "colorbar"
        if key in keyList:
            cmapObj = self.graphObjDict[key]
            cmapObj.setRanges([0., 1.], zrange)
        
        key = "powerprof"
        if key in keyList:
            powObj = self.graphObjDict[key]
            powObj.setRanges(zrange, yrange)

    def setup(self, subpage, title="", xlabel="", ylabel="", colormap="jet", showColorbar=False, showPowerProfile=False, XAxisAsTime=False):
        """
        """
        
        self.colorGraphObj.setSubpage(subpage)
        self.colorGraphObj.setSzchar(self.__szchar)
        self.colorGraphObj.setOpt("bcnts","bcntsv")
        self.colorGraphObj.setup(title,
                      xlabel,
                      ylabel,
                      colormap)
        
        if showColorbar:
            key = "colorbar"
            
            cmapObj = BaseGraph()
            cmapObj.setName(key)
            cmapObj.setSubpage(subpage)
            cmapObj.setSzchar(self.__szchar)
            cmapObj.setOpt("bc","bcmt")
            cmapObj.setup(title="dBs",
                          xlabel="",
                          ylabel="",
                          colormap=colormap)
            
            self.graphObjDict[key] = cmapObj
            
        
        if showPowerProfile:
            key = "powerprof"
            
            powObj = BaseGraph()
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
            
        self.showColorbar = showColorbar
        self.showPowerProfile = showPowerProfile
        self.setScreenPos()
        
        if XAxisAsTime:
            self.colorGraphObj.setXAxisAsTime()
        #self.setScreenPos(xi = 0.05, yi = 0.18, xw = 0.92, yw = 0.74, xcmapw = 0.015, xpoww = 0.14, deltaxcmap = 0.01, deltaxpow = 0.02)
        
        
    def plotData(self, data, x=None, y=None, xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None):
        """
        """
        
        try:
            nX, nY = numpy.shape(data)
        except:
            raise ValueError, "data is not a numpy array"
        
        if x == None: x = numpy.arange(nX)
        if y == None: y = numpy.arange(nY)
        
        if xmin == None: xmin = x[0]
        if xmax == None: xmax = x[-1]
        if ymin == None: ymin = y[0]
        if ymax == None: ymax = y[-1]
        if zmin == None: zmin = numpy.nanmin(data)
        if zmax == None: zmax = numpy.nanmax(data)
           
        if self.colorGraphObj.hasNotRange:
            self.setRanges([xmin, xmax], [ymin,ymax], [zmin,zmax])
        
        self.colorGraphObj.initSubpage()
        self.colorGraphObj.basicPcolorPlot(data, x, y, xmin, xmax, ymin, ymax, self.colorGraphObj.zrange[0], self.colorGraphObj.zrange[1])
        
        if self.showColorbar:
            key = "colorbar"
            cmapObj = self.graphObjDict[key]
            cmapObj.colorbarPlot()
        
        if self.showPowerProfile:
            power = numpy.average(data, axis=1)
            
            step = (ymax - ymin)/(nY-1)
            heis = numpy.arange(ymin, ymax + step, step)
            
            key = "powerprof"
            powObj = self.graphObjDict[key]
            powObj.basicXYPlot(power, heis)

if __name__ == '__main__':
    
    import numpy
    plplot.plsetopt("geometry", "%dx%d" %(350*2, 300*2))
    plplot.plsdev("xwin")
    plplot.plscolbg(255,255,255)
    plplot.plscol0(1,0,0,0)
    plplot.plspause(False)
    plplot.plinit()
    plplot.plssub(2, 2)
    
    nx = 64
    ny = 100
    
    data = numpy.random.uniform(-50,50,(nx,ny))
    
    baseObj = ColorPlot()
    specObj = ColorPlot()
    baseObj1 = ColorPlot()
    specObj1 = ColorPlot()
    
    baseObj.setup(1, "Spectrum", "Frequency", "Range", "br_green", True, True)
    specObj.setup(2, "Spectrum", "Frequency", "Range", "br_green", False, True)

    baseObj1.setup(3, "Spectrum", "Frequency", "Range", "br_green", False, True)
    specObj1.setup(4, "Spectrum", "Frequency", "Range", "br_green", False, True)
        
    data = numpy.random.uniform(-50,50,(nx,ny))
    
    plplot.plbop()
    baseObj.plotData(data)
    
    specObj.plotData(data)
    
    baseObj1.plotData(data)
    
    specObj1.plotData(data)
    
    plplot.plflush()      
    
    plplot.plspause(1)
    plplot.plend()
    exit(0)


