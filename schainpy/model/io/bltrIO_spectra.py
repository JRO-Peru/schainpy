import os
import sys
import glob
import fnmatch
import datetime
import time
import re
import h5py
import numpy

import pylab as plb
from scipy.optimize import curve_fit
from scipy import asarray as ar, exp

SPEED_OF_LIGHT = 299792458
SPEED_OF_LIGHT = 3e8

from .utils import folder_in_range

import schainpy.admin
from schainpy.model.data.jrodata import Spectra
from schainpy.model.proc.jroproc_base import ProcessingUnit, Operation, MPDecorator
from schainpy.utils import log
from schainpy.model.io.jroIO_base import JRODataReader

def pol2cart(rho, phi):
    x = rho * numpy.cos(phi)
    y = rho * numpy.sin(phi)
    return(x, y)

FILE_STRUCTURE = numpy.dtype([  # HEADER 48bytes
    ('FileMgcNumber', '<u4'),  # 0x23020100
    ('nFDTdataRecors', '<u4'),
    ('OffsetStartHeader', '<u4'),
    ('RadarUnitId', '<u4'),
    ('SiteName', 'S32'),  # Null terminated
])


class FileHeaderBLTR():

    def __init__(self, fo):

        self.fo = fo
        self.size = 48
        self.read()

    def read(self):

        header = numpy.fromfile(self.fo, FILE_STRUCTURE, 1)
        self.FileMgcNumber = hex(header['FileMgcNumber'][0])
        self.nFDTdataRecors = int(header['nFDTdataRecors'][0])
        self.RadarUnitId = int(header['RadarUnitId'][0])
        self.OffsetStartHeader = int(header['OffsetStartHeader'][0])
        self.SiteName = header['SiteName'][0]

    def write(self, fp):

        headerTuple = (self.FileMgcNumber,
                       self.nFDTdataRecors,
                       self.RadarUnitId,
                       self.SiteName,
                       self.size)

        header = numpy.array(headerTuple, FILE_STRUCTURE)
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


