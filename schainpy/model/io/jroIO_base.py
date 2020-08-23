"""
Created on Jul 2, 2014

@author: roj-idl71
"""
import os
import sys
import glob
import time
import numpy
import fnmatch
import inspect
import time
import datetime
import zmq

from schainpy.model.proc.jroproc_base import Operation, MPDecorator
from schainpy.model.data.jroheaderIO import PROCFLAG, BasicHeader, SystemHeader, RadarControllerHeader, ProcessingHeader
from schainpy.model.data.jroheaderIO import get_dtype_index, get_numpy_dtype, get_procflag_dtype, get_dtype_width
from schainpy.utils import log
import schainpy.admin

LOCALTIME = True
DT_DIRECTIVES = {
    '%Y': 4,
    '%y': 2,
    '%m': 2,
    '%d': 2,
    '%j': 3,
    '%H': 2,
    '%M': 2,
    '%S': 2,
    '%f': 6
}


def isNumber(cad):
    """
    Chequea si el conjunto de caracteres que componen un string puede ser convertidos a un numero.

    Excepciones:
        Si un determinado string no puede ser convertido a numero
    Input:
        str, string al cual se le analiza para determinar si convertible a un numero o no

    Return:
        True    :    si el string es uno numerico
        False   :    no es un string numerico
    """
    try:
        float(cad)
        return True
    except:
        return False


def isFileInEpoch(filename, startUTSeconds, endUTSeconds):
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
    basicHeaderObj = BasicHeader(LOCALTIME)

    try:
        fp = open(filename, 'rb')
    except IOError:
        print("The file %s can't be opened" % (filename))
        return 0

    sts = basicHeaderObj.read(fp)
    fp.close()

    if not(sts):
        print("Skipping the file %s because it has not a valid header" % (filename))
        return 0

    if not ((startUTSeconds <= basicHeaderObj.utc) and (endUTSeconds > basicHeaderObj.utc)):
        return 0

    return 1


def isTimeInRange(thisTime, startTime, endTime):
    if endTime >= startTime:
        if (thisTime < startTime) or (thisTime > endTime):
            return 0
        return 1
    else:
        if (thisTime < startTime) and (thisTime > endTime):
            return 0
        return 1


def isFileInTimeRange(filename, startDate, endDate, startTime, endTime):
    """
    Retorna 1 si el archivo de datos se encuentra dentro del rango de horas especificado.

    Inputs:
        filename            :    nombre completo del archivo de datos en formato Jicamarca (.r)

        startDate          :    fecha inicial del rango seleccionado en formato datetime.date

        endDate            :    fecha final del rango seleccionado en formato datetime.date

        startTime          :    tiempo inicial del rango seleccionado en formato datetime.time

        endTime            :    tiempo final del rango seleccionado en formato datetime.time

    Return:
        Boolean    :    Retorna True si el archivo de datos contiene datos en el rango de
                        fecha especificado, de lo contrario retorna False.

    Excepciones:
        Si el archivo no existe o no puede ser abierto
        Si la cabecera no puede ser leida.

    """

    try:
        fp = open(filename, 'rb')
    except IOError:
        print("The file %s can't be opened" % (filename))
        return None

    firstBasicHeaderObj = BasicHeader(LOCALTIME)
    systemHeaderObj = SystemHeader()
    radarControllerHeaderObj = RadarControllerHeader()
    processingHeaderObj = ProcessingHeader()

    lastBasicHeaderObj = BasicHeader(LOCALTIME)

    sts = firstBasicHeaderObj.read(fp)

    if not(sts):
        print("[Reading] Skipping the file %s because it has not a valid header" % (filename))
        return None

    if not systemHeaderObj.read(fp):
        return None

    if not radarControllerHeaderObj.read(fp):
        return None

    if not processingHeaderObj.read(fp):
        return None

    filesize = os.path.getsize(filename)

    offset = processingHeaderObj.blockSize + 24  # header size

    if filesize <= offset:
        print("[Reading] %s: This file has not enough data" % filename)
        return None

    fp.seek(-offset, 2)

    sts = lastBasicHeaderObj.read(fp)

    fp.close()

    thisDatetime = lastBasicHeaderObj.datatime
    thisTime_last_block = thisDatetime.time()

    thisDatetime = firstBasicHeaderObj.datatime
    thisDate = thisDatetime.date()
    thisTime_first_block = thisDatetime.time()

    # General case
    #           o>>>>>>>>>>>>>><<<<<<<<<<<<<<o
    #-----------o----------------------------o-----------
    #       startTime                     endTime

    if endTime >= startTime:
        if (thisTime_last_block < startTime) or (thisTime_first_block > endTime):
            return None

        return thisDatetime

    # If endTime < startTime then endTime belongs to the next day

    #<<<<<<<<<<<o                            o>>>>>>>>>>>
    #-----------o----------------------------o-----------
    #        endTime                    startTime

    if (thisDate == startDate) and (thisTime_last_block < startTime):
        return None

    if (thisDate == endDate) and (thisTime_first_block > endTime):
        return None

    if (thisTime_last_block < startTime) and (thisTime_first_block > endTime):
        return None

    return thisDatetime


