import sys
import numpy,math
from scipy import interpolate
from schainpy.model.proc.jroproc_base import ProcessingUnit, Operation, MPDecorator
from schainpy.model.data.jrodata import Voltage,hildebrand_sekhon
from schainpy.utils import log
from time import time



class VoltageProc(ProcessingUnit):

    def __init__(self):

        ProcessingUnit.__init__(self)

        self.dataOut = Voltage()
        self.flip = 1
        self.setupReq = False

    def run(self):

        if self.dataIn.type == 'AMISR':
            self.__updateObjFromAmisrInput()

        if self.dataIn.type == 'Voltage':
            self.dataOut.copy(self.dataIn)

    def __updateObjFromAmisrInput(self):

        self.dataOut.timeZone = self.dataIn.timeZone
        self.dataOut.dstFlag = self.dataIn.dstFlag
        self.dataOut.errorCount = self.dataIn.errorCount
        self.dataOut.useLocalTime = self.dataIn.useLocalTime

        self.dataOut.flagNoData = self.dataIn.flagNoData
        self.dataOut.data = self.dataIn.data
        self.dataOut.utctime = self.dataIn.utctime
        self.dataOut.channelList = self.dataIn.channelList
        #self.dataOut.timeInterval = self.dataIn.timeInterval
        self.dataOut.heightList = self.dataIn.heightList
        self.dataOut.nProfiles = self.dataIn.nProfiles

        self.dataOut.nCohInt = self.dataIn.nCohInt
        self.dataOut.ippSeconds = self.dataIn.ippSeconds
        self.dataOut.frequency = self.dataIn.frequency

        self.dataOut.azimuth = self.dataIn.azimuth
        self.dataOut.zenith = self.dataIn.zenith

        self.dataOut.beam.codeList = self.dataIn.beam.codeList
        self.dataOut.beam.azimuthList = self.dataIn.beam.azimuthList
        self.dataOut.beam.zenithList = self.dataIn.beam.zenithList


class selectChannels(Operation):

    def run(self, dataOut, channelList):

        channelIndexList = []
        self.dataOut = dataOut
        for channel in channelList:
            if channel not in self.dataOut.channelList:
                raise ValueError("Channel %d is not in %s" %(channel, str(self.dataOut.channelList)))

            index = self.dataOut.channelList.index(channel)
            channelIndexList.append(index)
        self.selectChannelsByIndex(channelIndexList)
        return self.dataOut

    def selectChannelsByIndex(self, channelIndexList):
        """
        Selecciona un bloque de datos en base a canales segun el channelIndexList

        Input:
            channelIndexList    :    lista sencilla de canales a seleccionar por ej. [2,3,7]

        Affected:
            self.dataOut.data
            self.dataOut.channelIndexList
            self.dataOut.nChannels
            self.dataOut.m_ProcessingHeader.totalSpectra
            self.dataOut.systemHeaderObj.numChannels
            self.dataOut.m_ProcessingHeader.blockSize

        Return:
            None
        """

        for channelIndex in channelIndexList:
            if channelIndex not in self.dataOut.channelIndexList:
                raise ValueError("The value %d in channelIndexList is not valid" %channelIndex)

        if self.dataOut.type == 'Voltage':
            if self.dataOut.flagDataAsBlock:
                """
                Si la data es obtenida por bloques, dimension = [nChannels, nProfiles, nHeis]
                """
                data = self.dataOut.data[channelIndexList,:,:]
            else:
                data = self.dataOut.data[channelIndexList,:]

            self.dataOut.data = data
            # self.dataOut.channelList = [self.dataOut.channelList[i] for i in channelIndexList]
            self.dataOut.channelList = range(len(channelIndexList))

        elif self.dataOut.type == 'Spectra':
            data_spc = self.dataOut.data_spc[channelIndexList, :]
            data_dc = self.dataOut.data_dc[channelIndexList, :]

            self.dataOut.data_spc = data_spc
            self.dataOut.data_dc = data_dc

            # self.dataOut.channelList = [self.dataOut.channelList[i] for i in channelIndexList]
            self.dataOut.channelList = range(len(channelIndexList))
            self.__selectPairsByChannel(channelIndexList)

        return 1

    def __selectPairsByChannel(self, channelList=None):

        if channelList == None:
            return

        pairsIndexListSelected = []
        for pairIndex in self.dataOut.pairsIndexList:
            # First pair
            if self.dataOut.pairsList[pairIndex][0] not in channelList:
                continue
            # Second pair
            if self.dataOut.pairsList[pairIndex][1] not in channelList:
                continue

            pairsIndexListSelected.append(pairIndex)

        if not pairsIndexListSelected:
            self.dataOut.data_cspc = None
            self.dataOut.pairsList = []
            return

        self.dataOut.data_cspc = self.dataOut.data_cspc[pairsIndexListSelected]
        self.dataOut.pairsList = [self.dataOut.pairsList[i]
                                  for i in pairsIndexListSelected]

        return

