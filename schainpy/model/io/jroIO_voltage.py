'''
Created on Jul 2, 2014

@author: roj-idl71
'''

import numpy

from .jroIO_base import LOCALTIME, JRODataReader, JRODataWriter
from schainpy.model.proc.jroproc_base import ProcessingUnit, Operation, MPDecorator
from schainpy.model.data.jroheaderIO import PROCFLAG, BasicHeader, SystemHeader, RadarControllerHeader, ProcessingHeader
from schainpy.model.data.jrodata import Voltage


class VoltageReader(JRODataReader, ProcessingUnit):
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

        ProcessingUnit.__init__(self)
        
        self.ext = ".r"
        self.optchar = "D"
        self.basicHeaderObj = BasicHeader(LOCALTIME)
        self.systemHeaderObj = SystemHeader()
        self.radarControllerHeaderObj = RadarControllerHeader()
        self.processingHeaderObj = ProcessingHeader()
        self.lastUTTime = 0
        self.profileIndex = 2**32 - 1        
        self.dataOut = Voltage()
        self.selBlocksize = None
        self.selBlocktime = None

    def createObjByDefault(self):

        dataObj = Voltage()

        return dataObj

    def __hasNotDataInBuffer(self):

        if self.profileIndex >= self.processingHeaderObj.profilesPerBlock * self.nTxs:
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
        pts2read = self.processingHeaderObj.profilesPerBlock * \
            self.processingHeaderObj.nHeights * self.systemHeaderObj.nChannels
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

        # if self.server is not None:
        #     self.zBlock = self.receiver.recv()
        #     self.zHeader = self.zBlock[:24]
        #     self.zDataBlock = self.zBlock[24:]
        #     junk = numpy.fromstring(self.zDataBlock, numpy.dtype([('real','<i4'),('imag','<i4')]))
        #     self.processingHeaderObj.profilesPerBlock = 240
        #     self.processingHeaderObj.nHeights = 248
        #     self.systemHeaderObj.nChannels
        # else:
        current_pointer_location = self.fp.tell()
        junk = numpy.fromfile(self.fp, self.dtype, self.blocksize)

        try:
            junk = junk.reshape((self.processingHeaderObj.profilesPerBlock,
                                 self.processingHeaderObj.nHeights, self.systemHeaderObj.nChannels))
        except:
            # print "The read block (%3d) has not enough data" %self.nReadBlocks

            if self.waitDataBlock(pointer_location=current_pointer_location):
                junk = numpy.fromfile(self.fp, self.dtype, self.blocksize)
                junk = junk.reshape((self.processingHeaderObj.profilesPerBlock,
                                     self.processingHeaderObj.nHeights, self.systemHeaderObj.nChannels))
        #             return 0

        # Dimensions : nChannels, nProfiles, nSamples

        junk = numpy.transpose(junk, (2, 0, 1))
        self.datablock = junk['real'] + junk['imag'] * 1j

        self.profileIndex = 0

        self.flagIsNewFile = 0
        self.flagIsNewBlock = 1

        self.nTotalBlocks += 1
        self.nReadBlocks += 1

        return 1

    def getFirstHeader(self):

        self.getBasicHeader()

        self.dataOut.processingHeaderObj = self.processingHeaderObj.copy()

        self.dataOut.systemHeaderObj = self.systemHeaderObj.copy()

        self.dataOut.radarControllerHeaderObj = self.radarControllerHeaderObj.copy()

        if self.nTxs > 1:
            self.dataOut.radarControllerHeaderObj.ippSeconds = self.radarControllerHeaderObj.ippSeconds / self.nTxs
        # Time interval and code are propierties of dataOut. Its value depends of radarControllerHeaderObj.

        #         self.dataOut.timeInterval = self.radarControllerHeaderObj.ippSeconds * self.processingHeaderObj.nCohInt
        #
        #         if self.radarControllerHeaderObj.code is not None:
        #
        #             self.dataOut.nCode = self.radarControllerHeaderObj.nCode
        #
        #             self.dataOut.nBaud = self.radarControllerHeaderObj.nBaud
        #
        #             self.dataOut.code = self.radarControllerHeaderObj.code

        self.dataOut.dtype = self.dtype

        self.dataOut.nProfiles = self.processingHeaderObj.profilesPerBlock

        self.dataOut.heightList = numpy.arange(
            self.processingHeaderObj.nHeights) * self.processingHeaderObj.deltaHeight + self.processingHeaderObj.firstHeight

        self.dataOut.channelList = list(range(self.systemHeaderObj.nChannels))

        self.dataOut.nCohInt = self.processingHeaderObj.nCohInt

        # asumo q la data no esta decodificada
        self.dataOut.flagDecodeData = self.processingHeaderObj.flag_decode

        # asumo q la data no esta sin flip
        self.dataOut.flagDeflipData = self.processingHeaderObj.flag_deflip

        self.dataOut.flagShiftFFT = self.processingHeaderObj.shif_fft

    def reshapeData(self):

        if self.nTxs < 0:
            return

        if self.nTxs == 1:
            return

        if self.nTxs < 1 and self.processingHeaderObj.profilesPerBlock % (1. / self.nTxs) != 0:
            raise ValueError("1./nTxs (=%f), should be a multiple of nProfiles (=%d)" % (
                1. / self.nTxs, self.processingHeaderObj.profilesPerBlock))

        if self.nTxs > 1 and self.processingHeaderObj.nHeights % self.nTxs != 0:
            raise ValueError("nTxs (=%d), should be a multiple of nHeights (=%d)" % (
                self.nTxs, self.processingHeaderObj.nHeights))

        self.datablock = self.datablock.reshape(
            (self.systemHeaderObj.nChannels, self.processingHeaderObj.profilesPerBlock * self.nTxs, int(self.processingHeaderObj.nHeights / self.nTxs)))

        self.dataOut.nProfiles = self.processingHeaderObj.profilesPerBlock * self.nTxs
        self.dataOut.heightList = numpy.arange(self.processingHeaderObj.nHeights / self.nTxs) * \
            self.processingHeaderObj.deltaHeight + self.processingHeaderObj.firstHeight
        self.dataOut.radarControllerHeaderObj.ippSeconds = self.radarControllerHeaderObj.ippSeconds / self.nTxs

        return

    def readFirstHeaderFromServer(self):

        self.getFirstHeader()

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

    def getFromServer(self):
        self.flagDiscontinuousBlock = 0
        self.profileIndex = 0
        self.flagIsNewBlock = 1
        self.dataOut.flagNoData = False
        self.nTotalBlocks += 1
        self.nReadBlocks += 1
        self.blockPointer = 0

        block = self.receiver.recv()

        self.basicHeaderObj.read(block[self.blockPointer:])
        self.blockPointer += self.basicHeaderObj.length
        self.systemHeaderObj.read(block[self.blockPointer:])
        self.blockPointer += self.systemHeaderObj.length
        self.radarControllerHeaderObj.read(block[self.blockPointer:])
        self.blockPointer += self.radarControllerHeaderObj.length
        self.processingHeaderObj.read(block[self.blockPointer:])
        self.blockPointer += self.processingHeaderObj.length
        self.readFirstHeaderFromServer()

        timestamp = self.basicHeaderObj.get_datatime()
        print('[Reading] - Block {} - {}'.format(self.nTotalBlocks, timestamp))
        current_pointer_location = self.blockPointer
        junk = numpy.fromstring(
            block[self.blockPointer:], self.dtype, self.blocksize)

        try:
            junk = junk.reshape((self.processingHeaderObj.profilesPerBlock,
                                 self.processingHeaderObj.nHeights, self.systemHeaderObj.nChannels))
        except:
            # print "The read block (%3d) has not enough data" %self.nReadBlocks
            if self.waitDataBlock(pointer_location=current_pointer_location):
                junk = numpy.fromstring(
                    block[self.blockPointer:], self.dtype, self.blocksize)
                junk = junk.reshape((self.processingHeaderObj.profilesPerBlock,
                                     self.processingHeaderObj.nHeights, self.systemHeaderObj.nChannels))
        #               return 0

        # Dimensions : nChannels, nProfiles, nSamples

        junk = numpy.transpose(junk, (2, 0, 1))
        self.datablock = junk['real'] + junk['imag'] * 1j
        self.profileIndex = 0
        if self.selBlocksize == None:
            self.selBlocksize = self.dataOut.nProfiles
        if self.selBlocktime != None:
            if self.dataOut.nCohInt is not None:
                nCohInt = self.dataOut.nCohInt
            else:
                nCohInt = 1
            self.selBlocksize = int(self.dataOut.nProfiles * round(self.selBlocktime / (
                nCohInt * self.dataOut.ippSeconds * self.dataOut.nProfiles)))
        self.dataOut.data = self.datablock[:,
                                           self.profileIndex:self.profileIndex + self.selBlocksize, :]
        datasize = self.dataOut.data.shape[1]
        if datasize < self.selBlocksize:
            buffer = numpy.zeros(
                (self.dataOut.data.shape[0], self.selBlocksize, self.dataOut.data.shape[2]), dtype='complex')
            buffer[:, :datasize, :] = self.dataOut.data
            self.dataOut.data = buffer
            self.profileIndex = blockIndex

        self.dataOut.flagDataAsBlock = True
        self.flagIsNewBlock = 1
        self.dataOut.realtime = self.online

        return self.dataOut.data

    def getData(self):
        """
            getData obtiene una unidad de datos del buffer de lectura, un perfil,  y la copia al objeto self.dataOut
            del tipo "Voltage" con todos los parametros asociados a este (metadata). cuando no hay datos
            en el buffer de lectura es necesario hacer una nueva lectura de los bloques de datos usando
            "readNextBlock"

            Ademas incrementa el contador del buffer "self.profileIndex" en 1.

            Return:

                Si el flag self.getByBlock ha sido seteado el bloque completo es copiado a self.dataOut y el self.profileIndex
                es igual al total de perfiles leidos desde el archivo.

                Si self.getByBlock == False:

                    self.dataOut.data = buffer[:, thisProfile, :]

                    shape = [nChannels, nHeis]

                Si self.getByBlock == True:

                    self.dataOut.data = buffer[:, :, :]

                    shape = [nChannels, nProfiles, nHeis]

            Variables afectadas:
                self.dataOut
                self.profileIndex

            Affected:
                self.dataOut
                self.profileIndex
                self.flagDiscontinuousBlock
                self.flagIsNewBlock
        """
        if self.flagNoMoreFiles:
            self.dataOut.flagNoData = True
            return 0
        self.flagDiscontinuousBlock = 0
        self.flagIsNewBlock = 0
        if self.__hasNotDataInBuffer():
            if not(self.readNextBlock()):
                return 0

            self.getFirstHeader()

            self.reshapeData()
        if self.datablock is None:
            self.dataOut.flagNoData = True
            return 0

        if not self.getByBlock:

            """
                Return profile by profile

                If nTxs > 1 then one profile is divided by nTxs and number of total
                blocks is increased by nTxs (nProfiles *= nTxs)
            """
            self.dataOut.flagDataAsBlock = False
            self.dataOut.data = self.datablock[:, self.profileIndex, :]
            self.dataOut.profileIndex = self.profileIndex

            self.profileIndex += 1

        else:
            """
                Return a block
            """
            if self.selBlocksize == None:
                self.selBlocksize = self.dataOut.nProfiles
            if self.selBlocktime != None:
                if self.dataOut.nCohInt is not None:
                    nCohInt = self.dataOut.nCohInt
                else:
                    nCohInt = 1
                self.selBlocksize = int(self.dataOut.nProfiles * round(self.selBlocktime / (
                    nCohInt * self.dataOut.ippSeconds * self.dataOut.nProfiles)))

            self.dataOut.data = self.datablock[:,
                                               self.profileIndex:self.profileIndex + self.selBlocksize, :]
            self.profileIndex += self.selBlocksize
            datasize = self.dataOut.data.shape[1]

            if datasize < self.selBlocksize:
                buffer = numpy.zeros(
                    (self.dataOut.data.shape[0], self.selBlocksize, self.dataOut.data.shape[2]), dtype='complex')
                buffer[:, :datasize, :] = self.dataOut.data

                while datasize < self.selBlocksize:  # Not enough profiles to fill the block
                    if not(self.readNextBlock()):
                        return 0
                    self.getFirstHeader()
                    self.reshapeData()
                    if self.datablock is None:
                        self.dataOut.flagNoData = True
                        return 0
                    # stack data
                    blockIndex = self.selBlocksize - datasize
                    datablock1 = self.datablock[:, :blockIndex, :]

                    buffer[:, datasize:datasize +
                           datablock1.shape[1], :] = datablock1
                    datasize += datablock1.shape[1]

                self.dataOut.data = buffer
                self.profileIndex = blockIndex

            self.dataOut.flagDataAsBlock = True
            self.dataOut.nProfiles = self.dataOut.data.shape[1]

        self.dataOut.flagNoData = False

        self.getBasicHeader()

        self.dataOut.realtime = self.online

        return self.dataOut.data


