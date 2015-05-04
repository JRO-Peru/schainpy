'''

'''
import os
import sys
import glob
import time
import numpy
import fnmatch
import time, datetime
#import h5py
import traceback

#try:
#    import pyfits
#except:
#    print "pyfits module has not been imported, it should be installed to save files in fits format"

#from jrodata import *
#from jroheaderIO import *
#from jroprocessing import *

#import re
#from xml.etree.ElementTree import Element, SubElement, ElementTree


LOCALTIME = True #-18000

from model.data.jroheaderIO import PROCFLAG, BasicHeader, SystemHeader, RadarControllerHeader, ProcessingHeader

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
    basicHeaderObj = BasicHeader(LOCALTIME)
    
    try:
        fp = open(filename,'rb')
    except IOError:
        traceback.print_exc()
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
    except IOError:
        traceback.print_exc()
        raise IOError, "The file %s can't be opened" %(filename)
    
    basicHeaderObj = BasicHeader(LOCALTIME)
    sts = basicHeaderObj.read(fp)
    fp.close()
    
    thisDatetime = basicHeaderObj.datatime
    thisTime = thisDatetime.time()
    
    if not(sts):
        print "Skipping the file %s because it has not a valid header" %(filename)
        return None
    
    if not ((startTime <= thisTime) and (endTime > thisTime)):
        return None
    
    return thisDatetime

def getFileFromSet(path, ext, set):
    validFilelist = []
    fileList = os.listdir(path)
    
    # 0 1234 567 89A BCDE
    # H YYYY DDD SSS .ext
    
    for thisFile in fileList:
        try:
            year = int(thisFile[1:5])
            doy  = int(thisFile[5:8])
        except:
            continue
        
        if (os.path.splitext(thisFile)[-1].lower() != ext.lower()):
            continue
        
        validFilelist.append(thisFile)

    myfile = fnmatch.filter(validFilelist,'*%4.4d%3.3d%3.3d*'%(year,doy,set))
    
    if len(myfile)!= 0:
        return myfile[0]
    else:
        filename = '*%4.4d%3.3d%3.3d%s'%(year,doy,set,ext.lower())
        print 'the filename %s does not exist'%filename
        print '...going to the last file: '
        
    if validFilelist:
        validFilelist = sorted( validFilelist, key=str.lower )
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
        validFilelist = sorted( validFilelist, key=str.lower )
        return validFilelist[-1]

    return None

def checkForRealPath(path, foldercounter, year, doy, set, ext):
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
            if foldercounter == 0:
                thispath = os.path.join(path, "%s%04d%03d" % ( prefixDir, year, doy )) 
            else:
                thispath = os.path.join(path, "%s%04d%03d_%02d" % ( prefixDir, year, doy , foldercounter))
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

def isDoyFolder(folder):
    try:
        year = int(folder[1:5])
    except:
        return 0
    
    try:
        doy = int(folder[5:8])
    except:
        return 0
    
    return 1

class JRODataIO:
    
    c = 3E8
    
    isConfig = False
    
    basicHeaderObj = None
    
    systemHeaderObj = None
    
    radarControllerHeaderObj = None
    
    processingHeaderObj = None
    
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
    
#     ippSeconds = None
    
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
    
    getByBlock = False
    
    def __init__(self):
        
        raise ValueError, "Not implemented"
    
    def run(self):
        
        raise ValueError, "Not implemented"

