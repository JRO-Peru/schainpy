'''
Created on Feb 7, 2012

@author $Author$
@version $Id$
'''

import os, sys
import numpy
import plplot

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from Graphics.BaseGraph import *
from Model.Spectra import Spectra

class Spectrum():
    
    def __init__(self, Spectra):
        
        """
        
        Inputs:
            
            type:   "power" ->> Potencia
                    "iq"    ->> Real + Imaginario
        """
        
        self.__isPlotConfig = False
        
        self.__isPlotIni = False
        
        self.__xrange = None
        
        self.__yrange = None
        
        self.nGraphs = 0
        
        self.graphObjList = [] 
           
        self.m_Spectra = Spectra
        
    
    def __addGraph(self, subpage, title="", xlabel="", ylabel="", showColorbar=False, showPowerProfile=True, XAxisAsTime=False):
        
        graphObj = ColorPlot()
        graphObj.setup(subpage,
                       title,
                       xlabel,
                       ylabel,
                       showColorbar=showColorbar,
                       showPowerProfile=showPowerProfile,
                       XAxisAsTime=XAxisAsTime)
                
        self.graphObjList.append(graphObj)

    
    def setup(self, titleList=None, xlabelList=None, ylabelList=None, showColorbar=False, showPowerProfile=True, XAxisAsTime=False):
        
        nChan = int(self.m_Spectra.m_SystemHeader.numChannels)
        
        myTitle = ""
        myXlabel = ""
        myYlabel = ""
        
        for i in range(nChan):
            if titleList != None:
                myTitle = titleList[i]
                myXlabel = xlabelList[i]
                myYlabel = ylabelList[i]
                
            self.__addGraph(i+1,
                            title=myTitle,
                            xlabel=myXlabel,
                            ylabel=myYlabel,
                            showColorbar=showColorbar,
                            showPowerProfile=showPowerProfile,
                            XAxisAsTime=XAxisAsTime)
        
        self.nGraphs = nChan
        self.__isPlotConfig = True

    def iniPlot(self):
        
        nx = int(numpy.sqrt(self.nGraphs)+1)
        #ny = int(self.nGraphs/nx)
        
        plplot.plsetopt("geometry", "%dx%d" %(400*nx, 300*nx))
        plplot.plsdev("xcairo")
        plplot.plscolbg(255,255,255)
        plplot.plscol0(1,0,0,0)
        plplot.plinit()
        plplot.plspause(False)
        plplot.pladv(0)
        plplot.plssub(nx, nx)
        
        self.__isPlotIni = True     
    
    def plotData(self, xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None, titleList=None, xlabelList=None, ylabelList=None, showColorbar=False, showPowerProfile=True, XAxisAsTime=False):
        
        if not(self.__isPlotConfig):
            self.setup(titleList,
                       xlabelList,
                       ylabelList,
                       showColorbar,
                       showPowerProfile,
                       XAxisAsTime)
        
        if not(self.__isPlotIni):
            self.iniPlot()
        
        data = numpy.log10(self.m_Spectra.data_spc)
        
        nX, nY, nChan = numpy.shape(data)
        
        x = numpy.arange(nX)        
        y = self.m_Spectra.heights
        
        if xmin == None: xmin = x[0]
        if xmax == None: xmax = x[-1]
        if ymin == None: ymin = y[0]
        if ymax == None: ymax = y[-1]
        if zmin == None: zmin = numpy.nanmin(abs(data))
        if zmax == None: zmax = numpy.nanmax(abs(data))
        
        plplot.plbop()
        for i in range(self.nGraphs):
            self.graphObjList[i].iniSubpage()
            self.graphObjList[i].plotData(data[:,:,i],
                                          x,
                                          y,
                                          xmin=xmin,
                                          xmax=xmax,
                                          ymin=ymin,
                                          ymax=ymax,
                                          zmin=zmin,
                                          zmax=zmax)
            
        
        plplot.plflush()
        plplot.pleop()
    
    def end(self):
        plplot.plend()
 

if __name__ == '__main__':
    pass