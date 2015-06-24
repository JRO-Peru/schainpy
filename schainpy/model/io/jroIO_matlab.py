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
from astropy.io.ascii.tests.test_connect import files

#         Path needs to be whereever the matlab data files are stored. 
#         This program works by reading how many data folders remain inside of the 
#         path destination. Every iteration of the program it will re-search 
#         the path destination, if new folder(s) are detected, it will read
#         in all data from say... enough files to cover an hour and generate 
#         spectra and RTI plots.

class MatReader(ProcessingUnit):
    
    index=None
    list=None
    firsttime=True
    utccounter=None
    utcfiletime=None
    utcmatcounter=0
    utcfirst=None
    utclist=None
    foldercountercrosscheck=None
    foldercountercheck=None
    indexfirsttime=-31
    
    def __init__(self):
        self.dataOut = Spectra()
        return
    
#     def FIRSTTIMERUNTHROUGH(self,path=None,startDate=None, endDate=None,startTime=datetime.time(0,0,0),
#         endTime=datetime.time(23,59,59),walk=True,timezone='ut',
#         all=0,online=True,ext=None,filelist=None, **kwargs):
#         
#         foldcountercrosscheck=0
#         self.foldercountercrosscheck=foldcountercrosscheck
#         
#         for g in range(len(filelist)):
#             strsplit=filelist[g].split('.')
#             timeints=[int(i) for i in strsplit]
#             timelist=datetime.datetime(timeints[0],timeints[1],timeints[2],timeints[3],timeints[4],timeints[5])
#             utctime=(timelist-datetime.datetime(1970,1,1)).total_seconds()
#             secondlist.append(filelist[g])
#             self.utclist.append(utctime)
#         
#         for k in range(len(secondlist)):
#             
#             path1=os.path.join(self.path,secondlist[k])
#             filecounter=len([name for name in os.listdir(path1)])
# #               print "Reading from this dir:" +path1
#             for r in range(filecounter):
#                 matname=str(r)+'.mat'
#                 bork=os.path.join(path1,matname)
# #  thirdlist is what ends up being the list to all matlab files
#                 thirdlist.append(os.path.join(path1,matname))
#                 
#             self.utcfirst=utclist[-1]       
#             self.index=-31
#             self.list=thirdlist
#             
#         while (self.index <= -1):   
#             currentfilenewest=self.list[self.index]
#             print "Reading from this file:" + currentfilenewest 
#             filesplit=currentfilenewest.split("\\")
#             newsplit=filesplit[-2]
#             newnewsplit=newsplit.split(".")
#             newnewsplit=[int(i) for i in newnewsplit]
#             gooblist=datetime.datetime(newnewsplit[0],newnewsplit[1],newnewsplit[2],newnewsplit[3],newnewsplit[4],newnewsplit[5])
#             self.utcfirst=(gooblist-datetime.datetime(1970,1,1)).total_seconds()
#             
#             
#             newsplit=filesplit[-1]
#             newnewsplit=newsplit.split(".")
#             goobnum=newnewsplit[0]
#             goobnum=int(goobnum)
#             
#             self.utcfirst=self.utcfirst+goobnum*2
#             print self.utcfirst
#             
#             datastuff=sio.loadmat(currentfilenewest)
#             dataphase=datastuff.get('phase')
#             data3=datastuff.get('doppler0')
#             data4=datastuff.get('doppler1')
#             data3= np.array(data3)
#             data4 = np.array(data4)
#             datacoh=datastuff.get('coherence2')
#             
#             datacohphase=datacoh*np.exp(-dataphase*1j)
#     #         data31 = np.fliplr(data3)
#     #         data41 = np.fliplr(data4)
#               
#             data31 = data3.reshape((1,data3.shape[0],data3.shape[1]))
#             data41 = data4.reshape((1,data4.shape[0],data4.shape[1]))
#             datacohphase1 = datacohphase.reshape((1,datacoh.shape[0],datacoh.shape[1]))
#             
#             datastack = np.vstack((data31,data41))
#             
#             self.dataOut.pairsList=[(0,1)]
#             self.dataOut.data_cspc=datacohphase1.copy()
#             self.dataOut.data_spc = datastack.copy()
#             self.dataOut.channelList = range(2)
#             self.dataOut.nProfiles = 25 #this!
#             self.dataOut.nIncohInt = 1
#             self.dataOut.nCohInt = 1 #this!
#             self.dataOut.ippSeconds = 0.004 #this!
#             self.dataOut.nFFTPoints = 25
#             self.dataOut.utctime = self.utcfirst
#             self.dataOut.heightList = np.array(datastuff.get('hts'))
#             
#             self.dataOut.flagNoData = False  
#             
#             self.firsttime=False
#         
#             self.index+=1
#         
#         
#         return foldercountercrosscheck, self.firsttime
    
    def run(self,path=None,startDate=None, endDate=None,startTime=datetime.time(0,0,0),
            endTime=datetime.time(23,59,59),walk=True,timezone='ut',
            all=0,online=True,ext=None, **kwargs):
        
        self.path=path
        self.ext=ext
        self.startDate=startDate
        self.endDate=endDate
        self.startTime=startTime
        self.endTime=endTime
        self.index=0
        
        filelist = [ f for f in listdir(path)]
        secondlist=[]
        thirdlist=[]
        utclist=[]
        foldercountercheck=len([name for name in os.listdir(self.path)])
        
