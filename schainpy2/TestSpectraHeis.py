'''
Created on Jul 31, 2012

@author $Author$
@version $Id$
'''

import os, sys
import time, datetime
import getopt
#import pylab as pl

from Data.JROData import Voltage
from IO.VoltageIO import *

from Data.JROData import SpectraHeis
from IO.SpectraIO import *

from Processing.VoltageProcessor import *
from Processing.SpectraProcessor import *

#from  Graphics.BaseGraph_mpl import LinearPlot

class TestHeis():
    
    def __init__(self):
        self.setValues()
        self.createObjects()
        self.testSChain()
        self.i=0
        
    
    
    def VerifyArguments(self):
        arglist = ''
        longarglist = ['path=','online=','N=','fpath=']
        optlist,args = getopt.getopt(sys.argv[1:],arglist, longarglist)
        for opt in optlist:
            if opt[0] == '--path':
                    self.path = opt[1]
            elif opt[0] == '--online':
                   self.online = int(opt[1])
                   
            elif opt[0] == '--N':
                   self.N = int(opt[1])
            elif opt[0] == '--fpath':
                   self.fpath = opt[1]
#                   if self.online==0:
#                       if opt[0] == '--starDate':
#                           self.StarDate = opt[1]
#                       elif opt[0] == '--endDate':
#                           self.EndDate = opt[1]  
#                       elif opt[0] == '--startTime':
#                           self.StartTime = opt[1]   
#                       elif opt[0] == '--endTime':
#                           self.EndTime = opt[1]     
#            
#            elif opt[0] == '--starDate':
#                self.StarDate = None
#            
#            elif opt[0] == '--endDate':   
#                self.EndDate = None
#                
#            elif opt[0] == '--startTime':
#                self.StartTime = None  
#                
#            elif opt[0] == '--endTime':
#                self.EndTime = None                                                                                                            

    
    def setValues(self):
        self.VerifyArguments()           
        #stardateList=self.Stardate.split()
        
        self.startDate = datetime.date(2012,10,1)
        self.endDate = datetime.date(2012,12,30)
        
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
                                   online = self.online,
                                   delay=10) 
       
        if not(self.voltObj1):
            sys.exit(0)   
   
        self.specObj1 = self.specProcObj.setup(dataInObj = self.voltObj1,nFFTPoints=self.voltObj1.nHeights)
#              
    def testSChain( self ):
     
         ini = time.time()
         counter = 0 
         while(True):
            self.readerObj.getData()
            
            self.specProcObj.init()
            
            self.specProcObj.integrator(self.N) ## return self.dataOutObj
            
            self.specProcObj.writedata(self.fpath)
            
            self.specProcObj.plotMatScope(idfigure=1)            
                       
            if self.readerObj.flagNoMoreFiles:
               break
       
               
            
            if self.readerObj.flagIsNewBlock:
                print 'Block No %04d, Time: %s' %(self.readerObj.basicHeaderObj.dataBlock,        
                                                  datetime.datetime.fromtimestamp(self.readerObj.basicHeaderObj.utc),)
                
         
      
if __name__ == '__main__':
    TestHeis()
  
    