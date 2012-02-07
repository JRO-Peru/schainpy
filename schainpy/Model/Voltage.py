'''
Created on Feb 7, 2012

@author: roj-idl71
'''

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
        