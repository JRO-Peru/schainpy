'''
Created on 23/01/2012

@author: danielangelsuarezmunoz
'''

from DataReader import DataReader

import numpy
import os.path
import glob
import fnmatch
import time
import datetime

class PROCFLAG:    
    COHERENT_INTEGRATION = numpy.uint32(0x00000001)
    DECODE_DATA = numpy.uint32(0x00000002) 
    SPECTRA_CALC = numpy.uint32(0x00000004)
    INCOHERENT_INTEGRATION = numpy.uint32(0x00000008) 
    POST_COHERENT_INTEGRATION = numpy.uint32(0x00000010)
    SHIFT_FFT_DATA = numpy.uint32(0x00000020)
    
    DATATYPE_CHAR = numpy.uint32(0x00000040)
    DATATYPE_SHORT = numpy.uint32(0x00000080)
    DATATYPE_LONG = numpy.uint32(0x00000100)
    DATATYPE_INT64 = numpy.uint32(0x00000200)
    DATATYPE_FLOAT = numpy.uint32(0x00000400)
    DATATYPE_DOUBLE = numpy.uint32(0x00000800)
    
    DATAARRANGE_CONTIGUOUS_CH = numpy.uint32(0x00001000) 
    DATAARRANGE_CONTIGUOUS_H = numpy.uint32(0x00002000) 
    DATAARRANGE_CONTIGUOUS_P = numpy.uint32(0x00004000) 
    
    SAVE_CHANNELS_DC = numpy.uint32(0x00008000)
    DEFLIP_DATA = numpy.uint32(0x00010000)    
    DEFINE_PROCESS_CODE = numpy.uint32(0x00020000) 
     
    ACQ_SYS_NATALIA = numpy.uint32(0x00040000)
    ACQ_SYS_ECHOTEK = numpy.uint32(0x00080000)
    ACQ_SYS_ADRXD = numpy.uint32(0x000C0000)
    ACQ_SYS_JULIA = numpy.uint32(0x00100000)
    ACQ_SYS_XXXXXX = numpy.uint32(0x00140000)
    
    EXP_NAME_ESP = numpy.uint32(0x00200000)
    CHANNEL_NAMES_ESP = numpy.uint32(0x00400000)
        
    OPERATION_MASK = numpy.uint32(0x0000003F)
    DATATYPE_MASK = numpy.uint32(0x00000FC0)
    DATAARRANGE_MASK = numpy.uint32(0x00007000)
    ACQ_SYS_MASK = numpy.uint32(0x001C0000)

class StructShortHeader():
    
    size = 0
    version = 0
    dataBlock = 0
    utc = 0
    miliSecond = 0
    timeZone = 0
    dstFlag = 0
    errorCount = 0
    struct = numpy.dtype([
                          ('nSize','<u4'),
                          ('nVersion','<u2'),
                          ('nDataBlockId','<u4'),
                          ('nUtime','<u4'),
                          ('nMilsec','<u2'),     
                          ('nTimezone','<i2'),
                          ('nDstflag','<i2'),
                          ('nErrorCount','<u4')
                          ])   
        
    def __init__(self):
        pass
    
    def read(self, fp):
        
        header = numpy.fromfile(fp, self.struct,1)
        self.size = header['nSize'][0]
        self.version = header['nVersion'][0]
        self.dataBlock = header['nDataBlockId'][0]
        self.utc = header['nUtime'][0]
        self.miliSecond = header['nMilsec'][0]
        self.timeZone = header['nTimezone'][0]
        self.dstFlag = header['nDstflag'][0]
        self.errorCount = header['nErrorCount'][0]
        
        return 1

class StructSystemHeader():
    size = 0 
    numSamples = 0
    numProfiles = 0
    numChannels = 0
    adcResolution = 0
    pciDioBusWidth = 0
    struct = numpy.dtype([
                        ('nSize','<u4'),
                        ('nNumSamples','<u4'),
                        ('nNumProfiles','<u4'),
                        ('nNumChannels','<u4'),
                        ('nADCResolution','<u4'),
                        ('nPCDIOBusWidth','<u4'),
                        ])
    
    def __init__(self):
        pass

    def read(self, fp):
        
        
        return 1
    
