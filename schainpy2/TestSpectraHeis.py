'''
Created on Jul 31, 2012

@author $Author$
@version $Id$
'''

import os, sys
import time, datetime
#import pylab as pl

from Data.JROData import Voltage
from IO.VoltageIO import *

from Data.JROData import SpectraHeis
from IO.SpectraIO import *

from Processing.VoltageProcessor import *
from Processing.SpectraProcessor import *

from  Graphics.BaseGraph_mpl import LinearPlot

class TestHeis():
    i=None
    def __init__(self):
        self.setValues()
        self.createObjects()
        self.testSChain()
        self.i=0
        
    def setValues( self ):
        
        self.path="C:\data2"        
        self.startDate = datetime.date(2012,4,1)
        self.endDate = datetime.date(2012,6,30)
        
        self.startTime = datetime.time(0,0,0)
        self.endTime = datetime.time(23,0,0)
        #self.N = 4
        #self.npts = 8
    
    def createObjects( self ):
        
        self.readerObj = VoltageReader()
        self.specProcObj = SpectraHeisProcessor()

        self.voltObj1 = self.readerObj.setup(
                                   path = self.path,
                                   startDate = self.startDate,
                                   endDate = self.endDate,
                                   startTime = self.startTime,
                                   endTime = self.endTime,
                                   expLabel = '',
                                   online = 0) 
       
        if not(self.voltObj1):
            sys.exit(0)   
            
        print "voltaje o alturas:   %03d"%(self.voltObj1.nHeights)
        #print "perfiles:   %03d"%(self.voltObj1.nProfiles)      
        self.specObj1 = self.specProcObj.setup(dataInObj = self.voltObj1,nFFTPoints=self.voltObj1.nHeights)
        
       
       
        print "nChannels: %03d"%(self.specObj1.nChannels)
        print "nHeights: %03d"%( self.specObj1.nHeights)
        print "nFFTPoints: %03d"% int(self.specObj1.nFFTPoints)
        
        
    def testSChain( self ):
     
         ini = time.time()
       
         while(True):
            self.readerObj.getData()
            #print self.readerObj.datablock
            #self.voltProcObj.init()
            self.specProcObj.init()
            
            self.specProcObj.integrator(N=32) ## return self.dataOutObj 
            
            self.plot()   
            #print self.readerObj.dataOutObj.data
           
            #CON TODO ESTO PLoTEO
            #freq = self.specProcObj.getFrecuencies()
            #spc = self.specProcObj.getSpectra()
#            print freq
#            print spc, spc.shape
#            pl.plot(freq, spc[2])
#            pl.show()
                   
            if self.readerObj.flagNoMoreFiles:
                break
            
            if self.readerObj.flagIsNewBlock:
                print 'Block No %04d, Time: %s' %(self.readerObj.nTotalBlocks,        
                                                  datetime.datetime.fromtimestamp(self.readerObj.m_BasicHeader.utc),)
         
         
    def plot(self):
        
#            x = self.specProcObj.getFrecuencies()
            x = numpy.arange(self.specObj1.nFFTPoints)
            spc = self.specObj1.data_spc
#            spc = self.specProcObj.getSpectra()
            nchannels = self.specObj1.nChannels
            
#            y1=spc[0]
#            y2=spc[1]
#            y3=spc[2]
#            y4=spc[3]

#            signalList=[y1,y2,y3,y4]
#            xmin = numpy.min(x)
#            xmax = numpy.max(x)   
      
           #Creating Object
            indexPlot = 1
            nsubplot = nchannels
            #nsubplot = 1
            print "nsubplot:%d"%(nsubplot)
            winTitle = "mi grafico de Espectrov1"
            
            subplotTitle = "subplot-Espectro - No Channel."
            xlabel = ""
            ylabel = ""
            
            linearObj = LinearPlot(indexPlot,nsubplot,winTitle)
            
           #Config SubPlots
            print "ConfigSubPlots"
            print "nsubplot:  %d "%nsubplot
            for subplot in range(nsubplot):
                indexplot = subplot + 1
                name=subplot+1
                print "Channel:  %d"%(name)
                title = subplotTitle + '%d'%name
                xmin = numpy.min(x)
                xmax = numpy.max(x)
                ymin = numpy.min(spc[subplot])
                ymax = numpy.max(spc[subplot])
                linearObj.setup(indexplot, xmin, xmax, ymin, ymax, title, xlabel, ylabel)
            
           #Plotting
            type = "simple"
            print "Ploteando"
            print "nsubplot:  %d  "%nsubplot
            for subplot in range(nsubplot):
                indexplot = subplot + 1
                y = spc[subplot,:]
                linearObj.plot(indexplot, x, y, type)
                
            linearObj.refresh()
            linearObj.show()  
      
if __name__ == '__main__':
    TestHeis()
  
    