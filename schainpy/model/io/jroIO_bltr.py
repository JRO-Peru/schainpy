import os, sys
import glob
import fnmatch
import datetime
import time
import re
import h5py
import numpy
import matplotlib.pyplot as plt

import pylab as plb
from scipy.optimize import curve_fit
from scipy import asarray as ar, exp
from scipy import stats

from numpy.ma.core import getdata

SPEED_OF_LIGHT = 299792458
SPEED_OF_LIGHT = 3e8

try:
    from gevent import sleep
except:
    from time import sleep

from schainpy.model.data.jrodata import Spectra
#from schainpy.model.data.BLTRheaderIO import FileHeader, RecordHeader
from schainpy.model.proc.jroproc_base import ProcessingUnit, Operation
#from schainpy.model.io.jroIO_bltr import BLTRReader
from numpy import imag, shape, NaN

from jroIO_base import JRODataReader


class Header(object):
    
    def __init__(self):
        raise NotImplementedError
    
   
    def read(self):
        
        raise NotImplementedError
    
    def write(self):
        
        raise NotImplementedError
    
    def printInfo(self):
        
        message = "#"*50 + "\n"
        message += self.__class__.__name__.upper() + "\n"
        message += "#"*50 + "\n"
        
        keyList = self.__dict__.keys()
        keyList.sort()
        
        for key in keyList:
            message += "%s = %s" %(key, self.__dict__[key]) + "\n"
        
        if "size" not in keyList:
            attr = getattr(self, "size")
            
            if attr:
                message += "%s = %s" %("size", attr) + "\n"
        
        #print message





FILE_STRUCTURE = numpy.dtype([          #HEADER 48bytes
                          ('FileMgcNumber','<u4'),      #0x23020100
                          ('nFDTdataRecors','<u4'),     #No Of FDT data records in this file (0 or more)
                          ('OffsetStartHeader','<u4'),
                          ('RadarUnitId','<u4'),
                          ('SiteName',numpy.str_,32),          #Null terminated
                          ])

class FileHeaderBLTR(Header):
    
    def __init__(self):
        
        self.FileMgcNumber= 0     #0x23020100
        self.nFDTdataRecors=0     #No Of FDT data records in this file (0 or more)
        self.RadarUnitId= 0
        self.OffsetStartHeader=0
        self.SiteName= ""
        self.size = 48
        
    def FHread(self, fp):
        #try:
        startFp = open(fp,"rb")
        
        header = numpy.fromfile(startFp, FILE_STRUCTURE,1)
        
        print ' '
        print 'puntero file header', startFp.tell()
        print ' '
        
        
        '''      numpy.fromfile(file, dtype, count, sep='')
            file : file or str
            Open file object or filename.

            dtype : data-type
            Data type of the returned array. For binary files, it is used to determine 
            the size and byte-order of the items in the file.

            count : int
            Number of items to read. -1 means all items (i.e., the complete file).

            sep : str
            Separator between items if file is a text file. Empty ("") separator means 
            the file should be treated as binary. Spaces (" ") in the separator match zero 
            or more whitespace characters. A separator consisting only of spaces must match 
            at least one whitespace.

    '''


        
        self.FileMgcNumber= hex(header['FileMgcNumber'][0])
        self.nFDTdataRecors=int(header['nFDTdataRecors'][0])     #No Of FDT data records in this file (0 or more)
        self.RadarUnitId= int(header['RadarUnitId'][0])
        self.OffsetStartHeader= int(header['OffsetStartHeader'][0])
        self.SiteName= str(header['SiteName'][0])
        
        #print 'Numero de bloques', self.nFDTdataRecors
        
        
        if self.size <48:
            return 0
            
        return 1
    
    
    def write(self, fp):
        
        headerTuple = (self.FileMgcNumber,
                       self.nFDTdataRecors,
                       self.RadarUnitId,
                       self.SiteName,
                       self.size)
             
                       
        header = numpy.array(headerTuple, FILE_STRUCTURE)
        #        numpy.array(object, dtype=None, copy=True, order=None, subok=False, ndmin=0)
        header.tofile(fp)
        ''' ndarray.tofile(fid, sep, format)    Write array to a file as text or binary (default).

        fid : file or str
        An open file object, or a string containing a filename.

        sep : str
        Separator between array items for text output. If "" (empty), a binary file is written, 
        equivalent to file.write(a.tobytes()).

        format : str
        Format string for text file output. Each entry in the array is formatted to text by 
        first converting it to the closest Python type, and then using "format" % item.

        '''
        
        return 1





