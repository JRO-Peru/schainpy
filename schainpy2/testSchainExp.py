'''

$Author$
$Id$
'''
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
        self.path = "/home/dsuarez/RadarData/EW_DRIFTS"
        self.startDate = datetime.date(2012,6,1)
        self.endDate = datetime.date(2012,7,30)
        
#        self.path = "/Users/danielangelsuarezmunoz/Data/Imaging_rawdata"
#        self.startDate = datetime.date(2011,10,4)
#        self.endDate = datetime.date(2011,10,4)

        # Probando los escritos por Signal Chain
#        self.path = "/home/dsuarez/RadaData"
#        self.startDate = datetime.date(2011,11,28)
#        self.endDate = datetime.date(2011,11,30)
        
        self.startTime = datetime.time(0,0,0)
        self.endTime = datetime.time(23,59,59)
        
        self.wrpath = "/home/dsuarez/RadarData"
        self.profilesPerBlock = 40
        self.blocksPerFile = 50
    
    def createObjects(self):        
        
        self.readerObj = VoltageReader()

        self.voltObj1 = self.readerObj.setup(
                                   path = self.path,
                                   startDate = self.startDate,
                                   endDate = self.endDate,
                                   startTime = self.startTime,
                                   endTime = self.endTime,
                                   expLabel = '',
                                   online = 0) 
        
        self.voltObjProc = VoltageProcessor()
        
        self.voltObj2 = self.voltObjProc.setup(dataInObj = self.voltObj1)

    def testSChain(self):
        
        ini = time.time()

        while(True):
            self.readerObj.getData()
            
            self.voltObjProc.init()
#            
#            self.voltObjProc.writeData(self.wrpath,self.profilesPerBlock,self.blocksPerFile)
            
            
            self.voltObjProc.plotScope(idfigure=1,
                                        wintitle='test plot library',
                                        driver='plplot',
                                        save=False,
                                        gpath=None,
                                        type="power")
            
            if self.readerObj.flagNoMoreFiles:
                break
            
            if self.readerObj.flagIsNewBlock:
#                print 'Block No %04d, Time: %s' %(self.readerObj.nTotalBlocks, datetime.datetime.fromtimestamp(self.readerObj.basicHeaderObj.utc),)
                print 'Block No %04d, Time: %s' %(self.readerObj.nTotalBlocks, 
                                                  datetime.datetime.utcfromtimestamp(self.readerObj.basicHeaderObj.utc + self.readerObj.basicHeaderObj.miliSecond/1000.0),)

    
if __name__ == '__main__':
    TestSChain()