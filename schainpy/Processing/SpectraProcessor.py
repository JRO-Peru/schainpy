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
    
    def __init__(self, spectraInObj, spectraOutObj=None, npts = None):
        '''
        Constructor
        '''
        self.spectraInObj = spectraInObj        
        
        if spectraOutObj == None:
            self.spectraOutObj = Spectra()
        else:
            self.spectraOutObj = spectraOutObj

            
        self.integratorIndex = None
        self.decoderIndex = None
        self.writerIndex = None
        self.plotterIndex = None
        
        if npts != None:
            self.spectraOutObj.nPoints = npts
        
        self.npts = self.spectraOutObj.nPoints
        
        self.integratorList = []
        self.decoderList = []
        self.writerList = []
        self.plotterList = []
        
        self.buffer = None
        self.ptsId = 0
    
    def init(self):
        self.integratorIndex = 0
        self.decoderIndex = 0
        self.writerIndex = 0
        self.plotterIndex = 0
        
        if not( isinstance(self.spectraInObj, Spectra) ):
            self.getFft()
        else:
            self.spectraOutObj.copy(self.spectraInObj)
    
    
    def getFft(self):
        
        if self.buffer == None:
            nheis = self.spectraInObj.data.shape[1]
            nchannel = self.spectraInObj.data.shape[0]
            npoints = self.spectraOutObj.nPoints
            self.buffer = numpy.zeros((nchannel,npoints,nheis),dtype='complex') 
        
        self.buffer[:,self.ptsId,:] = self.spectraInObj.data 
        self.ptsId += 1
        self.spectraOutObj.flagNoData = True
        if self.ptsId >= self.spectraOutObj.nPoints:
            data_spc = numpy.fft.fft(self.buffer,axis=1)
            self.ptsId = 0  
            self.buffer = None
        
            #calculo de self-spectra
            self.spectraOutObj.data_spc = numpy.abs(data_spc * numpy.conjugate(data_spc))
            
            #calculo de cross-spectra
            #self.m_Spectra.data_cspc = self.__data_cspc
            
            #escribiendo dc
            #self.m_Spectra.data_dc = self.__data_dc
            
            self.spectraOutObj.flagNoData = False
        
        self.spectraOutObj.heights = self.spectraInObj.heights
        self.spectraOutObj.m_BasicHeader = self.spectraInObj.m_BasicHeader.copy()
        self.spectraOutObj.m_ProcessingHeader = self.spectraInObj.m_ProcessingHeader.copy()
        self.spectraOutObj.m_RadarControllerHeader = self.spectraInObj.m_RadarControllerHeader.copy()
        self.spectraOutObj.m_SystemHeader = self.spectraInObj.m_SystemHeader.copy()
    
    def addWriter(self,wrpath):
        objWriter = SpectraWriter(self.spectraOutObj)
        objWriter.setup(wrpath)
        self.writerList.append(objWriter)
        
    
    def addPlotter(self, index=None):
        
        if index==None:
            index = self.plotterIndex
        
        plotObj = Spectrum(self.spectraOutObj, index)
        self.plotterList.append(plotObj)

    
    def addIntegrator(self,N):
        
        objIncohInt = IncoherentIntegration(N)
        self.integratorList.append(objIncohInt)
    
    
    def writeData(self):
        if self.voltageOutObj.flagNoData:
                return 0
            
        if len(self.writerList) <= self.writerIndex:
            self.addWriter(wrpath)
        
        self.writerList[self.writerIndex].putData()
        
        self.writerIndex += 1
        
    def plotData(self,xmin=None, xmax=None, ymin=None, ymax=None, winTitle='', index=None):
        if self.spectraOutObj.flagNoData:
            return 0
        
        if len(self.plotterList) <= self.plotterIndex:
            self.addPlotter(index)
        
        self.plotterList[self.plotterIndex].plotData(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,winTitle=winTitle)
        
        self.plotterIndex += 1
        
    def integrator(self, N):
        if self.spectraOutObj.flagNoData:
                return 0
        
        if len(self.integratorList) <= self.integratorIndex:
            self.addIntegrator(N)
        
        myCohIntObj = self.integratorList[self.integratorIndex]
        myCohIntObj.exe(self.spectraOutObj.data_spc)
        
        if myCohIntObj.flag:
            self.spectraOutObj.data_spc = myCohIntObj.data
            self.spectraOutObj.m_ProcessingHeader.incoherentInt *= N
            self.spectraOutObj.flagNoData = False

        else:
            self.spectraOutObj.flagNoData = True
        
        self.integratorIndex += 1
        
class IncoherentIntegration:
    def __init__(self, N):
        self.profCounter = 1
        self.data = None
        self.buffer = None
        self.flag = False
        self.nIncohInt = N
            
    def exe(self,data):
        print 'intg:', self.profCounter

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

