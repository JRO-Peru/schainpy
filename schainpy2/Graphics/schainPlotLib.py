import plplot
import numpy
import sys
import plplot #condicional

class Driver:
    def __init__(self,driver, idfigure, xw, yw, wintitle, overplot, colormap, colorbar):
        if driver == "plplot":
            self.driver = PlplotDriver(idfigure, xw, yw, wintitle, overplot, colormap, colorbar)
        elif driver == "mpl":
            self.driver = MplDriver(idfigure, xw, yw, wintitle, overplot, colormap, colorbar)
        else:
            raise ValueError, "The driver: %s is not defined"%driver

class PlplotDriver:
    
    __isDriverOpen = False
    pldriver = None
    __xg = None
    __yg = None
    def __init__(self, idfigure, xw, yw, wintitle, overplot, colormap, colorbar):
        
        if idfigure == None:
            raise ValueError, 'idfigure input must be defined'
        
        self.idfigure = idfigure
        self.xw = xw
        self.yw = yw
        self.wintitle = wintitle
        self.overplot = overplot
        self.colormap = colormap
        self.colorbar = colorbar
    
    def setFigure(self):
        """
        previous configuration to open(init) the plplot driver
        """
        plplot.plsstrm(self.idfigure)
        plplot.plparseopts([self.wintitle],plplot.PL_PARSE_FULL)
        plplot.plsetopt("geometry", "%dx%d"%(self.xw, self.yw))

        
    def openDriver(self, pldriver=None):
        if pldriver == None:
            if sys.platform == "linux":
                pldriver = "xcairo"
            
            if sys.platform == "linux2":
                pldriver = "xcairo"
             
            elif sys.platform == "darwin":
                pldriver = "xwin"
                
            else:
                pldriver = ""
                
        plplot.plsdev("xwin") #para pruebas
        plplot.plscolbg(255,255,255)
        plplot.plscol0(1,0,0,0)
        plplot.plinit()
        plplot.plspause(False)
        
        self.pldriver = pldriver

    def closeDriver(self):
        pass
    
    def openPage(self):
        plplot.plbop()
        plplot.pladv(0)
    
    def closePage(self):
        plplot.pleop()
    
    def openFigure(self):
        plplot.plbop()
        plplot.pladv(0)
    
    def closeFigure(self):
        plplot.pleop()
    
    def setSubPlots(self,nrows, ncolumns):
        plplot.plssub(ncolumns,nrows)
    
    def setPlotLabels(self, xlabel, ylabel, title):
        plplot.pllab(xlabel, ylabel, title)
    
    def setFigTitle(self, title,color="black", szchar=0.55):
        self.setSubPlots(1, 0)
        plplot.pladv(0)
        plplot.plvpor(0., 1., 0., 1.)
        
        if color == "black":
            plplot.plcol0(1)
        if color == "white":
            plplot.plcol0(15)
        
        plplot.plschr(0.0,szchar)
        plplot.plmtex("t",-1., 0.5, 0.5, title)
    
    def plotColorbar(self, minvalue, maxvalue, xpos, ypos):
