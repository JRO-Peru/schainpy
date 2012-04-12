'''
Created on 27/03/2012

@author $Author$
@version $Id$
'''
import os, sys
import time, datetime

from Model.Voltage import Voltage
from IO.VoltageIO import *
from Graphics.VoltagePlot import Osciloscope

class TestSChain():
    
    def __init__(self):
        self.setValues()
        self.createObjects()
        self.testSChain()
        pass
    
    def setValues( self ):
        
        self.path = "/home/valentin/Tmp/VOLTAGE"  #1
        #self.path = "/home/valentin/Tmp/VOLTAGE2" #2
        self.startDateTime = datetime.datetime(2011,10,4,00,00,0)
        self.endDateTime = datetime.datetime(2011,10,31,23,59,59)
    
    def createObjects( self ):        
        
        self.Obj = Voltage()
        self.readerObj = VoltageReader(self.Obj)
        self.plotObj = Osciloscope(self.Obj)
        
        if not(self.readerObj.setup( self.path, self.startDateTime, self.endDateTime, expLabel='', online =0) ): 
            sys.exit(0)
            
    def testSChain( self ):
        
        ini = time.time()
        while(True):
            if self.readerObj.getData():
                self.plotObj.plotData(idProfile=0, type='power' )
            
            if self.readerObj.flagNoMoreFiles:
                break
            
            if self.readerObj.flagIsNewBlock:
                print 'Block No %04d, Time: %s' %(self.readerObj.nReadBlocks,
                                                  datetime.datetime.fromtimestamp(self.readerObj.m_BasicHeader.utc),)
#                fin = time.time()
#                print 'Tiempo de un bloque leido y escrito: [%6.5f]' %(fin - ini)
#                ini = time.time()
            
            #time.sleep(0.5)
        self.plotObj.end()
    
if __name__ == '__main__':
    TestSChain()