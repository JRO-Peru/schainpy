'''
Created on 23/01/2012

@author $Author$
@version $Id$
'''
import os, sys
import time, datetime

from Model.Voltage import Voltage
from IO.VoltageIO import VoltageReader
from Graphics.VoltagePlot import Osciloscope

class TestSChain():
    
    
    def __init__(self):
        self.setValues()
        self.createObjects()
        self.testSChain()
        pass
    
    def setValues(self):
        
        self.path = '/home/roj-idl71/Data/RAWDATA/DP_Faraday/'
        self.path = '/Users/danielangelsuarezmunoz/Documents/Projects/testWR'
        #self.path = '/remote/puma/2004_11/DVD/'
        self.startDateTime = datetime.datetime(2004,5,1,17,49,0)
        self.endDateTime = datetime.datetime(2012,5,1,18,10,0)
    
    def createObjects(self):        
        
        self.voltageObj = Voltage()
        self.readerObj = VoltageReader(self.voltageObj)
        self.plotObj = Osciloscope(self.voltageObj)
        
        self.readerObj.setup(self.path, self.startDateTime, self.endDateTime)
    
    def testSChain(self):
        
        while(True):
            
            self.readerObj.getData()
            self.plotObj.plotData(idProfile = 1, type='iq', ymin = -100, ymax = 100)
            
            if self.readerObj.flagResetProcessing:
                print 'jump'
                
#            if self.readerObj.flagIsNewBlock:
#                print 'Block No %04d, Time: %s'%(self.readerObj.nReadBlocks,
#                                                 datetime.datetime.fromtimestamp(self.readerObj.m_BasicHeader.utc))

            if self.readerObj.noMoreFiles:
                break
                
        self.plotObj.end()
    
if __name__ == '__main__':
    TestSChain()