class StructRadarController():
    size = 0
    expType = 0
    nTx = 0
    ipp = 0
    txA = 0
    txB = 0
    numWindows = 0
    numTaus = 0
    codeType = 0
    line6Function = 0
    line5Fuction = 0
    fClock = 0
    prePulseBefore = 0
    prePulserAfter = 0
    rangeIpp = 0
    rangeTxA = 0
    rangeTxB = 0
    struct = numpy.dtype([
                         ('nSize','<u4'),
                         ('nExpType','<u4'),
                         ('nNTx','<u4'),
                         ('fIpp','<f4'),
                         ('fTxA','<f4'),
                         ('fTxB','<f4'),
                         ('nNumWindows','<u4'),
                         ('nNumTaus','<u4'),
                         ('nCodeType','<u4'),
                         ('nLine6Function','<u4'),
                         ('nLine5Function','<u4'),
                         ('fClock','<f4'),
                         ('nPrePulseBefore','<u4'),
                         ('nPrePulseAfter','<u4'),
                         ('sRangeIPP','<a20'),
                         ('sRangeTxA','<a20'),
                         ('sRangeTxB','<a20'),
                         ])
    
    
    def __init__(self):
        pass

    def read(self, fp):
        
        return 1
    
class StructProcessing():
    size = 0
    dataType = 0
    blockSize = 0
    profilesPerBlock = 0
    dataBlocksPerFile = 0
    numWindows = 0
    processFlags = 0
    coherentInt = 0
    incoherentInt = 0
    totalSpectra = 0
    struct = numpy.dtype([
                           ('nSize','<u4'),
                           ('nDataType','<u4'),
                           ('nSizeOfDataBlock','<u4'),
                           ('nProfilesperBlock','<u4'),
                           ('nDataBlocksperFile','<u4'),
                           ('nNumWindows','<u4'),
                           ('nProcessFlags','<u4'),
                           ('nCoherentIntegrations','<u4'),
                           ('nIncoherentIntegrations','<u4'),
                           ('nTotalSpectra','<u4')
                           ])
    samplingWindow = 0
    structSamplingWindow = numpy.dtype([('h0','<f4'),('dh','<f4'),('nsa','<u4')])
    numHeights = 0
    firstHeight = 0
    deltaHeight = 0
    samplesWin = 0
    spectraComb = 0
    numCode = 0
    codes = 0
    numBaud = 0
    
    def __init__(self):
        pass
    
    def read(self, fp):
        
        return 1

