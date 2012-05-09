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
    
    dataInObj = None
    dataOutObj = None
        
    integratorObjIndex = None
    decoderObjIndex = None
    profSelectorObjIndex = None
    writerObjIndex = None
    plotterObjIndex = None
    
    integratorObjList = []
    decoderObjList = []
    profileSelectorObjList = []
    writerObjList = []
    plotterObjList = []
    m_Voltage= Voltage()

    m_ProfileSelector= ProfileSelector()

    m_Decoder= Decoder()

    m_CoherentIntegrator= CoherentIntegrator()

        
    def __init__(self, dataInObj, dataOutObj=None):
        '''
        Constructor
        '''
        
        self.dataInObj = dataInObj
        
        if dataOutObj == None:
            self.dataOutObj = Voltage()
        else:
            self.dataOutObj = dataOutObj
            
        self.integratorObjIndex = None
        self.decoderObjIndex = None
        self.profSelectorObjIndex = None
        self.writerObjIndex = None
        self.plotterObjIndex = None
        
        self.integratorObjList = []
        self.decoderObjList = []
        self.profileSelectorObjList = []
        self.writerObjList = []
        self.plotterObjList = []
    
    def init(self):
        
        self.integratorObjIndex = 0
        self.decoderObjIndex = 0
        self.profSelectorObjIndex = 0
        self.writerObjIndex = 0
        self.plotterObjIndex = 0
        self.dataOutObj.copy(self.dataInObj)
                
    def addWriter(self, wrpath):
        objWriter = VoltageWriter(self.dataOutObj)
        objWriter.setup(wrpath)
        self.writerObjList.append(objWriter)
           
    def addPlotter(self):
        
        plotObj = Osciloscope(self.dataOutObj,self.plotterObjIndex)
        self.plotterObjList.append(plotObj)

    def addIntegrator(self, nCohInt):
        
        objCohInt = CoherentIntegrator(nCohInt)
        self.integratorObjList.append(objCohInt)
    
    def addDecoder(self, code, ncode, nbaud):
        
        objDecoder = Decoder(code,ncode,nbaud)
        self.decoderObjList.append(objDecoder)
    
    def addProfileSelector(self, nProfiles):
        
        objProfSelector = ProfileSelector(nProfiles)
        self.profileSelectorObjList.append(objProfSelector)
        
    def writeData(self,wrpath):
        
        if self.dataOutObj.flagNoData:
            return 0
            
        if len(self.writerObjList) <= self.writerObjIndex:
            self.addWriter(wrpath)
        
        self.writerObjList[self.writerObjIndex].putData()
        