class selectHeights(Operation):

    def run(self, dataOut, minHei=None, maxHei=None, minIndex=None, maxIndex=None):
        """
        Selecciona un bloque de datos en base a un grupo de valores de alturas segun el rango
        minHei <= height <= maxHei

        Input:
            minHei    :    valor minimo de altura a considerar
            maxHei    :    valor maximo de altura a considerar

        Affected:
            Indirectamente son cambiados varios valores a travez del metodo selectHeightsByIndex

        Return:
            1 si el metodo se ejecuto con exito caso contrario devuelve 0
        """

        self.dataOut = dataOut

        if minHei and maxHei:

            if (minHei < self.dataOut.heightList[0]):
                minHei = self.dataOut.heightList[0]

            if (maxHei > self.dataOut.heightList[-1]):
                maxHei = self.dataOut.heightList[-1]

            minIndex = 0
            maxIndex = 0
            heights = self.dataOut.heightList

            inda = numpy.where(heights >= minHei)
            indb = numpy.where(heights <= maxHei)

            try:
                minIndex = inda[0][0]
            except:
                minIndex = 0

            try:
                maxIndex = indb[0][-1]
            except:
                maxIndex = len(heights)

        self.selectHeightsByIndex(minIndex, maxIndex)

        return self.dataOut

    def selectHeightsByIndex(self, minIndex, maxIndex):
        """
        Selecciona un bloque de datos en base a un grupo indices de alturas segun el rango
        minIndex <= index <= maxIndex

        Input:
            minIndex    :    valor de indice minimo de altura a considerar
            maxIndex    :    valor de indice maximo de altura a considerar

        Affected:
            self.dataOut.data
            self.dataOut.heightList

        Return:
            1 si el metodo se ejecuto con exito caso contrario devuelve 0
        """

        if self.dataOut.type == 'Voltage':
            if (minIndex < 0) or (minIndex > maxIndex):
                raise ValueError("Height index range (%d,%d) is not valid" % (minIndex, maxIndex))

            if (maxIndex >= self.dataOut.nHeights):
                maxIndex = self.dataOut.nHeights

            #voltage
            if self.dataOut.flagDataAsBlock:
                """
                Si la data es obtenida por bloques, dimension = [nChannels, nProfiles, nHeis]
                """
                data = self.dataOut.data[:,:, minIndex:maxIndex]
            else:
                data = self.dataOut.data[:, minIndex:maxIndex]

            #         firstHeight = self.dataOut.heightList[minIndex]

            self.dataOut.data = data
            self.dataOut.heightList = self.dataOut.heightList[minIndex:maxIndex]

            if self.dataOut.nHeights <= 1:
                raise ValueError("selectHeights: Too few heights. Current number of heights is %d" %(self.dataOut.nHeights))
        elif self.dataOut.type == 'Spectra':
            if (minIndex < 0) or (minIndex > maxIndex):
                raise ValueError("Error selecting heights: Index range (%d,%d) is not valid" % (
                    minIndex, maxIndex))

            if (maxIndex >= self.dataOut.nHeights):
                maxIndex = self.dataOut.nHeights - 1

            # Spectra
            data_spc = self.dataOut.data_spc[:, :, minIndex:maxIndex + 1]

            data_cspc = None
            if self.dataOut.data_cspc is not None:
                data_cspc = self.dataOut.data_cspc[:, :, minIndex:maxIndex + 1]

            data_dc = None
            if self.dataOut.data_dc is not None:
                data_dc = self.dataOut.data_dc[:, minIndex:maxIndex + 1]

            self.dataOut.data_spc = data_spc
            self.dataOut.data_cspc = data_cspc
            self.dataOut.data_dc = data_dc

            self.dataOut.heightList = self.dataOut.heightList[minIndex:maxIndex + 1]

        return 1


class filterByHeights(Operation):

    def run(self, dataOut, window):

        deltaHeight = dataOut.heightList[1] - dataOut.heightList[0]

        if window == None:
            window = (dataOut.radarControllerHeaderObj.txA/dataOut.radarControllerHeaderObj.nBaud) / deltaHeight

        newdelta = deltaHeight * window
        r = dataOut.nHeights % window
        newheights = (dataOut.nHeights-r)/window

        if newheights <= 1:
            raise ValueError("filterByHeights: Too few heights. Current number of heights is %d and window is %d" %(dataOut.nHeights, window))

        if dataOut.flagDataAsBlock:
            """
            Si la data es obtenida por bloques, dimension = [nChannels, nProfiles, nHeis]
            """
            buffer = dataOut.data[:, :, 0:int(dataOut.nHeights-r)]
            buffer = buffer.reshape(dataOut.nChannels, dataOut.nProfiles, int(dataOut.nHeights/window), window)
            buffer = numpy.sum(buffer,3)

        else:
            buffer = dataOut.data[:,0:int(dataOut.nHeights-r)]
            buffer = buffer.reshape(dataOut.nChannels,int(dataOut.nHeights/window),int(window))
            buffer = numpy.sum(buffer,2)

        dataOut.data = buffer
        dataOut.heightList = dataOut.heightList[0] + numpy.arange( newheights )*newdelta
        dataOut.windowOfFilter = window

        return dataOut


class setH0(Operation):

    def run(self, dataOut, h0, deltaHeight = None):

        if not deltaHeight:
            deltaHeight = dataOut.heightList[1] - dataOut.heightList[0]

        nHeights = dataOut.nHeights

        newHeiRange = h0 + numpy.arange(nHeights)*deltaHeight

        dataOut.heightList = newHeiRange

        return dataOut


class deFlip(Operation):

    def run(self, dataOut, channelList = []):

        data = dataOut.data.copy()

        if dataOut.flagDataAsBlock:
            flip = self.flip
            profileList = list(range(dataOut.nProfiles))

            if not channelList:
                for thisProfile in profileList:
                    data[:,thisProfile,:] = data[:,thisProfile,:]*flip
                    flip *= -1.0
            else:
                for thisChannel in channelList:
                    if thisChannel not in dataOut.channelList:
                        continue

                    for thisProfile in profileList:
                        data[thisChannel,thisProfile,:] = data[thisChannel,thisProfile,:]*flip
                        flip *= -1.0

            self.flip = flip

        else:
            if not channelList:
                data[:,:] = data[:,:]*self.flip
            else:
                for thisChannel in channelList:
                    if thisChannel not in dataOut.channelList:
                        continue

                    data[thisChannel,:] = data[thisChannel,:]*self.flip

            self.flip *= -1.

        dataOut.data = data

        return dataOut


class setAttribute(Operation):
    '''
    Set an arbitrary attribute(s) to dataOut
    '''

    def __init__(self):

        Operation.__init__(self)
        self._ready = False

    def run(self, dataOut, **kwargs):

        for key, value in kwargs.items():
            setattr(dataOut, key, value)

        return dataOut


@MPDecorator
class printAttribute(Operation):
    '''
    Print an arbitrary attribute of dataOut
    '''

    def __init__(self):

        Operation.__init__(self)

    def run(self, dataOut, attributes):

        if isinstance(attributes, str):
            attributes = [attributes]
        for attr in attributes:
            if hasattr(dataOut, attr):
                log.log(getattr(dataOut, attr), attr)


