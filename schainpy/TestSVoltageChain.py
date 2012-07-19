'''
Created on 27/03/2012

@author $Author$
@version $Id$
'''
import os, sys
import time, datetime

from Model.Voltage import Voltage
from IO.VoltageIO import *
#from Graphics.VoltagePlot import Osciloscope

from Model.Spectra import Spectra
from IO.SpectraIO import *

from Processing.VoltageProcessor import *
from Processing.SpectraProcessor import *


class TestSChain():
    
    def __init__(self):
        self.setValues()
        self.createObjects()
        self.testSChain()
        
    
    def setValues( self ):
        
        self.path = "/home/dsuarez/Projects"  #1
        self.path = "/Users/jro/Documents/RadarData/EW_Drifts"
        self.path = "/Users/jro/Documents/RadarData/MST_ISR/MST"
#        self.startDateTime = datetime.datetime(2007,5,1,15,49,0)
#        self.endDateTime = datetime.datetime(2007,5,1,23,0,0)
        
        self.startDateTime = datetime.datetime(2009,01,1,0,0,0)
        self.endDateTime = datetime.datetime(2009,01,31,0,20,0)
        
#        self.startDateTime = datetime.datetime(2011,11,1,0,0,0)
#        self.endDateTime = datetime.datetime(2011,12,31,0,20,0)
        
        
        self.N = 4
        self.npts = 8
    
    def createObjects( self ):
        
        self.readerObj = VoltageReader()
        self.voltProcObj = VoltageProcessor()
        self.specProcObj = SpectraProcessor()

        voltObj1 = self.readerObj.setup(
                                   path = self.path,
                                   startDateTime = self.startDateTime,
                                   endDateTime = self.endDateTime,
                                   expLabel = '',
                                   online = 0) 
        
        if not(voltObj1):
            sys.exit(0)
        
        voltObj2 = self.voltProcObj.setup(dataInObj = voltObj1)
        
        specObj1 = self.specProcObj.setup(dataInObj = voltObj2,
                                          nFFTPoints = 16)
        
#        voltObj2 = self.voltProcObj.setup(dataInObj = voltObj1,
#                                          dataOutObj = voltObj2)
#        
#        specObj1 = self.specProcObj.setup(dataInObj = voltObj2,
#                                          dataOutObj =specObj1,
#                                          nFFTPoints=16)
        

    def testSChain( self ):
        
        ini = time.time()
        while(True):
            self.readerObj.getData()
            
            self.voltProcObj.init()
            
#            self.voltProcObj.plotData(winTitle='VOLTAGE INPUT', index=1)
#            
#            self.voltProcObj.integrator(4)
#            
#            self.voltProcObj.plotData(winTitle='VOLTAGE AVG', index=2)
#            
            
            self.specProcObj.init()
        
            self.specProcObj.integrator(N=1)
        
            self.specProcObj.plotData(winTitle='Spectra 1', index=1)
             
    
            if self.readerObj.flagNoMoreFiles:
                break
            
            if self.readerObj.flagIsNewBlock:
                print 'Block No %04d, Time: %s' %(self.readerObj.nTotalBlocks,
                                                  datetime.datetime.fromtimestamp(self.readerObj.m_BasicHeader.utc),)


#        self.plotObj.end()
    
if __name__ == '__main__':
    TestSChain()