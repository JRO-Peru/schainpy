'''
Created on Jul 9, 2014

@author: roj-idl71
'''
import os
import datetime
import numpy

from figure import Figure
from plotting_codes import *

class Scope(Figure):
    
    isConfig = None
    
    def __init__(self, **kwargs):
        Figure.__init__(self, **kwargs)
        self.isConfig = False
        self.WIDTH = 300
        self.HEIGHT = 200
        self.counter_imagwr = 0
    
    def getSubplots(self):
        
        nrow = self.nplots
        ncol = 3
        return nrow, ncol
    
    def setup(self, id, nplots, wintitle, show):
        
        self.nplots = nplots
        
        self.createFigure(id=id, 
                          wintitle=wintitle, 
                          show=show)
        
        nrow,ncol = self.getSubplots()
        colspan = 3
        rowspan = 1
        
        for i in range(nplots):
            self.addAxes(nrow, ncol, i, 0, colspan, rowspan)
    
    def plot_iq(self, x, y, id, channelIndexList, thisDatetime, wintitle, show, xmin, xmax, ymin, ymax):
        yreal = y[channelIndexList,:].real
        yimag = y[channelIndexList,:].imag
        
        title = wintitle + " Scope: %s" %(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
        xlabel = "Range (Km)"
        ylabel = "Intensity - IQ"
        
        if not self.isConfig:
            nplots = len(channelIndexList)
            
            self.setup(id=id,
                       nplots=nplots,
                       wintitle='',
                       show=show)
            
            if xmin == None: xmin = numpy.nanmin(x)
            if xmax == None: xmax = numpy.nanmax(x)
            if ymin == None: ymin = min(numpy.nanmin(yreal),numpy.nanmin(yimag))
            if ymax == None: ymax = max(numpy.nanmax(yreal),numpy.nanmax(yimag))
                
            self.isConfig = True
        
        self.setWinTitle(title)
        
        for i in range(len(self.axesList)):
            title = "Channel %d" %(i)
            axes = self.axesList[i]

            axes.pline(x, yreal[i,:],
                        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,
                        xlabel=xlabel, ylabel=ylabel, title=title)

            axes.addpline(x, yimag[i,:], idline=1, color="red", linestyle="solid", lw=2)
            
    def plot_power(self, x, y, id, channelIndexList, thisDatetime, wintitle, show, xmin, xmax, ymin, ymax):
        y = y[channelIndexList,:] * numpy.conjugate(y[channelIndexList,:])
        yreal = y.real
        
        title = wintitle + " Scope: %s" %(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
        xlabel = "Range (Km)"
        ylabel = "Intensity"
        
        if not self.isConfig:
            nplots = len(channelIndexList)
            
            self.setup(id=id,
                       nplots=nplots,
                       wintitle='',
                       show=show)
            
            if xmin == None: xmin = numpy.nanmin(x)
            if xmax == None: xmax = numpy.nanmax(x)
            if ymin == None: ymin = numpy.nanmin(yreal)
            if ymax == None: ymax = numpy.nanmax(yreal)
                
            self.isConfig = True
        
        self.setWinTitle(title)
        
        for i in range(len(self.axesList)):
            title = "Channel %d" %(i)
            axes = self.axesList[i]
            ychannel = yreal[i,:]
            axes.pline(x, ychannel,
                        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,
                        xlabel=xlabel, ylabel=ylabel, title=title)

    
    def run(self, dataOut, id, wintitle="", channelList=None,
            xmin=None, xmax=None, ymin=None, ymax=None, save=False,
            figpath='./', figfile=None, show=True, wr_period=1,
            ftp=False, server=None, folder=None, username=None, password=None, type='power', **kwargs):
        
        """
        
        Input:
            dataOut         :
            id        :
            wintitle        :
            channelList     :
            xmin            :    None,
            xmax            :    None,
            ymin            :    None,
            ymax            :    None,
        """
        
        if channelList == None:
            channelIndexList = dataOut.channelIndexList
        else:
            channelIndexList = []
            for channel in channelList:
                if channel not in dataOut.channelList:
                    raise ValueError, "Channel %d is not in dataOut.channelList"
                channelIndexList.append(dataOut.channelList.index(channel))
        
        thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.getTimeRange()[0])
        
        if dataOut.flagDataAsBlock:
            
            for i in range(dataOut.nProfiles):
                
                wintitle1 = wintitle + " [Profile = %d] " %i
                
                if type == "power":
                    self.plot_power(dataOut.heightList, 
                                    dataOut.data[:,i,:],
                                    id, 
                                    channelIndexList, 
                                    thisDatetime,
                                    wintitle1,
                                    show,
                                    xmin,
                                    xmax,
                                    ymin,
                                    ymax)
                
                if type == "iq":
                    self.plot_iq(dataOut.heightList, 
                                 dataOut.data[:,i,:],
                                 id, 
                                 channelIndexList, 
                                 thisDatetime,
                                 wintitle1,
                                 show,
                                 xmin,
                                 xmax,
                                 ymin,
                                 ymax)
                    
                self.draw()
                
                str_datetime = thisDatetime.strftime("%Y%m%d_%H%M%S")
                figfile = self.getFilename(name = str_datetime) + "_" + str(i)
        
                self.save(figpath=figpath,
                          figfile=figfile,
                          save=save,
                          ftp=ftp,
                          wr_period=wr_period,
                          thisDatetime=thisDatetime)
        
        else:
            wintitle += " [Profile = %d] " %dataOut.profileIndex
            
            if type == "power":
                self.plot_power(dataOut.heightList, 
                                dataOut.data,
                                id, 
                                channelIndexList, 
                                thisDatetime,
                                wintitle,
                                show,
                                xmin,
                                xmax,
                                ymin,
                                ymax)
            
            if type == "iq":
                self.plot_iq(dataOut.heightList, 
                             dataOut.data,
                             id, 
                             channelIndexList, 
                             thisDatetime,
                             wintitle,
                             show,
                             xmin,
                             xmax,
                             ymin,
                             ymax)
        
        self.draw()
        
        str_datetime = thisDatetime.strftime("%Y%m%d_%H%M%S") + "_" + str(dataOut.profileIndex)
        figfile = self.getFilename(name = str_datetime) 
                
        self.save(figpath=figpath,
                  figfile=figfile,
                  save=save,
                  ftp=ftp,
                  wr_period=wr_period,
                  thisDatetime=thisDatetime)


class VoltACFPLot(Figure):

    isConfig    = None
    __nsubplots = None
    PREFIX      = 'voltacf'

    def __init__(self, **kwargs):
	Figure.__init__(self,**kwargs)
	self.isConfig      = False
	self.__nsubplots   = 1
	self.PLOT_CODE     = VOLT_ACF_CODE
	self.WIDTH         = 900
	self.HEIGHT        = 700
	self.counter_imagwr= 0
	self.FTP_WEI       = None
	self.EXP_CODE      = None
	self.SUB_EXP_CODE  = None
	self.PLOT_POS      = None

    def getSubplots(self) :
	ncol = 1
	nrow = 1
   	return nrow, ncol

    def setup(self,id, nplots,wintitle,show):
	self.nplots = nplots
	ncolspan    = 1
	colspan     = 1
	self.createFigure(id=id,
			  wintitle   = wintitle,
			  widthplot  = self.WIDTH,
			  heightplot = self.HEIGHT,
			  show       = show)
	nrow, ncol  = self.getSubplots()
	counter = 0
	for y in range(nrow):
	   for x in range(ncol):
		self.addAxes(nrow, ncol*ncolspan,y, x*ncolspan, colspan, 1) 

    def run(self,dataOut, id, wintitle="",channelList = None , channel =None, nSamples = None,
	    nSampleList= None, resolutionFactor=None, xmin= None, xmax = None, ymin=None, ymax=None,
	    save= False, figpath='./', figfile= None,show= True, ftp= False, wr_period=1, server= None,
	    folder= None, username =None, password= None, ftp_wei=0 , exp_code=0,sub_exp_code=0,plot_pos=0,
	    xaxis="time"):
	
	channel0  = channel
	nSamples  = nSamples
	resFactor = resolutionFactor

	if nSamples == None:
	   nSamples  = 20
	
	if resFactor == None:
	   resFactor = 5

	if channel0 == None:
	   channel0 = 0
	else:
      	  if channel0 not in dataOut.channelList:
                raise ValueError, "Channel %d is not in %s dataOut.channelList"%(channel0, dataOut.channelList)

	if channelList == None: 
	   channelIndexList = dataOut.channelIndexList
	   channelList      = dataOut.channelList

	else:
            channelIndexList = []
            for channel in channelList:
                if channel not in dataOut.channelList:
                    raise ValueError, "Channel %d is not in dataOut.channelList"
                channelIndexList.append(dataOut.channelList.index(channel))


        #factor       =  dataOut.normFactor
        y            =  dataOut.getHeiRange()
	#print y, dataOut.heightList[0]
	#print "pause"
	#import time
	#time.sleep(10)
        deltaHeight  =  dataOut.heightList[1]-dataOut.heightList[0]
        z            =  dataOut.data

	shape     =  dataOut.data.shape
	hei_index =  numpy.arange(shape[2]) 
	hei_plot  =  numpy.arange(nSamples)*resFactor

        if nSampleList    is not  None:
            for nsample in nSampleList:
                if nsample not in dataOut.heightList/deltaHeight:
		    print "Lista available : %s "%(dataOut.heightList/deltaHeight)
                    raise ValueError, "nsample %d is not in %s dataOut.heightList"%(nsample,dataOut.heightList)

        if nSampleList is not  None:
            hei_plot = numpy.array(nSampleList)*resFactor

        if hei_plot[-1] >= hei_index[-1]:
            print ("La cantidad de puntos en altura es %d y la resolucion es %f Km"%(hei_plot.shape[0],deltaHeight*resFactor ))
            raise ValueError, "resFactor %d multiplicado por el valor de %d nSamples  es mayor a %d cantidad total de puntos"%(resFactor,nSamples,hei_index[-1])

	#escalamiento  -1 a 1 a resolucion (factor de resolucion en altura)* deltaHeight
        #min = numpy.min(z[0,:,0])
        #max =numpy.max(z[0,:,0])
        for i in range(shape[0]):
            for j in range(shape[2]):
		min = numpy.min(z[i,:,j])
		max = numpy.max(z[i,:,j])
                z[i,:,j]= (((z[i,:,j]-min)/(max-min))*deltaHeight*resFactor + j*deltaHeight+dataOut.heightList[0])
	
	
	if xaxis == "time":
           x = dataOut.getAcfRange()*1000
           zdB = z[channel0,:,hei_plot]
           xlabel = "Time (ms)"
           ylabel = "VOLT_ACF"


        thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.getTimeRange()[0])
        title = wintitle + "VOLT ACF Plot Ch %s %s" %(channel0,thisDatetime.strftime("%d-%b-%Y"))

        if not self.isConfig:

            nplots = 1

            self.setup(id=id,
                       nplots=nplots,
                       wintitle=wintitle,
                       show=show)

            if xmin == None: xmin = numpy.nanmin(x)#*0.9
            if xmax == None: xmax = numpy.nanmax(x)#*1.1
            if ymin == None: ymin = numpy.nanmin(zdB)
            if ymax == None: ymax = numpy.nanmax(zdB)

            print ("El parametro resFactor es %d y la resolucion en altura es %f"%(resFactor,deltaHeight ))
            print ("La cantidad de puntos en altura es %d y la nueva resolucion es %f Km"%(hei_plot.shape[0],deltaHeight*resFactor ))
            print ("La altura maxima es %d Km"%(hei_plot[-1]*deltaHeight ))

	    self.FTP_WEI = ftp_wei
            self.EXP_CODE = exp_code
            self.SUB_EXP_CODE = sub_exp_code
            self.PLOT_POS = plot_pos

            self.isConfig = True

        self.setWinTitle(title)

	title = "VOLT ACF Plot: %s" %(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
        axes = self.axesList[0]

        legendlabels = ["Range = %dKm" %y[i] for i in hei_plot]

        axes.pmultilineyaxis( x, zdB,
        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,
        xlabel=xlabel, ylabel=ylabel, title=title, legendlabels=legendlabels,
        ytick_visible=True, nxticks=5,
        grid='x')

        self.draw()

        if figfile == None:
            str_datetime = thisDatetime.strftime("%Y%m%d_%H%M%S")
            name = str_datetime
            if ((dataOut.azimuth!=None) and (dataOut.zenith!=None)):
                name = name + '_az' + '_%2.2f'%(dataOut.azimuth) + '_zn' + '_%2.2f'%(dataOut.zenith)
            figfile = self.getFilename(name)

        self.save(figpath=figpath,
                  figfile=figfile,
                  save=save,
                  ftp=ftp,
                  wr_period=wr_period,
                  thisDatetime=thisDatetime)


