class interpolateHeights(Operation):

    def run(self, dataOut, topLim, botLim):
        #69 al 72 para julia
        #82-84 para meteoros
        if len(numpy.shape(dataOut.data))==2:
            sampInterp = (dataOut.data[:,botLim-1] + dataOut.data[:,topLim+1])/2
            sampInterp = numpy.transpose(numpy.tile(sampInterp,(topLim-botLim + 1,1)))
            #dataOut.data[:,botLim:limSup+1] = sampInterp
            dataOut.data[:,botLim:topLim+1] = sampInterp
        else:
            nHeights = dataOut.data.shape[2]
            x = numpy.hstack((numpy.arange(botLim),numpy.arange(topLim+1,nHeights)))
            y = dataOut.data[:,:,list(range(botLim))+list(range(topLim+1,nHeights))]
            f = interpolate.interp1d(x, y, axis = 2)
            xnew = numpy.arange(botLim,topLim+1)
            ynew = f(xnew)
            dataOut.data[:,:,botLim:topLim+1]  = ynew

        return dataOut


class CohInt(Operation):

    isConfig = False
    __profIndex = 0
    __byTime = False
    __initime = None
    __lastdatatime = None
    __integrationtime = None
    __buffer = None
    __bufferStride = []
    __dataReady = False
    __profIndexStride = 0
    __dataToPutStride = False
    n = None

    def __init__(self, **kwargs):

        Operation.__init__(self, **kwargs)

    def setup(self, n=None, timeInterval=None, stride=None, overlapping=False, byblock=False):
        """
        Set the parameters of the integration class.

        Inputs:

            n               :    Number of coherent integrations
            timeInterval    :    Time of integration. If the parameter "n" is selected this one does not work
            overlapping     :
        """

        self.__initime = None
        self.__lastdatatime = 0
        self.__buffer = None
        self.__dataReady = False
        self.byblock = byblock
        self.stride = stride

        if n == None and timeInterval == None:
            raise ValueError("n or timeInterval should be specified ...")

        if n != None:
            self.n = n
            self.__byTime = False
        else:
            self.__integrationtime = timeInterval #* 60. #if (type(timeInterval)!=integer) -> change this line
            self.n = 9999
            self.__byTime = True

        if overlapping:
            self.__withOverlapping = True
            self.__buffer = None
        else:
            self.__withOverlapping = False
            self.__buffer = 0

        self.__profIndex = 0

    def putData(self, data):

        """
        Add a profile to the __buffer and increase in one the __profileIndex

        """

        if not self.__withOverlapping:
            self.__buffer += data.copy()
            self.__profIndex += 1
            return

        #Overlapping data
        nChannels, nHeis = data.shape
        data = numpy.reshape(data, (1, nChannels, nHeis))

        #If the buffer is empty then it takes the data value
        if self.__buffer is None:
            self.__buffer = data
            self.__profIndex += 1
            return

        #If the buffer length is lower than n then stakcing the data value
        if self.__profIndex < self.n:
            self.__buffer = numpy.vstack((self.__buffer, data))
            self.__profIndex += 1
            return

        #If the buffer length is equal to n then replacing the last buffer value with the data value
        self.__buffer = numpy.roll(self.__buffer, -1, axis=0)
        self.__buffer[self.n-1] = data
        self.__profIndex = self.n
        return


    def pushData(self):
        """
        Return the sum of the last profiles and the profiles used in the sum.

        Affected:

        self.__profileIndex

        """

        if not self.__withOverlapping:
            data = self.__buffer
            n = self.__profIndex

            self.__buffer = 0
            self.__profIndex = 0

            return data, n

        #Integration with Overlapping
        data = numpy.sum(self.__buffer, axis=0)
        # print data
        # raise
        n = self.__profIndex

        return data, n

    def byProfiles(self, data):

        self.__dataReady = False
        avgdata = None
        #         n = None
        # print data
        # raise
        self.putData(data)

        if self.__profIndex == self.n:
            avgdata, n = self.pushData()
            self.__dataReady = True

        return avgdata

    def byTime(self, data, datatime):

        self.__dataReady = False
        avgdata = None
        n = None

        self.putData(data)

        if (datatime - self.__initime) >= self.__integrationtime:
            avgdata, n = self.pushData()
            self.n = n
            self.__dataReady = True

        return avgdata

    def integrateByStride(self, data, datatime):
        # print data
        if self.__profIndex == 0:
            self.__buffer = [[data.copy(), datatime]]
        else:
            self.__buffer.append([data.copy(),datatime])
        self.__profIndex += 1
        self.__dataReady = False

        if self.__profIndex == self.n * self.stride :
            self.__dataToPutStride = True
            self.__profIndexStride = 0
            self.__profIndex = 0
            self.__bufferStride = []
            for i in range(self.stride):
                current = self.__buffer[i::self.stride]
                data = numpy.sum([t[0] for t in current], axis=0)
                avgdatatime = numpy.average([t[1] for t in current])
                # print data
                self.__bufferStride.append((data, avgdatatime))

        if self.__dataToPutStride:
            self.__dataReady = True
            self.__profIndexStride += 1
            if self.__profIndexStride == self.stride:
                self.__dataToPutStride = False
            # print self.__bufferStride[self.__profIndexStride - 1]
            # raise
            return self.__bufferStride[self.__profIndexStride - 1]


        return None, None

    def integrate(self, data, datatime=None):

        if self.__initime == None:
            self.__initime = datatime

        if self.__byTime:
            avgdata = self.byTime(data, datatime)
        else:
            avgdata = self.byProfiles(data)


        self.__lastdatatime = datatime

        if avgdata is None:
            return None, None

        avgdatatime = self.__initime

        deltatime = datatime - self.__lastdatatime

        if not self.__withOverlapping:
            self.__initime = datatime
        else:
            self.__initime += deltatime

        return avgdata, avgdatatime

    def integrateByBlock(self, dataOut):

        times = int(dataOut.data.shape[1]/self.n)
        avgdata = numpy.zeros((dataOut.nChannels, times, dataOut.nHeights), dtype=numpy.complex)

        id_min = 0
        id_max = self.n

        for i in range(times):
            junk = dataOut.data[:,id_min:id_max,:]
            avgdata[:,i,:] = junk.sum(axis=1)
            id_min += self.n
            id_max += self.n

        timeInterval = dataOut.ippSeconds*self.n
        avgdatatime = (times - 1) * timeInterval + dataOut.utctime
        self.__dataReady = True
        return avgdata, avgdatatime

    def run(self, dataOut, n=None, timeInterval=None, stride=None, overlapping=False, byblock=False, **kwargs):

        if not self.isConfig:
            self.setup(n=n, stride=stride, timeInterval=timeInterval, overlapping=overlapping, byblock=byblock, **kwargs)
            self.isConfig = True

        if dataOut.flagDataAsBlock:
            """
            Si la data es leida por bloques, dimension = [nChannels, nProfiles, nHeis]
            """
            avgdata, avgdatatime = self.integrateByBlock(dataOut)
            dataOut.nProfiles /= self.n
        else:
            if stride is None:
                avgdata, avgdatatime = self.integrate(dataOut.data, dataOut.utctime)
            else:
                avgdata, avgdatatime = self.integrateByStride(dataOut.data, dataOut.utctime)


        #   dataOut.timeInterval *= n
        dataOut.flagNoData = True

        if self.__dataReady:
            dataOut.data = avgdata
            if not dataOut.flagCohInt:
                dataOut.nCohInt *= self.n
                dataOut.flagCohInt = True
            dataOut.utctime = avgdatatime
            # print avgdata, avgdatatime
            # raise
            #   dataOut.timeInterval = dataOut.ippSeconds * dataOut.nCohInt
            dataOut.flagNoData = False
        return dataOut