class JRODataReader(JRODataIO):
    
    nReadBlocks = 0
    
    delay  = 10   #number of seconds waiting a new file
        
    nTries  = 3  #quantity tries
        
    nFiles = 3   #number of files for searching
    
    path = None
    
    foldercounter = 0
    
    flagNoMoreFiles = 0
    
    datetimeList = []
    
    __isFirstTimeOnline = 1
    
    __printInfo = True
    
    profileIndex = None
    
    nTxs = 1
    
    txIndex = None
    
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
            #pathList.append(path)
            multi_path = path.split(',')
            for single_path in multi_path:
                pathList.append(single_path)
        
        else:
            #dirList = []
            multi_path = path.split(',')
            for single_path in multi_path:
                dirList = []
                for thisPath in os.listdir(single_path):
                    if not os.path.isdir(os.path.join(single_path,thisPath)):
                        continue
                    if not isDoyFolder(thisPath):
                        continue
                
                    dirList.append(thisPath)
    
                if not(dirList):
                    return None, None
            
                thisDate = startDate
            
                while(thisDate <= endDate):
                    year = thisDate.timetuple().tm_year
                    doy = thisDate.timetuple().tm_yday
                    
                    matchlist = fnmatch.filter(dirList, '?' + '%4.4d%3.3d' % (year,doy) + '*')
                    if len(matchlist) == 0:
                        thisDate += datetime.timedelta(1)
                        continue
                    for match in matchlist:
                        pathList.append(os.path.join(single_path,match,expLabel))
                    
                    thisDate += datetime.timedelta(1)
        
        if pathList == []:
            print "Any folder was found for the date range: %s-%s" %(startDate, endDate)
            return None, None
        
        print "%d folder(s) was(were) found for the date range: %s - %s" %(len(pathList), startDate, endDate)
            
        filenameList = []
        datetimeList = []
        pathDict = {}
        filenameList_to_sort = []
        
        for i in range(len(pathList)):
            
            thisPath = pathList[i]
            
            fileList = glob.glob1(thisPath, "*%s" %ext)
            if len(fileList) < 1:
                continue
            
            fileList.sort()
            pathDict.setdefault(fileList[0])
            pathDict[fileList[0]] = i
            filenameList_to_sort.append(fileList[0])
        
        filenameList_to_sort.sort()
        
        for file in filenameList_to_sort:
            thisPath = pathList[pathDict[file]]
            
            fileList = glob.glob1(thisPath, "*%s" %ext)
            fileList.sort()
        
            for file in fileList:
                
                filename = os.path.join(thisPath,file)
                thisDatetime = isFileinThisTime(filename, startTime, endTime)
                
                if not(thisDatetime):
                    continue
                
                filenameList.append(filename)
                datetimeList.append(thisDatetime)
                
        if not(filenameList):
            print "Any file was found for the time range %s - %s" %(startTime, endTime)
            return None, None
        
        print "%d file(s) was(were) found for the time range: %s - %s" %(len(filenameList), startTime, endTime)
        print
        
        for i in range(len(filenameList)):
            print "%s -> [%s]" %(filenameList[i], datetimeList[i].ctime())

        self.filenameList = filenameList
        self.datetimeList = datetimeList
        
        return pathList, filenameList

    def __searchFilesOnLine(self, path, expLabel = "", ext = None, walk=True, set=None):
        
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
        
        if not walk:
            fullpath = path
            foldercounter = 0
        else:
            #Filtra solo los directorios
            for thisPath in os.listdir(path):
                if not os.path.isdir(os.path.join(path,thisPath)):
                    continue
                if not isDoyFolder(thisPath):
                    continue
                
                dirList.append(thisPath)
            
            if not(dirList):
                return None, None, None, None, None, None
        
            dirList = sorted( dirList, key=str.lower )
                
            doypath = dirList[-1]
            foldercounter = int(doypath.split('_')[1]) if len(doypath.split('_'))>1 else 0
            fullpath = os.path.join(path, doypath, expLabel)
            
            
        print "%s folder was found: " %(fullpath )

        if set == None:
            filename = getlastFileFromPath(fullpath, ext)
        else:
            filename = getFileFromSet(fullpath, ext, set)

        if not(filename):
            return None, None, None, None, None, None
        
        print "%s file was found" %(filename)
        
        if not(self.__verifyFile(os.path.join(fullpath, filename))):
            return None, None, None, None, None, None

        year = int( filename[1:5] )
        doy  = int( filename[5:8] )
        set  = int( filename[8:11] )        
        
        return fullpath, foldercounter, filename, year, doy, set
    
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
        
        if self.set > 999:
            self.set = 0
            self.foldercounter += 1 
        
        #busca el 1er file disponible
        fullfilename, filename = checkForRealPath( self.path, self.foldercounter, self.year, self.doy, self.set, self.ext )
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
                    
                    fullfilename, filename = checkForRealPath( self.path, self.foldercounter, self.year, self.doy, self.set, self.ext )
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
                    self.foldercounter = 0

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
                self.basicHeaderObj.read(self.fp)
                return 1
            
            if self.fileSize == self.fileSizeByHeader:
