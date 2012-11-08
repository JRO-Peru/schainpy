'''

$Author$
$Id$
'''

import os 
import sys
import numpy
import datetime
import time

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from Data.JROData import Voltage
from IO.VoltageIO import VoltageWriter
from Graphics.schainPlotTypes import ScopeFigure, RTIFigure

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
        self.plotObjIndex = None
        self.integratorObjList = []
        self.writerObjList = []
        self.plotObjList = []

    def setup(self,dataInObj=None,dataOutObj=None):
        self.dataInObj = dataInObj

        if self.dataOutObj == None:
            dataOutObj = Voltage()

        self.dataOutObj = dataOutObj

        return self.dataOutObj

    def init(self):
        self.integratorObjIndex = 0
        self.writerObjIndex = 0
        self.plotObjIndex = 0
        
        if not(self.dataInObj.flagNoData):
            self.dataOutObj.copy(self.dataInObj)
        # No necesita copiar en cada init() los atributos de dataInObj
        # la copia deberia hacerse por cada nuevo bloque de datos

    def addRti(self, idfigure, nframes, wintitle, driver, colormap, colorbar, showprofile):
        rtiObj = RTIFigure(idfigure, nframes, wintitle, driver, colormap, colorbar, showprofile)
        self.plotObjList.append(rtiObj)

    def plotRti(self, idfigure=None,
                    starttime=None,
                    endtime=None,
                    rangemin=None,
                    rangemax=None,
                    minvalue=None,
                    maxvalue=None,
                    wintitle='',
                    driver='plplot',
                    colormap='br_green',
                    colorbar=True,
                    showprofile=False,
                    xrangestep=None,
                    save=False,
                    gpath=None):
        
        if self.dataOutObj.flagNoData:
            return 0
        
        nframes = len(self.dataOutObj.channelList)
        
        if len(self.plotObjList) <= self.plotObjIndex:
            self.addRti(idfigure, nframes, wintitle, driver, colormap, colorbar, showprofile)
            
        data = self.dataOutObj.data * numpy.conjugate(self.dataOutObj.data)
        data = 10*numpy.log10(data.real)
        
