'''
Created on Feb 7, 2012

@author $Author$
@version $Id$
'''

import os, sys
import numpy

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from Model.Voltage import Voltage
from IO.VoltageIO import VoltageWriter
from Graphics.VoltagePlot import Osciloscope

class VoltageProcessor:
    '''
    classdocs
    '''

    def __init__(self, voltageInObj, voltageOutObj=None):
        '''
        Constructor
        '''
        
        self.voltageInObj = voltageInObj
        
        if voltageOutObj == None:
            self.voltageOutObj = Voltage()
        else:
            self.voltageOutObj = voltageOutObj
            
        self.integratorIndex = None
        self.decoderIndex = None
        self.profSelectorIndex = None
        self.writerIndex = None
        self.plotterIndex = None
        
        self.integratorList = []
        self.decoderList = []
        self.profileSelectorList = []
        self.writerList = []
        self.plotterList = []
    
    def init(self):
        
        self.integratorIndex = 0
        self.decoderIndex = 0
        self.profSelectorIndex = 0
        self.writerIndex = 0
        self.plotterIndex = 0
        self.voltageOutObj.copy(self.voltageInObj)
                
    def addWriter(self, wrpath):
        objWriter = VoltageWriter(self.voltageOutObj)
        objWriter.setup(wrpath)
        self.writerList.append(objWriter)
           
    def addPlotter(self):
        
        plotObj = Osciloscope(self.voltageOutObj,self.plotterIndex)
        self.plotterList.append(plotObj)

    def addIntegrator(self, nCohInt):
        
        objCohInt = CoherentIntegrator(nCohInt)
        self.integratorList.append(objCohInt)
    
    def addDecoder(self, code, ncode, nbaud):
        
        objDecoder = Decoder(code,ncode,nbaud)
        self.decoderList.append(objDecoder)
    
    def addProfileSelector(self, nProfiles):
        
        objProfSelector = ProfileSelector(nProfiles)
        self.profileSelectorList.append(objProfSelector)
        
    def writeData(self,wrpath):
        
        if self.voltageOutObj.flagNoData:
            return 0
            
        if len(self.writerList) <= self.writerIndex:
            self.addWriter(wrpath)
        
        self.writerList[self.writerIndex].putData()
        
