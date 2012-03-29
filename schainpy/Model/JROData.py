'''
Created on Feb 7, 2012

@author $Author$
@version $Id$
'''
import copy
from JROHeader import RadarControllerHeader, ProcessingHeader, SystemHeader, BasicHeader

class Data:
    '''
    classdocs
    '''
    __type = None
    
    def __init__(self):
        '''
        Constructor
        '''
        raise ValueError, "This class has not been implemented"
    
    def copy(self):
        
        return copy.copy(self)
    
    def deepcopy(self, obj):
        
        return copy.deepcopy(self)

class Noise(Data):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        pass

class JROData(Data):
    '''
    classdocs
    '''
    m_RadarControllerHeader = RadarControllerHeader()
    m_ProcessingHeader = ProcessingHeader()
    m_SystemHeader = SystemHeader()
    m_BasicHeader = BasicHeader()
    m_Noise = Noise()
    
    data = None
    dataType = None

    nProfiles = None
    nHeights = None
    nChannels = None    
    
    heights = None
    
    flagNoData = False
    flagResetProcessing = False
            
    def __init__(self):
        '''
        Constructor
        '''
        raise ValueError, "This class has not been implemented"