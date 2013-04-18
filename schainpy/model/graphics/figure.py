import os
import numpy
import time, datetime
import mpldriver
from customftp import *

class Figure:
    
    __driver = mpldriver
    fig = None
    
    id = None
    wintitle = None
    width = None
    height = None
    nplots = None
    timerange = None
    
    axesObjList = []
    
    WIDTH = None
    HEIGHT = None
    PREFIX = 'fig'
    
    def __init__(self):
         
        raise ValueError, "This method is not implemented"
    
    def __del__(self):
        
        self.__driver.closeFigure()
    
    def getFilename(self, name, ext='.png'):
        
        path = '%s%03d' %(self.PREFIX, self.id)
        filename = '%s_%s%s' %(self.PREFIX, name, ext)
        
        return os.path.join(path, filename)
        
    def getAxesObjList(self):
        
        return self.axesObjList
    
    def getSubplots(self):
        
        raise ValueError, "Abstract method: This method should be defined"
        
    def getScreenDim(self, widthplot, heightplot):
        
        nrow, ncol = self.getSubplots()
        
        widthscreen = widthplot*ncol
        heightscreen = heightplot*nrow
        
        return widthscreen, heightscreen
    
    def getTimeLim(self, x, xmin, xmax):
        
        thisdatetime = datetime.datetime.utcfromtimestamp(numpy.min(x))
        thisdate = datetime.datetime.combine(thisdatetime.date(), datetime.time(0,0,0))
        
        ####################################################
        #If the x is out of xrange
        if xmax < (thisdatetime - thisdate).seconds/(60*60.):
            xmin = None
            xmax = None
        
        if xmin == None:
            td = thisdatetime - thisdate
            xmin = td.seconds/(60*60.)
            
        if xmax == None:
            xmax = xmin + self.timerange/(60*60.)
        
        mindt = thisdate + datetime.timedelta(hours=xmin) - datetime.timedelta(seconds=time.timezone)
        tmin = time.mktime(mindt.timetuple())
        
        maxdt = thisdate + datetime.timedelta(hours=xmax) - datetime.timedelta(seconds=time.timezone)
        tmax = time.mktime(maxdt.timetuple())
        
        self.timerange = tmax - tmin
        
        return tmin, tmax
    
    def init(self, id, nplots, wintitle):
    
        raise ValueError, "This method has been replaced with createFigure"
    
    def createFigure(self, id, wintitle, widthplot=None, heightplot=None, show=True):
        
        """
        Crea la figura de acuerdo al driver y parametros seleccionados seleccionados.
        Las dimensiones de la pantalla es calculada a partir de los atributos self.WIDTH
        y self.HEIGHT y el numero de subplots (nrow, ncol)
            
        Input:
            id    :    Los parametros necesarios son 
            wintitle    :    
        
        """
        
        if widthplot == None:
            widthplot = self.WIDTH
        
        if heightplot == None:
            heightplot = self.HEIGHT
        
        self.id = id
        
        self.wintitle = wintitle
        
        self.widthscreen, self.heightscreen = self.getScreenDim(widthplot, heightplot)
        
        self.fig = self.__driver.createFigure(id=self.id,
                                              wintitle=self.wintitle,
                                              width=self.widthscreen,
                                              height=self.heightscreen,
                                              show=show)
        
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
    
    def saveFigure(self, figpath, figfile, *args):
        
        filename = os.path.join(figpath, figfile)
        
        fullpath = os.path.split(filename)[0]
        
        if not os.path.exists(fullpath):
            subpath = os.path.split(fullpath)[0]
            
            if not os.path.exists(subpath):
                os.mkdir(subpath)
                
            os.mkdir(fullpath)
        
        self.__driver.saveFigure(self.fig, filename, *args)
    
    def sendByFTP(self, figfilename):
        ftpObj = Ftp()
        ftpObj.upload(figfilename)
        ftpObj.close()
    
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
    __missing = 1E30
    __firsttime = None
    
    __showprofile = False
    
    xmin = None
    xmax = None
    ymin = None
    ymax = None
    zmin = None
    zmax = None
    
    x_buffer = None
    z_buffer = None
    
    __MAXNUMX = 1000
    __MAXNUMY = 500
    
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
        
        self.__firsttime = True
        self.idlineList = []
        
        self.x_buffer = numpy.array([])
        self.z_buffer = numpy.array([])
        
    def setText(self, text):
        
        self.__driver.setAxesText(self.ax, text)
    
    def setXAxisAsTime(self):
        pass
    
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
                          ytick_visible
        """
        
        if self.__firsttime:
            
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

            self.idlineList.append(0)
            self.__firsttime = False
            return
                    
        self.__driver.pline(self.plot, x, y, xlabel=xlabel,
                                                    ylabel=ylabel,
                                                    title=title)

    def addpline(self, x, y, idline, **kwargs):
        lines = self.ax.lines
        
        if idline in self.idlineList:
            self.__driver.set_linedata(self.ax, x, y, idline)
        
        if  idline not in(self.idlineList):
            self.__driver.addpline(self.ax, x, y, **kwargs)
            self.idlineList.append(idline)

        return
        
    def pmultiline(self, x, y,
                   xmin=None, xmax=None,
                   ymin=None, ymax=None,
                   xlabel='', ylabel='',
                   title='',
                   **kwargs):
        
        if self.__firsttime:
            
            if xmin == None: xmin = numpy.nanmin(x)
            if xmax == None: xmax = numpy.nanmax(x)
            if ymin == None: ymin = numpy.nanmin(y)
            if ymax == None: ymax = numpy.nanmax(y)
    
            self.plot = self.__driver.createPmultiline(self.ax, x, y,
                                                  xmin, xmax,
                                                  ymin, ymax,
                                                  xlabel=xlabel,
                                                  ylabel=ylabel,
                                                  title=title,
                                                  **kwargs)
            self.__firsttime = False
            return
                    
        self.__driver.pmultiline(self.plot, x, y, xlabel=xlabel,
                                                    ylabel=ylabel,
                                                    title=title)
    
    def pmultilineyaxis(self, x, y,
                   xmin=None, xmax=None,
                   ymin=None, ymax=None,
                   xlabel='', ylabel='',
                   title='',
                   **kwargs):
        
        if self.__firsttime:
            
            if xmin == None: xmin = numpy.nanmin(x)
            if xmax == None: xmax = numpy.nanmax(x)
            if ymin == None: ymin = numpy.nanmin(y)
            if ymax == None: ymax = numpy.nanmax(y)
    
            self.plot = self.__driver.createPmultilineYAxis(self.ax, x, y,
                                                  xmin, xmax,
                                                  ymin, ymax,
                                                  xlabel=xlabel,
                                                  ylabel=ylabel,
                                                  title=title,
                                                  **kwargs)
            if self.xmin == None: self.xmin = xmin
            if self.xmax == None: self.xmax = xmax
            if self.ymin == None: self.ymin = ymin
            if self.ymax == None: self.ymax = ymax
            
            self.__firsttime = False
            return
                    
        self.__driver.pmultilineyaxis(self.plot, x, y, xlabel=xlabel,
                                                    ylabel=ylabel,
                                                    title=title)
            
    def pcolor(self, x, y, z,
               xmin=None, xmax=None,
               ymin=None, ymax=None,
               zmin=None, zmax=None,
               xlabel='', ylabel='',
               title='', rti = False, colormap='jet',
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
                          rti = True or False
        """
        
        if self.__firsttime:
            
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
                                                    colormap=colormap,
                                                    **kwargs)
            
            if self.xmin == None: self.xmin = xmin
            if self.xmax == None: self.xmax = xmax
            if self.ymin == None: self.ymin = ymin
            if self.ymax == None: self.ymax = ymax
            if self.zmin == None: self.zmin = zmin
            if self.zmax == None: self.zmax = zmax
            
            self.__firsttime = False
            return
        
        if rti:
            self.__driver.addpcolor(self.ax, x, y, z, self.zmin, self.zmax,
                                    xlabel=xlabel,
                                    ylabel=ylabel,
                                    title=title,
                                    colormap=colormap)
            return
        
        self.__driver.pcolor(self.plot, z,
                             xlabel=xlabel,
                             ylabel=ylabel,
                             title=title)
    
    def pcolorbuffer(self, x, y, z,
               xmin=None, xmax=None,
               ymin=None, ymax=None,
               zmin=None, zmax=None,
               xlabel='', ylabel='',
               title='', rti = False, colormap='jet',
               maxNumX = None, maxNumY = None,
               **kwargs):
    
        if maxNumX == None:
            maxNumX = self.__MAXNUMX
        
        if maxNumY == None:
            maxNumY = self.__MAXNUMY
        
        if self.__firsttime:
            self.z_buffer = z
            self.x_buffer = numpy.hstack((self.x_buffer, x))
            
            if xmin == None: xmin = numpy.nanmin(x)
            if xmax == None: xmax = numpy.nanmax(x)
            if ymin == None: ymin = numpy.nanmin(y)
            if ymax == None: ymax = numpy.nanmax(y)
            if zmin == None: zmin = numpy.nanmin(z)
            if zmax == None: zmax = numpy.nanmax(z)
            
            
            self.plot = self.__driver.createPcolor(self.ax, self.x_buffer, y, z,
                                                   xmin, xmax,
                                                   ymin, ymax,
                                                   zmin, zmax,
                                                   xlabel=xlabel,
                                                    ylabel=ylabel,
                                                    title=title,
                                                    colormap=colormap,
                                                    **kwargs)
            
            if self.xmin == None: self.xmin = xmin
            if self.xmax == None: self.xmax = xmax
            if self.ymin == None: self.ymin = ymin
            if self.ymax == None: self.ymax = ymax
            if self.zmin == None: self.zmin = zmin
            if self.zmax == None: self.zmax = zmax
            
            
            deltax = (xmax - xmin)/maxNumX
            deltay = (ymax - ymin)/maxNumY
            
            resolutionx = x[1]-x[0]
            resolutiony = y[1]-y[0]
            
            self.decimationx = numpy.ceil(deltax / resolutionx) 
            self.decimationy = numpy.ceil(deltay / resolutiony)
            
            self.__firsttime = False
            return
        
        if rti:
            if x[0]>self.x_buffer[-1]:
                gap = z.copy()
                gap[:] = self.__missing
                self.z_buffer = numpy.hstack((self.z_buffer, gap))
                self.z_buffer = numpy.ma.masked_inside(self.z_buffer,0.99*self.__missing,1.01*self.__missing)
                self.x_buffer = numpy.hstack((self.x_buffer, x))
            
            else:
                self.x_buffer = numpy.hstack((self.x_buffer, x[-1]))
            
            self.z_buffer = numpy.hstack((self.z_buffer, z))
            
#            self.z_buffer = numpy.ma.masked_inside(self.z_buffer,0.99*self.__missing,1.01*self.__missing)
            ydim = len(y)
            z_buffer = self.z_buffer.reshape(-1,ydim)
            
            x_buffer = self.x_buffer[::self.decimationx]
            y_buffer = y[::self.decimationy]    
            z_buffer = z_buffer[::self.decimationx, ::self.decimationy]
            #===================================================
            
            self.__driver.addpcolorbuffer(self.ax, x_buffer, y_buffer, z_buffer, self.zmin, self.zmax,
                                    xlabel=xlabel,
                                    ylabel=ylabel,
                                    title=title,
                                    colormap=colormap)
            return
        
        self.__driver.pcolor(self.plot, z,
                             xlabel=xlabel,
                             ylabel=ylabel,
                             title=title)
        