#        myWrObj = self.writerList[self.writerIndex]
#        myWrObj.putData()
        
        self.writerIndex += 1

    def plotData(self,idProfile, type, xmin=None, xmax=None, ymin=None, ymax=None, winTitle=''):
        if self.voltageOutObj.flagNoData:
            return 0
            
        if len(self.plotterList) <= self.plotterIndex:
            self.addPlotter()
        
        self.plotterList[self.plotterIndex].plotData(type=type, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,winTitle=winTitle)
        
        self.plotterIndex += 1
    
    def integrator(self, N):
        
        if self.voltageOutObj.flagNoData:
            return 0
        
        if len(self.integratorList) <= self.integratorIndex:
            self.addIntegrator(N)
        
        myCohIntObj = self.integratorList[self.integratorIndex]
        myCohIntObj.exe(self.voltageOutObj.data)
        
        if myCohIntObj.flag:
            self.voltageOutObj.data = myCohIntObj.data
            self.voltageOutObj.m_ProcessingHeader.coherentInt *= N
            self.voltageOutObj.flagNoData = False

        else:
            self.voltageOutObj.flagNoData = True
        
        self.integratorIndex += 1
    
    def decoder(self,code=None,type = 0):
        
        if self.voltageOutObj.flagNoData:
            return 0
        
        if code == None:
            code = self.voltageOutObj.m_RadarControllerHeader.code
        ncode, nbaud = code.shape
        
        if len(self.decoderList) <= self.decoderIndex:
            self.addDecoder(code,ncode,nbaud)
        
        myDecodObj = self.decoderList[self.decoderIndex]
        myDecodObj.exe(data=self.voltageOutObj.data,type=type)
        
        if myDecodObj.flag:
            self.voltageOutObj.data = myDecodObj.data
            self.voltageOutObj.flagNoData = False
        else:
            self.voltageOutObj.flagNoData = True
        
        self.decoderIndex += 1

    
    def filterByHei(self, window):
        pass

    
    def selectChannels(self, channelList):
        """
        Selecciona un bloque de datos en base a canales y pares segun el channelList y el pairList
        
        Input:
            channelList    :    lista sencilla de canales a seleccionar por ej. (2,3,7) 
            pairList       :    tupla de pares que se desea selecionar por ej. ( (0,1), (0,2) )
            
        Affected:
            self.dataOutObj.datablock
            self.dataOutObj.nChannels
            self.dataOutObj.m_SystemHeader.numChannels
            self.voltageOutObj.m_ProcessingHeader.blockSize
            
        Return:
            None
        """
        if not(channelList):
            return
        
        channels = 0
        profiles = self.voltageOutObj.nProfiles
        heights  = self.voltageOutObj.m_ProcessingHeader.numHeights

        #self spectra
        channels = len(channelList)
        data = numpy.zeros( (channels,profiles,heights), dtype='complex' )
        for index,channel in enumerate(channelList):
            data[index,:,:] = self.voltageOutObj.data_spc[channel,:,:]
    
        self.voltageOutObj.datablock = data
        
        #fill the m_ProcessingHeader.spectraComb up            
        channels = len(channelList)

        self.voltageOutObj.channelList = channelList
        self.voltageOutObj.nChannels = nchannels
        self.voltageOutObj.m_ProcessingHeader.totalSpectra = nchannels
        self.voltageOutObj.m_SystemHeader.numChannels = nchannels
        self.voltageOutObj.m_ProcessingHeader.blockSize = data.size
        
    
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
            self.voltageOutObj.datablock
            self.voltageOutObj.m_ProcessingHeader.numHeights
            self.voltageOutObj.m_ProcessingHeader.blockSize
            self.voltageOutObj.heightList
            self.voltageOutObj.nHeights
            self.voltageOutObj.m_RadarControllerHeader.numHeights
            
        Return:
            None
        """
        channels = self.voltageOutObj.nChannels
        profiles = self.voltageOutObj.nProfiles
        newheis = maxIndex - minIndex + 1
        firstHeight = 0

        #voltage
        data = numpy.zeros( (channels,profiles,newheis), dtype='complex' )
        for i in range(channels):
            data[i] = self.voltageOutObj.data_spc[i,:,minIndex:maxIndex+1]

        self.voltageOutObj.datablock = data

        firstHeight = self.dataOutObj.heightList[minIndex]

        self.voltageOutObj.nHeights = newheis
        self.voltageOutObj.m_ProcessingHeader.blockSize = data.size
        self.voltageOutObj.m_ProcessingHeader.numHeights = newheis
        self.voltageOutObj.m_ProcessingHeader.firstHeight = firstHeight
        self.voltageOutObj.m_RadarControllerHeader = newheis

        xi = firstHeight
        step = self.voltageOutObj.m_ProcessingHeader.deltaHeight
        xf = xi + newheis * step
        self.voltageOutObj.heightList = numpy.arange(xi, xf, step) 
    
    
    def selectProfiles(self, minIndex, maxIndex, nProfiles):
        """
        Selecciona un bloque de datos en base a un grupo indices de alturas segun el rango
        minIndex <= index <= maxIndex
        
        Input:
            minIndex    :    valor minimo de altura a considerar 
            maxIndex    :    valor maximo de altura a considerar
            
        Affected:
            self.voltageOutObj.datablock
            self.voltageOutObj.m_ProcessingHeader.numHeights
            self.voltageOutObj.heightList
            
        Return:
            None
        """
        
        if self.voltageOutObj.flagNoData:
            return 0
        
        if self.profSelectorIndex >= len(self.profileSelectorList):
            self.addProfileSelector(nProfiles)
        
        profileSelectorObj = self.profileSelectorList[self.profSelectorIndex]
        
        if profileSelectorObj.isProfileInRange(minIndex, maxIndex):
            self.voltageOutObj.flagNoData = False
            self.profSelectorIndex += 1
            return 1
        
        self.voltageOutObj.flagNoData = True
        self.profSelectorIndex += 1
        
        return 0
    
    def selectNtxs(self, ntx):
        pass


class Decoder:
    
    def __init__(self,code, ncode, nbaud):
        
        self.buffer = None
        self.profCounter = 1
        self.nCode = ncode 
        self.nBaud = nbaud
        self.codeIndex = 0
        self.code = code #this is a List
        self.fft_code = None 
        self.flag = False
        self.setCodeFft = False
            
    def exe(self, data, ndata=None, type = 0):
        
        if ndata == None: ndata = data.shape[1] 
        
        if type == 0:
            self.convolutionInFreq(data,ndata)
            
        if type == 1:
            self.convolutionInTime(data, ndata)
            
    def convolutionInFreq(self,data, ndata):
        
        newcode = numpy.zeros(ndata)    
        newcode[0:self.nBaud] = self.code[self.codeIndex]
        
        self.codeIndex += 1
        
        fft_data = numpy.fft.fft(data, axis=1)
        fft_code = numpy.conj(numpy.fft.fft(newcode))
        fft_code = fft_code.reshape(1,len(fft_code))
        
        conv = fft_data.copy()
        conv.fill(0)
        
        conv = fft_data*fft_code    #            This other way to calculate multiplication between bidimensional arrays
                                                    #            for i in range(ndata):
                                                    #                conv[i,:] = fft_data[i,:]*fft_code[i]
            
        self.data = numpy.fft.ifft(conv,axis=1)
        self.flag = True
        
        if self.profCounter == self.nCode:
            self.profCounter = 0
            self.codeIndex = 0            
            
        self.profCounter += 1
        
    def convolutionInTime(self, data, ndata):

        nchannel = data.shape[1]
        newcode = self.code[self.codeIndex]
        self.codeIndex += 1
        conv = data.copy()
        for i in range(nchannel):
            conv[i,:] = numpy.correlate(data[i,:], newcode, 'same')
            
        self.data = conv
        self.flag = True
        
        if self.profCounter == self.nCode:
            self.profCounter = 0
            self.codeIndex = 0            
            
        self.profCounter += 1

            
class CoherentIntegrator:
    
    def __init__(self, N):
        
        self.profCounter = 1
        self.data = None
        self.buffer = None
        self.flag = False
        self.nCohInt = N
        
    def exe(self, data):
        
        if self.buffer == None:
            self.buffer = data
        else:
            self.buffer = self.buffer + data
        
        if self.profCounter == self.nCohInt:
            self.data = self.buffer
            self.buffer = None
            self.profCounter = 0
            self.flag = True
        else:
            self.flag = False
            
        self.profCounter += 1

class ProfileSelector():
    
    indexProfile = None
    # Tamaño total de los perfiles
    nProfiles = None
    
    def __init__(self, nProfiles):
        
        self.indexProfile = 0
        self.nProfiles = nProfiles
    
    def isProfileInRange(self, minIndex, maxIndex):
        
        if minIndex < self.indexProfile:
            self.indexProfile += 1
            return False
        
        if maxIndex > self.indexProfile:
            self.indexProfile += 1
            return False
        
        self.indexProfile += 1
        
        return True
    
    def isProfileInList(self, profileList):
        
        if self.indexProfile not in profileList:
            self.indexProfile += 1
            return False
        
        self.indexProfile += 1
        
        return True
        
    
        