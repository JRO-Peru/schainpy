'''

$Author: murco $
$Id: JRODataIO.py 169 2012-11-19 21:57:03Z murco $
'''

import os, sys
import glob
import time
import numpy
import fnmatch
import time, datetime

from jrodata import *
from jroheaderIO import *
from jroprocessing import *

def isNumber(str):
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
        float( str )
        return True
    except:
        return False

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
    basicHeaderObj = BasicHeader()
    
    try:
        fp = open(filename,'rb')
    except:
        raise IOError, "The file %s can't be opened" %(filename)
    
    sts = basicHeaderObj.read(fp)
    fp.close()
    
    if not(sts):
        print "Skipping the file %s because it has not a valid header" %(filename)
        return 0
    
    if not ((startUTSeconds <= basicHeaderObj.utc) and (endUTSeconds > basicHeaderObj.utc)):
        return 0
    
    return 1

def isFileinThisTime(filename, startTime, endTime):
    """
    Retorna 1 si el archivo de datos se encuentra dentro del rango de horas especificado.
    
    Inputs:
        filename            :    nombre completo del archivo de datos en formato Jicamarca (.r)
        
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
        fp = open(filename,'rb')
    except:
        raise IOError, "The file %s can't be opened" %(filename)
    
    basicHeaderObj = BasicHeader()
    sts = basicHeaderObj.read(fp)
    fp.close()
    
    thisTime = basicHeaderObj.datatime.time()
    
    if not(sts):
        print "Skipping the file %s because it has not a valid header" %(filename)
        return 0
    
    if not ((startTime <= thisTime) and (endTime > thisTime)):
        return 0
    
    return 1

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
    
    for file in fileList:
        try:
            year = int(file[1:5])
            doy  = int(file[5:8])
        
            
        except:
            continue
        
        if (os.path.splitext(file)[-1].lower() != ext.lower()):
            continue
        
        validFilelist.append(file)

    if validFilelist:
        validFilelist = sorted( validFilelist, key=str.lower )
        return validFilelist[-1]

    return None

def checkForRealPath(path, year, doy, set, ext):
    """
    Por ser Linux Case Sensitive entonces checkForRealPath encuentra el nombre correcto de un path,
    Prueba por varias combinaciones de nombres entre mayusculas y minusculas para determinar
    el path exacto de un determinado file.
    
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
        Si encuentra la cobinacion adecuada devuelve el path completo y el nombre del file 
        caso contrario devuelve None como path y el la ultima combinacion de nombre en mayusculas 
        para el filename  
    """
    fullfilename = None
    find_flag = False
    filename = None
    
    prefixDirList = [None,'d','D']
    if ext.lower() == ".r": #voltage
        prefixFileList = ['d','D']
    elif ext.lower() == ".pdata": #spectra
        prefixFileList = ['p','P']
    else:
        return None, filename
    
    #barrido por las combinaciones posibles        
    for prefixDir in prefixDirList:
        thispath = path
        if prefixDir != None:
            #formo el nombre del directorio xYYYYDDD (x=d o x=D)
            thispath = os.path.join(path, "%s%04d%03d" % ( prefixDir, year, doy )) 
            
        for prefixFile in prefixFileList: #barrido por las dos combinaciones posibles de "D"
            filename = "%s%04d%03d%03d%s" % ( prefixFile, year, doy, set, ext ) #formo el nombre del file xYYYYDDDSSS.ext
            fullfilename = os.path.join( thispath, filename ) #formo el path completo
            
            if os.path.exists( fullfilename ): #verifico que exista
                find_flag = True
                break
        if find_flag:
            break

    if not(find_flag):
        return None, filename

    return fullfilename, filename

class JRODataIO:
    
    c = 3E8
    
    isConfig = False
    
    basicHeaderObj = BasicHeader()
    
    systemHeaderObj = SystemHeader()
    
    radarControllerHeaderObj = RadarControllerHeader()
    
    processingHeaderObj = ProcessingHeader()
    
    online = 0
    
    dtype = None
    
    pathList = []
    
    filenameList = []
    
    filename = None
    
    ext = None
    
    flagIsNewFile = 1
    
    flagTimeBlock = 0
    
    flagIsNewBlock = 0
    
    fp = None
    
    firstHeaderSize = 0
    
    basicHeaderSize = 24
    
    versionFile = 1103
    
    fileSize = None
    
    ippSeconds = None
    
    fileSizeByHeader = None
    
    fileIndex = None
    
    profileIndex = None
    
    blockIndex = None
    
    nTotalBlocks = None
    
    maxTimeStep = 30
    
    lastUTTime = None
    
    datablock = None
    
    dataOut = None
    
    blocksize = None
    
    def __init__(self):
        
        raise ValueError, "Not implemented"
    
    def run(self):
        
        raise ValueError, "Not implemented"
    
    def getOutput(self):
        
        return self.dataOut

class JRODataReader(JRODataIO, ProcessingUnit):
    
    nReadBlocks = 0
    
    delay  = 10   #number of seconds waiting a new file
        
    nTries  = 3  #quantity tries
        
    nFiles = 3   #number of files for searching
    
    flagNoMoreFiles = 0
    
    def __init__(self):
        
        """

        """
        
        raise ValueError, "This method has not been implemented"
    

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
                            expLabel='',
                            ext='.r',
                            walk=True):
        
        pathList = []
        
        if not walk:
            pathList.append(path)
            
        else:
            dirList = []
            for thisPath in os.listdir(path):
                if os.path.isdir(os.path.join(path,thisPath)):
                    dirList.append(thisPath)
    
            if not(dirList):
                return None, None
            
            thisDate = startDate
            
            while(thisDate <= endDate):
                year = thisDate.timetuple().tm_year
                doy = thisDate.timetuple().tm_yday
                
                match = fnmatch.filter(dirList, '?' + '%4.4d%3.3d' % (year,doy))
                if len(match) == 0:
                    thisDate += datetime.timedelta(1)
                    continue
                
                pathList.append(os.path.join(path,match[0],expLabel))
                thisDate += datetime.timedelta(1)
        
        if pathList == []:
            print "Any folder found into date range %s-%s" %(startDate, endDate)
            return None, None
        
        print "%d folder(s) found [%s, ...]" %(len(pathList), pathList[0])
            
        filenameList = []
        for thisPath in pathList:
            
            fileList = glob.glob1(thisPath, "*%s" %ext)
            fileList.sort()
            
            for file in fileList:
                
                filename = os.path.join(thisPath,file)
                
                if isFileinThisTime(filename, startTime, endTime):
                    filenameList.append(filename)
                    
        if not(filenameList):
            print "Any file found into time range %s-%s" %(startTime, endTime)
            return None, None

        self.filenameList = filenameList
        
        return pathList, filenameList
    
    def __searchFilesOnLine(self, path, expLabel = "", ext = None, walk=True):
        
        """
        Busca el ultimo archivo de la ultima carpeta (determinada o no por startDateTime) y
        devuelve el archivo encontrado ademas de otros datos.
        
        Input: 
            path           :    carpeta donde estan contenidos los files que contiene data
            
            expLabel        :     Nombre del subexperimento (subfolder)
            
            ext              :    extension de los files
            
            walk        :    Si es habilitado no realiza busquedas dentro de los ubdirectorios (doypath)

        Return:
            directory   :    eL directorio donde esta el file encontrado
            filename    :    el ultimo file de una determinada carpeta
            year        :    el anho
            doy         :    el numero de dia del anho
            set         :    el set del archivo
            
            
        """
        dirList = []
        
        if walk:
            
            #Filtra solo los directorios
            for thisPath in os.listdir(path):
                if os.path.isdir(os.path.join(path, thisPath)):
                    dirList.append(thisPath)
        
            if not(dirList):
                return None, None, None, None, None
        
            dirList = sorted( dirList, key=str.lower )
                
            doypath = dirList[-1]
            fullpath = os.path.join(path, doypath, expLabel)
        
        else:
            fullpath = path

        filename = getlastFileFromPath(fullpath, ext)

        if not(filename):
            return None, None, None, None, None

        if not(self.__verifyFile(os.path.join(fullpath, filename))):
            return None, None, None, None, None

        year = int( filename[1:5] )
        doy  = int( filename[5:8] )
        set  = int( filename[8:11] )        
        
        return fullpath, filename, year, doy, set
    


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

    def __setNextFileOnline(self):
        """
        Busca el siguiente file que tenga suficiente data para ser leida, dentro de un folder especifico, si
        no encuentra un file valido espera un tiempo determinado y luego busca en los posibles n files
        siguientes.   
            
        Affected: 
            self.flagIsNewFile
            self.filename
            self.fileSize
            self.fp
            self.set
            self.flagNoMoreFiles

        Return: 
            0    : si luego de una busqueda del siguiente file valido este no pudo ser encontrado
            1    : si el file fue abierto con exito y esta listo a ser leido
        
        Excepciones: 
            Si un determinado file no puede ser abierto
        """
        nFiles = 0
        fileOk_flag = False        
        firstTime_flag = True

        self.set += 1
        
        #busca el 1er file disponible
        fullfilename, filename = checkForRealPath( self.path, self.year, self.doy, self.set, self.ext )
        if fullfilename:
            if self.__verifyFile(fullfilename, False):
                fileOk_flag = True

        #si no encuentra un file entonces espera y vuelve a buscar
        if not(fileOk_flag): 
            for nFiles in range(self.nFiles+1): #busco en los siguientes self.nFiles+1 files posibles

                if firstTime_flag: #si es la 1era vez entonces hace el for self.nTries veces  
                    tries = self.nTries
                else:
                    tries = 1 #si no es la 1era vez entonces solo lo hace una vez
                    
                for nTries in range( tries ): 
                    if firstTime_flag:
                        print "\tWaiting %0.2f sec for the file \"%s\" , try %03d ..." % ( self.delay, filename, nTries+1 ) 
                        time.sleep( self.delay )
                    else:
                        print "\tSearching next \"%s%04d%03d%03d%s\" file ..." % (self.optchar, self.year, self.doy, self.set, self.ext)
                    
                    fullfilename, filename = checkForRealPath( self.path, self.year, self.doy, self.set, self.ext )
                    if fullfilename:
                        if self.__verifyFile(fullfilename):
                            fileOk_flag = True
                            break
                    
                if fileOk_flag:
                    break

                firstTime_flag = False

                print "\tSkipping the file \"%s\" due to this file doesn't exist" % filename
                self.set += 1
                    
                if nFiles == (self.nFiles-1): #si no encuentro el file buscado cambio de carpeta y busco en la siguiente carpeta
                    self.set = 0
                    self.doy += 1

        if fileOk_flag:
            self.fileSize = os.path.getsize( fullfilename )
            self.filename = fullfilename
            self.flagIsNewFile = 1
            if self.fp != None: self.fp.close() 
            self.fp = open(fullfilename, 'rb')
            self.flagNoMoreFiles = 0
            print 'Setting the file: %s' % fullfilename
        else:
            self.fileSize = 0
            self.filename = None
            self.flagIsNewFile = 0
            self.fp = None
            self.flagNoMoreFiles = 1
            print 'No more Files'

        return fileOk_flag


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
        
        for nTries in range( self.nTries ):
            
            self.fp.close()
            self.fp = open( self.filename, 'rb' )
            self.fp.seek( currentPointer )

            self.fileSize = os.path.getsize( self.filename )
            currentSize = self.fileSize - currentPointer

            if ( currentSize >= neededSize ):
                self.__rdBasicHeader()
                return 1
            
            print "\tWaiting %0.2f seconds for the next block, try %03d ..." % (self.delay, nTries+1)
            time.sleep( self.delay )
            
        
        return 0

    def __setNewBlock(self):
        
        if self.fp == None:
            return 0

        if self.flagIsNewFile:
            return 1
        
        self.lastUTTime = self.basicHeaderObj.utc
        currentSize = self.fileSize - self.fp.tell()
        neededSize = self.processingHeaderObj.blockSize + self.basicHeaderSize
        
        if (currentSize >= neededSize):
            self.__rdBasicHeader()
            return 1
        
        if self.__waitNewBlock():
            return 1

        if not(self.setNextFile()):
            return 0

        deltaTime = self.basicHeaderObj.utc - self.lastUTTime #

        self.flagTimeBlock = 0

        if deltaTime > self.maxTimeStep:
            self.flagTimeBlock = 1

        return 1


    def readNextBlock(self):
        if not(self.__setNewBlock()):
            return 0

        if not(self.readBlock()):
            return 0

        return 1

    def __rdProcessingHeader(self, fp=None):
        if fp == None:
            fp = self.fp

        self.processingHeaderObj.read(fp)

    def __rdRadarControllerHeader(self, fp=None):
        if fp == None:
            fp = self.fp

        self.radarControllerHeaderObj.read(fp)

    def __rdSystemHeader(self, fp=None):
        if fp == None:
            fp = self.fp

        self.systemHeaderObj.read(fp)

    def __rdBasicHeader(self, fp=None):
        if fp == None:
            fp = self.fp

        self.basicHeaderObj.read(fp)
        

    def __readFirstHeader(self):
        self.__rdBasicHeader()
        self.__rdSystemHeader()
        self.__rdRadarControllerHeader()
        self.__rdProcessingHeader()

        self.firstHeaderSize = self.basicHeaderObj.size

        datatype = int(numpy.log2((self.processingHeaderObj.processFlags & PROCFLAG.DATATYPE_MASK))-numpy.log2(PROCFLAG.DATATYPE_CHAR))
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

        self.dtype = datatype_str
        self.ippSeconds = 2 * 1000 * self.radarControllerHeaderObj.ipp / self.c
        self.fileSizeByHeader = self.processingHeaderObj.dataBlocksPerFile * self.processingHeaderObj.blockSize + self.firstHeaderSize + self.basicHeaderSize*(self.processingHeaderObj.dataBlocksPerFile - 1)
#        self.dataOut.channelList = numpy.arange(self.systemHeaderObj.numChannels)
#        self.dataOut.channelIndexList = numpy.arange(self.systemHeaderObj.numChannels)
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

        neededSize = self.processingHeaderObj.blockSize + self.firstHeaderSize

        if neededSize == 0:
            basicHeaderObj = BasicHeader()
            systemHeaderObj = SystemHeader()
            radarControllerHeaderObj = RadarControllerHeader()
            processingHeaderObj = ProcessingHeader()

            try:
                if not( basicHeaderObj.read(fp) ): raise IOError
                if not( systemHeaderObj.read(fp) ): raise IOError
                if not( radarControllerHeaderObj.read(fp) ): raise IOError
                if not( processingHeaderObj.read(fp) ): raise IOError
                data_type = int(numpy.log2((processingHeaderObj.processFlags & PROCFLAG.DATATYPE_MASK))-numpy.log2(PROCFLAG.DATATYPE_CHAR))

                neededSize = processingHeaderObj.blockSize + basicHeaderObj.size

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

    def setup(self,
                path=None,
                startDate=None, 
                endDate=None, 
                startTime=datetime.time(0,0,0), 
                endTime=datetime.time(23,59,59), 
                set=0, 
                expLabel = "", 
                ext = None, 
                online = False,
                delay = 60,
                walk = True):

        if path == None:
            raise ValueError, "The path is not valid"

        if ext == None:
            ext = self.ext

        if online:
            print "Searching files in online mode..."  
                   
            for nTries in range( self.nTries ):
                fullpath, file, year, doy, set = self.__searchFilesOnLine(path=path, expLabel=expLabel, ext=ext, walk=walk)
                
                if fullpath:
                    break
                
                print '\tWaiting %0.2f sec for an valid file in %s: try %02d ...' % (self.delay, path, nTries+1)
                time.sleep( self.delay )
            
            if not(fullpath):
                print "There 'isn't valied files in %s" % path
                return None
        
            self.year = year
            self.doy  = doy
            self.set  = set - 1
            self.path = path

        else:
            print "Searching files in offline mode ..."
            pathList, filenameList = self.__searchFilesOffLine(path, startDate=startDate, endDate=endDate,
                                                               startTime=startTime, endTime=endTime,
                                                               set=set, expLabel=expLabel, ext=ext,
                                                               walk=walk)
            
            if not(pathList):
                print "No *%s files into the folder %s \nfor the range: %s - %s"%(ext, path,
                                                        datetime.datetime.combine(startDate,startTime).ctime(),
                                                        datetime.datetime.combine(endDate,endTime).ctime())
                
                sys.exit(-1)
                
            
            self.fileIndex = -1
            self.pathList = pathList
            self.filenameList = filenameList

        self.online = online
        self.delay = delay
        ext = ext.lower()
        self.ext = ext

        if not(self.setNextFile()):
            if (startDate!=None) and (endDate!=None):
                print "No files in range: %s - %s" %(datetime.datetime.combine(startDate,startTime).ctime(), datetime.datetime.combine(endDate,endTime).ctime())
            elif startDate != None:
                print "No files in range: %s" %(datetime.datetime.combine(startDate,startTime).ctime())
            else:
                print "No files"

            sys.exit(-1)

#        self.updateDataHeader()

        return self.dataOut
    
    def getData():
        
        raise ValueError, "This method has not been implemented"

    def hasNotDataInBuffer():
        
        raise ValueError, "This method has not been implemented"

    def readBlock():
        
        raise ValueError, "This method has not been implemented"
    
    def isEndProcess(self):
        
        return self.flagNoMoreFiles
    
    def printReadBlocks(self):
        
        print "Number of read blocks per file %04d" %self.nReadBlocks
    
    def printTotalBlocks(self):
        
        print "Number of read blocks %04d" %self.nTotalBlocks
    
    def printInfo(self):
        
        print self.basicHeaderObj.printInfo()
        print self.systemHeaderObj.printInfo()
        print self.radarControllerHeaderObj.printInfo()
        print self.processingHeaderObj.printInfo()
        
    
    def run(self, **kwargs):
        
        if not(self.isConfig):
            
#            self.dataOut = dataOut
            self.setup(**kwargs)
            self.isConfig = True
            
        self.getData()

class JRODataWriter(JRODataIO, Operation):

    """ 
    Esta clase permite escribir datos a archivos procesados (.r o ,pdata). La escritura
    de los datos siempre se realiza por bloques. 
    """
    
    blockIndex = 0
    
    path = None
        
    setFile = None
    
    profilesPerBlock = None
    
    blocksPerFile = None
    
    nWriteBlocks = 0
    
    def __init__(self, dataOut=None):
        raise ValueError, "Not implemented"


    def hasAllDataInBuffer(self):
        raise ValueError, "Not implemented"


    def setBlockDimension(self):
        raise ValueError, "Not implemented"

    
    def writeBlock(self):
        raise ValueError, "No implemented"


    def putData(self):
        raise ValueError, "No implemented"

    def getDataHeader(self):
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
        
        raise ValueError, "No implemented"
    
    def getBasicHeader(self):
        
        self.basicHeaderObj.size = self.basicHeaderSize #bytes
        self.basicHeaderObj.version = self.versionFile
        self.basicHeaderObj.dataBlock = self.nTotalBlocks
        
        utc = numpy.floor(self.dataOut.utctime)
        milisecond  = (self.dataOut.utctime - utc)* 1000.0
        
        self.basicHeaderObj.utc = utc
        self.basicHeaderObj.miliSecond = milisecond
        self.basicHeaderObj.timeZone = 0
        self.basicHeaderObj.dstFlag = 0
        self.basicHeaderObj.errorCount = 0
        
    def __writeFirstHeader(self):
        """
        Escribe el primer header del file es decir el Basic header y el Long header (SystemHeader, RadarControllerHeader, ProcessingHeader)
        
        Affected:
            __dataType
            
        Return:
            None
        """
        
#        CALCULAR PARAMETROS
        
        sizeLongHeader = self.systemHeaderObj.size + self.radarControllerHeaderObj.size + self.processingHeaderObj.size
        self.basicHeaderObj.size = self.basicHeaderSize + sizeLongHeader
        
        self.basicHeaderObj.write(self.fp)
        self.systemHeaderObj.write(self.fp)
        self.radarControllerHeaderObj.write(self.fp)
        self.processingHeaderObj.write(self.fp)
        
        self.dtype = self.dataOut.dtype

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
        
        if not( self.setNextFile() ):
            return 0
        
        return 1


    def writeNextBlock(self):
        """
        Selecciona el bloque siguiente de datos y los escribe en un file
            
        Return: 
            0    :    Si no hizo pudo escribir el bloque de datos 
            1    :    Si no pudo escribir el bloque de datos
        """
        if not( self.__setNewBlock() ):
            return 0
        
        self.writeBlock()

        return 1        

    def setNextFile(self):
        """ 
        Determina el siguiente file que sera escrito

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
        
        timeTuple = time.localtime( self.dataOut.dataUtcTime)
        subfolder = 'D%4.4d%3.3d' % (timeTuple.tm_year,timeTuple.tm_yday)

        fullpath = os.path.join( path, subfolder )
        if not( os.path.exists(fullpath) ):
            os.mkdir(fullpath)
            self.setFile = -1 #inicializo mi contador de seteo
        else:
            filesList = os.listdir( fullpath )
            if len( filesList ) > 0:
                filesList = sorted( filesList, key=str.lower )
                filen = filesList[-1]
                # el filename debera tener el siguiente formato
                # 0 1234 567 89A BCDE (hex)
                # x YYYY DDD SSS .ext
                if isNumber( filen[8:11] ):
                    self.setFile = int( filen[8:11] ) #inicializo mi contador de seteo al seteo del ultimo file
                else:    
                    self.setFile = -1
            else:
                self.setFile = -1 #inicializo mi contador de seteo
                
        setFile = self.setFile
        setFile += 1
                
        file = '%s%4.4d%3.3d%3.3d%s' % (self.optchar,
                                        timeTuple.tm_year,
                                        timeTuple.tm_yday,
                                        setFile,
                                        ext )

        filename = os.path.join( path, subfolder, file )

        fp = open( filename,'wb' )
        
        self.blockIndex = 0
        
        #guardando atributos 
        self.filename = filename
        self.subfolder = subfolder
        self.fp = fp
        self.setFile = setFile
        self.flagIsNewFile = 1
        
        self.getDataHeader()
        
        print 'Writing the file: %s'%self.filename
        
        self.__writeFirstHeader()
        
        return 1
    
    def setup(self, dataOut, path, blocksPerFile, profilesPerBlock=None, set=0, ext=None):
        """
        Setea el tipo de formato en la cual sera guardada la data y escribe el First Header 
            
        Inputs:
            path      :    el path destino en el cual se escribiran los files a crear
            format    :    formato en el cual sera salvado un file
            set       :    el setebo del file
            
        Return:
            0    :    Si no realizo un buen seteo
            1    :    Si realizo un buen seteo 
        """
        
        if ext == None:
            ext = self.ext
        
        ext = ext.lower()
        
        self.ext = ext
        
        self.path = path
        
        self.setFile = set - 1
        
        self.blocksPerFile = blocksPerFile
        
        self.profilesPerBlock = profilesPerBlock
        
        self.dataOut = dataOut
        
        if not(self.setNextFile()):
            print "There isn't a next file"
            return 0
        
        self.setBlockDimension()
        
        return 1
    
    def run(self, dataOut, **kwargs):
        
        if not(self.isConfig):
            
            self.setup(dataOut, **kwargs)
            self.isConfig = True
            
        self.putData()