def isFolderInDateRange(folder, startDate=None, endDate=None):
    """
    Retorna 1 si el archivo de datos se encuentra dentro del rango de horas especificado.

    Inputs:
        folder            :    nombre completo del directorio.
                               Su formato deberia ser "/path_root/?YYYYDDD"

                                siendo:
                                    YYYY    :    Anio         (ejemplo 2015)
                                    DDD     :    Dia del anio (ejemplo 305)

        startDate          :    fecha inicial del rango seleccionado en formato datetime.date

        endDate            :    fecha final del rango seleccionado en formato datetime.date

    Return:
        Boolean    :    Retorna True si el archivo de datos contiene datos en el rango de
                        fecha especificado, de lo contrario retorna False.
    Excepciones:
        Si el directorio no tiene el formato adecuado
    """

    basename = os.path.basename(folder)

    if not isRadarFolder(basename):
        print("The folder %s has not the rigth format" % folder)
        return 0

    if startDate and endDate:
        thisDate = getDateFromRadarFolder(basename)

        if thisDate < startDate:
            return 0

        if thisDate > endDate:
            return 0

    return 1


def isFileInDateRange(filename, startDate=None, endDate=None):
    """
    Retorna 1 si el archivo de datos se encuentra dentro del rango de horas especificado.

    Inputs:
        filename            :    nombre completo del archivo de datos en formato Jicamarca (.r)

                               Su formato deberia ser "?YYYYDDDsss"

                                siendo:
                                    YYYY    :    Anio         (ejemplo 2015)
                                    DDD     :    Dia del anio (ejemplo 305)
                                    sss     :    set

        startDate          :    fecha inicial del rango seleccionado en formato datetime.date

        endDate            :    fecha final del rango seleccionado en formato datetime.date

    Return:
        Boolean    :    Retorna True si el archivo de datos contiene datos en el rango de
                        fecha especificado, de lo contrario retorna False.
    Excepciones:
        Si el archivo no tiene el formato adecuado
    """

    basename = os.path.basename(filename)

    if not isRadarFile(basename):
        print("The filename %s has not the rigth format" % filename)
        return 0

    if startDate and endDate:
        thisDate = getDateFromRadarFile(basename)

        if thisDate < startDate:
            return 0

        if thisDate > endDate:
            return 0

    return 1


def getFileFromSet(path, ext, set):
    validFilelist = []
    fileList = os.listdir(path)

    # 0 1234 567 89A BCDE
    # H YYYY DDD SSS .ext

    for thisFile in fileList:
        try:
            year = int(thisFile[1:5])
            doy = int(thisFile[5:8])
        except:
            continue

        if (os.path.splitext(thisFile)[-1].lower() != ext.lower()):
            continue

        validFilelist.append(thisFile)

    myfile = fnmatch.filter(
        validFilelist, '*%4.4d%3.3d%3.3d*' % (year, doy, set))

    if len(myfile) != 0:
        return myfile[0]
    else:
        filename = '*%4.4d%3.3d%3.3d%s' % (year, doy, set, ext.lower())
        print('the filename %s does not exist' % filename)
        print('...going to the last file: ')

    if validFilelist:
        validFilelist = sorted(validFilelist, key=str.lower)
        return validFilelist[-1]

    return None


def getlastFileFromPath(path, ext):
    """
    Depura el fileList dejando solo los que cumplan el formato de "PYYYYDDDSSS.ext"
    al final de la depuracion devuelve el ultimo file de la lista que quedo.

    Input:
        fileList    :    lista conteniendo todos los files (sin path) que componen una determinada carpeta
        ext         :    extension de los files contenidos en una carpeta

    Return:
        El ultimo file de una determinada carpeta, no se considera el path.
    """
    validFilelist = []
    fileList = os.listdir(path)

    # 0 1234 567 89A BCDE
    # H YYYY DDD SSS .ext

    for thisFile in fileList:

        year = thisFile[1:5]
        if not isNumber(year):
            continue

        doy = thisFile[5:8]
        if not isNumber(doy):
            continue

        year = int(year)
        doy = int(doy)

        if (os.path.splitext(thisFile)[-1].lower() != ext.lower()):
            continue

        validFilelist.append(thisFile)

    if validFilelist:
        validFilelist = sorted(validFilelist, key=str.lower)
        return validFilelist[-1]

    return None


def isRadarFolder(folder):
    try:
        year = int(folder[1:5])
        doy = int(folder[5:8])
    except:
        return 0

    return 1


def isRadarFile(file):
    try:        
        year = int(file[1:5])
        doy = int(file[5:8])
        set = int(file[8:11])
    except:
        return 0

    return 1


def getDateFromRadarFile(file):
    try:    
        year = int(file[1:5])
        doy = int(file[5:8])
        set = int(file[8:11])    
    except:
        return None

    thisDate = datetime.date(year, 1, 1) + datetime.timedelta(doy - 1)
    return thisDate


def getDateFromRadarFolder(folder):
    try:
        year = int(folder[1:5])
        doy = int(folder[5:8])
    except:
        return None

    thisDate = datetime.date(year, 1, 1) + datetime.timedelta(doy - 1)
    return thisDate

def parse_format(s, fmt):
    
    for i in range(fmt.count('%')):
        x = fmt.index('%')
        d = DT_DIRECTIVES[fmt[x:x+2]]
        fmt = fmt.replace(fmt[x:x+2], s[x:x+d])
    return fmt

