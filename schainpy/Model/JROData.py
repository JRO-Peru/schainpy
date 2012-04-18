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
    type = None
    
    def __init__(self):
        '''
        Constructor
        '''
        raise ValueError, "This class has not been implemented"
    
    def copy(self, objIn=None):
        
        if objIn == None:
            return copy.deepcopy(self)
        
        for key in objIn.__dict__.keys():
            self.__dict__[key] = objIn.__dict__[key]
    
    def deepcopy(self):
        
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
    m_NoiseObj = Noise()
    
    data = None
    dataType = None

    nProfiles = None
    nHeights = None
    nChannels = None    
    
    heightList = None
    channelList = None
    
    flagNoData = False
    flagResetProcessing = False
            
    def __init__(self):
        '''
        Constructor
        '''
        raise ValueError, "This class has not been implemented"