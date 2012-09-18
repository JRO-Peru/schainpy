
import os, sys
import time, datetime

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from Data.Voltage import Voltage
from Data.Spectra import Spectra
from IO.VoltageIO import *
from IO.SpectraIO import *
from Processing.VoltageProcessor import *



class TestSChain:
    
    def __init__(self):
        self.setValues()
        self.createObjects()
        self.testSChain()

    def setValues(self):
        self.path = "/Users/jro/Documents/RadarData/MST_ISR/MST"
#        self.path = "/home/roj-idl71/Data/RAWDATA/IMAGING"
        self.path = "/Users/danielangelsuarezmunoz/Data/EW_Drifts"
        self.path = "/Users/danielangelsuarezmunoz/Data/IMAGING"
        
        self.wrpath = "/Users/jro/Documents/RadarData/wr_data"
        
        self.startDate = datetime.date(2012,3,1)
        self.endDate = datetime.date(2012,3,30)
        
        self.startTime = datetime.time(0,0,0)
        self.endTime = datetime.time(14,1,1)
    
    def createObjects(self):        
        
        self.readerObj = SpectraReader()

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
                                                  datetime.datetime.fromtimestamp(self.readerObj.basicHeaderObj.utc),)

    
if __name__ == '__main__':
    TestSChain()