class VoltageReader(DataReader):
    # Este flag indica que la data leida no es continua
    __jumpDataFlag = False
    
    __idFile = 0
    
    __fp = 0
    
    __startDateTime = 0
    
    __endDateTime = 0
    
    __dataType = 0
    
    __sizeOfFileByHeader = 0
    
    __listOfPath = []
    
    filenameList = []
    
    __flagReadShortHeader = 0
    
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
    
    objStructShortHeader = StructShortHeader()
    
    objStructSystemHeader = StructSystemHeader()
    
    objStructRadarController = StructRadarController()
    
    objStructProcessing = StructProcessing()
    
    __buffer = 0
    
    __buffer_id = 9999
                    
    def __init__(self):
        pass
    
    def __rdSystemHeader(self):
        header = numpy.fromfile(self.__fp,self.objStructSystemHeader.struct,1)
        self.objStructSystemHeader.size = header['nSize'][0]
        self.objStructSystemHeader.numSamples = header['nNumSamples'][0]
        self.objStructSystemHeader.numProfiles = header['nNumProfiles'][0]
        self.objStructSystemHeader.numChannels = header['nNumChannels'][0]
        self.objStructSystemHeader.adcResolution = header['nADCResolution'][0]
        self.objStructSystemHeader.pciDioBusWidth = header['nPCDIOBusWidth'][0]
    
    def __rdRadarControllerHeader(self):
        header = numpy.fromfile(self.__fp,self.objStructRadarController.struct,1)
        self.objStructRadarController.size = header['nSize'][0]
        self.objStructRadarController.expType = header['nExpType'][0]
        self.objStructRadarController.nTx = header['nNTx'][0]
        self.objStructRadarController.ipp = header['fIpp'][0]
        self.objStructRadarController.txA = header['fTxA'][0]
        self.objStructRadarController.txB = header['fTxB'][0]
        self.objStructRadarController.numWindows = header['nNumWindows'][0]
        self.objStructRadarController.numTaus = header['nNumTaus'][0]
        self.objStructRadarController.codeType = header['nCodeType'][0]
        self.objStructRadarController.line6Function = header['nLine6Function'][0]
        self.objStructRadarController.line5Fuction = header['nLine5Function'][0]
        self.objStructRadarController.fClock = header['fClock'][0]
        self.objStructRadarController.prePulseBefore = header['nPrePulseBefore'][0]
        self.objStructRadarController.prePulserAfter = header['nPrePulseAfter'][0]
        self.objStructRadarController.rangeIpp = header['sRangeIPP'][0]
        self.objStructRadarController.rangeTxA = header['sRangeTxA'][0]
        self.objStructRadarController.rangeTxB = header['sRangeTxB'][0]
        # jump Dynamic Radar Controller Header
        jumpHeader = self.objStructRadarController.size - 116
        self.__fp.seek(self.__fp.tell() + jumpHeader)
        
    def __rdProcessingHeader(self):
        header = numpy.fromfile(self.__fp,self.objStructProcessing.struct,1)
        self.objStructProcessing.size = header['nSize'][0]
        self.objStructProcessing.dataType = header['nDataType'][0]
        self.objStructProcessing.blockSize = header['nSizeOfDataBlock'][0]
        self.objStructProcessing.profilesPerBlock = header['nProfilesperBlock'][0]
        self.objStructProcessing.dataBlocksPerFile = header['nDataBlocksperFile'][0]
        self.objStructProcessing.numWindows = header['nNumWindows'][0]
        self.objStructProcessing.processFlags = header['nProcessFlags']
        self.objStructProcessing.coherentInt = header['nCoherentIntegrations'][0]
        self.objStructProcessing.incoherentInt = header['nIncoherentIntegrations'][0]
        self.objStructProcessing.totalSpectra = header['nTotalSpectra'][0]
        self.objStructProcessing.samplingWindow = numpy.fromfile(self.__fp,self.objStructProcessing.structSamplingWindow,self.objStructProcessing.numWindows)
        self.objStructProcessing.numHeights = numpy.sum(self.objStructProcessing.samplingWindow['nsa'])
        self.objStructProcessing.firstHeight = self.objStructProcessing.samplingWindow['h0']
        self.objStructProcessing.deltaHeight = self.objStructProcessing.samplingWindow['dh']
        self.objStructProcessing.samplesWin = self.objStructProcessing.samplingWindow['nsa']
        self.objStructProcessing.spectraComb = numpy.fromfile(self.__fp,'u1',2*self.objStructProcessing.totalSpectra)
        if self.objStructProcessing.processFlags & PROCFLAG.DEFINE_PROCESS_CODE == PROCFLAG.DEFINE_PROCESS_CODE:
            self.objStructProcessing.numCode = numpy.fromfile(self.__fp,'<u4',1)
            self.objStructProcessing.numBaud = numpy.fromfile(self.__fp,'<u4',1)
            self.objStructProcessing.codes = numpy.fromfile(self.__fp,'<f4',self.objStructProcessing.numCode*self.objStructProcessing.numBaud).reshape(self.objStructProcessing.numBaud,self.objStructProcessing.numCode)
    
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
        
        listOfPath = []
        dicOfPath = {}
        for year in rangeOfYears:
            for doy in doyList:        
                tmp = fnmatch.filter(folders, 'D' + '%4.4d%3.3d' % (year,doy))
                if len(tmp) == 0:
                    continue
                if expLabel == '':
                    listOfPath.append(os.path.join(path,tmp[0]))
                    dicOfPath.setdefault(os.path.join(path,tmp[0]))
                    dicOfPath[os.path.join(path,tmp[0])] = []
                else:
                    listOfPath.append(os.path.join(path,os.path.join(tmp[0],expLabel)))
                    dicOfPath.setdefault(os.path.join(path,os.path.join(tmp[0],expLabel)))
                    dicOfPath[os.path.join(path,os.path.join(tmp[0],expLabel))] = []
        
        
        filenameList = []
        for thisPath in listOfPath:
            fileList = glob.glob1(thisPath, ext)
            #dicOfPath[thisPath].append(fileList)
            fileList.sort()
            for file in fileList:
                filename = os.path.join(thisPath,file)
                if self.isThisFileinRange(filename, startUtSeconds, endUtSeconds):
                    filenameList.append(filename)
                    
        self.filenameList = filenameList
        
        return listOfPath, filenameList


    def isThisFileinRange(self, filename, startUTSeconds=None, endUTSeconds=None):
        
        try:
            fp = open(filename,'rb')
        except:
            raise IOError, "The file %s can't be opened" %(filename)
        
        if startUTSeconds==None:
            startUTSeconds = self.startUTCSeconds
        
        if endUTSeconds==None:
            endUTSeconds = self.endUTCSeconds
            
        objShortHeader = StructShortHeader()
        
        if not(objShortHeader.read(fp)):
            return 0
        
        if not ((startUTSeconds <= objShortHeader.utc) and (endUTSeconds >= objShortHeader.utc)):
            return 0
        
        return 1
    
    def __readBasicHeader(self, fp=None):
        
        if fp == None:
            fp = self.__fp
            
        self.objStructShortHeader.read(fp)
    

    def __readFirstHeader(self):
        
        self.__readBasicHeader()
        self.__rdSystemHeader()
        self.__rdRadarControllerHeader()
        self.__rdProcessingHeader()
        self.firstHeaderSize = self.objStructShortHeader.size
        
        data_type=int(numpy.log2((self.objStructProcessing.processFlags & PROCFLAG.DATATYPE_MASK))-numpy.log2(PROCFLAG.DATATYPE_CHAR))
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
        self.__sizeOfFileByHeader = self.objStructProcessing.dataBlocksPerFile * self.objStructProcessing.blockSize + self.firstHeaderSize + self.basicHeaderSize*(self.objStructProcessing.dataBlocksPerFile - 1)        



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
            neededSize = self.objStructProcessing.blockSize + self.firstHeaderSize
            
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
        neededSize = self.objStructProcessing.blockSize + self.basicHeaderSize
        
        # Bloque Completo
        if (currentSize >= neededSize):
            self.__readBasicHeader()
            return 1
        
        self.__setNextFile()
        self.__readFirstHeader()
        
        deltaTime = self.objStructShortHeader.utc - self.__lastUTTime # check this
        if deltaTime > self.__maxTimeStep:
            self.__flagResetProcessing = 1
            
        return 1
    
    def __readBlock(self):
        """Lee el bloque de datos desde la posicion actual del puntero del archivo y
        actualiza todos los parametros relacionados al bloque de datos (data, time,
        etc). La data leida es almacenada en el buffer y el contador de datos leidos es
        seteado a 0
        """
        
        pts2read = self.objStructProcessing.profilesPerBlock*self.objStructProcessing.numHeights*self.objStructSystemHeader.numChannels
        
        data = numpy.fromfile(self.__fp,self.__dataType,pts2read)
        
        data = data.reshape((self.objStructProcessing.profilesPerBlock, self.objStructProcessing.numHeights, self.objStructSystemHeader.numChannels))
        
        self.__buffer = data
        
        self.__buffer_id = 0
        
    def readNextBlock(self):

        self.__setNewBlock()
             
        self.__readBlock()
        
        self.__lastUTTime = self.objStructShortHeader.utc
 
    def __hasNotDataInBuffer(self):
        if self.__buffer_id >= self.objStructProcessing.profilesPerBlock:
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
            
        self.__listOfPath = pathList
        self.filenameList = filenameList 
        self.online = online
