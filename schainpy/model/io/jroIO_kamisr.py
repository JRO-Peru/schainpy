'''
Created on Set 9, 2015

@author: roj-idl71 Karim Kuyeng
'''

import os
import sys
import glob
import fnmatch
import datetime
import time
import re
import h5py
import numpy

try:
    from gevent import sleep
except:
    from time import sleep

from schainpy.model.data.jroheaderIO import RadarControllerHeader, SystemHeader
from schainpy.model.data.jrodata import Voltage
from schainpy.model.proc.jroproc_base import ProcessingUnit, Operation
from numpy import imag

class AMISRReader(ProcessingUnit):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
        ProcessingUnit.__init__(self)
        
        self.set = None
        self.subset = None
        self.extension_file = '.h5'
        self.dtc_str = 'dtc'
        self.dtc_id = 0
        self.status = True
        self.isConfig = False
        self.dirnameList = []
        self.filenameList = []
        self.fileIndex = None
        self.flagNoMoreFiles = False
        self.flagIsNewFile = 0
        self.filename = ''
        self.amisrFilePointer = None
        
        
        self.dataset = None
        
        
       

        self.profileIndex = 0
        
        
        self.beamCodeByFrame = None
        self.radacTimeByFrame = None
        
        self.dataset = None
        
             
                
        
        self.__firstFile = True
        
        self.buffer = None
        
        
        self.timezone = 'ut'
        
        self.__waitForNewFile = 20
        self.__filename_online = None 
        #Is really necessary create the output object in the initializer
        self.dataOut = Voltage()
        
    def setup(self,path=None,
                    startDate=None, 
                    endDate=None, 
                    startTime=None, 
                    endTime=None,
                    walk=True,
                    timezone='ut',
                    all=0,
                    code = None,
                    nCode = 0,
                    nBaud = 0,
                    online=False):
    
        self.timezone = timezone
        self.all = all
        self.online = online
        
        self.code = code
        self.nCode = int(nCode)
        self.nBaud = int(nBaud)
        
        
        
        #self.findFiles()
        if not(online):
            #Busqueda de archivos offline
            self.searchFilesOffLine(path, startDate, endDate, startTime, endTime, walk)
        else:
            self.searchFilesOnLine(path, startDate, endDate, startTime,endTime,walk)
        
        if not(self.filenameList):
            print("There is no files into the folder: %s"%(path))
                
            sys.exit(-1)
            
        self.fileIndex = -1
        
        self.readNextFile(online)   
               
        '''
        Add code
        '''        
        self.isConfig = True
        
        pass
    
    
    def readAMISRHeader(self,fp):
        header = 'Raw11/Data/RadacHeader'
        self.beamCodeByPulse = fp.get(header+'/BeamCode') # LIST OF BEAMS PER PROFILE, TO BE USED ON REARRANGE
        self.beamCode = fp.get('Raw11/Data/Beamcodes') # NUMBER OF CHANNELS AND IDENTIFY POSITION TO CREATE A FILE WITH THAT INFO
        #self.code = fp.get(header+'/Code') # NOT USE FOR THIS
        self.frameCount = fp.get(header+'/FrameCount')# NOT USE FOR THIS
        self.modeGroup = fp.get(header+'/ModeGroup')# NOT USE FOR THIS
        self.nsamplesPulse = fp.get(header+'/NSamplesPulse')# TO GET NSA OR USING DATA FOR THAT
        self.pulseCount = fp.get(header+'/PulseCount')# NOT USE FOR THIS
        self.radacTime = fp.get(header+'/RadacTime')# 1st TIME ON FILE ANDE CALCULATE THE REST WITH IPP*nindexprofile
        self.timeCount = fp.get(header+'/TimeCount')# NOT USE FOR THIS
        self.timeStatus = fp.get(header+'/TimeStatus')# NOT USE FOR THIS
        self.rangeFromFile = fp.get('Raw11/Data/Samples/Range')
        self.frequency =  fp.get('Rx/Frequency')
        txAus = fp.get('Raw11/Data/Pulsewidth')
         
        
        self.nblocks = self.pulseCount.shape[0] #nblocks
       
        self.nprofiles = self.pulseCount.shape[1] #nprofile
        self.nsa = self.nsamplesPulse[0,0] #ngates
        self.nchannels = self.beamCode.shape[1]
        self.ippSeconds = (self.radacTime[0][1] -self.radacTime[0][0]) #Ipp in seconds
        #self.__waitForNewFile = self.nblocks  # wait depending on the number of blocks since each block is 1 sec
        self.__waitForNewFile = self.nblocks * self.nprofiles * self.ippSeconds # wait until new file is created
        
        #filling radar controller header parameters
        self.__ippKm = self.ippSeconds *.15*1e6 # in km
        self.__txA = (txAus.value)*.15 #(ipp[us]*.15km/1us) in km
        self.__txB = 0
        nWindows=1
        self.__nSamples = self.nsa 
        self.__firstHeight = self.rangeFromFile[0][0]/1000 #in km
        self.__deltaHeight = (self.rangeFromFile[0][1] - self.rangeFromFile[0][0])/1000 
        
        #for now until understand why the code saved is different (code included even though code not in tuf file)
        #self.__codeType = 0
       # self.__nCode = None
       # self.__nBaud = None
        self.__code = self.code
        self.__codeType = 0
        if self.code != None:
            self.__codeType = 1
        self.__nCode = self.nCode
        self.__nBaud = self.nBaud
        #self.__code = 0
        
        #filling system header parameters
        self.__nSamples = self.nsa
        self.newProfiles = self.nprofiles/self.nchannels 
        self.__channelList = list(range(self.nchannels))
        
        self.__frequency = self.frequency[0][0]
        

    
    def createBuffers(self):
    
        pass      
       
    def __setParameters(self,path='', startDate='',endDate='',startTime='', endTime='', walk=''):
        self.path = path
        self.startDate = startDate
        self.endDate = endDate
        self.startTime = startTime
        self.endTime = endTime
        self.walk = walk
    
    def __checkPath(self):
        if os.path.exists(self.path):
            self.status = 1
        else:
            self.status = 0
            print('Path:%s does not exists'%self.path)
            
        return
    
    
    def __selDates(self, amisr_dirname_format):
        try:
            year = int(amisr_dirname_format[0:4])
            month = int(amisr_dirname_format[4:6])
            dom = int(amisr_dirname_format[6:8])
            thisDate = datetime.date(year,month,dom)
            
            if (thisDate>=self.startDate and thisDate <= self.endDate):
                return amisr_dirname_format
        except:
            return None
    
    
    def __findDataForDates(self,online=False):
        
        if not(self.status):
            return None
        
        pat = '\d+.\d+'
        dirnameList = [re.search(pat,x) for x in os.listdir(self.path)]
        dirnameList = [x for x in dirnameList if x!=None]
        dirnameList = [x.string for x in dirnameList]
        if not(online):
            dirnameList = [self.__selDates(x) for x in dirnameList]
            dirnameList = [x for x in dirnameList if x!=None]
        if len(dirnameList)>0:
            self.status = 1
            self.dirnameList = dirnameList
            self.dirnameList.sort()
        else:
            self.status = 0
            return None
    
    def __getTimeFromData(self):
        startDateTime_Reader = datetime.datetime.combine(self.startDate,self.startTime)
        endDateTime_Reader = datetime.datetime.combine(self.endDate,self.endTime)

        print('Filtering Files from %s to %s'%(startDateTime_Reader, endDateTime_Reader))
        print('........................................')
        filter_filenameList = []
        self.filenameList.sort()
        #for i in range(len(self.filenameList)-1):
        for i in range(len(self.filenameList)):
            filename = self.filenameList[i]
            fp = h5py.File(filename,'r')
            time_str = fp.get('Time/RadacTimeString')
            
            startDateTimeStr_File = time_str[0][0].split('.')[0]
            junk = time.strptime(startDateTimeStr_File, '%Y-%m-%d %H:%M:%S')
            startDateTime_File = datetime.datetime(junk.tm_year,junk.tm_mon,junk.tm_mday,junk.tm_hour, junk.tm_min, junk.tm_sec)
            
            endDateTimeStr_File = time_str[-1][-1].split('.')[0]
            junk = time.strptime(endDateTimeStr_File, '%Y-%m-%d %H:%M:%S')
            endDateTime_File = datetime.datetime(junk.tm_year,junk.tm_mon,junk.tm_mday,junk.tm_hour, junk.tm_min, junk.tm_sec)
            
            fp.close()
            
            if self.timezone == 'lt':
                startDateTime_File = startDateTime_File - datetime.timedelta(minutes = 300)
                endDateTime_File = endDateTime_File - datetime.timedelta(minutes = 300)

            if (endDateTime_File>=startDateTime_Reader and endDateTime_File<endDateTime_Reader):
                #self.filenameList.remove(filename)
                filter_filenameList.append(filename)
            
            if (endDateTime_File>=endDateTime_Reader):
                break
            
        
        filter_filenameList.sort()
        self.filenameList = filter_filenameList
        return 1
    
    def __filterByGlob1(self, dirName):
        filter_files = glob.glob1(dirName, '*.*%s'%self.extension_file)
        filter_files.sort()
        filterDict = {}
        filterDict.setdefault(dirName)
        filterDict[dirName] = filter_files
        return filterDict
    
    def __getFilenameList(self, fileListInKeys, dirList):
        for value in fileListInKeys:
            dirName = list(value.keys())[0]
            for file in value[dirName]:
                filename = os.path.join(dirName, file)
                self.filenameList.append(filename)
    
    
    def __selectDataForTimes(self, online=False):
        #aun no esta implementado el filtro for tiempo
        if not(self.status):
            return None
        
        dirList = [os.path.join(self.path,x) for x in self.dirnameList]
        
        fileListInKeys = [self.__filterByGlob1(x) for x in dirList]
        
        self.__getFilenameList(fileListInKeys, dirList)
        if not(online):
            #filtro por tiempo
            if not(self.all):
                self.__getTimeFromData()

            if len(self.filenameList)>0:
                self.status = 1
                self.filenameList.sort()
            else:
                self.status = 0
                return None
            
        else:
            #get the last file - 1
            self.filenameList = [self.filenameList[-2]]
        
        new_dirnameList = []
        for dirname in self.dirnameList:
            junk = numpy.array([dirname in x for x in self.filenameList])
            junk_sum = junk.sum()
            if junk_sum > 0:
                new_dirnameList.append(dirname)
        self.dirnameList = new_dirnameList
        return 1
    
    def searchFilesOnLine(self, path, startDate, endDate, startTime=datetime.time(0,0,0),
                            endTime=datetime.time(23,59,59),walk=True):
        
        if endDate ==None:
         startDate = datetime.datetime.utcnow().date()
         endDate = datetime.datetime.utcnow().date()
        
        self.__setParameters(path=path, startDate=startDate, endDate=endDate,startTime = startTime,endTime=endTime, walk=walk)
        
        self.__checkPath()
        
        self.__findDataForDates(online=True)
        
        self.dirnameList = [self.dirnameList[-1]]
        
        self.__selectDataForTimes(online=True)
        
        return
        
    
    def searchFilesOffLine(self,
                            path,
                            startDate,
                            endDate,
                            startTime=datetime.time(0,0,0),
                            endTime=datetime.time(23,59,59),
                            walk=True):
        
        self.__setParameters(path, startDate, endDate, startTime, endTime, walk)
        
        self.__checkPath()
        
        self.__findDataForDates()
        
        self.__selectDataForTimes()
        
        for i in range(len(self.filenameList)):
            print("%s" %(self.filenameList[i]))
        
        return 
        
    def __setNextFileOffline(self):
        idFile = self.fileIndex

        while (True):
            idFile += 1
            if not(idFile < len(self.filenameList)):
                self.flagNoMoreFiles = 1
                print("No more Files")
                return 0

            filename = self.filenameList[idFile]

            amisrFilePointer = h5py.File(filename,'r')
            
            break

        self.flagIsNewFile = 1
        self.fileIndex = idFile
        self.filename = filename

        self.amisrFilePointer = amisrFilePointer

        print("Setting the file: %s"%self.filename)

        return 1
    
    
    def __setNextFileOnline(self):
        filename = self.filenameList[0]
        if self.__filename_online != None:
            self.__selectDataForTimes(online=True)
            filename = self.filenameList[0]
            wait = 0
            while self.__filename_online == filename:
                print('waiting %d seconds to get a new file...'%(self.__waitForNewFile))
                if wait == 5:
                    return 0
                sleep(self.__waitForNewFile)
                self.__selectDataForTimes(online=True)
                filename = self.filenameList[0]
                wait += 1
        
        self.__filename_online = filename
        
        self.amisrFilePointer = h5py.File(filename,'r')
        self.flagIsNewFile = 1
        self.filename = filename
        print("Setting the file: %s"%self.filename)
        return 1
    
    
    def readData(self):
        buffer = self.amisrFilePointer.get('Raw11/Data/Samples/Data')
        re = buffer[:,:,:,0]
        im = buffer[:,:,:,1]
        dataset = re + im*1j
        self.radacTime = self.amisrFilePointer.get('Raw11/Data/RadacHeader/RadacTime')
        timeset = self.radacTime[:,0]
        return dataset,timeset
    
    def reshapeData(self):
    #self.beamCodeByPulse, self.beamCode, self.nblocks, self.nprofiles, self.nsa, 
        channels = self.beamCodeByPulse[0,:]
        nchan = self.nchannels
        #self.newProfiles = self.nprofiles/nchan #must be defined on filljroheader
        nblocks = self.nblocks
        nsamples = self.nsa
    
        #Dimensions : nChannels, nProfiles, nSamples
        new_block = numpy.empty((nblocks, nchan, self.newProfiles, nsamples), dtype="complex64")
        ############################################
    
        for thisChannel in range(nchan):
            new_block[:,thisChannel,:,:] = self.dataset[:,numpy.where(channels==self.beamCode[0][thisChannel])[0],:]

        
        new_block = numpy.transpose(new_block, (1,0,2,3))
        new_block = numpy.reshape(new_block, (nchan,-1, nsamples))
        
        return new_block 
    
    def updateIndexes(self):
    
        pass
        
    def fillJROHeader(self):
        
        #fill radar controller header
        self.dataOut.radarControllerHeaderObj = RadarControllerHeader(ippKm=self.__ippKm,
                                                                      txA=self.__txA,
                                                                      txB=0,
                                                                      nWindows=1,
                                                                      nHeights=self.__nSamples,
                                                                      firstHeight=self.__firstHeight,
                                                                      deltaHeight=self.__deltaHeight,
                                                                      codeType=self.__codeType,
                                                                      nCode=self.__nCode, nBaud=self.__nBaud,
                                                                      code = self.__code,
                                                                      fClock=1)
    
        
        
        #fill system header
        self.dataOut.systemHeaderObj = SystemHeader(nSamples=self.__nSamples,
                                                    nProfiles=self.newProfiles,
                                                    nChannels=len(self.__channelList),
                                                    adcResolution=14,
                                                    pciDioBusWith=32)
        
        self.dataOut.type = "Voltage"
        
        self.dataOut.data = None
        
        self.dataOut.dtype = numpy.dtype([('real','<i8'),('imag','<i8')])
        
