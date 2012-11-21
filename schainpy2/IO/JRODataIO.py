'''

$Author$
$Id$
'''

import os, sys
import glob
import time
import numpy
import fnmatch
import time, datetime

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from JROHeaderIO import *
from Data.JROData import JROData

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
        
            if (os.path.splitext(file)[-1].upper() != ext.upper()) : continue
        except:
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
    filepath = None
    find_flag = False
    filename = None

    if ext.lower() == ".r": #voltage
        header1 = "dD"
        header2 = "dD"
    elif ext.lower() == ".pdata": #spectra
        header1 = "dD"
        header2 = "pP"
    else:
        return None, filename
            
    for dir in header1: #barrido por las dos combinaciones posibles de "D"
        for fil in header2: #barrido por las dos combinaciones posibles de "D"
            doypath = "%s%04d%03d" % ( dir, year, doy ) #formo el nombre del directorio xYYYYDDD (x=d o x=D)
            filename = "%s%04d%03d%03d%s" % ( fil, year, doy, set, ext ) #formo el nombre del file xYYYYDDDSSS.ext
            filepath = os.path.join( path, doypath, filename ) #formo el path completo
            if os.path.exists( filepath ): #verifico que exista
                find_flag = True
                break
        if find_flag:
            break

    if not(find_flag):
        return None, filename

    return filepath, filename

class JRODataIO:
    
    c = 3E8
    
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
    
    flagNoMoreFiles = 0
    
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
    
    dataOutObj = None
    
    blocksize = None
    
    set = None
    
    def __init__(self):
        pass

class JRODataReader(JRODataIO):
    
    nReadBlocks = 0
    
    delay  = 60   #number of seconds waiting a new file
        
    nTries  = 3  #quantity tries
        
    nFiles = 3   #number of files for searching
        
    
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
    
    def __searchFilesOnLine(self, path, startDate=None, endDate=None, startTime=None, endTime=None, expLabel = "", ext = None):
        
        """
        Busca el ultimo archivo de la ultima carpeta (determinada o no por startDateTime) y
        devuelve el archivo encontrado ademas de otros datos.
        
        Input: 
            path           :    carpeta donde estan contenidos los files que contiene data
            
            startDate      :    Fecha inicial. Rechaza todos los directorios donde 
                                file end time < startDate (obejto datetime.date)
                                                         
            endDate        :    Fecha final. Rechaza todos los directorios donde 
                                file start time > endDate (obejto datetime.date)
            
            startTime      :    Tiempo inicial. Rechaza todos los archivos donde 
                                file end time < startTime (obejto datetime.time)
                                                         
            endTime        :    Tiempo final. Rechaza todos los archivos donde 
                                file start time > endTime (obejto datetime.time)
            
            expLabel        :     Nombre del subexperimento (subfolder)
            
            ext              :    extension de los files  

        Return:
            directory   :    eL directorio donde esta el file encontrado
            filename    :    el ultimo file de una determinada carpeta
            year        :    el anho
            doy         :    el numero de dia del anho
            set         :    el set del archivo
            
            
        """
        dirList = []
        pathList = []
        directory = None
        
        #Filtra solo los directorios
        for thisPath in os.listdir(path):
            if os.path.isdir(os.path.join(path, thisPath)):
                dirList.append(thisPath)

        if not(dirList):
            return None, None, None, None, None

        dirList = sorted( dirList, key=str.lower )

        if startDate:
            startDateTime = datetime.datetime.combine(startDate, startTime)
            thisDateTime = startDateTime
            if endDate == None: endDateTime = startDateTime
            else: endDateTime = datetime.datetime.combine(endDate, endTime)
            
            while(thisDateTime <= endDateTime):
                year = thisDateTime.timetuple().tm_year
                doy = thisDateTime.timetuple().tm_yday
                
                match = fnmatch.filter(dirList, '?' + '%4.4d%3.3d' % (year,doy))
                if len(match) == 0:
                    thisDateTime += datetime.timedelta(1)
                    continue
                
                pathList.append(os.path.join(path,match[0], expLabel))
                thisDateTime += datetime.timedelta(1)

            if not(pathList):
                print "\tNo files in range: %s - %s" %(startDateTime.ctime(), endDateTime.ctime())
                return None, None, None, None, None

            directory = pathList[0]
            
        else:
            directory = dirList[-1]
            directory = os.path.join(path,directory)

        filename = getlastFileFromPath(directory, ext)

        if not(filename):
            return None, None, None, None, None

        if not(self.__verifyFile(os.path.join(directory, filename))):
            return None, None, None, None, None

        year = int( filename[1:5] )
        doy  = int( filename[5:8] )
        set  = int( filename[8:11] )        
        
        return directory, filename, year, doy, set
    
    def setup(self,dataOutObj=None, 
                path=None,
                startDate=None, 
                endDate=None, 
                startTime=datetime.time(0,0,0), 
                endTime=datetime.time(23,59,59), 
                set=0, 
                expLabel = "", 
                ext = None, 
                online = False,
                delay = 60):

        if path == None:
            raise ValueError, "The path is not valid"

        if ext == None:
            ext = self.ext

        if dataOutObj == None:
            dataOutObj = self.createObjByDefault()

        self.dataOutObj = dataOutObj

        if online:
            print "Searching files in online mode..."  
            doypath, file, year, doy, set = self.__searchFilesOnLine(path=path, expLabel=expLabel, ext=ext)        

            if not(doypath):
                for nTries in range( self.nTries ):
                    print '\tWaiting %0.2f sec for an valid file in %s: try %02d ...' % (self.delay, path, nTries+1)
                    time.sleep( self.delay )
                    doypath, file, year, doy, set = self.__searchFilesOnLine(path=path, expLabel=expLabel, ext=exp)        
                    if doypath:
                        break
            
            if not(doypath):
                print "There 'isn't valied files in %s" % path
                return None
        
            self.year = year
            self.doy  = doy
            self.set  = set - 1
            self.path = path

        else:
            print "Searching files in offline mode ..."
            pathList, filenameList = self.__searchFilesOffLine(path, startDate, endDate, startTime, endTime, set, expLabel, ext)
            
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
        file, filename = checkForRealPath( self.path, self.year, self.doy, self.set, self.ext )
        if file:
            if self.__verifyFile(file, False):
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
                    
                    file, filename = checkForRealPath( self.path, self.year, self.doy, self.set, self.ext )
                    if file:
                        if self.__verifyFile(file):
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
            self.fileSize = os.path.getsize( file )
            self.filename = file
            self.flagIsNewFile = 1
            if self.fp != None: self.fp.close() 
            self.fp = open(file, 'rb')
            self.flagNoMoreFiles = 0
            print 'Setting the file: %s' % file
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
#        self.dataOutObj.channelList = numpy.arange(self.systemHeaderObj.numChannels)
#        self.dataOutObj.channelIndexList = numpy.arange(self.systemHeaderObj.numChannels)
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
                if not( basicHeaderObj.read(fp) ): raise ValueError
                if not( systemHeaderObj.read(fp) ): raise ValueError
                if not( radarControllerHeaderObj.read(fp) ): raise ValueError
                if not( processingHeaderObj.read(fp) ): raise ValueError
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

    def getData():
        pass

    def hasNotDataInBuffer():
        pass

    def readBlock():
        pass