class Reader(object):

    c = 3E8
    isConfig = False
    dtype = None
    pathList = []
    filenameList = []
    datetimeList = []
    filename = None
    ext = None
    flagIsNewFile = 1
    flagDiscontinuousBlock = 0
    flagIsNewBlock = 0
    flagNoMoreFiles = 0
    fp = None
    firstHeaderSize = 0
    basicHeaderSize = 24
    versionFile = 1103
    fileSize = None
    fileSizeByHeader = None
    fileIndex = -1
    profileIndex = None
    blockIndex = 0
    nTotalBlocks = 0
    maxTimeStep = 30
    lastUTTime = None
    datablock = None
    dataOut = None
    getByBlock = False
    path = None
    startDate = None
    endDate = None
    startTime = datetime.time(0, 0, 0)
    endTime = datetime.time(23, 59, 59)
    set = None
    expLabel = ""
    online = False
    delay = 60
    nTries = 3  # quantity tries
    nFiles = 3  # number of files for searching
    walk = True
    getblock = False
    nTxs = 1
    realtime = False
    blocksize = 0
    blocktime = None
    warnings = True
    verbose = True
    server = None
    format = None
    oneDDict = None
    twoDDict = None
    independentParam = None
    filefmt = None
    folderfmt = None
    open_file = open
    open_mode = 'rb'

    def run(self):

        raise NotImplementedError    

    def getAllowedArgs(self):
        if hasattr(self, '__attrs__'):
            return self.__attrs__
        else:
            return inspect.getargspec(self.run).args

    def set_kwargs(self, **kwargs):

        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def find_folders(self, path, startDate, endDate, folderfmt, last=False):

        folders = [x for f in path.split(',') 
                   for x in os.listdir(f) if os.path.isdir(os.path.join(f, x))]
        folders.sort()

        if last:
            folders = [folders[-1]]

        for folder in folders:            
            try:                
                dt = datetime.datetime.strptime(parse_format(folder, folderfmt), folderfmt).date()                
                if dt >= startDate and dt <= endDate:
                    yield os.path.join(path, folder)
                else:
                    log.log('Skiping folder {}'.format(folder), self.name)
            except Exception as e:
                log.log('Skiping folder {}'.format(folder), self.name)
                continue
        return
    
    def find_files(self, folders, ext, filefmt, startDate=None, endDate=None, 
                   expLabel='', last=False):
        
        for path in folders:            
            files = glob.glob1(path, '*{}'.format(ext))
            files.sort()
            if last:
                if files:                    
                    fo = files[-1]
                    try:                
                        dt = datetime.datetime.strptime(parse_format(fo, filefmt), filefmt).date()
                        yield os.path.join(path, expLabel, fo)                            
                    except Exception as e:                        
                        pass
                    return
                else:
                    return

            for fo in files:
                try:                
                    dt = datetime.datetime.strptime(parse_format(fo, filefmt), filefmt).date()                
                    if dt >= startDate and dt <= endDate:
                        yield os.path.join(path, expLabel, fo)
                    else:
                        log.log('Skiping file {}'.format(fo), self.name)
                except Exception as e:
                    log.log('Skiping file {}'.format(fo), self.name)
                    continue        

    def searchFilesOffLine(self, path, startDate, endDate,
                           expLabel, ext, walk, 
                           filefmt, folderfmt):
        """Search files in offline mode for the given arguments

        Return:
            Generator of files
        """

        if walk:
            folders = self.find_folders(
                path, startDate, endDate, folderfmt)
        else:
            folders = path.split(',')
        
        return self.find_files(
            folders, ext, filefmt, startDate, endDate, expLabel)        

    def searchFilesOnLine(self, path, startDate, endDate,
                          expLabel, ext, walk, 
                          filefmt, folderfmt):
        """Search for the last file of the last folder

        Arguments:
            path        :    carpeta donde estan contenidos los files que contiene data
            expLabel    :    Nombre del subexperimento (subfolder)
            ext         :    extension de los files
            walk        :    Si es habilitado no realiza busquedas dentro de los ubdirectorios (doypath)

        Return:
            generator with the full path of last filename
        """
     
        if walk:
            folders = self.find_folders(
                path, startDate, endDate, folderfmt, last=True)
        else:
            folders = path.split(',')
        
        return self.find_files(
            folders, ext, filefmt, startDate, endDate, expLabel, last=True)

    def setNextFile(self):
        """Set the next file to be readed open it and parse de file header"""

        while True:
            if self.fp != None:
                self.fp.close()            

            if self.online:
                newFile = self.setNextFileOnline()
            else:
                newFile = self.setNextFileOffline()
            
            if not(newFile):
                if self.online:
                    raise schainpy.admin.SchainError('Time to wait for new files reach')
                else:
                    if self.fileIndex == -1:
                        raise schainpy.admin.SchainWarning('No files found in the given path')
                    else:
                        raise schainpy.admin.SchainWarning('No more files to read')
            
            if self.verifyFile(self.filename):
                break
        
        log.log('Opening file: %s' % self.filename, self.name)

        self.readFirstHeader()
        self.nReadBlocks = 0

    def setNextFileOnline(self):
        """Check for the next file to be readed in online mode.

        Set:
            self.filename
            self.fp
            self.filesize
        
        Return:
            boolean

        """
        nextFile = True
        nextDay = False

        for nFiles in range(self.nFiles+1):            
            for nTries in range(self.nTries):
                fullfilename, filename = self.checkForRealPath(nextFile, nextDay)
                if fullfilename is not None:
                    break
                log.warning(
                    "Waiting %0.2f sec for the next file: \"%s\" , try %02d ..." % (self.delay, filename, nTries + 1),
                    self.name)
                time.sleep(self.delay)
                nextFile = False
                continue                
            
            if fullfilename is not None:
                break
            
            self.nTries = 1
            nextFile = True            

            if nFiles == (self.nFiles - 1):
                log.log('Trying with next day...', self.name)
                nextDay = True
                self.nTries = 3          

        if fullfilename:
            self.fileSize = os.path.getsize(fullfilename)
            self.filename = fullfilename
            self.flagIsNewFile = 1
            if self.fp != None:
                self.fp.close()
            self.fp = self.open_file(fullfilename, self.open_mode)
            self.flagNoMoreFiles = 0
            self.fileIndex += 1
            return 1
        else:            
            return 0
    
    def setNextFileOffline(self):
        """Open the next file to be readed in offline mode"""
                
        try:
            filename = next(self.filenameList)
            self.fileIndex +=1
        except StopIteration:
            self.flagNoMoreFiles = 1
            return 0        

        self.filename = filename
        self.fileSize = os.path.getsize(filename)
        self.fp = self.open_file(filename, self.open_mode)
        self.flagIsNewFile = 1

        return 1
    
    @staticmethod
    def isDateTimeInRange(dt, startDate, endDate, startTime, endTime):
        """Check if the given datetime is in range"""
        
        if startDate <= dt.date() <= endDate:
            if startTime <= dt.time() <= endTime:
                return True
        return False
    
    def verifyFile(self, filename):
        """Check for a valid file
        
        Arguments:
            filename -- full path filename
        
        Return:
            boolean
        """

        return True

    def checkForRealPath(self, nextFile, nextDay):
        """Check if the next file to be readed exists"""

        raise NotImplementedError
    
    def readFirstHeader(self):
        """Parse the file header"""

        pass

    def waitDataBlock(self, pointer_location, blocksize=None):
        """
        """

        currentPointer = pointer_location
        if blocksize is None:
            neededSize = self.processingHeaderObj.blockSize  # + self.basicHeaderSize
        else:
            neededSize = blocksize

        for nTries in range(self.nTries):
            self.fp.close()
            self.fp = open(self.filename, 'rb')
            self.fp.seek(currentPointer)

            self.fileSize = os.path.getsize(self.filename)
            currentSize = self.fileSize - currentPointer

            if (currentSize >= neededSize):
                return 1

            log.warning(
                "Waiting %0.2f seconds for the next block, try %03d ..." % (self.delay, nTries + 1),
                self.name
                )
            time.sleep(self.delay)

        return 0

