'''
Created on 23/01/2012

@author $Author: dsuarez $
@version $Id: VoltageIO.py 110 2012-07-19 15:18:18Z dsuarez $
'''

import os, sys
import numpy
import glob
import fnmatch
import time, datetime

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from JROHeader import *
from JRODataIO import JRODataReader
from JRODataIO import JRODataWriter

from Data.Voltage import Voltage

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
    dataOutObj = None
    
    datablock = None

    ext = ".r"
    
    optchar = "D"
    
    
    def __init__(self, dataOutObj=None):
        """
        Inicializador de la clase VoltageReader para la lectura de datos de voltage.
        
        Input:
            dataOutObj    :    Objeto de la clase Voltage. Este objeto sera utilizado para
                              almacenar un perfil de datos cada vez que se haga un requerimiento
                              (getData). El perfil sera obtenido a partir del buffer de datos,
                              si el buffer esta vacio se hara un nuevo proceso de lectura de un
                              bloque de datos.
                              Si este parametro no es pasado se creara uno internamente.
        
        Variables afectadas:
            self.dataOutObj
        
        Return:
            None
        """
        
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
            self.dataOutObj
            self.profileIndex
            
        Affected:
            self.dataOutObj
            self.profileIndex
            self.flagTimeBlock
            self.flagIsNewBlock
        """
        if self.flagNoMoreFiles: return 0
         
        self.flagTimeBlock = 0
        self.flagIsNewBlock = 0
        
        if self.__hasNotDataInBuffer():

            if not( self.readNextBlock() ):
                return 0
            
#            self.updateDataHeader()
            
        if self.flagNoMoreFiles == 1:
            print 'Process finished'
            return 0
        
        #data es un numpy array de 3 dmensiones (perfiles, alturas y canales)
        
        if self.datablock == None:
            self.dataOutObj.flagNoData = True
            return 0
        
        self.dataOutObj.data = self.datablock[:,self.profileIndex,:]
        
        self.dataOutObj.dtype = self.dtype
        
        self.dataOutObj.nChannels = self.systemHeaderObj.nChannels
        
        self.dataOutObj.nHeights = self.processingHeaderObj.nHeights
        
        self.dataOutObj.nProfiles = self.processingHeaderObj.profilesPerBlock
        
        xf = self.processingHeaderObj.firstHeight + self.processingHeaderObj.nHeights*self.processingHeaderObj.deltaHeight

        self.dataOutObj.heightList = numpy.arange(self.processingHeaderObj.firstHeight, xf, self.processingHeaderObj.deltaHeight) 
        
        self.dataOutObj.channelList = range(self.systemHeaderObj.nChannels)
        
        self.dataOutObj.channelIndexList = range(self.systemHeaderObj.nChannels)
        
        self.dataOutObj.flagNoData = True
        
        self.dataOutObj.flagTimeBlock = self.flagTimeBlock
        
        self.dataOutObj.dataUtcTime = self.basicHeaderObj.utc + self.profileIndex * self.ippSeconds
        
        self.dataOutObj.nCohInt = self.processingHeaderObj.nCohInt
        
        self.profileIndex += 1
        
        self.dataOutObj.systemHeaderObj = self.systemHeaderObj.copy()
        
        self.dataOutObj.radarControllerHeaderObj = self.radarControllerHeaderObj.copy()
    
        return 1


class VoltageWriter(JRODataWriter):
    """ 
    Esta clase permite escribir datos de voltajes a archivos procesados (.r). La escritura
    de los datos siempre se realiza por bloques. 
    """
    __configHeaderFile = 'wrSetHeadet.txt'
    
    dataOutObj = None
    
    ext = ".r"
    
    optchar = "D"
    
    datablock = None
    
    profileIndex = 0
    
    shapeBuffer = None
    

    def __init__(self, dataOutObj=None):
        """ 
        Inicializador de la clase VoltageWriter para la escritura de datos de espectros.
         
        Affected: 
            self.dataOutObj

        Return: None
        """
        if dataOutObj == None:
            dataOutObj = Voltage()    
        
        if not( isinstance(dataOutObj, Voltage) ):
            raise ValueError, "in VoltageReader, dataOutObj must be an Spectra class object"

        self.dataOutObj = dataOutObj


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
                            self.systemHeaderObj.nChannels )
            
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
        self.flagIsNewBlock = 0
        
        if self.dataOutObj.flagNoData:
            return 0
        
        if self.dataOutObj.flagTimeBlock:
            
            self.datablock.fill(0)
            self.profileIndex = 0
            self.setNextFile()
        
        self.datablock[:,self.profileIndex,:] = self.dataOutObj.data
        
        self.profileIndex += 1
        
        if self.hasAllDataInBuffer():
            #if self.flagIsNewFile: 
            self.getDataHeader()
            self.writeNextBlock()
        
        if self.flagNoMoreFiles:
            #print 'Process finished'
            return 0
        
        return 1
    
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
        
#        CALCULAR PARAMETROS
        
        self.systemHeaderObj = self.dataOutObj.systemHeaderObj.copy()
        self.radarControllerHeaderObj = self.dataOutObj.radarControllerHeaderObj.copy()
        
        self.basicHeaderObj.size = self.basicHeaderSize
        self.basicHeaderObj.version = self.versionFile
        self.basicHeaderObj.dataBlock = self.nTotalBlocks
        self.basicHeaderObj.utc = self.dataOutObj.dataUtcTime
        self.basicHeaderObj.miliSecond = 0
        self.basicHeaderObj.timeZone = 0
        self.basicHeaderObj.dstFlag = 0
        self.basicHeaderObj.errorCount = 0
        
        self.processingHeaderObj.size = 0
        self.processingHeaderObj.dtype = self.dataOutObj.dtype
        self.processingHeaderObj.blockSize = 0
        self.processingHeaderObj.profilesPerBlock = 0
        self.processingHeaderObj.dataBlocksPerFile = 0
        self.processingHeaderObj.numWindows = 0
        self.processingHeaderObj.processFlags = 0
        self.processingHeaderObj.coherentInt = 0
        self.processingHeaderObj.incoherentInt = 0
        self.processingHeaderObj.totalSpectra = 0
        
        self.dtype = self.dataOutObj.dtype
        