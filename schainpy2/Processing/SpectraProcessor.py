'''

$Author$
$Id$
'''

import os, sys
import numpy
import time

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from Data.JROData import Spectra
from IO.SpectraIO import SpectraWriter
#from Graphics.SpectraPlot import Spectrum
#from JRONoise import Noise

class SpectraProcessor:
    '''
    classdocs
    '''
    
    dataInObj = None        
    
    dataOutObj = None
        
    noiseObj = None
    
    integratorObjList = []
    
    writerObjList = []
    
    integratorObjIndex = None
    
    writerObjIndex = None
    
    profIndex = 0 # Se emplea cuando el objeto de entrada es un Voltage
    
#    integratorObjList = []
#    
#    decoderObjList = []
#    
#    writerObjList = []
#    
#    plotterObjList = []
#    
#    integratorObjIndex = None
#    
#    decoderObjIndex = None
#    
#    writerObjIndex = None
#    
#    plotterObjIndex = None
#    
#    buffer = None
#    
#    profIndex = 0
#    
#    nFFTPoints = None
#    
#    nChannels = None
#    
#    nHeights = None
#    
#    nPairs = None
#    
#    pairList = None

    
    def __init__(self):
        '''
        Constructor
        '''
        
        self.integratorObjIndex = None
        self.writerObjIndex = None
        self.integratorObjList = []
        self.writerObjList = []
        self.noiseObj = None
        self.buffer = None
        self.profIndex = 0
        
    def setup(self, dataInObj=None, dataOutObj=None, nFFTPoints=None, pairList=None):
        
        if dataInObj == None:
            raise ValueError, "This SpectraProcessor.setup() function needs dataInObj input variable"
        
        if dataInObj.type == "Voltage":
            if nFFTPoints == None:
                raise ValueError, "This SpectraProcessor.setup() function needs nFFTPoints input variable"
        else:
            nFFTPoints = dataInObj.nFFTPoints
        
        self.dataInObj = dataInObj        
        
        if dataOutObj == None:
            dataOutObj = Spectra()
            
        self.dataOutObj = dataOutObj
        
#        self.noiseObj = Noise() #aun no se incluye el objeto Noise()
        
        ##########################################
#        self.nFFTPoints = nFFTPoints
#        self.nChannels = self.dataInObj.nChannels
#        self.nHeights = self.dataInObj.nHeights
#        self.pairList = pairList
#        if pairList != None:
#            self.nPairs = len(pairList)
#        else:
#            self.nPairs = 0
#        
#        self.dataOutObj.heightList = self.dataInObj.heightList
#        self.dataOutObj.channelIndexList = self.dataInObj.channelIndexList
#        self.dataOutObj.m_BasicHeader = self.dataInObj.m_BasicHeader.copy()
#        self.dataOutObj.m_ProcessingHeader = self.dataInObj.m_ProcessingHeader.copy()
#        self.dataOutObj.m_RadarControllerHeader = self.dataInObj.m_RadarControllerHeader.copy()
#        self.dataOutObj.m_SystemHeader = self.dataInObj.m_SystemHeader.copy()
#        
#        self.dataOutObj.dataType = self.dataInObj.dataType
#        self.dataOutObj.nPairs = self.nPairs
#        self.dataOutObj.nChannels = self.nChannels
#        self.dataOutObj.nProfiles = self.nFFTPoints
#        self.dataOutObj.nHeights = self.nHeights
#        self.dataOutObj.nFFTPoints = self.nFFTPoints
#        #self.dataOutObj.data = None
#        
#        self.dataOutObj.m_SystemHeader.numChannels = self.nChannels
#        self.dataOutObj.m_SystemHeader.nProfiles = self.nFFTPoints
#        
#        self.dataOutObj.m_ProcessingHeader.totalSpectra = self.nChannels + self.nPairs 
#        self.dataOutObj.m_ProcessingHeader.profilesPerBlock = self.nFFTPoints
#        self.dataOutObj.m_ProcessingHeader.numHeights = self.nHeights
#        self.dataOutObj.m_ProcessingHeader.shif_fft = True
#        
#        spectraComb = numpy.zeros( (self.nChannels+self.nPairs)*2,numpy.dtype('u1'))
#        k = 0
#        for i in range( 0,self.nChannels*2,2 ):
#            spectraComb[i]   = k 
#            spectraComb[i+1] = k
#            k += 1
#        
#        k *= 2
#
#        if self.pairList != None:
#            
#            for pair in self.pairList:
#                spectraComb[k]   = pair[0] 
#                spectraComb[k+1] = pair[1]
#                k += 2    
#            
#        self.dataOutObj.m_ProcessingHeader.spectraComb = spectraComb
        
        return self.dataOutObj
    
    def init(self):
