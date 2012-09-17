import numpy
from JROData import JROData
# No deberia importar los Headers
class Voltage(JROData):
    data = None
    nCohInt = None
    
    def __init__(self):
        self.type = "Voltage"

    def updateObjFromHeader(self):
        xi = self.m_ProcessingHeader.firstHeight
        step = self.m_ProcessingHeader.deltaHeight
        xf = xi + self.m_ProcessingHeader.numHeights*step

        self.heightList = numpy.arange(xi, xf, step)
        self.channelIndexList = numpy.arange(self.m_SystemHeader.numChannels)
        self.channelList = numpy.arange(self.m_SystemHeader.numChannels)

        self.nHeights = len(self.heightList)
        self.nChannels = len(self.channelList)
        self.nProfiles = self.m_ProcessingHeader.profilesPerBlock
        self.nBlocksPerFile = self.m_ProcessingHeader.dataBlocksPerFile
        self.nCohInt = self.m_ProcessingHeader.coherentInt
    
    def updateHeaderFromObj(self):
        pass