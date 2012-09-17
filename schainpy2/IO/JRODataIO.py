import os, sys
import glob
import time
import numpy
import fnmatch
import time, datetime

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from Model.JROHeader import *
from Model.JROData import JROData

def isThisFileinRange(filename, startUTSeconds, endUTSeconds):
    """
    Esta funcion determina si un archivo de datos se encuentra o no dentro del rango de fecha especificado.
    
    Inputs:
        filename            :    nombre completo del archivo de datos en formato Jicamarca (.r)
        
        startUTSeconds      :    fecha inicial del rango seleccionado. La fecha esta dada en
                                 segundos contados desde 01/01/1970.
        endUTSeconds        :    fecha final del rango seleccionado. La fecha esta dada en
                                 segundos contados desde 01/01/1970.
    
    Return:
        Boolean    :    Retorna True si el archivo de datos contiene datos en el rango de
                        fecha especificado, de lo contrario retorna False.
    
    Excepciones:
        Si el archivo no existe o no puede ser abierto
        Si la cabecera no puede ser leida.
        
    """
    m_BasicHeader = BasicHeader()
    
    try:
        fp = open(filename,'rb')
    except:
        raise IOError, "The file %s can't be opened" %(filename)
    
    sts = m_BasicHeader.read(fp)
    fp.close()
    
    if not(sts):
        print "Skipping the file %s because it has not a valid header" %(filename)
        return 0
    
    if not ((startUTSeconds <= m_BasicHeader.utc) and (endUTSeconds > m_BasicHeader.utc)):
        return 0
    
    return 1




class JRODataIO:
    c = 3E8
    m_BasicHeader = BasicHeader()
    m_SystemHeader = SystemHeader()
    m_RadarControllerHeader = RadarControllerHeader()
    m_ProcessingHeader = ProcessingHeader()
    online = 0
    dataType = None
    pathList = []
    filenameList = []
    filename = None
    ext = None
    fileIndex = None
    flagNoMoreFiles = 0
    flagIsNewFile = 1
    flagResetProcessing = 0
    flagIsNewBlock = 0
    fp = None
    firstHeaderSize = 0
    basicHeaderSize = 24
    fileSize = None
    ippSeconds = None
    fileSizeByHeader = None
    def __init__(self):
        pass

class JRODataReader(JRODataIO):
    def __init__(self):
        pass

    def createObjByDefault(self):
        """

        """
        raise ValueError, "This method has not been implemented"

    def getBlockDimension(self):
        
        raise ValueError, "No implemented"

    def __searchFilesOffLine(self,
                            path,
                            startDate,
                            endDate,
                            startTime=datetime.time(0,0,0),
                            endTime=datetime.time(23,59,59),
                            set=None,
                            expLabel="",
                            ext=".r"):
        dirList = []
        for thisPath in os.listdir(path):
            if os.path.isdir(os.path.join(path,thisPath)):
                dirList.append(thisPath)

        if not(dirList):
            return None, None

        pathList = []
        dateList = []
        
        thisDate = startDate
        
        while(thisDate <= endDate):
            year = thisDate.timetuple().tm_year
            doy = thisDate.timetuple().tm_yday
            
            match = fnmatch.filter(dirList, '?' + '%4.4d%3.3d' % (year,doy))
            if len(match) == 0:
                thisDate += datetime.timedelta(1)
                continue
            
            pathList.append(os.path.join(path,match[0],expLabel))
            dateList.append(thisDate)
            thisDate += datetime.timedelta(1)
        
        filenameList = []
        for index in range(len(pathList)):
            
            thisPath = pathList[index]
            fileList = glob.glob1(thisPath, "*%s" %ext)
            fileList.sort()
            
            #Busqueda de datos en el rango de horas indicados
            thisDate = dateList[index]
            startDT = datetime.datetime.combine(thisDate, startTime)
            endDT = datetime.datetime.combine(thisDate, endTime)
            
            startUtSeconds = time.mktime(startDT.timetuple())
            endUtSeconds = time.mktime(endDT.timetuple())
            
            for file in fileList:
                
                filename = os.path.join(thisPath,file)
                
                if isThisFileinRange(filename, startUtSeconds, endUtSeconds):
                    filenameList.append(filename)
                    
        if not(filenameList):
            return None, None

        self.filenameList = filenameList
        
        return pathList, filenameList

    def setup(self,dataOutObj=None, 
                path=None,startDate=None, 
                endDate=None, 
                startTime=datetime.time(0,0,0), 
                endTime=datetime.time(23,59,59), 
                set=0, 
                expLabel = "", 
                ext = None, 
                online = 0):

        if path == None:
            raise ValueError, "The path is not valid"

        if ext == None:
            ext = self.ext

        if dataOutObj == None:
            dataOutObj = self.createObjByDefault()

        self.dataOutObj = dataOutObj

        if online:
            pass

        else:
            print "Searching file in offline mode"
            pathList, filenameList = self.__searchFilesOffLine(path, startDate, endDate, startTime, endTime, set, expLabel, ext)
            if not(pathList):
                print "No files in range: %s - %s"%(datetime.datetime.combine(startDate,startTime).ctime(), datetime.datetime.combine(endDate,endTime).ctime())
                return None
            self.fileIndex = -1
            self.pathList = pathList
            self.filenameList = filenameList

        self.online = online
        ext = ext.lower()
        self.ext = ext

        if not(self.setNextFile()):
            if (startDate!=None) and (endDate!=None):
                print "No files in range: %s - %s" %(datetime.datetime.combine(startDate,startTime).ctime(), datetime.datetime.combine(endDate,endTime).ctime())
            elif startDate != None:
                print "No files in range: %s" %(datetime.datetime.combine(startDate,startTime).ctime())
            else:
                print "No files"

            return None

        self.updateDataHeader()

        return self.dataOutObj

    def __setNextFileOffline(self):
        idFile = self.fileIndex

        while (True):
            idFile += 1
            if not(idFile < len(self.filenameList)):
                self.flagNoMoreFiles = 1
                print "No more Files"
                return 0

            filename = self.filenameList[idFile]

            if not(self.__verifyFile(filename)):
                continue

            fileSize = os.path.getsize(filename)
            fp = open(filename,'rb')
            break

        self.flagIsNewFile = 1
        self.fileIndex = idFile
        self.filename = filename
        self.fileSize = fileSize
        self.fp = fp

        print "Setting the file: %s"%self.filename

        return 1



    def setNextFile(self):
        if self.fp != None:
            self.fp.close()

        if self.online:
            newFile = self.__setNextFileOnline()
        else:
            newFile = self.__setNextFileOffline()

        if not(newFile):
            return 0

        self.__readFirstHeader()
        self.nReadBlocks = 0
        return 1

    def __rdProcessingHeader(self, fp=None):
        if fp == None:
            fp = self.fp

        self.m_ProcessingHeader.read(fp)

    def __rdRadarControllerHeader(self, fp=None):
        if fp == None:
            fp = self.fp

        self.m_RadarControllerHeader.read(fp)

    def __rdSystemHeader(self, fp=None):
        if fp == None:
            fp = self.fp

        self.m_SystemHeader.read(fp)

    def __rdBasicHeader(self, fp=None):
        if fp == None:
            fp = self.fp

        self.m_BasicHeader.read(fp)
        

    def __readFirstHeader(self):
        self.__rdBasicHeader()
        self.__rdSystemHeader()
        self.__rdRadarControllerHeader()
        self.__rdProcessingHeader()

        self.firstHeaderSize = self.m_BasicHeader.size

        datatype = int(numpy.log2((self.m_ProcessingHeader.processFlags & PROCFLAG.DATATYPE_MASK))-numpy.log2(PROCFLAG.DATATYPE_CHAR))
        if datatype == 0:
            datatype_str = numpy.dtype([('real','<i1'),('imag','<i1')])
        elif datatype == 1:
            datatype_str = numpy.dtype([('real','<i2'),('imag','<i2')])
        elif datatype == 2:
            datatype_str = numpy.dtype([('real','<i4'),('imag','<i4')])
        elif datatype == 3:
            datatype_str = numpy.dtype([('real','<i8'),('imag','<i8')])
        elif datatype == 4:
            datatype_str = numpy.dtype([('real','<f4'),('imag','<f4')])
        elif datatype == 5:
            datatype_str = numpy.dtype([('real','<f8'),('imag','<f8')])
        else:
            raise ValueError, 'Data type was not defined'

        self.dataType = datatype_str
        self.ippSeconds = 2 * 1000 * self.m_RadarControllerHeader.ipp / self.c
        self.fileSizeByHeader = self.m_ProcessingHeader.dataBlocksPerFile * self.m_ProcessingHeader.blockSize + self.firstHeaderSize + self.basicHeaderSize*(self.m_ProcessingHeader.dataBlocksPerFile - 1)
