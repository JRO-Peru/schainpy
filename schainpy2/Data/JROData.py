import os, sys
import copy
import numpy

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from IO.JROHeader import SystemHeader, RadarControllerHeader

class JROData():
    
#    m_BasicHeader = BasicHeader()
#    m_ProcessingHeader = ProcessingHeader()

    systemHeaderObj = SystemHeader()
    
    radarControllerHeaderObj = RadarControllerHeader()

    data = None
    
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

    def __init__(self):
        
        raise ValueError, "This class has not been implemented"
        
    def copy(self, inputObj=None):
        
        if inputObj == None:
            return copy.deepcopy(self)

        for key in inputObj.__dict__.keys():
            self.__dict__[key] = inputObj.__dict__[key]

    def deepcopy(self):
        
        return copy.deepcopy(self)