RECORD_STRUCTURE = numpy.dtype([         #RECORD HEADER 180+20N bytes
                            ('RecMgcNumber','<u4'),     #0x23030001
                            ('RecCounter','<u4'),       #Record counter(0,1, ...)
                            ('Off2StartNxtRec','<u4'),  #Offset to start of next record form start of this record
                            ('Off2StartData','<u4'),    #Offset to start of data from start of this record     
                            ('nUtime','<i4'),      #Epoch time stamp of start of acquisition (seconds)   
                            ('nMilisec','<u4'),      #Millisecond component of time stamp (0,...,999) 
                            ('ExpTagName',numpy.str_,32),      #Experiment tag name (null terminated)
                            ('ExpComment',numpy.str_,32),      #Experiment comment (null terminated)
                            ('SiteLatDegrees','<f4'),   #Site latitude (from GPS) in degrees (positive implies North)
                            ('SiteLongDegrees','<f4'),  #Site longitude (from GPS) in degrees (positive implies East)
                            ('RTCgpsStatus','<u4'),     #RTC GPS engine status (0=SEEK, 1=LOCK, 2=NOT FITTED, 3=UNAVAILABLE)
                            ('TransmitFrec','<u4'),     #Transmit frequency (Hz)
                            ('ReceiveFrec','<u4'),      #Receive frequency
                            ('FirstOsciFrec','<u4'),    #First local oscillator frequency (Hz) 
                            ('Polarisation','<u4'),     #(0="O", 1="E", 2="linear 1", 3="linear2")
                            ('ReceiverFiltSett','<u4'), #Receiver filter settings (0,1,2,3)
                            ('nModesInUse','<u4'),      #Number of modes in use (1 or 2)
                            ('DualModeIndex','<u4'),    #Dual Mode index number for these data (0 or 1)
                            ('DualModeRange','<u4'),    #Dual Mode range correction for these data (m)
                            ('nDigChannels','<u4'),     #Number of digital channels acquired (2*N)
                            ('SampResolution','<u4'),   #Sampling resolution (meters)
                            ('nHeights','<u4'),         #Number of range gates sampled
                            ('StartRangeSamp','<u4'),   #Start range of sampling (meters)
                            ('PRFhz','<u4'),            #PRF (Hz)
                            ('nCohInt','<u4'),          #Integrations
                            ('nProfiles','<u4'),        #Number of data points transformed
                            ('nChannels','<u4'),        #Number of receive beams stored in file (1 or N)
                            ('nIncohInt','<u4'),        #Number of spectral averages
                            ('FFTwindowingInd','<u4'),  #FFT windowing index (0 = no window)
                            ('BeamAngleAzim','<f4'),    #Beam steer angle (azimuth) in degrees (clockwise from true North)
                            ('BeamAngleZen','<f4'),     #Beam steer angle (zenith) in degrees (0=> vertical)
                            ('AntennaCoord0','<f4'),    #Antenna coordinates (Range(meters), Bearing(degrees)) - N pairs
                            ('AntennaAngl0','<f4'),     #Antenna coordinates (Range(meters), Bearing(degrees)) - N pairs
                            ('AntennaCoord1','<f4'),    #Antenna coordinates (Range(meters), Bearing(degrees)) - N pairs
                            ('AntennaAngl1','<f4'),     #Antenna coordinates (Range(meters), Bearing(degrees)) - N pairs
                            ('AntennaCoord2','<f4'),    #Antenna coordinates (Range(meters), Bearing(degrees)) - N pairs
                            ('AntennaAngl2','<f4'),     #Antenna coordinates (Range(meters), Bearing(degrees)) - N pairs
                            ('RecPhaseCalibr0','<f4'),  #Receiver phase calibration (degrees) - N values
                            ('RecPhaseCalibr1','<f4'),  #Receiver phase calibration (degrees) - N values
                            ('RecPhaseCalibr2','<f4'),  #Receiver phase calibration (degrees) - N values
                            ('RecAmpCalibr0','<f4'),    #Receiver amplitude calibration (ratio relative to receiver one) - N values
                            ('RecAmpCalibr1','<f4'),    #Receiver amplitude calibration (ratio relative to receiver one) - N values
                            ('RecAmpCalibr2','<f4'),    #Receiver amplitude calibration (ratio relative to receiver one) - N values
                            ('ReceiverGaindB0','<i4'),  #Receiver gains in dB - N values
                            ('ReceiverGaindB1','<i4'),  #Receiver gains in dB - N values
                            ('ReceiverGaindB2','<i4'),  #Receiver gains in dB - N values
                            ])


