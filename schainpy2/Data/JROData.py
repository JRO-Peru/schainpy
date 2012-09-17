
import copy
import numpy
from JROHeader import BasicHeader, SystemHeader, RadarControllerHeader, ProcessingHeader

class Data:
    def __init__(self):
        pass

    def copy(self, inputObj=None):
        if inputObj == None:
            return copy.deepcopy(self)

        for key in inputObj.__dict__.keys():
            self.__dict__[key] = inputObj.__dict__[key]

    def deepcopy(self):
        return copy.deepcopy(self)

class JROData(Data):
    data = None
#    m_BasicHeader = BasicHeader()
#    m_SystemHeader = SystemHeader()
#    m_RadarControllerHeader = RadarControllerHeader()
#    m_ProcessingHeader = ProcessingHeader()
    type = None
    dataType = None
    heightList = None
    channelIndexList = None
    channelList = None
    nHeights = None
    nProfiles = None
    nBlocksPerFile = None
    nChannels = None
    flagNoData = False
    flagResetProcessing = False

    def __init__(self):
        raise ValueError, "This class has not been implemented"

#    def updateHeaderFromObj(self):
#        pass
#        
#
#    def updateObjFromHeader(self):
#        pass
        
        
