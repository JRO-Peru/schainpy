'''
Created on 23/01/2012

@author: danielangelsuarezmunoz
'''

import numpy
import os.path
import glob
import fnmatch
import time
import datetime

from Header import *
from Data import DataReader
from Data import DataWriter

class VoltageReader(DataReader):
    # Este flag indica que la data leida no es continua
    __jumpDataFlag = False
    
    __idFile = 0
    
    __fp = 0
    
    __startDateTime = 0
    
    __endDateTime = 0
    
    __dataType = 0
    
    __sizeOfFileByHeader = 0
    
    __pathList = []
    
    filenameList = []
    
    __lastUTTime = 0
    
    __maxTimeStep = 5 
    
    __flagResetProcessing = 0
    
    __flagIsNewFile = 0
    
    noMoreFiles = 0
    
    online = 0
    
    filename = ''
    
    fileSize = 0
    
    firstHeaderSize = 0
    
    basicHeaderSize = 24
    
    objBasicHeader = BasicHeader()
    
    objSystemHeader = SystemHeader()
    
    objRadarControllerHeader = RadarControllerHeader()
    
    objProcessingHeader = ProcessingHeader()
    
    __buffer = 0
    
    __buffer_id = 9999
    m_Voltage= Voltage()

                    
    def __init__(self):
        pass
    
    def __rdSystemHeader(self,fp=None):
        if fp == None:
            fp = self.__fp
            
        self.objSystemHeader.read(fp)
    
    def __rdRadarControllerHeader(self,fp=None):
        if fp == None:
            fp = self.__fp
            
        self.objRadarControllerHeader.read(fp)
        
    def __rdProcessingHeader(self,fp=None):
        if fp == None:
            fp = self.__fp
            
        self.objProcessingHeader.read(fp)
        
    def __searchFiles(self,path, startDateTime, endDateTime, set=None, expLabel = "", ext = "*.r"):
        
        startUtSeconds = time.mktime(startDateTime.timetuple())
        endUtSeconds = time.mktime(endDateTime.timetuple())
        
        startYear = startDateTime.timetuple().tm_year 
        endYear = endDateTime.timetuple().tm_year
        
        startDoy = startDateTime.timetuple().tm_yday
        endDoy = endDateTime.timetuple().tm_yday
        
        rangeOfYears = range(startYear,endYear+1)
        
        listOfListDoys = []
        if startYear == endYear:
            doyList = range(startDoy,endDoy+1)
        else:
            for year in rangeOfYears:
                if (year == startYear):
                    listOfListDoys.append(range(startDoy,365+1))
                elif (year == endYear): 
                    listOfListDoys.append(range(1,endDoy+1))
                else:
                    listOfListDoys.append(range(1,365+1)) 
            doyList = []
            for list in listOfListDoys:
                doyList = doyList + list
            
        folders = []
        for thisPath in os.listdir(path):
            if os.path.isdir(os.path.join(path,thisPath)):
                #folders.append(os.path.join(path,thisPath))
                folders.append(thisPath)
        
        pathList = []
        dicOfPath = {}
        for year in rangeOfYears:
            for doy in doyList:        
                tmp = fnmatch.filter(folders, 'D' + '%4.4d%3.3d' % (year,doy))
                if len(tmp) == 0:
                    continue
                if expLabel == '':
                    pathList.append(os.path.join(path,tmp[0]))
                    dicOfPath.setdefault(os.path.join(path,tmp[0]))
                    dicOfPath[os.path.join(path,tmp[0])] = []
                else:
                    pathList.append(os.path.join(path,os.path.join(tmp[0],expLabel)))
                    dicOfPath.setdefault(os.path.join(path,os.path.join(tmp[0],expLabel)))
                    dicOfPath[os.path.join(path,os.path.join(tmp[0],expLabel))] = []
        
        
        filenameList = []
        for thisPath in pathList:
            fileList = glob.glob1(thisPath, ext)
            #dicOfPath[thisPath].append(fileList)
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
            
        objBasicHeader = BasicHeader()
        
        if not(objBasicHeader.read(fp)):
            return 0
        
        fp.close()
        
        if not ((startUTSeconds <= objBasicHeader.utc) and (endUTSeconds >= objBasicHeader.utc)):
            return 0
        
        return 1
    
    def __readBasicHeader(self, fp=None):
        
        if fp == None:
            fp = self.__fp
            
        self.objBasicHeader.read(fp)
    
    def __readFirstHeader(self):
        
        self.__readBasicHeader()
        self.__rdSystemHeader()
        self.__rdRadarControllerHeader()
        self.__rdProcessingHeader()
        self.firstHeaderSize = self.objBasicHeader.size
        
        data_type=int(numpy.log2((self.objProcessingHeader.processFlags & PROCFLAG.DATATYPE_MASK))-numpy.log2(PROCFLAG.DATATYPE_CHAR))
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
        
        self.__flagIsNewFile = 0
        self.__dataType = tmp
        self.__sizeOfFileByHeader = self.objProcessingHeader.dataBlocksPerFile * self.objProcessingHeader.blockSize + self.firstHeaderSize + self.basicHeaderSize*(self.objProcessingHeader.dataBlocksPerFile - 1)        

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
            neededSize = self.objProcessingHeader.blockSize + self.firstHeaderSize
            
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
        
        currentSize = self.fileSize - self.__fp.tell()
        neededSize = self.objProcessingHeader.blockSize + self.basicHeaderSize
        
        # Bloque Completo
        if (currentSize >= neededSize):
            self.__readBasicHeader()
            return 1
        
        self.__setNextFile()
        self.__readFirstHeader()
        
        deltaTime = self.objBasicHeader.utc - self.__lastUTTime # check this
        if deltaTime > self.__maxTimeStep:
            self.__flagResetProcessing = 1
            
        return 1
    
    def __readBlock(self):
        """Lee el bloque de datos desde la posicion actual del puntero del archivo y
        actualiza todos los parametros relacionados al bloque de datos (data, time,
        etc). La data leida es almacenada en el buffer y el contador de datos leidos es
        seteado a 0
        """
        
        pts2read = self.objProcessingHeader.profilesPerBlock*self.objProcessingHeader.numHeights*self.objSystemHeader.numChannels
        
        data = numpy.fromfile(self.__fp,self.__dataType,pts2read)
        
        data = data.reshape((self.objProcessingHeader.profilesPerBlock, self.objProcessingHeader.numHeights, self.objSystemHeader.numChannels))
        
        self.__buffer = data
        
        self.__buffer_id = 0
        
    def readNextBlock(self):

        self.__setNewBlock()
             
        self.__readBlock()
        
        self.__lastUTTime = self.objBasicHeader.utc
 
    def __hasNotDataInBuffer(self):
        if self.__buffer_id >= self.objProcessingHeader.profilesPerBlock:
            return 1
        
        return 0

    def getData(self):
        """Obtiene un unidad de datos del buffer de lectura y es copiada a la clase "Data"
        con todos los parametros asociados a este. cuando no hay datos en el buffer de
        lectura es necesario hacer una nueva lectura de los bloques de datos
        "__readBlock"
        """
        
        if self.__hasNotDataInBuffer():            
            self.readNextBlock() 
        
        if self.noMoreFiles == 1:
            print 'read finished'
            return None
        
        data = self.__buffer[self.__buffer_id,:,:]
        
        #print self.__buffer_id
        
        self.__buffer_id += 1
            
        #call setData - to Data Object
    
        return data


    def setup(self, path, startDateTime, endDateTime, set=None, expLabel = "", ext = ".r", online = 0):
        
        if online == 0:
            pathList, filenameList = self.__searchFiles(path, startDateTime, endDateTime, set, expLabel, ext)
            
            if len(filenameList) == 0:
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
    
    def __init__(self):
        pass
    