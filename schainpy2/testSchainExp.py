
import os, sys
import time, datetime

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from Data.Voltage import Voltage
from IO.VoltageIO import *

from Processing.VoltageProcessor import *



class TestSChain():
    
    def __init__(self):
        self.setValues()
        self.createObjects()
        self.testSChain()

    def setValues(self):
        self.path = "/Users/jro/Documents/RadarData/MST_ISR/MST"
        
        self.wrpath = "/Users/jro/Documents/RadarData/wr_data"
        
        self.startDate = datetime.date(2009,1,17)
        self.endDate = datetime.date(2009,1,17)
        
        self.startTime = datetime.time(0,0,0)
        self.endTime = datetime.time(14,1,1)
    
    def createObjects(self):        
        self.readerObj = VoltageReader()
        self.voltProcObj = VoltageProcessor()

        self.voltObj1 = self.readerObj.setup(
                                   path = self.path,
                                   startDate = self.startDate,
                                   endDate = self.endDate,
                                   startTime = self.startTime,
                                   endTime = self.endTime,
                                   expLabel = '',
                                   online = 0) 
        
        

    def testSChain(self):
        
        ini = time.time()

        while(True):
            self.readerObj.getData()
                   
            if self.readerObj.flagNoMoreFiles:
                break
            
            if self.readerObj.flagIsNewBlock:
                print 'Block No %04d, Time: %s' %(self.readerObj.nTotalBlocks,
                                                  datetime.datetime.fromtimestamp(self.readerObj.m_BasicHeader.utc),)

    
if __name__ == '__main__':
    TestSChain()