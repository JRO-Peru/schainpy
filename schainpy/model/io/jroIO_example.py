'''
Created on Jul 3, 2014

@author: roj-idl71
'''

import os

from schainpy.model.data.jrodata import Voltage
from schainpy.model.proc.jroproc_base import ProcessingUnit, Operation

class Reader(ProcessingUnit):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
        ProcessingUnit.__init__(self)
        
        #Is really necessary create the output object in the initializer
        self.dataOut = Voltage()
    
    def fillJROHeader(*args):
        
        self.dataOut.radarControllerHeaderObj = RadarControllerHeader(ippKm=10e5,
                                                                      txA=0,
                                                                      txB=0,
                                                                      nWindows=1,
                                                                      nHeights=self.__nSamples,
                                                                      firstHeight=self.__firstHeigth,
                                                                      deltaHeight=self.__deltaHeigth,
                                                                      codeType=self.__codeType,
                                                                      nCode=self.__nCode, nBaud=self.__nBaud,
                                                                      code = self.__code)
        
        self.dataOut.systemHeaderObj = SystemHeader(nSamples=self.__nSamples,
                                                    nProfiles=nProfiles,
                                                    nChannels=len(self.__channelList),
                                                    adcResolution=14)
        
        self.dataOut.data = None
        
        self.dataOut.dtype = numpy.dtype([('real','<i8'),('imag','<i8')])
        
        self.dataOut.nProfiles = nProfiles
        
        self.dataOut.heightList = self.__firstHeigth + numpy.arange(self.__nSamples, dtype = numpy.float)*self.__deltaHeigth
        
        self.dataOut.channelList = self.__channelList
        
        self.dataOut.blocksize = self.dataOut.getNChannels() * self.dataOut.getNHeights()
        
#        self.dataOut.channelIndexList = None
        
        self.dataOut.flagNoData = True
        
        #Set to TRUE if the data is discontinuous 
        self.dataOut.flagDiscontinuousBlock = False
        
        self.dataOut.utctime = None
         
        self.dataOut.timeZone = self.__timezone/60  #timezone like jroheader, difference in minutes between UTC and localtime

        self.dataOut.dstFlag = 0
        
        self.dataOut.errorCount = 0
        
        self.dataOut.nCohInt = 1
        
        self.dataOut.flagDecodeData = False #asumo que la data esta decodificada
    
        self.dataOut.flagDeflipData = False #asumo que la data esta sin flip
        
        self.dataOut.flagShiftFFT = False
        
        self.dataOut.ippSeconds = 1.0*self.__nSamples/self.__sample_rate
        
        #Time interval between profiles 
        #self.dataOut.timeInterval = self.dataOut.ippSeconds * self.dataOut.nCohInt
        
        self.dataOut.frequency = self.__frequency
        
        self.dataOut.realtime = self.__online
        
    def setup(self, path = None,
                    startDate = None, 
                    endDate = None, 
                    startTime = None, 
                    endTime = None, 
                    set = None, 
                    expLabel = "", 
                    ext = None, 
                    online = False,
                    delay = 60,
                    walk = True):
        '''
        In this method we should set all initial parameters.
        
        '''
        
        '''
        Add code
        '''
        
        self.isConfig = True
        
        self.readUSRPHeader()
        self.fillJROHeader()
    
    def getData(self):
        
        pass
    
    def run(self, **kwargs):
        '''
        This method will be called many times so here you should put all your code
        '''
        
        if not self.isConfig:
            self.setup(**kwargs)
            
        self.getData()
        
        '''
        Add code
        '''
            
class Writer(Operation):
    '''
    classdocs
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        self.dataOut = None
        
        self.isConfig = False
    
    def setup(self, dataIn, path, blocksPerFile, set=0, ext=None):
        '''
        In this method we should set all initial parameters.
        
        Input:
            dataIn        :        Input data will also be outputa data
        
        '''
        self.dataOut = dataIn
        
        
        
        
        
        self.isConfig = True
        
        return
        
    def run(self, dataIn, **kwargs):
        '''
        This method will be called many times so here you should put all your code
        
        Inputs:
        
            dataIn        :        object with the data
            
        '''
        
        if not self.isConfig:
            self.setup(dataIn, **kwargs)
        