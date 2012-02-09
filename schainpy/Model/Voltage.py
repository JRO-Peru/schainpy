'''
Created on Feb 7, 2012

@author $Author$
@version $Id$
'''
import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from Model.Data import Data
from IO.Header import *

class Voltage(Data):
    '''
    classdocs
    '''


    m_RadarControllerHeader= RadarControllerHeader()

    m_ProcessingHeader= ProcessingHeader()

    m_SystemHeader= SystemHeader()

    m_BasicHeader= BasicHeader()
    
    #data es un numpy array de 3 dmensiones (perfiles, alturas y canales)
    data = None
    
    noData = True


    def __init__(self):
        '''
        Constructor
        '''
        pass

    def copy(self):
        obj = Voltage()
        obj.m_BasicHeader = self.m_BasicHeader.copy()
        obj.m_SystemHeader = self.m_SystemHeader.copy()
        obj.m_RadarControllerHeader = self.m_RadarControllerHeader.copy()
        obj.m_ProcessingHeader = self.m_ProcessingHeader.copy()
        
        return obj
        