class VoltageReader(JRODataReader):
    """
    Esta clase permite leer datos de voltage desde archivos en formato rawdata (.r). La lectura
    de los datos siempre se realiza por bloques. Los datos leidos (array de 3 dimensiones: 
    perfiles*alturas*canales) son almacenados en la variable "buffer".
     
                             perfiles * alturas * canales  

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
            
            if readerObj.flagNoMoreFiles:
                break
            
    """

    ext = ".r"
    
    optchar = "D"
    dataOut = None
    
    
    def __init__(self):
        """
        Inicializador de la clase VoltageReader para la lectura de datos de voltage.
        
        Input:
            dataOut    :    Objeto de la clase Voltage. Este objeto sera utilizado para
                              almacenar un perfil de datos cada vez que se haga un requerimiento
                              (getData). El perfil sera obtenido a partir del buffer de datos,
                              si el buffer esta vacio se hara un nuevo proceso de lectura de un
                              bloque de datos.
                              Si este parametro no es pasado se creara uno internamente.
        
        Variables afectadas:
            self.dataOut
        
        Return:
            None
        """
        
        self.isConfig = False
        
        self.datablock = None
        
        self.utc = 0
    
        self.ext = ".r"
        
        self.optchar = "D"

        self.basicHeaderObj = BasicHeader()
        
        self.systemHeaderObj = SystemHeader()
        
        self.radarControllerHeaderObj = RadarControllerHeader()
        
        self.processingHeaderObj = ProcessingHeader()
        
        self.online = 0
        
        self.fp = None
        
        self.idFile = None
        
        self.dtype = None
        
        self.fileSizeByHeader = None
        
        self.filenameList = []
        
        self.filename = None
        
        self.fileSize = None
        
        self.firstHeaderSize = 0
        
        self.basicHeaderSize = 24
        
        self.pathList = []
        
        self.filenameList = []
        
        self.lastUTTime = 0
        
        self.maxTimeStep = 30
            
        self.flagNoMoreFiles = 0
        
        self.set = 0
        
        self.path = None
        
        self.profileIndex = 9999

        self.delay  = 3   #seconds
        
        self.nTries  = 3  #quantity tries
        
        self.nFiles = 3   #number of files for searching
        
        self.nReadBlocks = 0
        
        self.flagIsNewFile = 1
    
        self.ippSeconds = 0
    
        self.flagTimeBlock = 0    
    
        self.flagIsNewBlock = 0
        
        self.nTotalBlocks = 0
    
        self.blocksize = 0
        
        self.dataOut = self.createObjByDefault()
    
    def createObjByDefault(self):
        
        dataObj = Voltage()
        
        return dataObj
    
    def __hasNotDataInBuffer(self):
        if self.profileIndex >= self.processingHeaderObj.profilesPerBlock:
            return 1
        return 0


    def getBlockDimension(self):
        """
        Obtiene la cantidad de puntos a leer por cada bloque de datos
        
        Affected:
            self.blocksize

        Return:
            None
        """
        pts2read = self.processingHeaderObj.profilesPerBlock * self.processingHeaderObj.nHeights * self.systemHeaderObj.nChannels
        self.blocksize = pts2read

            
    def readBlock(self):
        """
        readBlock lee el bloque de datos desde la posicion actual del puntero del archivo
        (self.fp) y actualiza todos los parametros relacionados al bloque de datos
        (metadata + data). La data leida es almacenada en el buffer y el contador del buffer
        es seteado a 0
        
        Inputs:
            None
            
        Return:
            None
        
        Affected:
            self.profileIndex
            self.datablock
            self.flagIsNewFile
            self.flagIsNewBlock
            self.nTotalBlocks
            
        Exceptions: 
            Si un bloque leido no es un bloque valido
        """
        
        junk = numpy.fromfile( self.fp, self.dtype, self.blocksize )
        
        try:
            junk = junk.reshape( (self.processingHeaderObj.profilesPerBlock, self.processingHeaderObj.nHeights, self.systemHeaderObj.nChannels) )
        except:
            print "The read block (%3d) has not enough data" %self.nReadBlocks
            return 0
        
        junk = numpy.transpose(junk, (2,0,1))
        self.datablock = junk['real'] + junk['imag']*1j
        
        self.profileIndex = 0
        
        self.flagIsNewFile = 0
        self.flagIsNewBlock = 1

        self.nTotalBlocks += 1
        self.nReadBlocks += 1
          
        return 1

    
    def getData(self):
        """
        getData obtiene una unidad de datos del buffer de lectura y la copia a la clase "Voltage"
        con todos los parametros asociados a este (metadata). cuando no hay datos en el buffer de
        lectura es necesario hacer una nueva lectura de los bloques de datos usando "readNextBlock"
        
        Ademas incrementa el contador del buffer en 1.
        
        Return:
            data    :    retorna un perfil de voltages (alturas * canales) copiados desde el
                         buffer. Si no hay mas archivos a leer retorna None.
            
        Variables afectadas:
            self.dataOut
            self.profileIndex
            
        Affected:
            self.dataOut
            self.profileIndex
            self.flagTimeBlock
            self.flagIsNewBlock
        """
        
        if self.flagNoMoreFiles:
            self.dataOut.flagNoData = True
            print 'Process finished'
            return 0
        
        self.flagTimeBlock = 0
        self.flagIsNewBlock = 0
        
        if self.__hasNotDataInBuffer():

            if not( self.readNextBlock() ):
                return 0
        
            self.dataOut.dtype = self.dtype
            
            self.dataOut.nProfiles = self.processingHeaderObj.profilesPerBlock
            
            xf = self.processingHeaderObj.firstHeight + self.processingHeaderObj.nHeights*self.processingHeaderObj.deltaHeight
    
            self.dataOut.heightList = numpy.arange(self.processingHeaderObj.firstHeight, xf, self.processingHeaderObj.deltaHeight) 
            
            self.dataOut.channelList = range(self.systemHeaderObj.nChannels)
            
            self.dataOut.flagTimeBlock = self.flagTimeBlock
            
            self.dataOut.ippSeconds = self.ippSeconds
            
            self.dataOut.timeInterval = self.ippSeconds * self.processingHeaderObj.nCohInt
            
            self.dataOut.nCohInt = self.processingHeaderObj.nCohInt
            
            self.dataOut.flagShiftFFT = False
            
            if self.processingHeaderObj.code != None:
                
                self.dataOut.nCode = self.processingHeaderObj.nCode
                
                self.dataOut.nBaud = self.processingHeaderObj.nBaud
                
                self.dataOut.code = self.processingHeaderObj.code
            
            self.dataOut.systemHeaderObj = self.systemHeaderObj.copy()
            
            self.dataOut.radarControllerHeaderObj = self.radarControllerHeaderObj.copy()
            
            self.dataOut.flagDecodeData = False #asumo q la data no esta decodificada
    
            self.dataOut.flagDeflipData = False #asumo q la data no esta sin flip
            
            self.dataOut.flagShiftFFT = False
        
        
