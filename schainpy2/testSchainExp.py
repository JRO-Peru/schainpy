'''

$Author$
$Id$
'''
import os, sys
import time, datetime

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from Data.JROData import Voltage
from IO.VoltageIO import *

from Processing.VoltageProcessor import *
from Processing.SpectraProcessor import *

class TestSChain():
    
    def __init__(self):
        self.setValues()
        self.createObjects()
        self.testSChain()

    def setValues(self):
        self.path = "/home/roj-idl71/Data/RAWDATA/Meteors"
        self.path = "/remote/puma/2012_06/Meteors"
        
        self.startDate = datetime.date(2012,1,1)
        self.endDate = datetime.date(2012,12,30)
        
        self.startTime = datetime.time(0,0,0)
        self.endTime = datetime.time(23,59,59)
        
        self.nFFTPoints = 64
        
        self.wrpath = "/home/roj-idl71/tmp/results"
        self.profilesPerBlock = 40
        self.blocksPerFile = 50
    
    def createObjects(self):        
        
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
        
        self.voltObj2 = self.voltProcObj.setup(dataInObj = self.voltObj1)
        self.specObj1 = self.specProcObj.setup(dataInObj = self.voltObj2, nFFTPoints = self.nFFTPoints)

    def testSChain(self):
        
        ini = time.time()

        while(True):
            self.readerObj.getData()
            
            self.voltProcObj.init()
            
            self.voltProcObj.integrator(100, overlapping=False)
#            
#            self.voltProcObj.writeData(self.wrpath,self.profilesPerBlock,self.blocksPerFile)
            
            
            self.voltProcObj.plotScope(idfigure=0,
                                        wintitle='test plot library',
                                        driver='plplot',
                                        save=False,
                                        gpath=None,
                                        type="power")
            self.voltProcObj.plotRti(
                                     idfigure=1,
                                     starttime=self.startTime,
                                     endtime=self.endTime,
                                    rangemin=0,
                                    rangemax=1000,
                                    minvalue=None,
                                    maxvalue=None,
                                    wintitle='',
                                    driver='plplot',
                                    colormap='br_green',
                                    colorbar=True,
                                    showprofile=False,
                                    xrangestep=1,
                                    save=False,
                                    gpath=None)
                    
            
#            self.specProcObj.init()
#            
#            self.specProcObj.plotSpc(idfigure=1,
#                                    wintitle='Spectra',
#                                    driver='plplot',
#                                    colormap='br_green',
#                                    colorbar=True,
#                                    showprofile=False,
#                                    save=False,
#                                    gpath=None)
            
            if self.readerObj.flagNoMoreFiles:
                break
            
            if self.readerObj.flagIsNewBlock:
#                print 'Block No %04d, Time: %s' %(self.readerObj.nTotalBlocks, datetime.datetime.fromtimestamp(self.readerObj.basicHeaderObj.utc),)
                print 'Block No %04d, Time: %s' %(self.readerObj.nTotalBlocks, 
                                                  datetime.datetime.fromtimestamp(self.readerObj.basicHeaderObj.utc + self.readerObj.basicHeaderObj.miliSecond/1000.0),)

    
if __name__ == '__main__':
    TestSChain()