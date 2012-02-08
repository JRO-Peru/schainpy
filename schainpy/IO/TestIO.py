'''
Created on 23/01/2012

@author: danielangelsuarezmunoz
'''
import os
import sys
import datetime
import time

class TestIO():
    
    def __init__(self):
        self.setValues()
        self.createVoltageObjects()
        self.testReadVoltage()
        pass
    
    def setValues(self):
        
        
        self.path = '/Users/danielangelsuarezmunoz/Documents/Projects'
        self.startDateTime = datetime.datetime(2007,5,1,17,49,0)
        self.endDateTime = datetime.datetime(2007,5,1,18,10,0)
    
    def createVoltageObjects(self):
        path = os.path.split(os.getcwd())[0]
        sys.path.append(path)
        
        from IO.Voltage import VoltageReader
        from Model.Voltage import Voltage
        
        self.voltageModelObj = Voltage()
        self.voltageReaderObj = VoltageReader(self.voltageModelObj)
        self.voltageReaderObj.setup(self.path, self.startDateTime, self.endDateTime)
    
    def testReadVoltage(self):
        while(not(self.voltageReaderObj.noMoreFiles)):
            
            self.voltageReaderObj.getData()
            if self.voltageReaderObj.flagResetProcessing:
                print 'jump'
                
            if self.voltageReaderObj.flagIsNewBlock:
                print 'Block No %04d, Time: %s'%(self.voltageReaderObj.nReadBlocks,
                                                 datetime.datetime.fromtimestamp(self.voltageReaderObj.m_BasicHeader.utc))

if __name__ == '__main__':
    TestIO()