#            self.updateDataHeader()
        
        #data es un numpy array de 3 dmensiones (perfiles, alturas y canales)
        
        if self.datablock == None:
            self.dataOut.flagNoData = True
            return 0
        
        self.dataOut.data = self.datablock[:,self.profileIndex,:]
        
        self.dataOut.utctime = self.basicHeaderObj.utc + self.basicHeaderObj.miliSecond/1000. + self.profileIndex * self.ippSeconds
        
        self.profileIndex += 1
        
        self.dataOut.flagNoData = False
        
#        print self.profileIndex, self.dataOut.utctime 
#        if self.profileIndex == 800:
#            a=1
        
        
        return self.dataOut.data


class VoltageWriter(JRODataWriter):
    """ 
    Esta clase permite escribir datos de voltajes a archivos procesados (.r). La escritura
    de los datos siempre se realiza por bloques. 
    """
    
    ext = ".r"
    
    optchar = "D"
    
    shapeBuffer = None
    

    def __init__(self):
        """ 
        Inicializador de la clase VoltageWriter para la escritura de datos de espectros.
         
        Affected: 
            self.dataOut

        Return: None
        """
        
        self.nTotalBlocks = 0

        self.profileIndex = 0
        
        self.isConfig = False
        
        self.fp = None

        self.flagIsNewFile = 1
        
        self.nTotalBlocks = 0 
        
        self.flagIsNewBlock = 0

        self.setFile = None
        
        self.dtype = None
        
        self.path = None
        
        self.filename = None
        
        self.basicHeaderObj = BasicHeader()
    
        self.systemHeaderObj = SystemHeader()
    
        self.radarControllerHeaderObj = RadarControllerHeader()
    
        self.processingHeaderObj = ProcessingHeader()

    def hasAllDataInBuffer(self):
        if self.profileIndex >= self.processingHeaderObj.profilesPerBlock:
            return 1
        return 0


    def setBlockDimension(self):
        """
        Obtiene las formas dimensionales del los subbloques de datos que componen un bloque

        Affected:
            self.shape_spc_Buffer
            self.shape_cspc_Buffer
            self.shape_dc_Buffer

        Return: None
        """
        self.shapeBuffer = (self.processingHeaderObj.profilesPerBlock,
                            self.processingHeaderObj.nHeights,
                            self.systemHeaderObj.nChannels)
            
        self.datablock = numpy.zeros((self.systemHeaderObj.nChannels,
                                     self.processingHeaderObj.profilesPerBlock,
                                     self.processingHeaderObj.nHeights),
                                     dtype=numpy.dtype('complex'))

        
    def writeBlock(self):
        """
        Escribe el buffer en el file designado
            
        Affected:
            self.profileIndex 
            self.flagIsNewFile
            self.flagIsNewBlock
            self.nTotalBlocks
            self.blockIndex    
            
        Return: None
        """
        data = numpy.zeros( self.shapeBuffer, self.dtype )
        
        junk = numpy.transpose(self.datablock, (1,2,0))
        
        data['real'] = junk.real
        data['imag'] = junk.imag
        
        data = data.reshape( (-1) )
            
        data.tofile( self.fp )
        
        self.datablock.fill(0)
        
        self.profileIndex = 0 
        self.flagIsNewFile = 0
        self.flagIsNewBlock = 1
        
        self.blockIndex += 1
        self.nTotalBlocks += 1
        
    def putData(self):
        """
        Setea un bloque de datos y luego los escribe en un file 
            
        Affected:
            self.flagIsNewBlock
            self.profileIndex

        Return: 
            0    :    Si no hay data o no hay mas files que puedan escribirse 
            1    :    Si se escribio la data de un bloque en un file
        """
        if self.dataOut.flagNoData:
            return 0
        
        self.flagIsNewBlock = 0
        
        if self.dataOut.flagTimeBlock:
            
            self.datablock.fill(0)
            self.profileIndex = 0
            self.setNextFile()
        
        if self.profileIndex == 0:
            self.getBasicHeader()
        
        self.datablock[:,self.profileIndex,:] = self.dataOut.data
        
        self.profileIndex += 1
        
        if self.hasAllDataInBuffer():
            #if self.flagIsNewFile: 
            self.writeNextBlock()