# ______________________________________________________________________________________________________________________________________________________________-         
#         First time through this acts much like the offline program,
#         It reads in the latest file in the path to create a list. So, it finds
#         the very last folder in the path, opens it and reads in the 30 matlab files
#         inside of that. Then, this loop never runs again.


        if (self.firsttime==True):
#             self.FIRSTTIMERUNTHROUGH(path, self.startDate, self.endDate, self.startTime, 
#                                      self.endTime, walk, timezone, all, online, ext,filelist)
            foldercountercrosscheck=0
            self.utclist=utclist
            
            
            for g in range(len(filelist)):
                strsplit=filelist[g].split('.')
                timeints=[int(i) for i in strsplit]
                timelist=datetime.datetime(timeints[0],timeints[1],timeints[2],timeints[3],timeints[4],timeints[5])
                utctime=(timelist-datetime.datetime(1970,1,1)).total_seconds()
                secondlist.append(filelist[g])
                self.utclist.append(utctime)
             
            for k in range(len(secondlist)):
                 
                path1=os.path.join(self.path,secondlist[k])
                filecounter=len([name for name in os.listdir(path1)])
#               print "Reading from this dir:" +path1
                for r in range(filecounter):
                    matname=str(r)+'.mat'
                    bork=os.path.join(path1,matname)
#  thirdlist is what ends up being the list to all matlab files
                    thirdlist.append(os.path.join(path1,matname))
            
# Set the index to -31 initially such that it reads the final 30 matlab files in the 
# path for the first iteration. It gets reset in the continually checking portion.

            self.utcfirst=utclist[-1]       
            self.list=thirdlist
               
            currentfilenewest=self.list[self.indexfirsttime]
            print "Reading from this file:" + currentfilenewest
            filesplit=currentfilenewest.split("\\")
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
            print self.utcfirst
             
            datastuff=sio.loadmat(currentfilenewest)
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
            self.indexfirsttime+=1
            
            if (self.indexfirsttime>=30):
                self.firsttime=False
                self.index=0
         
            
#         
        
        
        
# __________________________________________________________________________________________________________________________________________________________-
    
            
# Now we check for new folders, if some are detected, we repeat the process
        self.firsttime=False

        if(foldercountercheck>foldercountercrosscheck):
            foldercountercrosscheck=foldercountercheck
            

            for g in range(len(filelist)):
                strsplit=filelist[g].split('.')
                timeints=[int(i) for i in strsplit]
                timelist=datetime.datetime(timeints[0],timeints[1],timeints[2],timeints[3],timeints[4],timeints[5])
                utctime=(timelist-datetime.datetime(1970,1,1)).total_seconds()
                secondlist.append(filelist[g])
                self.utclist.append(utctime)
             
            for k in range(len(secondlist)):
                 
                path1=os.path.join(self.path,secondlist[k])
                filecounter=len([name for name in os.listdir(path1)])
#               print "Reading from this dir:" +path1
                for r in range(filecounter):
                    matname=str(r)+'.mat'
                    bork=os.path.join(path1,matname)
#  thirdlist is what ends up being the list to all matlab files
                    thirdlist.append(os.path.join(path1,matname))
            
# Set the index to -31 initially such that it reads the final 30 matlab files in the 
# path for the first iteration. It gets reset in the continually checking portion.

            self.utcfirst=utclist[-1]       
            self.list=thirdlist
               
            currentfilenewest=self.list[self.indexfirsttime]
            print "Reading from this file:" + currentfilenewest
            filesplit=currentfilenewest.split("\\")
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
            print "The utc of the file is:" + self.utcfirst
             
            datastuff=sio.loadmat(currentfilenewest)
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
            self.indexfirsttime+=1
            
            if (self.indexfirsttime>=30):
                self.firsttime=False
                self.index=0

        else:
            time.sleep(15)

        return 1