#        currenttime = self.dataOutObj.utctime
#        if timezone == "lt":
        currenttime = self.dataOutObj.utctime - time.timezone
        
        range = self.dataOutObj.heightList
        
        channelList = self.dataOutObj.channelList
        
        thisdatetime = datetime.datetime.fromtimestamp(self.dataOutObj.utctime)
        dateTime = "%s"%(thisdatetime.strftime("%d-%b-%Y %H:%M:%S"))
        date = "%s"%(thisdatetime.strftime("%d-%b-%Y"))
        
        figuretitle = "RTI Plot Radar Data" #+ date
        
        plotObj = self.plotObjList[self.plotObjIndex]
        
        cleardata = False
        
        plotObj.plotPcolor(data, 
                           currenttime, 
                           range, 
                           channelList, 
                           starttime, 
                           endtime, 
                           rangemin, 
                           rangemax,
                           minvalue, 
                           maxvalue, 
                           figuretitle, 
                           xrangestep,
                           save, 
                           gpath,
                           cleardata)
        
        self.plotObjIndex += 1

    def addScope(self, idfigure, nframes, wintitle, driver):
        if idfigure==None:
            idfigure = self.plotObjIndex
            
        scopeObj = ScopeFigure(idfigure, nframes, wintitle, driver)
        self.plotObjList.append(scopeObj)
    
    def plotScope(self,
                    idfigure=None,
                    minvalue=None,
                    maxvalue=None,
                    xmin=None,
                    xmax=None,
                    wintitle='',
                    driver='plplot',
                    save=False,
                    gpath=None,
                    titleList=None,
                    xlabelList=None,
                    ylabelList=None,
                    type="power"):
        
        if self.dataOutObj.flagNoData:
            return 0
        
        nframes = len(self.dataOutObj.channelList)
        
        if len(self.plotObjList) <= self.plotObjIndex:
            self.addScope(idfigure, nframes, wintitle, driver)
            
        
        if type=="power":
            data1D = self.dataOutObj.data * numpy.conjugate(self.dataOutObj.data)
            data1D = data1D.real
            
        if type =="iq":
            data1D = self.dataOutObj.data
        
        thisDatetime = datetime.datetime.fromtimestamp(self.dataOutObj.utctime)
        
        dateTime = "%s"%(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
        date = "%s"%(thisDatetime.strftime("%d-%b-%Y"))
        
        figureTitle = "Scope Plot Radar Data: " + date
        
        plotObj = self.plotObjList[self.plotObjIndex]
        
        plotObj.plot1DArray(data1D, 
                             self.dataOutObj.heightList, 
                             self.dataOutObj.channelList, 
                             xmin, 
                             xmax, 
                             minvalue, 
                             maxvalue,
                             figureTitle,
                             save, 
                             gpath)
                
        self.plotObjIndex += 1
    

    def addIntegrator(self, *args):
        objCohInt = CoherentIntegrator(*args)
        self.integratorObjList.append(objCohInt)

    def addWriter(self, *args):
        writerObj = VoltageWriter(self.dataOutObj)
        writerObj.setup(*args)
        self.writerObjList.append(writerObj)
        
    def writeData(self, wrpath, blocksPerFile, profilesPerBlock):
        
        if self.dataOutObj.flagNoData:
            return 0
            
        if len(self.writerObjList) <= self.writerObjIndex:
            self.addWriter(wrpath, blocksPerFile, profilesPerBlock)
        
        self.writerObjList[self.writerObjIndex].putData()
        
        self.writerObjIndex += 1
        
    def integrator(self, nCohInt=None, timeInterval=None, overlapping=False):
        
        if self.dataOutObj.flagNoData:
            return 0
        
        if len(self.integratorObjList) <= self.integratorObjIndex:
            self.addIntegrator(nCohInt, timeInterval, overlapping)

        myCohIntObj = self.integratorObjList[self.integratorObjIndex]
        myCohIntObj.exe(data = self.dataOutObj.data, datatime=None)
        
        self.dataOutObj.flagNoData = True
        
        if myCohIntObj.isReady:
            self.dataOutObj.flagNoData = False
        


class CoherentIntegrator:
    
    
    __profIndex = 0
    __withOverapping  = False
    
    __isByTime = False
    __initime = None
    __integrationtime = None
    
    __buffer = None
    
    isReady = False
    nCohInt = None
    
    
    def __init__(self, nCohInt=None, timeInterval=None, overlapping=False):
        
        """
        Set the parameters of the integration class.
        
        Inputs:
        
            nCohInt        :    Number of coherent integrations
            timeInterval   :    Time of integration. If nCohInt is selected this parameter does not work
            overlapping    :    
            
        """
        
        self.__buffer = None
        self.isReady = False
        
        if nCohInt == None and timeInterval == None:
            raise ValueError, "nCohInt or timeInterval should be specified ..." 
        
        if nCohInt != None:
            self.nCohInt = nCohInt
            self.__isByTime = False
        else:
            self.__integrationtime = timeInterval * 60. #if (type(timeInterval)!=integer) -> change this line
            self.__isByTime = True
        
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
                             
        if self.__buffer == None:
            self.__buffer = data
            self.__profIndex += 1
            return
        
        if self.__profIndex < self.nCohInt:
            self.__buffer = numpy.vstack((self.__buffer, data))
            self.__profIndex += 1
            return
        
        self.__buffer = numpy.roll(self.__buffer, -1, axis=0)
        self.__buffer[self.nCohInt-1] = data
        #self.__profIndex = self.nCohInt
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
        
        #Overlapping data
        data = numpy.sum(self.__buffer, axis=0)
        nCohInt = self.__profIndex
        
        return data, nCohInt
    
    def byProfiles(self, data):
        
        self.isReady = False
        avg_data = None
        
        self.putData(data)
        
        if self.__profIndex == self.nCohInt:
            avg_data, nCohInt = self.pushData()
            self.isReady = True
        
        return avg_data    
    
    def byTime(self, data, datatime):
        
        self.isReady = False
        avg_data = None
        
        if self.__initime == None:
            self.__initime = datatime
        
        self.putData(data)
        
        if (datatime - self.__initime) >= self.__integrationtime:
            avg_data, nCohInt = self.pushData()
            self.nCohInt = nCohInt
            self.isReady = True
        
        return avg_data      
        
    def exe(self, data, datatime=None):
        
        if not self.__isByTime:
            avg_data = self.byProfiles(data)
        else:
            avg_data = self.byTime(data, datatime)
        
        self.data = avg_data
        
        return avg_data

    