class RecordHeaderBLTR(Header):
    
    def __init__(self,      RecMgcNumber=None,   RecCounter= 0,      Off2StartNxtRec= 811248,      
                            nUtime= 0,           nMilisec= 0,        ExpTagName= None,      
                            ExpComment=None,     SiteLatDegrees=0,   SiteLongDegrees= 0, 
                            RTCgpsStatus= 0,     TransmitFrec= 0,    ReceiveFrec= 0,     
                            FirstOsciFrec= 0,    Polarisation= 0,    ReceiverFiltSett= 0,
                            nModesInUse= 0,      DualModeIndex= 0,   DualModeRange= 0,   
                            nDigChannels= 0,     SampResolution= 0,  nHeights= 0,
                            StartRangeSamp= 0,   PRFhz= 0,           nCohInt= 0,
                            nProfiles= 0,        nChannels= 0,       nIncohInt= 0,
                            FFTwindowingInd= 0,  BeamAngleAzim= 0,   BeamAngleZen= 0,
                            AntennaCoord0= 0,     AntennaCoord1= 0,    AntennaCoord2= 0, 
                            RecPhaseCalibr0= 0,  RecPhaseCalibr1= 0, RecPhaseCalibr2= 0,
                            RecAmpCalibr0= 0,    RecAmpCalibr1= 0,   RecAmpCalibr2= 0,
                            AntennaAngl0=0,      AntennaAngl1=0,     AntennaAngl2=0,
                            ReceiverGaindB0= 0,  ReceiverGaindB1= 0, ReceiverGaindB2= 0, Off2StartData=0,    OffsetStartHeader=0):
        
        self.RecMgcNumber = RecMgcNumber     #0x23030001
        self.RecCounter = RecCounter      
        self.Off2StartNxtRec = Off2StartNxtRec       
        self.Off2StartData = Off2StartData
        self.nUtime = nUtime        
        self.nMilisec = nMilisec   
        self.ExpTagName = ExpTagName       
        self.ExpComment = ExpComment      
        self.SiteLatDegrees = SiteLatDegrees  
        self.SiteLongDegrees = SiteLongDegrees  
        self.RTCgpsStatus = RTCgpsStatus     
        self.TransmitFrec = TransmitFrec     
        self.ReceiveFrec = ReceiveFrec      
        self.FirstOsciFrec = FirstOsciFrec     
        self.Polarisation = Polarisation     
        self.ReceiverFiltSett = ReceiverFiltSett 
        self.nModesInUse = nModesInUse      
        self.DualModeIndex = DualModeIndex    
        self.DualModeRange = DualModeRange    
        self.nDigChannels = nDigChannels
        self.SampResolution = SampResolution 
        self.nHeights = nHeights 
        self.StartRangeSamp = StartRangeSamp 
        self.PRFhz = PRFhz 
        self.nCohInt = nCohInt 
        self.nProfiles = nProfiles 
        self.nChannels = nChannels 
        self.nIncohInt = nIncohInt 
        self.FFTwindowingInd = FFTwindowingInd 
        self.BeamAngleAzim = BeamAngleAzim 
        self.BeamAngleZen = BeamAngleZen 
        self.AntennaCoord0 = AntennaCoord0
        self.AntennaAngl0 = AntennaAngl0
        self.AntennaAngl1 = AntennaAngl1
        self.AntennaAngl2 = AntennaAngl2
        self.AntennaCoord1 = AntennaCoord1
        self.AntennaCoord2 = AntennaCoord2  
        self.RecPhaseCalibr0 = RecPhaseCalibr0
        self.RecPhaseCalibr1 = RecPhaseCalibr1
        self.RecPhaseCalibr2 = RecPhaseCalibr2 
        self.RecAmpCalibr0 = RecAmpCalibr0
        self.RecAmpCalibr1 = RecAmpCalibr1
        self.RecAmpCalibr2 = RecAmpCalibr2 
        self.ReceiverGaindB0 = ReceiverGaindB0
        self.ReceiverGaindB1 = ReceiverGaindB1
        self.ReceiverGaindB2 = ReceiverGaindB2 
        self.OffsetStartHeader =  48
        
        
    
    def RHread(self, fp):
        #print fp
        #startFp = open('/home/erick/Documents/Data/huancayo.20161019.22.fdt',"rb") #The method tell() returns the current position of the file read/write pointer within the file.
        startFp = open(fp,"rb") #The method tell() returns the current position of the file read/write pointer within the file.
        #RecCounter=0
        #Off2StartNxtRec=811248
        OffRHeader= self.OffsetStartHeader + self.RecCounter*self.Off2StartNxtRec
        print ' '
        print 'puntero Record Header', startFp.tell()
        print ' '
        
        
        startFp.seek(OffRHeader, os.SEEK_SET)
        
        print ' '
        print 'puntero Record Header con seek', startFp.tell()
        print ' '
        
        #print 'Posicion del bloque:        ',OffRHeader
        
        header = numpy.fromfile(startFp,RECORD_STRUCTURE,1)
        
        print ' '
        print 'puntero Record Header con seek', startFp.tell()
        print ' '
        
        print ' '
        #
        #print 'puntero Record Header despues de seek', header.tell()
        print ' '
        
        self.RecMgcNumber = hex(header['RecMgcNumber'][0])     #0x23030001
        self.RecCounter = int(header['RecCounter'][0])      
        self.Off2StartNxtRec = int(header['Off2StartNxtRec'][0])   
        self.Off2StartData = int(header['Off2StartData'][0])    
        self.nUtime = header['nUtime'][0]         
        self.nMilisec = header['nMilisec'][0]   
        self.ExpTagName = str(header['ExpTagName'][0])       
        self.ExpComment = str(header['ExpComment'][0])      
        self.SiteLatDegrees = header['SiteLatDegrees'][0]  
        self.SiteLongDegrees = header['SiteLongDegrees'][0]  
        self.RTCgpsStatus = header['RTCgpsStatus'][0]     
        self.TransmitFrec = header['TransmitFrec'][0]     
        self.ReceiveFrec = header['ReceiveFrec'][0]      
        self.FirstOsciFrec = header['FirstOsciFrec'][0]     
        self.Polarisation = header['Polarisation'][0]     
        self.ReceiverFiltSett = header['ReceiverFiltSett'][0] 
        self.nModesInUse = header['nModesInUse'][0]      
        self.DualModeIndex = header['DualModeIndex'][0]    
        self.DualModeRange = header['DualModeRange'][0]    
        self.nDigChannels = header['nDigChannels'][0]
        self.SampResolution = header['SampResolution'][0] 
        self.nHeights = header['nHeights'][0] 
        self.StartRangeSamp = header['StartRangeSamp'][0] 
        self.PRFhz = header['PRFhz'][0] 
        self.nCohInt = header['nCohInt'][0] 
        self.nProfiles = header['nProfiles'][0] 
        self.nChannels = header['nChannels'][0] 
        self.nIncohInt = header['nIncohInt'][0] 
        self.FFTwindowingInd = header['FFTwindowingInd'][0] 
        self.BeamAngleAzim = header['BeamAngleAzim'][0] 
        self.BeamAngleZen = header['BeamAngleZen'][0] 
        self.AntennaCoord0 = header['AntennaCoord0'][0]
        self.AntennaAngl0 = header['AntennaAngl0'][0]
        self.AntennaCoord1 = header['AntennaCoord1'][0]
        self.AntennaAngl1 = header['AntennaAngl1'][0] 
        self.AntennaCoord2 = header['AntennaCoord2'][0]
        self.AntennaAngl2 = header['AntennaAngl2'][0]  
        self.RecPhaseCalibr0 = header['RecPhaseCalibr0'][0]
        self.RecPhaseCalibr1 = header['RecPhaseCalibr1'][0]
        self.RecPhaseCalibr2 = header['RecPhaseCalibr2'][0] 
        self.RecAmpCalibr0 = header['RecAmpCalibr0'][0]
        self.RecAmpCalibr1 = header['RecAmpCalibr1'][0]
        self.RecAmpCalibr2 = header['RecAmpCalibr2'][0] 
        self.ReceiverGaindB0 = header['ReceiverGaindB0'][0]
        self.ReceiverGaindB1 = header['ReceiverGaindB1'][0]
        self.ReceiverGaindB2 = header['ReceiverGaindB2'][0]

        self.ipp= 0.5*(SPEED_OF_LIGHT/self.PRFhz)
        
        self.RHsize = 180+20*self.nChannels
        self.Datasize= self.nProfiles*self.nChannels*self.nHeights*2*4
        #print 'Datasize',self.Datasize
        endFp = self.OffsetStartHeader + self.RecCounter*self.Off2StartNxtRec
        
        print '=============================================='
        print 'RecMgcNumber         ',self.RecMgcNumber
        print 'RecCounter           ',self.RecCounter
        print 'Off2StartNxtRec      ',self.Off2StartNxtRec 
        print 'Off2StartData        ',self.Off2StartData
        print 'Range Resolution     ',self.SampResolution
        print 'First Height         ',self.StartRangeSamp
        print 'PRF (Hz)             ',self.PRFhz
        print 'Heights (K)          ',self.nHeights
        print 'Channels (N)         ',self.nChannels
        print 'Profiles (J)         ',self.nProfiles
        print 'iCoh                 ',self.nCohInt
        print 'iInCoh               ',self.nIncohInt
        print 'BeamAngleAzim        ',self.BeamAngleAzim
        print 'BeamAngleZen         ',self.BeamAngleZen
        
        #print 'ModoEnUso            ',self.DualModeIndex
        #print 'UtcTime              ',self.nUtime
        #print 'MiliSec              ',self.nMilisec
        #print 'Exp TagName          ',self.ExpTagName
        #print 'Exp Comment          ',self.ExpComment
        #print 'FFT Window Index     ',self.FFTwindowingInd
        #print 'N Dig. Channels      ',self.nDigChannels
        print 'Size de bloque       ',self.RHsize
        print 'DataSize             ',self.Datasize
        print 'BeamAngleAzim        ',self.BeamAngleAzim
        #print 'AntennaCoord0        ',self.AntennaCoord0
        #print 'AntennaAngl0         ',self.AntennaAngl0
        #print 'AntennaCoord1        ',self.AntennaCoord1
        #print 'AntennaAngl1         ',self.AntennaAngl1
        #print 'AntennaCoord2        ',self.AntennaCoord2
        #print 'AntennaAngl2         ',self.AntennaAngl2
        print 'RecPhaseCalibr0      ',self.RecPhaseCalibr0
        print 'RecPhaseCalibr1      ',self.RecPhaseCalibr1
        print 'RecPhaseCalibr2      ',self.RecPhaseCalibr2
        print 'RecAmpCalibr0        ',self.RecAmpCalibr0
        print 'RecAmpCalibr1        ',self.RecAmpCalibr1
        print 'RecAmpCalibr2        ',self.RecAmpCalibr2
        print 'ReceiverGaindB0      ',self.ReceiverGaindB0
        print 'ReceiverGaindB1      ',self.ReceiverGaindB1
        print 'ReceiverGaindB2      ',self.ReceiverGaindB2
        print '=============================================='
        
        if OffRHeader > endFp:
            sys.stderr.write("Warning %s: Size value read from System Header is lower than it has to be\n" %fp)
            return 0
            
        if OffRHeader < endFp:
            sys.stderr.write("Warning %s: Size value read from System Header size is greater than it has to be\n" %fp)
            return 0
        
        return 1

        
