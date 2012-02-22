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
        self.path = '/home/roj-idl71/tmp/data'
        #self.path = '/remote/puma/2004_11/DVD/'
        
        self.ppath = "/home/roj-idl71/tmp/data"
        self.startDateTime = datetime.datetime(2004,5,1,17,49,0)
        self.endDateTime = datetime.datetime(2012,5,1,18,10,0)
    
    def createObjects(self):        
        
        self.voltageObj = Voltage()
        self.readerObj = VoltageReader(self.voltageObj)
        self.plotObj = Osciloscope(self.voltageObj)
        self.writerObj = VoltageWriter(self.voltageObj)
        
        if not(self.readerObj.setup(self.path, self.startDateTime, self.endDateTime)):
            sys.exit(0)
            
        if not(self.writerObj.setup(self.ppath)):
            sys.exit(0)
    
    def testSChain(self):
        
        ini = time.time()
        while(True):
            self.readerObj.getData()
            self.plotObj.plotData(idProfile = 1, type='iq', ymin = -100, ymax = 100)
            
#            self.writerObj.putData()
            
            if self.readerObj.noMoreFiles:
                break
            
            if self.readerObj.flagIsNewBlock:
                print 'Block No %04d, Time: %s' %(self.readerObj.nReadBlocks,
                                                  datetime.datetime.fromtimestamp(self.readerObj.m_BasicHeader.utc),)
                fin = time.time()
                print 'Tiempo de un bloque leido y escrito: [%6.5f]' %(fin - ini)
                ini = time.time()            
            
            
            
            
            
        self.plotObj.end()
    
if __name__ == '__main__':
    TestSChain()