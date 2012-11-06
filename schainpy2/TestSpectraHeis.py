'''
Created on Jul 31, 2012

@author $Author$
@version $Id$
'''

import os, sys
import time, datetime
#import pylab as pl

from Data.JROData import Voltage
from IO.VoltageIO import *

from Data.JROData import SpectraHeis
from IO.SpectraIO import *

from Processing.VoltageProcessor import *
from Processing.SpectraProcessor import *

#from  Graphics.BaseGraph_mpl import LinearPlot

class TestHeis():
    i=None
    def __init__(self):
        self.setValues()
        self.createObjects()
        self.testSChain()
        self.i=0
        
    def setValues( self ):
        
        self.path="/home/roj-idl71/data"

        #self.path = ""     
        self.startDate = datetime.date(2012,4,1)
        self.endDate = datetime.date(2012,6,30)
        
        self.startTime = datetime.time(0,0,0)
        self.endTime = datetime.time(23,0,0)

    
    def createObjects( self ):
        
        self.readerObj = VoltageReader()
        self.specProcObj = SpectraHeisProcessor()

        self.voltObj1 = self.readerObj.setup(
                                   path = self.path,
                                   startDate = self.startDate,
                                   endDate = self.endDate,
                                   startTime = self.startTime,
                                   endTime = self.endTime,
                                   expLabel = '',
                                   online = 0) 
       
        if not(self.voltObj1):
            sys.exit(0)   
   
        self.specObj1 = self.specProcObj.setup(dataInObj = self.voltObj1,nFFTPoints=self.voltObj1.nHeights)
        
       
#       

#        
        
    def testSChain( self ):
     
         ini = time.time()
         counter = 0 
         while(True):
            self.readerObj.getData()
            self.specProcObj.init()
            
            self.specProcObj.integrator(N=32) ## return self.dataOutObj
            

            
         
            self.specProcObj.plotScope(idfigure=1,
                                        wintitle='test plot library',
                                        driver='plplot',
                                        minvalue = 30000.0,
                                        maxvalue = 5000000.0,
                                        save=True,
                                        gpath="/home/roj-idl71/PlotImage")
     
            
            if self.readerObj.flagNoMoreFiles: 
               break
       
               
            
            if self.readerObj.flagIsNewBlock:
                print 'Block No %04d, Time: %s' %(self.readerObj.nTotalBlocks,        
                                                  datetime.datetime.fromtimestamp(self.readerObj.basicHeaderObj.utc),)
 
         
      
if __name__ == '__main__':
    TestHeis()
  
    