class Decoder(Operation):

    isConfig = False
    __profIndex = 0

    code = None

    nCode = None
    nBaud = None

    def __init__(self, **kwargs):

        Operation.__init__(self, **kwargs)

        self.times = None
        self.osamp = None
    #         self.__setValues = False
        self.isConfig = False
        self.setupReq = False
    def setup(self, code, osamp, dataOut):

        self.__profIndex = 0

        self.code = code

        self.nCode = len(code)
        self.nBaud = len(code[0])

        if (osamp != None) and (osamp >1):
            self.osamp = osamp
            self.code = numpy.repeat(code, repeats=self.osamp, axis=1)
            self.nBaud = self.nBaud*self.osamp

        self.__nChannels = dataOut.nChannels
        self.__nProfiles = dataOut.nProfiles
        self.__nHeis = dataOut.nHeights

        if self.__nHeis < self.nBaud:
            raise ValueError('Number of heights (%d) should be greater than number of bauds (%d)' %(self.__nHeis, self.nBaud))

        #Frequency
        __codeBuffer = numpy.zeros((self.nCode, self.__nHeis), dtype=numpy.complex)

        __codeBuffer[:,0:self.nBaud] = self.code

        self.fft_code = numpy.conj(numpy.fft.fft(__codeBuffer, axis=1))

        if dataOut.flagDataAsBlock:

            self.ndatadec = self.__nHeis #- self.nBaud + 1

            self.datadecTime = numpy.zeros((self.__nChannels, self.__nProfiles, self.ndatadec), dtype=numpy.complex)

        else:

            #Time
            self.ndatadec = self.__nHeis #- self.nBaud + 1

            self.datadecTime = numpy.zeros((self.__nChannels, self.ndatadec), dtype=numpy.complex)

    def __convolutionInFreq(self, data):

        fft_code = self.fft_code[self.__profIndex].reshape(1,-1)

        fft_data = numpy.fft.fft(data, axis=1)

        conv = fft_data*fft_code

        data = numpy.fft.ifft(conv,axis=1)

        return data

    def __convolutionInFreqOpt(self, data):

        raise NotImplementedError

    def __convolutionInTime(self, data):

        code = self.code[self.__profIndex]
        for i in range(self.__nChannels):
            self.datadecTime[i,:] = numpy.correlate(data[i,:], code, mode='full')[self.nBaud-1:]

        return self.datadecTime

    def __convolutionByBlockInTime(self, data):

        repetitions = int(self.__nProfiles / self.nCode)
        junk = numpy.lib.stride_tricks.as_strided(self.code, (repetitions, self.code.size), (0, self.code.itemsize))
        junk = junk.flatten()
        code_block = numpy.reshape(junk, (self.nCode*repetitions, self.nBaud))
        profilesList = range(self.__nProfiles)

        for i in range(self.__nChannels):
            for j in profilesList:
                self.datadecTime[i,j,:] = numpy.correlate(data[i,j,:], code_block[j,:], mode='full')[self.nBaud-1:]
        return self.datadecTime

    def __convolutionByBlockInFreq(self, data):

        raise NotImplementedError("Decoder by frequency fro Blocks not implemented")


        fft_code = self.fft_code[self.__profIndex].reshape(1,-1)

        fft_data = numpy.fft.fft(data, axis=2)

        conv = fft_data*fft_code

        data = numpy.fft.ifft(conv,axis=2)

        return data


    def run(self, dataOut, code=None, nCode=None, nBaud=None, mode = 0, osamp=None, times=None):

        if dataOut.flagDecodeData:
            print("This data is already decoded, recoding again ...")

        if not self.isConfig:

            if code is None:
                if dataOut.code is None:
                    raise ValueError("Code could not be read from %s instance. Enter a value in Code parameter" %dataOut.type)

                code = dataOut.code
            else:
                code = numpy.array(code).reshape(nCode,nBaud)
            self.setup(code, osamp, dataOut)

            self.isConfig = True

            if mode == 3:
                sys.stderr.write("Decoder Warning: mode=%d is not valid, using mode=0\n" %mode)

            if times != None:
                sys.stderr.write("Decoder Warning: Argument 'times' in not used anymore\n")

        if self.code is None:
            print("Fail decoding: Code is not defined.")
            return

        self.__nProfiles = dataOut.nProfiles
        datadec = None

        if mode == 3:
            mode = 0

        if dataOut.flagDataAsBlock:
            """
            Decoding when data have been read as block,
            """

            if mode == 0:
                datadec = self.__convolutionByBlockInTime(dataOut.data)
            if mode == 1:
                datadec = self.__convolutionByBlockInFreq(dataOut.data)
        else:
            """
            Decoding when data have been read profile by profile
            """
            if mode == 0:
                datadec = self.__convolutionInTime(dataOut.data)

            if mode == 1:
                datadec = self.__convolutionInFreq(dataOut.data)

            if mode == 2:
                datadec = self.__convolutionInFreqOpt(dataOut.data)

        if datadec is None:
            raise ValueError("Codification mode selected is not valid: mode=%d. Try selecting 0 or 1" %mode)

        dataOut.code = self.code
        dataOut.nCode = self.nCode
        dataOut.nBaud = self.nBaud

        dataOut.data = datadec

        dataOut.heightList = dataOut.heightList[0:datadec.shape[-1]]

        dataOut.flagDecodeData = True #asumo q la data esta decodificada

        if self.__profIndex == self.nCode-1:
            self.__profIndex = 0
            return dataOut

        self.__profIndex += 1

        return dataOut
    #        dataOut.flagDeflipData = True #asumo q la data no esta sin flip