class JRODataReader(Reader):

    utc = 0
    nReadBlocks = 0
    foldercounter = 0
    firstHeaderSize = 0
    basicHeaderSize = 24
    __isFirstTimeOnline = 1
    filefmt = "*%Y%j***"
    folderfmt = "*%Y%j"
    __attrs__ = ['path', 'startDate', 'endDate', 'startTime', 'endTime', 'online', 'delay', 'walk']

    def getDtypeWidth(self):

        dtype_index = get_dtype_index(self.dtype)
        dtype_width = get_dtype_width(dtype_index)

        return dtype_width

    def checkForRealPath(self, nextFile, nextDay):
        """Check if the next file to be readed exists.

        Example    :
            nombre correcto del file es  .../.../D2009307/P2009307367.ext

            Entonces la funcion prueba con las siguientes combinaciones
                .../.../y2009307367.ext
                .../.../Y2009307367.ext
                .../.../x2009307/y2009307367.ext
                .../.../x2009307/Y2009307367.ext
                .../.../X2009307/y2009307367.ext
                .../.../X2009307/Y2009307367.ext
            siendo para este caso, la ultima combinacion de letras, identica al file buscado

        Return:
            str -- fullpath of the file
        """
        
        
        if nextFile:
            self.set += 1
        if nextDay:
            self.set = 0
            self.doy += 1
        foldercounter = 0
        prefixDirList = [None, 'd', 'D']
        if self.ext.lower() == ".r":  # voltage
            prefixFileList = ['d', 'D']
        elif self.ext.lower() == ".pdata":  # spectra
            prefixFileList = ['p', 'P']
        
        # barrido por las combinaciones posibles
        for prefixDir in prefixDirList:
            thispath = self.path
            if prefixDir != None:
                # formo el nombre del directorio xYYYYDDD (x=d o x=D)
                if foldercounter == 0:
                    thispath = os.path.join(self.path, "%s%04d%03d" %
                                            (prefixDir, self.year, self.doy))
                else:
                    thispath = os.path.join(self.path, "%s%04d%03d_%02d" % (
                        prefixDir, self.year, self.doy, foldercounter))
            for prefixFile in prefixFileList:  # barrido por las dos combinaciones posibles de "D"
                # formo el nombre del file xYYYYDDDSSS.ext
                filename = "%s%04d%03d%03d%s" % (prefixFile, self.year, self.doy, self.set, self.ext)
                fullfilename = os.path.join(
                    thispath, filename)

                if os.path.exists(fullfilename):
                    return fullfilename, filename
            
        return None, filename    
    
    def __waitNewBlock(self):
        """
        Return 1 si se encontro un nuevo bloque de datos, 0 de otra forma.

        Si el modo de lectura es OffLine siempre retorn 0
        """
        if not self.online:
            return 0

        if (self.nReadBlocks >= self.processingHeaderObj.dataBlocksPerFile):
            return 0

        currentPointer = self.fp.tell()

        neededSize = self.processingHeaderObj.blockSize + self.basicHeaderSize

        for nTries in range(self.nTries):

            self.fp.close()
            self.fp = open(self.filename, 'rb')
            self.fp.seek(currentPointer)

            self.fileSize = os.path.getsize(self.filename)
            currentSize = self.fileSize - currentPointer

            if (currentSize >= neededSize):
                self.basicHeaderObj.read(self.fp)
                return 1

            if self.fileSize == self.fileSizeByHeader:
                #                self.flagEoF = True
                return 0

            print("[Reading] Waiting %0.2f seconds for the next block, try %03d ..." % (self.delay, nTries + 1))
            time.sleep(self.delay)

        return 0

    def __setNewBlock(self):

        if self.fp == None:
            return 0 
        
        if self.flagIsNewFile:            
            self.lastUTTime = self.basicHeaderObj.utc
            return 1

        if self.realtime:
            self.flagDiscontinuousBlock = 1
            if not(self.setNextFile()):
                return 0
            else:
                return 1

        currentSize = self.fileSize - self.fp.tell()
        neededSize = self.processingHeaderObj.blockSize + self.basicHeaderSize
        
        if (currentSize >= neededSize):
            self.basicHeaderObj.read(self.fp)
            self.lastUTTime = self.basicHeaderObj.utc
            return 1
       
        if self.__waitNewBlock():
            self.lastUTTime = self.basicHeaderObj.utc
            return 1

        if not(self.setNextFile()):
            return 0

        deltaTime = self.basicHeaderObj.utc - self.lastUTTime
        self.lastUTTime = self.basicHeaderObj.utc

        self.flagDiscontinuousBlock = 0

        if deltaTime > self.maxTimeStep:
            self.flagDiscontinuousBlock = 1

        return 1

    def readNextBlock(self):

        while True:
            if not(self.__setNewBlock()):
                continue

            if not(self.readBlock()):
                return 0

            self.getBasicHeader()

            if not self.isDateTimeInRange(self.dataOut.datatime, self.startDate, self.endDate, self.startTime, self.endTime):
                print("[Reading] Block No. %d/%d -> %s [Skipping]" % (self.nReadBlocks,
                                                                      self.processingHeaderObj.dataBlocksPerFile,
                                                                      self.dataOut.datatime.ctime()))
                continue

            break

        if self.verbose:
            print("[Reading] Block No. %d/%d -> %s" % (self.nReadBlocks,
                                                       self.processingHeaderObj.dataBlocksPerFile,
                                                       self.dataOut.datatime.ctime()))
        return 1

    def readFirstHeader(self):

        self.basicHeaderObj.read(self.fp)
        self.systemHeaderObj.read(self.fp)
        self.radarControllerHeaderObj.read(self.fp)
        self.processingHeaderObj.read(self.fp)
        self.firstHeaderSize = self.basicHeaderObj.size

        datatype = int(numpy.log2((self.processingHeaderObj.processFlags &
                                   PROCFLAG.DATATYPE_MASK)) - numpy.log2(PROCFLAG.DATATYPE_CHAR))
        if datatype == 0:
            datatype_str = numpy.dtype([('real', '<i1'), ('imag', '<i1')])
        elif datatype == 1:
            datatype_str = numpy.dtype([('real', '<i2'), ('imag', '<i2')])
        elif datatype == 2:
            datatype_str = numpy.dtype([('real', '<i4'), ('imag', '<i4')])
        elif datatype == 3:
            datatype_str = numpy.dtype([('real', '<i8'), ('imag', '<i8')])
        elif datatype == 4:
            datatype_str = numpy.dtype([('real', '<f4'), ('imag', '<f4')])
        elif datatype == 5:
            datatype_str = numpy.dtype([('real', '<f8'), ('imag', '<f8')])
        else:
            raise ValueError('Data type was not defined')

        self.dtype = datatype_str
        #self.ippSeconds = 2 * 1000 * self.radarControllerHeaderObj.ipp / self.c
        self.fileSizeByHeader = self.processingHeaderObj.dataBlocksPerFile * self.processingHeaderObj.blockSize + \
            self.firstHeaderSize + self.basicHeaderSize * \
            (self.processingHeaderObj.dataBlocksPerFile - 1)
        #        self.dataOut.channelList = numpy.arange(self.systemHeaderObj.numChannels)
        #        self.dataOut.channelIndexList = numpy.arange(self.systemHeaderObj.numChannels)
        self.getBlockDimension()

    def verifyFile(self, filename):

        flag = True

        try:
            fp = open(filename, 'rb')
        except IOError:
            log.error("File {} can't be opened".format(filename), self.name)
            return False
        
        if self.online and self.waitDataBlock(0):
            pass
            
        basicHeaderObj = BasicHeader(LOCALTIME)
        systemHeaderObj = SystemHeader()
        radarControllerHeaderObj = RadarControllerHeader()
        processingHeaderObj = ProcessingHeader()

        if not(basicHeaderObj.read(fp)):
            flag = False
        if not(systemHeaderObj.read(fp)):
            flag = False
        if not(radarControllerHeaderObj.read(fp)):
            flag = False
        if not(processingHeaderObj.read(fp)):
            flag = False
        if not self.online:
            dt1 = basicHeaderObj.datatime
            pos = self.fileSize-processingHeaderObj.blockSize-24
            if pos<0:
                flag = False
                log.error('Invalid size for file: {}'.format(self.filename), self.name)
            else:
                fp.seek(pos)
                if not(basicHeaderObj.read(fp)):
                    flag = False
            dt2 = basicHeaderObj.datatime
            if not self.isDateTimeInRange(dt1, self.startDate, self.endDate, self.startTime, self.endTime) and not \
                    self.isDateTimeInRange(dt2, self.startDate, self.endDate, self.startTime, self.endTime):
                flag = False            

        fp.close()
        return flag

    def findDatafiles(self, path, startDate=None, endDate=None, expLabel='', ext='.r', walk=True, include_path=False):

        path_empty = True

        dateList = []
        pathList = []

        multi_path = path.split(',')

        if not walk:

            for single_path in multi_path:

                if not os.path.isdir(single_path):
                    continue

                fileList = glob.glob1(single_path, "*" + ext)

                if not fileList:
                    continue

                path_empty = False

                fileList.sort()

                for thisFile in fileList:

                    if not os.path.isfile(os.path.join(single_path, thisFile)):
                        continue

                    if not isRadarFile(thisFile):
                        continue

                    if not isFileInDateRange(thisFile, startDate, endDate):
                        continue

                    thisDate = getDateFromRadarFile(thisFile)

                    if thisDate in dateList or single_path in pathList:
                        continue

                    dateList.append(thisDate)
                    pathList.append(single_path)

        else:
            for single_path in multi_path:

                if not os.path.isdir(single_path):
                    continue

                dirList = []

                for thisPath in os.listdir(single_path):

                    if not os.path.isdir(os.path.join(single_path, thisPath)):
                        continue

                    if not isRadarFolder(thisPath):
                        continue

                    if not isFolderInDateRange(thisPath, startDate, endDate):
                        continue

                    dirList.append(thisPath)

                if not dirList:
                    continue

                dirList.sort()

                for thisDir in dirList:

                    datapath = os.path.join(single_path, thisDir, expLabel)
                    fileList = glob.glob1(datapath, "*" + ext)

                    if not fileList:
                        continue

                    path_empty = False

                    thisDate = getDateFromRadarFolder(thisDir)

                    pathList.append(datapath)
                    dateList.append(thisDate)

        dateList.sort()

        if walk:
            pattern_path = os.path.join(multi_path[0], "[dYYYYDDD]", expLabel)
        else:
            pattern_path = multi_path[0]

        if path_empty:
            raise schainpy.admin.SchainError("[Reading] No *%s files in %s for %s to %s" % (ext, pattern_path, startDate, endDate))
        else:
            if not dateList:
                raise schainpy.admin.SchainError("[Reading] Date range selected invalid [%s - %s]: No *%s files in %s)" % (startDate, endDate, ext, path))

        if include_path:
            return dateList, pathList

        return dateList

    def setup(self, **kwargs):
        
        self.set_kwargs(**kwargs)
        if not self.ext.startswith('.'):
            self.ext = '.{}'.format(self.ext)
        
        if self.server is not None:
            if 'tcp://' in self.server:
                address = server
            else:
                address = 'ipc:///tmp/%s' % self.server
            self.server = address
            self.context = zmq.Context()
            self.receiver = self.context.socket(zmq.PULL)
            self.receiver.connect(self.server)
            time.sleep(0.5)
            print('[Starting] ReceiverData from {}'.format(self.server))
        else:
            self.server = None
            if self.path == None:
                raise ValueError("[Reading] The path is not valid")

            if self.online:
                log.log("[Reading] Searching files in online mode...", self.name)

                for nTries in range(self.nTries):
                    fullpath = self.searchFilesOnLine(self.path, self.startDate,
                        self.endDate, self.expLabel, self.ext, self.walk, 
                        self.filefmt, self.folderfmt)

                    try:
                        fullpath = next(fullpath)
                    except:
                        fullpath = None
                    
                    if fullpath:
                        break

                    log.warning(
                        'Waiting {} sec for a valid file in {}: try {} ...'.format(
                            self.delay, self.path, nTries + 1), 
                        self.name)
                    time.sleep(self.delay)

                if not(fullpath):
                    raise schainpy.admin.SchainError(
                        'There isn\'t any valid file in {}'.format(self.path))                    

                pathname, filename = os.path.split(fullpath)
                self.year = int(filename[1:5])
                self.doy = int(filename[5:8])
                self.set = int(filename[8:11]) - 1                
            else:
                log.log("Searching files in {}".format(self.path), self.name)
                self.filenameList = self.searchFilesOffLine(self.path, self.startDate, 
                    self.endDate, self.expLabel, self.ext, self.walk, self.filefmt, self.folderfmt)
            
            self.setNextFile()

        return

    def getBasicHeader(self):

        self.dataOut.utctime = self.basicHeaderObj.utc + self.basicHeaderObj.miliSecond / \
            1000. + self.profileIndex * self.radarControllerHeaderObj.ippSeconds

        self.dataOut.flagDiscontinuousBlock = self.flagDiscontinuousBlock

        self.dataOut.timeZone = self.basicHeaderObj.timeZone

        self.dataOut.dstFlag = self.basicHeaderObj.dstFlag

        self.dataOut.errorCount = self.basicHeaderObj.errorCount

        self.dataOut.useLocalTime = self.basicHeaderObj.useLocalTime

        self.dataOut.ippSeconds = self.radarControllerHeaderObj.ippSeconds / self.nTxs

 #         self.dataOut.nProfiles = self.processingHeaderObj.profilesPerBlock*self.nTxs

    def getFirstHeader(self):

        raise NotImplementedError

    def getData(self):

        raise NotImplementedError

    def hasNotDataInBuffer(self):

        raise NotImplementedError

    def readBlock(self):

        raise NotImplementedError

    def isEndProcess(self):

        return self.flagNoMoreFiles

    def printReadBlocks(self):

        print("[Reading] Number of read blocks per file %04d" % self.nReadBlocks)

    def printTotalBlocks(self):

        print("[Reading] Number of read blocks %04d" % self.nTotalBlocks)

    def run(self, **kwargs):
        """

        Arguments:
            path        : 
            startDate   : 
            endDate     :
            startTime   :
            endTime     :
            set         :
            expLabel    :
            ext         :
            online      :
            delay       :
            walk        :
            getblock    :
            nTxs        :
            realtime    :
            blocksize   :
            blocktime   :
            skip        :
            cursor      :
            warnings    :
            server      :
            verbose     :
            format      :
            oneDDict    :
            twoDDict    :
            independentParam    :
        """

        if not(self.isConfig):
            self.setup(**kwargs)
            self.isConfig = True
        if self.server is None:
            self.getData()
        else:
            self.getFromServer()