#        myWrObj = self.writerObjList[self.writerObjIndex]
#        myWrObj.putData()
        
        self.writerObjIndex += 1

    def plotData(self,idProfile, type, xmin=None, xmax=None, ymin=None, ymax=None, winTitle=''):
        if self.dataOutObj.flagNoData:
            return 0
            
        if len(self.plotterObjList) <= self.plotterObjIndex:
            self.addPlotter()
        
        self.plotterObjList[self.plotterObjIndex].plotData(type=type, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,winTitle=winTitle)
        
        self.plotterObjIndex += 1
    
    def integrator(self, N):
        
        if self.dataOutObj.flagNoData:
            return 0
        
        if len(self.integratorObjList) <= self.integratorObjIndex:
            self.addIntegrator(N)
        
        myCohIntObj = self.integratorObjList[self.integratorObjIndex]
        myCohIntObj.exe(self.dataOutObj.data)
        
        if myCohIntObj.flag:
            self.dataOutObj.data = myCohIntObj.data
            self.dataOutObj.m_ProcessingHeader.coherentInt *= N
            self.dataOutObj.flagNoData = False

        else:
            self.dataOutObj.flagNoData = True
        
        self.integratorObjIndex += 1
    
    def decoder(self,code=None,type = 0):
        
        if self.dataOutObj.flagNoData:
            return 0
        
        if code == None:
            code = self.dataOutObj.m_RadarControllerHeader.code
        ncode, nbaud = code.shape
        
        if len(self.decoderObjList) <= self.decoderObjIndex:
            self.addDecoder(code,ncode,nbaud)
        
        myDecodObj = self.decoderObjList[self.decoderObjIndex]
        myDecodObj.exe(data=self.dataOutObj.data,type=type)
        
        if myDecodObj.flag:
            self.dataOutObj.data = myDecodObj.data
            self.dataOutObj.flagNoData = False
        else:
            self.dataOutObj.flagNoData = True
        
        self.decoderObjIndex += 1

    
    def filterByHei(self, window):
        pass

    
    def selectChannels(self, channelList):
        """
        Selecciona un bloque de datos en base a canales y pares segun el channelList y el pairList
        
        Input:
            channelList    :    lista sencilla de canales a seleccionar por ej. [2,3,7] 
            
        Affected:
            self.dataOutObj.data
            self.dataOutObj.channelList
            self.dataOutObj.nChannels
            self.dataOutObj.m_ProcessingHeader.totalSpectra
            self.dataOutObj.m_SystemHeader.numChannels
            self.dataOutObj.m_ProcessingHeader.blockSize
            
        Return:
            None
        """
        if self.dataOutObj.flagNoData:
            return 0

        for channel in channelList:
            if channel not in self.dataOutObj.channelList:
                raise ValueError, "The value %d in channelList is not valid" %channel
        
        nchannels = len(channelList)
        profiles = self.dataOutObj.nProfiles
        heights  = self.dataOutObj.nHeights #m_ProcessingHeader.numHeights

        data = numpy.zeros( (nchannels,heights), dtype='complex' )
        for index,channel in enumerate(channelList):
            data[index,:] = self.dataOutObj.data[channel,:]
    
        self.dataOutObj.data = data
        self.dataOutObj.channelList = channelList
        self.dataOutObj.nChannels = nchannels
        self.dataOutObj.m_ProcessingHeader.totalSpectra = nchannels
        self.dataOutObj.m_SystemHeader.numChannels = nchannels
        self.dataOutObj.m_ProcessingHeader.blockSize = data.size
        return 1

    
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
            1 si el metodo se ejecuto con exito caso contrario devuelve 0
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
        return 1

    
    def selectHeightsByIndex(self, minIndex, maxIndex):
        """
        Selecciona un bloque de datos en base a un grupo indices de alturas segun el rango
        minIndex <= index <= maxIndex
        
        Input:
            minIndex    :    valor de indice minimo de altura a considerar 
            maxIndex    :    valor de indice maximo de altura a considerar
            
        Affected:
            self.dataOutObj.data
            self.dataOutObj.heightList 
            self.dataOutObj.nHeights
            self.dataOutObj.m_ProcessingHeader.blockSize
            self.dataOutObj.m_ProcessingHeader.numHeights
            self.dataOutObj.m_ProcessingHeader.firstHeight
            self.dataOutObj.m_RadarControllerHeader
            
        Return:
            1 si el metodo se ejecuto con exito caso contrario devuelve 0
        """
        if self.dataOutObj.flagNoData:
            return 0
        
        if (minIndex < 0) or (minIndex > maxIndex):
            raise ValueError, "some value in (%d,%d) is not valid" % (minIndex, maxIndex)
        
        if (maxIndex >= self.dataOutObj.nHeights):
            raise ValueError, "some value in (%d,%d) is not valid" % (minIndex, maxIndex)
        
        nHeights = maxIndex - minIndex + 1
        firstHeight = 0

        #voltage
        data = self.dataOutObj.data[:,minIndex:maxIndex+1]

        firstHeight = self.dataOutObj.heightList[minIndex]

        self.dataOutObj.data = data
        self.dataOutObj.heightList = self.dataOutObj.heightList[minIndex:maxIndex+1] 
        self.dataOutObj.nHeights = nHeights
        self.dataOutObj.m_ProcessingHeader.blockSize = data.size
        self.dataOutObj.m_ProcessingHeader.numHeights = nHeights
        self.dataOutObj.m_ProcessingHeader.firstHeight = firstHeight
        self.dataOutObj.m_RadarControllerHeader.numHeights = nHeights
        return 1
    
    
    def selectProfiles(self, minIndex, maxIndex, nProfiles):
        """
        Selecciona un bloque de datos en base a un grupo indices de perfiles segun el rango
        minIndex <= index <= maxIndex
        
        Input:
            minIndex    :    valor de indice minimo de perfil a considerar 
            maxIndex    :    valor de indice maximo de perfil a considerar
            nProfiles   :    numero de profiles
            
        Affected:
            self.dataOutObj.flagNoData
            self.profSelectorObjIndex
            
        Return:
            1 si el metodo se ejecuto con exito caso contrario devuelve 0
        """
        
        if self.dataOutObj.flagNoData:
            return 0
        
        if self.profSelectorObjIndex >= len(self.profileSelectorObjList):
            self.addProfileSelector(nProfiles)
        
        profileSelectorObj = self.profileSelectorObjList[self.profSelectorObjIndex]
        
        if profileSelectorObj.isProfileInRange(minIndex, maxIndex):
            self.dataOutObj.flagNoData = False
            self.profSelectorObjIndex += 1
            return 1
        
        self.dataOutObj.flagNoData = True
        self.profSelectorObjIndex += 1
        
        return 0
    
    def selectNtxs(self, ntx):
        pass


class Decoder:

    data = None
    profCounter = 1
    nCode = ncode 
    nBaud = nbaud
    codeIndex = 0
    code = code #this is a List
    fft_code = None 
    flag = False
    setCodeFft = False
    
    def __init__(self,code, ncode, nbaud):
        
        self.data = None
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
    
    profCounter = 1
    data = None
    buffer = None
    flag = False
    nCohInt = N
    
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

class ProfileSelector:
    
    indexProfile = None
    # Tamanho total de los perfiles
    nProfiles = None
    
    def __init__(self, nProfiles):
        
        self.indexProfile = 0
        self.nProfiles = nProfiles
    
    def isProfileInRange(self, minIndex, maxIndex):
        
        if self.indexProfile < minIndex:
            self.indexProfile += 1
            return False
        
        if self.indexProfile > maxIndex:
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
        
    
        