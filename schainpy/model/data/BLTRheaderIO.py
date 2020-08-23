'''

$Author: murco $
$Id: JROHeaderIO.py 151 2012-10-31 19:00:51Z murco $
'''
import sys
import numpy
import copy
import datetime


SPEED_OF_LIGHT = 299792458
SPEED_OF_LIGHT = 3e8

FILE_STRUCTURE = numpy.dtype([          #HEADER 48bytes
                          ('FileMgcNumber','<u4'),      #0x23020100
                          ('nFDTdataRecors','<u4'),     #No Of FDT data records in this file (0 or more)
                          ('RadarUnitId','<u4'),
                          ('SiteName','<s32'),          #Null terminated
                          ])

RECORD_STRUCTURE = numpy.dtype([         #RECORD HEADER 180+20N bytes
                            ('RecMgcNumber','<u4'),     #0x23030001
                            ('RecCounter','<u4'),       #Record counter(0,1, ...)
                            ('Off2StartNxtRec','<u4'),  #Offset to start of next record form start of this record
                            ('Off2StartData','<u4'),    #Offset to start of data from start of this record     
                            ('EpTimeStamp','<i4'),      #Epoch time stamp of start of acquisition (seconds)   
                            ('msCompTimeStamp','<u4'),  #Millisecond component of time stamp (0,...,999) 
                            ('ExpTagName','<s32'),      #Experiment tag name (null terminated)
                            ('ExpComment','<s32'),      #Experiment comment (null terminated)
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
                            ('nRangeGatesSamp','<u4'),  #Number of range gates sampled
                            ('StartRangeSamp','<u4'),   #Start range of sampling (meters)
                            ('PRFhz','<u4'),            #PRF (Hz)
                            ('Integrations','<u4'),     #Integrations
                            ('nDataPointsTrsf','<u4'),  #Number of data points transformed
                            ('nReceiveBeams','<u4'),    #Number of receive beams stored in file (1 or N)
                            ('nSpectAverages','<u4'),   #Number of spectral averages
                            ('FFTwindowingInd','<u4'),  #FFT windowing index (0 = no window)
                            ('BeamAngleAzim','<f4'),    #Beam steer angle (azimuth) in degrees (clockwise from true North)
                            ('BeamAngleZen','<f4'),     #Beam steer angle (zenith) in degrees (0=> vertical)
                            ('AntennaCoord','<f24'),     #Antenna coordinates (Range(meters), Bearing(degrees)) - N pairs
                            ('RecPhaseCalibr','<f12'),   #Receiver phase calibration (degrees) - N values
                            ('RecAmpCalibr','<f12'),     #Receiver amplitude calibration (ratio relative to receiver one) - N values
                            ('ReceiverGaindB','<u12'),   #Receiver gains in dB - N values
                            ])


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
        
        keyList = list(self.__dict__.keys())
        keyList.sort()
        
        for key in keyList:
            message += "%s = %s" %(key, self.__dict__[key]) + "\n"
        
        if "size" not in keyList:
            attr = getattr(self, "size")
            
            if attr:
                message += "%s = %s" %("size", attr) + "\n"
        
        print(message)