RECORD_STRUCTURE = numpy.dtype([  # RECORD HEADER 180+20N bytes
    ('RecMgcNumber', '<u4'),  # 0x23030001
    ('RecCounter', '<u4'),  # Record counter(0,1, ...)
    # Offset to start of next record form start of this record
                            ('Off2StartNxtRec', '<u4'),
                            # Offset to start of data from start of this record
                            ('Off2StartData', '<u4'),
                            # Epoch time stamp of start of acquisition (seconds)
                            ('nUtime', '<i4'),
                            # Millisecond component of time stamp (0,...,999)
                            ('nMilisec', '<u4'),
                            # Experiment tag name (null terminated)
                            ('ExpTagName', 'S32'),
                            # Experiment comment (null terminated)
                            ('ExpComment', 'S32'),
                            # Site latitude (from GPS) in degrees (positive implies North)
                            ('SiteLatDegrees', '<f4'),
                            # Site longitude (from GPS) in degrees (positive implies East)
                            ('SiteLongDegrees', '<f4'),
                            # RTC GPS engine status (0=SEEK, 1=LOCK, 2=NOT FITTED, 3=UNAVAILABLE)
                            ('RTCgpsStatus', '<u4'),
                            ('TransmitFrec', '<u4'),  # Transmit frequency (Hz)
                            ('ReceiveFrec', '<u4'),  # Receive frequency
                            # First local oscillator frequency (Hz)
                            ('FirstOsciFrec', '<u4'),
                            # (0="O", 1="E", 2="linear 1", 3="linear2")
                            ('Polarisation', '<u4'),
                            # Receiver filter settings (0,1,2,3)
                            ('ReceiverFiltSett', '<u4'),
                            # Number of modes in use (1 or 2)
                            ('nModesInUse', '<u4'),
                            # Dual Mode index number for these data (0 or 1)
                            ('DualModeIndex', '<u4'),
                            # Dual Mode range correction for these data (m)
                            ('DualModeRange', '<u4'),
                            # Number of digital channels acquired (2*N)
                            ('nDigChannels', '<u4'),
                            # Sampling resolution (meters)
                            ('SampResolution', '<u4'),
                            # Number of range gates sampled
                            ('nHeights', '<u4'),
                            # Start range of sampling (meters)
                            ('StartRangeSamp', '<u4'),
                            ('PRFhz', '<u4'),  # PRF (Hz)
                            ('nCohInt', '<u4'),  # Integrations
                            # Number of data points transformed
                            ('nProfiles', '<u4'),
                            # Number of receive beams stored in file (1 or N)
                            ('nChannels', '<u4'),
                            ('nIncohInt', '<u4'),  # Number of spectral averages
                            # FFT windowing index (0 = no window)
                            ('FFTwindowingInd', '<u4'),
                            # Beam steer angle (azimuth) in degrees (clockwise from true North)
                            ('BeamAngleAzim', '<f4'),
                            # Beam steer angle (zenith) in degrees (0=> vertical)
                            ('BeamAngleZen', '<f4'),
                            # Antenna coordinates (Range(meters), Bearing(degrees)) - N pairs
                            ('AntennaCoord0', '<f4'),
                            # Antenna coordinates (Range(meters), Bearing(degrees)) - N pairs
                            ('AntennaAngl0', '<f4'),
                            # Antenna coordinates (Range(meters), Bearing(degrees)) - N pairs
                            ('AntennaCoord1', '<f4'),
                            # Antenna coordinates (Range(meters), Bearing(degrees)) - N pairs
                            ('AntennaAngl1', '<f4'),
                            # Antenna coordinates (Range(meters), Bearing(degrees)) - N pairs
                            ('AntennaCoord2', '<f4'),
                            # Antenna coordinates (Range(meters), Bearing(degrees)) - N pairs
                            ('AntennaAngl2', '<f4'),
                            # Receiver phase calibration (degrees) - N values
                            ('RecPhaseCalibr0', '<f4'),
                            # Receiver phase calibration (degrees) - N values
                            ('RecPhaseCalibr1', '<f4'),
                            # Receiver phase calibration (degrees) - N values
                            ('RecPhaseCalibr2', '<f4'),
                            # Receiver amplitude calibration (ratio relative to receiver one) - N values
                            ('RecAmpCalibr0', '<f4'),
                            # Receiver amplitude calibration (ratio relative to receiver one) - N values
                            ('RecAmpCalibr1', '<f4'),
                            # Receiver amplitude calibration (ratio relative to receiver one) - N values
                            ('RecAmpCalibr2', '<f4'),
                            # Receiver gains in dB - N values
                            ('ReceiverGaindB0', '<i4'),
                            # Receiver gains in dB - N values
                            ('ReceiverGaindB1', '<i4'),
                            # Receiver gains in dB - N values
                            ('ReceiverGaindB2', '<i4'),
])


class RecordHeaderBLTR():

    def __init__(self, fo):

        self.fo = fo
        self.OffsetStartHeader = 48
        self.Off2StartNxtRec = 811248

    def read(self, block):
        OffRHeader = self.OffsetStartHeader + block * self.Off2StartNxtRec
        self.fo.seek(OffRHeader, os.SEEK_SET)
        header = numpy.fromfile(self.fo, RECORD_STRUCTURE, 1)
        self.RecMgcNumber = hex(header['RecMgcNumber'][0])  # 0x23030001
        self.RecCounter = int(header['RecCounter'][0])
        self.Off2StartNxtRec = int(header['Off2StartNxtRec'][0])
        self.Off2StartData = int(header['Off2StartData'][0])
        self.nUtime = header['nUtime'][0]
        self.nMilisec = header['nMilisec'][0]
        self.ExpTagName = '' # str(header['ExpTagName'][0])
        self.ExpComment = '' # str(header['ExpComment'][0])
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
        self.ipp = 0.5 * (SPEED_OF_LIGHT / self.PRFhz)
        self.RHsize = 180 + 20 * self.nChannels
        self.Datasize = self.nProfiles * self.nChannels * self.nHeights * 2 * 4
        endFp = self.OffsetStartHeader + self.RecCounter * self.Off2StartNxtRec

        
        if OffRHeader > endFp:
            sys.stderr.write(
                "Warning %s: Size value read from System Header is lower than it has to be\n" % fp)
            return 0

        if OffRHeader < endFp:
            sys.stderr.write(
                "Warning %s: Size value read from System Header size is greater than it has to be\n" % fp)
            return 0

        return 1


