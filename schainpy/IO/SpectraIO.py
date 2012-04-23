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

from Model.JROHeader import *
from Model.Spectra import Spectra

from DataIO import JRODataReader
from DataIO import JRODataWriter
from DataIO import isNumber


class SpectraReader( JRODataReader ):
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
            
            print readerObj.m_Spectra.data
            
            if readerObj.flagNoMoreFiles:
                break
            
    """
    m_DataObj = None
    
    data_spc = None
    data_cspc = None
    data_dc = None

    pts2read_SelfSpectra = 0
    pts2read_CrossSpectra = 0
    pts2read_DCchannels = 0
    
    nChannels = 0
    
    nPairs = 0
    
    #pairList = None
    
    channelList = None
    
    def __init__(self, m_Spectra=None):
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
            self.m_DataObj

        Return      : None
        """
        if m_Spectra == None:
            m_Spectra = Spectra()
        
        if not( isinstance(m_Spectra, Spectra) ):
            raise ValueError, "in SpectraReader, m_Spectra must be an Spectra class object"

        self.m_DataObj = m_Spectra

        self.data_spc = None
        self.data_cspc = None
        self.data_dc = None
    
        self.pts2read_SelfSpectra = 0
        self.pts2read_CrossSpectra = 0
        self.pts2read_DCs = 0
        
        self.nChannels = 0
        
        self.nPairs = 0
        
        self.ext = ".pdata"
        
        self.optchar = "P"

        ######################

        self.m_BasicHeader = BasicHeader()
        
        self.m_SystemHeader = SystemHeader()
        
        self.m_RadarControllerHeader = RadarControllerHeader()
        
        self.m_ProcessingHeader = ProcessingHeader()
        
        self.online = 0
        
        self.fp = None
        
        self.fileSizeByHeader = None
        
        self.filenameList = []
        
        self.filename = None
        
        self.fileSize = None
        
        self.firstHeaderSize = 0
        
        self.basicHeaderSize = 24
        
        self.dataType = None
        
        self.maxTimeStep = 30
            
        self.flagNoMoreFiles = 0
        
        self.set = 0
        
        self.path = None
        
        self.delay  = 3  #seconds
        
        self.nTries = 3  #quantity tries
        
        self.nFiles = 3  #number of files for searching
        
        self.nBlocks = 0
        
        self.flagIsNewFile = 1
    
        self.ippSeconds = 0
    
        self.flagResetProcessing = 0    
    
        self.flagIsNewBlock = 0
        
        self.nReadBlocks = 0
    
        self.blocksize = 0

        #pairList = None

        channelList = None


    def __hasNotDataInBuffer(self):
        return 1


    def getBlockDimension(self):
        """
        Obtiene la cantidad de puntos a leer por cada bloque de datos
        
        Affected:
            self.nChannels
            self.nPairs
            self.pts2read_SelfSpectra
            self.pts2read_CrossSpectra
            self.pts2read_DCchannels
            self.blocksize
            self.m_DataObj.nChannels
            self.m_DataObj.nPairs

        Return:
            None
        """
        self.nChannels = 0
        self.nPairs = 0
        #self.pairList = []
        
        for i in range( 0, self.m_ProcessingHeader.totalSpectra*2, 2 ):
            if self.m_ProcessingHeader.spectraComb[i] == self.m_ProcessingHeader.spectraComb[i+1]:
                self.nChannels = self.nChannels + 1   #par de canales iguales 
            else:
                self.nPairs = self.nPairs + 1 #par de canales diferentes
                #self.pairList.append( (self.m_ProcessingHeader.spectraComb[i], self.m_ProcessingHeader.spectraComb[i+1]) )

        pts2read = self.m_ProcessingHeader.numHeights * self.m_ProcessingHeader.profilesPerBlock

        self.pts2read_SelfSpectra = int( self.nChannels * pts2read )
        self.pts2read_CrossSpectra = int( self.nPairs * pts2read )
        self.pts2read_DCchannels = int( self.m_SystemHeader.numChannels * self.m_ProcessingHeader.numHeights )
        
        self.blocksize = self.pts2read_SelfSpectra + self.pts2read_CrossSpectra + self.pts2read_DCchannels   
        
        self.m_DataObj.nPoints = self.m_ProcessingHeader.profilesPerBlock
        self.m_DataObj.nChannels = self.nChannels
        self.m_DataObj.nPairs = self.nPairs
        
        #self.pairList = tuple( self.pairList )
        self.channelList = numpy.arange( self.nChannels )

            
    def readBlock(self):
        """
        Lee el bloque de datos desde la posicion actual del puntero del archivo
        (self.fp) y actualiza todos los parametros relacionados al bloque de datos
        (metadata + data). La data leida es almacenada en el buffer y el contador del buffer
        es seteado a 0
        
        Return: None
        
        Variables afectadas:
            self.datablockIndex
            self.flagIsNewFile
            self.flagIsNewBlock
            self.nReadBlocks
            self.data_spc
            self.data_cspc
            self.data_dc

        Exceptions: 
            Si un bloque leido no es un bloque valido
        """
        blockOk_flag = False
        fpointer = self.fp.tell()

        spc = numpy.fromfile( self.fp, self.dataType[0], self.pts2read_SelfSpectra )
        cspc = numpy.fromfile( self.fp, self.dataType, self.pts2read_CrossSpectra )
        dc = numpy.fromfile( self.fp, self.dataType, self.pts2read_DCchannels ) #int(self.m_ProcessingHeader.numHeights*self.m_SystemHeader.numChannels) )

        if self.online:
            if (spc.size + cspc.size + dc.size) != self.blocksize:
                for nTries in range( self.nTries ):
                    print "\tWaiting %0.2f sec for the next block, try %03d ..." % (self.delay, nTries+1)
                    time.sleep( self.delay )
                    self.fp.seek( fpointer )
                    fpointer = self.fp.tell() 
                    
                    spc = numpy.fromfile( self.fp, self.dataType[0], self.pts2read_SelfSpectra )
                    cspc = numpy.fromfile( self.fp, self.dataType, self.pts2read_CrossSpectra )
                    dc = numpy.fromfile( self.fp, self.dataType, self.pts2read_DCchannels ) #int(self.m_ProcessingHeader.numHeights*self.m_SystemHeader.numChannels) )
                    
                    if (spc.size + cspc.size + dc.size) == self.blocksize:
                        blockOk_flag = True
                        break
                    
                if not( blockOk_flag ):
                    return 0
        
        try:
            spc = spc.reshape( (self.nChannels, self.m_ProcessingHeader.numHeights, self.m_ProcessingHeader.profilesPerBlock) ) #transforma a un arreglo 3D 
            if self.nPairs != 0:
                cspc = cspc.reshape( (self.nPairs, self.m_ProcessingHeader.numHeights, self.m_ProcessingHeader.profilesPerBlock) ) #transforma a un arreglo 3D
            else:
                cspc = None    
            dc = dc.reshape( (self.m_SystemHeader.numChannels, self.m_ProcessingHeader.numHeights) ) #transforma a un arreglo 2D
        except:
            print "Data file %s is invalid" % self.filename
            return 0
        
        if not( self.m_ProcessingHeader.shif_fft ):
            spc = numpy.roll( spc, self.m_ProcessingHeader.profilesPerBlock/2, axis=2 ) #desplaza a la derecha en el eje 2 determinadas posiciones
            if cspc != None:
                cspc = numpy.roll( cspc, self.m_ProcessingHeader.profilesPerBlock/2, axis=2 ) #desplaza a la derecha en el eje 2 determinadas posiciones
        
        spc = numpy.transpose( spc, (0,2,1) )
        if cspc != None: cspc = numpy.transpose( cspc, (0,2,1) )

        self.data_spc = spc
        if cspc != None: 
            self.data_cspc = cspc['real'] + cspc['imag']*1j
        else:
            self.data_cspc = None
        self.data_dc = dc['real'] + dc['imag']*1j

        self.datablockIndex = 0
        self.flagIsNewFile = 0
        self.flagIsNewBlock = 1

        self.nReadBlocks += 1
        self.nBlocks += 1

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
            self.m_DataObj
            self.datablockIndex
            self.flagResetProcessing
            self.flagIsNewBlock
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
            self.m_DataObj.heightList = self.heightList
            self.m_DataObj.dataType = self.dataType
        
        if self.flagNoMoreFiles == 1:
            print 'Process finished'
            return 0
        
        #data es un numpy array de 3 dmensiones (perfiles, alturas y canales)

        if self.data_dc == None:
            self.m_DataObj.flagNoData = True
            return 0

        self.m_DataObj.flagNoData = False
        self.m_DataObj.flagResetProcessing = self.flagResetProcessing
        
        self.m_DataObj.data_spc = self.data_spc
        self.m_DataObj.data_cspc = self.data_cspc
        self.m_DataObj.data_dc = self.data_dc

        return 1


