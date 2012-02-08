'''
Created on 23/01/2012

@author: danielangelsuarezmunoz
'''


import os, sys
import numpy
import glob
import fnmatch
import time
import datetime

from Header import *
from Data import DataReader
from Data import DataWriter

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from Model.Voltage import Voltage

class VoltageReader(DataReader):
    
    __idFile = None
    
    __fp = None
    
    __startDateTime = None
    
    __endDateTime = None
    
    __dataType = None
    
    __fileSizeByHeader = 0
    
    __pathList = []
    
    filenameList = []
    
    __lastUTTime = 0
    
    __maxTimeStep = 5 
    
    flagResetProcessing = 0
    
    __flagIsNewFile = 0
    
    noMoreFiles = 0
    
    online = 0
    
    filename = None
    
    fileSize = None
    
    firstHeaderSize = 0
    
    basicHeaderSize = 24
    
    m_BasicHeader = BasicHeader()
    
    m_SystemHeader = SystemHeader()
    
    m_RadarControllerHeader = RadarControllerHeader()
    
    m_ProcessingHeader = ProcessingHeader()
    
    m_Voltage = None
    
    __buffer = 0
    
    __buffer_id = 9999
     
    def __init__(self, m_Voltage = None):
        
        if m_Voltage == None:
            m_Voltage = Voltage()
            
        self.m_Voltage = m_Voltage
    
    def __rdSystemHeader(self,fp=None):
        if fp == None:
            fp = self.__fp
            
        self.m_SystemHeader.read(fp)
    
    def __rdRadarControllerHeader(self,fp=None):
        if fp == None:
            fp = self.__fp
            
        self.m_RadarControllerHeader.read(fp)
        
    def __rdProcessingHeader(self,fp=None):
        if fp == None:
            fp = self.__fp
            
        self.m_ProcessingHeader.read(fp)
        
    def __searchFiles(self,path, startDateTime, endDateTime, set=None, expLabel = "", ext = ".r"):
        
        print "Searching files ..."
        
        startUtSeconds = time.mktime(startDateTime.timetuple())
        endUtSeconds = time.mktime(endDateTime.timetuple())
        
