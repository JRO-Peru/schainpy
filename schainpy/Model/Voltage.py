'''
Created on Feb 7, 2012

@author: roj-idl71
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


    def __init__(self):
        '''
        Constructor
        '''
        pass

    def copy(self):
        pass
        