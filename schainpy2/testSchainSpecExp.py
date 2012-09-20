
import os, sys
import time, datetime

path = os.path.split(os.getcwd())[0]
sys.path.append(path)


from Data.Spectra import Spectra
from IO.SpectraIO import *
from Processing.SpectraProcessor import *



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
        
        self.startDate = datetime.date(2012,3,1)
        self.endDate = datetime.date(2012,3,30)
        
        self.startTime = datetime.time(0,0,0)
        self.endTime = datetime.time(14,1,1)
        
        # paramatros para Escritura de Pdata
        self.wrpath = "/Users/danielangelsuarezmunoz/Data/testWR_pdata"
        self.profilesPerBlock = 8
        self.blocksPerFile = 5
#        self.pairList = [(0,1),(0,2)]
        
    
    def createObjects(self):        
        
        self.readerObj = SpectraReader()

        self.specObj1 = self.readerObj.setup(
                                   path = self.path,
                                   startDate = self.startDate,
                                   endDate = self.endDate,
                                   startTime = self.startTime,
                                   endTime = self.endTime,
                                   expLabel = '',
                                   online = 0) 
        # new lines
        self.specObjProc = SpectraProcessor()
        
        self.specObj2 = self.specObjProc.setup(dataInObj = self.specObj1)
        
        

    def testSChain(self):
        
        ini = time.time()

        while(True):
            self.readerObj.getData()
            
            self.specObjProc.init()
            
            self.specObjProc.writeData(self.wrpath,self.profilesPerBlock,self.blocksPerFile)
                   
            if self.readerObj.flagNoMoreFiles:
                break
            
            if self.readerObj.flagIsNewBlock:
                print 'Block No %04d, Time: %s' %(self.readerObj.nTotalBlocks,
                                                  datetime.datetime.fromtimestamp(self.readerObj.basicHeaderObj.utc))

    
if __name__ == '__main__':
    TestSChain()