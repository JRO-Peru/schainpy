''' 
File: SpectraIO.py
Created on 20/02/2012

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

from HeaderIO import *
from DataIO import DataReader
from DataIO import DataWriter

from Model.Spectra import Spectra


def getlastFileFromPath( pathList, ext ):
    """
    Depura el pathList dejando solo los que cumplan el formato de "PYYYYDDDSSS.ext"
    al final de la depuracion devuelve el ultimo file de la lista que quedo.  
    
    Input: 
        pathList    :    lista conteniendo todos los filename completos que componen una determinada carpeta
        ext         :    extension de los files contenidos en una carpeta 
            
    Return:
        El ultimo file de una determinada carpeta
    """
    
    filesList = []
    filename = None

    # 0 1234 567 89A BCDE
    # P YYYY DDD SSS .ext
    
    for filename in pathList:
        year = filename[1:5]
        doy  = filename[5:8]
        leng = len( ext )
        
        if ( filename[-leng:].upper() != ext.upper() ) : continue 
        if not( isNumber( year ) )  : continue
        if not( isNumber( doy )  )  : continue

        filesList.append(filename)

    if len( filesList ) > 0:
        #filesList.sort()
        filesList = sorted( filesList, key=str.lower )
        filename = filesList[-1]

    return filename
    

def checkForRealPath( path, year, doy, set, ext ):
    """
    Por ser Linux Case Sensitive entonces checkForRealPath encuentra el nombre correcto de un path,
    Prueba por varias combinaciones de nombres entre mayusculas y minusculas para determinar
    el path exacto de un determinado file.
    
    Example    :
        nombre correcto del file es  ../RAWDATA/D2009307/P2009307367
        
        Entonces la funcion prueba con las siguientes combinaciones
            ../RAWDATA/d2009307/p2009307367
            ../RAWDATA/d2009307/P2009307367
            ../RAWDATA/D2009307/p2009307367
            ../RAWDATA/D2009307/P2009307367
        siendo para este caso, la ultima combinacion de letras, identica al file buscado 
        
    Return:
        Si encuentra la cobinacion adecuada devuelve el path completo y el nombre del file 
        caso contrario devuelve None como path y el la ultima combinacion de nombre en mayusculas 
        para el filename  
    """
    filepath = None
    find_flag = False
    filename = None
    
    for dir in "dD": #barrido por las dos combinaciones posibles de "D"
        for fil in "pP": #barrido por las dos combinaciones posibles de "D"
            doypath = "%s%04d%03d" % ( dir, year, doy ) #formo el nombre del directorio xYYYYDDD (x=d o x=D)
            filename = "%s%04d%03d%03d%s" % ( fil, year, doy, set, ext ) #formo el nombre del file xYYYYDDDSSS.ext (p=d o p=D)
            filepath = os.path.join( path, doypath, filename ) #formo el path completo
            if os.path.exists( filepath ): #verifico que exista
                find_flag = True
                break
        if find_flag:
            break

    if not(find_flag):
        return None, filename

    return filepath, filename

def isNumber( str ):
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



def isThisFileinRange( filename, startUTSeconds, endUTSeconds ):
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
        fp = open( filename,'rb' ) #lectura binaria
    except:
        raise IOError, "The file %s can't be opened" %(filename)
    
    if not(m_BasicHeader.read(fp)):
        raise IOError, "The file %s has not a valid header" %(filename)
    
    fp.close()
    
    if not ((startUTSeconds <= m_BasicHeader.utc) and (endUTSeconds >= m_BasicHeader.utc)):
        return 0
    
    return 1


class SpectraReader( DataReader ):
    """ 
    Esta clase permite leer datos de espectros desde archivos procesados (.pdata). La lectura
    de los datos siempre se realiza por bloques. Los datos leidos (array de 3 dimensiones) 
    son almacenados en tres buffer's para el Self Spectra, el Cross Spectra y el DC Channel.

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
            
            print readerObj.m_Spectra.data
            
            if readerObj.noMoreFiles:
                break
            
    """
    
    #speed of light
    __c = 3E8
    
    
    def __init__( self, m_Spectra = None ):
        """ 
        Inicializador de la clase SpectraReader para la lectura de datos de espectros.

        Inputs: 
            m_Spectra    :    Objeto de la clase Spectra. Este objeto sera utilizado para
                              almacenar un perfil de datos cada vez que se haga un requerimiento
                              (getData). El perfil sera obtenido a partir del buffer de datos,
                              si el buffer esta vacio se hara un nuevo proceso de lectura de un
                              bloque de datos.
                              Si este parametro no es pasado se creara uno internamente.
         
        Affected: 
            self.m_Spectra
            self.m_BasicHeader
            self.m_SystemHeader
            self.m_RadarControllerHeader
            self.m_ProcessingHeader

        Return      : None
        """
        if m_Spectra == None:
            m_Spectra = Spectra()
        
        if not( isinstance(m_Spectra, Spectra) ):
            raise ValueError, "in SpectraReader, m_Spectra must be an Spectra class object"
        
        self.m_Spectra = m_Spectra
        
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
        
        self.flagResetProcessing = 0    
        
        self.flagIsNewBlock = 0
        
        self.noMoreFiles = 0
        
        self.nReadBlocks = 0
        
        self.online = 0
        
        self.firstHeaderSize = 0
        
        self.basicHeaderSize = 24
        
        self.filename = None
        
        self.fileSize = None
        
        self.__data_spc = None
        self.__data_cspc = None
        self.__data_dc = None

        self.nChannels = 0
        self.nPairs = 0
        
        self.__pts2read_SelfSpectra = 0
        self.__pts2read_CrossSpectra = 0
        self.__pts2read_DCchannels = 0
        self.__blocksize = 0
        
        self.__datablockIndex = 0
        
        self.__ippSeconds = 0
        
        self.nSelfChannels = 0
        
        self.nCrossPairs = 0
        
        self.__delay  = 7   #seconds
        self.__nTries  = 3  #quantity tries
        self.__nFiles = 3   #number of files for searching
        self.__year = 0 
        self.__doy = 0 
        self.__set = 0 
        self.__ext = None
        self.__path = None
        self.datablock_id = 9999

        
    def __rdSystemHeader( self, fp=None ):
        """ 
        Lectura del System Header

        Inputs: 
            fp    :    file pointer
         
        Affected:
            self.m_SystemHeader

        Return: None
        """
        if fp == None:
            fp = self.__fp
            
        self.m_SystemHeader.read( fp )


    
    def __rdRadarControllerHeader( self, fp=None ):
        """ 
        Lectura del Radar Controller Header

        Inputs: 
            fp    :    file pointer
         
        Affected: 
            self.m_RadarControllerHeader

        Return: None
        """
        if fp == None:
            fp = self.__fp
            
        self.m_RadarControllerHeader.read(fp)

        
    def __rdProcessingHeader( self,fp=None ):
        """ 
        Lectura del Processing Header

        Inputs: 
            fp    :    file pointer
         
        Affected: 
            self.m_ProcessingHeader

        Return: None
        """
        if fp == None:
            fp = self.__fp
            
        self.m_ProcessingHeader.read(fp)


    def __rdBasicHeader( self, fp=None ):
        """ 
        Lectura del  Basic Header

        Inputs: 
            fp    :    file pointer
         
        Affected: 
            self.m_BasicHeader

        Return: None
        """
        if fp == None:
            fp = self.__fp
            
        self.m_BasicHeader.read(fp)

    
    def __readFirstHeader( self ):
        """ 
        Lectura del First Header, es decir el Basic Header y el Long Header
            
        Affected:
            self.m_BasicHeader
            self.m_SystemHeader
            self.m_RadarControllerHeader
            self.m_ProcessingHeader
            self.firstHeaderSize
            self.__heights
            self.__dataType
            self.__fileSizeByHeader
            self.__ippSeconds
            self.nChannels
            self.nPairs
            self.__pts2read_SelfSpectra
            self.__pts2read_CrossSpectra
            
        Return: None
        """
        self.__rdBasicHeader()
        self.__rdSystemHeader()
        self.__rdRadarControllerHeader()
        self.__rdProcessingHeader()
        self.firstHeaderSize = self.m_BasicHeader.size
        
        data_type = int( numpy.log2((self.m_ProcessingHeader.processFlags & PROCFLAG.DATATYPE_MASK))-numpy.log2(PROCFLAG.DATATYPE_CHAR) )
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
        self.__ippSeconds = 2 * 1000 * self.m_RadarControllerHeader.ipp / self.__c
        
        self.nChannels = 0
        self.nPairs = 0
        
        for i in range( 0, self.m_ProcessingHeader.totalSpectra*2, 2 ):
            if self.m_ProcessingHeader.spectraComb[i] == self.m_ProcessingHeader.spectraComb[i+1]:
                self.nChannels = self.nChannels + 1 
            else:
                self.nPairs = self.nPairs + 1
        
        pts2read = self.m_ProcessingHeader.profilesPerBlock * self.m_ProcessingHeader.numHeights
        self.__pts2read_SelfSpectra = int( pts2read * self.nChannels )
        self.__pts2read_CrossSpectra = int( pts2read * self.nPairs )
        self.__pts2read_DCchannels = int( self.m_ProcessingHeader.numHeights * self.m_SystemHeader.numChannels )
        
        self.__blocksize = self.__pts2read_SelfSpectra + self.__pts2read_CrossSpectra + self.__pts2read_DCchannels   
        
        self.m_Spectra.nChannels = self.nChannels
        self.m_Spectra.nPairs = self.nPairs
         
        
    def __setNextFileOnline( self ):
        """
        Busca el siguiente file que tenga suficiente data para ser leida, dentro de un folder especifico, si
        no encuentra un file valido espera un tiempo determinado y luego busca en los posibles n files
        siguientes.   
            
        Affected: 
            self.__flagIsNewFile
            self.filename
            self.fileSize
            self.__fp
            self.__set
            self.noMoreFiles

        Return: 
            0    : si luego de una busqueda del siguiente file valido este no pudo ser encontrado
            1    : si el file fue abierto con exito y esta listo a ser leido
        
        Excepciones: 
            Si un determinado file no puede ser abierto
        """
        countFiles = 0
        countTries = 0
        
        fileStatus = 0
        notFirstTime_flag = False
        bChangeDir = False
        
        fileSize = 0
        fp = None
        
        self.__flagIsNewFile = 0
        
        while(True): #este loop permite llevar la cuenta de intentos, de files y carpetas, 
                     #si no encuentra alguno sale del bucle   
            
            countFiles += 1
            
            if countFiles > (self.__nFiles + 1):
                break
            
            self.__set += 1
                
            if countFiles > self.__nFiles: #si no encuentro el file buscado cambio de carpeta y busco en la siguiente carpeta
                self.__set = 0
                self.__doy += 1
                bChangeDir = True 
            
            file = None
            filename = None
            
            countTries = 0
            
            #espero hasta encontrar el 1er file disponible
            while( True ):
                
                countTries += 1
                if( countTries >= self.__nTries ): #checkeo que no haya ido mas alla de la cantidad de intentos
                    break
                
                file, filename = checkForRealPath( self.__path, self.__year, self.__doy, self.__set, self.__ext )
                if file != None:
                    break
                
                if notFirstTime_flag: #este flag me sirve solo para esperar por el 1er file, en lo siguientes no espera solo checkea si existe o no
                    countTries = self.__nTries
                    print "\tsearching next \"%s\" file ..." % filename 
                    break 
                
                print "\twaiting new \"%s\" file ..." % filename 
                time.sleep( self.__delay )
                
            if countTries >= self.__nTries: #se realizaron n intentos y no hubo un file nuevo 
                notFirstTime_flag = True
                continue #vuelvo al inico del while principal        
            
            countTries = 0
            
            #una vez que se obtuvo el 1er file valido se procede a checkear su contenido, y se espera una cierta cantidad
            #de tiempo por una cierta cantidad de veces hasta que el contenido del file sea un contenido valido
            while( True ):
                countTries += 1
                if countTries > self.__nTries:
                    break
                
                try:
                    fp = open(file)
                except:
                    print "The file \"%s\" can't be opened" % file
                    break
                
                fileSize = os.path.getsize( file )
                currentSize = fileSize - fp.tell()
                neededSize = self.m_ProcessingHeader.blockSize + self.firstHeaderSize
                
                if currentSize > neededSize:
                    fileStatus = 1
                    break
                
                fp.close()
                
                if bChangeDir: #si al buscar un file cambie de directorio ya no espero y salgo del bucle while
                    print "\tsearching next \"%s\" file ..." % filename
                    break
                
                print "\twaiting for block of \"%s\" file ..." % filename 
                time.sleep( self.__delay )
            
            if fileStatus == 1:
                break
            
            print "Skipping the file \"%s\" due to this files is empty" % filename
            countFiles = 0
        
        
        if fileStatus == 1:
            self.fileSize = fileSize
            self.filename = file#name
            self.__flagIsNewFile = 1
            self.__fp = fp
            self.noMoreFiles = 0
            print 'Setting the file: %s' % file #name
        else:
            self.fileSize = 0
            self.filename = None
            self.__fp = None
            self.noMoreFiles = 1
            print 'No more Files'

        return fileStatus
        

    def __setNextFileOffline( self ):
        """ 
        Busca el siguiente file dentro de un folder que tenga suficiente data para ser leida
            
        Affected: 
            self.__flagIsNewFile
            self.__idFile
            self.filename
            self.fileSize
            self.__fp

        Return: 
            0    : si un determinado file no puede ser abierto
            1    : si el file fue abierto con exito 
        
        Excepciones: 
            Si un determinado file no puede ser abierto
        """
        idFile = self.__idFile
        self.__flagIsNewFile = 0
        
        while(True):
            idFile += 1
            
            if not( idFile < len(self.filenameList) ):
                self.noMoreFiles = 1
                return 0
            
            filename = self.filenameList[idFile]
            fileSize = os.path.getsize(filename)
            
            try:
                fp = open( filename, 'rb' )
            except:
                raise IOError, "The file %s can't be opened" %filename
            
            currentSize = fileSize - fp.tell()
            neededSize = self.m_ProcessingHeader.blockSize + self.firstHeaderSize
            
            if (currentSize < neededSize):
                print "Skipping the file %s due to it hasn't enough data" %filename
                fp.close()
                continue
            
            break
        self.__flagIsNewFile = 1
        self.__idFile = idFile
        self.filename = filename
        self.fileSize = fileSize
        self.__fp = fp
        
        print 'Setting the file: %s'%self.filename
        
        return 1


    def __setNextFile( self ):
        """ 
        Determina el siguiente file a leer y si hay uno disponible lee el First Header
            
        Affected: 
            self.m_BasicHeader
            self.m_SystemHeader
            self.m_RadarControllerHeader
            self.m_ProcessingHeader
            self.firstHeaderSize

        Return: 
            0    :    Si no hay files disponibles
            1    :    Si hay mas files disponibles
        """
        if self.__fp != None:
            self.__fp.close()

        if self.online:
            newFile = self.__setNextFileOnline()
        else:
            newFile = self.__setNextFileOffline()
        
        if not(newFile):
            return 0
        
        self.__readFirstHeader()
        
        return 1
    
    
    def __setNewBlock( self ):
        """ 
        Lee el Basic Header y posiciona le file pointer en la posicion inicial del bloque a leer

        Affected: 
            self.m_BasicHeader
            self.flagResetProcessing
            self.ns

        Return: 
            0    :    Si el file no tiene un Basic Header que pueda ser leido
            1    :    Si se pudo leer el Basic Header
        """
        if self.__fp == None:
            return 0
        
        if self.__flagIsNewFile:
            return 1
        
        currentSize = self.fileSize - self.__fp.tell()
        neededSize = self.m_ProcessingHeader.blockSize + self.basicHeaderSize
        
        #If there is enough data setting new data block
        if ( currentSize >= neededSize ):
            self.__rdBasicHeader()
            return 1
        elif self.online:
            nTries = 0
            while( nTries < self.__nTries ):
                nTries += 1 
                print "Waiting for the next block, try %03d ..." % nTries
                time.sleep( self.__delay )
                
                fileSize = os.path.getsize(self.filename)
                currentSize = fileSize - self.__fp.tell()
                neededSize = self.m_ProcessingHeader.blockSize + self.basicHeaderSize

                if ( currentSize >= neededSize ):
                    self.__rdBasicHeader()
                    return 1
        
        #Setting new file 
        if not( self.__setNextFile() ):
            return 0
        
        deltaTime = self.m_BasicHeader.utc - self.__lastUTTime # check this
        
        self.flagResetProcessing = 0
        
        if deltaTime > self.__maxTimeStep:
            self.flagResetProcessing = 1
            self.ns = 0
            
        return 1
    

    def __readBlock(self):
        """
        Lee el bloque de datos desde la posicion actual del puntero del archivo
        (self.__fp) y actualiza todos los parametros relacionados al bloque de datos
        (metadata + data). La data leida es almacenada en el buffer y el contador del buffer
        es seteado a 0
        
        Return: None
        
        Variables afectadas:
            self.__datablockIndex
            self.__flagIsNewFile
            self.flagIsNewBlock
            self.nReadBlocks
            self.__data_spc
            self.__data_cspc
            self.__data_dc
        """
        self.datablock_id = 0
        self.__flagIsNewFile = 0
        self.flagIsNewBlock = 1

        fpointer = self.__fp.tell()

        spc = numpy.fromfile( self.__fp, self.__dataType[0], self.__pts2read_SelfSpectra )
        cspc = numpy.fromfile( self.__fp, self.__dataType, self.__pts2read_CrossSpectra )
        dc = numpy.fromfile( self.__fp, self.__dataType, self.__pts2read_DCchannels ) #int(self.m_ProcessingHeader.numHeights*self.m_SystemHeader.numChannels) )

        if self.online:
            if (spc.size + cspc.size + dc.size) != self.__blocksize:
                nTries = 0
                while( nTries < self.__nTries ):
                    nTries += 1 
                    print "Waiting for the next block, try %03d ..." % nTries
                    time.sleep( self.__delay )
                    self.__fp.seek( fpointer )
                    fpointer = self.__fp.tell() 
                    spc = numpy.fromfile( self.__fp, self.__dataType[0], self.__pts2read_SelfSpectra )
                    cspc = numpy.fromfile( self.__fp, self.__dataType, self.__pts2read_CrossSpectra )
                    dc = numpy.fromfile( self.__fp, self.__dataType, self.__pts2read_DCchannels ) #int(self.m_ProcessingHeader.numHeights*self.m_SystemHeader.numChannels) )
                    if (spc.size + cspc.size + dc.size) == self.__blocksize:
                        nTries = 0
                        break
                if nTries > 0:
                    return
        
        spc = spc.reshape( (self.nChannels, self.m_ProcessingHeader.numHeights, self.m_ProcessingHeader.profilesPerBlock) ) #transforma a un arreglo 3D 

        cspc = cspc.reshape( (self.nPairs, self.m_ProcessingHeader.numHeights, self.m_ProcessingHeader.profilesPerBlock) ) #transforma a un arreglo 3D
        dc = dc.reshape( (self.m_SystemHeader.numChannels, self.m_ProcessingHeader.numHeights) ) #transforma a un arreglo 2D
        
        if not( self.m_ProcessingHeader.shif_fft ):
            spc = numpy.roll( spc, self.m_ProcessingHeader.profilesPerBlock/2, axis=2 ) #desplaza a la derecha en el eje 2 determinadas posiciones
            cspc = numpy.roll( cspc, self.m_ProcessingHeader.profilesPerBlock/2, axis=2 ) #desplaza a la derecha en el eje 2 determinadas posiciones
        
        spc = numpy.transpose( spc, (0,2,1) )
        cspc = numpy.transpose( cspc, (0,2,1) )
        #dc = numpy.transpose(dc, (0,2,1))

        self.__data_spc = spc
        self.__data_cspc = cspc['real'] + cspc['imag']*1j
        self.__data_dc = dc['real'] + dc['imag']*1j

        self.__flagIsNewFile = 0
        
        self.flagIsNewBlock = 1
        
        self.nReadBlocks += 1
        self.datablock_id = 0

        
 
    def __hasNotDataInBuffer( self ):
        #if self.datablock_id >= self.m_ProcessingHeader.profilesPerBlock:
            return 1


    def __searchFilesOnLine( self, path, startDateTime=None, ext = ".pdata" ):
        """
        Busca el ultimo archivo de la ultima carpeta (determinada o no por startDateTime) y
        devuelve el archivo encontrado ademas de otros datos.
        
        Input: 
            path             :    carpeta donde estan contenidos los files que contiene data  
            startDateTime    :    punto especifico en el tiempo del cual se requiere la data
            ext              :    extension de los files  

        Return:
            year        :    el anho
            doy         :    el numero de dia del anho
            set         :    el set del archivo
            filename    :    el ultimo file de una determinada carpeta
            directory   :    eL directorio donde esta el file encontrado
        """

        print "Searching files ..."

        dirList = []
        directory = None
        
        if startDateTime == None:
            for thisPath in os.listdir(path):
                if os.path.isdir( os.path.join(path,thisPath) ):
                    dirList.append( thisPath )

            dirList = sorted( dirList, key=str.lower ) #para que quede ordenado al margen de si el nombre esta en mayusculas o minusculas, utilizo la funcion sorted 
            if len(dirList) > 0 :
                directory = dirList[-1]
        else:
            year = startDateTime.timetuple().tm_year
            doy = startDateTime.timetuple().tm_yday

            doyPath = "D%04d%03d" % (year,doy)  #caso del nombre en mayusculas
            if os.path.isdir( os.path.join(path,doyPath) ):
                directory = doyPath
            
            doyPath = doyPath.lower()   #caso del nombre en minusculas
            if os.path.isdir( os.path.join(path,doyPath) ):
                directory = doyPath

        if directory == None:
            return 0, 0, 0, None, None   
        
        filename = getlastFileFromPath( os.listdir( os.path.join(path,directory) ), ext )

        if filename == None:
            return 0, 0, 0, None, None 

        year = int( directory[-7:-3] )
        doy  = int( directory[-3:] )
        ln   = len( ext )
        set  = int( filename[-ln-3:-ln] )
        
        return year, doy, set, filename, directory


    def __searchFilesOffLine( self, path, startDateTime, endDateTime, set=None, expLabel = "", ext = ".pdata" ):
        """
        Realiza una busqueda de los archivos que coincidan con los parametros
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
                                file end time < startDateTime (objeto datetime.datetime)
                                                         
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


    def __initFilesOnline( self, path, dirfilename, filename ):
        """
        Verifica que el primer file tenga una data valida, para ello leo el 1er bloque
        del file, si no es un file valido espera una cierta cantidad de tiempo a que 
        lo sea, si transcurrido el tiempo no logra validar el file entonces el metodo
        devuelve 0 caso contrario devuelve 1
        
        Affected:
            m_BasicHeader
                   
        Return:
            0    :    file no valido para ser leido
            1    :    file valido para ser leido
        """
        m_BasicHeader = BasicHeader()
    
        file = os.path.join( path, dirfilename, filename )
        
        nTries = 0
        while(True):
            
            nTries += 1
            if nTries > self.__nTries:
                break
            
            try:
                fp = open( file,'rb' ) #lectura binaria
            except:
                raise IOError, "The file %s can't be opened" %(file)
            
            try:
                m_BasicHeader.read(fp)
            except:
                print "The file %s is empty" % filename
            
            fp.close()
            
            if m_BasicHeader.size > 24:
                break
            
            print 'waiting for new block: try %02d' % ( nTries )
            time.sleep( self.__delay)
            
        if m_BasicHeader.size <= 24:
            return 0
        
        return 1
    
    
    def setup( self, path, startDateTime=None, endDateTime=None, set=None, expLabel = "", ext = ".pdata", online = 0 ):
        """
        setup configura los parametros de lectura de la clase SpectraReader.
        
        Si el modo de lectura es offline, primero se realiza una busqueda de todos los archivos
        que coincidan con los parametros especificados; esta lista de archivos son almacenados en
        self.filenameList.
        
        Input:
            path                :    Directorios donde se ubican los datos a leer. Dentro de este
                                     directorio deberia de estar subdirectorios de la forma:
                                     
                                     path/D[yyyy][ddd]/expLabel/P[yyyy][ddd][sss][ext]
            
            startDateTime       :    Fecha inicial. Rechaza todos los archivos donde
                                     file end time < startDatetime (objeto datetime.datetime)
            
            endDateTime         :    Fecha final. Si no es None, rechaza todos los archivos donde
                                     file end time < startDatetime (objeto datetime.datetime)
            
            set                 :    Set del primer archivo a leer. Por defecto None
            
            expLabel            :    Nombre del subdirectorio de datos.  Por defecto ""
            
            ext                 :    Extension de los archivos a leer. Por defecto .pdata
            
            online              :    Si es == a 0 entonces busca files que cumplan con las condiciones dadas 
            
        Return:
            0    :    Si no encuentra files que cumplan con las condiciones dadas
            1    :    Si encuentra files que cumplan con las condiciones dadas
        
        Affected:
            self.startUTCSeconds
            self.endUTCSeconds
            self.startYear 
            self.endYear
            self.startDoy
            self.endDoy
            self.__pathList
            self.filenameList 
            self.online
        """

        if online:
            nTries = 0 
            while( nTries < self.__nTries ):
               nTries += 1 
               subfolder = "D%04d%03d" % ( startDateTime.timetuple().tm_year,startDateTime.timetuple().tm_yday )
               file = os.path.join( path, subfolder )
               print "Searching first file in \"%s\", try %03d ..." % ( file, nTries ) 
               year, doy, set, filename, dirfilename = self.__searchFilesOnLine( path, startDateTime, ext )
               if filename == None:
                   time.sleep( self.__delay )
               else:
                   break

            if filename == None:
                print "No files  On Line"
                return 0

            if self.__initFilesOnline( path, dirfilename, filename ) == 0:
                print "The file %s hasn't enough data"
                return 0            

            self.__year = year
            self.__doy  = doy
            self.__set  = set - 1
            self.__path = path

        else:
            pathList, filenameList = self.__searchFilesOffLine( path, startDateTime, endDateTime, set, expLabel, ext )
            self.__idFile = -1
            self.__pathList = pathList
            self.filenameList = filenameList
             
        self.online = online
        self.__ext = ext
        
        if not(self.__setNextFile()):
            if (startDateTime != None) and (endDateTime != None):
                print "No files in range: %s - %s" %(startDateTime.ctime(), endDateTime.ctime())
            elif startDateTime != None:
                print "No files in : %s" % startDateTime.ctime()
            else:
                print "No files"
            return 0
        
        if startDateTime != None:
            self.startUTCSeconds = time.mktime(startDateTime.timetuple())
            self.startYear = startDateTime.timetuple().tm_year 
            self.startDoy = startDateTime.timetuple().tm_yday
        
        if endDateTime != None:
            self.endUTCSeconds = time.mktime(endDateTime.timetuple())
            self.endYear = endDateTime.timetuple().tm_year
            self.endDoy = endDateTime.timetuple().tm_yday
        #call fillHeaderValues() - to Data Object
        
        self.m_Spectra.m_BasicHeader = self.m_BasicHeader.copy()
        self.m_Spectra.m_ProcessingHeader = self.m_ProcessingHeader.copy()
        self.m_Spectra.m_RadarControllerHeader = self.m_RadarControllerHeader.copy()
        self.m_Spectra.m_SystemHeader = self.m_SystemHeader.copy()
        self.m_Spectra.dataType = self.__dataType
        
        return 1
    
        
    def readNextBlock(self):
        """ 
        Establece un nuevo bloque de datos a leer y los lee, si es que no existiese
        mas bloques disponibles en el archivo actual salta al siguiente.

        Affected: 
            self.__lastUTTime

        Return: None
        """

        if not( self.__setNewBlock() ):
            return 0

        self.__readBlock()
        
        self.__lastUTTime = self.m_BasicHeader.utc
        
        return 1

   
    def getData(self):
        """
        Copia el buffer de lectura a la clase "Spectra",
        con todos los parametros asociados a este (metadata). cuando no hay datos en el buffer de
        lectura es necesario hacer una nueva lectura de los bloques de datos usando "readNextBlock"
        
        Return:
            0    :    Si no hay mas archivos disponibles
            1    :    Si hizo una buena copia del buffer
            
        Variables afectadas:
            self.m_Spectra
            self.__datablockIndex
            self.flagResetProcessing
            self.flagIsNewBlock
        """

        self.flagResetProcessing = 0
        self.flagIsNewBlock = 0
        
        if self.__hasNotDataInBuffer():            

            self.readNextBlock() 
            
            self.m_Spectra.m_BasicHeader = self.m_BasicHeader.copy()
            self.m_Spectra.m_ProcessingHeader = self.m_ProcessingHeader.copy()
            self.m_Spectra.m_RadarControllerHeader = self.m_RadarControllerHeader.copy()
            self.m_Spectra.m_SystemHeader = self.m_SystemHeader.copy()
            self.m_Spectra.heights = self.__heights
            self.m_Spectra.dataType = self.__dataType
        
        if self.noMoreFiles == 1:
            print 'Process finished'
            return 0
        
        #data es un numpy array de 3 dmensiones (perfiles, alturas y canales)

        self.m_Spectra.flagNoData = False
        self.m_Spectra.flagResetProcessing = self.flagResetProcessing
        
        self.m_Spectra.data_spc = self.__data_spc
        self.m_Spectra.data_cspc = self.__data_cspc
        self.m_Spectra.data_dc = self.__data_dc
        
        #call setData - to Data Object
        #self.datablock_id += 1
        #self.idProfile += 1

        return 1


class SpectraWriter( DataWriter ):
    """ 
    Esta clase permite escribir datos de espectros a archivos procesados (.pdata). La escritura
    de los datos siempre se realiza por bloques. 
    """
    
    def __init__( self, m_Spectra = None ):
        """ 
        Inicializador de la clase SpectraWriter para la escritura de datos de espectros.
         
        Affected: 
            self.m_Spectra
            self.m_BasicHeader
            self.m_SystemHeader
            self.m_RadarControllerHeader
            self.m_ProcessingHeader

        Return: None
        """
        
        if m_Spectra == None:
            m_Spectra = Spectra()    
        
        self.m_Spectra = m_Spectra
        
        self.__path = None
        
        self.__fp = None
        
        self.__format = None
    
        self.__blocksCounter = 0
        
        self.__setFile = None
        
        self.__flagIsNewFile = 1
        
        self.__dataType = None
        
        self.__ext = None
        
        self.__shape_spc_Buffer = None
        self.__shape_cspc_Buffer = None
        self.__shape_dc_Buffer = None
        
        self.nWriteBlocks = 0 
        
        self.flagIsNewBlock = 0
        
        self.noMoreFiles = 0
        
        self.filename = None
        
        self.m_BasicHeader= BasicHeader()
    
        self.m_SystemHeader = SystemHeader()
    
        self.m_RadarControllerHeader = RadarControllerHeader()
    
        self.m_ProcessingHeader = ProcessingHeader()
        
        self.__data_spc = None
        self.__data_cspc = None
        self.__data_dc = None
        
    def __writeFirstHeader( self ):
        """
        Escribe el primer header del file es decir el Basic header y el Long header (SystemHeader, RadarControllerHeader, ProcessingHeader)
        
        Affected:
            __dataType
            
        Return:
            None
        """
        self.__writeBasicHeader()
        self.__wrSystemHeader()
        self.__wrRadarControllerHeader()
        self.__wrProcessingHeader()
        self.__dataType = self.m_Spectra.dataType
            
    def __writeBasicHeader( self, fp=None ):
        """
        Escribe solo el Basic header en el file creado

        Return:
            None
        """
        if fp == None:
            fp = self.__fp
            
        self.m_BasicHeader.write(fp)
    
    def __wrSystemHeader( self, fp=None ):
        """
        Escribe solo el System header en el file creado

        Return:
            None
        """
        if fp == None:
            fp = self.__fp
            
        self.m_SystemHeader.write(fp)
    
    def __wrRadarControllerHeader( self, fp=None ):
        """
        Escribe solo el RadarController header en el file creado

        Return:
            None
        """
        if fp == None:
            fp = self.__fp
        
        self.m_RadarControllerHeader.write(fp)
        
    def __wrProcessingHeader( self, fp=None ):
        """
        Escribe solo el Processing header en el file creado

        Return:
            None
        """
        if fp == None:
            fp = self.__fp
            
        self.m_ProcessingHeader.write(fp)
    
    def __setNextFile( self ):
        """ 
        Determina el siguiente file que sera escrito

        Affected: 
            self.filename
            self.__subfolder
            self.__fp
            self.__setFile
            self.__flagIsNewFile

        Return:
            0    :    Si el archivo no puede ser escrito
            1    :    Si el archivo esta listo para ser escrito
        """
        ext = self.__ext
        path = self.__path
        
        if self.__fp != None:
            self.__fp.close()
        
        if self.m_BasicHeader.size <= 24: return 0 #no existe la suficiente data para ser escrita
        
        timeTuple = time.localtime(self.m_Spectra.m_BasicHeader.utc) # utc from m_Spectra
        subfolder = 'D%4.4d%3.3d' % (timeTuple.tm_year,timeTuple.tm_yday)

        tmp = os.path.join( path, subfolder )
        if not( os.path.exists(tmp) ):
            os.mkdir(tmp)
            self.__setFile = -1 #inicializo mi contador de seteo
        else:
            filesList = os.listdir( tmp )
            if len( filesList ) > 0:
                filesList = sorted( filesList, key=str.lower )
                filen = filesList[-1]
                # el filename debera tener el siguiente formato
                # 0 1234 567 89A BCDE (hex)
                # P YYYY DDD SSS .ext
                if isNumber( filen[8:11] ):
                    self.__setFile = int( filen[8:11] ) #inicializo mi contador de seteo al seteo del ultimo file
                else:    
                    self.__setFile = -1
            else:
                self.__setFile = -1 #inicializo mi contador de seteo
                
        setFile = self.__setFile
        setFile += 1
        file = 'P%4.4d%3.3d%3.3d%s' % ( timeTuple.tm_year, timeTuple.tm_yday, setFile, ext )
        
        filename = os.path.join( path, subfolder, file )
        
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
    
    def __setNewBlock( self ):
        """
        Si es un nuevo file escribe el First Header caso contrario escribe solo el Basic Header
        
        Return:
            0    :    si no pudo escribir nada
            1    :    Si escribio el Basic el First Header
        """        
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
    
    def __writeBlock( self ):
        """
        Escribe el buffer en el file designado
            
        Affected:
            self.__data_spc
            self.__data_cspc
            self.__data_dc
            self.__flagIsNewFile
            self.flagIsNewBlock
            self.nWriteBlocks
            self.__blocksCounter    
            
        Return: None
        """
        spc = numpy.transpose( self.__data_spc, (0,2,1) )
        if not( self.m_ProcessingHeader.shif_fft ):
            spc = numpy.roll( spc, self.m_ProcessingHeader.profilesPerBlock/2, axis=2 ) #desplaza a la derecha en el eje 2 determinadas posiciones
        data = spc.reshape((-1))
        data.tofile(self.__fp)

        data = numpy.zeros( self.__shape_cspc_Buffer, self.__dataType )
        cspc = numpy.transpose( self.__data_cspc, (0,2,1) )
        if not( self.m_ProcessingHeader.shif_fft ):
            cspc = numpy.roll( cspc, self.m_ProcessingHeader.profilesPerBlock/2, axis=2 ) #desplaza a la derecha en el eje 2 determinadas posiciones
        data['real'] = cspc.real
        data['imag'] = cspc.imag
        data = data.reshape((-1))
        data.tofile(self.__fp)

        data = numpy.zeros( self.__shape_dc_Buffer, self.__dataType )
        dc = self.__data_dc
        data['real'] = dc.real
        data['imag'] = dc.imag
        data = data.reshape((-1))
        data.tofile(self.__fp)

        self.__data_spc.fill(0)
        self.__data_cspc.fill(0)
        self.__data_dc.fill(0)
        
        self.__flagIsNewFile = 0
        
        self.flagIsNewBlock = 1
        
        self.nWriteBlocks += 1
        
        self.__blocksCounter += 1
    

    def writeNextBlock( self ):
        """
        Selecciona el bloque siguiente de datos y los escribe en un file
            
        Return: 
            0    :    Si no hizo pudo escribir el bloque de datos 
            1    :    Si no pudo escribir el bloque de datos
        """
        if not( self.__setNewBlock() ):
            return 0
        
        self.__writeBlock()
        
        return 1


    def __hasAllDataInBuffer( self ):
        return 1


    def putData( self ):
        """
        Setea un bloque de datos y luego los escribe en un file 
            
        Affected:
            self.__data_spc
            self.__data_cspc
            self.__data_dc

        Return: 
            0    :    Si no hay data o no hay mas files que puedan escribirse 
            1    :    Si se escribio la data de un bloque en un file
        """
        self.flagIsNewBlock = 0
        
        if self.m_Spectra.flagNoData:
            return 0
        
        if self.m_Spectra.flagResetProcessing:
            self.__data_spc.fill(0)
            self.__data_cspc.fill(0)
            self.__data_dc.fill(0)
            self.__setNextFile()
        
        self.__data_spc = self.m_Spectra.data_spc
        self.__data_cspc = self.m_Spectra.data_cspc
        self.__data_dc = self.m_Spectra.data_dc
        
        if True:
            #time.sleep( 3 )
            self.__getHeader()
            self.writeNextBlock()
        
        if self.noMoreFiles:
            #print 'Process finished'
            return 0
        
        return 1

    def __getHeader( self ):
        """
        Obtiene una copia del First Header
         
        Affected:
            self.m_BasicHeader
            self.m_SystemHeader
            self.m_RadarControllerHeader
            self.m_ProcessingHeader
            self.__dataType

        Return: 
            None
        """
        self.m_BasicHeader = self.m_Spectra.m_BasicHeader.copy()
        self.m_SystemHeader = self.m_Spectra.m_SystemHeader.copy()
        self.m_RadarControllerHeader = self.m_Spectra.m_RadarControllerHeader.copy()
        self.m_ProcessingHeader = self.m_Spectra.m_ProcessingHeader.copy()
        self.__dataType = self.m_Spectra.dataType
            
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

    def setup( self, path, format='pdata' ):
        """
        Setea el tipo de formato en la cual sera guardada la data y escribe el First Header 
            
        Inputs:
            path      :    el path destino en el cual se escribiran los files a crear
            format    :    formato en el cual sera salvado un file

        Return:
            0    :    Si no realizo un buen seteo
            1    :    Si realizo un buen seteo 
        """
        if format == 'hdf5':
            ext = '.hdf5'
            format = 'hdf5'
            print 'call hdf5 library'
            return 0
        
        if format == 'rawdata':
            ext = '.r'
            format = 'Jicamarca'

        if format == 'pdata':
            ext = '.pdata'
            format = 'pdata'
        
        #call to config_headers
        #self.__setHeaderByFile()
        
        self.__path = path
        self.__setFile = -1
        self.__ext = ext
        self.__format = format
        
        self.__getHeader()

        self.__shape_spc_Buffer = ( self.m_Spectra.nChannels,
                                    self.m_ProcessingHeader.numHeights,
                                    self.m_ProcessingHeader.profilesPerBlock
                                  )

        self.__shape_cspc_Buffer = ( self.m_Spectra.nPairs,
                                     self.m_ProcessingHeader.numHeights,
                                     self.m_ProcessingHeader.profilesPerBlock
                                   )
        
        self.__shape_dc_Buffer = ( self.m_SystemHeader.numChannels,
                                   self.m_ProcessingHeader.numHeights
                                 )
        
        if not( self.__setNextFile() ):
            print "There isn't a next file" #"zzzzzzzzzzzz"
            return 0

        return 1