#        plplot.pladv(id)
#        plplot.plschr(0.0,szchar-0.05)
        xmin = 0; xmax = 1
        ymin = minvalue; ymax = maxvalue
        plplot.plvpor(xpos[0], xpos[1], ypos[0], ypos[1])
        plplot.plwind(float(xmin), float(xmax), float(ymin), float(ymax))
        plplot.plbox("bc", 0.0, 0, "bcmtsv", 0.0, 0)
        
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
    
    
    def __getGrid(self, x, y, deltax=None, deltay=None):        
        
        if not(len(x)>0 and len(y)>0):
            raise ValueError, "x axis and y axis are empty"
        
        if deltax == None: deltax = x[-1] - x[-2]
        if deltay == None: deltay = y[-1] - y[-2]
        
        x1 = numpy.append(x, x[-1] + deltax)
        y1 = numpy.append(y, y[-1] + deltay)
        
        xg = (numpy.multiply.outer(x1, numpy.ones(len(y1))))
        yg = (numpy.multiply.outer(numpy.ones(len(x1)), y1))
        
        return xg, yg
    
    
    def pcolor(self, id, xpos, ypos, data, x, y, xmin, xmax, ymin, ymax, zmin, zmax, deltax=None, deltay=None, getGrid=True, xaxisastime = False, timefmt="%H:%M"):
        
        plplot.pladv(id)
        plplot.plvpor(xpos[0], xpos[1], ypos[0], ypos[1])
        plplot.plwind(float(xmin),float(xmax), float(ymin), float(ymax))
        
        if xaxisastime:
            timedelta = (xmax - xmin + 1)/8.
        
        if getGrid:
            self.__xg, self.__yg = self.__getGrid(x, y, deltax, deltay)
        
        xmin = x[0] 
        xmax = xmin + deltax
        
        plplot.plimagefr(data, 
                         float(xmin), 
                         float(xmax), 
                         float(ymin), 
                         float(ymax), 
                         0., 
                         0., 
                         float(zmin), 
                         float(zmax), 
                         plplot.pltr2, 
                         self.__xg, 
                         self.__yg)
        
        if xaxisastime:
            plplot.pltimefmt(timefmt)
            xopt = "bcstd"
            yopt = "bcst"
            plplot.plbox(xopt, timedelta, 3, yopt, 0.0, 0)
        else:
            xopt = "bcst"
            yopt = "bcst"
            plplot.plbox(xopt, 0.0, 0, yopt, 0.0, 0)
    
    
    def plotBox(self, id, xpos, ypos, xmin, xmax, ymin, ymax, minvalue, maxvalue, xopt, yopt, szchar=0.6, xaxisastime = False, timefmt="%H:%M"):
        """
        xopt, yopt: entradas que no se aplican en MPL
        """
        plplot.pladv(id)
        plplot.plschr(0.0,szchar-0.05)
        plplot.plvpor(xpos[0], xpos[1], ypos[0], ypos[1])
        plplot.plwind(float(xmin), float(xmax), float(ymin), float(ymax))
        if xaxisastime:
            plplot.pltimefmt(timefmt)
            timedelta = (xmax - xmin + 1)/8.
            plplot.plbox(xopt, timedelta, 3, yopt, 0.0, 0)
        else:
            plplot.plbox(xopt, 0.0, 0, yopt, 0.0, 0)
            
    def refresh(self):
        plplot.plflush() 
        
    def basicLine(self, id, xpos, ypos, x, y, xmin, xmax, ymin, ymax, color):
        
        """
        Inputs:
            x: datos en el eje x
            
            y: datos en el eje y
            
            xmin, xmax: intervalo de datos en el eje x
            
            ymin, ymax: intervalo de datos en el eje y
            
            color: color de la linea a dibujarse
            
            id: identificador del plot, en este caso indica al frame que pertenece, la posicion de cada
                plot esta definido por xpos, ypos. 
            
            xpos,ypos: coordenadas que indican la posicion del plot en el frame
            
        """
        
        plplot.pladv(id)
        plplot.plvpor(xpos[0], xpos[1], ypos[0], ypos[1])
        plplot.plwind(float(xmin),float(xmax), float(ymin), float(ymax))
        
        if color == "blue":
            colline = 9
        if color == "green":
            colline = 3
            
        plplot.plcol0(colline)
        plplot.plline(x, y)
        plplot.plcol0(1)
        plplot.plbox("bcst", 0.0, 0, "bcst", 0.0, 0)
    
    def setColormap(self, colormap="gray"):
    
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
        
        if colormap == 'jet':
            ncolor = 256          
            pos = numpy.zeros((ncolor))
            r = numpy.zeros((ncolor))
            g = numpy.zeros((ncolor))
            b = numpy.zeros((ncolor))
            
            for i in range(ncolor):
                if(i <= 35.0/100*(ncolor-1)): rf = 0.0
                elif (i <= 66.0/100*(ncolor-1)): rf = (100.0/31)*i/(ncolor-1) - 35.0/31
                elif (i <= 89.0/100*(ncolor-1)): rf = 1.0
                else: rf = (-100.0/22)*i/(ncolor-1) + 111.0/22
        
                if(i <= 12.0/100*(ncolor-1)): gf = 0.0
                elif(i <= 38.0/100*(ncolor-1)): gf = (100.0/26)*i/(ncolor-1) - 12.0/26
                elif(i <= 64.0/100*(ncolor-1)): gf = 1.0
                elif(i <= 91.0/100*(ncolor-1)): gf = (-100.0/27)*i/(ncolor-1) + 91.0/27
                else: gf = 0.0
        
                if(i <= 11.0/100*(ncolor-1)): bf = (50.0/11)*i/(ncolor-1) + 0.5
                elif(i <= 34.0/100*(ncolor-1)): bf = 1.0
                elif(i <= 65.0/100*(ncolor-1)): bf = (-100.0/31)*i/(ncolor-1) + 65.0/31
                else: bf = 0           
                
                r[i] = rf
                g[i] = gf
                b[i] = bf
            
                pos[i] = float(i)/float(ncolor-1)
            
    
            plplot.plscmap1n(ncolor)
            plplot.plscmap1l(1, pos, r, g, b)
        
        
        
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


class MplDriver:
    def __init__(self):
        pass