#        self.dataOut.nChannels = 0
        
#        self.dataOut.nHeights = 0
        
        self.dataOut.nProfiles = self.newProfiles*self.nblocks
        
        #self.dataOut.heightList = self.__firstHeigth + numpy.arange(self.__nSamples, dtype = numpy.float)*self.__deltaHeigth
        ranges = numpy.reshape(self.rangeFromFile.value,(-1))
        self.dataOut.heightList =  ranges/1000.0 #km
        
        
        self.dataOut.channelList = self.__channelList
        
        self.dataOut.blocksize = self.dataOut.nChannels * self.dataOut.nHeights
        
#        self.dataOut.channelIndexList = None
        
        self.dataOut.flagNoData = True
        
        #Set to TRUE if the data is discontinuous 
        self.dataOut.flagDiscontinuousBlock = False
        
        self.dataOut.utctime = None
         
        #self.dataOut.timeZone = -5 #self.__timezone/60  #timezone like jroheader, difference in minutes between UTC and localtime
        if self.timezone == 'lt':
            self.dataOut.timeZone = time.timezone / 60. #get the timezone in minutes
        else: 
            self.dataOut.timeZone = 0 #by default time is UTC

        self.dataOut.dstFlag = 0
        
        self.dataOut.errorCount = 0
        
        self.dataOut.nCohInt = 1
        
        self.dataOut.flagDecodeData = False #asumo que la data esta decodificada
    
        self.dataOut.flagDeflipData = False #asumo que la data esta sin flip
        
        self.dataOut.flagShiftFFT = False
        
        self.dataOut.ippSeconds = self.ippSeconds
        
        #Time interval between profiles 
        #self.dataOut.timeInterval = self.dataOut.ippSeconds * self.dataOut.nCohInt
        
        self.dataOut.frequency = self.__frequency
        
        self.dataOut.realtime = self.online
        pass
    
    def readNextFile(self,online=False):
        
        if not(online):
            newFile = self.__setNextFileOffline()
        else:
            newFile = self.__setNextFileOnline() 
        
        if not(newFile):
            return 0
        
        #if self.__firstFile:
        self.readAMISRHeader(self.amisrFilePointer)
        self.createBuffers()
        self.fillJROHeader()
        #self.__firstFile = False
            
        
        
        self.dataset,self.timeset = self.readData()
        
        if self.endDate!=None:
         endDateTime_Reader = datetime.datetime.combine(self.endDate,self.endTime)
         time_str = self.amisrFilePointer.get('Time/RadacTimeString')
         startDateTimeStr_File = time_str[0][0].split('.')[0]
         junk = time.strptime(startDateTimeStr_File, '%Y-%m-%d %H:%M:%S')
         startDateTime_File = datetime.datetime(junk.tm_year,junk.tm_mon,junk.tm_mday,junk.tm_hour, junk.tm_min, junk.tm_sec)
         if self.timezone == 'lt':
          startDateTime_File = startDateTime_File - datetime.timedelta(minutes = 300)
         if (startDateTime_File>endDateTime_Reader):
             return 0
        
        self.jrodataset = self.reshapeData()
        #----self.updateIndexes()
        self.profileIndex = 0
        
        return 1
    
    
    def __hasNotDataInBuffer(self):
        if self.profileIndex >= (self.newProfiles*self.nblocks):
            return 1
        return 0
            
            
    def getData(self):
        
        if self.flagNoMoreFiles:
            self.dataOut.flagNoData = True
            return 0
        
        if self.__hasNotDataInBuffer():
            if not (self.readNextFile(self.online)):
                return 0

        
        if self.dataset is None: # setear esta condicion cuando no hayan datos por leers
            self.dataOut.flagNoData = True 
            return 0
        
        #self.dataOut.data = numpy.reshape(self.jrodataset[self.profileIndex,:],(1,-1))
        
        self.dataOut.data = self.jrodataset[:,self.profileIndex,:]
        
        #self.dataOut.utctime = self.jrotimeset[self.profileIndex]
        #verificar basic header de jro data y ver si es compatible con este valor
        #self.dataOut.utctime = self.timeset + (self.profileIndex * self.ippSeconds * self.nchannels)
        indexprof = numpy.mod(self.profileIndex, self.newProfiles)
        indexblock = self.profileIndex/self.newProfiles
        #print indexblock, indexprof
        self.dataOut.utctime = self.timeset[indexblock] + (indexprof * self.ippSeconds * self.nchannels)
        self.dataOut.profileIndex = self.profileIndex
        self.dataOut.flagNoData = False
#         if indexprof == 0:
#             print self.dataOut.utctime
        
        self.profileIndex += 1
        
        return self.dataOut.data
    
       
    def run(self, **kwargs):
        '''
        This method will be called many times so here you should put all your code
        '''
        
        if not self.isConfig:
            self.setup(**kwargs)
            self.isConfig = True
            
        self.getData()
