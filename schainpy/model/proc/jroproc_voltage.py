import numpy

from jroproc_base import ProcessingUnit, Operation
from model.data.jrodata import Voltage

class VoltageProc(ProcessingUnit):
    
    
    def __init__(self):
        
        ProcessingUnit.__init__(self)
        
#         self.objectDict = {}
        self.dataOut = Voltage()
        self.flip = 1

    def run(self):
        self.dataOut.copy(self.dataIn)

#    def __updateObjFromAmisrInput(self):
#        
#        self.dataOut.timeZone = self.dataIn.timeZone
#        self.dataOut.dstFlag = self.dataIn.dstFlag
#        self.dataOut.errorCount = self.dataIn.errorCount
#        self.dataOut.useLocalTime = self.dataIn.useLocalTime
#        
#       self.dataOut.flagNoData = self.dataIn.flagNoData
#        self.dataOut.data = self.dataIn.data
#        self.dataOut.utctime = self.dataIn.utctime
#        self.dataOut.channelList = self.dataIn.channelList
#        self.dataOut.timeInterval = self.dataIn.timeInterval
#        self.dataOut.heightList = self.dataIn.heightList
#        self.dataOut.nProfiles = self.dataIn.nProfiles
#        
#        self.dataOut.nCohInt = self.dataIn.nCohInt
#        self.dataOut.ippSeconds = self.dataIn.ippSeconds
#        self.dataOut.frequency = self.dataIn.frequency
#        
#        pass#
#
#    def init(self):
#        
#        
#        if self.dataIn.type == 'AMISR':
#            self.__updateObjFromAmisrInput()
#        
#        if self.dataIn.type == 'Voltage':
#            self.dataOut.copy(self.dataIn) 
#        # No necesita copiar en cada init() los atributos de dataIn
#        # la copia deberia hacerse por cada nuevo bloque de datos
        
    def selectChannels(self, channelList):
        
        channelIndexList = []
        
        for channel in channelList:
            index = self.dataOut.channelList.index(channel)
            channelIndexList.append(index)
        
        self.selectChannelsByIndex(channelIndexList)
        
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
                print channelIndexList
                raise ValueError, "The value %d in channelIndexList is not valid" %channelIndex
        
#         nChannels = len(channelIndexList)
            
        data = self.dataOut.data[channelIndexList,:]
        
        self.dataOut.data = data
        self.dataOut.channelList = [self.dataOut.channelList[i] for i in channelIndexList]
#        self.dataOut.nChannels = nChannels
        
        return 1
    
    def selectHeights(self, minHei=None, maxHei=None):
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
        
        if minHei == None:
            minHei = self.dataOut.heightList[0]
            
        if maxHei == None:
            maxHei = self.dataOut.heightList[-1]
            
        if (minHei < self.dataOut.heightList[0]) or (minHei > maxHei):
            raise ValueError, "some value in (%d,%d) is not valid" % (minHei, maxHei)
        
        
        if (maxHei > self.dataOut.heightList[-1]):
            maxHei = self.dataOut.heightList[-1]
#            raise ValueError, "some value in (%d,%d) is not valid" % (minHei, maxHei)

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
        
        return 1

    
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
        
        if (minIndex < 0) or (minIndex > maxIndex):
            raise ValueError, "some value in (%d,%d) is not valid" % (minIndex, maxIndex)
        
        if (maxIndex >= self.dataOut.nHeights):
            maxIndex = self.dataOut.nHeights-1
#            raise ValueError, "some value in (%d,%d) is not valid" % (minIndex, maxIndex)
        
#         nHeights = maxIndex - minIndex + 1

        #voltage
        data = self.dataOut.data[:,minIndex:maxIndex+1]

#         firstHeight = self.dataOut.heightList[minIndex]

        self.dataOut.data = data
        self.dataOut.heightList = self.dataOut.heightList[minIndex:maxIndex+1]
        
        return 1
    
 
    def filterByHeights(self, window):
        deltaHeight = self.dataOut.heightList[1] - self.dataOut.heightList[0]
        
        if window == None:
            window = (self.dataOut.radarControllerHeaderObj.txA/self.dataOut.radarControllerHeaderObj.nBaud) / deltaHeight
        
        newdelta = deltaHeight * window
        r = self.dataOut.data.shape[1] % window
        buffer = self.dataOut.data[:,0:self.dataOut.data.shape[1]-r] 
        buffer = buffer.reshape(self.dataOut.data.shape[0],self.dataOut.data.shape[1]/window,window)
        buffer = numpy.sum(buffer,2)
        self.dataOut.data = buffer
        self.dataOut.heightList = numpy.arange(self.dataOut.heightList[0],newdelta*(self.dataOut.nHeights-r)/window,newdelta)
        self.dataOut.windowOfFilter = window

    def deFlip(self):
        self.dataOut.data *= self.flip
        self.flip *= -1.

    def setRadarFrequency(self, frequency=None):
        if frequency != None:
            self.dataOut.frequency = frequency
        
        return 1
    
class CohInt(Operation):
    
    isConfig = False
    
    __profIndex = 0
    __withOverapping  = False
    
    __byTime = False
    __initime = None
    __lastdatatime = None
    __integrationtime = None
    
    __buffer = None
    
    __dataReady = False
    
    n = None
    
    
    def __init__(self):
        
        Operation.__init__(self)
        