#            self.getDataHeader()
        
        return 1
    
    def __getProcessFlags(self):
        
        processFlags = 0
        
        dtype0 = numpy.dtype([('real','<i1'),('imag','<i1')])
        dtype1 = numpy.dtype([('real','<i2'),('imag','<i2')])
        dtype2 = numpy.dtype([('real','<i4'),('imag','<i4')])
        dtype3 = numpy.dtype([('real','<i8'),('imag','<i8')])
        dtype4 = numpy.dtype([('real','<f4'),('imag','<f4')])
        dtype5 = numpy.dtype([('real','<f8'),('imag','<f8')])
        
        dtypeList = [dtype0, dtype1, dtype2, dtype3, dtype4, dtype5]
        
        
        
        datatypeValueList =  [PROCFLAG.DATATYPE_CHAR, 
                           PROCFLAG.DATATYPE_SHORT, 
                           PROCFLAG.DATATYPE_LONG, 
                           PROCFLAG.DATATYPE_INT64, 
                           PROCFLAG.DATATYPE_FLOAT, 
                           PROCFLAG.DATATYPE_DOUBLE]
        
        
        for index in range(len(dtypeList)):
            if self.dataOut.dtype == dtypeList[index]:
                dtypeValue = datatypeValueList[index]
                break
        
        processFlags += dtypeValue
        
        if self.dataOut.flagDecodeData:
            processFlags += PROCFLAG.DECODE_DATA
        
        if self.dataOut.flagDeflipData:
            processFlags += PROCFLAG.DEFLIP_DATA
        
        if self.dataOut.code != None:
            processFlags += PROCFLAG.DEFINE_PROCESS_CODE
        
        if self.dataOut.nCohInt > 1:
            processFlags += PROCFLAG.COHERENT_INTEGRATION
        
        return processFlags
    
    
    def __getBlockSize(self):
        '''
        Este metodos determina el cantidad de bytes para un bloque de datos de tipo Voltage
        '''
        
        dtype0 = numpy.dtype([('real','<i1'),('imag','<i1')])
        dtype1 = numpy.dtype([('real','<i2'),('imag','<i2')])
        dtype2 = numpy.dtype([('real','<i4'),('imag','<i4')])
        dtype3 = numpy.dtype([('real','<i8'),('imag','<i8')])
        dtype4 = numpy.dtype([('real','<f4'),('imag','<f4')])
        dtype5 = numpy.dtype([('real','<f8'),('imag','<f8')])
        
        dtypeList = [dtype0, dtype1, dtype2, dtype3, dtype4, dtype5]
        datatypeValueList = [1,2,4,8,4,8]
        for index in range(len(dtypeList)):
            if self.dataOut.dtype == dtypeList[index]:
                datatypeValue = datatypeValueList[index]
                break
        
        blocksize = int(self.dataOut.nHeights * self.dataOut.nChannels * self.dataOut.nProfiles * datatypeValue * 2)
        
        return blocksize
    
    def getDataHeader(self):
        
        """
        Obtiene una copia del First Header
         
        Affected:
            self.systemHeaderObj
            self.radarControllerHeaderObj
            self.dtype

        Return: 
            None
        """
        
        self.systemHeaderObj = self.dataOut.systemHeaderObj.copy()
        self.systemHeaderObj.nChannels = self.dataOut.nChannels
        self.radarControllerHeaderObj = self.dataOut.radarControllerHeaderObj.copy()
        
        self.getBasicHeader()
        
        processingHeaderSize = 40 # bytes    
        self.processingHeaderObj.dtype = 0 # Voltage
        self.processingHeaderObj.blockSize = self.__getBlockSize()
        self.processingHeaderObj.profilesPerBlock = self.profilesPerBlock
        self.processingHeaderObj.dataBlocksPerFile = self.blocksPerFile
        self.processingHeaderObj.nWindows = 1 #podria ser 1 o self.dataOut.processingHeaderObj.nWindows
        self.processingHeaderObj.processFlags = self.__getProcessFlags()
        self.processingHeaderObj.nCohInt = self.dataOut.nCohInt
        self.processingHeaderObj.nIncohInt = 1 # Cuando la data de origen es de tipo Voltage
        self.processingHeaderObj.totalSpectra = 0 # Cuando la data de origen es de tipo Voltage
        
        if self.dataOut.code != None:
            self.processingHeaderObj.code = self.dataOut.code
            self.processingHeaderObj.nCode = self.dataOut.nCode
            self.processingHeaderObj.nBaud = self.dataOut.nBaud
            codesize = int(8 + 4 * self.dataOut.nCode * self.dataOut.nBaud)
            processingHeaderSize += codesize
        
        if self.processingHeaderObj.nWindows != 0:
            self.processingHeaderObj.firstHeight = self.dataOut.heightList[0]
            self.processingHeaderObj.deltaHeight = self.dataOut.heightList[1] - self.dataOut.heightList[0]
            self.processingHeaderObj.nHeights = self.dataOut.nHeights
            self.processingHeaderObj.samplesWin = self.dataOut.nHeights
            processingHeaderSize += 12
            
        self.processingHeaderObj.size = processingHeaderSize
    
