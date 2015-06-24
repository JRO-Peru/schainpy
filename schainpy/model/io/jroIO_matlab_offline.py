from schainpy.model.data.jrodata import *
from schainpy.model.proc.jroproc_base import ProcessingUnit, Operation
from schainpy.model.io.jroIO_base import *

import scipy.io as sio 
import pprint
import numpy as np
from os import listdir
from os.path import isfile, join
import datetime
import cmath

class matoffReader(ProcessingUnit):
    
    index=None
    list=None
    firsttime=True
    utccounter=None
    utcfiletime=None
    utcmatcounter=0
    utcfirst=None
    utclist=None
    
    def __init__(self):
        self.dataOut = Spectra()
        return
    
    
    def run(self,path=None,startDate=None, endDate=None,startTime=datetime.time(0,0,0),
        endTime=datetime.time(23,59,59),walk=True,timezone='ut',
        all=0,online=False,ext=None,**kwargs):
        
        self.path=path
        self.ext=ext
        self.startDate=startDate
        self.endDate=endDate
        self.startTime=startTime
        self.endTime=endTime
        
        
        startsearch1=datetime.datetime.combine(startDate,startTime)
        startsearch2=(startsearch1-datetime.datetime(1970,1,1)).total_seconds()
        endsearch1=datetime.datetime.combine(endDate,endTime)
        endsearch2=(endsearch1-datetime.datetime(1970,1,1)).total_seconds()

        
        filelist = [ f for f in listdir(path)]
        
        secondlist=[]
        thirdlist=[]
        utclist=[]
        
        if (self.firsttime==True):
            
            self.utclist=utclist
            
            for g in range(len(filelist)):
                
                strsplit=filelist[g].split('.')
                timeints=[int(i) for i in strsplit]
                timelist=datetime.datetime(timeints[0],timeints[1],timeints[2],timeints[3],timeints[4],timeints[5])
                utctime=(timelist-datetime.datetime(1970,1,1)).total_seconds()
                
                if (utctime<=endsearch2):
                    if (utctime>=startsearch2):
                        secondlist.append(filelist[g])
                        self.utclist.append(utctime)
            
    
            
    
            for k in range(len(secondlist)):
                
                path1=os.path.join(self.path,secondlist[k])
                
                filecounter=len([name for name in os.listdir(path1)])
#                 print "Reading from this dir:" +path1
                for r in range(filecounter):
                    matname=str(r)+'.mat'
                    bork=os.path.join(path1,matname)
                    thirdlist.append(os.path.join(path1,matname))
                    
                    
            self.utcfirst=utclist[0]        
            self.firsttime=False
            self.index=0
            self.list=thirdlist
            
        
        currentfile=self.list[self.index]
        print "Reading from this file:" + currentfile
        
        #filesplit=currentfile.split("\\")
        filesplit=currentfile.split("/")
        newsplit=filesplit[-2]
        newnewsplit=newsplit.split(".")
        newnewsplit=[int(i) for i in newnewsplit]
        gooblist=datetime.datetime(newnewsplit[0],newnewsplit[1],newnewsplit[2],newnewsplit[3],newnewsplit[4],newnewsplit[5])
        self.utcfirst=(gooblist-datetime.datetime(1970,1,1)).total_seconds()
        
        
        newsplit=filesplit[-1]
        newnewsplit=newsplit.split(".")
        goobnum=newnewsplit[0]
        goobnum=int(goobnum)
        
        self.utcfirst=self.utcfirst+goobnum*2
#         if (currentfile[43:]=='0.mat'):
#             self.utcmatcounter=0
#             self.utcfirst=self.utclist[self.index]
            
#         if (self.utcmatcounter>60):
#             self.utcmatcounter=0
       
#         print self.utcmatcounter
        print self.utcfirst
        
        datastuff=sio.loadmat(currentfile)
        dataphase=datastuff.get('phase')
        data3=datastuff.get('doppler0')
        data4=datastuff.get('doppler1')
        data3= np.array(data3)
        data4 = np.array(data4)
        datacoh=datastuff.get('coherence2')
        
        datacohphase=datacoh*np.exp(-dataphase*1j)
#         data31 = np.fliplr(data3)
#         data41 = np.fliplr(data4)
          
        data31 = data3.reshape((1,data3.shape[0],data3.shape[1]))
        data41 = data4.reshape((1,data4.shape[0],data4.shape[1]))
        datacohphase1 = datacohphase.reshape((1,datacoh.shape[0],datacoh.shape[1]))
        
        datastack = np.vstack((data31,data41))
        
        self.dataOut.pairsList=[(0,1)]
        self.dataOut.data_cspc=datacohphase1.copy()
        self.dataOut.data_spc = datastack.copy()
        self.dataOut.channelList = range(2)
        self.dataOut.nProfiles = 25 #this!
        self.dataOut.nIncohInt = 1
        self.dataOut.nCohInt = 1 #this!
        self.dataOut.ippSeconds = 0.004 #this!
        self.dataOut.nFFTPoints = 25
        self.dataOut.utctime = self.utcfirst
        self.dataOut.heightList = np.array(datastuff.get('hts'))
        
        self.dataOut.flagNoData = False  

        
        
#         self.utcmatcounter=2
#         self.utcfirst+=self.utcmatcounter
        self.index+=1    
         
        if (self.index>len(self.list)):
            return 0 
         
               
        
  
        return 1
 