@MPDecorator
class VoltageWriter(JRODataWriter, Operation):
    """
    Esta clase permite escribir datos de voltajes a archivos procesados (.r). La escritura
    de los datos siempre se realiza por bloques.
    """

    ext = ".r"

    optchar = "D"

    shapeBuffer = None

    def __init__(self):#, **kwargs):
        """
        Inicializador de la clase VoltageWriter para la escritura de datos de espectros.

        Affected:
            self.dataOut

        Return: None
        """
        Operation.__init__(self)#, **kwargs)

        self.nTotalBlocks = 0

        self.profileIndex = 0

        self.isConfig = False

        self.fp = None

        self.flagIsNewFile = 1

        self.blockIndex = 0

        self.flagIsNewBlock = 0

        self.setFile = None

        self.dtype = None

        self.path = None

        self.filename = None

        self.basicHeaderObj = BasicHeader(LOCALTIME)

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
                                     dtype=numpy.dtype('complex64'))

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
        data = numpy.zeros(self.shapeBuffer, self.dtype)

        junk = numpy.transpose(self.datablock, (1, 2, 0))

        data['real'] = junk.real
        data['imag'] = junk.imag

        data = data.reshape((-1))

        data.tofile(self.fp)

        self.datablock.fill(0)

        self.profileIndex = 0
        self.flagIsNewFile = 0
        self.flagIsNewBlock = 1

        self.blockIndex += 1
        self.nTotalBlocks += 1

