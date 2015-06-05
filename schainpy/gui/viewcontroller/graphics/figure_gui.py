import os
import numpy
import time, datetime
import mpldriver_gui
from customftp import *
import Queue
import threading

class FTP_Thread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.exitFlag = 0
        self.queueLock = threading.Lock()
        self.workQueue = Queue.Queue()
        
    def run(self):
        self.send_data()

    def fin(self):
        self.exitFlag = 1

    def put_data(self, data):
        # Fill the queue
        self.queueLock.acquire()
        self.workQueue.put(data)
        self.queueLock.release()         
            
    def send_data(self):
        while not self.exitFlag:
            if self.workQueue.qsize():
                
                data = self.workQueue.get(True)
                
                try:
                    ftpObj = Ftp(host=data['server'], 
                                 username=data['username'], 
                                 passw=data['password'], 
                                 remotefolder=data['folder'])
                    
                    ftpObj.upload(data['figfilename'])
                    ftpObj.close()
                except:
                    print ValueError, 'Error FTP'
                    print "don't worry still running the program"


class Figure():
    
    __driver = mpldriver_gui
    __isConfigThread = False
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
    
    FTP_WEI = None #(WW)
    EXP_CODE = None #(EXP)
    SUB_EXP_CODE = None #(SS)
    PLOT_CODE = None #(TT)
    PLOT_POS = None #(NN)
    
    
    
    def __init__(self):
         
        raise ValueError, "This method is not implemented"
    
    def getSubplots(self):
        
        raise ValueError, "Abstract method: This method should be defined"
    
    def getAxesObjList(self):
        
        return self.axesObjList
    
    def getScreenDim(self, widthplot, heightplot):
        
        nrow, ncol = self.getSubplots()
        widthscreen = widthplot*ncol
        heightscreen = heightplot*nrow
        
        return widthscreen, heightscreen

    def getFilename(self, name, ext='.png'):
        path = '%s%03d' %(self.PREFIX, self.id)
        filename = '%s_%s%s' %(self.PREFIX, name, ext)
        return os.path.join(path, filename)
    
    def createFigure(self, id, wintitle, widthplot=None, heightplot=None):
        
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
                                              height=self.heightscreen)
        
        self.axesObjList = []
        
        return self.fig
    
    def clearAxes(self):
        self.axesObjList = []
    
    def addAxes(self, *args):
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
    
    def getTimeLim(self, x, xmin, xmax):
        
        if self.timerange != None:
            txmin = x[0] - x[0]%self.timerange
        else:
            txmin = numpy.min(x)
        
        thisdatetime = datetime.datetime.utcfromtimestamp(txmin)
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
    
    def sendByFTP(self, figfilename, server, folder, username, password):
        ftpObj = Ftp(host=server, username=username, passw=password, remotefolder=folder)
        ftpObj.upload(figfilename)
        ftpObj.close()
    
    def sendByFTP_Thread(self, figfilename, server, folder, username, password):
        data = {'figfilename':figfilename,'server':server,'folder':folder,'username':username,'password':password}

        if not(self.__isConfigThread):
            
            self.thread = FTP_Thread()
            self.thread.start()
            self.__isConfigThread = True
        
        self.thread.put_data(data)

    
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
    
    axesList = property(getAxesObjList)

class Axes:
    
    __driver = mpldriver_gui
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
    
    __MAXNUMX = 1000.
    __MAXNUMY = 500.
    
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
    
    def addpline(self, x, y, idline, **kwargs):
        lines = self.ax.lines
        
        if idline in self.idlineList:
            self.__driver.set_linedata(self.ax, x, y, idline)
        
        if  idline not in(self.idlineList):
            self.__driver.addpline(self.ax, x, y, **kwargs)
            self.idlineList.append(idline)

        return
    
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
            
        self.x_buffer = numpy.hstack((self.x_buffer, x[-1]))
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
    def __fillGaps(self, x_buffer, y_buffer, z_buffer):
        
        deltas = x_buffer[1:] - x_buffer[0:-1]
        x_median = numpy.median(deltas)
        
        index = numpy.where(deltas >= 2*x_median)
        
        if len(index[0]) != 0:
            z_buffer[index[0],::] = self.__missing
            z_buffer = numpy.ma.masked_inside(z_buffer,0.99*self.__missing,1.01*self.__missing)

        return x_buffer, y_buffer, z_buffer
    
    