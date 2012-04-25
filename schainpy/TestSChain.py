'''
Created on 23/01/2012

@author $Author$
@version $Id$
'''
import os, sys
import time, datetime

from Model.Voltage import Voltage
from IO.VoltageIO import *
from Graphics.VoltagePlot import Osciloscope

from Model.Spectra import Spectra
from IO.SpectraIO import *
from Graphics.SpectraPlot import Spectrum

class TestSChain():
    
    
    def __init__(self):
        self.setValues()
        self.createObjects()
        self.setupObjects()
        self.testSChain()
        pass
    
    def setValues(self):
        
        self.path = '/home/roj-idl71/Data/RAWDATA/DP_Faraday/'
        self.path = '/Users/danielangelsuarezmunoz/Documents/Projects/testWR'
        self.path = '/home/roj-idl71/Data/RAWDATA/IMAGING'
        #self.path = '/remote/puma/2011_08/E-F_Valley'
        #self.path = '/remote/puma/2011_12/EEJ+150km+ONAXIS+ESF+Twilight/Twilight/'
        self.path = '/home/roj-idl71/tmp/data/'
        
        self.ppath = "/home/roj-idl71/tmp/data"
        self.startDateTime = datetime.datetime(2011,1,31,0,20,0)
        self.endDateTime = datetime.datetime(2011,12,5,18,10,0)
    
    def createObjects(self):        

#        self.Obj = Voltage()
#        self.readerObj = VoltageReader(self.Obj)
#        self.plotObj = Osciloscope(self.Obj)
#        self.writerObj = VoltageWriter(self.Obj)
      
        self.Obj = Spectra()
        self.readerObj = SpectraReader(self.Obj)
        self.plotObj = Spectrum(self.Obj)
#        self.writerObj = SpectraWriter(self.Obj)

    def setupObjects(self):
        
        if not(self.readerObj.setup(self.path, self.startDateTime, self.endDateTime, expLabel='', online = 0)):
            sys.exit(0)
        
        print "Parameters:"
        
        print "Num profiles: %s" %(self.readerObj.m_SystemHeader.numProfiles)
        print "Num samples: %s" %(self.readerObj.m_SystemHeader.numSamples)
        print "Num channels: %s" %(self.readerObj.m_SystemHeader.numChannels)
        
        print "Num profiles per block: %s" %(self.readerObj.m_ProcessingHeader.profilesPerBlock)
        print "Num heights: %s" %(self.readerObj.m_ProcessingHeader.numHeights)
        print "Num coh int: %s" %(self.readerObj.m_ProcessingHeader.coherentInt)
        print "Num incoh int: %s" %(self.readerObj.m_ProcessingHeader.incoherentInt)
        
        print "Num code: %d" %(self.readerObj.m_ProcessingHeader.numCode)
        print "Num baud: %d" %(self.readerObj.m_ProcessingHeader.numBaud)
        
#        if not(self.writerObj.setup(self.ppath)):
#            sys.exit(0)
    
    def testSChain(self):
        
        ini = time.time()
        while(True):
            self.readerObj.getData()
            self.plotObj.plotData(zmin=40, zmax=140, showColorbar=True, showPowerProfile=True)
            #self.plotObj.plotData(idProfile=1, type="power")
#            self.writerObj.putData()
            
            if self.readerObj.noMoreFiles:
                break
            
            if self.readerObj.flagIsNewBlock:
                print 'Block No %04d, Time: %s' %(self.readerObj.nTotalBlocks,
                                                  datetime.datetime.fromtimestamp(self.readerObj.m_BasicHeader.utc),)
                fin = time.time()
                print 'Tiempo de un bloque leido y escrito: [%6.5f]' %(fin - ini)
                ini = time.time()
            
            #time.sleep(0.5)
        self.plotObj.end()
    
if __name__ == '__main__':
    TestSChain()