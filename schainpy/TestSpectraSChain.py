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
        
        #self.path = "/home/valentin/Tmp/RAWDATA"
        self.path = "/home/valentin/Tmp/RAWDATA"
        self.startDateTime = datetime.datetime(2009,11,2,00,00,0)
        self.endDateTime = datetime.datetime(2009,11,30,18,10,0)
    
    def createObjects(self):        
        
        self.Obj = Spectra()
        self.readerObj = SpectraReader(self.Obj)
        self.plotObj = Spectrum(self.Obj)
#        self.writerObj = SpectraWriter(self.Obj)
        
        if not(self.readerObj.setup(self.path, self.startDateTime, self.endDateTime, expLabel='', online =1)): #self.startDateTime
            sys.exit(0)
            
#        if not(self.writerObj.setup(self.ppath)):
#            sys.exit(0)
    
    def testSChain(self):
        
        ini = time.time()
        while(True):
            if self.readerObj.getData():
                self.plotObj.plotData(showColorbar=True, showPowerProfile=True) #zmin=40, zmax=140, 
            
#            self.writerObj.putData()

            
            if self.readerObj.flagNoMoreFiles:
                break
            
            if self.readerObj.flagIsNewBlock and self.readerObj.nReadBlocks:
                print 'Block No %04d, Time: %s' %(self.readerObj.nReadBlocks,
                                                  datetime.datetime.fromtimestamp(self.readerObj.m_BasicHeader.utc),)
                #===============================================================
                # fin = time.time()
                # print 'Tiempo de un bloque leido y escrito: [%6.5f]' %(fin - ini)
                # ini = time.time()
                #===============================================================
            
            #time.sleep(0.5)
        self.plotObj.end()
    
if __name__ == '__main__':
    TestSChain()