class FileHeader(Header):
    
    FileMgcNumber= None
    nFDTdataRecors=None     #No Of FDT data records in this file (0 or more)
    RadarUnitId= None
    SiteName= None
 
    #__LOCALTIME = None
        
    def __init__(self, useLocalTime=True):
        
        self.FileMgcNumber= 0     #0x23020100
        self.nFDTdataRecors=0     #No Of FDT data records in this file (0 or more)
        self.RadarUnitId= 0
        self.SiteName= ""
        self.size = 48
 
        #self.useLocalTime = useLocalTime
    
    def read(self, fp):
        
        try:
            header = numpy.fromfile(fp, FILE_STRUCTURE,1)
            '''      numpy.fromfile(file, dtype, count, sep='')
            file : file or str
            Open file object or filename.

            dtype : data-type
            Data type of the returned array. For binary files, it is used to determine 
            the size and byte-order of the items in the file.

            count : int
            Number of items to read. -1 means all items (i.e., the complete file).

            sep : str
            Separator between items if file is a text file. Empty (“”) separator means 
            the file should be treated as binary. Spaces (” ”) in the separator match zero 
            or more whitespace characters. A separator consisting only of spaces must match 
            at least one whitespace.

            '''
            
        except Exception as e:
            print("FileHeader: ")
            print(eBasicHeader)
            return 0
        
        self.FileMgcNumber= byte(header['FileMgcNumber'][0])
        self.nFDTdataRecors=int(header['nFDTdataRecors'][0])     #No Of FDT data records in this file (0 or more)
        self.RadarUnitId= int(header['RadarUnitId'][0])
        self.SiteName= char(header['SiteName'][0])
        

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
        Separator between array items for text output. If “” (empty), a binary file is written, 
        equivalent to file.write(a.tobytes()).

        format : str
        Format string for text file output. Each entry in the array is formatted to text by 
        first converting it to the closest Python type, and then using “format” % item.

        '''
        
        return 1
    

class RecordHeader(Header):
    
    RecMgcNumber=None     #0x23030001
    RecCounter= None      
    Off2StartNxtRec= None      
    EpTimeStamp= None        
    msCompTimeStamp= None  
    ExpTagName= None      
    ExpComment=None      
    SiteLatDegrees=None  
    SiteLongDegrees= None 
    RTCgpsStatus= None    
    TransmitFrec= None    
    ReceiveFrec= None     
    FirstOsciFrec= None    
    Polarisation= None    
    ReceiverFiltSett= None
    nModesInUse= None     
    DualModeIndex= None   
    DualModeRange= None   
    nDigChannels= None
    SampResolution= None
    nRangeGatesSamp= None
    StartRangeSamp= None
    PRFhz= None
    Integrations= None
    nDataPointsTrsf= None
    nReceiveBeams= None
    nSpectAverages= None
    FFTwindowingInd= None
    BeamAngleAzim= None
    BeamAngleZen= None
    AntennaCoord= None
    RecPhaseCalibr= None
    RecAmpCalibr= None
    ReceiverGaindB= None
    
    '''size = None
    nSamples = None
    nProfiles = None
    nChannels = None
    adcResolution = None
    pciDioBusWidth = None'''
        
    def __init__(self,      RecMgcNumber=None,    RecCounter= 0,       Off2StartNxtRec= 0,      
                            EpTimeStamp= 0,    msCompTimeStamp= 0,  ExpTagName= None,      
                            ExpComment=None,      SiteLatDegrees=0,    SiteLongDegrees= 0, 
                            RTCgpsStatus= 0,   TransmitFrec= 0,     ReceiveFrec= 0,     
                            FirstOsciFrec= 0,  Polarisation= 0,     ReceiverFiltSett= 0,
                            nModesInUse= 0,    DualModeIndex= 0,    DualModeRange= 0,   
                            nDigChannels= 0,   SampResolution= 0,   nRangeGatesSamp= 0,
                            StartRangeSamp= 0, PRFhz= 0,            Integrations= 0,
                            nDataPointsTrsf= 0,  nReceiveBeams= 0,  nSpectAverages= 0,
                            FFTwindowingInd= 0,  BeamAngleAzim= 0,  BeamAngleZen= 0,
                            AntennaCoord= 0,   RecPhaseCalibr= 0,   RecAmpCalibr= 0,
                            ReceiverGaindB= 0):
        
        self.RecMgcNumber = RecMgcNumber     #0x23030001
        self.RecCounter = RecCounter      
        self.Off2StartNxtRec = Off2StartNxtRec       
        self.EpTimeStamp = EpTimeStamp         
        self.msCompTimeStamp = msCompTimeStamp   
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
        self.nRangeGatesSamp = nRangeGatesSamp 
        self.StartRangeSamp = StartRangeSamp 
        self.PRFhz = PRFhz 
        self.Integrations = Integrations 
        self.nDataPointsTrsf = nDataPointsTrsf 
        self.nReceiveBeams = nReceiveBeams 
        self.nSpectAverages = nSpectAverages 
        self.FFTwindowingInd = FFTwindowingInd 
        self.BeamAngleAzim = BeamAngleAzim 
        self.BeamAngleZen = BeamAngleZen 
        self.AntennaCoord = AntennaCoord 
        self.RecPhaseCalibr = RecPhaseCalibr 
        self.RecAmpCalibr = RecAmpCalibr 
        self.ReceiverGaindB = ReceiverGaindB 
        
        
    def read(self, fp):
        
        startFp = fp.tell() #The method tell() returns the current position of the file read/write pointer within the file.
        
        try:
            header = numpy.fromfile(fp,RECORD_STRUCTURE,1)
        except Exception as e:
            print("System Header: " + e)
            return 0
        
        self.RecMgcNumber = header['RecMgcNumber'][0]     #0x23030001
        self.RecCounter = header['RecCounter'][0]      
        self.Off2StartNxtRec = header['Off2StartNxtRec'][0]       
        self.EpTimeStamp = header['EpTimeStamp'][0]         
        self.msCompTimeStamp = header['msCompTimeStamp'][0]   
        self.ExpTagName = header['ExpTagName'][0]       
        self.ExpComment = header['ExpComment'][0]      
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
        self.nRangeGatesSamp = header['nRangeGatesSamp'][0] 
        self.StartRangeSamp = header['StartRangeSamp'][0] 
        self.PRFhz = header['PRFhz'][0] 
        self.Integrations = header['Integrations'][0] 
        self.nDataPointsTrsf = header['nDataPointsTrsf'][0] 
        self.nReceiveBeams = header['nReceiveBeams'][0] 
        self.nSpectAverages = header['nSpectAverages'][0] 
        self.FFTwindowingInd = header['FFTwindowingInd'][0] 
        self.BeamAngleAzim = header['BeamAngleAzim'][0] 
        self.BeamAngleZen = header['BeamAngleZen'][0] 
        self.AntennaCoord = header['AntennaCoord'][0] 
        self.RecPhaseCalibr = header['RecPhaseCalibr'][0] 
        self.RecAmpCalibr = header['RecAmpCalibr'][0] 
        self.ReceiverGaindB = header['ReceiverGaindB'][0]
        
        Self.size = 180+20*3
        
        endFp = self.size + startFp
        
        if fp.tell() > endFp:
            sys.stderr.write("Warning %s: Size value read from System Header is lower than it has to be\n" %fp.name)
            return 0
            
        if fp.tell() < endFp:
            sys.stderr.write("Warning %s: Size value read from System Header size is greater than it has to be\n" %fp.name)
            return 0
        
        return 1
    
    def write(self, fp):
        
        headerTuple = (self.RecMgcNumber,
                       self.RecCounter,      
                       self.Off2StartNxtRec,       
                       self.EpTimeStamp,         
                       self.msCompTimeStamp,   
                       self.ExpTagName,       
                       self.ExpComment,      
                       self.SiteLatDegrees,  
                       self.SiteLongDegrees,  
                       self.RTCgpsStatus,     
                       self.TransmitFrec,     
                       self.ReceiveFrec,      
                       self.FirstOsciFrec,     
                       self.Polarisation,     
                       self.ReceiverFiltSett, 
                       self.nModesInUse,      
                       self.DualModeIndex,    
                       self.DualModeRange,    
                       self.nDigChannels,
                       self.SampResolution, 
                       self.nRangeGatesSamp, 
                       self.StartRangeSamp, 
                       self.PRFhz, 
                       self.Integrations, 
                       self.nDataPointsTrsf, 
                       self.nReceiveBeams, 
                       self.nSpectAverages, 
                       self.FFTwindowingInd, 
                       self.BeamAngleAzim, 
                       self.BeamAngleZen, 
                       self.AntennaCoord, 
                       self.RecPhaseCalibr, 
                       self.RecAmpCalibr, 
                       self.ReceiverGaindB) 
                       
#                        self.size,self.nSamples,
#                        self.nProfiles,
#                        self.nChannels,
#                        self.adcResolution,
#                        self.pciDioBusWidth
                       
        header = numpy.array(headerTuple,RECORD_STRUCTURE)
        header.tofile(fp)
        
        return 1

    
def get_dtype_index(numpy_dtype):
    
    index = None
    
    for i in range(len(NUMPY_DTYPE_LIST)):
        if numpy_dtype == NUMPY_DTYPE_LIST[i]:
            index = i
            break
    
    return index

def get_numpy_dtype(index):
    
    #dtype4 = numpy.dtype([('real','<f4'),('imag','<f4')])
    
    return NUMPY_DTYPE_LIST[index]


def get_dtype_width(index):
    
    return DTYPE_WIDTH[index]