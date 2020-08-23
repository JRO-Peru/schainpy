'''
Created on Oct 24, 2016

@author: roj- LouVD
'''

import numpy
import datetime
import time
from time import gmtime

from numpy import transpose

from .jroproc_base import ProcessingUnit, Operation
from schainpy.model.data.jrodata import Parameters


class PXParametersProc(ProcessingUnit):    
    '''
    Processing unit for PX parameters data
    '''

    def __init__(self, **kwargs):
        """
        Inputs: None           
        """
        ProcessingUnit.__init__(self, **kwargs)
        self.dataOut = Parameters()
        self.isConfig = False

    def setup(self, mode):
        """
        """
        self.dataOut.mode = mode

    def run(self, mode):
        """
        Args:
            mode (str): select independent variable 'E' for elevation or 'A' for azimuth
        """

        if not self.isConfig:
            self.setup(mode)
            self.isConfig = True

        if self.dataIn.type == 'Parameters':
            self.dataOut.copy(self.dataIn)

        self.dataOut.data_param = numpy.array([self.dataOut.data[var] for var in self.dataOut.parameters])
        self.dataOut.data_param[self.dataOut.data_param == self.dataOut.missing] = numpy.nan

        if mode.upper()=='E':    
            self.dataOut.heightList = self.dataOut.data['Azimuth']
        else:
            self.dataOut.heightList = self.dataOut.data['Elevation']

        attrs = ['units', 'elevation', 'azimuth', 'max_range', 'latitude', 'longitude']
        meta = {}

        for attr in attrs:
            meta[attr] = getattr(self.dataOut, attr)

        meta['mode'] = mode
        self.dataOut.meta = meta