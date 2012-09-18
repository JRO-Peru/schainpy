import os 
import sys
import numpy

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from Data.Voltage import Voltage


class VoltageProcessor:
    dataInObj = None
    dataOutObj = None
    integratorObjIndex = None
    writerObjIndex = None
    integratorObjList = None
    writerObjList = None

    def __init__(self):
        self.integratorObjIndex = None
        self.writerObjIndex = None
        self.integratorObjList = []
        self.writerObjList = []

    def setup(self,dataInObj=None,dataOutObj=None):
        self.dataInObj = dataInObj

        if self.dataOutObj == None:
            dataOutObj = Voltage()

        self.dataOutObj = dataOutObj

        return self.dataOutObj

    def init(self):
        self.integratorObjIndex = 0
        self.writerObjIndex = 0
        # No necesita copiar en cada init() los atributos de dataInObj
        # la copia deberia hacerse por cada nuevo bloque de datos

    def addIntegrator(self,N,timeInterval):
        objCohInt = CoherentIntegrator(N,timeInterval)
        self.integratorObjList.append(objCohInt)

    def addWriter(self):
        pass

    def integrator(self, N=None, timeInterval=None):
        if self.dataOutObj.flagNoData:
            return 0
        if len(self.integratorObjList) <= self.integratorObjIndex:
            self.addIntegrator(N,timeInterval)

        myCohIntObj = self.integratorObjList[self.integratorObjIndex]
        myCohIntObj.exe(data=self.dataOutObj.data,timeOfData=None)
        
        pass

    def writeData(self):
        pass

class CoherentIntegrator:
    
    integ_counter = None
    data = None
    navg = None
    buffer = None
    nCohInt = None
    
    def __init__(self, N=None,timeInterval=None):
        
        self.data = None
        self.navg = None
        self.buffer = None
        self.timeOut = None
        self.exitCondition = False
        self.isReady = False
        self.nCohInt = N
        self.integ_counter = 0
        if timeInterval!=None:
            self.timeIntervalInSeconds = timeInterval * 60. #if (type(timeInterval)!=integer) -> change this line
        
        if ((timeInterval==None) and (N==None)):
            raise ValueError, "N = None ; timeInterval = None"
        
        if timeInterval == None:
            self.timeFlag = False
        else:
            self.timeFlag = True
        
    def exe(self, data, timeOfData):
        
        if self.timeFlag:
            if self.timeOut == None:
                self.timeOut = timeOfData + self.timeIntervalInSeconds
            
            if timeOfData < self.timeOut:
                if self.buffer == None:
                    self.buffer = data
                else:
                    self.buffer = self.buffer + data
                self.integ_counter += 1
            else:
                self.exitCondition = True
                
        else:
            if self.integ_counter < self.nCohInt:
                if self.buffer == None:
                    self.buffer = data
                else:
                    self.buffer = self.buffer + data
            
                self.integ_counter += 1

            if self.integ_counter == self.nCohInt:
                self.exitCondition = True
                
        if self.exitCondition:
            self.data = self.buffer
            self.navg = self.integ_counter
            self.isReady = True
            self.buffer = None
            self.timeOut = None
            self.integ_counter = 0
            self.exitCondition = False
            
            if self.timeFlag:
                self.buffer = data
                self.timeOut = timeOfData + self.timeIntervalInSeconds
        else:
            self.isReady = False

    