#        startYear = startDateTime.timetuple().tm_year 
#        endYear = endDateTime.timetuple().tm_year
#        
#        startDoy = startDateTime.timetuple().tm_yday
#        endDoy = endDateTime.timetuple().tm_yday
#        
#        yearRange = range(startYear,endYear+1)
#        
#        doyDoubleList = []
#        if startYear == endYear:
#            doyList = range(startDoy,endDoy+1)
#        else:
#            for year in yearRange:
#                if (year == startYear):
#                    doyDoubleList.append(range(startDoy,365+1))
#                elif (year == endYear): 
#                    doyDoubleList.append(range(1,endDoy+1))
#                else:
#                    doyDoubleList.append(range(1,365+1)) 
#            doyList = []
#            for list in doyDoubleList:
#                doyList = doyList + list
#            
#        dirList = []
#        for thisPath in os.listdir(path):
#            if os.path.isdir(os.path.join(path,thisPath)):
#                #dirList.append(os.path.join(path,thisPath))
#                dirList.append(thisPath)
#        
#        pathList = []
#        pathDict = {}
#        for year in yearRange:
#            for doy in doyList:        
#                match = fnmatch.filter(dirList, 'D' + '%4.4d%3.3d' % (year,doy))
#                if len(match) == 0:
#                    match = fnmatch.filter(dirList, 'd' + '%4.4d%3.3d' % (year,doy))
#                    if len(match) == 0: continue
#                if expLabel == '':
#                    pathList.append(os.path.join(path,match[0]))
#                    pathDict.setdefault(os.path.join(path,match[0]))
#                    pathDict[os.path.join(path,match[0])] = []
#                else:
#                    pathList.append(os.path.join(path,os.path.join(match[0],expLabel)))
#                    pathDict.setdefault(os.path.join(path,os.path.join(match[0],expLabel)))
#                    pathDict[os.path.join(path,os.path.join(match[0],expLabel))] = []
        

        dirList = []
        for thisPath in os.listdir(path):
            if os.path.isdir(os.path.join(path,thisPath)):
                dirList.append(thisPath)

        pathList = []
        
        thisDateTime = startDateTime
        
        while(thisDateTime <= endDateTime):
            year = thisDateTime.timetuple().tm_year
            doy = thisDateTime.timetuple().tm_yday
            
            match = fnmatch.filter(dirList, '?' + '%4.4d%3.3d' % (year,doy))
            if len(match) == 0:
                thisDateTime += datetime.timedelta(1)
                continue
            
            pathList.append(os.path.join(path,match[0],expLabel))
            thisDateTime += datetime.timedelta(1)
                
        filenameList = []
        for thisPath in pathList:
            fileList = glob.glob1(thisPath, "*%s" %ext)
            #pathDict[thisPath].append(fileList)
            fileList.sort()
            for file in fileList:
                filename = os.path.join(thisPath,file)
                if self.isThisFileinRange(filename, startUtSeconds, endUtSeconds):
                    filenameList.append(filename)
                    
        self.filenameList = filenameList
        
        return pathList, filenameList

    def isThisFileinRange(self, filename, startUTSeconds=None, endUTSeconds=None):
        
        try:
            fp = open(filename,'rb')
        except:
            raise IOError, "The file %s can't be opened" %(filename)
        
        if startUTSeconds==None:
            startUTSeconds = self.startUTCSeconds
        
        if endUTSeconds==None:
            endUTSeconds = self.endUTCSeconds
            
        m_BasicHeader = BasicHeader()
        
        if not(m_BasicHeader.read(fp)):
            return 0
        
        fp.close()
        
        if not ((startUTSeconds <= m_BasicHeader.utc) and (endUTSeconds >= m_BasicHeader.utc)):
            return 0
        
        return 1
    
    def __readBasicHeader(self, fp=None):
        
        if fp == None:
            fp = self.__fp
            
        self.m_BasicHeader.read(fp)
    
    def __readFirstHeader(self):
        
        self.__readBasicHeader()
        self.__rdSystemHeader()
        self.__rdRadarControllerHeader()
        self.__rdProcessingHeader()
        self.firstHeaderSize = self.m_BasicHeader.size
        
        data_type=int(numpy.log2((self.m_ProcessingHeader.processFlags & PROCFLAG.DATATYPE_MASK))-numpy.log2(PROCFLAG.DATATYPE_CHAR))
        if data_type == 0:
            tmp=numpy.dtype([('real','<i1'),('imag','<i1')])
        elif data_type == 1:
            tmp=numpy.dtype([('real','<i2'),('imag','<i2')])
        elif data_type == 2:
            tmp=numpy.dtype([('real','<i4'),('imag','<i4')])
        elif data_type == 3:
            tmp=numpy.dtype([('real','<i8'),('imag','<i8')])
        elif data_type == 4:
            tmp=numpy.dtype([('real','<f4'),('imag','<f4')])
        elif data_type == 5:
            tmp=numpy.dtype([('real','<f8'),('imag','<f8')])
        else:
            print 'no define data type'
            tmp = 0
        
        self.__dataType = tmp
        self.__fileSizeByHeader = self.m_ProcessingHeader.dataBlocksPerFile * self.m_ProcessingHeader.blockSize + self.firstHeaderSize + self.basicHeaderSize*(self.m_ProcessingHeader.dataBlocksPerFile - 1)        

    def __setNextFileOnline(self):
        return 0

    def __setNextFileOffline(self):
        
        idFile = self.__idFile
        while(True):
            
            idFile += 1
            
            if not(idFile < len(self.filenameList)):
                self.noMoreFiles = 1
                return 0
            
            filename = self.filenameList[idFile]
            fileSize = os.path.getsize(filename)
            fp = open(filename,'rb')
            
            currentSize = fileSize - fp.tell()
            neededSize = self.m_ProcessingHeader.blockSize + self.firstHeaderSize
            
            if (currentSize < neededSize):
                continue
            
            break
        
        self.__flagIsNewFile = 1
        self.__idFile = idFile
        self.filename = filename
        self.fileSize = fileSize
        self.__fp = fp
        
        print 'Setting the file: %s'%self.filename
        
        return 1

    def __setNextFile(self):
        
        if self.online:
            return self.__setNextFileOnline()
        else:
            return self.__setNextFileOffline()
    
    def __setNewBlock(self):
        
        if self.__fp == None:
            return 0
            
        if self.__flagIsNewFile:
            return 1
        
        currentSize = self.fileSize - self.__fp.tell()
        neededSize = self.m_ProcessingHeader.blockSize + self.basicHeaderSize
        
        # Bloque Completo
        if (currentSize >= neededSize):
            self.__readBasicHeader()
            return 1
        
        if not(self.__setNextFile()):
            return 0
        
        self.__readFirstHeader()
        
        deltaTime = self.m_BasicHeader.utc - self.__lastUTTime # check this
        
        self.flagResetProcessing = 0
        if deltaTime > self.__maxTimeStep:
            self.flagResetProcessing = 1
            
        return 1
    
    def __readBlock(self):
        """Lee el bloque de datos desde la posicion actual del puntero del archivo y
        actualiza todos los parametros relacionados al bloque de datos (data, time,
        etc). La data leida es almacenada en el buffer y el contador de datos leidos es
        seteado a 0
        """
        
        pts2read = self.m_ProcessingHeader.profilesPerBlock*self.m_ProcessingHeader.numHeights*self.m_SystemHeader.numChannels
        
        data = numpy.fromfile(self.__fp,self.__dataType,pts2read)
        
        data = data.reshape((self.m_ProcessingHeader.profilesPerBlock, self.m_ProcessingHeader.numHeights, self.m_SystemHeader.numChannels))
        
        self.__flagIsNewFile = 0
        
        self.__buffer = data
        
        self.__buffer_id = 0
        
    def readNextBlock(self):

        if not(self.__setNewBlock()):
            return 0
             
        self.__readBlock()
        
        self.__lastUTTime = self.m_BasicHeader.utc
        
        return 1
 
    def __hasNotDataInBuffer(self):
        if self.__buffer_id >= self.m_ProcessingHeader.profilesPerBlock:
            return 1
        
        return 0

    def getData(self):
        """Obtiene un unidad de datos del buffer de lectura y es copiada a la clase "Voltage"
        con todos los parametros asociados a este. cuando no hay datos en el buffer de
        lectura es necesario hacer una nueva lectura de los bloques de datos usando "readNextBlock"
        """
        self.flagResetProcessing = 0
        
        if self.__hasNotDataInBuffer():            
            self.readNextBlock() 
        
        if self.noMoreFiles == 1:
            print 'Process finished'
            return None
        
        data = self.__buffer[self.__buffer_id,:,:]
        time = 111
        
