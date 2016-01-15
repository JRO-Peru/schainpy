import os
import numpy
import time, datetime
import mpldriver

from schainpy.model.proc.jroproc_base import Operation

def isTimeInHourRange(datatime, xmin, xmax):
    
    if xmin == None or xmax == None:
        return 1
    hour = datatime.hour + datatime.minute/60.0
    
    if xmin < (xmax % 24):
        
        if hour >= xmin and hour <= xmax:
            return 1
        else:
            return 0
    
    else:
        
        if hour >= xmin or hour <= (xmax % 24):
            return 1
        else:
            return 0
        
    return 0

def isRealtime(utcdatatime):
    
    utcnow = time.mktime(time.localtime())
    delta = abs(utcnow - utcdatatime) # abs
    if delta >= 30.:
        return False
    return True

class Figure(Operation):
    
    __driver = mpldriver
    fig = None
    
    id = None
    wintitle = None
    width = None
    height = None
    nplots = None
    timerange = None
    
    axesObjList = []
    
    WIDTH = 300
    HEIGHT = 200
    PREFIX = 'fig'
    
    xmin = None
    xmax = None
    
    counter_imagwr = 0
    
    figfile = None
    
    created = False
    
    def __init__(self):
         
        raise NotImplementedError
    
    def __del__(self):
        
        self.__driver.closeFigure()
    
    def getFilename(self, name, ext='.png'):
        
        path = '%s%03d' %(self.PREFIX, self.id)
        filename = '%s_%s%s' %(self.PREFIX, name, ext)
        return os.path.join(path, filename)
        
    def getAxesObjList(self):
        
        return self.axesObjList
    
    def getSubplots(self):
        
        raise NotImplementedError
        
    def getScreenDim(self, widthplot, heightplot):
        
        nrow, ncol = self.getSubplots()
        
        widthscreen = widthplot*ncol
        heightscreen = heightplot*nrow
        
        return widthscreen, heightscreen
    
    def getTimeLim(self, x, xmin=None, xmax=None, timerange=None):
        
#         if self.xmin != None and self.xmax != None:
#             if timerange == None:
#                 timerange = self.xmax - self.xmin
#             xmin = self.xmin + timerange
#             xmax = self.xmax + timerange
#             
#             return xmin, xmax
        
        if timerange == None and (xmin==None or xmax==None):
            timerange = 14400   #seconds
            
        if timerange != None:
            txmin = x[0] #- x[0] % min(timerange/10, 10*60)
        else:
            txmin = x[0] #- x[0] % 10*60
            
        thisdatetime = datetime.datetime.utcfromtimestamp(txmin)
        thisdate = datetime.datetime.combine(thisdatetime.date(), datetime.time(0,0,0))
        
        if timerange != None:
            xmin = (thisdatetime - thisdate).seconds/(60*60.)
            xmax = xmin + timerange/(60*60.)
        
        mindt = thisdate + datetime.timedelta(hours=xmin) - datetime.timedelta(seconds=time.timezone)
        xmin_sec = time.mktime(mindt.timetuple())
        
        maxdt = thisdate + datetime.timedelta(hours=xmax) - datetime.timedelta(seconds=time.timezone)
        xmax_sec = time.mktime(maxdt.timetuple())

        return xmin_sec, xmax_sec
    
    def init(self, id, nplots, wintitle):
    
        raise NotImplementedError, "This method has been replaced with createFigure"
    
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
        
#         if self.created:
#             self.__driver.closeFigure(self.fig)
        
        if not self.created:
            self.fig = self.__driver.createFigure(id=self.id,
                                                  wintitle=self.wintitle,
                                                  width=self.widthscreen,
                                                  height=self.heightscreen,
                                                  show=show)
        else:
            self.__driver.clearFigure(self.fig)
        
        self.axesObjList = []
        self.counter_imagwr = 0

        self.created = True
    
    def setDriver(self, driver=mpldriver):
        
        self.__driver = driver
        
    def setTitle(self, title):
        
        self.__driver.setTitle(self.fig, title)
    
    def setWinTitle(self, title):
        
        self.__driver.setWinTitle(self.fig, title=title)
    
    def setTextFromAxes(self, text):
        
        raise NotImplementedError, "This method has been replaced with Axes.setText"
    
    def makeAxes(self, nrow, ncol, xpos, ypos, colspan, rowspan):
        
        raise NotImplementedError, "This method has been replaced with Axes.addAxes"
        
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
    
    def save(self, figpath, figfile=None, save=True, ftp=False, wr_period=1, thisDatetime=None, update_figfile=True):
        
        self.counter_imagwr += 1
        if self.counter_imagwr < wr_period:
            return
        
        self.counter_imagwr = 0
        
        if save:
        
            if not figfile:
                
                if not thisDatetime:
                    raise ValueError, "Saving figure: figfile or thisDatetime should be defined"
                    return
                
                str_datetime = thisDatetime.strftime("%Y%m%d_%H%M%S")
                figfile = self.getFilename(name = str_datetime)
            
            if self.figfile == None:
                self.figfile = figfile
                
            if update_figfile:
                self.figfile = figfile
            
            # store png plot to local folder            
            self.saveFigure(figpath, self.figfile)
            
            
        if not ftp:
            return
        
        if not thisDatetime:
            return
        
        # store png plot to FTP server according to RT-Web format 
        ftp_filename = self.getNameToFtp(thisDatetime, self.FTP_WEI, self.EXP_CODE, self.SUB_EXP_CODE, self.PLOT_CODE, self.PLOT_POS)
