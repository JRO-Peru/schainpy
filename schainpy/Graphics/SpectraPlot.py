'''
Created on Feb 7, 2012

@author $Author$
@version $Id$
'''

import os, sys
import numpy
import datetime
import plplot

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from Graphics.BaseGraph import *
from Model.Spectra import Spectra

class Spectrum():
    
    def __init__(self, Spectra, index=0):
        
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
        
        self.indexPlot = index
        
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
        channels = range(nChan)
        
        myXlabel = "Radial Velocity (m/s)"
        myYlabel = "Range (km)"
        
        for i in channels:
            if titleList != None:
                myTitle = titleList[i]
                myXlabel = xlabelList[i]
                myYlabel = ylabelList[i]
            
#            if self.m_Spectra.m_NoiseObj != None:
#                noise = '%4.2fdB' %(self.m_Spectra.m_NoiseObj[i])
#            else:
            noise = '--'
            
            myTitle = "Channel: %d - Noise: %s" %(i, noise)
                
            self.__addGraph(i+1,
                            title=myTitle,
                            xlabel=myXlabel,
                            ylabel=myYlabel,
                            showColorbar=showColorbar,
                            showPowerProfile=showPowerProfile,
                            XAxisAsTime=XAxisAsTime)
        
        self.nGraphs = nChan
        self.__isPlotConfig = True

    def iniPlot(self, winTitle=""):
        
        nx = int(numpy.sqrt(self.nGraphs)+1)
        #ny = int(self.nGraphs/nx)
        
        plplot.plsstrm(self.indexPlot)
        plplot.plparseopts([winTitle], plplot.PL_PARSE_FULL)
        plplot.plsetopt("geometry", "%dx%d" %(300*nx, 240*nx))
        plplot.plsdev("xwin")
        plplot.plscolbg(255,255,255)
        plplot.plscol0(1,0,0,0)
        plplot.plinit()
        plplot.plspause(False)
        plplot.pladv(0)
        plplot.plssub(nx, nx)
        
        self.__nx = nx
        self.__ny = nx
        self.__isPlotIni = True
         
    
    def plotData(self, xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None, titleList=None, xlabelList=None, ylabelList=None, showColorbar=False, showPowerProfile=True, XAxisAsTime=False, winTitle="Spectra"):
        
        if not(self.__isPlotConfig):
            self.setup(titleList,
                       xlabelList,
                       ylabelList,
                       showColorbar,
                       showPowerProfile,
                       XAxisAsTime)
        
        if not(self.__isPlotIni):
            self.iniPlot(winTitle)
        
        plplot.plsstrm(self.indexPlot)
        
        data = 10.*numpy.log10(self.m_Spectra.data_spc)
        
        #data.shape = Channels x Heights x Profiles
#        data = numpy.transpose( data, (0,2,1) )
        #data.shape = Channels x Profiles x Heights

        nChan, nX, nY = numpy.shape(data)
        
        x = numpy.arange(nX)        
        y = self.m_Spectra.heightList
        
        thisDatetime = datetime.datetime.fromtimestamp(self.m_Spectra.m_BasicHeader.utc)
        txtDate = "Self Spectra - Date: %s" %(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
        
        if xmin == None: xmin = x[0]
        if xmax == None: xmax = x[-1]
        if ymin == None: ymin = y[0]
        if ymax == None: ymax = y[-1]
        if zmin == None: zmin = numpy.nanmin(abs(data))
        if zmax == None: zmax = numpy.nanmax(abs(data))
        
        plplot.plbop()
        
        plplot.plssub(self.__nx, self.__ny)
        for i in range(self.nGraphs):
            self.graphObjList[i].iniSubpage()
            self.graphObjList[i].plotData(data[i,:,:],
                                          x,
                                          y,
                                          xmin=xmin,
                                          xmax=xmax,
                                          ymin=ymin,
                                          ymax=ymax,
                                          zmin=zmin,
                                          zmax=zmax)
        
        plplot.plssub(1,0)
        plplot.pladv(0)
        plplot.plvpor(0., 1., 0., 1.)
        plplot.plmtex("t",-1., 0.5, 0.5, txtDate)
        plplot.plflush()
        plplot.pleop()
    
    def end(self):
        plplot.plend()
 

if __name__ == '__main__':
    pass