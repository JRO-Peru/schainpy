'''
Created on Jul 31, 2012

@author $Author$
@version $Id$
'''

import os, sys
import time, datetime

from Model.Voltage import Voltage
from IO.VoltageIO import *

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
        
        self.path = "/home/dsuarez/Projects"
        self.path = "/Users/jro/Documents/RadarData/EW_Drifts"
        self.path = "/Users/jro/Documents/RadarData/MST_ISR/MST"
        self.path = "/home/daniel/RadarData/MST"
        
        self.startDate = datetime.date(2009,01,1)
        self.endDate = datetime.date(2009,01,31)
        
        self.startTime = datetime.time(0,0,0)
        self.endTime = datetime.time(20,0,0)
        self.N = 4
        self.npts = 8
    
    def createObjects( self ):
        
        self.readerObj = VoltageReader()
        self.voltProcObj = VoltageProcessor()
        self.specProcObj = SpectraProcessor()

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
        
        self.voltObj2 = self.voltProcObj.setup(dataInObj = self.voltObj1)
        
        self.specObj1 = self.specProcObj.setup(dataInObj = self.voltObj2,
                                          nFFTPoints = 16)
        

    def testSChain( self ):
        
        ini = time.time()

        while(True):
            self.readerObj.getData()
            
            self.voltProcObj.init()
            
            self.voltProcObj.plotScope(winTitle="Scope 1",type="iq", index=1)
            
            self.voltProcObj.plotRti(winTitle='VOLTAGE INPUT', showPowerProfile=True, index=2)
            
            self.voltProcObj.integrator(4)

            self.specProcObj.init()
        
            self.specProcObj.integrator(N=4)
            
#            self.specProcObj.plotSpec(winTitle='Spectra Test', showColorbar=True,showPowerProfile=True,index=3)
            self.specProcObj.plotData(winTitle='Spectra Test', showColorbar=True,showPowerProfile=True,save=False,index=3)
            
            if self.readerObj.flagNoMoreFiles:
                break
            
            if self.readerObj.flagIsNewBlock:
                print 'Block No %04d, Time: %s' %(self.readerObj.nTotalBlocks,
                                                  datetime.datetime.fromtimestamp(self.readerObj.m_BasicHeader.utc),)

    
if __name__ == '__main__':
    TestSChain()