class SpectraReader(JRODataReader):
    """ 
    Esta clase permite leer datos de espectros desde archivos procesados (.pdata). La lectura
    de los datos siempre se realiza por bloques. Los datos leidos (array de 3 dimensiones) 
    son almacenados en tres buffer's para el Self Spectra, el Cross Spectra y el DC Channel.

                        paresCanalesIguales    * alturas * perfiles  (Self Spectra)
                        paresCanalesDiferentes * alturas * perfiles  (Cross Spectra)
                        canales * alturas                            (DC Channels)

    Esta clase contiene instancias (objetos) de las clases BasicHeader, SystemHeader, 
    RadarControllerHeader y Spectra. Los tres primeros se usan para almacenar informacion de la
    cabecera de datos (metadata), y el cuarto (Spectra) para obtener y almacenar un bloque de
    datos desde el "buffer" cada vez que se ejecute el metodo "getData".
    
    Example:     
        dpath = "/home/myuser/data"
        
        startTime = datetime.datetime(2010,1,20,0,0,0,0,0,0)
        
        endTime = datetime.datetime(2010,1,21,23,59,59,0,0,0)
        
        readerObj = SpectraReader()
        
        readerObj.setup(dpath, startTime, endTime)
        
        while(True):
            
            readerObj.getData()
            
            print readerObj.data_spc
            
            print readerObj.data_cspc
            
            print readerObj.data_dc
            
            if readerObj.flagNoMoreFiles:
                break
            
    """

    pts2read_SelfSpectra = 0
    
    pts2read_CrossSpectra = 0
    
    pts2read_DCchannels = 0
    
    ext = ".pdata"
        
    optchar = "P"
    
    dataOut = None
    
    nRdChannels = None
    
    nRdPairs = None
    
    rdPairList = []

    
    def __init__(self):
        """ 
        Inicializador de la clase SpectraReader para la lectura de datos de espectros.

        Inputs: 
            dataOut    :    Objeto de la clase Spectra. Este objeto sera utilizado para
                              almacenar un perfil de datos cada vez que se haga un requerimiento
                              (getData). El perfil sera obtenido a partir del buffer de datos,
                              si el buffer esta vacio se hara un nuevo proceso de lectura de un
                              bloque de datos.
                              Si este parametro no es pasado se creara uno internamente.
         
        Affected: 
            self.dataOut

        Return      : None
        """
        
        self.isConfig = False
        
        self.pts2read_SelfSpectra = 0
        
        self.pts2read_CrossSpectra = 0
        
        self.pts2read_DCchannels = 0
        
        self.datablock = None
        
        self.utc = None
        
        self.ext = ".pdata"
        
        self.optchar = "P"
        
        self.basicHeaderObj = BasicHeader()
        
        self.systemHeaderObj = SystemHeader()
        
        self.radarControllerHeaderObj = RadarControllerHeader()
        
        self.processingHeaderObj = ProcessingHeader()
        
        self.online = 0
        
        self.fp = None
        
        self.idFile = None
        
        self.dtype = None
        
        self.fileSizeByHeader = None
        
        self.filenameList = []
        
        self.filename = None
        
        self.fileSize = None
        
        self.firstHeaderSize = 0
        
        self.basicHeaderSize = 24
        
        self.pathList = []

        self.lastUTTime = 0
        
        self.maxTimeStep = 30
            
        self.flagNoMoreFiles = 0
        
        self.set = 0
        
        self.path = None

        self.delay  = 3   #seconds
        
        self.nTries = 3  #quantity tries
        
        self.nFiles = 3   #number of files for searching
        
        self.nReadBlocks = 0
        
        self.flagIsNewFile = 1
    
        self.ippSeconds = 0
    
        self.flagTimeBlock = 0    
    
        self.flagIsNewBlock = 0
        
        self.nTotalBlocks = 0
    
        self.blocksize = 0
        
        self.dataOut = self.createObjByDefault()


    def createObjByDefault(self):
        
        dataObj = Spectra()
        
        return dataObj
    
    def __hasNotDataInBuffer(self):
        return 1


    def getBlockDimension(self):
        """
        Obtiene la cantidad de puntos a leer por cada bloque de datos
        
        Affected:
            self.nRdChannels
            self.nRdPairs
            self.pts2read_SelfSpectra
            self.pts2read_CrossSpectra
            self.pts2read_DCchannels
            self.blocksize
            self.dataOut.nChannels
            self.dataOut.nPairs

        Return:
            None
        """
        self.nRdChannels = 0
        self.nRdPairs = 0
        self.rdPairList = []
        
        for i in range(0, self.processingHeaderObj.totalSpectra*2, 2):
            if self.processingHeaderObj.spectraComb[i] == self.processingHeaderObj.spectraComb[i+1]:
                self.nRdChannels = self.nRdChannels + 1 #par de canales iguales 
            else:
                self.nRdPairs = self.nRdPairs + 1 #par de canales diferentes
                self.rdPairList.append((self.processingHeaderObj.spectraComb[i], self.processingHeaderObj.spectraComb[i+1]))

        pts2read = self.processingHeaderObj.nHeights * self.processingHeaderObj.profilesPerBlock

        self.pts2read_SelfSpectra = int(self.nRdChannels * pts2read)
        self.blocksize = self.pts2read_SelfSpectra
        
        if self.processingHeaderObj.flag_cspc:
            self.pts2read_CrossSpectra = int(self.nRdPairs * pts2read)
            self.blocksize += self.pts2read_CrossSpectra
            
        if self.processingHeaderObj.flag_dc:
            self.pts2read_DCchannels = int(self.systemHeaderObj.nChannels * self.processingHeaderObj.nHeights)
            self.blocksize += self.pts2read_DCchannels
            