#         self.isConfig = False
    
    def setup(self, n=None, timeInterval=None, overlapping=False):
        """
        Set the parameters of the integration class.
        
        Inputs:
        
            n        :    Number of coherent integrations
            timeInterval   :    Time of integration. If the parameter "n" is selected this one does not work
            overlapping    :    
            
        """
        
        self.__initime = None
        self.__lastdatatime = 0
        self.__buffer = None
        self.__dataReady = False
        
        
        if n == None and timeInterval == None:
            raise ValueError, "n or timeInterval should be specified ..." 
        
        if n != None:
            self.n = n
            self.__byTime = False
        else:
            self.__integrationtime = timeInterval * 60. #if (type(timeInterval)!=integer) -> change this line
            self.n = 9999
            self.__byTime = True
        
        if overlapping:
            self.__withOverapping = True
            self.__buffer = None
        else:
            self.__withOverapping = False
            self.__buffer = 0
        
        self.__profIndex = 0
    
    def putData(self, data):
        
        """
        Add a profile to the __buffer and increase in one the __profileIndex
        
        """
            
        if not self.__withOverapping:
            self.__buffer += data.copy()
            self.__profIndex += 1            
            return
        
        #Overlapping data
        nChannels, nHeis = data.shape
        data = numpy.reshape(data, (1, nChannels, nHeis))
        
        #If the buffer is empty then it takes the data value
        if self.__buffer == None:
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
        
        if not self.__withOverapping:
            data = self.__buffer
            n = self.__profIndex
        
            self.__buffer = 0
            self.__profIndex = 0
            
            return data, n
        
        #Integration with Overlapping
        data = numpy.sum(self.__buffer, axis=0)
        n = self.__profIndex
        
        return data, n
    
    def byProfiles(self, data):
        
        self.__dataReady = False
        avgdata = None
#         n = None
            
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
        
    def integrate(self, data, datatime=None):
        
        if self.__initime == None:
            self.__initime = datatime
        
        if self.__byTime:
            avgdata = self.byTime(data, datatime)
        else:
            avgdata = self.byProfiles(data)
        
        
        self.__lastdatatime = datatime
        
        if avgdata == None:
            return None, None
        
        avgdatatime = self.__initime
        
        deltatime = datatime -self.__lastdatatime
        
        if not self.__withOverapping:
            self.__initime = datatime
        else:
            self.__initime += deltatime
            
        return avgdata, avgdatatime
        
    def run(self, dataOut, **kwargs):
        
        if not self.isConfig:
            self.setup(**kwargs)
            self.isConfig = True
                    
        avgdata, avgdatatime = self.integrate(dataOut.data, dataOut.utctime)
        
#        dataOut.timeInterval *= n
        dataOut.flagNoData = True
        
        if self.__dataReady:
            dataOut.data = avgdata
            dataOut.nCohInt *= self.n
            dataOut.utctime = avgdatatime
            dataOut.timeInterval = dataOut.ippSeconds * dataOut.nCohInt
            dataOut.flagNoData = False

class Decoder(Operation):
    
    isConfig = False
    __profIndex = 0
    
    code = None
    
    nCode = None 
    nBaud = None
    
    def __init__(self):
        
        Operation.__init__(self)
#         self.isConfig = False
        
    def setup(self, code, shape):
        
        self.__profIndex = 0
        
        self.code = code
        
        self.nCode = len(code) 
        self.nBaud = len(code[0])
        
        self.__nChannels, self.__nHeis = shape
        
        __codeBuffer = numpy.zeros((self.nCode, self.__nHeis), dtype=numpy.complex)
        
        __codeBuffer[:,0:self.nBaud] = self.code
        
        self.fft_code = numpy.conj(numpy.fft.fft(__codeBuffer, axis=1))
        
        self.ndatadec = self.__nHeis - self.nBaud + 1
        
        self.datadecTime = numpy.zeros((self.__nChannels, self.ndatadec), dtype=numpy.complex)
        
    def convolutionInFreq(self, data):
        
        fft_code = self.fft_code[self.__profIndex].reshape(1,-1)
        
        fft_data = numpy.fft.fft(data, axis=1)
        
        conv = fft_data*fft_code
        
        data = numpy.fft.ifft(conv,axis=1)
        
        datadec = data[:,:-self.nBaud+1]
        
        return datadec
        
    def convolutionInFreqOpt(self, data):
        
        fft_code = self.fft_code[self.__profIndex].reshape(1,-1)
        
        data = cfunctions.decoder(fft_code, data)
        
        datadec = data[:,:-self.nBaud+1]
        
        return datadec
    
    def convolutionInTime(self, data):
        
        code = self.code[self.__profIndex]
        
        for i in range(self.__nChannels):
            self.datadecTime[i,:] = numpy.correlate(data[i,:], code, mode='valid')
        
        return self.datadecTime
    
    def run(self, dataOut, code=None, nCode=None, nBaud=None, mode = 0):
        
        if code == None:
            code = dataOut.code
        else:
            code = numpy.array(code).reshape(nCode,nBaud)
            dataOut.code = code
            dataOut.nCode = nCode
            dataOut.nBaud = nBaud
            dataOut.radarControllerHeaderObj.code = code
            dataOut.radarControllerHeaderObj.nCode = nCode
            dataOut.radarControllerHeaderObj.nBaud = nBaud
            
        
        if not self.isConfig:
            
            self.setup(code, dataOut.data.shape)
            self.isConfig = True
        
        if mode == 0:
            datadec = self.convolutionInTime(dataOut.data)
            
        if mode == 1:
            datadec = self.convolutionInFreq(dataOut.data)
        
        if mode == 2:
            datadec = self.convolutionInFreqOpt(dataOut.data)
        
        dataOut.data = datadec
        
        dataOut.heightList = dataOut.heightList[0:self.ndatadec]
        
        dataOut.flagDecodeData = True #asumo q la data no esta decodificada

        if self.__profIndex == self.nCode-1: 
            self.__profIndex = 0             
            return 1
        
        self.__profIndex += 1
        
        return 1
#        dataOut.flagDeflipData = True #asumo q la data no esta sin flip