class ProfileConcat(Operation):

    isConfig = False
    buffer = None

    def __init__(self, **kwargs):

        Operation.__init__(self, **kwargs)
        self.profileIndex = 0

    def reset(self):
        self.buffer = numpy.zeros_like(self.buffer)
        self.start_index = 0
        self.times = 1

    def setup(self, data, m, n=1):
        self.buffer = numpy.zeros((data.shape[0],data.shape[1]*m),dtype=type(data[0,0]))
        self.nHeights = data.shape[1]#.nHeights
        self.start_index = 0
        self.times = 1

    def concat(self, data):

        self.buffer[:,self.start_index:self.nHeights*self.times] = data.copy()
        self.start_index = self.start_index + self.nHeights

    def run(self, dataOut, m):
        dataOut.flagNoData = True

        if not self.isConfig:
            self.setup(dataOut.data, m, 1)
            self.isConfig = True

        if dataOut.flagDataAsBlock:
            raise ValueError("ProfileConcat can only be used when voltage have been read profile by profile, getBlock = False")

        else:
            self.concat(dataOut.data)
            self.times += 1
            if self.times > m:
                dataOut.data = self.buffer
                self.reset()
                dataOut.flagNoData = False
                # se deben actualizar mas propiedades del header y del objeto dataOut, por ejemplo, las alturas
                deltaHeight = dataOut.heightList[1] - dataOut.heightList[0]
                xf = dataOut.heightList[0] + dataOut.nHeights * deltaHeight * m
                dataOut.heightList = numpy.arange(dataOut.heightList[0], xf, deltaHeight)
                dataOut.ippSeconds *= m
        return dataOut

class ProfileSelector(Operation):

    profileIndex = None
    # Tamanho total de los perfiles
    nProfiles = None

    def __init__(self, **kwargs):

        Operation.__init__(self, **kwargs)
        self.profileIndex = 0

    def incProfileIndex(self):

        self.profileIndex += 1

        if self.profileIndex >= self.nProfiles:
            self.profileIndex = 0

    def isThisProfileInRange(self, profileIndex, minIndex, maxIndex):

        if profileIndex < minIndex:
            return False

        if profileIndex > maxIndex:
            return False

        return True

    def isThisProfileInList(self, profileIndex, profileList):

        if profileIndex not in profileList:
            return False

        return True

    def run(self, dataOut, profileList=None, profileRangeList=None, beam=None, byblock=False, rangeList = None, nProfiles=None):

        """
        ProfileSelector:

        Inputs:
            profileList        :    Index of profiles selected. Example: profileList = (0,1,2,7,8)

            profileRangeList    :    Minimum and maximum profile indexes. Example: profileRangeList = (4, 30)

            rangeList            :    List of profile ranges. Example: rangeList = ((4, 30), (32, 64), (128, 256))

        """

        if rangeList is not None:
            if type(rangeList[0]) not in (tuple, list):
                rangeList = [rangeList]

        dataOut.flagNoData = True

        if dataOut.flagDataAsBlock:
            """
            data dimension  = [nChannels, nProfiles, nHeis]
            """
            if profileList != None:
                dataOut.data = dataOut.data[:,profileList,:]

            if profileRangeList != None:
                minIndex = profileRangeList[0]
                maxIndex = profileRangeList[1]
                profileList = list(range(minIndex, maxIndex+1))

                dataOut.data = dataOut.data[:,minIndex:maxIndex+1,:]

            if rangeList != None:

                profileList = []

                for thisRange in rangeList:
                    minIndex = thisRange[0]
                    maxIndex = thisRange[1]

                    profileList.extend(list(range(minIndex, maxIndex+1)))

                dataOut.data = dataOut.data[:,profileList,:]

            dataOut.nProfiles = len(profileList)
            dataOut.profileIndex = dataOut.nProfiles - 1
            dataOut.flagNoData = False

            return dataOut

        """
        data dimension  = [nChannels, nHeis]
        """

        if profileList != None:

            if self.isThisProfileInList(dataOut.profileIndex, profileList):

                self.nProfiles = len(profileList)
                dataOut.nProfiles = self.nProfiles
                dataOut.profileIndex = self.profileIndex
                dataOut.flagNoData = False

                self.incProfileIndex()
            return dataOut

        if profileRangeList != None:

            minIndex = profileRangeList[0]
            maxIndex = profileRangeList[1]

            if self.isThisProfileInRange(dataOut.profileIndex, minIndex, maxIndex):

                self.nProfiles = maxIndex - minIndex + 1
                dataOut.nProfiles = self.nProfiles
                dataOut.profileIndex = self.profileIndex
                dataOut.flagNoData = False

                self.incProfileIndex()
            return dataOut

        if rangeList != None:

            nProfiles = 0

            for thisRange in rangeList:
                minIndex = thisRange[0]
                maxIndex = thisRange[1]

                nProfiles += maxIndex - minIndex + 1

            for thisRange in rangeList:

                minIndex = thisRange[0]
                maxIndex = thisRange[1]

                if self.isThisProfileInRange(dataOut.profileIndex, minIndex, maxIndex):

                    self.nProfiles = nProfiles
                    dataOut.nProfiles = self.nProfiles
                    dataOut.profileIndex = self.profileIndex
                    dataOut.flagNoData = False

                    self.incProfileIndex()

                    break

            return dataOut


        if beam != None: #beam is only for AMISR data
            if self.isThisProfileInList(dataOut.profileIndex, dataOut.beamRangeDict[beam]):
                dataOut.flagNoData = False
                dataOut.profileIndex = self.profileIndex

                self.incProfileIndex()

            return dataOut

        raise ValueError("ProfileSelector needs profileList, profileRangeList or rangeList parameter")


