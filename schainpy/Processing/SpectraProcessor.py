'''
Created on Feb 7, 2012

@author $Author$
@version $Id$
'''
import os, sys
import numpy

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from Model.Spectra import Spectra
from IO.SpectraIO import SpectraWriter
from Graphics.SpectraPlot import Spectrum


class SpectraProcessor:
    '''
    classdocs
    '''
    
    dataInObj = None        
    
    dataOutObj = None
        
    integratorObjIndex = None
    
    decoderObjIndex = None
    
    writerObjIndex = None
    
    plotterObjIndex = None
    
    integratorObjList = []
    
    decoderObjList = []
    
    writerObjList = []
    
    plotterObjList = []
    
    buffer = None
    
    ptsId = 0
    
    nFFTPoints = None
    
    pairList = None

    
    def __init__(self, dataInObj=None, dataOutObj=None):
        '''
        Constructor
        '''
        self.dataInObj = dataInObj        
        
        if dataOutObj == None:
            self.dataOutObj = Spectra()
        else:
            self.dataOutObj = dataOutObj
            
        self.integratorObjIndex = None
        self.decoderObjIndex = None
        self.writerObjIndex = None
        self.plotterObjIndex = None
        
        self.integratorObjList = []
        self.decoderObjList = []
        self.writerObjList = []
        self.plotterObjList = []
        
        self.buffer = None
        self.ptsId = 0
    
    def setIO(self,inputObject, outputObject):
        
#        if not( isinstance(inputObject, Voltage) ):
#            print 'InputObject must be an instance from Voltage()'
#            sys.exit(0)
        
        if not( isinstance(outputObject, Spectra) ):
            print 'OutputObject must be an instance from Spectra()'
            sys.exit(0)
        
        self.dataInObj = inputObject
        self.dataOutObj = outputObject
        
    def setup(self,nFFTPoints=None, pairList=None):
        if nFFTPoints == None:
            nFFTPoints = self.dataOutObj.nFFTPoints
        
        self.nFFTPoints = nFFTPoints
        self.pairList = pairList
    
#    def init(self, nFFTPoints, pairList=None):
    def init(self):
        
        self.integratorObjIndex = 0
        self.decoderObjIndex = 0
        self.writerObjIndex = 0
        self.plotterObjIndex = 0
        
