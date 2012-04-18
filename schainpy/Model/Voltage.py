'''
Created on Feb 7, 2012

@author $Author$
@version $Id$
'''

from JROData import JROData, Noise
from JROHeader import RadarControllerHeader, ProcessingHeader, SystemHeader, BasicHeader

class Voltage(JROData):
    '''
    classdocs
    '''
    
    type = "Voltage"
    data = None
    profileIndex = None
    
    def __init__(self):
        '''
        Constructor
        '''
        
        self.m_RadarControllerHeader= RadarControllerHeader()
        
        self.m_ProcessingHeader= ProcessingHeader()
    
        self.m_SystemHeader= SystemHeader()
    
        self.m_BasicHeader= BasicHeader()
        
        m_NoiseObj = Noise()
        
        #data es un numpy array de 3 dmensiones (perfiles, alturas y canales)
        self.data = None
        
        self.dataType = None
        
        self.heightList = None
        
        self.profileIndex = None
        
        self.nProfiles = None
        
        self.flagNoData = True
        
        self.flagResetProcessing = False
        