import os, sys
import numpy

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from JROData import JROData
from IO.JROHeader import SystemHeader, RadarControllerHeader

class Voltage(JROData):
    
    nCohInt = None
    
    data = None
    
    def __init__(self):
        '''
        Constructor
        '''
        
        self.m_RadarControllerHeader = RadarControllerHeader()
    
        self.m_SystemHeader = SystemHeader()
        
        self.type = "Voltage"
        
        #data es un numpy array de 2 dmensiones ( canales, alturas)
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
