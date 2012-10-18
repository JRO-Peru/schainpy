import plplot
import numpy
import sys
import plplot #condicional

class Driver:
    def __init__(self,driver, idfigure, xw, yw, wintitle, overplot, colorbar, colormap):
        if driver == "plplot":
            self.driver = PlplotDriver(idfigure, xw, yw, wintitle, overplot, colorbar, colormap)
        elif driver == "mpl":
            self.driver = MplDriver(idfigure, xw, yw, wintitle, overplot, colormap)
        else:
            raise ValueError, "The driver: %s is not defined"%driver

class PlplotDriver:
    
    __isDriverOpen = False
    pldriver = None
    
    def __init__(self, idfigure, xw, yw, wintitle, overplot, colorbar, colormap):
        
        if idfigure == None:
            raise ValueError, 'idfigure input must be defined'
        
        self.idfigure = idfigure
        self.xw = xw
        self.yw = yw
        self.wintitle = wintitle
        self.overplot = overplot
        self.colorbar = colorbar
        self.colormap = colormap
        
        
    
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
        
    def basicLine(self, x, y, xmin, xmax, ymin, ymax, color, id, xpos, ypos):
        
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
