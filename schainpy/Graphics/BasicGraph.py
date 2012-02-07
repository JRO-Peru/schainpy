import numpy
import plplot

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

class BasicGraph:
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