#                self.flagEoF = True
                return 0
            
            print "\tWaiting %0.2f seconds for the next block, try %03d ..." % (self.delay, nTries+1)
            time.sleep( self.delay )
            
        
        return 0        

    def waitDataBlock(self,pointer_location):
        
        currentPointer = pointer_location
        
        neededSize = self.processingHeaderObj.blockSize #+ self.basicHeaderSize
        
        for nTries in range( self.nTries ):
            self.fp.close()
            self.fp = open( self.filename, 'rb' )
            self.fp.seek( currentPointer )
            
            self.fileSize = os.path.getsize( self.filename )
            currentSize = self.fileSize - currentPointer
            
            if ( currentSize >= neededSize ):
                return 1
            
            print "\tWaiting %0.2f seconds for the next block, try %03d ..." % (self.delay, nTries+1)
            time.sleep( self.delay )
        
        return 0

    def __jumpToLastBlock(self):
        
        if not(self.__isFirstTimeOnline):
            return
        
        csize = self.fileSize - self.fp.tell()
        blocksize = self.processingHeaderObj.blockSize
        
        #salta el primer bloque de datos
        if csize > self.processingHeaderObj.blockSize:
            self.fp.seek(self.fp.tell() + blocksize)
        else:
            return
        
        csize = self.fileSize - self.fp.tell()
        neededsize = self.processingHeaderObj.blockSize + self.basicHeaderSize
        while True:
            
            if self.fp.tell()<self.fileSize:
                self.fp.seek(self.fp.tell() + neededsize)
            else:
                self.fp.seek(self.fp.tell() - neededsize)
                break
        
#        csize = self.fileSize - self.fp.tell()
#        neededsize = self.processingHeaderObj.blockSize + self.basicHeaderSize
#        factor = int(csize/neededsize)
#        if factor > 0:
#            self.fp.seek(self.fp.tell() + factor*neededsize)
        
        self.flagIsNewFile = 0
        self.__isFirstTimeOnline = 0

    def __setNewBlock(self):
        
        if self.fp == None:
            return 0
        
        if self.online:
            self.__jumpToLastBlock()
        
        if self.flagIsNewFile:
            return 1
        
        self.lastUTTime = self.basicHeaderObj.utc
        currentSize = self.fileSize - self.fp.tell()
        neededSize = self.processingHeaderObj.blockSize + self.basicHeaderSize
        
        if (currentSize >= neededSize):
            self.basicHeaderObj.read(self.fp)
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

    def __readFirstHeader(self):
        
        self.basicHeaderObj.read(self.fp)
        self.systemHeaderObj.read(self.fp)
        self.radarControllerHeaderObj.read(self.fp)
        self.processingHeaderObj.read(self.fp)

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
        #self.ippSeconds = 2 * 1000 * self.radarControllerHeaderObj.ipp / self.c
        self.fileSizeByHeader = self.processingHeaderObj.dataBlocksPerFile * self.processingHeaderObj.blockSize + self.firstHeaderSize + self.basicHeaderSize*(self.processingHeaderObj.dataBlocksPerFile - 1)
#        self.dataOut.channelList = numpy.arange(self.systemHeaderObj.numChannels)
#        self.dataOut.channelIndexList = numpy.arange(self.systemHeaderObj.numChannels)
        self.getBlockDimension()
    
    def __verifyFile(self, filename, msgFlag=True):
        msg = None
        try:
            fp = open(filename, 'rb')
            currentPosition = fp.tell()
        except IOError:
            traceback.print_exc()
            if msgFlag:
                print "The file %s can't be opened" % (filename)
            return False

        neededSize = self.processingHeaderObj.blockSize + self.firstHeaderSize

        if neededSize == 0:
            basicHeaderObj = BasicHeader(LOCALTIME)
            systemHeaderObj = SystemHeader()
            radarControllerHeaderObj = RadarControllerHeader()
            processingHeaderObj = ProcessingHeader()

            try:
                if not( basicHeaderObj.read(fp) ): raise IOError
                if not( systemHeaderObj.read(fp) ): raise IOError
                if not( radarControllerHeaderObj.read(fp) ): raise IOError
                if not( processingHeaderObj.read(fp) ): raise IOError
