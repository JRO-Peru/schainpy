'''

$Author$
$Id$
'''

import os, sys
import copy
import numpy

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from IO.JROHeaderIO import SystemHeader, RadarControllerHeader

class JROData:
    
#    m_BasicHeader = BasicHeader()
#    m_ProcessingHeader = ProcessingHeader()

    systemHeaderObj = SystemHeader()
    
    radarControllerHeaderObj = RadarControllerHeader()

#    data = None
    
    type = None
    
    dtype = None
    
    nChannels = None
    
    nHeights = None
    
    nProfiles = None
    
    heightList = None
    
    channelList = None
    
    channelIndexList = None
    
    flagNoData = False
    
    flagTimeBlock = False
    
    dataUtcTime = None
    
    nCode = None
    
    nBaud = None
    
    code = None
    
    flagDecodeData = True #asumo q la data esta decodificada
    
    flagDeflipData = True #asumo q la data esta sin flip
    
    flagShiftFFT = False
    
    ippSeconds = None
    

    def __init__(self):
        
        raise ValueError, "This class has not been implemented"
        
    def copy(self, inputObj=None):
        
        if inputObj == None:
            return copy.deepcopy(self)

        for key in inputObj.__dict__.keys():
            self.__dict__[key] = inputObj.__dict__[key]

    def deepcopy(self):
        
        return copy.deepcopy(self)
    
class Voltage(JROData):
    
    nCohInt = None
    
    #data es un numpy array de 2 dmensiones (canales, alturas)
    data = None
    
    def __init__(self):
        '''
        Constructor
        '''
        
        self.m_RadarControllerHeader = RadarControllerHeader()
    
        self.m_SystemHeader = SystemHeader()
        
        self.type = "Voltage"
        
        self.data = None
        
        self.dtype = None
        
        self.nChannels = 0
        
        self.nHeights = 0
        
        self.nProfiles = None
        
        self.heightList = None
        
        self.channelList = None
        
        self.channelIndexList = None
        
        self.flagNoData = True
        
        self.flagTimeBlock = False
        
        self.dataUtcTime = None
        
        self.nCohInt = None

class Spectra(JROData):
    
    #data es un numpy array de 2 dmensiones (canales, perfiles, alturas)
    data_spc = None
    
    #data es un numpy array de 2 dmensiones (canales, pares, alturas)
    data_cspc = None
    
    #data es un numpy array de 2 dmensiones (canales, alturas)
    data_dc = None
    
    nFFTPoints = None
    
    nPairs = None
    
    pairsList = None
    
    nIncohInt = None
    
    def __init__(self):
        '''
        Constructor
        '''
        
        self.m_RadarControllerHeader = RadarControllerHeader()
    
        self.m_SystemHeader = SystemHeader()
        
        self.type = "Spectra"
        
#        self.data = None
        
        self.dtype = None
        
        self.nChannels = 0
        
        self.nHeights = 0
        
        self.nProfiles = None
        
        self.heightList = None
        
        self.channelList = None
        
        self.channelIndexList = None
        
        self.flagNoData = True
        
        self.flagTimeBlock = False
        
        self.dataUtcTime = None
        
        self.nIncohInt = None
        
        
class SpectraHeis(JROData):
    
    data_spc = None
    
    data_cspc = None
    
    data_dc = None
    
    nFFTPoints = None
    
    nPairs = None
    
    pairsList = None
    
    def __init__(self):
        
        self.m_RadarControllerHeader = RadarControllerHeader()
    
        self.m_SystemHeader = SystemHeader()
        
        self.type = "SpectraHeis"
        
        self.dataType = None
        
        self.nHeights = 0
        
        self.nChannels = 0
        
        self.channelList = None
        
        self.heightList = None
        
        self.flagNoData = True
        
        self.flagResetProcessing = False
        
        
        #data es un numpy array de 3 dmensiones (perfiles, alturas y canales)
        self.data_spc = None
        
        self.data_cspc = None
        
        self.data_dc = None
        
        self.nFFTPoints = None
        
        self.nAvg = None
        
        self.nPairs = 0
        
        self.pairsList = None