#        
#        self.nHeights = self.dataInObj.nHeights
#        self.dataOutObj.nHeights = self.nHeights
#        self.dataOutObj.heightList = self.dataInObj.heightList
#        
        
        self.integratorObjIndex = 0
        self.writerObjIndex = 0
        
        if self.dataInObj.type == "Voltage":
            
            if self.buffer == None:
                self.buffer = numpy.zeros((self.nChannels,
                                           self.nFFTPoints,
                                           self.dataInObj.nHeights), 
                                          dtype='complex')
            
            self.buffer[:,self.profIndex,:] = self.dataInObj.data
            self.profIndex += 1
            
            if self.profIndex == self.nFFTPoints:
                self.__getFft()
                self.dataOutObj.flagNoData = False
                
                self.buffer = None
                self.profIndex = 0
                return
            
            self.dataOutObj.flagNoData = True
            
            return
        
        #Other kind of data
        if self.dataInObj.type == "Spectra":
            self.dataOutObj.copy(self.dataInObj)
            self.dataOutObj.flagNoData = False
            return
        
        raise ValueError, "The datatype is not valid"

    def __getFft(self):
        """
        Convierte valores de Voltaje a Spectra
        
        Affected:
            self.dataOutObj.data_spc
            self.dataOutObj.data_cspc
            self.dataOutObj.data_dc
            self.dataOutObj.heightList
            self.dataOutObj.m_BasicHeader
            self.dataOutObj.m_ProcessingHeader
            self.dataOutObj.m_RadarControllerHeader
            self.dataOutObj.m_SystemHeader
            self.profIndex  
            self.buffer
            self.dataOutObj.flagNoData
            self.dataOutObj.dataType
            self.dataOutObj.nPairs
            self.dataOutObj.nChannels
            self.dataOutObj.nProfiles
            self.dataOutObj.m_SystemHeader.numChannels
            self.dataOutObj.m_ProcessingHeader.totalSpectra 
            self.dataOutObj.m_ProcessingHeader.profilesPerBlock
            self.dataOutObj.m_ProcessingHeader.numHeights
            self.dataOutObj.m_ProcessingHeader.spectraComb
            self.dataOutObj.m_ProcessingHeader.shif_fft
        """
        
        if self.dataInObj.flagNoData:
            return 0
            
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
        if self.pairList != None:
            #calculo de cross-spectra
            cspc = numpy.zeros((self.nPairs, self.nFFTPoints, self.nHeights), dtype='complex')
            for pair in self.pairList:
                cspc[pairIndex,:,:] = numpy.abs(fft_volt[pair[0],:,:] * numpy.conjugate(fft_volt[pair[1],:,:]))
                pairIndex += 1
            blocksize += cspc.size
        
        self.dataOutObj.data_spc = spc
        self.dataOutObj.data_cspc = cspc
        self.dataOutObj.data_dc = dc
        self.dataOutObj.m_ProcessingHeader.blockSize = blocksize
        self.dataOutObj.m_BasicHeader.utc = self.dataInObj.m_BasicHeader.utc
        
#        self.getNoise()
        
    def addWriter(self, wrpath, blocksPerFile):
        objWriter = SpectraWriter(self.dataOutObj)
        objWriter.setup(wrpath, blocksPerFile)
        self.writerObjList.append(objWriter)
                    
    def addIntegrator(self,N,timeInterval):
        
        objIncohInt = IncoherentIntegration(N,timeInterval)
        self.integratorObjList.append(objIncohInt)
    
    def writeData(self, wrpath, blocksPerFile):
        if self.dataOutObj.flagNoData:
                return 0
            
        if len(self.writerObjList) <= self.writerObjIndex:
            self.addWriter(wrpath, blocksPerFile)
        
        self.writerObjList[self.writerObjIndex].putData()
        
        self.writerObjIndex += 1
                
    def integrator(self, N=None, timeInterval=None):
        
        if self.dataOutObj.flagNoData:
                return 0
        
        if len(self.integratorObjList) <= self.integratorObjIndex:
            self.addIntegrator(N,timeInterval)
        
        myIncohIntObj = self.integratorObjList[self.integratorObjIndex]
        myIncohIntObj.exe(data=self.dataOutObj.data_spc,timeOfData=self.dataOutObj.m_BasicHeader.utc)
        
        if myIncohIntObj.isReady:
            self.dataOutObj.data_spc = myIncohIntObj.data
            self.dataOutObj.nAvg = myIncohIntObj.navg
            self.dataOutObj.m_ProcessingHeader.incoherentInt = self.dataInObj.m_ProcessingHeader.incoherentInt*myIncohIntObj.navg
            #print "myIncohIntObj.navg: ",myIncohIntObj.navg
            self.dataOutObj.flagNoData = False
            
            """Calcular el ruido"""
            self.getNoise()
        else:
            self.dataOutObj.flagNoData = True
        
        self.integratorObjIndex += 1
        
        
        

class IncoherentIntegration:

    integ_counter = None
    data = None
    navg = None
    buffer = None
    nIncohInt = None
    
    def __init__(self, N = None, timeInterval = None):
        """
        N 
        timeInterval - interval time [min], integer value
        """
        
        self.data = None
        self.navg = None
        self.buffer = None
        self.timeOut = None
        self.exitCondition = False
        self.isReady = False
        self.nIncohInt = N
        self.integ_counter = 0
        if timeInterval!=None:
            self.timeIntervalInSeconds = timeInterval * 60. #if (type(timeInterval)!=integer) -> change this line
        
        if ((timeInterval==None) and (N==None)):
             print 'N = None ; timeInterval = None'
             sys.exit(0)
        elif timeInterval == None:
            self.timeFlag = False
        else:
            self.timeFlag = True
            
            
    def exe(self,data,timeOfData):
        """
        data
        
        timeOfData [seconds]
        """

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
            if self.integ_counter < self.nIncohInt:
                if self.buffer == None:
                    self.buffer = data
                else:
                    self.buffer = self.buffer + data
            
                self.integ_counter += 1

            if self.integ_counter == self.nIncohInt:
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
            