#        if nFFTPoints == None:
#            nFFTPoints = self.dataOutObj.nFFTPoints
#        
#        self.nFFTPoints = nFFTPoints
#        self.pairList = pairList
#            
        if not( isinstance(self.dataInObj, Spectra) ):
            self.__getFft()
        else:
            self.dataOutObj.copy(self.dataInObj)
    
    
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
            self.ptsId  
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
        
        blocksize = 0
        nFFTPoints = self.nFFTPoints
        nChannels, nheis = self.dataInObj.data.shape
        
        if self.buffer == None:
            self.buffer = numpy.zeros((nChannels, nFFTPoints, nheis), dtype='complex') 
        
        self.buffer[:,self.ptsId,:] = self.dataInObj.data 
        self.ptsId += 1
        
        if self.ptsId < self.nFFTPoints: 
            self.dataOutObj.flagNoData = True
            return
            
        fft_volt = numpy.fft.fft(self.buffer,axis=1)
        dc = fft_volt[:,0,:]
        
        #calculo de self-spectra
        fft_volt = numpy.fft.fftshift(fft_volt,axes=(1,))
        spc = numpy.abs(fft_volt * numpy.conjugate(fft_volt))
        
        blocksize += dc.size
        blocksize += spc.size
        
        cspc = None
        nPair = 0
        if self.pairList != None:
            #calculo de cross-spectra
            nPairs = len(self.pairList)
            cspc = numpy.zeros((nPairs, nFFTPoints, nheis), dtype='complex')
            for pair in self.pairList:
                cspc[nPair,:,:] = numpy.abs(fft_volt[pair[0],:,:] * numpy.conjugate(fft_volt[pair[1],:,:]))
                nPair += 1
            blocksize += cspc.size
        
        self.dataOutObj.data_spc = spc
        self.dataOutObj.data_cspc = cspc
        self.dataOutObj.data_dc = dc

        self.ptsId = 0  
        self.buffer = None
        self.dataOutObj.flagNoData = False
            
        self.dataOutObj.heightList = self.dataInObj.heightList
        self.dataOutObj.channelList = self.dataInObj.channelList
        self.dataOutObj.m_BasicHeader = self.dataInObj.m_BasicHeader.copy()
        self.dataOutObj.m_ProcessingHeader = self.dataInObj.m_ProcessingHeader.copy()
        self.dataOutObj.m_RadarControllerHeader = self.dataInObj.m_RadarControllerHeader.copy()
        self.dataOutObj.m_SystemHeader = self.dataInObj.m_SystemHeader.copy()
        
        self.dataOutObj.dataType = self.dataInObj.dataType
        self.dataOutObj.nPairs = nPair
        self.dataOutObj.nChannels = nChannels
        self.dataOutObj.nProfiles = nFFTPoints
        self.dataOutObj.nHeights = nheis
        self.dataOutObj.nFFTPoints = nFFTPoints
        #self.dataOutObj.data = None
        
        self.dataOutObj.m_SystemHeader.numChannels = nChannels
        self.dataOutObj.m_SystemHeader.nProfiles = nFFTPoints

        self.dataOutObj.m_ProcessingHeader.blockSize = blocksize
        self.dataOutObj.m_ProcessingHeader.totalSpectra = nChannels + nPair 
        self.dataOutObj.m_ProcessingHeader.profilesPerBlock = nFFTPoints
        self.dataOutObj.m_ProcessingHeader.numHeights = nheis
        self.dataOutObj.m_ProcessingHeader.shif_fft = True
        
        spectraComb = numpy.zeros( (nChannels+nPair)*2,numpy.dtype('u1'))
        k = 0
        for i in range( 0,nChannels*2,2 ):
            spectraComb[i]   = k 
            spectraComb[i+1] = k
            k += 1
        
        k *= 2

        if self.pairList != None:
            
            for pair in self.pairList:
                spectraComb[k]   = pair[0] 
                spectraComb[k+1] = pair[1]
                k += 2    
            
        self.dataOutObj.m_ProcessingHeader.spectraComb = spectraComb

        
    def addWriter(self,wrpath):
        objWriter = SpectraWriter(self.dataOutObj)
        objWriter.setup(wrpath)
        self.writerObjList.append(objWriter)
        
    
    def addPlotter(self, index=None):
        
        if index==None:
            index = self.plotterObjIndex
        
        plotObj = Spectrum(self.dataOutObj, index)
        self.plotterObjList.append(plotObj)

    
    def addIntegrator(self,N,timeInterval):
        
        objIncohInt = IncoherentIntegration(N,timeInterval)
        self.integratorObjList.append(objIncohInt)
    
    def writeData(self, wrpath):
        if self.dataOutObj.flagNoData:
                return 0
            
        if len(self.writerObjList) <= self.writerObjIndex:
            self.addWriter(wrpath)
        
        self.writerObjList[self.writerObjIndex].putData()
        
        self.writerObjIndex += 1
        
    def plotData(self,xmin=None, xmax=None, ymin=None, ymax=None, winTitle='', index=None):
        if self.dataOutObj.flagNoData:
            return 0
        
        if len(self.plotterObjList) <= self.plotterObjIndex:
            self.addPlotter(index)
        
        self.plotterObjList[self.plotterObjIndex].plotData(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,winTitle=winTitle)
        
        self.plotterObjIndex += 1
        
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
            self.dataOutObj.m_ProcessingHeader.incoherentInt *= myIncohIntObj.navg
            #print "myIncohIntObj.navg: ",myIncohIntObj.navg
            self.dataOutObj.flagNoData = False
            
        else:
            self.dataOutObj.flagNoData = True
        
        self.integratorObjIndex += 1
    
    def removeDC(self, type):
        
        if self.dataOutObj.flagNoData:
            return 0
        pass
    
    def removeInterference(self):
        
        if self.dataOutObj.flagNoData:
            return 0
        pass
    
    def removeSatellites(self):
        
        if self.dataOutObj.flagNoData:
            return 0
        pass
    
    def selectChannels(self, channelList, pairList=None):
        """
        Selecciona un bloque de datos en base a canales y pares segun el channelList y el pairList
        
        Input:
            channelList    :    lista sencilla de canales a seleccionar por ej. (2,3,7) 
            pairList       :    tupla de pares que se desea selecionar por ej. ( (0,1), (0,2) )
            
        Affected:
            self.dataOutObj.data_spc
            self.dataOutObj.data_cspc
            self.dataOutObj.data_dc
            self.dataOutObj.nChannels
            self.dataOutObj.nPairs
            self.dataOutObj.m_ProcessingHeader.spectraComb
            self.dataOutObj.m_SystemHeader.numChannels
            
        Return:
            None
        """
        
        if self.dataOutObj.flagNoData:
            return 0
        
        channelIndexList = []
        for channel in channelList:
            if channel in self.dataOutObj.channelList:
                index = self.dataOutObj.channelList.index(channel)
                channelIndexList.append(index)
                continue
            
            raise ValueError, "The value %d in channelList is not valid" %channel

        nProfiles = self.dataOutObj.nProfiles
        #dataType = self.dataOutObj.dataType
        nHeights  = self.dataOutObj.nHeights #m_ProcessingHeader.numHeights
        blocksize = 0

        #self spectra
        nChannels = len(channelIndexList)
        spc = numpy.zeros( (nChannels,nProfiles,nHeights), dtype='float' ) #dataType[0] )
        
        for index, channel in enumerate(channelIndexList):
            spc[index,:,:] = self.dataOutObj.data_spc[index,:,:]
        
        #DC channel
        dc = numpy.zeros( (nChannels,nHeights), dtype='complex' )
        for index, channel in enumerate(channelIndexList):
            dc[index,:] = self.dataOutObj.data_dc[channel,:]        
            
        blocksize += dc.size
        blocksize += spc.size
            
        nPairs = 0
        cspc = None
        
        if pairList == None:
            pairList = self.pairList

        if (pairList != None) and (self.dataOutObj.data_cspc != None):
            #cross spectra
            nPairs = len(pairList)
            cspc = numpy.zeros( (nPairs,nProfiles,nHeights), dtype='complex' )

            spectraComb = self.dataOutObj.m_ProcessingHeader.spectraComb
            totalSpectra = len(spectraComb)
            nchan = self.dataOutObj.nChannels 
            pairIndexList = []

            for pair in pairList: #busco el par en la lista de pares del Spectra Combinations
                for index in range(0,totalSpectra,2):
                    if pair[0] == spectraComb[index] and pair[1] == spectraComb[index+1]:
                        pairIndexList.append( index/2 - nchan )

            for index, pair in enumerate(pairIndexList):
                cspc[index,:,:] = self.dataOutObj.data_cspc[pair,:,:]
            blocksize += cspc.size
                
        else:
            pairList = self.pairList
            cspc = self.dataOutObj.data_cspc
            if cspc != None:
                blocksize += cspc.size
            
        spectraComb = numpy.zeros( (nChannels+nPairs)*2,numpy.dtype('u1'))
        i = 0
        for val in channelList:
            spectraComb[i]   = val 
            spectraComb[i+1] = val
            i += 2
        
        if pairList != None:
            for pair in pairList:
                spectraComb[i]   = pair[0] 
                spectraComb[i+1] = pair[1]
                i += 2
                
        self.dataOutObj.data_spc = spc
        self.dataOutObj.data_cspc = cspc
        self.dataOutObj.data_dc = dc
        self.dataOutObj.nChannels = nChannels 
        self.dataOutObj.nPairs = nPairs    

        self.dataOutObj.channelList = channelList

        self.dataOutObj.m_ProcessingHeader.spectraComb = spectraComb
        self.dataOutObj.m_ProcessingHeader.totalSpectra = nChannels + nPairs
        self.dataOutObj.m_SystemHeader.numChannels = nChannels
        self.dataOutObj.nChannels = nChannels
        self.dataOutObj.m_ProcessingHeader.blockSize = blocksize

    def selectHeightsByValue(self, minHei, maxHei):
        """
        Selecciona un bloque de datos en base a un grupo de valores de alturas segun el rango
        minHei <= height <= maxHei
        
        Input:
            minHei    :    valor minimo de altura a considerar 
            maxHei    :    valor maximo de altura a considerar
            
        Affected:
            Indirectamente son cambiados varios valores a travez del metodo selectHeightsByIndex
            
        Return:
            None
        """
        
        if self.dataOutObj.flagNoData:
            return 0
        
        if (minHei < self.dataOutObj.heightList[0]) or (minHei > maxHei):
            raise ValueError, "some value in (%d,%d) is not valid" % (minHei, maxHei)
        
        if (maxHei > self.dataOutObj.heightList[-1]):
            raise ValueError, "some value in (%d,%d) is not valid" % (minHei, maxHei)

        minIndex = 0
        maxIndex = 0
        data = self.dataOutObj.heightList
        
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
        
    def selectHeightsByIndex(self, minIndex, maxIndex):
        """
        Selecciona un bloque de datos en base a un grupo indices de alturas segun el rango
        minIndex <= index <= maxIndex
        
        Input:
            minIndex    :    valor minimo de altura a considerar 
            maxIndex    :    valor maximo de altura a considerar
            
        Affected:
            self.dataOutObj.data_spc
            self.dataOutObj.data_cspc
            self.dataOutObj.data_dc
            self.dataOutObj.heightList
            self.dataOutObj.nHeights
            self.dataOutObj.m_ProcessingHeader.numHeights
            self.dataOutObj.m_ProcessingHeader.blockSize
            self.dataOutObj.m_ProcessingHeader.firstHeight
            self.dataOutObj.m_RadarControllerHeader.numHeights
            
        Return:
            None
        """
        
        if self.dataOutObj.flagNoData:
            return 0
        
        if (minIndex < 0) or (minIndex > maxIndex):
            raise ValueError, "some value in (%d,%d) is not valid" % (minIndex, maxIndex)
        
        if (maxIndex >= self.dataOutObj.nHeights):
            raise ValueError, "some value in (%d,%d) is not valid" % (minIndex, maxIndex)
        
        nChannels = self.dataOutObj.nChannels
        nPairs = self.dataOutObj.nPairs
        nProfiles = self.dataOutObj.nProfiles
        dataType = self.dataOutObj.dataType
        nHeights = maxIndex - minIndex + 1
        blockSize = 0

        #self spectra
        spc = self.dataOutObj.data_spc[:,:,minIndex:maxIndex+1]
        blockSize += spc.size

        #cross spectra
        cspc = None
        if self.dataOutObj.data_cspc != None:
            cspc = self.dataOutObj.data_cspc[:,:,minIndex:maxIndex+1]
            blockSize += cspc.size

        #DC channel
        dc = self.dataOutObj.data_dc[:,minIndex:maxIndex+1]
        blockSize += dc.size

        self.dataOutObj.data_spc = spc
        if cspc != None: 
            self.dataOutObj.data_cspc = cspc
        self.dataOutObj.data_dc = dc

        firstHeight = self.dataOutObj.heightList[minIndex]
        
        self.dataOutObj.nHeights = nHeights
        self.dataOutObj.m_ProcessingHeader.blockSize = blockSize
        self.dataOutObj.m_ProcessingHeader.numHeights = nHeights
        self.dataOutObj.m_ProcessingHeader.firstHeight = firstHeight
        self.dataOutObj.m_RadarControllerHeader.numHeights = nHeights
        
        self.dataOutObj.heightList = self.dataOutObj.heightList[minIndex:maxIndex+1] 


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
            