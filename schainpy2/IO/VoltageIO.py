
import os, sys
import numpy
import glob
import fnmatch
import time, datetime

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from Model.JROHeader import *
from Model.Voltage import Voltage

from IO.JRODataIO import JRODataReader


class VoltageReader(JRODataReader):
    dataOutObj = None
    datablock = None
    ext = ".r"
    optchar = "D"

    def __init__(self, dataOutObj=None):
        self.datablock = None
        #Por herencia no necesito instanciar nuevamente estos objetos
        #self.m_BasicHeader = BasicHeader()
        #self.m_SystemHeader = SystemHeader()
        #self.m_RadarControllerHeader = RadarControllerHeader()
        #self.m_ProcessingHeader = ProcessingHeader()
        self.online = 0

    def createObjByDefault(self):
        dataObj = Voltage()

        return dataObj

    def getBlockDimension(self):
        pts2read = self.m_ProcessingHeader.profilesPerBlock * self.m_ProcessingHeader.numHeights * self.m_SystemHeader.numChannels
        self.blocksize = pts2read
        

