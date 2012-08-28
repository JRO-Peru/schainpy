'''
Created on Feb 7, 2012

@author $Author$
@version $Id$
'''

import numpy
import os
import sys
import plplot
import datetime

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from Graphics.BaseGraph import *
from Model.Spectra import Spectra

class Spectrum:
    colorplotObj = None
    
    def __init__(self,Spectra, index):
        self.__isPlotConfig = False
        self.__isPlotIni = False
        self.__xrange = None
        self.__yrange = None
        self.nGraphs = 0
        self.indexPlot = index
        self.spectraObj = Spectra
    
    def setup(self,indexPlot,nsubplot,winTitle='',colormap="br_green",showColorbar=False,showPowerProfile=False,XAxisAsTime=False):
        self.colorplotObj = SpectraPlot(indexPlot,nsubplot,winTitle,colormap,showColorbar,showPowerProfile,XAxisAsTime)
    
    def initPlot(self,xmin,xmax,ymin,ymax,zmin,zmax,titleList,xlabelList,ylabelList):
        nsubplot = self.spectraObj.nChannels
        
        for index in range(nsubplot):
            title = titleList[index]
            xlabel = xlabelList[index]
            ylabel = ylabelList[index]
            subplot = index
            self.colorplotObj.setup(subplot+1,xmin,xmax,ymin,ymax,zmin,zmax,title,xlabel,ylabel)

    
    def plotData(self,
                 xmin=None,
                 xmax=None,
                 ymin=None,
                 ymax=None,
                 zmin=None,
                 zmax=None,
                 titleList=None,
                 xlabelList=None,
                 ylabelList=None,
                 winTitle='',
                 colormap = "br_green",
                 showColorbar = True,
                 showPowerProfile = True,
                 XAxisAsTime = False):
        
        databuffer = 10.*numpy.log10(self.spectraObj.data_spc)
        noise = 10.*numpy.log10(self.spectraObj.noise)
        
        nsubplot = self.spectraObj.nChannels
        nsubplot, nX, nY = numpy.shape(databuffer)
        
        x = numpy.arange(nX)        
        y = self.spectraObj.heightList
        
        indexPlot = self.indexPlot
        
        if not(self.__isPlotConfig):
            self.setup(indexPlot,nsubplot,winTitle,colormap,showColorbar,showPowerProfile,XAxisAsTime)
            self.__isPlotConfig = True
        
        if not(self.__isPlotIni):
            if titleList == None:
                titleList = []
                for i in range(nsubplot):
                    titleList.append("Channel: %d - Noise: %.2f" %(i, noise[i]))

            if xlabelList == None:
                xlabelList = []
                for i in range(nsubplot):
                    xlabelList.append("")

            if ylabelList == None:
                ylabelList = []
                for i in range(nsubplot):
                    ylabelList.append("Range (Km)")

            if xmin == None: xmin = x[0]
            if xmax == None: xmax = x[-1] 
            if ymin == None: ymin = y[0]
            if ymax == None: ymax = y[-1]                
            if zmin == None: zmin = 0
            if zmax == None: zmax = 120
            
            self.initPlot(xmin,xmax,ymin,ymax,zmin,zmax,titleList,xlabelList,ylabelList)
            self.__isPlotIni = True
        
        self.colorplotObj.setFigure(indexPlot)
        
        thisDatetime = datetime.datetime.fromtimestamp(self.spectraObj.m_BasicHeader.utc)
        pltitle = "Self Spectra - Date: %s" %(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
        
        self.colorplotObj.printTitle(pltitle) #setPlTitle(pltitle)
        
        for index in range(nsubplot):
            data = databuffer[index,:,:]
            subtitle = "Channel: %d - Noise: %.2f" %(index, noise[index])
            self.colorplotObj.plot(index+1,x,y,data,subtitle)
        
        
        
        self.colorplotObj.refresh()