#        self.blocksize = self.pts2read_SelfSpectra + self.pts2read_CrossSpectra + self.pts2read_DCchannels

            
    def readBlock(self):
        """
        Lee el bloque de datos desde la posicion actual del puntero del archivo
        (self.fp) y actualiza todos los parametros relacionados al bloque de datos
        (metadata + data). La data leida es almacenada en el buffer y el contador del buffer
        es seteado a 0
        
        Return: None
        
        Variables afectadas:
            
            self.flagIsNewFile
            self.flagIsNewBlock
            self.nTotalBlocks
            self.data_spc
            self.data_cspc
            self.data_dc

        Exceptions: 
            Si un bloque leido no es un bloque valido
        """
        blockOk_flag = False
        fpointer = self.fp.tell()

        spc = numpy.fromfile( self.fp, self.dtype[0], self.pts2read_SelfSpectra )
        spc = spc.reshape( (self.nRdChannels, self.processingHeaderObj.nHeights, self.processingHeaderObj.profilesPerBlock) ) #transforma a un arreglo 3D
        
        if self.processingHeaderObj.flag_cspc:
            cspc = numpy.fromfile( self.fp, self.dtype, self.pts2read_CrossSpectra )
            cspc = cspc.reshape( (self.nRdPairs, self.processingHeaderObj.nHeights, self.processingHeaderObj.profilesPerBlock) ) #transforma a un arreglo 3D
        
        if self.processingHeaderObj.flag_dc:
            dc = numpy.fromfile( self.fp, self.dtype, self.pts2read_DCchannels ) #int(self.processingHeaderObj.nHeights*self.systemHeaderObj.nChannels) )
            dc = dc.reshape( (self.systemHeaderObj.nChannels, self.processingHeaderObj.nHeights) ) #transforma a un arreglo 2D
            
        
        if not(self.processingHeaderObj.shif_fft):
            #desplaza a la derecha en el eje 2 determinadas posiciones
            shift = int(self.processingHeaderObj.profilesPerBlock/2)
            spc = numpy.roll( spc, shift , axis=2 )
            
            if self.processingHeaderObj.flag_cspc:
                #desplaza a la derecha en el eje 2 determinadas posiciones
                cspc = numpy.roll( cspc, shift, axis=2 )
        

        spc = numpy.transpose( spc, (0,2,1) )
        self.data_spc = spc
        
        if self.processingHeaderObj.flag_cspc: 
            cspc = numpy.transpose( cspc, (0,2,1) )
            self.data_cspc = cspc['real'] + cspc['imag']*1j
        else:
            self.data_cspc = None
        
        if self.processingHeaderObj.flag_dc:
            self.data_dc = dc['real'] + dc['imag']*1j
        else:
            self.data_dc = None

        self.flagIsNewFile = 0
        self.flagIsNewBlock = 1

        self.nTotalBlocks += 1
        self.nReadBlocks += 1

        return 1
    

    def getData(self):
        """
        Copia el buffer de lectura a la clase "Spectra",
        con todos los parametros asociados a este (metadata). cuando no hay datos en el buffer de
        lectura es necesario hacer una nueva lectura de los bloques de datos usando "readNextBlock"
        
        Return:
            0    :    Si no hay mas archivos disponibles
            1    :    Si hizo una buena copia del buffer
            
        Affected:
            self.dataOut
            
            self.flagTimeBlock
            self.flagIsNewBlock
        """

        if self.flagNoMoreFiles:
            self.dataOut.flagNoData = True
            print 'Process finished'
            return 0
         
        self.flagTimeBlock = 0
        self.flagIsNewBlock = 0
        
        if self.__hasNotDataInBuffer():            

            if not( self.readNextBlock() ):
                self.dataOut.flagNoData = True
                return 0 
            
#            self.updateDataHeader()
        
        #data es un numpy array de 3 dmensiones (perfiles, alturas y canales)

        if self.data_dc == None:
            self.dataOut.flagNoData = True
            return 0

        self.dataOut.data_spc = self.data_spc
        
        self.dataOut.data_cspc = self.data_cspc
        
        self.dataOut.data_dc = self.data_dc
                
        self.dataOut.flagTimeBlock = self.flagTimeBlock
    
        self.dataOut.flagNoData = False

        self.dataOut.dtype = self.dtype

#        self.dataOut.nChannels = self.nRdChannels
        
        self.dataOut.nPairs = self.nRdPairs
        
        self.dataOut.pairsList = self.rdPairList
        
#        self.dataOut.nHeights = self.processingHeaderObj.nHeights
        
        self.dataOut.nProfiles = self.processingHeaderObj.profilesPerBlock
        
        self.dataOut.nFFTPoints = self.processingHeaderObj.profilesPerBlock
        
        self.dataOut.nCohInt = self.processingHeaderObj.nCohInt
        
        self.dataOut.nIncohInt = self.processingHeaderObj.nIncohInt
        
        xf = self.processingHeaderObj.firstHeight + self.processingHeaderObj.nHeights*self.processingHeaderObj.deltaHeight

        self.dataOut.heightList = numpy.arange(self.processingHeaderObj.firstHeight, xf, self.processingHeaderObj.deltaHeight) 
        
        self.dataOut.channelList = range(self.systemHeaderObj.nChannels)
        
#        self.dataOut.channelIndexList = range(self.systemHeaderObj.nChannels)
        
        self.dataOut.utctime = self.basicHeaderObj.utc + self.basicHeaderObj.miliSecond/1000.#+ self.profileIndex * self.ippSeconds
        
        self.dataOut.ippSeconds = self.ippSeconds
        
        self.dataOut.timeInterval = self.ippSeconds * self.processingHeaderObj.nCohInt * self.processingHeaderObj.nIncohInt * self.dataOut.nFFTPoints
        
#        self.profileIndex += 1
        
        self.dataOut.systemHeaderObj = self.systemHeaderObj.copy()
        
        self.dataOut.radarControllerHeaderObj = self.radarControllerHeaderObj.copy()
        
        self.dataOut.flagShiftFFT = self.processingHeaderObj.shif_fft
        
        self.dataOut.flagDecodeData = True #asumo q la data no esta decodificada
    
        self.dataOut.flagDeflipData = True #asumo q la data no esta sin flip
            

        return self.dataOut.data_spc