class JRODataWriter(Reader):

    """
    Esta clase permite escribir datos a archivos procesados (.r o ,pdata). La escritura
    de los datos siempre se realiza por bloques.
    """

    setFile = None
    profilesPerBlock = None
    blocksPerFile = None
    nWriteBlocks = 0
    fileDate = None

    def __init__(self, dataOut=None):
        raise NotImplementedError

    def hasAllDataInBuffer(self):
        raise NotImplementedError

    def setBlockDimension(self):
        raise NotImplementedError

    def writeBlock(self):
        raise NotImplementedError

    def putData(self):
        raise NotImplementedError

    def getDtypeWidth(self):

        dtype_index = get_dtype_index(self.dtype)
        dtype_width = get_dtype_width(dtype_index)

        return dtype_width
    
    def getProcessFlags(self):

        processFlags = 0

        dtype_index = get_dtype_index(self.dtype)
        procflag_dtype = get_procflag_dtype(dtype_index)

        processFlags += procflag_dtype

        if self.dataOut.flagDecodeData:
            processFlags += PROCFLAG.DECODE_DATA

        if self.dataOut.flagDeflipData:
            processFlags += PROCFLAG.DEFLIP_DATA

        if self.dataOut.code is not None:
            processFlags += PROCFLAG.DEFINE_PROCESS_CODE

        if self.dataOut.nCohInt > 1:
            processFlags += PROCFLAG.COHERENT_INTEGRATION

        if self.dataOut.type == "Spectra":
            if self.dataOut.nIncohInt > 1:
                processFlags += PROCFLAG.INCOHERENT_INTEGRATION

            if self.dataOut.data_dc is not None:
                processFlags += PROCFLAG.SAVE_CHANNELS_DC

            if self.dataOut.flagShiftFFT:
                processFlags += PROCFLAG.SHIFT_FFT_DATA

        return processFlags

    def setBasicHeader(self):

        self.basicHeaderObj.size = self.basicHeaderSize  # bytes
        self.basicHeaderObj.version = self.versionFile
        self.basicHeaderObj.dataBlock = self.nTotalBlocks        
        utc = numpy.floor(self.dataOut.utctime)
        milisecond = (self.dataOut.utctime - utc) * 1000.0        
        self.basicHeaderObj.utc = utc
        self.basicHeaderObj.miliSecond = milisecond
        self.basicHeaderObj.timeZone = self.dataOut.timeZone
        self.basicHeaderObj.dstFlag = self.dataOut.dstFlag
        self.basicHeaderObj.errorCount = self.dataOut.errorCount

    def setFirstHeader(self):
        """
        Obtiene una copia del First Header

        Affected:

            self.basicHeaderObj
            self.systemHeaderObj
            self.radarControllerHeaderObj
            self.processingHeaderObj self.

        Return:
            None
        """

        raise NotImplementedError

    def __writeFirstHeader(self):
        """
        Escribe el primer header del file es decir el Basic header y el Long header (SystemHeader, RadarControllerHeader, ProcessingHeader)

        Affected:
            __dataType

        Return:
            None
        """

