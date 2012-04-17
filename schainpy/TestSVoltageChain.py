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
        #self.path = "/home/valentin/Tmp/VOLTAGE2" #2
#        self.startDateTime = datetime.datetime(2007,5,1,15,49,0)
#        self.endDateTime = datetime.datetime(2007,5,1,23,0,0)
        
        self.startDateTime = datetime.datetime(2011,10,4,0,0,0)
        self.endDateTime = datetime.datetime(2011,10,4,0,20,0)
        self.N = 2
        self.npts = 4
    
    def createObjects( self ):        
        
        self.Obj = Voltage()
        self.OutObj = Voltage()
        self.readerObj = VoltageReader(self.Obj)
        self.procObj = VoltageProcessor(self.Obj, self.OutObj)
        
        self.spectraObj = Spectra()
        self.specProcObj = SpectraProcessor(self.OutObj, self.spectraObj,self.npts)
        
        
        #self.plotObj = Osciloscope(self.Obj)
        
        if not(self.readerObj.setup( self.path, self.startDateTime, self.endDateTime, expLabel='', online =0) ): 
            sys.exit(0)
        
#        if not(self.readerObj.setup(self.path, self.startDateTime, self.endDateTime)):
#            sys.exit(0)
            
    def testSChain( self ):
        
        ini = time.time()
        while(True):
            self.readerObj.getData()
            
            self.procObj.init()
            
            self.procObj.plotData(idProfile = 1, type='power',winTitle='figura 1')
            
            self.procObj.decoder(type=0)
            
#            self.procObj.plotData(idProfile = 1, type='iq', xmin=0, xmax=100,winTitle='figura 2')
#            
#            self.procObj.integrator(self.N)
            
            self.procObj.plotData(idProfile = 1, type='power',winTitle='figura 3')
            
            self.specProcObj.init()
        
            self.specProcObj.integrator(2)
        
            self.specProcObj.plotData(winTitle='Spectra 1', index=2)
            
#            if self.readerObj.getData():
#                self.plotObj.plotData(idProfile=0, type='power' )
#
#            
#            if self.readerObj.flagNoMoreFiles:
#                break
#            
            if self.readerObj.flagIsNewBlock:
                print 'Block No %04d, Time: %s' %(self.readerObj.nReadBlocks,
                                                  datetime.datetime.fromtimestamp(self.readerObj.m_BasicHeader.utc),)

#                fin = time.time()
#                print 'Tiempo de un bloque leido y escrito: [%6.5f]' %(fin - ini)
#                ini = time.time()
            
            #time.sleep(0.5)
#        self.plotObj.end()
    
if __name__ == '__main__':
    TestSChain()