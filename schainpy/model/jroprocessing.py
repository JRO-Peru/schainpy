'''

$Author: dsuarez $
$Id: Processor.py 1 2012-11-12 18:56:07Z dsuarez $
'''
import os 
import numpy
import datetime
import time
import math
from jrodata import *
from jrodataIO import *
from jroplot import *

try:
    import cfunctions
except:
    pass

class ProcessingUnit:
    
    """
    Esta es la clase base para el procesamiento de datos.
    
    Contiene el metodo "call" para llamar operaciones. Las operaciones pueden ser:
        - Metodos internos (callMethod)
        - Objetos del tipo Operation (callObject). Antes de ser llamados, estos objetos
          tienen que ser agreagados con el metodo "add".
    
    """
    # objeto de datos de entrada (Voltage, Spectra o Correlation)
    dataIn = None
    
    # objeto de datos de entrada (Voltage, Spectra o Correlation)
    dataOut = None
    
    
    objectDict = None
    
    def __init__(self):
        
        self.objectDict = {}
    
    def init(self):
        
        raise ValueError, "Not implemented"
    
    def addOperation(self, object, objId):
        
        """
        Agrega el objeto "object" a la lista de objetos "self.objectList" y retorna el
        identificador asociado a este objeto. 
        
        Input:
        
            object    :    objeto de la clase "Operation"
        
        Return:
            
            objId    :    identificador del objeto, necesario para ejecutar la operacion
        """
        
        self.objectDict[objId] = object
        
        return objId
    
    def operation(self, **kwargs):
        
        """
        Operacion directa sobre la data (dataOut.data). Es necesario actualizar los valores de los
        atributos del objeto dataOut
        
        Input:
        
            **kwargs    :    Diccionario de argumentos de la funcion a ejecutar
        """
        
        raise ValueError, "ImplementedError"
    
    def callMethod(self, name, **kwargs):
        
        """
        Ejecuta el metodo con el nombre "name" y con argumentos **kwargs de la propia clase.
        
        Input:
            name        :    nombre del metodo a ejecutar
            
            **kwargs     :    diccionario con los nombres y valores de la funcion a ejecutar.
        
        """
        if name != 'run':
            
            if name == 'init' and self.dataIn.isEmpty():
                self.dataOut.flagNoData = True
                return False
                
            if name != 'init' and self.dataOut.isEmpty():
                return False
        
        methodToCall = getattr(self, name)
        
        methodToCall(**kwargs)
        
        if name != 'run':
            return True
        
        if self.dataOut.isEmpty():
            return False
        
        return True
    
    def callObject(self, objId, **kwargs):
        
        """
        Ejecuta la operacion asociada al identificador del objeto "objId"
        
        Input:
            
            objId        :    identificador del objeto a ejecutar
            
            **kwargs    :    diccionario con los nombres y valores de la funcion a ejecutar.
        
        Return:
            
            None    
        """
        
        if self.dataOut.isEmpty():
            return False
        
        object = self.objectDict[objId]
        
        object.run(self.dataOut, **kwargs)
        
        return True
    
    def call(self, operationConf, **kwargs):
        
        """
        Return True si ejecuta la operacion "operationConf.name" con los
        argumentos "**kwargs". False si la operacion no se ha ejecutado.
        La operacion puede ser de dos tipos:
        
            1. Un metodo propio de esta clase:
                
                operation.type = "self"
            
            2. El metodo "run" de un objeto del tipo Operation o de un derivado de ella:
                operation.type = "other".
                
               Este objeto de tipo Operation debe de haber sido agregado antes con el metodo:
               "addOperation" e identificado con el operation.id
               
            
        con el id de la operacion.
        
        Input:
        
            Operation    :    Objeto del tipo operacion con los atributos: name, type y id.
            
        """
        
        if operationConf.type == 'self':
            sts = self.callMethod(operationConf.name, **kwargs)
        
        if operationConf.type == 'other':
            sts = self.callObject(operationConf.id, **kwargs)
        
        return sts 
    
    def setInput(self, dataIn):
        
        self.dataIn = dataIn
    
    def getOutput(self):
        
        return self.dataOut
        
class Operation():
    
    """
    Clase base para definir las operaciones adicionales que se pueden agregar a la clase ProcessingUnit
    y necesiten acumular informacion previa de los datos a procesar. De preferencia usar un buffer de
    acumulacion dentro de esta clase
    
    Ejemplo: Integraciones coherentes, necesita la informacion previa de los n perfiles anteriores (bufffer)
    
    """
    
    __buffer = None
    __isConfig = False
    
    def __init__(self):
        
        pass
    
    def run(self, dataIn, **kwargs):
        
        """
        Realiza las operaciones necesarias sobre la dataIn.data y actualiza los atributos del objeto dataIn.
        
        Input:
        
            dataIn    :    objeto del tipo JROData
        
        Return:
            
            None
        
        Affected:
            __buffer    :    buffer de recepcion de datos.
            
        """
        
        raise ValueError, "ImplementedError"