class BLTRSpectraReader (ProcessingUnit, FileHeaderBLTR, RecordHeaderBLTR, JRODataReader):
    
    path = None
    startDate = None
    endDate = None
    startTime = None
    endTime = None
    walk = None
    isConfig = False
    
    
    fileList= None
    
    #metadata
    TimeZone= None
    Interval= None
    heightList= None
    
    #data
    data= None
    utctime= None
    
    
    
    def __init__(self, **kwargs):
        
        #Eliminar de la base la herencia
        ProcessingUnit.__init__(self, **kwargs)
        
        #self.isConfig = False
        
        #self.pts2read_SelfSpectra = 0
        #self.pts2read_CrossSpectra = 0
        #self.pts2read_DCchannels = 0
        #self.datablock = None
        self.utc = None
        self.ext = ".fdt"
        self.optchar = "P"
        self.fpFile=None
        self.fp = None
        self.BlockCounter=0
        self.dtype = None
        self.fileSizeByHeader = None
        self.filenameList = []
        self.fileSelector = 0
        self.Off2StartNxtRec=0
        self.RecCounter=0
        self.flagNoMoreFiles = 0
        self.data_spc=None
        self.data_cspc=None
        self.data_output=None
        self.path = None
        self.OffsetStartHeader=0
        self.Off2StartData=0
        self.ipp = 0
        self.nFDTdataRecors=0
        self.blocksize = 0
        self.dataOut = Spectra()
        self.profileIndex = 1 #Always
        self.dataOut.flagNoData=False
        self.dataOut.nRdPairs = 0
        self.dataOut.pairsList = []
        self.dataOut.data_spc=None
        self.dataOut.noise=[]
        self.dataOut.velocityX=[]
        self.dataOut.velocityY=[]
        self.dataOut.velocityV=[]
        


    def Files2Read(self, fp):
        ''' 
        Function that indicates the number of .fdt files that exist in the folder to be read.
        It also creates an organized list with the names of the files to read.
        '''
        #self.__checkPath()
        
        ListaData=os.listdir(fp)    #Gets the list of files within the fp address
        ListaData=sorted(ListaData) #Sort the list of files from least to largest by names
        nFiles=0                    #File Counter
        FileList=[]                 #A list is created that will contain the .fdt files
        for IndexFile in ListaData :
            if  '.fdt' in IndexFile:
                FileList.append(IndexFile)
                nFiles+=1
        
        #print 'Files2Read'
        #print 'Existen '+str(nFiles)+' archivos .fdt' 
        
        self.filenameList=FileList #List of files from least to largest by names
        
    
    def run(self, **kwargs):
        '''
        This method will be the one that will initiate the data entry, will be called constantly.
        You should first verify that your Setup () is set up and then continue to acquire
        the data to be processed with getData ().
        '''
        if not self.isConfig:
            self.setup(**kwargs)
            self.isConfig = True
            
        self.getData()
        #print 'running'
        
        
    def setup(self, path=None,
                    startDate=None, 
                    endDate=None, 
                    startTime=None, 
                    endTime=None,
                    walk=True,
                    timezone='utc',
                    code = None,
                    online=False,
                    ReadMode=None,
                    **kwargs):
        
        self.isConfig = True
        
        self.path=path 
        self.startDate=startDate
        self.endDate=endDate
        self.startTime=startTime 
        self.endTime=endTime
        self.walk=walk 
        self.ReadMode=int(ReadMode)
        
        pass
        
        
    def getData(self):
        '''
        Before starting this function, you should check that there is still an unread file,
        If there are still blocks to read or if the data block is empty.
        
        You should call the file "read".
        
        '''
        
        if self.flagNoMoreFiles:
            self.dataOut.flagNoData = True
            #print 'NoData se vuelve true'
            return 0

        self.fp=self.path
        self.Files2Read(self.fp)
        self.readFile(self.fp)
        self.dataOut.data_spc = self.data_spc
        self.dataOut.data_cspc =self.data_cspc
        self.dataOut.data_output=self.data_output
        
        #print 'self.dataOut.data_output', shape(self.dataOut.data_output)
        
        #self.removeDC()
        return self.dataOut.data_spc  
        
    
    def readFile(self,fp):
        '''
        You must indicate if you are reading in Online or Offline mode and load the
        The parameters for this file reading mode.
        
        Then you must do 2 actions:
        
        1. Get the BLTR FileHeader.
        2. Start reading the first block.
        '''
        
        #The address of the folder is generated the name of the .fdt file that will be read
        #print "File:    ",self.fileSelector+1
        
        if self.fileSelector < len(self.filenameList):
            
            self.fpFile=str(fp)+'/'+str(self.filenameList[self.fileSelector])
            #print self.fpFile
            fheader = FileHeaderBLTR()
            fheader.FHread(self.fpFile)   #Bltr FileHeader Reading
            self.nFDTdataRecors=fheader.nFDTdataRecors
            
            self.readBlock()    #Block reading
        else:
            #print 'readFile FlagNoData becomes true'
            self.flagNoMoreFiles=True
            self.dataOut.flagNoData = True
            return 0 
    
    def getVelRange(self, extrapoints=0):
                    Lambda= SPEED_OF_LIGHT/50000000
                    PRF = self.dataOut.PRF#1./(self.dataOut.ippSeconds * self.dataOut.nCohInt)
                    Vmax=-Lambda/(4.*(1./PRF)*self.dataOut.nCohInt*2.)
                    deltafreq = PRF / (self.nProfiles)
                    deltavel = (Vmax*2) / (self.nProfiles)
                    freqrange = deltafreq*(numpy.arange(self.nProfiles)-self.nProfiles/2.) - deltafreq/2
                    velrange = deltavel*(numpy.arange(self.nProfiles)-self.nProfiles/2.) 
                    return velrange
    
    def readBlock(self):  
        '''
        It should be checked if the block has data, if it is not passed to the next file.
        
        Then the following is done:
        
        1. Read the RecordHeader
        2. Fill the buffer with the current block number.
        
        '''
        
        if self.BlockCounter < self.nFDTdataRecors-1:
            #print self.nFDTdataRecors, 'CONDICION'
            if self.ReadMode==1:
                rheader = RecordHeaderBLTR(RecCounter=self.BlockCounter+1)
            elif self.ReadMode==0:
                rheader = RecordHeaderBLTR(RecCounter=self.BlockCounter)
            
            rheader.RHread(self.fpFile)   #Bltr FileHeader Reading
            
            self.OffsetStartHeader=rheader.OffsetStartHeader
            self.RecCounter=rheader.RecCounter
            self.Off2StartNxtRec=rheader.Off2StartNxtRec
            self.Off2StartData=rheader.Off2StartData
            self.nProfiles=rheader.nProfiles
            self.nChannels=rheader.nChannels
            self.nHeights=rheader.nHeights
            self.frequency=rheader.TransmitFrec
            self.DualModeIndex=rheader.DualModeIndex
            
            self.pairsList =[(0,1),(0,2),(1,2)]
            self.dataOut.pairsList = self.pairsList
            
            self.nRdPairs=len(self.dataOut.pairsList)
            self.dataOut.nRdPairs = self.nRdPairs
            
            self.__firstHeigth=rheader.StartRangeSamp
            self.__deltaHeigth=rheader.SampResolution
            self.dataOut.heightList= self.__firstHeigth + numpy.array(range(self.nHeights))*self.__deltaHeigth
            self.dataOut.channelList = range(self.nChannels)
            self.dataOut.nProfiles=rheader.nProfiles
            self.dataOut.nIncohInt=rheader.nIncohInt
            self.dataOut.nCohInt=rheader.nCohInt
            self.dataOut.ippSeconds= 1/float(rheader.PRFhz)
            self.dataOut.PRF=rheader.PRFhz
            self.dataOut.nFFTPoints=rheader.nProfiles
            self.dataOut.utctime=rheader.nUtime
            self.dataOut.timeZone=0
            self.dataOut.normFactor= self.dataOut.nProfiles*self.dataOut.nIncohInt*self.dataOut.nCohInt
            self.dataOut.outputInterval= self.dataOut.ippSeconds * self.dataOut.nCohInt * self.dataOut.nIncohInt * self.nProfiles
            
            self.data_output=numpy.ones([3,rheader.nHeights])*numpy.NaN
            #print 'self.data_output', shape(self.data_output)
            self.dataOut.velocityX=[]
            self.dataOut.velocityY=[]
            self.dataOut.velocityV=[]
            
            '''Block Reading, the Block Data is received and Reshape is used to give it
            shape.
            '''    
            
            #Procedure to take the pointer to where the date block starts
            startDATA = open(self.fpFile,"rb")
            OffDATA= self.OffsetStartHeader + self.RecCounter*self.Off2StartNxtRec+self.Off2StartData
            startDATA.seek(OffDATA, os.SEEK_SET)
            
            def moving_average(x, N=2):
                return numpy.convolve(x, numpy.ones((N,))/N)[(N-1):]
                
            def gaus(xSamples,a,x0,sigma):
                return a*exp(-(xSamples-x0)**2/(2*sigma**2))
                
            def Find(x,value):
                for index in range(len(x)):
                    if x[index]==value:
                        return index     
                            
            def pol2cart(rho, phi):
                x = rho * numpy.cos(phi)
                y = rho * numpy.sin(phi)
                return(x, y)
            
            
            
            
            if self.DualModeIndex==self.ReadMode:
                
                self.data_fft = numpy.fromfile( startDATA, [('complex','<c8')],self.nProfiles*self.nChannels*self.nHeights )
