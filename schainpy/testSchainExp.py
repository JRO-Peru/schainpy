'''

$Author: murco $
$Id: testSchainExp.py 158 2012-11-08 21:31:03Z murco $
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
        
        self.startDate = datetime.date(2012,06,19)
        self.endDate = datetime.date(2012,12,30)
        
        self.startTime = datetime.time(11,0,0)
        self.endTime = datetime.time(23,59,59)
        
        self.nFFTPoints = 32
        
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
                                   online = True)         
        
        self.voltObj2 = self.voltProcObj.setup(dataInObj = self.voltObj1)
        self.specObj1 = self.specProcObj.setup(dataInObj = self.voltObj2, nFFTPoints = self.nFFTPoints)

    def testSChain(self):
        
        ini = time.time()
        
        while(True):
            self.readerObj.getData()
            
            self.voltProcObj.init()
            
            self.voltProcObj.integrator(25, overlapping=False)
#            
#            self.voltProcObj.writeData(self.wrpath,self.profilesPerBlock,self.blocksPerFile)
            self.voltProcObj.selectChannels([0,1,2])
            
#            self.voltProcObj.plotScope(idfigure=0,
#                                        wintitle='test plot library',
#                                        driver='plplot',
#                                        save=False,
#                                        gpath=None,
#                                        type="power")
            
#            self.voltProcObj.plotRti(idfigure=1,
#                                     starttime=self.startTime,
#                                     endtime=self.endTime,
#                                    minvalue=0,
#                                    maxvalue=50,
#                                    wintitle='',
#                                    driver='plplot',
#                                    colormap='jet',
#                                    colorbar=True,
#                                    showprofile=False,
#                                    xrangestep=2,
#                                    save=False,
#                                    gpath=None)
#
#            if self.voltProcObj.dataOutObj.flagNoData ==False:
#                print self.readerObj.dataOutObj.nProfiles
            
            self.specProcObj.init()
            
            self.specProcObj.plotSpc(idfigure=2,
                                     minvalue=30,
                                    maxvalue=70,
                                    wintitle='Spectra',
                                    driver='plplot',
                                    colormap='jet',
                                    colorbar=True,
                                    showprofile=True,
                                    save=False,
                                    gpath=None)
            
            if self.readerObj.flagNoMoreFiles:
                break
            
            if self.readerObj.flagIsNewBlock:
#                print 'Block No %04d, Time: %s' %(self.readerObj.nTotalBlocks, datetime.datetime.fromtimestamp(self.readerObj.basicHeaderObj.utc),)
                print 'Block No %04d, Time: %s' %(self.readerObj.nTotalBlocks, 
                                                  datetime.datetime.fromtimestamp(self.readerObj.basicHeaderObj.utc + self.readerObj.basicHeaderObj.miliSecond/1000.0),)

    
if __name__ == '__main__':
    TestSChain()