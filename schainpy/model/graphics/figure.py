import numpy
import mpldriver


class Figure:
    
    __driver = mpldriver
    
    idfigure = None
    wintitle = None
    width = None
    height = None
    nplots = None
    
    axesObjList = []
    
    WIDTH = None
    HEIGHT = None
    
    def __init__(self):
         
        raise ValueError, "This method is not implemented"
    
    def getAxesObjList(self):
        
        return self.axesObjList
    
    def getSubplots(self):
        
        raise ValueError, "Abstract method: This method should be defined"
        
    def getScreenDim(self):
        
        nrow, ncol = self.getSubplots()
        
        width = self.WIDTH*ncol
        height = self.HEIGHT*nrow
        
        return width, height
        
    def init(self, idfigure, nplots, wintitle):
        
        """
        Inicializa la figura de acuerdo al driver seleccionado
        Input:
            *args    :    Los parametros necesarios son 
                        idfigure, wintitle, width, height
        """
        
        self.idfigure = idfigure
        
        self.nplots = nplots
        
        self.wintitle = wintitle
        
        self.width, self.height = self.getScreenDim()
        
        self.fig = self.__driver.createFigure(self.idfigure,
                                              self.wintitle,
                                              self.width,
                                              self.height)
        
        self.axesObjList = []
    
    def setDriver(self, driver=mpldriver):
        
        self.__driver = driver
        
    def setTitle(self, title):
        
        self.__driver.setTitle(self.fig, title)
    
    def setWinTitle(self, title):
        
        self.__driver.setWinTitle(self.fig, title=title)
    
    def setTextFromAxes(self, text):
        
        raise ValueError, "Este metodo ha sido reemplazaado con el metodo setText de la clase Axes"
    
    def makeAxes(self, nrow, ncol, xpos, ypos, colspan, rowspan):
        
        raise ValueError, "Este metodo ha sido reemplazaado con el metodo addAxes"
        
    def addAxes(self, *args):
        """
        
        Input:
            *args    :    Los parametros necesarios son
                          nrow, ncol, xpos, ypos, colspan, rowspan
        """
        
        axesObj = Axes(self.fig, *args)
        self.axesObjList.append(axesObj)
    
    def draw(self):
        
        self.__driver.draw(self.fig)
    
    def run(self):
        
        raise ValueError, "This method is not implemented"
    
    axesList = property(getAxesObjList)
            

class Axes:
    
    __driver = mpldriver
    fig = None
    ax = None
    plot = None
    
    firsttime = None
    
    def __init__(self, *args):
        
        """
        
        Input:
            *args    :    Los parametros necesarios son
                          fig, nrow, ncol, xpos, ypos, colspan, rowspan
        """
        
        ax = self.__driver.createAxes(*args)
        self.fig = args[0]
        self.ax = ax
        self.plot = None
        
        self.firsttime = True
        
    def setText(self, text):
        
        self.__driver.setAxesText(self.ax, text)
    
    def pline(self, x, y,
               xmin=None, xmax=None,
               ymin=None, ymax=None,
               xlabel='', ylabel='',
               title='',
               **kwargs):
        
        """
        
        Input:
            x        :    
            y        :  
            xmin    :
            xmax    :
            ymin    :
            ymax    :  
            xlabel    :
            ylabel    :
            title    :
            **kwargs :    Los parametros aceptados son
                          
                          ticksize
        """
        
        if self.firsttime:
            
            if xmin == None: xmin = numpy.nanmin(x)
            if xmax == None: xmax = numpy.nanmax(x)
            if ymin == None: ymin = numpy.nanmin(y)
            if ymax == None: ymax = numpy.nanmax(y)
    
            self.plot = self.__driver.createPline(self.ax, x, y,
                                                  xmin, xmax,
                                                  ymin, ymax,
                                                  xlabel=xlabel,
                                                    ylabel=ylabel,
                                                    title=title,
                                                  **kwargs)
            self.firsttime = False
            return
                    
        self.__driver.pline(self.plot, x, y, xlabel=xlabel,
                                                    ylabel=ylabel,
                                                    title=title)
        
        
    def pcolor(self, x, y, z,
               xmin=None, xmax=None,
               ymin=None, ymax=None,
               zmin=None, zmax=None,
               xlabel='', ylabel='',
               title='',
               **kwargs):
        
        """
        Input:
            x        :    
            y        :    
            x        :
            xmin    :
            xmax    :
            ymin    :
            ymax    :
            zmin    :
            zmax    :
            xlabel    :
            ylabel    :
            title    :
            **kwargs :    Los parametros aceptados son
                          ticksize=9,
                          cblabel=''
        """
        
        if self.firsttime:
            
            if xmin == None: xmin = numpy.nanmin(x)
            if xmax == None: xmax = numpy.nanmax(x)
            if ymin == None: ymin = numpy.nanmin(y)
            if ymax == None: ymax = numpy.nanmax(y)
            if zmin == None: zmin = numpy.nanmin(z)
            if zmax == None: zmax = numpy.nanmax(z)
    
            self.plot = self.__driver.createPcolor(self.ax, x, y, z,
                                                   xmin, xmax,
                                                   ymin, ymax,
                                                   zmin, zmax,
                                                   xlabel=xlabel,
                                                    ylabel=ylabel,
                                                    title=title,
                                                    **kwargs)
            self.firsttime = False
            return
            
        mesh = self.__driver.pcolor(self.plot, z, xlabel=xlabel,
                                                    ylabel=ylabel,
                                                    title=title)