#        CALCULAR PARAMETROS

        sizeLongHeader = self.systemHeaderObj.size + \
            self.radarControllerHeaderObj.size + self.processingHeaderObj.size
        self.basicHeaderObj.size = self.basicHeaderSize + sizeLongHeader

        self.basicHeaderObj.write(self.fp)
        self.systemHeaderObj.write(self.fp)
        self.radarControllerHeaderObj.write(self.fp)
        self.processingHeaderObj.write(self.fp)

    def __setNewBlock(self):
        """
        Si es un nuevo file escribe el First Header caso contrario escribe solo el Basic Header

        Return:
            0    :    si no pudo escribir nada
            1    :    Si escribio el Basic el First Header
        """
        if self.fp == None:
            self.setNextFile()

        if self.flagIsNewFile:
            return 1

        if self.blockIndex < self.processingHeaderObj.dataBlocksPerFile:
            self.basicHeaderObj.write(self.fp)
            return 1

        if not(self.setNextFile()):
            return 0

        return 1

    def writeNextBlock(self):
        """
        Selecciona el bloque siguiente de datos y los escribe en un file

        Return:
            0    :    Si no hizo pudo escribir el bloque de datos
            1    :    Si no pudo escribir el bloque de datos
        """
        if not(self.__setNewBlock()):
            return 0

        self.writeBlock()

        print("[Writing] Block No. %d/%d" % (self.blockIndex,
                                             self.processingHeaderObj.dataBlocksPerFile))

        return 1

    def setNextFile(self):
        """Determina el siguiente file que sera escrito

        Affected:
            self.filename
            self.subfolder
            self.fp
            self.setFile
            self.flagIsNewFile

        Return:
            0    :    Si el archivo no puede ser escrito
            1    :    Si el archivo esta listo para ser escrito
        """
        ext = self.ext
        path = self.path

        if self.fp != None:
            self.fp.close()

        if not os.path.exists(path):
            os.mkdir(path)

        timeTuple = time.localtime(self.dataOut.utctime)
        subfolder = 'd%4.4d%3.3d' % (timeTuple.tm_year, timeTuple.tm_yday)

        fullpath = os.path.join(path, subfolder)
        setFile = self.setFile

        if not(os.path.exists(fullpath)):
            os.mkdir(fullpath)
            setFile = -1  # inicializo mi contador de seteo
        else:
            filesList = os.listdir(fullpath)
            if len(filesList) > 0:
                filesList = sorted(filesList, key=str.lower)
                filen = filesList[-1]
                # el filename debera tener el siguiente formato
                # 0 1234 567 89A BCDE (hex)
                # x YYYY DDD SSS .ext
                if isNumber(filen[8:11]):
                    # inicializo mi contador de seteo al seteo del ultimo file
                    setFile = int(filen[8:11])
                else:
                    setFile = -1
            else:
                setFile = -1  # inicializo mi contador de seteo

        setFile += 1

        # If this is a new day it resets some values
        if self.dataOut.datatime.date() > self.fileDate:
            setFile = 0
            self.nTotalBlocks = 0
        
        filen = '{}{:04d}{:03d}{:03d}{}'.format(
                self.optchar, timeTuple.tm_year, timeTuple.tm_yday, setFile, ext)        

        filename = os.path.join(path, subfolder, filen)

        fp = open(filename, 'wb')

        self.blockIndex = 0
        self.filename = filename
        self.subfolder = subfolder
        self.fp = fp
        self.setFile = setFile
        self.flagIsNewFile = 1
        self.fileDate = self.dataOut.datatime.date()
        self.setFirstHeader()

        print('[Writing] Opening file: %s' % self.filename)

        self.__writeFirstHeader()

        return 1

    def setup(self, dataOut, path, blocksPerFile, profilesPerBlock=64, set=None, ext=None, datatype=4):
        """
        Setea el tipo de formato en la cual sera guardada la data y escribe el First Header

        Inputs:
            path                :    directory where data will be saved
            profilesPerBlock    :    number of profiles per block
            set                 :    initial file set
            datatype            :    An integer number that defines data type:
                                        0 : int8  (1 byte)
                                        1 : int16 (2 bytes)
                                        2 : int32 (4 bytes)
                                        3 : int64 (8 bytes)
                                        4 : float32 (4 bytes)
                                        5 : double64 (8 bytes)

        Return:
            0    :    Si no realizo un buen seteo
            1    :    Si realizo un buen seteo
        """

        if ext == None:
            ext = self.ext

        self.ext = ext.lower()

        self.path = path
        
        if set is None:
            self.setFile = -1
        else:
            self.setFile = set - 1        

        self.blocksPerFile = blocksPerFile
        self.profilesPerBlock = profilesPerBlock
        self.dataOut = dataOut
        self.fileDate = self.dataOut.datatime.date()
        self.dtype = self.dataOut.dtype

        if datatype is not None:
            self.dtype = get_numpy_dtype(datatype)

        if not(self.setNextFile()):
            print("[Writing] There isn't a next file")
            return 0

        self.setBlockDimension()

        return 1

    def run(self, dataOut, path, blocksPerFile=100, profilesPerBlock=64, set=None, ext=None, datatype=4, **kwargs):

        if not(self.isConfig):

            self.setup(dataOut, path, blocksPerFile, profilesPerBlock=profilesPerBlock,
                       set=set, ext=ext, datatype=datatype, **kwargs)
            self.isConfig = True

        self.dataOut = dataOut
        self.putData()
        return self.dataOut

@MPDecorator
class printInfo(Operation):

    def __init__(self):

        Operation.__init__(self)
        self.__printInfo = True

    def run(self, dataOut, headers = ['systemHeaderObj', 'radarControllerHeaderObj', 'processingHeaderObj']):
        if self.__printInfo == False:
            return

        for header in headers:
            if hasattr(dataOut, header):
                obj = getattr(dataOut, header)
                if hasattr(obj, 'printInfo'):
                    obj.printInfo()
                else:
                    print(obj)
            else:
                log.warning('Header {} Not found in object'.format(header))

        self.__printInfo = False
