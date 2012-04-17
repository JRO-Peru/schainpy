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

from Model.JROHeader import *
from Model.Voltage import Voltage

from IO.DataIO import JRODataReader
from IO.DataIO import JRODataWriter


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
    m_DataObj = None
    
    idProfile = 0
    
    datablock = None
    
    pts2read = 0
    
    utc = 0

    ext = ".r"
    
    optchar = "D"
    
    
    def __init__(self, m_Voltage=None):
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
            self.m_DataObj
        
        Return:
            None
        """
        if m_Voltage == None:
            m_Voltage = Voltage()
        
        if not(isinstance(m_Voltage, Voltage)):
            raise ValueError, "in VoltageReader, m_Voltage must be an Voltage class object"
        
        self.m_DataObj = m_Voltage

    
    def __hasNotDataInBuffer(self):
        if self.datablockIndex >= self.m_ProcessingHeader.profilesPerBlock:
            return 1
        return 0


    def getBlockDimension(self):
        """
        Obtiene la cantidad de puntos a leer por cada bloque de datos
        
        Affected:
            self.pts2read
            self.blocksize

        Return:
            None
        """
        self.pts2read = self.m_ProcessingHeader.profilesPerBlock * self.m_ProcessingHeader.numHeights * self.m_SystemHeader.numChannels
        self.blocksize = self.pts2read
        self.m_DataObj.nProfiles = self.m_ProcessingHeader.profilesPerBlock

            
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
            self.datablockIndex
            self.datablock
            self.flagIsNewFile
            self.idProfile
            self.flagIsNewBlock
            self.nReadBlocks
            
        Exceptions: 
            Si un bloque leido no es un bloque valido
        """
        blockOk_flag = False
        fpointer = self.fp.tell()
        
        junk = numpy.fromfile( self.fp, self.dataType, self.pts2read )
        
        if self.online:
            if junk.size != self.blocksize:
                for nTries in range( self.nTries ):
                    print "\tWaiting %0.2f sec for the next block, try %03d ..." % (self.delay, nTries+1)
                    time.sleep( self.delay )
                    self.fp.seek( fpointer )
                    fpointer = self.fp.tell() 
                    
                    junk = numpy.fromfile( self.fp, self.dataType, self.pts2read )
                    
                    if junk.size == self.blocksize:
                        blockOk_flag = True
                        break
                
                if not( blockOk_flag ):
                    return 0
        
        try:
            junk = junk.reshape( (self.m_ProcessingHeader.profilesPerBlock, self.m_ProcessingHeader.numHeights, self.m_SystemHeader.numChannels) )
        except:
            print "Data file %s is invalid" % self.filename
            return 0
        
        junk = numpy.transpose(junk, (2,0,1))
        self.datablock = junk['real'] + junk['imag']*1j
        
        self.datablockIndex = 0
        self.flagIsNewFile = 0
        self.idProfile = 0
        self.flagIsNewBlock = 1

        self.nReadBlocks += 1
        self.nBlocks += 1
          
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
            self.m_DataObj
            self.datablockIndex
            self.idProfile
            
        Affected:
            self.m_DataObj
            self.datablockIndex
            self.flagResetProcessing
            self.flagIsNewBlock
            self.idProfile
        """
        if self.flagNoMoreFiles: return 0
         
        self.flagResetProcessing = 0
        self.flagIsNewBlock = 0
        
        if self.__hasNotDataInBuffer():

            if not( self.readNextBlock() ):
                self.setNextFile()
                return 0
            
            self.m_DataObj.m_BasicHeader = self.m_BasicHeader.copy()
            self.m_DataObj.m_ProcessingHeader = self.m_ProcessingHeader.copy()
            self.m_DataObj.m_RadarControllerHeader = self.m_RadarControllerHeader.copy()
            self.m_DataObj.m_SystemHeader = self.m_SystemHeader.copy()
            self.m_DataObj.heights = self.heights
            self.m_DataObj.dataType = self.dataType
            
        if self.flagNoMoreFiles == 1:
            print 'Process finished'
            return 0
        
        #data es un numpy array de 3 dmensiones (perfiles, alturas y canales)
        
        if self.datablock == None:
            self.m_DataObj.flagNoData = True
            return 0

        time = self.m_BasicHeader.utc + self.datablockIndex * self.ippSeconds
        self.utc = time
        #self.m_DataObj.m_BasicHeader.utc = time  
        
        self.m_DataObj.flagNoData = False
        self.m_DataObj.flagResetProcessing = self.flagResetProcessing
        
        self.m_DataObj.data = self.datablock[:,self.datablockIndex,:]
        self.m_DataObj.idProfile = self.idProfile
        
        self.datablockIndex += 1
        self.idProfile += 1
        
        #call setData - to Data Object
    
        return 1 #self.m_DataObj.data


class VoltageWriter( JRODataWriter ):
    """ 
    Esta clase permite escribir datos de voltajes a archivos procesados (.r). La escritura
    de los datos siempre se realiza por bloques. 
    """
    __configHeaderFile = 'wrSetHeadet.txt'
    
    m_DataObj = None
    
    ext = ".r"
    
    optchar = "D"
    
    datablock = None
    
    datablockIndex = 0
    
    shapeBuffer = None
    

    def __init__(self, m_Voltage=None):
        """ 
        Inicializador de la clase VoltageWriter para la escritura de datos de espectros.
         
        Affected: 
            self.m_DataObj

        Return: None
        """
        if m_Voltage == None:
            m_Voltage = Voltage()    
        
        if not( isinstance(m_Voltage, Voltage) ):
            raise ValueError, "in VoltageReader, m_Spectra must be an Spectra class object"

        self.m_DataObj = m_Voltage


    def hasAllDataInBuffer(self):
        if self.datablockIndex >= self.m_ProcessingHeader.profilesPerBlock:
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
        self.shapeBuffer = (self.m_ProcessingHeader.profilesPerBlock,
                            self.m_ProcessingHeader.numHeights,
                            self.m_SystemHeader.numChannels )
            
        self.datablock = numpy.zeros(self.m_SystemHeader.numChannels,
                                     self.m_ProcessingHeader.profilesPerBlock,
                                     self.m_ProcessingHeader.numHeights,
                                     numpy.dtype('complex'))

        
    def writeBlock(self):
        """
        Escribe el buffer en el file designado
            
        Affected:
            self.datablockIndex 
            self.flagIsNewFile
            self.flagIsNewBlock
            self.nWriteBlocks
            self.blocksCounter    
            
        Return: None
        """
        data = numpy.zeros( self.shapeBuffer, self.dataType )
        
        junk = numpy.transpose(self.datablock, (1,2,0))
        
        data['real'] = junk.real
        data['imag'] = junk.imag
        
        data = data.reshape( (-1) )
            
        data.tofile( self.fp )
        
        self.datablock.fill(0)
        self.datablockIndex = 0 
        self.flagIsNewFile = 0
        self.flagIsNewBlock = 1
        self.nWriteBlocks += 1
        self.blocksCounter += 1
        
        
    def putData(self):
        """
        Setea un bloque de datos y luego los escribe en un file 
            
        Affected:
            self.flagIsNewBlock
            self.datablockIndex

        Return: 
            0    :    Si no hay data o no hay mas files que puedan escribirse 
            1    :    Si se escribio la data de un bloque en un file
        """
        self.flagIsNewBlock = 0
        
        if self.m_DataObj.flagNoData:
            return 0
        
        if self.m_DataObj.flagResetProcessing:
            
            self.datablock.fill(0)
            self.datablockIndex = 0
            self.setNextFile()
        
        self.datablock[:,self.datablockIndex,:] = self.m_DataObj.data
        
        self.datablockIndex += 1
        
        if self.hasAllDataInBuffer():
            #if self.flagIsNewFile: 
            self.getHeader()
            self.writeNextBlock()
        
        if self.flagNoMoreFiles:
            #print 'Process finished'
            return 0
        
        return 1
    