#                 data_type = int(numpy.log2((processingHeaderObj.processFlags & PROCFLAG.DATATYPE_MASK))-numpy.log2(PROCFLAG.DATATYPE_CHAR))

                neededSize = processingHeaderObj.blockSize + basicHeaderObj.size

            except IOError:
                traceback.print_exc()
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
                set=None, 
                expLabel = "", 
                ext = None, 
                online = False,
                delay = 60,
                walk = True,
                getblock = False,
                nTxs = 1):

        if path == None:
            raise ValueError, "The path is not valid"

        if ext == None:
            ext = self.ext

        if online:
            print "Searching files in online mode..."  
                   
            for nTries in range( self.nTries ):
                fullpath, foldercounter, file, year, doy, set = self.__searchFilesOnLine(path=path, expLabel=expLabel, ext=ext, walk=walk, set=set)
                
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
            self.foldercounter = foldercounter
            last_set = None
        
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
            file_name = os.path.basename(filenameList[-1])
            basename, ext = os.path.splitext(file_name)
            last_set = int(basename[-3:])
            
        self.online = online
        self.delay = delay
        ext = ext.lower()
        self.ext = ext
        self.getByBlock = getblock
        self.nTxs = int(nTxs)
        
        if not(self.setNextFile()):
            if (startDate!=None) and (endDate!=None):
                print "No files in range: %s - %s" %(datetime.datetime.combine(startDate,startTime).ctime(), datetime.datetime.combine(endDate,endTime).ctime())
            elif startDate != None:
                print "No files in range: %s" %(datetime.datetime.combine(startDate,startTime).ctime())
            else:
                print "No files"

            sys.exit(-1)

#        self.updateDataHeader()
        if last_set != None:
            self.dataOut.last_block = last_set * self.processingHeaderObj.dataBlocksPerFile + self.basicHeaderObj.dataBlock
        return

    def getBasicHeader(self):
        
        self.dataOut.utctime = self.basicHeaderObj.utc + self.basicHeaderObj.miliSecond/1000. + self.profileIndex * self.radarControllerHeaderObj.ippSeconds
        
        self.dataOut.flagTimeBlock = self.flagTimeBlock
        
        self.dataOut.timeZone = self.basicHeaderObj.timeZone
    
        self.dataOut.dstFlag = self.basicHeaderObj.dstFlag
        
        self.dataOut.errorCount = self.basicHeaderObj.errorCount
        
        self.dataOut.useLocalTime = self.basicHeaderObj.useLocalTime
        
        self.dataOut.ippSeconds = self.radarControllerHeaderObj.ippSeconds/self.nTxs
        
        self.dataOut.nProfiles = self.processingHeaderObj.profilesPerBlock*self.nTxs
        
        
    def getFirstHeader(self):
        
        raise ValueError, "This method has not been implemented"
    
    def getData(self):
        
        raise ValueError, "This method has not been implemented"

    def hasNotDataInBuffer(self):
        
        raise ValueError, "This method has not been implemented"

    def readBlock(self):
        
        raise ValueError, "This method has not been implemented"
    
    def isEndProcess(self):
        
        return self.flagNoMoreFiles
    
    def printReadBlocks(self):
        
        print "Number of read blocks per file %04d" %self.nReadBlocks
    
    def printTotalBlocks(self):
        
        print "Number of read blocks %04d" %self.nTotalBlocks

    def printNumberOfBlock(self):
        
        if self.flagIsNewBlock:
            print "Block No. %04d, Total blocks %04d -> %s" %(self.basicHeaderObj.dataBlock, self.nTotalBlocks, self.dataOut.datatime.ctime())
            self.dataOut.blocknow = self.basicHeaderObj.dataBlock

    def printInfo(self):
        
        if self.__printInfo == False:
            return
        
        self.basicHeaderObj.printInfo()
        self.systemHeaderObj.printInfo()
        self.radarControllerHeaderObj.printInfo()
        self.processingHeaderObj.printInfo()
        
        self.__printInfo = False
        
    
    def run(self, **kwargs):
        
        if not(self.isConfig):
            
#            self.dataOut = dataOut
            self.setup(**kwargs)
            self.isConfig = True
            
        self.getData()

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

    
    def setBasicHeader(self):
        
        self.basicHeaderObj.size = self.basicHeaderSize #bytes
        self.basicHeaderObj.version = self.versionFile
        self.basicHeaderObj.dataBlock = self.nTotalBlocks
        
        utc = numpy.floor(self.dataOut.utctime)
        milisecond  = (self.dataOut.utctime - utc)* 1000.0
        
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
        
        timeTuple = time.localtime( self.dataOut.utctime)
        subfolder = 'd%4.4d%3.3d' % (timeTuple.tm_year,timeTuple.tm_yday)

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
        
        self.setFirstHeader()
        
        print 'Writing the file: %s'%self.filename
        
        self.__writeFirstHeader()
        
        return 1
    
    def setup(self, dataOut, path, blocksPerFile, profilesPerBlock=64, set=0, ext=None):
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