class VoltageProc(ProcessingUnit):
    
    
    def __init__(self):
        
        self.objectDict = {}
        self.dataOut = Voltage()
        self.flip = 1

    def __updateObjFromAmisrInput(self):
        
        self.dataOut.timeZone = self.dataIn.timeZone
        self.dataOut.dstFlag = self.dataIn.dstFlag
        self.dataOut.errorCount = self.dataIn.errorCount
        self.dataOut.useLocalTime = self.dataIn.useLocalTime
        
        self.dataOut.flagNoData = self.dataIn.flagNoData
        self.dataOut.data = self.dataIn.data
        self.dataOut.utctime = self.dataIn.utctime
        self.dataOut.channelList = self.dataIn.channelList
        self.dataOut.timeInterval = self.dataIn.timeInterval
        self.dataOut.heightList = self.dataIn.heightList
        self.dataOut.nProfiles = self.dataIn.nProfiles
        
        pass

    def init(self):
        
        
        if self.dataIn.type == 'AMISR':
            self.__updateObjFromAmisrInput()
        
        if self.dataIn.type == 'Voltage':
            self.dataOut.copy(self.dataIn) 
        # No necesita copiar en cada init() los atributos de dataIn
        # la copia deberia hacerse por cada nuevo bloque de datos
        
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
        
        nChannels = len(channelIndexList)
            
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
        
        nHeights = maxIndex - minIndex + 1

        #voltage
        data = self.dataOut.data[:,minIndex:maxIndex+1]

        firstHeight = self.dataOut.heightList[minIndex]

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
    
    __isConfig = False
    
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
        
        self.__isConfig = False
    
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
        n = None
            
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
        
        if not self.__isConfig:
            self.setup(**kwargs)
            self.__isConfig = True
                    
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
    
    __isConfig = False
    __profIndex = 0
    
    code = None
    
    nCode = None 
    nBaud = None
    
    def __init__(self):
        
        self.__isConfig = False
        
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
            
        
        if not self.__isConfig:
            
            self.setup(code, dataOut.data.shape)
            self.__isConfig = True
        
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



class SpectraProc(ProcessingUnit):
    
    def __init__(self):
        
        self.objectDict = {}
        self.buffer = None
        self.firstdatatime = None
        self.profIndex = 0
        self.dataOut = Spectra()

    def __updateObjFromInput(self):
        
        self.dataOut.timeZone = self.dataIn.timeZone
        self.dataOut.dstFlag = self.dataIn.dstFlag
        self.dataOut.errorCount = self.dataIn.errorCount
        self.dataOut.useLocalTime = self.dataIn.useLocalTime
        
        self.dataOut.radarControllerHeaderObj = self.dataIn.radarControllerHeaderObj.copy()
        self.dataOut.systemHeaderObj = self.dataIn.systemHeaderObj.copy()
        self.dataOut.channelList = self.dataIn.channelList
        self.dataOut.heightList = self.dataIn.heightList
        self.dataOut.dtype = numpy.dtype([('real','<f4'),('imag','<f4')])
#        self.dataOut.nHeights = self.dataIn.nHeights
#        self.dataOut.nChannels = self.dataIn.nChannels
        self.dataOut.nBaud = self.dataIn.nBaud
        self.dataOut.nCode = self.dataIn.nCode
        self.dataOut.code = self.dataIn.code
        self.dataOut.nProfiles = self.dataOut.nFFTPoints
#        self.dataOut.channelIndexList = self.dataIn.channelIndexList
        self.dataOut.flagTimeBlock = self.dataIn.flagTimeBlock
        self.dataOut.utctime = self.firstdatatime
        self.dataOut.flagDecodeData = self.dataIn.flagDecodeData #asumo q la data esta decodificada
        self.dataOut.flagDeflipData = self.dataIn.flagDeflipData #asumo q la data esta sin flip