class BLTRSpectraReader (ProcessingUnit):

    def __init__(self):

        ProcessingUnit.__init__(self)

        self.ext = ".fdt"
        self.optchar = "P"
        self.fpFile = None
        self.fp = None
        self.BlockCounter = 0
        self.fileSizeByHeader = None
        self.filenameList = []
        self.fileSelector = 0
        self.Off2StartNxtRec = 0
        self.RecCounter = 0
        self.flagNoMoreFiles = 0
        self.data_spc = None
        self.data_cspc = None
        self.path = None
        self.OffsetStartHeader = 0
        self.Off2StartData = 0
        self.ipp = 0
        self.nFDTdataRecors = 0
        self.blocksize = 0
        self.dataOut = Spectra()
        self.dataOut.flagNoData = False

    def search_files(self):
        ''' 
        Function that indicates the number of .fdt files that exist in the folder to be read.
        It also creates an organized list with the names of the files to read.
        '''

        files = glob.glob(os.path.join(self.path, '*{}'.format(self.ext)))
        files = sorted(files)
        for f in files:
            filename = f.split('/')[-1]
            if folder_in_range(filename.split('.')[1], self.startDate, self.endDate, '%Y%m%d'):
                self.filenameList.append(f)

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

    def setup(self, 
              path=None,
              startDate=None,
              endDate=None,
              startTime=None,
              endTime=None,
              walk=True,
              code=None,
              online=False,
              mode=None,
              **kwargs):

        self.isConfig = True

        self.path = path
        self.startDate = startDate
        self.endDate = endDate
        self.startTime = startTime
        self.endTime = endTime
        self.walk = walk
        self.mode = int(mode)
        self.search_files()
        if self.filenameList:
            self.readFile()

    def getData(self):
        '''
        Before starting this function, you should check that there is still an unread file,
        If there are still blocks to read or if the data block is empty.

        You should call the file "read".

        '''

        if self.flagNoMoreFiles:
            self.dataOut.flagNoData = True
            raise schainpy.admin.SchainError('No more files')

        self.readBlock()

    def readFile(self):
        '''
        You must indicate if you are reading in Online or Offline mode and load the
        The parameters for this file reading mode.

        Then you must do 2 actions:

        1. Get the BLTR FileHeader.
        2. Start reading the first block.
        '''
        
        if self.fileSelector < len(self.filenameList):
            log.success('Opening file: {}'.format(self.filenameList[self.fileSelector]), self.name)
            self.fp = open(self.filenameList[self.fileSelector])
            self.fheader = FileHeaderBLTR(self.fp)
            self.rheader = RecordHeaderBLTR(self.fp)
            self.nFDTdataRecors = self.fheader.nFDTdataRecors
            self.fileSelector += 1    
            self.BlockCounter = 0
            return 1
        else:
            self.flagNoMoreFiles = True
            self.dataOut.flagNoData = True
            return 0

    def readBlock(self):
        '''
        It should be checked if the block has data, if it is not passed to the next file.

        Then the following is done:

        1. Read the RecordHeader
        2. Fill the buffer with the current block number.

        '''

        if self.BlockCounter == self.nFDTdataRecors:
            if not self.readFile():
                return
        
        if self.mode == 1:
            self.rheader.read(self.BlockCounter+1)
        elif self.mode == 0:
            self.rheader.read(self.BlockCounter)

        self.RecCounter = self.rheader.RecCounter
        self.OffsetStartHeader = self.rheader.OffsetStartHeader
        self.Off2StartNxtRec = self.rheader.Off2StartNxtRec
        self.Off2StartData = self.rheader.Off2StartData
        self.nProfiles = self.rheader.nProfiles
        self.nChannels = self.rheader.nChannels
        self.nHeights = self.rheader.nHeights
        self.frequency = self.rheader.TransmitFrec
        self.DualModeIndex = self.rheader.DualModeIndex
        self.pairsList = [(0, 1), (0, 2), (1, 2)]
        self.dataOut.pairsList = self.pairsList
        self.nRdPairs = len(self.dataOut.pairsList)
        self.dataOut.nRdPairs = self.nRdPairs
        self.dataOut.heightList = (self.rheader.StartRangeSamp + numpy.arange(self.nHeights) * self.rheader.SampResolution) / 1000.
        self.dataOut.channelList = range(self.nChannels)
        self.dataOut.nProfiles=self.rheader.nProfiles
        self.dataOut.nIncohInt=self.rheader.nIncohInt
        self.dataOut.nCohInt=self.rheader.nCohInt
        self.dataOut.ippSeconds= 1/float(self.rheader.PRFhz)
        self.dataOut.PRF=self.rheader.PRFhz
        self.dataOut.nFFTPoints=self.rheader.nProfiles
        self.dataOut.utctime = self.rheader.nUtime + self.rheader.nMilisec/1000.
        self.dataOut.timeZone = 0
        self.dataOut.useLocalTime = False
        self.dataOut.nmodes = 2
        log.log('Reading block {} - {}'.format(self.BlockCounter, self.dataOut.datatime), self.name)
        OffDATA = self.OffsetStartHeader + self.RecCounter * \
            self.Off2StartNxtRec + self.Off2StartData
        self.fp.seek(OffDATA, os.SEEK_SET)
            
        self.data_fft = numpy.fromfile(self.fp, [('complex','<c8')], self.nProfiles*self.nChannels*self.nHeights )
        self.data_fft = self.data_fft.astype(numpy.dtype('complex'))
        self.data_block = numpy.reshape(self.data_fft,(self.nHeights, self.nChannels, self.nProfiles))
        self.data_block = numpy.transpose(self.data_block, (1,2,0))
        copy = self.data_block.copy()
        spc = copy * numpy.conjugate(copy)
        self.data_spc = numpy.absolute(spc)  # valor absoluto o magnitud
        self.dataOut.data_spc = self.data_spc

        cspc = self.data_block.copy()
        self.data_cspc = self.data_block.copy()
        
        for i in range(self.nRdPairs):
            
            chan_index0 = self.dataOut.pairsList[i][0]
            chan_index1 = self.dataOut.pairsList[i][1]

            self.data_cspc[i, :, :] = cspc[chan_index0, :, :] * numpy.conjugate(cspc[chan_index1, :, :])

        '''Getting Eij and Nij'''
        (AntennaX0, AntennaY0) = pol2cart(
            self.rheader.AntennaCoord0, self.rheader.AntennaAngl0 * numpy.pi / 180)
        (AntennaX1, AntennaY1) = pol2cart(
            self.rheader.AntennaCoord1, self.rheader.AntennaAngl1 * numpy.pi / 180)
        (AntennaX2, AntennaY2) = pol2cart(
            self.rheader.AntennaCoord2, self.rheader.AntennaAngl2 * numpy.pi / 180)

        E01 = AntennaX0 - AntennaX1
        N01 = AntennaY0 - AntennaY1

        E02 = AntennaX0 - AntennaX2
        N02 = AntennaY0 - AntennaY2

        E12 = AntennaX1 - AntennaX2
        N12 = AntennaY1 - AntennaY2

        self.ChanDist = numpy.array(
            [[E01, N01], [E02, N02], [E12, N12]])

        self.dataOut.ChanDist = self.ChanDist

        self.BlockCounter += 2
        self.dataOut.data_spc = self.data_spc
        self.dataOut.data_cspc =self.data_cspc