class Reshaper(Operation):

    def __init__(self, **kwargs):

        Operation.__init__(self, **kwargs)

        self.__buffer = None
        self.__nitems = 0

    def __appendProfile(self, dataOut, nTxs):

        if self.__buffer is None:
            shape = (dataOut.nChannels, int(dataOut.nHeights/nTxs) )
            self.__buffer = numpy.empty(shape, dtype = dataOut.data.dtype)

        ini = dataOut.nHeights * self.__nitems
        end = ini + dataOut.nHeights

        self.__buffer[:, ini:end] = dataOut.data

        self.__nitems += 1

        return int(self.__nitems*nTxs)

    def __getBuffer(self):

        if self.__nitems == int(1./self.__nTxs):

            self.__nitems = 0

            return self.__buffer.copy()

        return None

    def __checkInputs(self, dataOut, shape, nTxs):

        if shape is None and nTxs is None:
            raise ValueError("Reshaper: shape of factor should be defined")

        if nTxs:
            if nTxs < 0:
                raise ValueError("nTxs should be greater than 0")

            if nTxs < 1 and dataOut.nProfiles % (1./nTxs) != 0:
                raise ValueError("nProfiles= %d is not divisibled by (1./nTxs) = %f" %(dataOut.nProfiles, (1./nTxs)))

            shape = [dataOut.nChannels, dataOut.nProfiles*nTxs, dataOut.nHeights/nTxs]

            return shape, nTxs

        if len(shape) != 2 and len(shape) !=  3:
            raise ValueError("shape dimension should be equal to 2 or 3. shape = (nProfiles, nHeis) or (nChannels, nProfiles, nHeis). Actually shape = (%d, %d, %d)" %(dataOut.nChannels, dataOut.nProfiles, dataOut.nHeights))

        if len(shape) == 2:
            shape_tuple = [dataOut.nChannels]
            shape_tuple.extend(shape)
        else:
            shape_tuple = list(shape)

        nTxs = 1.0*shape_tuple[1]/dataOut.nProfiles

        return shape_tuple, nTxs

    def run(self, dataOut, shape=None, nTxs=None):

        shape_tuple, self.__nTxs = self.__checkInputs(dataOut, shape, nTxs)

        dataOut.flagNoData = True
        profileIndex = None

        if dataOut.flagDataAsBlock:

            dataOut.data = numpy.reshape(dataOut.data, shape_tuple)
            dataOut.flagNoData = False

            profileIndex = int(dataOut.nProfiles*self.__nTxs) - 1

        else:

            if self.__nTxs < 1:

                self.__appendProfile(dataOut, self.__nTxs)
                new_data = self.__getBuffer()

                if new_data is not None:
                    dataOut.data = new_data
                    dataOut.flagNoData = False

                    profileIndex = dataOut.profileIndex*nTxs

            else:
                raise ValueError("nTxs should be greater than 0 and lower than 1, or use VoltageReader(..., getblock=True)")

        deltaHeight = dataOut.heightList[1] - dataOut.heightList[0]

        dataOut.heightList = numpy.arange(dataOut.nHeights/self.__nTxs) * deltaHeight + dataOut.heightList[0]

        dataOut.nProfiles = int(dataOut.nProfiles*self.__nTxs)

        dataOut.profileIndex = profileIndex

        dataOut.ippSeconds /= self.__nTxs

        return dataOut

class SplitProfiles(Operation):

    def __init__(self, **kwargs):

        Operation.__init__(self, **kwargs)

    def run(self, dataOut, n):

        dataOut.flagNoData = True
        profileIndex = None

        if dataOut.flagDataAsBlock:

            #nchannels, nprofiles, nsamples
            shape = dataOut.data.shape

            if shape[2] % n != 0:
                raise ValueError("Could not split the data, n=%d has to be multiple of %d" %(n, shape[2]))

            new_shape = shape[0], shape[1]*n, int(shape[2]/n)

            dataOut.data = numpy.reshape(dataOut.data, new_shape)
            dataOut.flagNoData = False

            profileIndex = int(dataOut.nProfiles/n) - 1

        else:

            raise ValueError("Could not split the data when is read Profile by Profile. Use VoltageReader(..., getblock=True)")

        deltaHeight = dataOut.heightList[1] - dataOut.heightList[0]

        dataOut.heightList = numpy.arange(dataOut.nHeights/n) * deltaHeight + dataOut.heightList[0]

        dataOut.nProfiles = int(dataOut.nProfiles*n)

        dataOut.profileIndex = profileIndex

        dataOut.ippSeconds /= n

        return dataOut

class CombineProfiles(Operation):
    def __init__(self, **kwargs):

        Operation.__init__(self, **kwargs)

        self.__remData = None
        self.__profileIndex = 0

    def run(self, dataOut, n):

        dataOut.flagNoData = True
        profileIndex = None

        if dataOut.flagDataAsBlock:

            #nchannels, nprofiles, nsamples
            shape = dataOut.data.shape
            new_shape = shape[0], shape[1]/n, shape[2]*n

            if shape[1] % n != 0:
                raise ValueError("Could not split the data, n=%d has to be multiple of %d" %(n, shape[1]))

            dataOut.data = numpy.reshape(dataOut.data, new_shape)
            dataOut.flagNoData = False

            profileIndex = int(dataOut.nProfiles*n) - 1

        else:

            #nchannels, nsamples
            if self.__remData is None:
                newData = dataOut.data
            else:
                newData = numpy.concatenate((self.__remData, dataOut.data), axis=1)

            self.__profileIndex += 1

            if self.__profileIndex < n:
                self.__remData = newData
                #continue
                return

            self.__profileIndex = 0
            self.__remData = None

            dataOut.data = newData
            dataOut.flagNoData = False

            profileIndex = dataOut.profileIndex/n


        deltaHeight = dataOut.heightList[1] - dataOut.heightList[0]

        dataOut.heightList = numpy.arange(dataOut.nHeights*n) * deltaHeight + dataOut.heightList[0]

        dataOut.nProfiles = int(dataOut.nProfiles/n)

        dataOut.profileIndex = profileIndex

        dataOut.ippSeconds *= n

        return dataOut

