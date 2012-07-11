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
#        self.path = "/Users/jro/Documents/RadarData/JULIA"
#        self.startDateTime = datetime.datetime(2007,5,1,15,49,0)
#        self.endDateTime = datetime.datetime(2007,5,1,23,0,0)
        
        self.startDateTime = datetime.datetime(2011,10,1,0,0,0)
        self.endDateTime = datetime.datetime(2011,12,31,0,20,0)
        self.N = 4
        self.npts = 8
    
    def createObjects( self ):        
        
        self.voltObj1 = Voltage()
        self.voltObj2 = Voltage()
        self.specObj1 = Spectra()
        
        self.readerObj = VoltageReader(self.voltObj1)
        self.voltProcObj = VoltageProcessor(self.voltObj1, self.voltObj2)
        self.specProcObj = SpectraProcessor(self.voltObj2, self.specObj1)

        if not(self.readerObj.setup( self.path, self.startDateTime, self.endDateTime, expLabel='', online =0) ): 
            sys.exit(0)
        
        self.specProcObj.setup(nFFTPoints=8)
        

    def testSChain( self ):
        
        ini = time.time()
        while(True):
            self.readerObj.getData()
            
            self.voltProcObj.init()
            
            self.voltProcObj.plotData(winTitle='VOLTAGE INPUT', index=1)
            
            self.voltProcObj.integrator(4)
            
            self.voltProcObj.plotData(winTitle='VOLTAGE AVG', index=2)
            
                        
            self.specProcObj.init()
        
            self.specProcObj.integrator(N=2)
        
            self.specProcObj.plotData(winTitle='Spectra 1', index=3)
             
    
            if self.readerObj.flagNoMoreFiles:
                break
            
            if self.readerObj.flagIsNewBlock:
                print 'Block No %04d, Time: %s' %(self.readerObj.nTotalBlocks,
                                                  datetime.datetime.fromtimestamp(self.readerObj.m_BasicHeader.utc),)


#        self.plotObj.end()
    
if __name__ == '__main__':
    TestSChain()