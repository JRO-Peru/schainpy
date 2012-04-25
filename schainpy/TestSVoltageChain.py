'''
Created on 27/03/2012

@author $Author$
@version $Id$
'''
import os, sys
import time, datetime

from Model.Voltage import Voltage
from IO.VoltageIO import *
#from Graphics.VoltagePlot import Osciloscope

from Model.Spectra import Spectra
from IO.SpectraIO import *

from Processing.VoltageProcessor import *
from Processing.SpectraProcessor import *

class TestSChain():
    
    def __init__(self):
        self.setValues()
        self.createObjects()
        self.testSChain()
        
    
    def setValues( self ):
        
        self.path = "/home/dsuarez/Projects"  #1
        self.path = "/home/roj-idl71/Data/RAWDATA/IMAGING"
#        self.startDateTime = datetime.datetime(2007,5,1,15,49,0)
#        self.endDateTime = datetime.datetime(2007,5,1,23,0,0)
        
        self.startDateTime = datetime.datetime(2011,10,4,0,0,0)
        self.endDateTime = datetime.datetime(2011,10,4,0,20,0)
        self.N = 10
        self.npts = 1024
    
    def createObjects( self ):        
        
        self.voltObj1 = Voltage()
        self.voltObj2 = Voltage()
        self.specObj1 = Spectra()
        
        self.readerObj = VoltageReader(self.voltObj1)
        self.voltProcObj = VoltageProcessor(self.voltObj1, self.voltObj2)
        self.specProcObj = SpectraProcessor(self.voltObj2, self.specObj1)
        
        
        #self.plotObj = Osciloscope(self.voltObj1)
        
        if not(self.readerObj.setup( self.path, self.startDateTime, self.endDateTime, expLabel='', online =0) ): 
            sys.exit(0)
        
#        if not(self.readerObj.setup(self.path, self.startDateTime, self.endDateTime)):
#            sys.exit(0)
            
    def testSChain( self ):
        
        ini = time.time()
        while(True):
            self.readerObj.getData()
            
            self.voltProcObj.init()
            
#            self.voltProcObj.plotData(idProfile = 1, type='iq', ymin=-25000, ymax=25000, winTitle='sin decodificar')
            
            self.voltProcObj.decoder(type=0)
            
#            self.voltProcObj.plotData(idProfile = 1, type='iq', ymin=-70000, ymax=70000,winTitle='Decodificado')
#            
            self.voltProcObj.integrator(self.N)
            
#            self.voltProcObj.plotData(idProfile = 1, type='iq', ymin=-700000, ymax=700000,winTitle='figura 3')
            
            self.specProcObj.init(self.npts)
        
            self.specProcObj.integrator(2)
        
            self.specProcObj.plotData(winTitle='Spectra 1', index=0)
            
#            if self.readerObj.getData():
#                self.plotObj.plotData(idProfile=0, type='power' )
#
#            
            if self.readerObj.flagNoMoreFiles:
                break
#            
            if self.readerObj.flagIsNewBlock:
                print 'Block No %04d, Time: %s' %(self.readerObj.nTotalBlocks,
                                                  datetime.datetime.fromtimestamp(self.readerObj.m_BasicHeader.utc),)

#                fin = time.time()
#                print 'Tiempo de un bloque leido y escrito: [%6.5f]' %(fin - ini)
#                ini = time.time()
            
            #time.sleep(0.5)
#        self.plotObj.end()
    
if __name__ == '__main__':
    TestSChain()