class SpectraWriter(JRODataWriter):
    
    """ 
    Esta clase permite escribir datos de espectros a archivos procesados (.pdata). La escritura
    de los datos siempre se realiza por bloques. 
    """
    
    ext = ".pdata"
    
    optchar = "P"
    
    shape_spc_Buffer = None
    
    shape_cspc_Buffer = None
    
    shape_dc_Buffer = None
    
    data_spc = None
    
    data_cspc = None
    
    data_dc = None
    
#    dataOut = None
    
    def __init__(self):
        """ 
        Inicializador de la clase SpectraWriter para la escritura de datos de espectros.
         
        Affected: 
            self.dataOut
            self.basicHeaderObj
            self.systemHeaderObj
            self.radarControllerHeaderObj
            self.processingHeaderObj

        Return: None
        """
        
        self.isConfig = False
        
        self.nTotalBlocks = 0
         
        self.data_spc = None
        
        self.data_cspc = None
        
        self.data_dc = None

        self.fp = None

        self.flagIsNewFile = 1
        
        self.nTotalBlocks = 0 
        
        self.flagIsNewBlock = 0

        self.setFile = None
        
        self.dtype = None
        
        self.path = None
        
        self.noMoreFiles = 0
        
        self.filename = None
        
        self.basicHeaderObj = BasicHeader()
    
        self.systemHeaderObj = SystemHeader()
    
        self.radarControllerHeaderObj = RadarControllerHeader()
    
        self.processingHeaderObj = ProcessingHeader()

        
    def hasAllDataInBuffer(self):
        return 1

    
    def setBlockDimension(self):
        """
        Obtiene las formas dimensionales del los subbloques de datos que componen un bloque

        Affected:
            self.shape_spc_Buffer
            self.shape_cspc_Buffer
            self.shape_dc_Buffer

        Return: None
        """
        self.shape_spc_Buffer = (self.dataOut.nChannels,
                                 self.processingHeaderObj.nHeights,
                                 self.processingHeaderObj.profilesPerBlock)

        self.shape_cspc_Buffer = (self.dataOut.nPairs,
                                  self.processingHeaderObj.nHeights,
                                  self.processingHeaderObj.profilesPerBlock)
        
        self.shape_dc_Buffer = (self.dataOut.nChannels,
                                self.processingHeaderObj.nHeights)

    
    def writeBlock(self):
        """
        Escribe el buffer en el file designado
            
        Affected:
            self.data_spc
            self.data_cspc
            self.data_dc
            self.flagIsNewFile
            self.flagIsNewBlock
            self.nTotalBlocks
            self.nWriteBlocks    
            
        Return: None
        """
        
        spc = numpy.transpose( self.data_spc, (0,2,1) )
        if not( self.processingHeaderObj.shif_fft ):
            spc = numpy.roll( spc, self.processingHeaderObj.profilesPerBlock/2, axis=2 ) #desplaza a la derecha en el eje 2 determinadas posiciones
        data = spc.reshape((-1))
        data.tofile(self.fp)

        if self.data_cspc != None:
            data = numpy.zeros( self.shape_cspc_Buffer, self.dtype )
            cspc = numpy.transpose( self.data_cspc, (0,2,1) )
            if not( self.processingHeaderObj.shif_fft ):
                cspc = numpy.roll( cspc, self.processingHeaderObj.profilesPerBlock/2, axis=2 ) #desplaza a la derecha en el eje 2 determinadas posiciones
            data['real'] = cspc.real
            data['imag'] = cspc.imag
            data = data.reshape((-1))
            data.tofile(self.fp)
        
        if self.data_dc != None:
            data = numpy.zeros( self.shape_dc_Buffer, self.dtype )
            dc = self.data_dc
            data['real'] = dc.real
            data['imag'] = dc.imag
            data = data.reshape((-1))
            data.tofile(self.fp)

        self.data_spc.fill(0)
        self.data_dc.fill(0)
        if self.data_cspc != None:
            self.data_cspc.fill(0)
        
        self.flagIsNewFile = 0
        self.flagIsNewBlock = 1
        self.nTotalBlocks += 1
        self.nWriteBlocks += 1
        self.blockIndex += 1
        
        
    def putData(self):
        """
        Setea un bloque de datos y luego los escribe en un file 
            
        Affected:
            self.data_spc
            self.data_cspc
            self.data_dc

        Return: 
            0    :    Si no hay data o no hay mas files que puedan escribirse 
            1    :    Si se escribio la data de un bloque en un file
        """
        
        if self.dataOut.flagNoData:
            return 0
        
        self.flagIsNewBlock = 0
        
        if self.dataOut.flagTimeBlock:
            self.data_spc.fill(0)
            self.data_cspc.fill(0)
            self.data_dc.fill(0)
            self.setNextFile()
        
        if self.flagIsNewFile == 0:
            self.getBasicHeader()
        
        self.data_spc = self.dataOut.data_spc
        self.data_cspc = self.dataOut.data_cspc
        self.data_dc = self.dataOut.data_dc
        
        # #self.processingHeaderObj.dataBlocksPerFile)
        if self.hasAllDataInBuffer():
