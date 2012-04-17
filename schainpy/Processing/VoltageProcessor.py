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
        self.writerIndex = None
        self.plotterIndex = None
        
        self.integratorList = []
        self.decoderList = []
        self.writerList = []
        self.plotterList = []
    
    def init(self):
        self.integratorIndex = 0
        self.decoderIndex = 0
        self.writerIndex = 0
        self.plotterIndex = 0
        self.voltageOutObj.copy(self.voltageInObj)
                
    def addWriter(self,wrpath):
        objWriter = VoltageWriter(self.voltageOutObj)
        objWriter.setup(wrpath)
        self.writerList.append(objWriter)
           
    def addPlotter(self):
        
        plotObj = Osciloscope(self.voltageOutObj,self.plotterIndex)
        self.plotterList.append(plotObj)

    def addIntegrator(self,N):
        
        objCohInt = CoherentIntegrator(N)
        self.integratorList.append(objCohInt)
    
    def addDecoder(self,code,ncode,nbaud):
        
        objDecoder = Decoder(code,ncode,nbaud)
        self.decoderList.append(objDecoder)
    
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
    
    def removeDC(self):
        pass
    
    def removeSignalInt(self):
        pass
    
    def selChannel(self):
        pass
    
    def selRange(self):
        pass
    
    def selProfiles(self):
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
            
    def convolutionInFreq(self,data,ndata):
        
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
        
    def exe(self,data):
        
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


        