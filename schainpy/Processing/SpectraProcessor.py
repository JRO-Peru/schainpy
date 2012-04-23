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
    
    def __init__(self, dataInObj, dataOutObj=None):
        '''
        Constructor
        '''
        self.dataInObj = dataInObj        
        
        if dataOutObj == None:
            self.dataOutObj = Spectra()
        else:
            self.dataOutObj = dataOutObj
            
        self.integratorIndex = None
        self.decoderIndex = None
        self.writerIndex = None
        self.plotterIndex = None
        
        self.integratorList = []
        self.decoderList = []
        self.writerList = []
        self.plotterList = []
        
        self.buffer = None
        self.ptsId = 0
    
    def init(self, nFFTPoints, pairList=None):
        
        self.integratorIndex = 0
        self.decoderIndex = 0
        self.writerIndex = 0
        self.plotterIndex = 0
        
        if nFFTPoints == None:
            nFFTPoints = self.dataOutObj.nPoints
        
        self.nFFTPoints = nFFTPoints
        self.pairList = pairList
            
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
        blocksize = 0
        npoints = self.nFFTPoints
        nchannels, nheis = self.dataInObj.data.shape
        
        if self.buffer == None:
            self.buffer = numpy.zeros((nchannels, npoints, nheis), dtype='complex') 
        
        self.buffer[:,self.ptsId,:] = self.dataInObj.data 
        self.ptsId += 1
        
        if self.ptsId < self.dataOutObj.nPoints:
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
        npair = 0
        if self.pairList != None:
            #calculo de cross-spectra
            npairs = len(self.pairList)
            cspc = numpy.zeros((npairs, npoints, nheis), dtype='complex')
            for pair in self.pairList:
                cspc[npair,:,:] = numpy.abs(fft_volt[pair[0],:,:] * numpy.conjugate(fft_volt[pair[1],:,:]))
                npair += 1
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
        self.dataOutObj.nPairs = npair
        self.dataOutObj.nChannels = nchannels
        self.dataOutObj.nProfiles = npoints
        self.dataOutObj.nHeights = nheis
        self.dataOutObj.nPoints = npoints
        #self.dataOutObj.data = None
        
        self.dataOutObj.m_SystemHeader.numChannels = nchannels
        self.dataOutObj.m_SystemHeader.nProfiles = npoints

        self.dataOutObj.m_ProcessingHeader.blockSize = blocksize
        self.dataOutObj.m_ProcessingHeader.totalSpectra = nchannels + npair 
        self.dataOutObj.m_ProcessingHeader.profilesPerBlock = npoints
        self.dataOutObj.m_ProcessingHeader.numHeights = nheis
        self.dataOutObj.m_ProcessingHeader.shif_fft = True
        
        spectraComb = numpy.zeros( (nchannels+npair)*2,numpy.dtype('u1'))
        k = 0
        for i in range( 0,nchannels*2,2 ):
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
        
        #self.selectHeightsByIndex( 0,10)
        #self.selectHeightsByValue( 120,200 )
        #self.selectChannels((2,4,5), self.pairList)

        
    def addWriter(self,wrpath):
        objWriter = SpectraWriter(self.dataOutObj)
        objWriter.setup(wrpath)
        self.writerList.append(objWriter)
        
    
    def addPlotter(self, index=None):
        
        if index==None:
            index = self.plotterIndex
        
        plotObj = Spectrum(self.dataOutObj, index)
        self.plotterList.append(plotObj)

    
    def addIntegrator(self,N):
        
        objIncohInt = IncoherentIntegration(N)
        self.integratorList.append(objIncohInt)
    
    
    def writeData(self, wrpath):
        if self.dataOutObj.flagNoData:
                return 0
            
        if len(self.writerList) <= self.writerIndex:
            self.addWriter(wrpath)
        
        self.writerList[self.writerIndex].putData()
        
        self.writerIndex += 1
        
    def plotData(self,xmin=None, xmax=None, ymin=None, ymax=None, winTitle='', index=None):
        if self.dataOutObj.flagNoData:
            return 0
        
        if len(self.plotterList) <= self.plotterIndex:
            self.addPlotter(index)
        
        self.plotterList[self.plotterIndex].plotData(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,winTitle=winTitle)
        
        self.plotterIndex += 1
        
    def integrator(self, N):
        if self.dataOutObj.flagNoData:
                return 0
        
        if len(self.integratorList) <= self.integratorIndex:
            self.addIntegrator(N)
        
        myCohIntObj = self.integratorList[self.integratorIndex]
        myCohIntObj.exe(self.dataOutObj.data_spc)
        
        if myCohIntObj.flag:
            self.dataOutObj.data_spc = myCohIntObj.data
            self.dataOutObj.m_ProcessingHeader.incoherentInt *= N
            self.dataOutObj.flagNoData = False

        else:
            self.dataOutObj.flagNoData = True
        
        self.integratorIndex += 1
    
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
        
        nchannels = 0
        npairs = 0
        profiles = self.dataOutObj.nProfiles
        dataType = self.dataOutObj.dataType
        heights  = self.dataOutObj.m_ProcessingHeader.numHeights
        blocksize = 0

        #self spectra
        nchannels = len(channelList)
        spc = numpy.zeros( (nchannels,profiles,heights), dataType[0] )
        
        for index, channel in enumerate(channelList):
            spc[index,:,:] = self.dataOutObj.data_spc[channel,:,:]
        
        #DC channel
        dc = numpy.zeros( (nchannels,heights), dtype='complex' )
        for index, channel in enumerate(channelList):
            dc[index,:] = self.dataOutObj.data_dc[channel,:]        
            
        blocksize += dc.size
        blocksize += spc.size
            
        npairs = 0
        cspc = None
        
        if pairList == None:
            pairList = self.pairList

        if pairList != None:
            #cross spectra
            npairs = len(pairList)
            cspc = numpy.zeros( (npairs,profiles,heights), dtype='complex' )

            spectraComb = self.dataOutObj.m_ProcessingHeader.spectraComb
            totalSpectra = len(spectraComb)
            nchan = self.dataOutObj.nChannels 
            indexList = []

            for pair in pairList: #busco el par en la lista de pares del Spectra Combinations
                for index in range(0,totalSpectra,2):
                    if pair[0] == spectraComb[index] and pair[1] == spectraComb[index+1]:
                        indexList.append( index/2 - nchan )

            for index, pair in enumerate(indexList):
                cspc[index,:,:] = self.dataOutObj.data_cspc[pair,:,:]
            blocksize += cspc.size
                
        else:
            pairList = self.pairList
            cspc = self.dataOutObj.data_cspc
            if cspc != None:
                blocksize += cspc.size
            
        spectraComb = numpy.zeros( (nchannels+npairs)*2,numpy.dtype('u1'))
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
        self.dataOutObj.nChannels = nchannels 
        self.dataOutObj.nPairs = npairs    

        self.dataOutObj.channelList = channelList

        self.dataOutObj.m_ProcessingHeader.spectraComb = spectraComb
        self.dataOutObj.m_ProcessingHeader.totalSpectra = nchannels + npairs
        self.dataOutObj.m_SystemHeader.numChannels = nchannels
        self.dataOutObj.nChannels = nchannels
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
        
        nchannels = self.dataOutObj.nChannels
        npairs = self.dataOutObj.nPairs
        profiles = self.dataOutObj.nProfiles
        dataType = self.dataOutObj.dataType
        newheis = maxIndex - minIndex + 1
        blockSize = 0

        #self spectra
        spc = numpy.zeros( (nchannels,profiles,newheis), dataType[0] )
        for i in range(nchannels):
            spc[i,:,:] = self.dataOutObj.data_spc[i,:,minIndex:maxIndex+1]

        #cross spectra
        cspc = numpy.zeros( (npairs,profiles,newheis), dtype='complex')
        for i in range(npairs):
            cspc[i,:,:] = self.dataOutObj.data_cspc[i,:,minIndex:maxIndex+1]

        #DC channel
        dc = numpy.zeros( (nchannels,newheis), dtype='complex')
        for i in range(nchannels):
            dc[i] = self.dataOutObj.data_dc[i,minIndex:maxIndex+1]

        self.dataOutObj.data_spc = spc
        self.dataOutObj.data_cspc = cspc
        self.dataOutObj.data_dc = dc

        firstHeight = self.dataOutObj.heightList[minIndex]
        
        self.dataOutObj.nHeights = newheis
        self.dataOutObj.m_ProcessingHeader.blockSize = spc.size + cspc.size + dc.size
        self.dataOutObj.m_ProcessingHeader.numHeights = newheis
        self.dataOutObj.m_ProcessingHeader.firstHeight = firstHeight
        self.dataOutObj.m_RadarControllerHeader.numHeights = newheis
        
        xi = firstHeight
        step = self.dataOutObj.m_ProcessingHeader.deltaHeight
        xf = xi + newheis * step
        self.dataOutObj.heightList = numpy.arange(xi, xf, step) 


class IncoherentIntegration:
    def __init__(self, N):
        self.profCounter = 1
        self.data = None
        self.buffer = None
        self.flag = False
        self.nIncohInt = N
            
    def exe(self,data):

        if self.buffer == None:
            self.buffer = data
        else:
            self.buffer = self.buffer + data
        
        if self.profCounter == self.nIncohInt:
            self.data = self.buffer
            self.buffer = None
            self.profCounter = 0
            self.flag = True
        else:
            self.flag = False
            
        self.profCounter += 1