class PulsePairVoltage(Operation):
    '''
    Function PulsePair(Signal Power, Velocity)
    The real component of Lag[0] provides Intensity Information
    The imag component of Lag[1] Phase provides Velocity Information

    Configuration Parameters:
    nPRF = Number of Several PRF
    theta = Degree Azimuth angel Boundaries

    Input:
          self.dataOut
          lag[N]
    Affected:
          self.dataOut.spc
    '''
    isConfig       = False
    __profIndex    = 0
    __initime      = None
    __lastdatatime = None
    __buffer       = None
    noise          = None
    __dataReady    = False
    n              = None
    __nch          = 0
    __nHeis        = 0
    removeDC       = False
    ipp            = None
    lambda_        = 0

    def __init__(self,**kwargs):
        Operation.__init__(self,**kwargs)

    def setup(self, dataOut, n = None, removeDC=False):
        '''
        n= Numero de PRF's de entrada
        '''
        self.__initime        = None
        self.__lastdatatime   = 0
        self.__dataReady      = False
        self.__buffer         = 0
        self.__profIndex      = 0
        self.noise            = None
        self.__nch            = dataOut.nChannels
        self.__nHeis          = dataOut.nHeights
        self.removeDC         = removeDC
        self.lambda_          = 3.0e8/(9345.0e6)
        self.ippSec           = dataOut.ippSeconds
        self.nCohInt          = dataOut.nCohInt
        print("IPPseconds",dataOut.ippSeconds)

        print("ELVALOR DE n es:", n)
        if n == None:
            raise ValueError("n should be specified.")

        if n != None:
            if n<2:
                raise ValueError("n should be greater than 2")

        self.n       = n
        self.__nProf = n

        self.__buffer = numpy.zeros((dataOut.nChannels,
                                           n,
                                           dataOut.nHeights),
                                          dtype='complex')

    def putData(self,data):
        '''
        Add a profile to he __buffer and increase in one the __profiel Index
        '''
        self.__buffer[:,self.__profIndex,:]= data
        self.__profIndex      += 1
        return

    def pushData(self,dataOut):
        '''
        Return the PULSEPAIR and the profiles used in the operation
        Affected :  self.__profileIndex
        '''
        #----------------- Remove DC-----------------------------------
        if self.removeDC==True:
            mean    = numpy.mean(self.__buffer,1)
            tmp     = mean.reshape(self.__nch,1,self.__nHeis)
            dc= numpy.tile(tmp,[1,self.__nProf,1])
            self.__buffer = self.__buffer -  dc
        #------------------Calculo de Potencia ------------------------
        pair0       = self.__buffer*numpy.conj(self.__buffer)
        pair0       = pair0.real
        lag_0       = numpy.sum(pair0,1)
        #------------------Calculo de Ruido x canal--------------------
        self.noise  = numpy.zeros(self.__nch)
        for i in range(self.__nch):
            daux         = numpy.sort(pair0[i,:,:],axis= None)
            self.noise[i]=hildebrand_sekhon( daux ,self.nCohInt)

        self.noise       = self.noise.reshape(self.__nch,1)
        self.noise       = numpy.tile(self.noise,[1,self.__nHeis])
        noise_buffer     = self.noise.reshape(self.__nch,1,self.__nHeis)
        noise_buffer     = numpy.tile(noise_buffer,[1,self.__nProf,1])
        #------------------ Potencia recibida= P , Potencia senal = S , Ruido= N--
        #------------------   P= S+N  ,P=lag_0/N ---------------------------------
        #-------------------- Power --------------------------------------------------
        data_power       = lag_0/(self.n*self.nCohInt)
        #------------------  Senal  ---------------------------------------------------
        data_intensity   = pair0 - noise_buffer
        data_intensity   = numpy.sum(data_intensity,axis=1)*(self.n*self.nCohInt)#*self.nCohInt)
        #data_intensity   = (lag_0-self.noise*self.n)*(self.n*self.nCohInt)
        for i in range(self.__nch):
            for j in range(self.__nHeis):
                if data_intensity[i][j]  < 0:
                    data_intensity[i][j] = numpy.min(numpy.absolute(data_intensity[i][j]))

        #----------------- Calculo de Frecuencia y Velocidad doppler--------
        pair1            = self.__buffer[:,:-1,:]*numpy.conjugate(self.__buffer[:,1:,:])
        lag_1            = numpy.sum(pair1,1)
        data_freq        = (-1/(2.0*math.pi*self.ippSec*self.nCohInt))*numpy.angle(lag_1)
        data_velocity    = (self.lambda_/2.0)*data_freq

        #---------------- Potencia promedio estimada de la Senal-----------
        lag_0            = lag_0/self.n
        S                = lag_0-self.noise

        #---------------- Frecuencia Doppler promedio ---------------------
        lag_1            = lag_1/(self.n-1)
        R1               = numpy.abs(lag_1)

        #---------------- Calculo del SNR----------------------------------
        data_snrPP       = S/self.noise
        for i in range(self.__nch):
            for j in range(self.__nHeis):
                if data_snrPP[i][j]  < 1.e-20:
                    data_snrPP[i][j] = 1.e-20

        #----------------- Calculo del ancho espectral ----------------------
        L                = S/R1
        L                = numpy.where(L<0,1,L)
        L                = numpy.log(L)
        tmp              = numpy.sqrt(numpy.absolute(L))
        data_specwidth   = (self.lambda_/(2*math.sqrt(2)*math.pi*self.ippSec*self.nCohInt))*tmp*numpy.sign(L)
        n                = self.__profIndex

        self.__buffer    = numpy.zeros((self.__nch, self.__nProf,self.__nHeis),  dtype='complex')
        self.__profIndex = 0
        return data_power,data_intensity,data_velocity,data_snrPP,data_specwidth,n


    def pulsePairbyProfiles(self,dataOut):

        self.__dataReady     =  False
        data_power           =  None
        data_intensity       =  None
        data_velocity        =  None
        data_specwidth       =  None
        data_snrPP           =  None
        self.putData(data=dataOut.data)
        if self.__profIndex  == self.n:
            data_power,data_intensity, data_velocity,data_snrPP,data_specwidth, n   = self.pushData(dataOut=dataOut)
            self.__dataReady                   = True

        return data_power, data_intensity, data_velocity, data_snrPP, data_specwidth


    def pulsePairOp(self, dataOut, datatime= None):

        if self.__initime == None:
            self.__initime = datatime
        data_power, data_intensity, data_velocity, data_snrPP, data_specwidth = self.pulsePairbyProfiles(dataOut)
        self.__lastdatatime           = datatime

        if data_power is None:
            return None, None, None,None,None,None

        avgdatatime    = self.__initime
        deltatime      = datatime - self.__lastdatatime
        self.__initime = datatime

        return data_power, data_intensity, data_velocity, data_snrPP, data_specwidth, avgdatatime

    def run(self, dataOut,n = None,removeDC= False, overlapping= False,**kwargs):

        if not self.isConfig:
            self.setup(dataOut = dataOut, n    = n , removeDC=removeDC , **kwargs)
            self.isConfig   = True
        data_power, data_intensity, data_velocity,data_snrPP,data_specwidth, avgdatatime = self.pulsePairOp(dataOut, dataOut.utctime)
        dataOut.flagNoData                         = True

        if self.__dataReady:
            dataOut.nCohInt        *= self.n
            dataOut.dataPP_POW      = data_intensity # S
            dataOut.dataPP_POWER    = data_power     # P
            dataOut.dataPP_DOP      = data_velocity
            dataOut.dataPP_SNR      = data_snrPP
            dataOut.dataPP_WIDTH    = data_specwidth
            dataOut.PRFbyAngle      = self.n         #numero de PRF*cada angulo rotado que equivale a un tiempo.
            dataOut.utctime         = avgdatatime
            dataOut.flagNoData      = False
        return dataOut



