'''
Created on Feb 7, 2012

@author $Author$
@version $Id$
'''
import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from Model.Data import Data
from IO.HeaderIO import *


class Spectra(Data):
    '''
    classdocs
    '''
        

    def __init__(self):
        '''
        Constructor
        '''
        
        self.m_RadarControllerHeader = RadarControllerHeader()
        
        self.m_ProcessingHeader = ProcessingHeader()
    
        self.m_SystemHeader = SystemHeader()
    
        self.m_BasicHeader = BasicHeader()
        
        #data es un numpy array de 3 dmensiones (perfiles, alturas y canales)
        self.data_spc = None
        self.data_cspc = None
        self.data_dc = None
        """
        self.datablock_spc = None
        self.datablock_cspc = None
        self.datablock_dc = None
        """
          
        self.heights  = None
        
        self.flagNoData = True
        
        self.nProfiles = None
        
        self.dataType = None
        
        self.flagResetProcessing = False

        self.noise = None
        
        self.nPairs = 0

        self.nChannels = 0


    def copy(self):
        obj = Spectra()
        obj.m_BasicHeader = self.m_BasicHeader.copy()
        obj.m_SystemHeader = self.m_SystemHeader.copy()
        obj.m_RadarControllerHeader = self.m_RadarControllerHeader.copy()
        obj.m_ProcessingHeader = self.m_ProcessingHeader.copy()
        
        obj.data_spc = self.data_spc
        obj.data_cspc = self.data_cspc
        obj.data_dc = self.data_dc
        
        obj.heights = self.heights
        obj.flagNoData = self.flagNoData
        
        obj.nProfiles = self.nProfiles
        
        obj.noise = self.noise

        obj.dataType = self.dataType

        return obj
        