#         ftp_filename = os.path.join(figpath, name)
        self.saveFigure(figpath, ftp_filename)  
    
    def getNameToFtp(self, thisDatetime, FTP_WEI, EXP_CODE, SUB_EXP_CODE, PLOT_CODE, PLOT_POS):
        YEAR_STR = '%4.4d'%thisDatetime.timetuple().tm_year  
        DOY_STR = '%3.3d'%thisDatetime.timetuple().tm_yday
        FTP_WEI = '%2.2d'%FTP_WEI
        EXP_CODE = '%3.3d'%EXP_CODE
        SUB_EXP_CODE = '%2.2d'%SUB_EXP_CODE
        PLOT_CODE = '%2.2d'%PLOT_CODE
        PLOT_POS = '%2.2d'%PLOT_POS
        name = YEAR_STR + DOY_STR + FTP_WEI + EXP_CODE + SUB_EXP_CODE + PLOT_CODE + PLOT_POS
        return name
    
    def draw(self):
        
        self.__driver.draw(self.fig)
    
    def run(self):
        
        raise NotImplementedError
    
    def close(self, show=False):
        
        self.__driver.closeFigure(show=show, fig=self.fig)
        
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
    
    decimationx = None
    decimationy = None
    
    __MAXNUMX = 300
    __MAXNUMY = 150
    
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

#         self.__driver.pause()
        
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
        
#         self.__driver.pause()
        
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
        
#         self.__driver.pause()
        
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
    
#         self.__driver.pause()
        
    def pcolorbuffer(self, x, y, z,
               xmin=None, xmax=None,
               ymin=None, ymax=None,
               zmin=None, zmax=None,
               xlabel='', ylabel='',
               title='', rti = True, colormap='jet',
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
            
            self.__firsttime = False
            return
            
        self.x_buffer = numpy.hstack((self.x_buffer[:-1], x[0], x[-1]))
        self.z_buffer = numpy.hstack((self.z_buffer, z))
        
        if self.decimationx == None:
            deltax = float(self.xmax - self.xmin)/maxNumX
            deltay = float(self.ymax - self.ymin)/maxNumY
            
            resolutionx = self.x_buffer[2]-self.x_buffer[0]
            resolutiony = y[1]-y[0]
            
            self.decimationx = numpy.ceil(deltax / resolutionx) 
            self.decimationy = numpy.ceil(deltay / resolutiony)
        
        z_buffer = self.z_buffer.reshape(-1,len(y))
        
        x_buffer = self.x_buffer[::self.decimationx]
        y_buffer = y[::self.decimationy]    
        z_buffer = z_buffer[::self.decimationx, ::self.decimationy]
        #===================================================
        
        x_buffer, y_buffer, z_buffer = self.__fillGaps(x_buffer, y_buffer, z_buffer)
        
        self.__driver.addpcolorbuffer(self.ax, x_buffer, y_buffer, z_buffer, self.zmin, self.zmax,
                                xlabel=xlabel,
                                ylabel=ylabel,
                                title=title,
                                colormap=colormap)
        
#         self.__driver.pause()
        
    def polar(self, x, y,
               title='', xlabel='',ylabel='',**kwargs):
        
        if self.__firsttime:
            self.plot = self.__driver.createPolar(self.ax, x, y, title = title, xlabel = xlabel, ylabel = ylabel)
            self.__firsttime = False
            self.x_buffer = x
            self.y_buffer = y
            return
        
        self.x_buffer = numpy.hstack((self.x_buffer,x))
        self.y_buffer = numpy.hstack((self.y_buffer,y))
        self.__driver.polar(self.plot, self.x_buffer, self.y_buffer, xlabel=xlabel,
                                            ylabel=ylabel,
                                            title=title)
    
#         self.__driver.pause()
        
    def __fillGaps(self, x_buffer, y_buffer, z_buffer):
        
        if x_buffer.shape[0] < 2:
            return x_buffer, y_buffer, z_buffer
        
        deltas = x_buffer[1:] - x_buffer[0:-1]
        x_median = numpy.median(deltas)
        
        index = numpy.where(deltas > 5*x_median)
        
        if len(index[0]) != 0:
            z_buffer[index[0],::] = self.__missing
            z_buffer = numpy.ma.masked_inside(z_buffer,0.99*self.__missing,1.01*self.__missing)

        return x_buffer, y_buffer, z_buffer
        
        
        
        