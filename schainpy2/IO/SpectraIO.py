'''

$Author$
$Id$
'''

import os, sys
import numpy
import glob
import fnmatch
import time, datetime

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from JROHeaderIO import *
from JRODataIO import JRODataReader
from JRODataIO import JRODataWriter

from Data.JROData import Spectra

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
    
    dataOutObj = None
    
    nRdChannels = None
    
    nRdPairs = None
    
    rdPairList = []

    
    def __init__(self, dataOutObj=None):
        """ 
        Inicializador de la clase SpectraReader para la lectura de datos de espectros.

        Inputs: 
            dataOutObj    :    Objeto de la clase Spectra. Este objeto sera utilizado para
                              almacenar un perfil de datos cada vez que se haga un requerimiento
                              (getData). El perfil sera obtenido a partir del buffer de datos,
                              si el buffer esta vacio se hara un nuevo proceso de lectura de un
                              bloque de datos.
                              Si este parametro no es pasado se creara uno internamente.
         
        Affected: 
            self.dataOutObj

        Return      : None
        """

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
            self.dataOutObj.nChannels
            self.dataOutObj.nPairs

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
            spc = numpy.roll( spc, self.processingHeaderObj.profilesPerBlock/2, axis=2 ) #desplaza a la derecha en el eje 2 determinadas posiciones
            
            if self.processingHeaderObj.flag_cspc:
                cspc = numpy.roll( cspc, self.processingHeaderObj.profilesPerBlock/2, axis=2 ) #desplaza a la derecha en el eje 2 determinadas posiciones
        

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
            self.dataOutObj
            
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

        if self.data_dc == None:
            self.dataOutObj.flagNoData = True
            return 0


        self.dataOutObj.data_spc = self.data_spc
        
        self.dataOutObj.data_cspc = self.data_cspc
        
        self.dataOutObj.data_dc = self.data_dc
                
        self.dataOutObj.flagTimeBlock = self.flagTimeBlock
    
        self.dataOutObj.flagNoData = False

        self.dataOutObj.dtype = self.dtype

        self.dataOutObj.nChannels = self.nRdChannels
        
        self.dataOutObj.nPairs = self.nRdPairs
        
        self.dataOutObj.pairsList = self.rdPairList
        
        self.dataOutObj.nHeights = self.processingHeaderObj.nHeights
        
        self.dataOutObj.nProfiles = self.processingHeaderObj.profilesPerBlock
        
        self.dataOutObj.nFFTPoints = self.processingHeaderObj.profilesPerBlock
        
        self.dataOutObj.nIncohInt = self.processingHeaderObj.nIncohInt
        
        
        xf = self.processingHeaderObj.firstHeight + self.processingHeaderObj.nHeights*self.processingHeaderObj.deltaHeight

        self.dataOutObj.heightList = numpy.arange(self.processingHeaderObj.firstHeight, xf, self.processingHeaderObj.deltaHeight) 
        
        self.dataOutObj.channelList = range(self.systemHeaderObj.nChannels)
        
        self.dataOutObj.channelIndexList = range(self.systemHeaderObj.nChannels)
        
        self.dataOutObj.utctime = self.basicHeaderObj.utc + self.basicHeaderObj.miliSecond/1000.#+ self.profileIndex * self.ippSeconds
        
        self.dataOutObj.ippSeconds = self.ippSeconds
        
        self.dataOutObj.timeInterval = self.ippSeconds * self.processingHeaderObj.nCohInt * self.processingHeaderObj.nIncohInt * self.dataOutObj.nFFTPoints
        
        self.dataOutObj.flagShiftFFT = self.processingHeaderObj.shif_fft
        
#        self.profileIndex += 1
        
        self.dataOutObj.systemHeaderObj = self.systemHeaderObj.copy()
        
        self.dataOutObj.radarControllerHeaderObj = self.radarControllerHeaderObj.copy()

        return self.dataOutObj.data_spc


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
        
    wrPairList = []
    
    nWrPairs = 0
    
    nWrChannels = 0
    
