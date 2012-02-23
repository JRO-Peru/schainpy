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
        self.testSChain()
        pass
    
    def setValues(self):
        
        self.path = '/home/roj-idl71/Data/RAWDATA/DP_Faraday/'
        self.path = '/Users/danielangelsuarezmunoz/Documents/Projects/testWR'
        self.path = '/home/roj-idl71/Data/RAWDATA/IMAGING'
#        self.path = '/home/roj-idl71/tmp/data'
        #self.path = '/remote/puma/2004_11/DVD/'
        
        self.ppath = "/home/roj-idl71/tmp/data"
        self.startDateTime = datetime.datetime(2011,1,1,17,49,0)
        self.endDateTime = datetime.datetime(2011,1,30,18,10,0)
    
    def createObjects(self):        
        
        self.Obj = Spectra()
        self.readerObj = SpectraReader(self.Obj)
        self.plotObj = Spectrum(self.Obj)
#        self.writerObj = SpectraWriter(self.Obj)
        
        if not(self.readerObj.setup(self.path, self.startDateTime, self.endDateTime, expLabel='')):
            sys.exit(0)
            
#        if not(self.writerObj.setup(self.ppath)):
#            sys.exit(0)
    
    def testSChain(self):
        
        ini = time.time()
        while(True):
            self.readerObj.getData()
            self.plotObj.plotData(showColorbar=False, showPowerProfile=True)
            
#            self.writerObj.putData()
            
            if self.readerObj.noMoreFiles:
                break
            
            if self.readerObj.flagIsNewBlock:
                print 'Block No %04d, Time: %s' %(self.readerObj.nReadBlocks,
                                                  datetime.datetime.fromtimestamp(self.readerObj.m_BasicHeader.utc),)
                fin = time.time()
                print 'Tiempo de un bloque leido y escrito: [%6.5f]' %(fin - ini)
                ini = time.time()
            
            #time.sleep(0.5)
        self.plotObj.end()
    
if __name__ == '__main__':
    TestSChain()