#        self.dataOut.flagShiftFFT = self.dataIn.flagShiftFFT
        self.dataOut.nCohInt = self.dataIn.nCohInt
        self.dataOut.nIncohInt = 1
        self.dataOut.ippSeconds = self.dataIn.ippSeconds
        self.dataOut.windowOfFilter = self.dataIn.windowOfFilter
        
        self.dataOut.timeInterval = self.dataIn.timeInterval*self.dataOut.nFFTPoints*self.dataOut.nIncohInt
        self.dataOut.frequency = self.dataIn.frequency
        self.dataOut.realtime = self.dataIn.realtime
        
    def __getFft(self):
        """
        Convierte valores de Voltaje a Spectra
        
        Affected:
            self.dataOut.data_spc
            self.dataOut.data_cspc
            self.dataOut.data_dc
            self.dataOut.heightList
            self.profIndex  
            self.buffer
            self.dataOut.flagNoData
        """
        fft_volt = numpy.fft.fft(self.buffer,n=self.dataOut.nFFTPoints,axis=1)
        fft_volt = fft_volt.astype(numpy.dtype('complex'))
        dc = fft_volt[:,0,:]
        
        #calculo de self-spectra
        fft_volt = numpy.fft.fftshift(fft_volt,axes=(1,))
        spc = fft_volt * numpy.conjugate(fft_volt)
        spc = spc.real
        
        blocksize = 0
        blocksize += dc.size
        blocksize += spc.size
        
        cspc = None
        pairIndex = 0
        if self.dataOut.pairsList != None:
            #calculo de cross-spectra
            cspc = numpy.zeros((self.dataOut.nPairs, self.dataOut.nFFTPoints, self.dataOut.nHeights), dtype='complex')
            for pair in self.dataOut.pairsList:
                cspc[pairIndex,:,:] = fft_volt[pair[0],:,:] * numpy.conjugate(fft_volt[pair[1],:,:])
                pairIndex += 1
            blocksize += cspc.size
        
        self.dataOut.data_spc = spc
        self.dataOut.data_cspc = cspc
        self.dataOut.data_dc = dc
        self.dataOut.blockSize = blocksize
        self.dataOut.flagShiftFFT = False
        
    def init(self, nProfiles=None, nFFTPoints=None, pairsList=None, ippFactor=None):
        
        self.dataOut.flagNoData = True
        
        if self.dataIn.type == "Spectra":
            self.dataOut.copy(self.dataIn)
            return
        
        if self.dataIn.type == "Voltage":
            
            if nFFTPoints == None:
                raise ValueError, "This SpectraProc.init() need nFFTPoints input variable"
            
            if pairsList == None:
                nPairs = 0
            else:
                nPairs = len(pairsList)
            
            if ippFactor == None:
                ippFactor = 1
            self.dataOut.ippFactor = ippFactor
            
            self.dataOut.nFFTPoints = nFFTPoints
            self.dataOut.pairsList = pairsList
            self.dataOut.nPairs = nPairs
            
            if self.buffer == None:
                self.buffer = numpy.zeros((self.dataIn.nChannels,
                                           nProfiles,
                                           self.dataIn.nHeights), 
                                           dtype='complex')

            
            self.buffer[:,self.profIndex,:] = self.dataIn.data.copy()
            self.profIndex += 1
            
            if self.firstdatatime == None:
                self.firstdatatime = self.dataIn.utctime
            
            if self.profIndex == nProfiles:
                self.__updateObjFromInput()
                self.__getFft()
                
                self.dataOut.flagNoData = False
                
                self.buffer = None
                self.firstdatatime = None
                self.profIndex = 0
            
            return
        
        raise ValueError, "The type object %s is not valid"%(self.dataIn.type)
    
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
            self.dataOut.data_spc
            self.dataOut.channelIndexList
            self.dataOut.nChannels
            
        Return:
            None
        """

        for channelIndex in channelIndexList:
            if channelIndex not in self.dataOut.channelIndexList:
                print channelIndexList
                raise ValueError, "The value %d in channelIndexList is not valid" %channelIndex
        
        nChannels = len(channelIndexList)
            
        data_spc = self.dataOut.data_spc[channelIndexList,:]
        
        self.dataOut.data_spc = data_spc
        self.dataOut.channelList = [self.dataOut.channelList[i] for i in channelIndexList]
#        self.dataOut.nChannels = nChannels
        
        return 1

    def selectHeights(self, minHei, maxHei):
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

    def getBeaconSignal(self, tauindex = 0, channelindex = 0, hei_ref=None):
        newheis = numpy.where(self.dataOut.heightList>self.dataOut.radarControllerHeaderObj.Taus[tauindex])
        
        if hei_ref != None:
            newheis = numpy.where(self.dataOut.heightList>hei_ref)
            
        minIndex = min(newheis[0])
        maxIndex = max(newheis[0])
        data_spc = self.dataOut.data_spc[:,:,minIndex:maxIndex+1]
        heightList = self.dataOut.heightList[minIndex:maxIndex+1]
        
        # determina indices
        nheis = int(self.dataOut.radarControllerHeaderObj.txB/(self.dataOut.heightList[1]-self.dataOut.heightList[0]))
        avg_dB = 10*numpy.log10(numpy.sum(data_spc[channelindex,:,:],axis=0))
        beacon_dB = numpy.sort(avg_dB)[-nheis:]
        beacon_heiIndexList = []
        for val in avg_dB.tolist():
            if val >= beacon_dB[0]:
                beacon_heiIndexList.append(avg_dB.tolist().index(val))
        
        #data_spc = data_spc[:,:,beacon_heiIndexList]
        data_cspc = None
        if self.dataOut.data_cspc != None:
            data_cspc = self.dataOut.data_cspc[:,:,minIndex:maxIndex+1]
            #data_cspc = data_cspc[:,:,beacon_heiIndexList]
        
        data_dc = None
        if self.dataOut.data_dc != None:
            data_dc = self.dataOut.data_dc[:,minIndex:maxIndex+1]
            #data_dc = data_dc[:,beacon_heiIndexList]
        
        self.dataOut.data_spc = data_spc
        self.dataOut.data_cspc = data_cspc
        self.dataOut.data_dc = data_dc
        self.dataOut.heightList = heightList
        self.dataOut.beacon_heiIndexList = beacon_heiIndexList
        
        return 1
        
    
    def selectHeightsByIndex(self, minIndex, maxIndex):
        """
        Selecciona un bloque de datos en base a un grupo indices de alturas segun el rango
        minIndex <= index <= maxIndex
        
        Input:
            minIndex    :    valor de indice minimo de altura a considerar 
            maxIndex    :    valor de indice maximo de altura a considerar
            
        Affected:
            self.dataOut.data_spc
            self.dataOut.data_cspc
            self.dataOut.data_dc
            self.dataOut.heightList
            
        Return:
            1 si el metodo se ejecuto con exito caso contrario devuelve 0
        """
        
        if (minIndex < 0) or (minIndex > maxIndex):
            raise ValueError, "some value in (%d,%d) is not valid" % (minIndex, maxIndex)
        
        if (maxIndex >= self.dataOut.nHeights):
            maxIndex = self.dataOut.nHeights-1
#            raise ValueError, "some value in (%d,%d) is not valid" % (minIndex, maxIndex)
        
        nHeights = maxIndex - minIndex + 1

        #Spectra
        data_spc = self.dataOut.data_spc[:,:,minIndex:maxIndex+1]
        
        data_cspc = None
        if self.dataOut.data_cspc != None:
            data_cspc = self.dataOut.data_cspc[:,:,minIndex:maxIndex+1]
        
        data_dc = None
        if self.dataOut.data_dc != None:
            data_dc = self.dataOut.data_dc[:,minIndex:maxIndex+1]
        
        self.dataOut.data_spc = data_spc
        self.dataOut.data_cspc = data_cspc
        self.dataOut.data_dc = data_dc
        
        self.dataOut.heightList = self.dataOut.heightList[minIndex:maxIndex+1]
        
        return 1
    
    def removeDC(self, mode = 2):
        jspectra = self.dataOut.data_spc
        jcspectra = self.dataOut.data_cspc
        
                
        num_chan = jspectra.shape[0]
        num_hei = jspectra.shape[2]
        
        if jcspectra != None:
            jcspectraExist = True
            num_pairs = jcspectra.shape[0]
        else:   jcspectraExist = False
             
        freq_dc = jspectra.shape[1]/2
        ind_vel = numpy.array([-2,-1,1,2]) + freq_dc 
        
        if ind_vel[0]<0:
            ind_vel[range(0,1)] = ind_vel[range(0,1)] + self.num_prof
        
        if mode == 1:         
            jspectra[:,freq_dc,:] = (jspectra[:,ind_vel[1],:] + jspectra[:,ind_vel[2],:])/2 #CORRECCION
                
            if jcspectraExist:
                jcspectra[:,freq_dc,:] = (jcspectra[:,ind_vel[1],:] + jcspectra[:,ind_vel[2],:])/2
        
        if mode == 2:
            
            vel = numpy.array([-2,-1,1,2])
            xx = numpy.zeros([4,4])
                
            for fil in range(4):
                xx[fil,:] = vel[fil]**numpy.asarray(range(4))
                    
            xx_inv = numpy.linalg.inv(xx)
            xx_aux = xx_inv[0,:]
                   
            for ich in range(num_chan):
                yy = jspectra[ich,ind_vel,:]
                jspectra[ich,freq_dc,:] = numpy.dot(xx_aux,yy)

                junkid = jspectra[ich,freq_dc,:]<=0
                cjunkid = sum(junkid)
            
                if cjunkid.any():
                    jspectra[ich,freq_dc,junkid.nonzero()] = (jspectra[ich,ind_vel[1],junkid] + jspectra[ich,ind_vel[2],junkid])/2
       
            if jcspectraExist:
                for ip in range(num_pairs):
                    yy = jcspectra[ip,ind_vel,:]
                    jcspectra[ip,freq_dc,:] = numpy.dot(xx_aux,yy)
        
        
        self.dataOut.data_spc = jspectra
        self.dataOut.data_cspc = jcspectra
        
        return 1
    
    def removeInterference(self,  interf = 2,hei_interf = None, nhei_interf = None, offhei_interf = None):
        
        jspectra = self.dataOut.data_spc
        jcspectra = self.dataOut.data_cspc
        jnoise = self.dataOut.getNoise()
        num_incoh = self.dataOut.nIncohInt
        
        num_channel  = jspectra.shape[0]
        num_prof  = jspectra.shape[1]
        num_hei   = jspectra.shape[2]
        
        #hei_interf
        if hei_interf == None:
            count_hei = num_hei/2   #Como es entero no importa
            hei_interf = numpy.asmatrix(range(count_hei)) + num_hei - count_hei
            hei_interf = numpy.asarray(hei_interf)[0]
        #nhei_interf    
        if (nhei_interf == None):
            nhei_interf = 5
        if (nhei_interf < 1):
            nhei_interf = 1        
        if (nhei_interf > count_hei):
            nhei_interf = count_hei
        if (offhei_interf == None):    
            offhei_interf = 0
            
        ind_hei = range(num_hei)
#         mask_prof = numpy.asarray(range(num_prof - 2)) + 1 
#         mask_prof[range(num_prof/2 - 1,len(mask_prof))] += 1
        mask_prof = numpy.asarray(range(num_prof)) 
        num_mask_prof = mask_prof.size
        comp_mask_prof = [0, num_prof/2]
       
         
        #noise_exist:    Determina si la variable jnoise ha sido definida y contiene la informacion del ruido de cada canal
        if (jnoise.size < num_channel or numpy.isnan(jnoise).any()):
            jnoise = numpy.nan
        noise_exist = jnoise[0] < numpy.Inf
         
        #Subrutina de Remocion de la Interferencia
        for ich in range(num_channel):
            #Se ordena los espectros segun su potencia (menor a mayor)
            power = jspectra[ich,mask_prof,:]
            power = power[:,hei_interf]
            power = power.sum(axis = 0)
            psort = power.ravel().argsort()
            
            #Se estima la interferencia promedio en los Espectros de Potencia empleando
            junkspc_interf = jspectra[ich,:,hei_interf[psort[range(offhei_interf, nhei_interf + offhei_interf)]]]
            
            if noise_exist:
            #    tmp_noise = jnoise[ich] / num_prof
                tmp_noise = jnoise[ich]
            junkspc_interf = junkspc_interf - tmp_noise
            #junkspc_interf[:,comp_mask_prof] = 0
            
            jspc_interf = junkspc_interf.sum(axis = 0) / nhei_interf
            jspc_interf = jspc_interf.transpose()
            #Calculando el espectro de interferencia promedio
            noiseid =  numpy.where(jspc_interf <= tmp_noise/ math.sqrt(num_incoh))
            noiseid = noiseid[0]
            cnoiseid = noiseid.size
            interfid = numpy.where(jspc_interf > tmp_noise/ math.sqrt(num_incoh))
            interfid = interfid[0]
            cinterfid = interfid.size
            
            if (cnoiseid > 0):   jspc_interf[noiseid] = 0
            
            #Expandiendo los perfiles a limpiar
            if (cinterfid > 0):
                new_interfid = (numpy.r_[interfid - 1, interfid, interfid + 1] + num_prof)%num_prof
                new_interfid = numpy.asarray(new_interfid)   
                new_interfid = {x for x in new_interfid}
                new_interfid = numpy.array(list(new_interfid))
                new_cinterfid = new_interfid.size
            else: new_cinterfid = 0
            
            for ip in range(new_cinterfid):
                ind = junkspc_interf[:,new_interfid[ip]].ravel().argsort()  
                jspc_interf[new_interfid[ip]] = junkspc_interf[ind[nhei_interf/2],new_interfid[ip]]
                
            
            jspectra[ich,:,ind_hei] = jspectra[ich,:,ind_hei] - jspc_interf #Corregir indices
            
            #Removiendo la interferencia del punto de mayor interferencia
            ListAux = jspc_interf[mask_prof].tolist()
            maxid = ListAux.index(max(ListAux))
            
            
            if cinterfid > 0:
                for ip in range(cinterfid*(interf == 2) - 1):
                    ind = (jspectra[ich,interfid[ip],:] < tmp_noise*(1 + 1/math.sqrt(num_incoh))).nonzero()
                    cind = len(ind)
                    
                    if (cind > 0):
                        jspectra[ich,interfid[ip],ind] = tmp_noise*(1 + (numpy.random.uniform(cind) - 0.5)/math.sqrt(num_incoh))
                    
                ind = numpy.array([-2,-1,1,2])
                xx = numpy.zeros([4,4])
                
                for id1 in range(4):
                    xx[:,id1] = ind[id1]**numpy.asarray(range(4))
                    
                xx_inv = numpy.linalg.inv(xx)
                xx = xx_inv[:,0]
                ind = (ind + maxid + num_mask_prof)%num_mask_prof
                yy = jspectra[ich,mask_prof[ind],:]
                jspectra[ich,mask_prof[maxid],:] = numpy.dot(yy.transpose(),xx)
                    
                    
            indAux = (jspectra[ich,:,:] < tmp_noise*(1-1/math.sqrt(num_incoh))).nonzero()         
            jspectra[ich,indAux[0],indAux[1]] = tmp_noise * (1 - 1/math.sqrt(num_incoh))
            
        #Remocion de Interferencia en el Cross Spectra
        if jcspectra == None: return jspectra, jcspectra
        num_pairs = jcspectra.size/(num_prof*num_hei)
        jcspectra = jcspectra.reshape(num_pairs, num_prof, num_hei)
        
        for ip in range(num_pairs):
            
            #-------------------------------------------
            
            cspower = numpy.abs(jcspectra[ip,mask_prof,:])
            cspower = cspower[:,hei_interf]
            cspower = cspower.sum(axis = 0)
            
            cspsort = cspower.ravel().argsort()
            junkcspc_interf = jcspectra[ip,:,hei_interf[cspsort[range(offhei_interf, nhei_interf + offhei_interf)]]]
            junkcspc_interf = junkcspc_interf.transpose()
            jcspc_interf = junkcspc_interf.sum(axis = 1)/nhei_interf
            
            ind = numpy.abs(jcspc_interf[mask_prof]).ravel().argsort()
            
            median_real = numpy.median(numpy.real(junkcspc_interf[mask_prof[ind[range(3*num_prof/4)]],:]))
            median_imag = numpy.median(numpy.imag(junkcspc_interf[mask_prof[ind[range(3*num_prof/4)]],:]))
            junkcspc_interf[comp_mask_prof,:] = numpy.complex(median_real, median_imag)
            
            for iprof in range(num_prof):
                ind = numpy.abs(junkcspc_interf[iprof,:]).ravel().argsort()
                jcspc_interf[iprof] = junkcspc_interf[iprof, ind[nhei_interf/2]]
            
            #Removiendo la Interferencia
            jcspectra[ip,:,ind_hei] = jcspectra[ip,:,ind_hei] - jcspc_interf
            
            ListAux = numpy.abs(jcspc_interf[mask_prof]).tolist()
            maxid = ListAux.index(max(ListAux))
            
            ind = numpy.array([-2,-1,1,2])
            xx = numpy.zeros([4,4])
                
            for id1 in range(4):
                xx[:,id1] = ind[id1]**numpy.asarray(range(4))
                    
            xx_inv = numpy.linalg.inv(xx)
            xx = xx_inv[:,0]
            
            ind = (ind + maxid + num_mask_prof)%num_mask_prof
            yy = jcspectra[ip,mask_prof[ind],:]
            jcspectra[ip,mask_prof[maxid],:] = numpy.dot(yy.transpose(),xx)
        
        #Guardar Resultados
        self.dataOut.data_spc = jspectra
        self.dataOut.data_cspc = jcspectra
            
        return 1
    
    def setRadarFrequency(self, frequency=None):
        if frequency != None:
            self.dataOut.frequency = frequency
        
        return 1
    
    def getNoise(self, minHei=None, maxHei=None, minVel=None, maxVel=None):        
        #validacion de rango
        if minHei == None:
            minHei = self.dataOut.heightList[0]
        
        if maxHei == None:
            maxHei = self.dataOut.heightList[-1]
            
        if (minHei < self.dataOut.heightList[0]) or (minHei > maxHei):
            print 'minHei: %.2f is out of the heights range'%(minHei)
            print 'minHei is setting to %.2f'%(self.dataOut.heightList[0])
            minHei = self.dataOut.heightList[0]
        
        if (maxHei > self.dataOut.heightList[-1]) or (maxHei < minHei):
            print 'maxHei: %.2f is out of the heights range'%(maxHei)
            print 'maxHei is setting to %.2f'%(self.dataOut.heightList[-1])
            maxHei = self.dataOut.heightList[-1]
        
        # validacion de velocidades
        velrange = self.dataOut.getVelRange(1)
        
        if minVel == None:
            minVel = velrange[0]
        
        if maxVel == None:
            maxVel = velrange[-1]
        
        if (minVel < velrange[0]) or (minVel > maxVel):
            print 'minVel: %.2f is out of the velocity range'%(minVel)
            print 'minVel is setting to %.2f'%(velrange[0])
            minVel = velrange[0]
        
        if (maxVel > velrange[-1]) or (maxVel < minVel):
            print 'maxVel: %.2f is out of the velocity range'%(maxVel)
            print 'maxVel is setting to %.2f'%(velrange[-1])
            maxVel = velrange[-1]
        
        # seleccion de indices para rango        
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

        if (minIndex < 0) or (minIndex > maxIndex):
            raise ValueError, "some value in (%d,%d) is not valid" % (minIndex, maxIndex)
        
        if (maxIndex >= self.dataOut.nHeights):
            maxIndex = self.dataOut.nHeights-1

        # seleccion de indices para velocidades
        indminvel = numpy.where(velrange >= minVel)
        indmaxvel = numpy.where(velrange <= maxVel)
        try:
            minIndexVel = indminvel[0][0]
        except:
            minIndexVel = 0
        
        try:
            maxIndexVel = indmaxvel[0][-1]
        except: 
            maxIndexVel = len(velrange)
        
        #seleccion del espectro
        data_spc = self.dataOut.data_spc[:,minIndexVel:maxIndexVel+1,minIndex:maxIndex+1]
        #estimacion de ruido
        noise = numpy.zeros(self.dataOut.nChannels)
        
        for channel in range(self.dataOut.nChannels):
            daux = data_spc[channel,:,:]
            noise[channel] = hildebrand_sekhon(daux, self.dataOut.nIncohInt)
        
        self.dataOut.noise = noise.copy()
        
        return 1

        
class IncohInt(Operation):
    
    
    __profIndex = 0
    __withOverapping  = False
    
    __byTime = False
    __initime = None
    __lastdatatime = None
    __integrationtime = None
    
    __buffer_spc = None
    __buffer_cspc = None
    __buffer_dc = None
    
    __dataReady = False
    
    __timeInterval = None
    
    n = None
    
    
    
    def __init__(self):
        
        self.__isConfig = False
    
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
        self.__buffer_spc = None
        self.__buffer_cspc = None
        self.__buffer_dc = None
        self.__dataReady = False
        
        
        if n == None and timeInterval == None:
            raise ValueError, "n or timeInterval should be specified ..." 
        
        if n != None:
            self.n = n
            self.__byTime = False
        else:
            self.__integrationtime = timeInterval #if (type(timeInterval)!=integer) -> change this line
            self.n = 9999
            self.__byTime = True
        
        if overlapping:
            self.__withOverapping = True
        else:
            self.__withOverapping = False
            self.__buffer_spc = 0
            self.__buffer_cspc = 0
            self.__buffer_dc = 0
        
        self.__profIndex = 0
    
    def putData(self, data_spc, data_cspc, data_dc):
        
        """
        Add a profile to the __buffer_spc and increase in one the __profileIndex
        
        """
            
        if not self.__withOverapping:
            self.__buffer_spc += data_spc
            
            if data_cspc == None:
                self.__buffer_cspc = None
            else:
                self.__buffer_cspc += data_cspc
            
            if data_dc == None:
                self.__buffer_dc = None
            else:
                self.__buffer_dc += data_dc
            
            self.__profIndex += 1            
            return
        
        #Overlapping data
        nChannels, nFFTPoints, nHeis = data_spc.shape
        data_spc = numpy.reshape(data_spc, (1, nChannels, nFFTPoints, nHeis))
        if data_cspc != None:
            data_cspc = numpy.reshape(data_cspc, (1, -1, nFFTPoints, nHeis))
        if data_dc != None:
            data_dc = numpy.reshape(data_dc, (1, -1, nHeis))
        
        #If the buffer is empty then it takes the data value
        if self.__buffer_spc == None:
            self.__buffer_spc = data_spc
            
            if data_cspc == None:
                self.__buffer_cspc = None
            else:
                self.__buffer_cspc += data_cspc
            
            if data_dc == None:
                self.__buffer_dc = None
            else:
                self.__buffer_dc += data_dc
                
            self.__profIndex += 1
            return
        
        #If the buffer length is lower than n then stakcing the data value
        if self.__profIndex < self.n:
            self.__buffer_spc = numpy.vstack((self.__buffer_spc, data_spc))
            
            if data_cspc != None:
                self.__buffer_cspc = numpy.vstack((self.__buffer_cspc, data_cspc))
            
            if data_dc != None: 
                self.__buffer_dc = numpy.vstack((self.__buffer_dc, data_dc))
                
            self.__profIndex += 1
            return
        
        #If the buffer length is equal to n then replacing the last buffer value with the data value 
        self.__buffer_spc = numpy.roll(self.__buffer_spc, -1, axis=0)
        self.__buffer_spc[self.n-1] = data_spc
        
        if data_cspc != None:
            self.__buffer_cspc = numpy.roll(self.__buffer_cspc, -1, axis=0)
            self.__buffer_cspc[self.n-1] = data_cspc
        
        if data_dc != None:
            self.__buffer_dc = numpy.roll(self.__buffer_dc, -1, axis=0)
            self.__buffer_dc[self.n-1] = data_dc
        
        self.__profIndex = self.n
        return
        
        
    def pushData(self):
        """
        Return the sum of the last profiles and the profiles used in the sum.
        
        Affected:
        
        self.__profileIndex
        
        """
        data_spc = None
        data_cspc  = None
        data_dc = None
        
        if not self.__withOverapping:
            data_spc = self.__buffer_spc
            data_cspc = self.__buffer_cspc
            data_dc = self.__buffer_dc
            
            n = self.__profIndex
        
            self.__buffer_spc = 0
            self.__buffer_cspc = 0
            self.__buffer_dc = 0
            self.__profIndex = 0
            
            return data_spc, data_cspc, data_dc, n
        
        #Integration with Overlapping
        data_spc = numpy.sum(self.__buffer_spc, axis=0)
        
        if self.__buffer_cspc != None:
            data_cspc = numpy.sum(self.__buffer_cspc, axis=0)
        
        if self.__buffer_dc != None:
            data_dc = numpy.sum(self.__buffer_dc, axis=0)
        
        n = self.__profIndex
        
        return data_spc, data_cspc, data_dc, n
    
    def byProfiles(self, *args):
        
        self.__dataReady = False
        avgdata_spc = None
        avgdata_cspc = None
        avgdata_dc = None
        n = None
            
        self.putData(*args)
        
        if self.__profIndex == self.n:
            
            avgdata_spc, avgdata_cspc, avgdata_dc, n = self.pushData()
            self.__dataReady = True
        
        return avgdata_spc, avgdata_cspc, avgdata_dc
    
    def byTime(self, datatime, *args):
        
        self.__dataReady = False
        avgdata_spc = None
        avgdata_cspc = None
        avgdata_dc = None
        n = None
        
        self.putData(*args)
        
        if (datatime - self.__initime) >= self.__integrationtime:
            avgdata_spc, avgdata_cspc, avgdata_dc, n = self.pushData()
            self.n = n
            self.__dataReady = True
        
        return avgdata_spc, avgdata_cspc, avgdata_dc
        
    def integrate(self, datatime, *args):
        
        if self.__initime == None:
            self.__initime = datatime
        
        if self.__byTime:
            avgdata_spc, avgdata_cspc, avgdata_dc = self.byTime(datatime, *args)
        else:
            avgdata_spc, avgdata_cspc, avgdata_dc = self.byProfiles(*args)
        
        self.__lastdatatime = datatime
        
        if avgdata_spc == None:
            return None, None, None, None
        
        avgdatatime = self.__initime
        try:
            self.__timeInterval = (self.__lastdatatime - self.__initime)/(self.n - 1)
        except:
            self.__timeInterval = self.__lastdatatime - self.__initime
            
        deltatime = datatime -self.__lastdatatime
        
        if not self.__withOverapping:
            self.__initime = datatime
        else:
            self.__initime += deltatime
            
        return avgdatatime, avgdata_spc, avgdata_cspc, avgdata_dc
        
    def run(self, dataOut, n=None, timeInterval=None, overlapping=False):
        
        if n==1:
            dataOut.flagNoData = False
            return
        
        if not self.__isConfig:
            self.setup(n, timeInterval, overlapping)
            self.__isConfig = True
                    
        avgdatatime, avgdata_spc, avgdata_cspc, avgdata_dc = self.integrate(dataOut.utctime,
                                                                            dataOut.data_spc,
                                                                            dataOut.data_cspc,
                                                                            dataOut.data_dc)
        
#        dataOut.timeInterval *= n
        dataOut.flagNoData = True
        
        if self.__dataReady:
            
            dataOut.data_spc = avgdata_spc
            dataOut.data_cspc = avgdata_cspc
            dataOut.data_dc = avgdata_dc
            
            dataOut.nIncohInt *= self.n
            dataOut.utctime = avgdatatime
            #dataOut.timeInterval = dataOut.ippSeconds * dataOut.nCohInt * dataOut.nIncohInt * dataOut.nFFTPoints
            dataOut.timeInterval = self.__timeInterval*self.n
            dataOut.flagNoData = False

class ProfileConcat(Operation):
    
    __isConfig = False
    buffer = None
    
    def __init__(self):
        
        self.profileIndex = 0
    
    def reset(self):
        self.buffer = numpy.zeros_like(self.buffer)
        self.start_index = 0
        self.times = 1
    
    def setup(self, data, m, n=1):
        self.buffer = numpy.zeros((data.shape[0],data.shape[1]*m),dtype=type(data[0,0]))
        self.profiles = data.shape[1]
        self.start_index = 0
        self.times = 1
    
    def concat(self, data):
        
        self.buffer[:,self.start_index:self.profiles*self.times] = data.copy()
        self.start_index = self.start_index + self.profiles 
        
    def run(self, dataOut, m):
        
        dataOut.flagNoData = True
        
        if not self.__isConfig:
            self.setup(dataOut.data, m, 1)
            self.__isConfig = True
        
        self.concat(dataOut.data)
        self.times += 1
        if self.times > m:
            dataOut.data = self.buffer
            self.reset()
            dataOut.flagNoData = False
            # se deben actualizar mas propiedades del header y del objeto dataOut, por ejemplo, las alturas
            deltaHeight = dataOut.heightList[1] - dataOut.heightList[0]  
            xf = dataOut.heightList[0] + dataOut.nHeights * deltaHeight * 5
            dataOut.heightList = numpy.arange(dataOut.heightList[0], xf, deltaHeight) 
        
        

class ProfileSelector(Operation):
    
    profileIndex = None
    # Tamanho total de los perfiles
    nProfiles = None
    
    def __init__(self):
        
        self.profileIndex = 0
    
    def incIndex(self):
        self.profileIndex += 1
        
        if self.profileIndex >= self.nProfiles:
            self.profileIndex = 0
    
    def isProfileInRange(self, minIndex, maxIndex):
        
        if self.profileIndex < minIndex:
            return False
        
        if self.profileIndex > maxIndex:
            return False
        
        return True
    
    def isProfileInList(self, profileList):
        
        if self.profileIndex not in profileList:
            return False
        
        return True
    
    def run(self, dataOut, profileList=None, profileRangeList=None):
        
        dataOut.flagNoData = True
        self.nProfiles = dataOut.nProfiles

        if profileList != None:
            if self.isProfileInList(profileList):
                dataOut.flagNoData = False
                
            self.incIndex()
            return 1

        
        elif profileRangeList != None:
            minIndex = profileRangeList[0]
            maxIndex = profileRangeList[1]
            if self.isProfileInRange(minIndex, maxIndex):
                dataOut.flagNoData = False
                
            self.incIndex()
            return 1
        
        else:
            raise ValueError, "ProfileSelector needs profileList or profileRangeList"
        
        return 0    

class SpectraHeisProc(ProcessingUnit):
    def __init__(self):
        self.objectDict = {}
#        self.buffer = None
#        self.firstdatatime = None
#        self.profIndex = 0
        self.dataOut = SpectraHeis()

    def __updateObjFromInput(self):
        self.dataOut.timeZone = self.dataIn.timeZone
        self.dataOut.dstFlag = self.dataIn.dstFlag
        self.dataOut.errorCount = self.dataIn.errorCount
        self.dataOut.useLocalTime = self.dataIn.useLocalTime
        
        self.dataOut.radarControllerHeaderObj = self.dataIn.radarControllerHeaderObj.copy()#
        self.dataOut.systemHeaderObj = self.dataIn.systemHeaderObj.copy()#
        self.dataOut.channelList = self.dataIn.channelList
        self.dataOut.heightList = self.dataIn.heightList
#        self.dataOut.dtype = self.dataIn.dtype
        self.dataOut.dtype = numpy.dtype([('real','<f4'),('imag','<f4')])
#        self.dataOut.nHeights = self.dataIn.nHeights
#        self.dataOut.nChannels = self.dataIn.nChannels
        self.dataOut.nBaud = self.dataIn.nBaud
        self.dataOut.nCode = self.dataIn.nCode
        self.dataOut.code = self.dataIn.code
#        self.dataOut.nProfiles = 1
#        self.dataOut.nProfiles = self.dataOut.nFFTPoints
        self.dataOut.nFFTPoints = self.dataIn.nHeights
#        self.dataOut.channelIndexList = self.dataIn.channelIndexList
#        self.dataOut.flagNoData = self.dataIn.flagNoData
        self.dataOut.flagTimeBlock = self.dataIn.flagTimeBlock
        self.dataOut.utctime = self.dataIn.utctime
#        self.dataOut.utctime = self.firstdatatime
        self.dataOut.flagDecodeData = self.dataIn.flagDecodeData #asumo q la data esta decodificada
        self.dataOut.flagDeflipData = self.dataIn.flagDeflipData #asumo q la data esta sin flip
#        self.dataOut.flagShiftFFT = self.dataIn.flagShiftFFT
        self.dataOut.nCohInt = self.dataIn.nCohInt
        self.dataOut.nIncohInt = 1
        self.dataOut.ippSeconds= self.dataIn.ippSeconds
        self.dataOut.windowOfFilter = self.dataIn.windowOfFilter
        
        self.dataOut.timeInterval = self.dataIn.timeInterval*self.dataOut.nIncohInt
#        self.dataOut.set=self.dataIn.set
#        self.dataOut.deltaHeight=self.dataIn.deltaHeight


    def __updateObjFromFits(self):
        self.dataOut.utctime = self.dataIn.utctime
        self.dataOut.channelIndexList = self.dataIn.channelIndexList
        
        self.dataOut.channelList = self.dataIn.channelList
        self.dataOut.heightList = self.dataIn.heightList
        self.dataOut.data_spc = self.dataIn.data
        self.dataOut.timeInterval = self.dataIn.timeInterval
        self.dataOut.timeZone = self.dataIn.timeZone
        self.dataOut.useLocalTime = True
#         self.dataOut.
#         self.dataOut.

    def __getFft(self):
           
        fft_volt = numpy.fft.fft(self.dataIn.data, axis=1)
        fft_volt = numpy.fft.fftshift(fft_volt,axes=(1,))
        spc = numpy.abs(fft_volt * numpy.conjugate(fft_volt))/(self.dataOut.nFFTPoints)
        self.dataOut.data_spc = spc

    def init(self):

        self.dataOut.flagNoData = True
        
        if self.dataIn.type == "Fits":
            self.__updateObjFromFits()
            self.dataOut.flagNoData = False
            return
        
        if self.dataIn.type == "SpectraHeis":
            self.dataOut.copy(self.dataIn)
            return
        
        if self.dataIn.type == "Voltage":
            self.__updateObjFromInput()
            self.__getFft()
            self.dataOut.flagNoData = False
                            
            return
        
        raise ValueError, "The type object %s is not valid"%(self.dataIn.type)
    
    
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
        
        nChannels = len(channelIndexList)
            
        data_spc = self.dataOut.data_spc[channelIndexList,:]
        
        self.dataOut.data_spc = data_spc
        self.dataOut.channelList = [self.dataOut.channelList[i] for i in channelIndexList]
        
        return 1

class IncohInt4SpectraHeis(Operation):
    
    __isConfig = False
    
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
        
        self.__isConfig = False
    
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
            self.__integrationtime = timeInterval #* 60. #if (type(timeInterval)!=integer) -> change this line
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
        n = None
            
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
        
        if not self.__isConfig:
            self.setup(**kwargs)
            self.__isConfig = True
                    
        avgdata, avgdatatime = self.integrate(dataOut.data_spc, dataOut.utctime)
        
#        dataOut.timeInterval *= n
        dataOut.flagNoData = True
        
        if self.__dataReady:
            dataOut.data_spc = avgdata
            dataOut.nIncohInt *= self.n
#            dataOut.nCohInt *= self.n
            dataOut.utctime = avgdatatime
            dataOut.timeInterval = dataOut.ippSeconds * dataOut.nIncohInt
#            dataOut.timeInterval = self.__timeInterval*self.n
            dataOut.flagNoData = False




            