'''
Created on Feb 7, 2012

@author $Author$
@version $Id$
'''

from JROData import JROData, Noise
from JROHeader import RadarControllerHeader, ProcessingHeader, SystemHeader, BasicHeader

class Spectra(JROData):
    '''
    classdocs
    '''
    
    type = "Spectra"
    data_spc = None
    data_cspc = None
    data_dc = None
    

    def __init__(self):
        '''
        Constructor
        '''
        
        self.m_RadarControllerHeader = RadarControllerHeader()
        
        self.m_ProcessingHeader = ProcessingHeader()
    
        self.m_SystemHeader = SystemHeader()
    
        self.m_BasicHeader = BasicHeader()
        
        m_NoiseObj = Noise()
        
        #data es un numpy array de 3 dmensiones (perfiles, alturas y canales)
        self.data_spc = None
        
        self.data_cspc = None
        
        self.data_dc = None
          
        self.heightList  = None
        
        self.channelList = None
        
        self.flagNoData = True
        
        self.nProfiles = None
        
        self.nPoints = None
        
        self.dataType = None
        
        self.flagResetProcessing = False
        
        self.nPairs = 0

        self.nChannels = 0