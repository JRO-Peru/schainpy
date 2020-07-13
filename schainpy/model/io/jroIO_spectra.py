'''
Created on Jul 2, 2014

@author: roj-idl71
'''
import numpy

from schainpy.model.io.jroIO_base import LOCALTIME, JRODataReader, JRODataWriter
from schainpy.model.proc.jroproc_base import ProcessingUnit, Operation, MPDecorator
from schainpy.model.data.jroheaderIO import PROCFLAG, BasicHeader, SystemHeader, RadarControllerHeader, ProcessingHeader
from schainpy.model.data.jrodata import Spectra
from schainpy.utils import log


class SpectraReader(JRODataReader, ProcessingUnit):
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

    def __init__(self):#, **kwargs):
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

        ProcessingUnit.__init__(self)

        self.pts2read_SelfSpectra = 0
        self.pts2read_CrossSpectra = 0
        self.pts2read_DCchannels = 0        
        self.ext = ".pdata"
        self.optchar = "P"
        self.basicHeaderObj = BasicHeader(LOCALTIME)
        self.systemHeaderObj = SystemHeader()
        self.radarControllerHeaderObj = RadarControllerHeader()
        self.processingHeaderObj = ProcessingHeader()
        self.lastUTTime = 0
        self.maxTimeStep = 30
        self.dataOut = Spectra()
        self.profileIndex = 1
        self.nRdChannels = None
        self.nRdPairs = None
        self.rdPairList = []

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
        
        fpointer = self.fp.tell()

        spc = numpy.fromfile( self.fp, self.dtype[0], self.pts2read_SelfSpectra )
        spc = spc.reshape( (self.nRdChannels, self.processingHeaderObj.nHeights, self.processingHeaderObj.profilesPerBlock) ) #transforma a un arreglo 3D

        if self.processingHeaderObj.flag_cspc:
            cspc = numpy.fromfile( self.fp, self.dtype, self.pts2read_CrossSpectra )
            cspc = cspc.reshape( (self.nRdPairs, self.processingHeaderObj.nHeights, self.processingHeaderObj.profilesPerBlock) ) #transforma a un arreglo 3D

        if self.processingHeaderObj.flag_dc:
            dc = numpy.fromfile( self.fp, self.dtype, self.pts2read_DCchannels ) #int(self.processingHeaderObj.nHeights*self.systemHeaderObj.nChannels) )
            dc = dc.reshape( (self.systemHeaderObj.nChannels, self.processingHeaderObj.nHeights) ) #transforma a un arreglo 2D

        if not self.processingHeaderObj.shif_fft:
            #desplaza a la derecha en el eje 2 determinadas posiciones
            shift = int(self.processingHeaderObj.profilesPerBlock/2)
            spc = numpy.roll( spc, shift , axis=2 )

            if self.processingHeaderObj.flag_cspc:
                #desplaza a la derecha en el eje 2 determinadas posiciones
                cspc = numpy.roll( cspc, shift, axis=2 )

        #Dimensions : nChannels, nProfiles, nSamples
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

    def getFirstHeader(self):

        self.getBasicHeader()
        self.dataOut.systemHeaderObj = self.systemHeaderObj.copy()
        self.dataOut.radarControllerHeaderObj = self.radarControllerHeaderObj.copy()
        self.dataOut.dtype = self.dtype
        self.dataOut.pairsList = self.rdPairList
        self.dataOut.nProfiles = self.processingHeaderObj.profilesPerBlock
        self.dataOut.nFFTPoints = self.processingHeaderObj.profilesPerBlock
        self.dataOut.nCohInt = self.processingHeaderObj.nCohInt
        self.dataOut.nIncohInt = self.processingHeaderObj.nIncohInt
        xf = self.processingHeaderObj.firstHeight + self.processingHeaderObj.nHeights*self.processingHeaderObj.deltaHeight
        self.dataOut.heightList = numpy.arange(self.processingHeaderObj.firstHeight, xf, self.processingHeaderObj.deltaHeight)
        self.dataOut.channelList = list(range(self.systemHeaderObj.nChannels))
        self.dataOut.flagShiftFFT = True    #Data is always shifted
        self.dataOut.flagDecodeData = self.processingHeaderObj.flag_decode #asumo q la data no esta decodificada
        self.dataOut.flagDeflipData = self.processingHeaderObj.flag_deflip #asumo q la data esta sin flip

    def getData(self):
        """
        First method to execute before "RUN" is called.

        Copia el buffer de lectura a la clase "Spectra",
        con todos los parametros asociados a este (metadata). cuando no hay datos en el buffer de
        lectura es necesario hacer una nueva lectura de los bloques de datos usando "readNextBlock"

        Return:
            0    :    Si no hay mas archivos disponibles
            1    :    Si hizo una buena copia del buffer

        Affected:
            self.dataOut
            self.flagDiscontinuousBlock
            self.flagIsNewBlock
        """

        if self.flagNoMoreFiles:
            self.dataOut.flagNoData = True
            return 0

        self.flagDiscontinuousBlock = 0
        self.flagIsNewBlock = 0

        if self.__hasNotDataInBuffer():

            if not( self.readNextBlock() ):
                self.dataOut.flagNoData = True
                return 0

        #data es un numpy array de 3 dmensiones (perfiles, alturas y canales)

        if self.data_spc is None:
            self.dataOut.flagNoData = True
            return 0

        self.getBasicHeader()
        self.getFirstHeader()
        self.dataOut.data_spc = self.data_spc
        self.dataOut.data_cspc = self.data_cspc
        self.dataOut.data_dc = self.data_dc
        self.dataOut.flagNoData = False
        self.dataOut.realtime = self.online

        return self.dataOut.data_spc