#    dataOutObj = None
    
    def __init__(self, dataOutObj=None):
        """ 
        Inicializador de la clase SpectraWriter para la escritura de datos de espectros.
         
        Affected: 
            self.dataOutObj
            self.basicHeaderObj
            self.systemHeaderObj
            self.radarControllerHeaderObj
            self.processingHeaderObj

        Return: None
        """
        if dataOutObj == None:
            dataOutObj = Spectra()    
        
        if not( isinstance(dataOutObj, Spectra) ):
            raise ValueError, "in SpectraReader, dataOutObj must be an Spectra class object"

        self.dataOutObj = dataOutObj
        
        self.nTotalBlocks = 0
        
        self.nWrChannels = self.dataOutObj.nChannels
        
#        if len(pairList) > 0:
#            self.wrPairList = pairList
#            
#            self.nWrPairs = len(pairList)
        
        self.wrPairList = self.dataOutObj.pairsList
        
        self.nWrPairs = self.dataOutObj.nPairs
        
        
        
        

#        self.data_spc = None
#        self.data_cspc = None
#        self.data_dc = None

#        self.fp = None

#        self.flagIsNewFile = 1
#        
#        self.nTotalBlocks = 0 
#        
#        self.flagIsNewBlock = 0
#        
#        self.flagNoMoreFiles = 0
#
#        self.setFile = None
#        
#        self.dtype = None
#        
#        self.path = None
#        
#        self.noMoreFiles = 0
#        
#        self.filename = None
#        
#        self.basicHeaderObj = BasicHeader()
#    
#        self.systemHeaderObj = SystemHeader()
#    
#        self.radarControllerHeaderObj = RadarControllerHeader()
#    
#        self.processingHeaderObj = ProcessingHeader()

        
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
        self.shape_spc_Buffer = (self.dataOutObj.nChannels,
                                 self.processingHeaderObj.nHeights,
                                 self.processingHeaderObj.profilesPerBlock)

        self.shape_cspc_Buffer = (self.dataOutObj.nPairs,
                                  self.processingHeaderObj.nHeights,
                                  self.processingHeaderObj.profilesPerBlock)
        
        self.shape_dc_Buffer = (self.dataOutObj.nChannels,
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
        self.flagIsNewBlock = 0
        
        if self.dataOutObj.flagNoData:
            return 0
        
        if self.dataOutObj.flagTimeBlock:
            self.data_spc.fill(0)
            self.data_cspc.fill(0)
            self.data_dc.fill(0)
            self.setNextFile()
        
        if self.flagIsNewFile == 0:
            self.getBasicHeader()
        
        self.data_spc = self.dataOutObj.data_spc
        self.data_cspc = self.dataOutObj.data_cspc
        self.data_dc = self.dataOutObj.data_dc
        
        # #self.processingHeaderObj.dataBlocksPerFile)
        if self.hasAllDataInBuffer():
#            self.getDataHeader()
            self.writeNextBlock()
        
        if self.flagNoMoreFiles:
            #print 'Process finished'
            return 0
        
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
            if self.dataOutObj.dtype == dtypeList[index]:
                dtypeValue = datatypeValueList[index]
                break
        
        processFlags += dtypeValue
        
        if self.dataOutObj.flagDecodeData:
            processFlags += PROCFLAG.DECODE_DATA
        
        if self.dataOutObj.flagDeflipData:
            processFlags += PROCFLAG.DEFLIP_DATA
        
        if self.dataOutObj.code != None:
            processFlags += PROCFLAG.DEFINE_PROCESS_CODE
        
        if self.dataOutObj.nIncohInt > 1:
            processFlags += PROCFLAG.INCOHERENT_INTEGRATION
            
        if self.dataOutObj.data_dc != None:
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
            if self.dataOutObj.dtype == dtypeList[index]:
                datatypeValue = datatypeValueList[index]
                break
        
        
        pts2write = self.dataOutObj.nHeights * self.dataOutObj.nFFTPoints
        
        pts2write_SelfSpectra = int(self.nWrChannels * pts2write)
        blocksize = (pts2write_SelfSpectra*datatypeValue)
        
        if self.dataOutObj.data_cspc != None:
            pts2write_CrossSpectra = int(self.nWrPairs * pts2write)
            blocksize += (pts2write_CrossSpectra*datatypeValue*2)
        
        if self.dataOutObj.data_dc != None:
            pts2write_DCchannels = int(self.nWrChannels * self.dataOutObj.nHeights)
            blocksize += (pts2write_DCchannels*datatypeValue*2)
        
        blocksize = blocksize #* datatypeValue * 2 #CORREGIR ESTO

        return blocksize
    
    
    def getBasicHeader(self):
        self.basicHeaderObj.size = self.basicHeaderSize #bytes
        self.basicHeaderObj.version = self.versionFile
        self.basicHeaderObj.dataBlock = self.nTotalBlocks
        
        utc = numpy.floor(self.dataOutObj.utctime)
        milisecond  = (self.dataOutObj.utctime - utc)* 1000.0
        
        self.basicHeaderObj.utc = utc
        self.basicHeaderObj.miliSecond = milisecond
        self.basicHeaderObj.timeZone = 0
        self.basicHeaderObj.dstFlag = 0
        self.basicHeaderObj.errorCount = 0
    
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
        
        self.systemHeaderObj = self.dataOutObj.systemHeaderObj.copy()
        self.systemHeaderObj.nChannels = self.dataOutObj.nChannels
        self.radarControllerHeaderObj = self.dataOutObj.radarControllerHeaderObj.copy()
        
        self.getBasicHeader()
        
        processingHeaderSize = 40 # bytes    
        self.processingHeaderObj.dtype = 0 # Voltage
        self.processingHeaderObj.blockSize = self.__getBlockSize()
        self.processingHeaderObj.profilesPerBlock = self.dataOutObj.nFFTPoints
        self.processingHeaderObj.dataBlocksPerFile = self.blocksPerFile
        self.processingHeaderObj.nWindows = 1 #podria ser 1 o self.dataOutObj.processingHeaderObj.nWindows
        self.processingHeaderObj.processFlags = self.__getProcessFlags()
        self.processingHeaderObj.nCohInt = self.dataOutObj.nCohInt# Se requiere para determinar el valor de timeInterval
        self.processingHeaderObj.nIncohInt = self.dataOutObj.nIncohInt 
        self.processingHeaderObj.totalSpectra = self.dataOutObj.nPairs + self.dataOutObj.nChannels
        
        if self.processingHeaderObj.totalSpectra > 0:
            channelList = []
            for channel in range(self.dataOutObj.nChannels):
                channelList.append(channel)
                channelList.append(channel)
                
            pairsList = []
            for pair in self.dataOutObj.pairsList:
                pairsList.append(pair[0])
                pairsList.append(pair[1])
            spectraComb = channelList + pairsList
            spectraComb = numpy.array(spectraComb,dtype="u1")
            self.processingHeaderObj.spectraComb = spectraComb
            sizeOfSpcComb = len(spectraComb)
            processingHeaderSize += sizeOfSpcComb
        
        if self.dataOutObj.code != None:
            self.processingHeaderObj.code = self.dataOutObj.code
            self.processingHeaderObj.nCode = self.dataOutObj.nCode
            self.processingHeaderObj.nBaud = self.dataOutObj.nBaud
            nCodeSize = 4 # bytes
            nBaudSize = 4 # bytes
            codeSize = 4 # bytes
            sizeOfCode = int(nCodeSize + nBaudSize + codeSize * self.dataOutObj.nCode * self.dataOutObj.nBaud)
            processingHeaderSize += sizeOfCode
        
        if self.processingHeaderObj.nWindows != 0:
            self.processingHeaderObj.firstHeight = self.dataOutObj.heightList[0]
            self.processingHeaderObj.deltaHeight = self.dataOutObj.heightList[1] - self.dataOutObj.heightList[0]
            self.processingHeaderObj.nHeights = self.dataOutObj.nHeights
            self.processingHeaderObj.samplesWin = self.dataOutObj.nHeights
            sizeOfFirstHeight = 4
            sizeOfdeltaHeight = 4
            sizeOfnHeights = 4
            sizeOfWindows = (sizeOfFirstHeight + sizeOfdeltaHeight + sizeOfnHeights)*self.processingHeaderObj.nWindows
            processingHeaderSize += sizeOfWindows
            
        self.processingHeaderObj.size = processingHeaderSize    
            
    