#        self.dataOutObj.channelList = numpy.arange(self.m_SystemHeader.numChannels)
#        self.dataOutObj.channelIndexList = numpy.arange(self.m_SystemHeader.numChannels)
        self.getBlockDimension()


    def __verifyFile(self, filename, msgFlag=True):
        msg = None
        try:
            fp = open(filename, 'rb')
            currentPosition = fp.tell()
        except:
            if msgFlag:
                print "The file %s can't be opened" % (filename)
            return False

        neededSize = self.m_ProcessingHeader.blockSize + self.firstHeaderSize

        if neededSize == 0:
            m_BasicHeader = BasicHeader()
            m_SystemHeader = SystemHeader()
            m_RadarControllerHeader = RadarControllerHeader()
            m_ProcessingHeader = ProcessingHeader()

            try:
                if not( m_BasicHeader.read(fp) ): raise ValueError
                if not( m_SystemHeader.read(fp) ): raise ValueError
                if not( m_RadarControllerHeader.read(fp) ): raise ValueError
                if not( m_ProcessingHeader.read(fp) ): raise ValueError
                data_type = int(numpy.log2((m_ProcessingHeader.processFlags & PROCFLAG.DATATYPE_MASK))-numpy.log2(PROCFLAG.DATATYPE_CHAR))

                neededSize = m_ProcessingHeader.blockSize + m_BasicHeader.size

            except:
                if msgFlag:
                    print "\tThe file %s is empty or it hasn't enough data" % filename

                fp.close()
                return False
        else:
            msg = "\tSkipping the file %s due to it hasn't enough data" %filename

        fp.close()
        fileSize = os.path.getsize(filename)
        currentSize = fileSize - currentPosition
        if currentSize < neededSize:
            if msgFlag and (msg != None):
                print msg #print"\tSkipping the file %s due to it hasn't enough data" %filename
            return False

        return True



    def updateDataHeader(self):
        self.dataOutObj.m_BasicHeader = self.m_BasicHeader.copy()
        self.dataOutObj.m_ProcessingHeader = self.m_ProcessingHeader.copy()
        self.dataOutObj.m_RadarControllerHeader = self.m_RadarControllerHeader.copy()
        self.dataOutObj.m_SystemHeader = self.m_SystemHeader.copy()
        self.dataOutObj.dataType = self.dataType
        self.dataOutObj.updateObjFromHeader() # actualiza los atributos del objeto de salida de la clase JROData