@MPDecorator
class SpectraWriter(JRODataWriter, Operation):

    """
    Esta clase permite escribir datos de espectros a archivos procesados (.pdata). La escritura
    de los datos siempre se realiza por bloques.
    """

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

        Operation.__init__(self)

        self.ext = ".pdata"
        self.optchar = "P"
        self.shape_spc_Buffer = None
        self.shape_cspc_Buffer = None
        self.shape_dc_Buffer = None
        self.data_spc = None
        self.data_cspc = None
        self.data_dc = None
        self.setFile = None
        self.noMoreFiles = 0
        self.basicHeaderObj = BasicHeader(LOCALTIME)
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
        """processingHeaderObj
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
        if not self.processingHeaderObj.shif_fft:
            spc = numpy.roll( spc, int(self.processingHeaderObj.profilesPerBlock/2), axis=2 ) #desplaza a la derecha en el eje 2 determinadas posiciones
        data = spc.reshape((-1))
        data = data.astype(self.dtype[0])
        data.tofile(self.fp)

        if self.data_cspc is not None:
            
            cspc = numpy.transpose( self.data_cspc, (0,2,1) )
            data = numpy.zeros( numpy.shape(cspc), self.dtype )
            #print 'data.shape', self.shape_cspc_Buffer
            if not self.processingHeaderObj.shif_fft:
                cspc = numpy.roll( cspc, int(self.processingHeaderObj.profilesPerBlock/2), axis=2 ) #desplaza a la derecha en el eje 2 determinadas posiciones
            data['real'] = cspc.real
            data['imag'] = cspc.imag
            data = data.reshape((-1))
            data.tofile(self.fp)

        if self.data_dc is not None:
            
            dc = self.data_dc
            data = numpy.zeros( numpy.shape(dc), self.dtype )
            data['real'] = dc.real
            data['imag'] = dc.imag
            data = data.reshape((-1))
            data.tofile(self.fp)

#         self.data_spc.fill(0)
#
#         if self.data_dc is not None:
#             self.data_dc.fill(0)
#
#         if self.data_cspc is not None:
#             self.data_cspc.fill(0)

        self.flagIsNewFile = 0
        self.flagIsNewBlock = 1
        self.nTotalBlocks += 1
        self.nWriteBlocks += 1
        self.blockIndex += 1

#         print "[Writing] Block = %d04" %self.blockIndex

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

        if self.dataOut.flagDiscontinuousBlock:
            self.data_spc.fill(0)
            if self.dataOut.data_cspc is not None:
                self.data_cspc.fill(0)
            if self.dataOut.data_dc is not None:
                self.data_dc.fill(0)
            self.setNextFile()

        if self.flagIsNewFile == 0:
            self.setBasicHeader()

        self.data_spc = self.dataOut.data_spc.copy()

        if self.dataOut.data_cspc is not None:
            self.data_cspc = self.dataOut.data_cspc.copy()

        if self.dataOut.data_dc is not None:
            self.data_dc = self.dataOut.data_dc.copy()

        # #self.processingHeaderObj.dataBlocksPerFile)
        if self.hasAllDataInBuffer():
#            self.setFirstHeader()
            self.writeNextBlock()

    def __getBlockSize(self):
        '''
        Este metodos determina el cantidad de bytes para un bloque de datos de tipo Spectra
        '''

        dtype_width = self.getDtypeWidth()

        pts2write = self.dataOut.nHeights * self.dataOut.nFFTPoints

        pts2write_SelfSpectra = int(self.dataOut.nChannels * pts2write)
        blocksize = (pts2write_SelfSpectra*dtype_width)

        if self.dataOut.data_cspc is not None:
            pts2write_CrossSpectra = int(self.dataOut.nPairs * pts2write)
            blocksize += (pts2write_CrossSpectra*dtype_width*2)

        if self.dataOut.data_dc is not None:
            pts2write_DCchannels = int(self.dataOut.nChannels * self.dataOut.nHeights)
            blocksize += (pts2write_DCchannels*dtype_width*2)

#         blocksize = blocksize #* datatypeValue * 2 #CORREGIR ESTO

        return blocksize

    def setFirstHeader(self):

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

        self.processingHeaderObj.dtype = 1 # Spectra
        self.processingHeaderObj.blockSize = self.__getBlockSize()
        self.processingHeaderObj.profilesPerBlock = self.dataOut.nFFTPoints
        self.processingHeaderObj.dataBlocksPerFile = self.blocksPerFile
        self.processingHeaderObj.nWindows = 1 #podria ser 1 o self.dataOut.processingHeaderObj.nWindows
        self.processingHeaderObj.nCohInt = self.dataOut.nCohInt# Se requiere para determinar el valor de timeInterval
        self.processingHeaderObj.nIncohInt = self.dataOut.nIncohInt
        self.processingHeaderObj.totalSpectra = self.dataOut.nPairs + self.dataOut.nChannels
        self.processingHeaderObj.shif_fft = self.dataOut.flagShiftFFT

        if self.processingHeaderObj.totalSpectra > 0:
            channelList = []
            for channel in range(self.dataOut.nChannels):
                channelList.append(channel)
                channelList.append(channel)

            pairsList = []
            if self.dataOut.nPairs > 0:
                for pair in self.dataOut.pairsList:
                    pairsList.append(pair[0])
                    pairsList.append(pair[1])

            spectraComb = channelList + pairsList
            spectraComb = numpy.array(spectraComb, dtype="u1")
            self.processingHeaderObj.spectraComb = spectraComb

        if self.dataOut.code is not None:
            self.processingHeaderObj.code = self.dataOut.code
            self.processingHeaderObj.nCode = self.dataOut.nCode
            self.processingHeaderObj.nBaud = self.dataOut.nBaud

        if self.processingHeaderObj.nWindows != 0:
            self.processingHeaderObj.firstHeight = self.dataOut.heightList[0]
            self.processingHeaderObj.deltaHeight = self.dataOut.heightList[1] - self.dataOut.heightList[0]
            self.processingHeaderObj.nHeights = self.dataOut.nHeights
            self.processingHeaderObj.samplesWin = self.dataOut.nHeights

        self.processingHeaderObj.processFlags = self.getProcessFlags()

        self.setBasicHeader()