class JRODataWriter(JRODataIO):

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
    
    def __init__(self, dataOutObj=None):
        raise ValueError, "Not implemented"


    def hasAllDataInBuffer(self):
        raise ValueError, "Not implemented"


    def setBlockDimension(self):
        raise ValueError, "Not implemented"

    
    def writeBlock(self):
        raise ValueError, "No implemented"


    def putData(self):
        raise ValueError, "No implemented"

    
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
        
        self.__writeBasicHeader()
        self.__wrSystemHeader()
        self.__wrRadarControllerHeader()
        self.__wrProcessingHeader()
        self.dtype = self.dataOutObj.dtype
            
            
    def __writeBasicHeader(self, fp=None):
        """
        Escribe solo el Basic header en el file creado

        Return:
            None
        """
        if fp == None:
            fp = self.fp
            
        self.basicHeaderObj.write(fp)

    
    def __wrSystemHeader(self, fp=None):
        """
        Escribe solo el System header en el file creado

        Return:
            None
        """
        if fp == None:
            fp = self.fp
            
        self.systemHeaderObj.write(fp)

    
    def __wrRadarControllerHeader(self, fp=None):
        """
        Escribe solo el RadarController header en el file creado

        Return:
            None
        """
        if fp == None:
            fp = self.fp
        
        self.radarControllerHeaderObj.write(fp)

        
    def __wrProcessingHeader(self, fp=None):
        """
        Escribe solo el Processing header en el file creado

        Return:
            None
        """
        if fp == None:
            fp = self.fp
            
        self.processingHeaderObj.write(fp)
    
    
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
        
        timeTuple = time.localtime( self.dataOutObj.dataUtcTime)
        subfolder = 'D%4.4d%3.3d' % (timeTuple.tm_year,timeTuple.tm_yday)

        doypath = os.path.join( path, subfolder )
        if not( os.path.exists(doypath) ):
            os.mkdir(doypath)
            self.setFile = -1 #inicializo mi contador de seteo
        else:
            filesList = os.listdir( doypath )
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
            self.__writeBasicHeader()
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
    

    def getDataHeader(self):
        """Obtiene una copia del First Header  Affected: self.basicHeaderObj     self.
        systemHeaderObj self.radarControllerHeaderObj     self.processingHeaderObj self.
        dtype  Return:     None
        """
        
        raise ValueError, "No implemented"        
    
    def setup(self, path, blocksPerFile, profilesPerBlock=None, set=0, ext=None):
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
        
        if not(self.setNextFile()):
            print "There isn't a next file"
            return 0
        
        self.setBlockDimension()
        
        return 1






