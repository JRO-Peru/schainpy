'''
Created on 23/01/2012

@author $Author$
@version $Id$
'''

import os, sys
import numpy
import glob
import fnmatch
import time, datetime

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from IO.HeaderIO import *
from IO.DataIO import DataReader
from IO.DataIO import DataWriter

from Model.Voltage import Voltage

def isThisFileinRange(filename, startUTSeconds, endUTSeconds):
    """
    Esta funcion determina si un archivo de datos  en formato Jicamarca(.r) se encuentra
    o no dentro del rango de fecha especificado.
    
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
    
    if not(m_BasicHeader.read(fp)):
        raise IOError, "The file %s has not a valid header" %(filename)
    
    fp.close()
    
    if not ((startUTSeconds <= m_BasicHeader.utc) and (endUTSeconds >= m_BasicHeader.utc)):
        return 0
    
    return 1

class VoltageReader(DataReader):
    """
    Esta clase permite leer datos de voltage desde archivos en formato rawdata (.r). La lectura
    de los datos siempre se realiza por bloques. Los datos leidos (array de 3 dimensiones: 
    perfiles*alturas*canales) son almacenados en la variable "buffer".
     
    Esta clase contiene instancias (objetos) de las clases BasicHeader, SystemHeader, 
    RadarControllerHeader y Voltage. Los tres primeros se usan para almacenar informacion de la
    cabecera de datos (metadata), y el cuarto (Voltage) para obtener y almacenar un perfil de
    datos desde el "buffer" cada vez que se ejecute el metodo "getData".
    
    Example:
    
        dpath = "/home/myuser/data"
        
        startTime = datetime.datetime(2010,1,20,0,0,0,0,0,0)
        
        endTime = datetime.datetime(2010,1,21,23,59,59,0,0,0)
        
        readerObj = VoltageReader()
        
        readerObj.setup(dpath, startTime, endTime)
        
        while(True):
            
            #to get one profile 
            profile =  readerObj.getData()
            
            #print the profile
            print profile
            
            #If you want to see all datablock
            print readerObj.datablock
            
            if readerObj.noMoreFiles:
                break
            
    """
    
    #speed of light
    __c = 3E8
    
    def __init__(self, m_Voltage = None):
        """
        Inicializador de la clase VoltageReader para la lectura de datos de voltage.
        
        Input:
            m_Voltage    :    Objeto de la clase Voltage. Este objeto sera utilizado para
                              almacenar un perfil de datos cada vez que se haga un requerimiento
                              (getData). El perfil sera obtenido a partir del buffer de datos,
                              si el buffer esta vacio se hara un nuevo proceso de lectura de un
                              bloque de datos.
                              Si este parametro no es pasado se creara uno internamente.
        
        Variables afectadas:
            self.m_Voltage
            self.m_BasicHeader
            self.m_SystemHeader
            self.m_RadarControllerHeader
            self.m_ProcessingHeader
            
        
        Return:
            Void
        
        """
        if m_Voltage == None:
            m_Voltage = Voltage()
        
        if not(isinstance(m_Voltage, Voltage)):
            raise ValueError, "in VoltageReader, m_Voltage must be an Voltage class object"
        
        self.m_Voltage = m_Voltage
        
        self.m_BasicHeader = BasicHeader()
        
        self.m_SystemHeader = SystemHeader()
        
        self.m_RadarControllerHeader = RadarControllerHeader()
        
        self.m_ProcessingHeader = ProcessingHeader()
    
        self.__fp = None
        
        self.__idFile = None
        
        self.__startDateTime = None
        
        self.__endDateTime = None
        
        self.__dataType = None
        
        self.__fileSizeByHeader = 0
        
        self.__pathList = []
        
        self.filenameList = []
        
        self.__lastUTTime = 0
        
        self.__maxTimeStep = 30
        
        self.__flagIsNewFile = 0
        
        self.__ippSeconds = 0
        
        self.flagResetProcessing = 0    
        
        self.flagIsNewBlock = 0
        
        self.noMoreFiles = 0
        
        self.nReadBlocks = 0
        
        self.online = 0
        
        self.filename = None
        
        self.fileSize = None
        
        self.firstHeaderSize = 0
        
        self.basicHeaderSize = 24
        
        self.idProfile = 0
        
        self.datablock = None
        
        self.datablock_id = 9999
    
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

    def __rdBasicHeader(self, fp=None):
        
        if fp == None:
            fp = self.__fp
            
        self.m_BasicHeader.read(fp)
    
    def __readFirstHeader(self):
        
        self.__rdBasicHeader()
        self.__rdSystemHeader()
        self.__rdRadarControllerHeader()
        self.__rdProcessingHeader()
        self.firstHeaderSize = self.m_BasicHeader.size
        
        data_type=int(numpy.log2((self.m_ProcessingHeader.processFlags & PROCFLAG.DATATYPE_MASK))-numpy.log2(PROCFLAG.DATATYPE_CHAR))
        if data_type == 0:
            tmp = numpy.dtype([('real','<i1'),('imag','<i1')])
            
        elif data_type == 1:
            tmp = numpy.dtype([('real','<i2'),('imag','<i2')])
            
        elif data_type == 2:
            tmp = numpy.dtype([('real','<i4'),('imag','<i4')])
            
        elif data_type == 3:
            tmp = numpy.dtype([('real','<i8'),('imag','<i8')])
            
        elif data_type == 4:
            tmp = numpy.dtype([('real','<f4'),('imag','<f4')])
            
        elif data_type == 5:
            tmp = numpy.dtype([('real','<f8'),('imag','<f8')])
            
        else:
            raise ValueError, 'Data type was not defined'
        
        xi = self.m_ProcessingHeader.firstHeight
        step = self.m_ProcessingHeader.deltaHeight
        xf = xi + self.m_ProcessingHeader.numHeights*step
        
        self.__heights = numpy.arange(xi, xf, step)
        self.__dataType = tmp
        self.__fileSizeByHeader = self.m_ProcessingHeader.dataBlocksPerFile * self.m_ProcessingHeader.blockSize + self.firstHeaderSize + self.basicHeaderSize*(self.m_ProcessingHeader.dataBlocksPerFile - 1)
        self.__ippSeconds = 2*1000*self.m_RadarControllerHeader.ipp/self.__c
        
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
            
            try:
                fp = open(filename,'rb')
            except:
                raise IOError, "The file %s can't be opened" %filename
            
            currentSize = fileSize - fp.tell()
            neededSize = self.m_ProcessingHeader.blockSize + self.firstHeaderSize
            
            if (currentSize < neededSize):
                print "Skipping the file %s due to it hasn't enough data" %filename
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
            newFile = self.__setNextFileOnline()
        else:
            newFile = self.__setNextFileOffline()
        
        if not(newFile):
            return 0
        
        self.__readFirstHeader()
        
        return 1
    
    def __setNewBlock(self):
        
        if self.__fp == None:
            return 0
        
        if self.__flagIsNewFile:
            return 1
        
        currentSize = self.fileSize - self.__fp.tell()
        neededSize = self.m_ProcessingHeader.blockSize + self.basicHeaderSize
        
        #If there is enough data setting new data block
        if (currentSize >= neededSize):
            self.__rdBasicHeader()
            return 1
        
        #Setting new file 
        if not(self.__setNextFile()):
            return 0
        
        deltaTime = self.m_BasicHeader.utc - self.__lastUTTime # check this
        
        self.flagResetProcessing = 0
        
        if deltaTime > self.__maxTimeStep:
            self.flagResetProcessing = 1
            self.nReadBlocks = 0
            
        return 1
    
    def __readBlock(self):
        """
        __readBlock lee el bloque de datos desde la posicion actual del puntero del archivo
        (self.__fp) y actualiza todos los parametros relacionados al bloque de datos
        (metadata + data). La data leida es almacenada en el buffer y el contador del buffer
        es seteado a 0
        
        
        Inputs:
            None
            
        Return:
            None
        
        Variables afectadas:
        
            self.datablock_id
            
            self.datablock
            
            self.__flagIsNewFile
            
            self.idProfile
            
            self.flagIsNewBlock
            
            self.nReadBlocks
            
        """
        
        pts2read = self.m_ProcessingHeader.profilesPerBlock*self.m_ProcessingHeader.numHeights*self.m_SystemHeader.numChannels
        
        junk = numpy.fromfile(self.__fp, self.__dataType, pts2read)
        
        junk = junk.reshape((self.m_ProcessingHeader.profilesPerBlock, self.m_ProcessingHeader.numHeights, self.m_SystemHeader.numChannels))
        
        data = junk['real'] + junk['imag']*1j
        
        self.datablock_id = 0
        
        self.datablock = data
        
        self.__flagIsNewFile = 0
        
        self.idProfile = 0
        
        self.flagIsNewBlock = 1
        
        self.nReadBlocks += 1
 
    def __hasNotDataInBuffer(self):
        if self.datablock_id >= self.m_ProcessingHeader.profilesPerBlock:
            return 1
        
        return 0

    def __searchFiles(self, path, startDateTime, endDateTime, set=None, expLabel = "", ext = ".r"):
        """
        __searchFiles realiza una busqueda de los archivos que coincidan con los parametros
        especificados y se encuentren ubicados en el path indicado. Para realizar una busqueda
        correcta la estructura de directorios debe ser la siguiente:
        
        ...path/D[yyyy][ddd]/expLabel/D[yyyy][ddd][sss].ext
        
        [yyyy]: anio
        [ddd] : dia del anio
        [sss] : set del archivo        
        
        Inputs:
            path           :    Directorio de datos donde se realizara la busqueda. Todos los
                                ficheros que concidan con el criterio de busqueda seran
                                almacenados en una lista y luego retornados.
            startDateTime  :    Fecha inicial. Rechaza todos los archivos donde 
                                file end time < startDateTime (obejto datetime.datetime)
                                                         
            endDateTime    :    Fecha final. Rechaza todos los archivos donde 
                                file start time > endDateTime (obejto datetime.datetime)
            
            set            :    Set del primer archivo a leer. Por defecto None
            
            expLabel       :    Nombre del subdirectorio de datos.  Por defecto ""
            
            ext            :    Extension de los archivos a leer. Por defecto .r
            
        Return:
            
            (pathList, filenameList)
            
            pathList        :    Lista de directorios donde se encontraron archivos dentro 
                                 de los parametros especificados
            filenameList    :    Lista de archivos (ruta completa) que coincidieron con los
                                 parametros especificados.
        
        Variables afectadas:
        
            self.filenameList:    Lista de archivos (ruta completa) que la clase utiliza
                                  como fuente para leer los bloque de datos, si se termina
                                  de leer todos los bloques de datos de un determinado 
                                  archivo se pasa al siguiente archivo de la lista.
             
        Excepciones:
        
        """
        
        print "Searching files ..."
        
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
        
        startUtSeconds = time.mktime(startDateTime.timetuple())
        endUtSeconds = time.mktime(endDateTime.timetuple())
        
        filenameList = []
        for thisPath in pathList:
            fileList = glob.glob1(thisPath, "*%s" %ext)
            fileList.sort()
            for file in fileList:
                filename = os.path.join(thisPath,file)
                if isThisFileinRange(filename, startUtSeconds, endUtSeconds):
                    filenameList.append(filename)
                    
        self.filenameList = filenameList
        
        return pathList, filenameList
    
    def setup(self, path, startDateTime, endDateTime=None, set=None, expLabel = "", ext = ".r", online = 0):
        """
        setup configura los parametros de lectura de la clase VoltageReader.
        
        Si el modo de lectura es offline, primero se realiza una busqueda de todos los archivos
        que coincidan con los parametros especificados; esta lista de archivos son almacenados en
        self.filenameList.
        
        Input:
            path                :    Directorios donde se ubican los datos a leer. Dentro de este
                                     directorio deberia de estar subdirectorios de la forma:
                                     
                                     path/D[yyyy][ddd]/expLabel/P[yyyy][ddd][sss][ext]
            
            startDateTime       :    Fecha inicial. Rechaza todos los archivos donde
                                     file end time < startDatetime (obejto datetime.datetime)
            
            endDateTime         :    Fecha final. Si no es None, rechaza todos los archivos donde
                                     file end time < startDatetime (obejto datetime.datetime)
            
            set                 :    Set del primer archivo a leer. Por defecto None
            
            expLabel            :    Nombre del subdirectorio de datos.  Por defecto ""
            
            ext                 :    Extension de los archivos a leer. Por defecto .r
            
            online              :    
            
        Return:
        
        Affected:
        
        Excepciones:
        
        Example:       
        
        """
        
        if online == 0:
            pathList, filenameList = self.__searchFiles(path, startDateTime, endDateTime, set, expLabel, ext)
        
        self.__idFile = -1
        
        if not(self.__setNextFile()):
            print "No files in range: %s - %s" %(startDateTime.ctime(), endDateTime.ctime())
            return 0
        
        self.startUTCSeconds = time.mktime(startDateTime.timetuple())
        self.endUTCSeconds = time.mktime(endDateTime.timetuple())
        
        self.startYear = startDateTime.timetuple().tm_year 
        self.endYear = endDateTime.timetuple().tm_year
        
        self.startDoy = startDateTime.timetuple().tm_yday
        self.endDoy = endDateTime.timetuple().tm_yday
        
        self.m_Voltage.m_BasicHeader = self.m_BasicHeader.copy()
        self.m_Voltage.m_ProcessingHeader = self.m_ProcessingHeader.copy()
        self.m_Voltage.m_RadarControllerHeader = self.m_RadarControllerHeader.copy()
        self.m_Voltage.m_SystemHeader = self.m_SystemHeader.copy()
        self.m_Voltage.dataType = self.__dataType
            
        self.__pathList = pathList
        self.filenameList = filenameList 
        self.online = online
        
        return 1 
    
    def readNextBlock(self):
        """
        readNextBlock establece un nuevo bloque de datos a leer y los lee, si es que no existiese
        mas bloques disponibles en el archivo actual salta al siguiente.
        
        """
        
        if not(self.__setNewBlock()):
            return 0
             
        self.__readBlock()
        
        self.__lastUTTime = self.m_BasicHeader.utc
        
        return 1
    
    def getData(self):
        """
        getData obtiene una unidad de datos del buffer de lectura y la copia a la clase "Voltage"
        con todos los parametros asociados a este (metadata). cuando no hay datos en el buffer de
        lectura es necesario hacer una nueva lectura de los bloques de datos usando "readNextBlock"
        
        Ademas incrementa el contador del buffer en 1.
        
        Inputs:
            None
            
        Return:
            data    :    retorna un perfil de voltages (alturas * canales) copiados desde el
                         buffer. Si no hay mas archivos a leer retorna None.
            
        Variables afectadas:
            self.m_Voltage
            self.datablock_id
            self.idProfile
            
        Excepciones:
        
        """
        self.flagResetProcessing = 0
        self.flagIsNewBlock = 0
        
        if self.__hasNotDataInBuffer():
            self.readNextBlock()
            
            self.m_Voltage.m_BasicHeader = self.m_BasicHeader.copy()
            self.m_Voltage.m_ProcessingHeader = self.m_ProcessingHeader.copy()
            self.m_Voltage.m_RadarControllerHeader = self.m_RadarControllerHeader.copy()
            self.m_Voltage.m_SystemHeader = self.m_SystemHeader.copy()
            
            self.m_Voltage.heights = self.__heights
            self.m_Voltage.dataType = self.__dataType
            
        if self.noMoreFiles == 1:
            print 'Process finished'
            return None
        
        #data es un numpy array de 3 dmensiones (perfiles, alturas y canales)
        
        time = self.m_BasicHeader.utc + self.datablock_id*self.__ippSeconds
        self.m_Voltage.m_BasicHeader.utc = time  
        self.m_Voltage.data = self.datablock[self.datablock_id,:,:]
        self.m_Voltage.flagNoData = False
        self.m_Voltage.flagResetProcessing = self.flagResetProcessing
        
        self.m_Voltage.idProfile = self.idProfile
        
        
        self.datablock_id += 1
        self.idProfile += 1
        
        #call setData - to Data Object
    
        return self.m_Voltage.data

class VoltageWriter(DataWriter):
    __configHeaderFile = 'wrSetHeadet.txt'
    
    def __init__(self, m_Voltage = None):
        
        if m_Voltage == None:
            m_Voltage = Voltage()    
        
        self.m_Voltage = m_Voltage
        
        self.__path = None
        
        self.__fp = None
        
        self.__format = None
    
        self.__blocksCounter = 0
        
        self.__setFile = None
        
        self.__flagIsNewFile = 1
        
        self.datablock = None
        
        self.datablock_id = 0
        
        self.__dataType = None
        
        self.__ext = None
        
        self.__shapeBuffer = None
        
        self.nWriteBlocks = 0 
        
        self.flagIsNewBlock = 0
        
        self.noMoreFiles = 0
        
        self.filename = None
        
        self.m_BasicHeader= BasicHeader()
    
        self.m_SystemHeader = SystemHeader()
    
        self.m_RadarControllerHeader = RadarControllerHeader()
    
        self.m_ProcessingHeader = ProcessingHeader()
    
    
    def __writeBasicHeader(self, fp=None):
        if fp == None:
            fp = self.__fp
            
        self.m_BasicHeader.write(fp)
    
    def __wrSystemHeader(self,fp=None):
        if fp == None:
            fp = self.__fp
            
        self.m_SystemHeader.write(fp)
    
    def __wrRadarControllerHeader(self,fp=None):
        if fp == None:
            fp = self.__fp
        
        self.m_RadarControllerHeader.write(fp)
        
    def __wrProcessingHeader(self,fp=None):
        if fp == None:
            fp = self.__fp
            
        self.m_ProcessingHeader.write(fp)
    
    def __writeFirstHeader(self):
        self.__writeBasicHeader()
        self.__wrSystemHeader()
        self.__wrRadarControllerHeader()
        self.__wrProcessingHeader()
        self.__dataType = self.m_Voltage.dataType
    
 
    def __setNextFile(self):
        
        setFile = self.__setFile
        ext = self.__ext
        path = self.__path
        
        setFile += 1
        
        if self.__fp != None:
            self.__fp.close()
        
        timeTuple = time.localtime(self.m_Voltage.m_BasicHeader.utc) # utc from m_Voltage
        file = 'D%4.4d%3.3d%3.3d%s' % (timeTuple.tm_year,timeTuple.tm_yday,setFile,ext)
        subfolder = 'D%4.4d%3.3d' % (timeTuple.tm_year,timeTuple.tm_yday) 
        tmp = os.path.join(path,subfolder)
        if not(os.path.exists(tmp)):
            os.mkdir(tmp)
   
        filename = os.path.join(path,subfolder,file)
        fp = open(filename,'wb')
        
        self.__blocksCounter = 0
        
        #guardando atributos 
        self.filename = filename
        self.__subfolder = subfolder
        self.__fp = fp
        self.__setFile = setFile
        self.__flagIsNewFile = 1
        
        print 'Writing the file: %s'%self.filename
        
        self.__writeFirstHeader()
        
        return 1
    
    def __setNewBlock(self):
        
        if self.__fp == None:
            self.__setNextFile()
        
        if self.__flagIsNewFile:
            return 1
        
        if self.__blocksCounter < self.m_ProcessingHeader.dataBlocksPerFile:
            self.__writeBasicHeader()
            return 1
        
        if not(self.__setNextFile()):
            return 0
        
        return 1
    
    def __writeBlock(self):
        
        data = numpy.zeros(self.__shapeBuffer, self.__dataType)
        
        data['real'] = self.datablock.real
        data['imag'] = self.datablock.imag
        
        data = data.reshape((-1))
            
        data.tofile(self.__fp)
        
        self.datablock.fill(0)
        
        self.datablock_id = 0 
        
        self.__flagIsNewFile = 0
        
        self.flagIsNewBlock = 1
        
        self.nWriteBlocks += 1
        
        self.__blocksCounter += 1
    

    def writeNextBlock(self):
        
        if not(self.__setNewBlock()):
            return 0
        
        self.__writeBlock()
        
        return 1

    def __hasAllDataInBuffer(self):
        if self.datablock_id >= self.m_ProcessingHeader.profilesPerBlock:
            return 1
        
        return 0

    def putData(self):
        
        self.flagIsNewBlock = 0
        
        if self.m_Voltage.flagNoData:
            return 0
        
        if self.m_Voltage.flagResetProcessing:
            
            self.datablock.fill(0)
            
            self.datablock_id = 0
            self.__setNextFile()
        
        self.datablock[self.datablock_id,:,:] = self.m_Voltage.data
        
        self.datablock_id += 1
        
        if self.__hasAllDataInBuffer():
                     
            self.__getHeader()
            self.writeNextBlock()
        
        if self.noMoreFiles:
            #print 'Process finished'
            return 0
        
        return 1

    def __getHeader(self):
        self.m_BasicHeader = self.m_Voltage.m_BasicHeader.copy()
        self.m_SystemHeader = self.m_Voltage.m_SystemHeader.copy()
        self.m_RadarControllerHeader = self.m_Voltage.m_RadarControllerHeader.copy()
        self.m_ProcessingHeader = self.m_Voltage.m_ProcessingHeader.copy()
        self.__dataType = self.m_Voltage.dataType
            
    def __setHeaderByFile(self): 
         
        format = self.__format
        header = ['Basic','System','RadarController','Processing']                       
        
        fmtFromFile = None
        headerFromFile = None  

        
        fileTable = self.__configHeaderFile
        
        if os.access(fileTable, os.R_OK):
            import re, string
            
            f = open(fileTable,'r')
            lines = f.read()
            f.close()
            
            #Delete comments into expConfig
            while 1:
                
                startComment = string.find(lines.lower(),'#')
                if startComment == -1:
                    break
                endComment = string.find(lines.lower(),'\n',startComment)
                lines = string.replace(lines,lines[startComment:endComment+1],'', 1)
            
            while expFromFile == None:

                currFmt = string.find(lines.lower(),'format="%s"' %(expName))
                nextFmt = string.find(lines.lower(),'format',currFmt+10)
                                   
                if currFmt == -1:
                    break
                if nextFmt == -1:
                    nextFmt = len(lines)-1  
                             
                fmtTable = lines[currFmt:nextFmt]
                lines = lines[nextFmt:]    
                
                fmtRead = self.__getValueFromArg(fmtTable,'format')                
                if fmtRead != format:
                    continue                
                fmtFromFile = fmtRead
                
                lines2 = fmtTable
                
                while headerFromFile == None:
                    
                    currHeader = string.find(lines2.lower(),'header="%s"' %(header))
                    nextHeader = string.find(lines2.lower(),'header',currHeader+10) 
                    
                    if currHeader == -1:
                        break
                    if nextHeader == -1:
                        nextHeader = len(lines2)-1
                                        
                    headerTable = lines2[currHeader:nextHeader]
                    lines2 = lines2[nextHeader:]
                    
                    headerRead = self.__getValueFromArg(headerTable,'site')                
                    if not(headerRead in header):
                        continue                
                    headerFromFile = headerRead
                    
                    if headerRead == 'Basic':
                        self.m_BasicHeader.size = self.__getValueFromArg(headerTable,'size',lower=False)
                        self.m_BasicHeader.version = self.__getValueFromArg(headerTable,'version',lower=False)
                        self.m_BasicHeader.dataBlock = self.__getValueFromArg(headerTable,'dataBlock',lower=False)
                        self.m_BasicHeader.utc = self.__getValueFromArg(headerTable,'utc',lower=False)
                        self.m_BasicHeader.miliSecond = self.__getValueFromArg(headerTable,'miliSecond',lower=False)
                        self.m_BasicHeader.timeZone = self.__getValueFromArg(headerTable,'timeZone',lower=False)
                        self.m_BasicHeader.dstFlag = self.__getValueFromArg(headerTable,'dstFlag',lower=False)
                        self.m_BasicHeader.errorCount = self.__getValueFromArg(headerTable,'errorCount',lower=False)

        else:
            print "file access denied:%s"%fileTable
            sys.exit(0)

    def setup(self, path, set=0, format='rawdata'):
        
        
        if format == 'hdf5':
            ext = '.hdf5'
            format = 'hdf5'
            print 'call hdf5 library'
            return 0
        
        if format == 'rawdata':
            ext = '.r'
            format = 'Jicamarca'
        
        #call to config_headers
        #self.__setHeaderByFile()
        
        self.__path = path
        self.__setFile = set - 1
        self.__ext = ext
        self.__format = format
        
        self.__getHeader()
        self.__shapeBuffer =  (self.m_ProcessingHeader.profilesPerBlock,
                               self.m_ProcessingHeader.numHeights,
                               self.m_SystemHeader.numChannels )
            
        self.datablock = numpy.zeros(self.__shapeBuffer, numpy.dtype('complex'))
        
#        if not(self.__setNextFile()):
#            return 0
        return 1
        
            
        
        
    