#        self.m_Voltage.data = data
#        self.m_Voltage.timeProfile = time
#        self.m_Voltage.m_BasicHeader = self.m_BasicHeader.copy()
#        self.m_Voltage.m_ProcessingHeader = self.m_ProcessingHeader.copy()
#        self.m_Voltage.m_RadarControllerHeader = self.m_RadarControllerHeader.copy()
#        self.m_Voltage.m_SystemHeader = self.m_systemHeader.copy()
        
        self.__buffer_id += 1
        
        #call setData - to Data Object
    
        return data


    def setup(self, path, startDateTime, endDateTime, set=None, expLabel = "", ext = ".r", online = 0):
        
        if online == 0:
            pathList, filenameList = self.__searchFiles(path, startDateTime, endDateTime, set, expLabel, ext)
            
            if len(filenameList) == 0:
                self.__fp = None
                self.noMoreFiles = 1
                print 'Do not exist files in range: %s - %s'%(startDateTime.ctime(), endDateTime.ctime())
                return 0
    
#        for thisFile in filenameList:
#            print thisFile
        
        self.__idFile = -1
        
        if not(self.__setNextFile()):
            print "No more files"
            return 0
        
        self.__readFirstHeader()
        
        self.startUTCSeconds = time.mktime(startDateTime.timetuple())
        self.endUTCSeconds = time.mktime(endDateTime.timetuple())
        
        self.startYear = startDateTime.timetuple().tm_year 
        self.endYear = endDateTime.timetuple().tm_year
        
        self.startDoy = startDateTime.timetuple().tm_yday
        self.endDoy = endDateTime.timetuple().tm_yday
        #call fillHeaderValues() - to Data Object
            
        self.__pathList = pathList
        self.filenameList = filenameList 
        self.online = online

class VoltageWriter(DataWriter):
    
    m_BasicHeader= BasicHeader()


    m_SystemHeader = SystemHeader()


    m_RadarControllerHeader = RadarControllerHeader()


    m_ProcessingHeader = ProcessingHeader()

    m_Voltage = None
    
    def __init__(self, m_Voltage):
        
        self.m_Voltage = m_Voltage


    