#         print "[Writing] Block = %04d" %self.blockIndex

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

        if self.dataOut.flagDiscontinuousBlock:
            self.datablock.fill(0)
            self.profileIndex = 0
            self.setNextFile()

        if self.profileIndex == 0:
            self.setBasicHeader()

        self.datablock[:, self.profileIndex, :] = self.dataOut.data

        self.profileIndex += 1

        if self.hasAllDataInBuffer():
            # if self.flagIsNewFile:
            self.writeNextBlock()
#            self.setFirstHeader()

        return 1

    def __getBlockSize(self):
        '''
        Este metodos determina el cantidad de bytes para un bloque de datos de tipo Voltage
        '''

        dtype_width = self.getDtypeWidth()

        blocksize = int(self.dataOut.nHeights * self.dataOut.nChannels *
                        self.profilesPerBlock * dtype_width * 2)

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

        self.processingHeaderObj.dtype = 0  # Voltage
        self.processingHeaderObj.blockSize = self.__getBlockSize()
        self.processingHeaderObj.profilesPerBlock = self.profilesPerBlock
        self.processingHeaderObj.dataBlocksPerFile = self.blocksPerFile
        # podria ser 1 o self.dataOut.processingHeaderObj.nWindows
        self.processingHeaderObj.nWindows = 1
        self.processingHeaderObj.nCohInt = self.dataOut.nCohInt
        # Cuando la data de origen es de tipo Voltage
        self.processingHeaderObj.nIncohInt = 1
        # Cuando la data de origen es de tipo Voltage
        self.processingHeaderObj.totalSpectra = 0

        if self.dataOut.code is not None:
            self.processingHeaderObj.code = self.dataOut.code
            self.processingHeaderObj.nCode = self.dataOut.nCode
            self.processingHeaderObj.nBaud = self.dataOut.nBaud

        if self.processingHeaderObj.nWindows != 0:
            self.processingHeaderObj.firstHeight = self.dataOut.heightList[0]
            self.processingHeaderObj.deltaHeight = self.dataOut.heightList[1] - \
                self.dataOut.heightList[0]
            self.processingHeaderObj.nHeights = self.dataOut.nHeights
            self.processingHeaderObj.samplesWin = self.dataOut.nHeights

        self.processingHeaderObj.processFlags = self.getProcessFlags()

        self.setBasicHeader()
        