#            self.getDataHeader()
            self.writeNextBlock()
        
        return 1
    
    
    def __getProcessFlags(self):
        
        processFlags = 0
        
        dtype0 = numpy.dtype([('real','<i1'),('imag','<i1')])
        dtype1 = numpy.dtype([('real','<i2'),('imag','<i2')])
        dtype2 = numpy.dtype([('real','<i4'),('imag','<i4')])
        dtype3 = numpy.dtype([('real','<i8'),('imag','<i8')])
        dtype4 = numpy.dtype([('real','<f4'),('imag','<f4')])
        dtype5 = numpy.dtype([('real','<f8'),('imag','<f8')])
        
        dtypeList = [dtype0, dtype1, dtype2, dtype3, dtype4, dtype5]
        
        
        
        datatypeValueList =  [PROCFLAG.DATATYPE_CHAR, 
                           PROCFLAG.DATATYPE_SHORT, 
                           PROCFLAG.DATATYPE_LONG, 
                           PROCFLAG.DATATYPE_INT64, 
                           PROCFLAG.DATATYPE_FLOAT, 
                           PROCFLAG.DATATYPE_DOUBLE]
        
        
        for index in range(len(dtypeList)):
            if self.dataOut.dtype == dtypeList[index]:
                dtypeValue = datatypeValueList[index]
                break
        
        processFlags += dtypeValue
        
        if self.dataOut.flagDecodeData:
            processFlags += PROCFLAG.DECODE_DATA
        
        if self.dataOut.flagDeflipData:
            processFlags += PROCFLAG.DEFLIP_DATA
        
        if self.dataOut.code != None:
            processFlags += PROCFLAG.DEFINE_PROCESS_CODE
        
        if self.dataOut.nIncohInt > 1:
            processFlags += PROCFLAG.INCOHERENT_INTEGRATION
            
        if self.dataOut.data_dc != None:
            processFlags += PROCFLAG.SAVE_CHANNELS_DC
        
        return processFlags
    
    
    def __getBlockSize(self):
        '''
        Este metodos determina el cantidad de bytes para un bloque de datos de tipo Spectra
        '''
        
        dtype0 = numpy.dtype([('real','<i1'),('imag','<i1')])
        dtype1 = numpy.dtype([('real','<i2'),('imag','<i2')])
        dtype2 = numpy.dtype([('real','<i4'),('imag','<i4')])
        dtype3 = numpy.dtype([('real','<i8'),('imag','<i8')])
        dtype4 = numpy.dtype([('real','<f4'),('imag','<f4')])
        dtype5 = numpy.dtype([('real','<f8'),('imag','<f8')])
        
        dtypeList = [dtype0, dtype1, dtype2, dtype3, dtype4, dtype5]
        datatypeValueList = [1,2,4,8,4,8]
        for index in range(len(dtypeList)):
            if self.dataOut.dtype == dtypeList[index]:
                datatypeValue = datatypeValueList[index]
                break
        
        
        pts2write = self.dataOut.nHeights * self.dataOut.nFFTPoints
        
        pts2write_SelfSpectra = int(self.dataOut.nChannels * pts2write)
        blocksize = (pts2write_SelfSpectra*datatypeValue)
        
        if self.dataOut.data_cspc != None:
            pts2write_CrossSpectra = int(self.dataOut.nPairs * pts2write)
            blocksize += (pts2write_CrossSpectra*datatypeValue*2)
        
        if self.dataOut.data_dc != None:
            pts2write_DCchannels = int(self.dataOut.nChannels * self.dataOut.nHeights)
            blocksize += (pts2write_DCchannels*datatypeValue*2)
        
        blocksize = blocksize #* datatypeValue * 2 #CORREGIR ESTO

        return blocksize
    
    def getDataHeader(self):
        
        """
        Obtiene una copia del First Header
         
        Affected:
            self.systemHeaderObj
            self.radarControllerHeaderObj
            self.dtype

        Return: 
            None
        """
        
        self.systemHeaderObj = self.dataOut.systemHeaderObj.copy()
        self.systemHeaderObj.nChannels = self.dataOut.nChannels
        self.radarControllerHeaderObj = self.dataOut.radarControllerHeaderObj.copy()
        
        self.getBasicHeader()
        
        processingHeaderSize = 40 # bytes    
        self.processingHeaderObj.dtype = 0 # Voltage
        self.processingHeaderObj.blockSize = self.__getBlockSize()
        self.processingHeaderObj.profilesPerBlock = self.dataOut.nFFTPoints
        self.processingHeaderObj.dataBlocksPerFile = self.blocksPerFile
        self.processingHeaderObj.nWindows = 1 #podria ser 1 o self.dataOut.processingHeaderObj.nWindows
        self.processingHeaderObj.processFlags = self.__getProcessFlags()
        self.processingHeaderObj.nCohInt = self.dataOut.nCohInt# Se requiere para determinar el valor de timeInterval
        self.processingHeaderObj.nIncohInt = self.dataOut.nIncohInt 
        self.processingHeaderObj.totalSpectra = self.dataOut.nPairs + self.dataOut.nChannels
        
        if self.processingHeaderObj.totalSpectra > 0:
            channelList = []
            for channel in range(self.dataOut.nChannels):
                channelList.append(channel)
                channelList.append(channel)
                
            pairsList = []
            for pair in self.dataOut.pairsList:
                pairsList.append(pair[0])
                pairsList.append(pair[1])
            spectraComb = channelList + pairsList
            spectraComb = numpy.array(spectraComb,dtype="u1")
            self.processingHeaderObj.spectraComb = spectraComb
            sizeOfSpcComb = len(spectraComb)
            processingHeaderSize += sizeOfSpcComb
        
        if self.dataOut.code != None:
            self.processingHeaderObj.code = self.dataOut.code
            self.processingHeaderObj.nCode = self.dataOut.nCode
            self.processingHeaderObj.nBaud = self.dataOut.nBaud
            nCodeSize = 4 # bytes
            nBaudSize = 4 # bytes
            codeSize = 4 # bytes
            sizeOfCode = int(nCodeSize + nBaudSize + codeSize * self.dataOut.nCode * self.dataOut.nBaud)
            processingHeaderSize += sizeOfCode
        
        if self.processingHeaderObj.nWindows != 0:
            self.processingHeaderObj.firstHeight = self.dataOut.heightList[0]
            self.processingHeaderObj.deltaHeight = self.dataOut.heightList[1] - self.dataOut.heightList[0]
            self.processingHeaderObj.nHeights = self.dataOut.nHeights
            self.processingHeaderObj.samplesWin = self.dataOut.nHeights
            sizeOfFirstHeight = 4
            sizeOfdeltaHeight = 4
            sizeOfnHeights = 4
            sizeOfWindows = (sizeOfFirstHeight + sizeOfdeltaHeight + sizeOfnHeights)*self.processingHeaderObj.nWindows
            processingHeaderSize += sizeOfWindows
            
        self.processingHeaderObj.size = processingHeaderSize
        
class SpectraHeisWriter():
    
    i=0
    
    def __init__(self, dataOut):
        
        self.wrObj = FITS()
        self.dataOut = dataOut 
        
    def isNumber(str):
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
            float( str )
            return True
        except:
            return False     
        
    def setup(self, wrpath,):

        if not(os.path.exists(wrpath)):
            os.mkdir(wrpath)
       
        self.wrpath = wrpath
        self.setFile = 0

    def putData(self):
      # self.wrObj.writeHeader(nChannels=self.dataOut.nChannels, nFFTPoints=self.dataOut.nFFTPoints)
        #name = self.dataOut.utctime
        name= time.localtime( self.dataOut.utctime)
        ext=".fits"
        #folder='D%4.4d%3.3d'%(name.tm_year,name.tm_yday)    
        subfolder = 'D%4.4d%3.3d' % (name.tm_year,name.tm_yday)

        fullpath = os.path.join( self.wrpath, subfolder )
        if not( os.path.exists(fullpath) ):
            os.mkdir(fullpath)
        self.setFile += 1
        file = 'D%4.4d%3.3d%3.3d%s' % (name.tm_year,name.tm_yday,self.setFile,ext) 

        filename = os.path.join(self.wrpath,subfolder, file) 
        
       # print self.dataOut.ippSeconds
        freq=numpy.arange(-1*self.dataOut.nHeights/2.,self.dataOut.nHeights/2.)/(2*self.dataOut.ippSeconds)
        
        col1=self.wrObj.setColF(name="freq", format=str(self.dataOut.nFFTPoints)+'E', array=freq)
        col2=self.wrObj.writeData(name="P_Ch1",format=str(self.dataOut.nFFTPoints)+'E',data=10*numpy.log10(self.dataOut.data_spc[0,:]))
        col3=self.wrObj.writeData(name="P_Ch2",format=str(self.dataOut.nFFTPoints)+'E',data=10*numpy.log10(self.dataOut.data_spc[1,:]))
        col4=self.wrObj.writeData(name="P_Ch3",format=str(self.dataOut.nFFTPoints)+'E',data=10*numpy.log10(self.dataOut.data_spc[2,:]))
        col5=self.wrObj.writeData(name="P_Ch4",format=str(self.dataOut.nFFTPoints)+'E',data=10*numpy.log10(self.dataOut.data_spc[3,:]))
        col6=self.wrObj.writeData(name="P_Ch5",format=str(self.dataOut.nFFTPoints)+'E',data=10*numpy.log10(self.dataOut.data_spc[4,:]))
        col7=self.wrObj.writeData(name="P_Ch6",format=str(self.dataOut.nFFTPoints)+'E',data=10*numpy.log10(self.dataOut.data_spc[5,:]))
        col8=self.wrObj.writeData(name="P_Ch7",format=str(self.dataOut.nFFTPoints)+'E',data=10*numpy.log10(self.dataOut.data_spc[6,:]))
        col9=self.wrObj.writeData(name="P_Ch8",format=str(self.dataOut.nFFTPoints)+'E',data=10*numpy.log10(self.dataOut.data_spc[7,:]))
        #n=numpy.arange((100))
        n=self.dataOut.data_spc[6,:]
        a=self.wrObj.cFImage(n)
        b=self.wrObj.Ctable(col1,col2,col3,col4,col5,col6,col7,col8,col9)
        self.wrObj.CFile(a,b)
        self.wrObj.wFile(filename)
        return 1

class FITS: 
    
    name=None
    format=None
    array =None
    data =None
    thdulist=None
    
    def __init__(self):
        
        pass
    
    def setColF(self,name,format,array):
        self.name=name
        self.format=format
        self.array=array
        a1=numpy.array([self.array],dtype=numpy.float32)
        self.col1 = pyfits.Column(name=self.name, format=self.format, array=a1)
        return self.col1
            
#    def setColP(self,name,format,data):
#        self.name=name
#        self.format=format
#        self.data=data
#        a2=numpy.array([self.data],dtype=numpy.float32)
#        self.col2 = pyfits.Column(name=self.name, format=self.format, array=a2)
#        return self.col2
    
    def writeHeader(self,):
        pass
    
    def writeData(self,name,format,data):
        self.name=name
        self.format=format
        self.data=data
        a2=numpy.array([self.data],dtype=numpy.float32)
        self.col2 = pyfits.Column(name=self.name, format=self.format, array=a2)
        return self.col2
    
    def cFImage(self,n):
        self.hdu= pyfits.PrimaryHDU(n)
        return self.hdu
    
    def Ctable(self,col1,col2,col3,col4,col5,col6,col7,col8,col9):
        self.cols=pyfits.ColDefs( [col1,col2,col3,col4,col5,col6,col7,col8,col9])
        self.tbhdu = pyfits.new_table(self.cols)
        return self.tbhdu
    
    def CFile(self,hdu,tbhdu):
        self.thdulist=pyfits.HDUList([hdu,tbhdu])
        
    def wFile(self,filename):
        self.thdulist.writeto(filename)