# import collections
# from scipy.stats import mode
#
# class Synchronize(Operation):
#
#     isConfig = False
#     __profIndex = 0
#
#     def __init__(self, **kwargs):
#
#         Operation.__init__(self, **kwargs)
# #         self.isConfig = False
#         self.__powBuffer = None
#         self.__startIndex = 0
#         self.__pulseFound = False
#
#     def __findTxPulse(self, dataOut, channel=0, pulse_with = None):
#
#         #Read data
#
#         powerdB = dataOut.getPower(channel = channel)
#         noisedB = dataOut.getNoise(channel = channel)[0]
#
#         self.__powBuffer.extend(powerdB.flatten())
#
#         dataArray = numpy.array(self.__powBuffer)
#
#         filteredPower = numpy.correlate(dataArray, dataArray[0:self.__nSamples], "same")
#
#         maxValue = numpy.nanmax(filteredPower)
#
#         if maxValue < noisedB + 10:
#             #No se encuentra ningun pulso de transmision
#             return None
#
#         maxValuesIndex = numpy.where(filteredPower > maxValue - 0.1*abs(maxValue))[0]
#
#         if len(maxValuesIndex) < 2:
#             #Solo se encontro un solo pulso de transmision de un baudio, esperando por el siguiente TX
#             return None
#
#         phasedMaxValuesIndex = maxValuesIndex - self.__nSamples
#
#         #Seleccionar solo valores con un espaciamiento de nSamples
#         pulseIndex = numpy.intersect1d(maxValuesIndex, phasedMaxValuesIndex)
#
#         if len(pulseIndex) < 2:
#             #Solo se encontro un pulso de transmision con ancho mayor a 1
#             return None
#
#         spacing = pulseIndex[1:] - pulseIndex[:-1]
#
#         #remover senales que se distancien menos de 10 unidades o muestras
#         #(No deberian existir IPP menor a 10 unidades)
#
#         realIndex = numpy.where(spacing > 10 )[0]
#
#         if len(realIndex) < 2:
#             #Solo se encontro un pulso de transmision con ancho mayor a 1
#             return None
#
#         #Eliminar pulsos anchos (deja solo la diferencia entre IPPs)
#         realPulseIndex = pulseIndex[realIndex]
#
#         period = mode(realPulseIndex[1:] - realPulseIndex[:-1])[0][0]
#
#         print "IPP = %d samples" %period
#
#         self.__newNSamples = dataOut.nHeights #int(period)
#         self.__startIndex = int(realPulseIndex[0])
#
#         return 1
#
#
#     def setup(self, nSamples, nChannels, buffer_size = 4):
#
#         self.__powBuffer = collections.deque(numpy.zeros( buffer_size*nSamples,dtype=numpy.float),
#                                           maxlen = buffer_size*nSamples)
#
#         bufferList = []
#
#         for i in range(nChannels):
#             bufferByChannel = collections.deque(numpy.zeros( buffer_size*nSamples, dtype=numpy.complex) +  numpy.NAN,
#                                           maxlen = buffer_size*nSamples)
#
#             bufferList.append(bufferByChannel)
#
#         self.__nSamples = nSamples
#         self.__nChannels = nChannels
#         self.__bufferList = bufferList
#
#     def run(self, dataOut, channel = 0):
#
#         if not self.isConfig:
#             nSamples = dataOut.nHeights
#             nChannels = dataOut.nChannels
#             self.setup(nSamples, nChannels)
#             self.isConfig = True
#
#         #Append new data to internal buffer
#         for thisChannel in range(self.__nChannels):
#             bufferByChannel = self.__bufferList[thisChannel]
#             bufferByChannel.extend(dataOut.data[thisChannel])
#
#         if self.__pulseFound:
#             self.__startIndex -= self.__nSamples
#
#         #Finding Tx Pulse
#         if not self.__pulseFound:
#             indexFound = self.__findTxPulse(dataOut, channel)
#
#             if indexFound == None:
#                 dataOut.flagNoData = True
#                 return
#
#             self.__arrayBuffer = numpy.zeros((self.__nChannels, self.__newNSamples), dtype = numpy.complex)
#             self.__pulseFound = True
#             self.__startIndex = indexFound
#
#         #If pulse was found ...
#         for thisChannel in range(self.__nChannels):
#             bufferByChannel = self.__bufferList[thisChannel]
#             #print self.__startIndex
#             x = numpy.array(bufferByChannel)
#             self.__arrayBuffer[thisChannel] = x[self.__startIndex:self.__startIndex+self.__newNSamples]
#
#         deltaHeight = dataOut.heightList[1] - dataOut.heightList[0]
#         dataOut.heightList = numpy.arange(self.__newNSamples)*deltaHeight
# #             dataOut.ippSeconds = (self.__newNSamples / deltaHeight)/1e6
#
#         dataOut.data = self.__arrayBuffer
#
#         self.__startIndex += self.__newNSamples
#
#         return