#                 
#                 if len(self.data_fft) is not 101376:
#                     
#                     self.data_fft = numpy.empty(101376)
                
                self.data_fft=self.data_fft.astype(numpy.dtype('complex'))
                
                
                
                
                
                self.data_block=numpy.reshape(self.data_fft,(self.nHeights, self.nChannels, self.nProfiles ))
                
                self.data_block = numpy.transpose(self.data_block, (1,2,0))
                
                copy = self.data_block.copy()
                spc = copy * numpy.conjugate(copy)   
                
                self.data_spc = numpy.absolute(spc) # valor absoluto o magnitud
                
                factor = self.dataOut.normFactor
                
                
                z = self.data_spc.copy()#/factor
                z = numpy.where(numpy.isfinite(z), z, numpy.NAN)
                #zdB = 10*numpy.log10(z)
                
                
                self.dataOut.data_spc=self.data_spc
                
                self.noise = self.dataOut.getNoise(ymin_index=80, ymax_index=132)#/factor
                #noisedB = 10*numpy.log10(self.noise)
                
                
                ySamples=numpy.ones([3,self.nProfiles])
                phase=numpy.ones([3,self.nProfiles])
                CSPCSamples=numpy.ones([3,self.nProfiles],dtype=numpy.complex_)
                coherence=numpy.ones([3,self.nProfiles])
                PhaseSlope=numpy.ones(3)
                PhaseInter=numpy.ones(3)
                
                '''****** Getting CrossSpectra ******'''
                cspc=self.data_block.copy()
                self.data_cspc=self.data_block.copy()
                
                xFrec=self.getVelRange(1)
                VelRange=self.getVelRange(1)
                self.dataOut.VelRange=VelRange
                #print ' '
                #print ' '
                #print 'xFrec',xFrec
                #print ' '
                #print ' '
                #Height=35
                
                for i in range(self.nRdPairs):    
                    
                    chan_index0 = self.dataOut.pairsList[i][0]
                    chan_index1 = self.dataOut.pairsList[i][1]
                    
                    self.data_cspc[i,:,:]=cspc[chan_index0,:,:] * numpy.conjugate(cspc[chan_index1,:,:])
                
                
                    '''Getting Eij and Nij'''
                    (AntennaX0,AntennaY0)=pol2cart(rheader.AntennaCoord0, rheader.AntennaAngl0*numpy.pi/180)
                    (AntennaX1,AntennaY1)=pol2cart(rheader.AntennaCoord1, rheader.AntennaAngl1*numpy.pi/180)
                    (AntennaX2,AntennaY2)=pol2cart(rheader.AntennaCoord2, rheader.AntennaAngl2*numpy.pi/180)
                    
                    E01=AntennaX0-AntennaX1
                    N01=AntennaY0-AntennaY1
                    
                    E02=AntennaX0-AntennaX2
                    N02=AntennaY0-AntennaY2
                    
                    E12=AntennaX1-AntennaX2
                    N12=AntennaY1-AntennaY2
                    
                    self.ChanDist= numpy.array([[E01, N01],[E02,N02],[E12,N12]])
                    
                    self.dataOut.ChanDist = self.ChanDist
                
                
                
                
            self.BlockCounter+=2
            
        else:
            self.fileSelector+=1    
            self.BlockCounter=0
            print "Next File"                