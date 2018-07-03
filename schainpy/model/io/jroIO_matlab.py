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
        self.online = False
        return
    
    def __setHeader(self, datastuff):
        
        self.dataOut.pairsList=[(0,1)]
        self.dataOut.channelList =  list(range(np.array(datastuff.get('power')).shape[1]))
        self.dataOut.nProfiles = len(np.array(datastuff.get('vel')).flatten())     #this!
        self.dataOut.nIncohInt = 20
        self.dataOut.nCohInt = 1 #this!
        self.dataOut.ippSeconds = 0.004 #this!
        self.dataOut.nFFTPoints = len(np.array(datastuff.get('vel')).flatten())    
        self.dataOut.timeZone = 0
        self.dataOut.heightList = np.array(datastuff.get('hts')).flatten()
    
    def __readFile(self, currentfile):
        print("Reading from this file:" + currentfile)
        
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
        print(self.utcfirst)
        try:
            datastuff=sio.loadmat(currentfile)
        except:
            return None, None
        
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
        
        self.__setHeader(datastuff)
        
        spc = datastack
        cspc = datacohphase1
        
        return spc, cspc
    
    def __findFiles(self, path, startDate=None, endDate=None,startTime=datetime.time(0,0,0), endTime=datetime.time(23,59,59)):
        
        if startDate == None:
            startDate = datetime.date(1970,1,1)
            
        if endDate == None:
            endDate = datetime.date(2050,1,1)
            
        startsearch1=datetime.datetime.combine(startDate,startTime)
        startsearch2=(startsearch1-datetime.datetime(1970,1,1)).total_seconds()
        endsearch1=datetime.datetime.combine(endDate,endTime)
        endsearch2=(endsearch1-datetime.datetime(1970,1,1)).total_seconds()
        
        dirList = listdir(path)
        dirList = sorted(dirList)
        
        dirListFiltered=[]
        fileListFiltered=[]
        utclist=[]
        
        if not dirList:
            print("No directories found")
            return []
        
        #if self.online:
        #    dirList= [dirList[-1]]
         
        if self.online:
            currentdate = datetime.datetime.now()
            strsplit1=currentdate.strftime('%Y.%m.%d')
            dirList = fnmatch.filter(dirList,strsplit1+'*')  
        
        for thisDir in dirList:
            if not os.path.isdir(os.path.join(path, thisDir)):
                continue
            
            strsplit=thisDir.split('.')
            timeints=[int(i) for i in strsplit]
            timelist=datetime.datetime(timeints[0],timeints[1],timeints[2],timeints[3],timeints[4],timeints[5])
            utctime=(timelist-datetime.datetime(1970,1,1)).total_seconds()
            
            if not self.online:
                if (utctime > endsearch2):
                    continue
                
                if (utctime < startsearch2):
                    continue
            
            dirListFiltered.append(thisDir)
            utclist.append(utctime)
        
        if not dirListFiltered:
            print("filtro")
            return []
        
        for thisDir in dirListFiltered:
            
            pathFile = os.path.join(self.path, thisDir)
            
            fileList = os.listdir(pathFile)
            
            if not fileList:
                continue
            
            for k in range(len(fileList)):
                thisFile = str(k)+'.mat'
                
                if not os.path.isfile(os.path.join(pathFile, thisFile)):
                    continue
                
                fileListFiltered.append(os.path.join(pathFile, thisFile))
                    
        return fileListFiltered
    
    def __getNextOnlineFile(self, seconds = 40):
        
        filename = self.__getNextOfflineFile()
        
        if filename:
            return filename
        
        ncurrentfiles = len(self.fileList)
        
        nTries = 0
        while (True):
            filelist = self.__findFiles(self.path)
            if len(filelist) > ncurrentfiles:
                break

            nTries += 1
            
            if nTries > 3:
                break
            
            print("Waiting %d seconds ..." %seconds)
            time.sleep(40)
        
        if not (len(filelist) > ncurrentfiles):
            return None
        
        self.fileList = filelist
        filename = self.__getNextOfflineFile()
        
        return filename
    
    def __getNextOfflineFile(self):
        
        if self.index >= len(self.fileList):
            return None
         
        filename=self.fileList[self.index]
        self.index += 1
        return filename
    
    def __getNextFile(self):
        
        if self.online:
            filename = self.__getNextOnlineFile()
        else:
            filename = self.__getNextOfflineFile()   
        return filename
    
    def setup(self, path, startDate=None, endDate=None,startTime=datetime.time(0,0,0), endTime=datetime.time(23,59,59)):
        
        fileList = self.__findFiles(path, startDate, endDate, startTime, endTime)
        
        if self.online:
            self.index = len(fileList) -1
        else:
            self.index = 0
            
        self.fileList = fileList
        
        print("fin setup")
    
    def run(self,path=None,startDate=None, endDate=None,
            startTime=datetime.time(0,0,0),
            endTime=datetime.time(23,59,59),
            walk=True,timezone='ut',
            all=0,online=False,ext=None,**kwargs):
        
        self.path=path
        self.ext=ext
        self.startDate=startDate
        self.endDate=endDate
        self.startTime=startTime
        self.endTime=endTime
        self.online = online
        self.dataOut.flagNoData = True  
        
        if (self.firsttime==True):
            self.setup(path, startDate, endDate, startTime, endTime)      
            self.firsttime=False
            
        
        if not self.fileList:
            self.dataOut.flagNoData = True
            print("lista vacia")
            return
        
        currentfile = self.__getNextFile()
        
        if not currentfile:
            "no file"
            return
        
        spc, cspc = self.__readFile(currentfile)
        
        if spc!=None:
            
            self.dataOut.data_spc = spc
            self.dataOut.data_cspc = cspc
            self.dataOut.utctime = self.utcfirst
            self.dataOut.flagNoData = False  
  
        return 1
 