class SpectraWriter(JRODataWriter):
    
    """ 
    Esta clase permite escribir datos de espectros a archivos procesados (.pdata). La escritura
    de los datos siempre se realiza por bloques. 
    """
    
    m_DataObj = None
    
    shape_spc_Buffer = None
    shape_cspc_Buffer = None
    shape_dc_Buffer = None
    
    data_spc = None
    data_cspc = None
    data_dc = None

    
    def __init__(self, m_Spectra=None):
        """ 
        Inicializador de la clase SpectraWriter para la escritura de datos de espectros.
         
        Affected: 
            self.m_DataObj
            self.m_BasicHeader
            self.m_SystemHeader
            self.m_RadarControllerHeader
            self.m_ProcessingHeader

        Return: None
        """
        if m_Spectra == None:
            m_Spectra = Spectra()    
        
        if not( isinstance(m_Spectra, Spectra) ):
            raise ValueError, "in SpectraReader, m_Spectra must be an Spectra class object"

        self.m_DataObj = m_Spectra

        self.ext = ".pdata"
        
        self.optchar = "P"
        
        self.shape_spc_Buffer = None
        self.shape_cspc_Buffer = None
        self.shape_dc_Buffer = None

        self.data_spc = None
        self.data_cspc = None
        self.data_dc = None

        ####################################

        self.fp = None
        
        self.blocksCounter = 0
        
        self.flagIsNewFile = 1
        
        self.nWriteBlocks = 0 
        
        self.flagIsNewBlock = 0
        
        self.flagNoMoreFiles = 0

        self.setFile = None
        
        self.dataType = None
        
        self.path = None
        
        self.noMoreFiles = 0
        
        self.filename = None
        
        self.m_BasicHeader= BasicHeader()
    
        self.m_SystemHeader = SystemHeader()
    
        self.m_RadarControllerHeader = RadarControllerHeader()
    
        self.m_ProcessingHeader = ProcessingHeader()

        
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
        self.shape_spc_Buffer = (self.m_DataObj.nChannels,
                                 self.m_ProcessingHeader.numHeights,
                                 self.m_ProcessingHeader.profilesPerBlock)

        self.shape_cspc_Buffer = (self.m_DataObj.nPairs,
                                  self.m_ProcessingHeader.numHeights,
                                  self.m_ProcessingHeader.profilesPerBlock)
        
        self.shape_dc_Buffer = (self.m_SystemHeader.numChannels,
                                self.m_ProcessingHeader.numHeights)

    
    def writeBlock(self):
        """
        Escribe el buffer en el file designado
            
        Affected:
            self.data_spc
            self.data_cspc
            self.data_dc
            self.flagIsNewFile
            self.flagIsNewBlock
            self.nWriteBlocks
            self.blocksCounter    
            
        Return: None
        """
        
        spc = numpy.transpose( self.data_spc, (0,2,1) )
        if not( self.m_ProcessingHeader.shif_fft ):
            spc = numpy.roll( spc, self.m_ProcessingHeader.profilesPerBlock/2, axis=2 ) #desplaza a la derecha en el eje 2 determinadas posiciones
        data = spc.reshape((-1))
        data.tofile(self.fp)

        if self.data_cspc != None:
            data = numpy.zeros( self.shape_cspc_Buffer, self.dataType )
            cspc = numpy.transpose( self.data_cspc, (0,2,1) )
            if not( self.m_ProcessingHeader.shif_fft ):
                cspc = numpy.roll( cspc, self.m_ProcessingHeader.profilesPerBlock/2, axis=2 ) #desplaza a la derecha en el eje 2 determinadas posiciones
            data['real'] = cspc.real
            data['imag'] = cspc.imag
            data = data.reshape((-1))
            data.tofile(self.fp)

        data = numpy.zeros( self.shape_dc_Buffer, self.dataType )
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
        self.nWriteBlocks += 1
        self.blocksCounter += 1
        
        
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
        self.flagIsNewBlock = 0
        
        if self.m_DataObj.flagNoData:
            return 0
        
        if self.m_DataObj.flagResetProcessing:
            self.data_spc.fill(0)
            self.data_cspc.fill(0)
            self.data_dc.fill(0)
            self.setNextFile()
        
        self.data_spc = self.m_DataObj.data_spc
        self.data_cspc = self.m_DataObj.data_cspc
        self.data_dc = self.m_DataObj.data_dc
        
        # #self.m_ProcessingHeader.dataBlocksPerFile)
        if self.hasAllDataInBuffer():
            self.getHeader()
            self.writeNextBlock()
        
        if self.flagNoMoreFiles:
            #print 'Process finished'
            return 0
        
        return 1