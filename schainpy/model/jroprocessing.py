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
        
        if self.dataIn.isEmpty():
            return None
        
        raise ValueError, "ImplementedError"
    
    def callMethod(self, name, **kwargs):
        
        """
        Ejecuta el metodo con el nombre "name" y con argumentos **kwargs de la propia clase.
        
        Input:
            name        :    nombre del metodo a ejecutar
            
            **kwargs     :    diccionario con los nombres y valores de la funcion a ejecutar.
        
        """
        
        if self.dataIn.isEmpty():
            return None
        
        methodToCall = getattr(self, name)
        
        methodToCall(**kwargs)
        
    def callObject(self, objId, **kwargs):
        
        """
        Ejecuta la operacion asociada al identificador del objeto "objId"
        
        Input:
            
            objId        :    identificador del objeto a ejecutar
            
            **kwargs    :    diccionario con los nombres y valores de la funcion a ejecutar.
        
        Return:
            
            None    
        """
        
        if self.dataIn.isEmpty():
            return None
        
        object = self.objectList[objId]
        
        object.run(self.dataOut, **kwargs)
    
    def call(self, operation, **kwargs):
        
        """
        Ejecuta la operacion "operation" con los argumentos "**kwargs". La operacion puede
        ser de dos tipos:
        
            1. Un metodo propio de esta clase:
                
                operation.type = "self"
            
            2. El metodo "run" de un objeto del tipo Operation o de un derivado de ella:
                operation.type = "other".
                
               Este objeto de tipo Operation debe de haber sido agregado antes con el metodo:
               "addOperation" e identificado con el operation.id
               
            
        con el id de la operacion.
        """
        if self.dataIn.isEmpty():
            return None
        
        if operation.type == 'self':
            self.callMethod(operation.name, **kwargs)
            return
        
        if operation.type == 'other':
            self.callObject(operation.id, **kwargs)
            return
        
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
        pass

    def setup(self, dataIn=None, dataOut=None):
        
        self.dataIn = dataIn

        if self.dataOut == None:
            dataOut = Voltage()

        self.dataOut = dataOut

        return self.dataOut

    def init(self):
        
        if self.dataIn.isEmpty():
            return 0
        
        self.dataOut.copy(self.dataIn)
        # No necesita copiar en cada init() los atributos de dataIn
        # la copia deberia hacerse por cada nuevo bloque de datos
        
    def selectChannels(self, channelList):
        
        if self.dataIn.isEmpty():
            return 0
        
        self.selectChannelsByIndex(channelList)
        
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

        for channel in channelIndexList:
            if channel not in self.dataOut.channelIndexList:
                raise ValueError, "The value %d in channelIndexList is not valid" %channel
        
        nChannels = len(channelIndexList)
            
        data = self.dataOut.data[channelIndexList,:]
        
        self.dataOut.data = data
        self.dataOut.channelIndexList = channelIndexList
        self.dataOut.channelList = [self.dataOut.channelList[i] for i in channelIndexList]
        self.dataOut.nChannels = nChannels
        
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
    
    nCohInt = None
    
    
    def __init__(self):
        
        self.__isConfig = False
    
    def setup(self, nCohInt=None, timeInterval=None, overlapping=False):
        """
        Set the parameters of the integration class.
        
        Inputs:
        
            nCohInt        :    Number of coherent integrations
            timeInterval   :    Time of integration. If the parameter "nCohInt" is selected this one does not work
            overlapping    :    
            
        """
        
        self.__initime = None
        self.__lastdatatime = 0
        self.__buffer = None
        self.__dataReady = False
        
        
        if nCohInt == None and timeInterval == None:
            raise ValueError, "nCohInt or timeInterval should be specified ..." 
        
        if nCohInt != None:
            self.nCohInt = nCohInt
            self.__byTime = False
        else:
            self.__integrationtime = timeInterval * 60. #if (type(timeInterval)!=integer) -> change this line
            self.nCohInt = 9999
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
            self.__buffer += data
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
        
        #If the buffer length is lower than nCohInt then stakcing the data value
        if self.__profIndex < self.nCohInt:
            self.__buffer = numpy.vstack((self.__buffer, data))
            self.__profIndex += 1
            return
        
        #If the buffer length is equal to nCohInt then replacing the last buffer value with the data value 
        self.__buffer = numpy.roll(self.__buffer, -1, axis=0)
        self.__buffer[self.nCohInt-1] = data
        self.__profIndex = self.nCohInt
        return
        
        
    def pushData(self):
        """
        Return the sum of the last profiles and the profiles used in the sum.
        
        Affected:
        
        self.__profileIndex
        
        """
        
        if not self.__withOverapping:
            data = self.__buffer
            nCohInt = self.__profIndex
        
            self.__buffer = 0
            self.__profIndex = 0
            
            return data, nCohInt
        
        #Integration with Overlapping
        data = numpy.sum(self.__buffer, axis=0)
        nCohInt = self.__profIndex
        
        return data, nCohInt
    
    def byProfiles(self, data):
        
        self.__dataReady = False
        avg_data = None
        nCohInt = None
            
        self.putData(data)
        
        if self.__profIndex == self.nCohInt:
            
            avgdata, nCohInt = self.pushData()
            self.__dataReady = True
        
        return avgdata, nCohInt
    
    def byTime(self, data, datatime):
        
        self.__dataReady = False
        avg_data = None
        nCohInt = None
        
        self.putData(data)
        
        if (datatime - self.__initime) >= self.__integrationtime:
            avgdata, nCohInt = self.pushData()
            self.nCohInt = nCohInt
            self.__dataReady = True
        
        return avgdata, nCohInt
        
    def integrate(self, data, datatime=None):
        
        if self.__initime == None:
            self.__initime = datatime
        
        if self.__byTime:
            avgdata = self.byTime(data, datatime)
        else:
            avgdata = self.byProfiles(data)
        
        
        self.__lastdatatime = datatime
        
        if avgdata == None:
            return None
        
        avgdatatime = self.__initime
        
        deltatime = datatime -self.__lastdatatime
        
        if not self.__withOverapping:
            self.__initime = datatime
        else:
            self.__initime += deltatime
            
        return avgdata, avgdatatime
        
    def run(self, dataOut, nCohInt=None, timeInterval=None, overlapping=False):
        
        if not self.__isConfig:
            self.setup(nCohInt, timeInterval, overlapping)
            self.__isConfig = True
                    
        avgdata, avgdatatime = self.integrate(dataOut.data, dataOut.utctime)
        
#        self.dataOut.timeInterval *= nCohInt
        self.dataOut.flagNoData = True
        
        if self.__dataReady:
            dataOut.data = avgdata
            dataOut.timeInterval *= self.nCohInt
            dataOut.nCohInt *= self.nCohInt
            dataOut.utctime = avgdatatime
            dataOut.flagNoData = False