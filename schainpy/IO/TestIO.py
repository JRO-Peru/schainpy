'''
Created on 23/01/2012

@author $Author$
@version $Id$
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
        
        
        self.path = '/Users/danielangelsuarezmunoz/Documents/Projects/testWR'
        self.startDateTime = datetime.datetime(2007,5,1,17,49,0)
        self.endDateTime = datetime.datetime(2007,5,1,18,15,0)
    
    def createVoltageObjects(self):
        path = os.path.split(os.getcwd())[0]
        sys.path.append(path)
        
        from IO.VoltageIO import VoltageReader
        from IO.VoltageIO import VoltageWriter
        from Model.Voltage import Voltage
        
        self.voltageModelObj = Voltage()
        self.voltageReaderObj = VoltageReader(self.voltageModelObj)
        self.voltageReaderObj.setup(self.path, self.startDateTime, self.endDateTime)
        
#        self.voltageWriterObj = VoltageWriter(self.voltageModelObj)
#        self.voltageWriterObj.setup('/Users/danielangelsuarezmunoz/Documents/Projects/testWR')

    
    def testReadVoltage(self):
        while(not(self.voltageReaderObj.noMoreFiles)):
            
            self.voltageReaderObj.getData()
            if self.voltageReaderObj.flagResetProcessing:
                print 'jump'
                
            if self.voltageReaderObj.flagIsNewBlock:
                print 'Block No %04d, Time: %s'%(self.voltageReaderObj.nTotalBlocks,
                                                 datetime.datetime.fromtimestamp(self.voltageReaderObj.m_BasicHeader.utc))
            
#            self.voltageWriterObj.putData()

if __name__ == '__main__':
    TestIO()