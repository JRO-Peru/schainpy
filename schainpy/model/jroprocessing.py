'''

$Author: dsuarez $
$Id: Processor.py 1 2012-11-12 18:56:07Z dsuarez $
'''
import os 
import numpy
import datetime
import time

from jrodata import *
from jrodataIO import *
from jroplot import *

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
        Operacion directa sobre la data (dataout.data). Es necesario actualizar los valores de los
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

    def init(self):
        
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
        data = self.dataOut.heightList
        
        for i,val in enumerate(data): 
            if val < minHei:
                continue
            else:
                minIndex = i;
                break
        
        for i,val in enumerate(data): 
            if val <= maxHei:
                maxIndex = i;
            else:
                break

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
    

class CohInt(Operation):
    
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
        
    def run(self, dataOut, n=None, timeInterval=None, overlapping=False):
        
        if not self.__isConfig:
            self.setup(n, timeInterval, overlapping)
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
            

class SpectraProc(ProcessingUnit):
    
    def __init__(self):
        
        self.objectDict = {}
        self.buffer = None
        self.firstdatatime = None
        self.profIndex = 0
        self.dataOut = Spectra()

    def __updateObjFromInput(self):
        
        self.dataOut.radarControllerHeaderObj = self.dataIn.radarControllerHeaderObj.copy()
        self.dataOut.systemHeaderObj = self.dataIn.systemHeaderObj.copy()
        self.dataOut.channelList = self.dataIn.channelList
        self.dataOut.heightList = self.dataIn.heightList
        self.dataOut.dtype = self.dataIn.dtype
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
        self.dataOut.flagShiftFFT = self.dataIn.flagShiftFFT
        self.dataOut.nCohInt = self.dataIn.nCohInt
        self.dataOut.nIncohInt = 1
        self.dataOut.ippSeconds = self.dataIn.ippSeconds
        
        self.dataOut.timeInterval = self.dataIn.timeInterval*self.dataOut.nFFTPoints*self.dataOut.nIncohInt
        
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
        fft_volt = numpy.fft.fft(self.buffer,axis=1)
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
                cspc[pairIndex,:,:] = numpy.abs(fft_volt[pair[0],:,:] * numpy.conjugate(fft_volt[pair[1],:,:]))
                pairIndex += 1
            blocksize += cspc.size
        
        self.dataOut.data_spc = spc
        self.dataOut.data_cspc = cspc
        self.dataOut.data_dc = dc
        self.dataOut.blockSize = blocksize
        
    def init(self, nFFTPoints=None, pairsList=None):
        
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
            
            self.dataOut.nFFTPoints = nFFTPoints
            self.dataOut.pairsList = pairsList
            self.dataOut.nPairs = nPairs
            
            if self.buffer == None:
                self.buffer = numpy.zeros((self.dataIn.nChannels,
                                           self.dataOut.nFFTPoints,
                                           self.dataIn.nHeights), 
                                           dtype='complex')

            
            self.buffer[:,self.profIndex,:] = self.dataIn.data
            self.profIndex += 1
            
            if self.firstdatatime == None:
                self.firstdatatime = self.dataIn.utctime
            
            if self.profIndex == self.dataOut.nFFTPoints:
                self.__updateObjFromInput()
                self.__getFft()
                
                self.dataOut.flagNoData = False
                
                self.buffer = None
                self.firstdatatime = None
                self.profIndex = 0
            
            return
        
        raise ValuError, "The type object %s is not valid"%(self.dataIn.type)
    
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
            self.__integrationtime = timeInterval * 60. #if (type(timeInterval)!=integer) -> change this line
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
        
        deltatime = datatime -self.__lastdatatime
        
        if not self.__withOverapping:
            self.__initime = datatime
        else:
            self.__initime += deltatime
            
        return avgdatatime, avgdata_spc, avgdata_cspc, avgdata_dc
        
    def run(self, dataOut, n=None, timeInterval=None, overlapping=False):
        
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
            dataOut.timeInterval = dataOut.ippSeconds * dataOut.nCohInt * dataOut.nIncohInt * dataOut.nFFTPoints
            dataOut.flagNoData = False
      