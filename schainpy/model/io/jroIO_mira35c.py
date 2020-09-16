import os
import sys
import glob
import fnmatch
import datetime
import time
import re
import h5py
import numpy

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
from numpy import imag, shape, NaN, empty


class Header(object):

    def __init__(self):
        raise NotImplementedError

    def read(self):

        raise NotImplementedError

    def write(self):

        raise NotImplementedError

    def printInfo(self):

        message = "#" * 50 + "\n"
        message += self.__class__.__name__.upper() + "\n"
        message += "#" * 50 + "\n"

        keyList = list(self.__dict__.keys())
        keyList.sort()

        for key in keyList:
            message += "%s = %s" % (key, self.__dict__[key]) + "\n"

        if "size" not in keyList:
            attr = getattr(self, "size")

            if attr:
                message += "%s = %s" % ("size", attr) + "\n"

        # print message


FILE_HEADER = numpy.dtype([  # HEADER 1024bytes
                          ('Hname', 'a32'),  # Original file name
                          # Date and time when the file was created
                          ('Htime', numpy.str_, 32),
                          # Name of operator who created the file
                          ('Hoper', numpy.str_, 64),
                          # Place where the measurements was carried out
                          ('Hplace', numpy.str_, 128),
                          # Description of measurements
                          ('Hdescr', numpy.str_, 256),
                          ('Hdummy', numpy.str_, 512),  # Reserved space
                          # Main chunk 8bytes
                          # Main chunk signature FZKF or NUIG
                          ('Msign', numpy.str_, 4),
                          ('MsizeData', '<i4'),  # Size of data block main chunk
                          # Processing DSP parameters 36bytes
                          ('PPARsign', numpy.str_, 4),  # PPAR signature
                          ('PPARsize', '<i4'),  # PPAR size of block
                          ('PPARprf', '<i4'),  # Pulse repetition frequency
                          ('PPARpdr', '<i4'),  # Pulse duration
                          ('PPARsft', '<i4'),  # FFT length
                          # Number of spectral (in-coherent) averages
                          ('PPARavc', '<i4'),
                          # Number of lowest range gate for moment estimation
                          ('PPARihp', '<i4'),
                          # Count for gates for moment estimation
                          ('PPARchg', '<i4'),
                          # switch on/off polarimetric measurements. Should be 1.
                          ('PPARpol', '<i4'),
                          # Service DSP parameters 112bytes
                          # STC attenuation on the lowest ranges on/off
                          ('SPARatt', '<i4'),
                          ('SPARtx', '<i4'),  # OBSOLETE
                          ('SPARaddGain0', '<f4'),  # OBSOLETE
                          ('SPARaddGain1', '<f4'),  # OBSOLETE
                          # Debug only. It normal mode it is 0.
                          ('SPARwnd', '<i4'),
                          # Delay between sync pulse and tx pulse for phase corr, ns
                          ('SPARpos', '<i4'),
                          # "add to pulse" to compensate for delay between the leading edge of driver pulse and envelope of the RF signal.
                          ('SPARadd', '<i4'),
                          # Time for measuring txn pulse phase. OBSOLETE
                          ('SPARlen', '<i4'),
                          ('SPARcal', '<i4'),  # OBSOLETE
                          ('SPARnos', '<i4'),  # OBSOLETE
                          ('SPARof0', '<i4'),  # detection threshold
                          ('SPARof1', '<i4'),  # OBSOLETE
                          ('SPARswt', '<i4'),  # 2nd moment estimation threshold
                          ('SPARsum', '<i4'),  # OBSOLETE
                          ('SPARosc', '<i4'),  # flag Oscillosgram mode
                          ('SPARtst', '<i4'),  # OBSOLETE
                          ('SPARcor', '<i4'),  # OBSOLETE
                          ('SPARofs', '<i4'),  # OBSOLETE
                          # Hildebrand div noise detection on noise gate
                          ('SPARhsn', '<i4'),
                          # Hildebrand div noise detection on all gates
                          ('SPARhsa', '<f4'),
                          ('SPARcalibPow_M', '<f4'),  # OBSOLETE
                          ('SPARcalibSNR_M', '<f4'),  # OBSOLETE
                          ('SPARcalibPow_S', '<f4'),  # OBSOLETE
                          ('SPARcalibSNR_S', '<f4'),  # OBSOLETE
                          # Lowest range gate for spectra saving Raw_Gate1 >=5
                          ('SPARrawGate1', '<i4'),
                          # Number of range gates with atmospheric signal
                          ('SPARrawGate2', '<i4'),
                          # flag - IQ or spectra saving on/off
                          ('SPARraw', '<i4'),
                          ('SPARprc', '<i4'), ])  # flag - Moment estimation switched on/off


class FileHeaderMIRA35c(Header):

    def __init__(self):

        self.Hname = None
        self.Htime = None
        self.Hoper = None
        self.Hplace = None
        self.Hdescr = None
        self.Hdummy = None

        self.Msign = None
        self.MsizeData = None

        self.PPARsign = None
        self.PPARsize = None
        self.PPARprf = None
        self.PPARpdr = None
        self.PPARsft = None
        self.PPARavc = None
        self.PPARihp = None
        self.PPARchg = None
        self.PPARpol = None
        # Service DSP parameters
        self.SPARatt = None
        self.SPARtx = None
        self.SPARaddGain0 = None
        self.SPARaddGain1 = None
        self.SPARwnd = None
        self.SPARpos = None
        self.SPARadd = None
        self.SPARlen = None
        self.SPARcal = None
        self.SPARnos = None
        self.SPARof0 = None
        self.SPARof1 = None
        self.SPARswt = None
        self.SPARsum = None
        self.SPARosc = None
        self.SPARtst = None
        self.SPARcor = None
        self.SPARofs = None
        self.SPARhsn = None
        self.SPARhsa = None
        self.SPARcalibPow_M = None
        self.SPARcalibSNR_M = None
        self.SPARcalibPow_S = None
        self.SPARcalibSNR_S = None
        self.SPARrawGate1 = None
        self.SPARrawGate2 = None
        self.SPARraw = None
        self.SPARprc = None

        self.FHsize = 1180

    def FHread(self, fp):

        header = numpy.fromfile(fp, FILE_HEADER, 1)
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

        self.Hname = str(header['Hname'][0])
        self.Htime = str(header['Htime'][0])
        self.Hoper = str(header['Hoper'][0])
        self.Hplace = str(header['Hplace'][0])
        self.Hdescr = str(header['Hdescr'][0])
        self.Hdummy = str(header['Hdummy'][0])
        # 1024

        self.Msign = str(header['Msign'][0])
        self.MsizeData = header['MsizeData'][0]
        # 8

        self.PPARsign = str(header['PPARsign'][0])
        self.PPARsize = header['PPARsize'][0]
        self.PPARprf = header['PPARprf'][0]
        self.PPARpdr = header['PPARpdr'][0]
        self.PPARsft = header['PPARsft'][0]
        self.PPARavc = header['PPARavc'][0]
        self.PPARihp = header['PPARihp'][0]
        self.PPARchg = header['PPARchg'][0]
        self.PPARpol = header['PPARpol'][0]
        # Service DSP parameters
        # 36

        self.SPARatt = header['SPARatt'][0]
        self.SPARtx = header['SPARtx'][0]
        self.SPARaddGain0 = header['SPARaddGain0'][0]
        self.SPARaddGain1 = header['SPARaddGain1'][0]
        self.SPARwnd = header['SPARwnd'][0]
        self.SPARpos = header['SPARpos'][0]
        self.SPARadd = header['SPARadd'][0]
        self.SPARlen = header['SPARlen'][0]
        self.SPARcal = header['SPARcal'][0]
        self.SPARnos = header['SPARnos'][0]
        self.SPARof0 = header['SPARof0'][0]
        self.SPARof1 = header['SPARof1'][0]
        self.SPARswt = header['SPARswt'][0]
        self.SPARsum = header['SPARsum'][0]
        self.SPARosc = header['SPARosc'][0]
        self.SPARtst = header['SPARtst'][0]
        self.SPARcor = header['SPARcor'][0]
        self.SPARofs = header['SPARofs'][0]
        self.SPARhsn = header['SPARhsn'][0]
        self.SPARhsa = header['SPARhsa'][0]
        self.SPARcalibPow_M = header['SPARcalibPow_M'][0]
        self.SPARcalibSNR_M = header['SPARcalibSNR_M'][0]
        self.SPARcalibPow_S = header['SPARcalibPow_S'][0]
        self.SPARcalibSNR_S = header['SPARcalibSNR_S'][0]
        self.SPARrawGate1 = header['SPARrawGate1'][0]
        self.SPARrawGate2 = header['SPARrawGate2'][0]
        self.SPARraw = header['SPARraw'][0]
        self.SPARprc = header['SPARprc'][0]
        # 112
        # 1180
        # print 'Pointer fp header', fp.tell()
        # print ' '
        # print 'SPARrawGate'
        # print self.SPARrawGate2 - self.SPARrawGate1

        # print ' '
        # print 'Hname'
        # print self.Hname

        # print ' '
        # print 'Msign'
        # print self.Msign

    def write(self, fp):

        headerTuple = (self.Hname,
                       self.Htime,
                       self.Hoper,
                       self.Hplace,
                       self.Hdescr,
                       self.Hdummy)

        header = numpy.array(headerTuple, FILE_HEADER)
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


SRVI_HEADER = numpy.dtype([
                         ('SignatureSRVI1', numpy.str_, 4),
                         ('SizeOfDataBlock1', '<i4'),
                         ('DataBlockTitleSRVI1', numpy.str_, 4),
                         ('SizeOfSRVI1', '<i4'), ])


class SRVIHeader(Header):
    def __init__(self,     SignatureSRVI1=0,     SizeOfDataBlock1=0,     DataBlockTitleSRVI1=0,    SizeOfSRVI1=0):

        self.SignatureSRVI1 = SignatureSRVI1
        self.SizeOfDataBlock1 = SizeOfDataBlock1
        self.DataBlockTitleSRVI1 = DataBlockTitleSRVI1
        self.SizeOfSRVI1 = SizeOfSRVI1

        self.SRVIHsize = 16

    def SRVIread(self, fp):

        header = numpy.fromfile(fp, SRVI_HEADER, 1)

        self.SignatureSRVI1 = str(header['SignatureSRVI1'][0])
        self.SizeOfDataBlock1 = header['SizeOfDataBlock1'][0]
        self.DataBlockTitleSRVI1 = str(header['DataBlockTitleSRVI1'][0])
        self.SizeOfSRVI1 = header['SizeOfSRVI1'][0]
        # 16
        print('Pointer fp SRVIheader', fp.tell())


SRVI_STRUCTURE = numpy.dtype([
                            ('frame_cnt', '<u4'),
                            ('time_t', '<u4'),   #
                            ('tpow', '<f4'),     #
                            ('npw1', '<f4'),     #
                            ('npw2', '<f4'),     #
                            ('cpw1', '<f4'),     #
                            ('pcw2', '<f4'),     #
                            ('ps_err', '<u4'),   #
                            ('te_err', '<u4'),   #
                            ('rc_err', '<u4'),   #
                            ('grs1', '<u4'),     #
                            ('grs2', '<u4'),     #
                            ('azipos', '<f4'),     #
                            ('azivel', '<f4'),     #
                            ('elvpos', '<f4'),     #
                            ('elvvel', '<f4'),     #
                            ('northAngle', '<f4'),
                            ('microsec', '<u4'),   #
                            ('azisetvel', '<f4'),  #
                            ('elvsetpos', '<f4'),  #
                            ('RadarConst', '<f4'), ])   #


class RecordHeader(Header):

    def __init__(self,     frame_cnt=0,  time_t=0,  tpow=0,   npw1=0,   npw2=0,
                 cpw1=0,   pcw2=0,       ps_err=0,   te_err=0,   rc_err=0,   grs1=0,
                 grs2=0,   azipos=0,   azivel=0,   elvpos=0,   elvvel=0,   northangle=0,
                 microsec=0,   azisetvel=0,   elvsetpos=0,   RadarConst=0, RecCounter=0, Off2StartNxtRec=0):

        self.frame_cnt = frame_cnt
        self.dwell = time_t
        self.tpow = tpow
        self.npw1 = npw1
        self.npw2 = npw2
        self.cpw1 = cpw1
        self.pcw2 = pcw2
        self.ps_err = ps_err
        self.te_err = te_err
        self.rc_err = rc_err
        self.grs1 = grs1
        self.grs2 = grs2
        self.azipos = azipos
        self.azivel = azivel
        self.elvpos = elvpos
        self.elvvel = elvvel
        self.northAngle = northangle
        self.microsec = microsec
        self.azisetvel = azisetvel
        self.elvsetpos = elvsetpos
        self.RadarConst = RadarConst
        self.RHsize = 84
        self.RecCounter = RecCounter
        self.Off2StartNxtRec = Off2StartNxtRec

    def RHread(self, fp):

        # startFp = open(fp,"rb") #The method tell() returns the current position of the file read/write pointer within the file.

        #OffRHeader= 1180 + self.RecCounter*(self.Off2StartNxtRec)
        #startFp.seek(OffRHeader, os.SEEK_SET)

        # print 'Posicion del bloque:        ',OffRHeader

        header = numpy.fromfile(fp, SRVI_STRUCTURE, 1)

        self.frame_cnt = header['frame_cnt'][0]
        self.time_t = header['time_t'][0]   #
        self.tpow = header['tpow'][0]     #
        self.npw1 = header['npw1'][0]     #
        self.npw2 = header['npw2'][0]     #
        self.cpw1 = header['cpw1'][0]     #
        self.pcw2 = header['pcw2'][0]     #
        self.ps_err = header['ps_err'][0]    #
        self.te_err = header['te_err'][0]    #
        self.rc_err = header['rc_err'][0]    #
        self.grs1 = header['grs1'][0]      #
        self.grs2 = header['grs2'][0]      #
        self.azipos = header['azipos'][0]     #
        self.azivel = header['azivel'][0]     #
        self.elvpos = header['elvpos'][0]     #
        self.elvvel = header['elvvel'][0]     #
        self.northAngle = header['northAngle'][0]    #
        self.microsec = header['microsec'][0]      #
        self.azisetvel = header['azisetvel'][0]     #
        self.elvsetpos = header['elvsetpos'][0]     #
        self.RadarConst = header['RadarConst'][0]    #
        # 84

        # print 'Pointer fp RECheader', fp.tell()

        #self.ipp= 0.5*(SPEED_OF_LIGHT/self.PRFhz)

        #self.RHsize = 180+20*self.nChannels
        #self.Datasize= self.nProfiles*self.nChannels*self.nHeights*2*4
        # print 'Datasize',self.Datasize
        #endFp = self.OffsetStartHeader + self.RecCounter*self.Off2StartNxtRec

        print('==============================================')

        print('==============================================')

        return 1


class MIRA35CReader (ProcessingUnit, FileHeaderMIRA35c, SRVIHeader, RecordHeader):

    path = None
    startDate = None
    endDate = None
    startTime = None
    endTime = None
    walk = None
    isConfig = False

    fileList = None

    # metadata
    TimeZone = None
    Interval = None
    heightList = None

    # data
    data = None
    utctime = None

    def __init__(self, **kwargs):

        # Eliminar de la base la herencia
        ProcessingUnit.__init__(self, **kwargs)
        self.PointerReader = 0
        self.FileHeaderFlag = False
        self.utc = None
        self.ext = ".zspca"
        self.optchar = "P"
        self.fpFile = None
        self.fp = None
        self.BlockCounter = 0
        self.dtype = None
        self.fileSizeByHeader = None
        self.filenameList = []
        self.fileSelector = 0
        self.Off2StartNxtRec = 0
        self.RecCounter = 0
        self.flagNoMoreFiles = 0
        self.data_spc = None
        # self.data_cspc=None
        self.data_output = None
        self.path = None
        self.OffsetStartHeader = 0
        self.Off2StartData = 0
        self.ipp = 0
        self.nFDTdataRecors = 0
        self.blocksize = 0
        self.dataOut = Spectra()
        self.profileIndex = 1  # Always
        self.dataOut.flagNoData = False
        self.dataOut.nRdPairs = 0        
        self.dataOut.data_spc = None        
        self.nextfileflag = True
        self.dataOut.RadarConst = 0
        self.dataOut.HSDV = []
        self.dataOut.NPW = []
        self.dataOut.COFA = []
        # self.dataOut.noise = 0

    def Files2Read(self, fp):
        ''' 
        Function that indicates the number of .fdt files that exist in the folder to be read.
        It also creates an organized list with the names of the files to read.
        '''
        # self.__checkPath()

        # Gets the list of files within the fp address
        ListaData = os.listdir(fp)
        # Sort the list of files from least to largest by names
        ListaData = sorted(ListaData)
        nFiles = 0  # File Counter
        FileList = []  # A list is created that will contain the .fdt files
        for IndexFile in ListaData:
            if '.zspca' in IndexFile and '.gz' not in IndexFile:
                FileList.append(IndexFile)
                nFiles += 1

        # print 'Files2Read'
        # print 'Existen '+str(nFiles)+' archivos .fdt'

        self.filenameList = FileList  # List of files from least to largest by names

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

    def setup(self, path=None,
              startDate=None,
              endDate=None,
              startTime=None,
              endTime=None,
              walk=True,
              timezone='utc',
              code=None,
              online=False,
              ReadMode=None, **kwargs):

        self.isConfig = True

        self.path = path
        self.startDate = startDate
        self.endDate = endDate
        self.startTime = startTime
        self.endTime = endTime
        self.walk = walk
        # self.ReadMode=int(ReadMode)

        pass

    def getData(self):
        '''
        Before starting this function, you should check that there is still an unread file,
        If there are still blocks to read or if the data block is empty.

        You should call the file "read".

        '''

        if self.flagNoMoreFiles:
            self.dataOut.flagNoData = True
            print('NoData se vuelve true')
            return 0

        self.fp = self.path
        self.Files2Read(self.fp)
        self.readFile(self.fp)

        self.dataOut.data_spc = self.dataOut_spc  # self.data_spc.copy()
        self.dataOut.RadarConst = self.RadarConst
        self.dataOut.data_output = self.data_output
        self.dataOut.noise = self.dataOut.getNoise()
        # print 'ACAAAAAA', self.dataOut.noise
        self.dataOut.data_spc = self.dataOut.data_spc + self.dataOut.noise
        self.dataOut.normFactor = 1
        # print 'self.dataOut.noise',self.dataOut.noise

        return self.dataOut.data_spc

    def readFile(self, fp):
        '''
        You must indicate if you are reading in Online or Offline mode and load the
        The parameters for this file reading mode.

        Then you must do 2 actions:

        1. Get the BLTR FileHeader.
        2. Start reading the first block.
        '''

        # The address of the folder is generated the name of the .fdt file that will be read
        print("File:    ", self.fileSelector + 1)

        if self.fileSelector < len(self.filenameList):

            self.fpFile = str(fp) + '/' + \
                str(self.filenameList[self.fileSelector])

            if self.nextfileflag == True:
                self.fp = open(self.fpFile, "rb")
                self.nextfileflag == False

            '''HERE STARTING THE FILE READING'''

            self.fheader = FileHeaderMIRA35c()
            self.fheader.FHread(self.fp)  # Bltr FileHeader Reading

            self.SPARrawGate1 = self.fheader.SPARrawGate1
            self.SPARrawGate2 = self.fheader.SPARrawGate2
            self.Num_Hei = self.SPARrawGate2 - self.SPARrawGate1
            self.Num_Bins = self.fheader.PPARsft
            self.dataOut.nFFTPoints = self.fheader.PPARsft

            self.Num_inCoh = self.fheader.PPARavc
            self.dataOut.PRF = self.fheader.PPARprf
            self.dataOut.frequency = 34.85 * 10**9
            self.Lambda = SPEED_OF_LIGHT / self.dataOut.frequency
            self.dataOut.ippSeconds = 1. / float(self.dataOut.PRF)

            pulse_width = self.fheader.PPARpdr * 10**-9
            self.__deltaHeigth = 0.5 * SPEED_OF_LIGHT * pulse_width

            self.data_spc = numpy.zeros((self.Num_Hei, self.Num_Bins, 2))
            self.dataOut.HSDV = numpy.zeros((self.Num_Hei, 2))

            self.Ze = numpy.zeros(self.Num_Hei)
            self.ETA = numpy.zeros(([2, self.Num_Hei]))

            self.readBlock()  # Block reading

        else:
            print('readFile FlagNoData becomes true')
            self.flagNoMoreFiles = True
            self.dataOut.flagNoData = True
            self.FileHeaderFlag == True
            return 0

    def readBlock(self):
        '''
        It should be checked if the block has data, if it is not passed to the next file.

        Then the following is done:

        1. Read the RecordHeader
        2. Fill the buffer with the current block number.

        '''

        if self.PointerReader > 1180:
            self.fp.seek(self.PointerReader, os.SEEK_SET)
            self.FirstPoint = self.PointerReader

        else:
            self.FirstPoint = 1180

        self.srviHeader = SRVIHeader()

        self.srviHeader.SRVIread(self.fp)  # Se obtiene la cabecera del SRVI

        self.blocksize = self.srviHeader.SizeOfDataBlock1  # Se obtiene el tamao del bloque

        if self.blocksize == 148:
            print('blocksize == 148 bug')
            jump = numpy.fromfile(self.fp, [('jump', numpy.str_, 140)], 1)

            # Se obtiene la cabecera del SRVI
            self.srviHeader.SRVIread(self.fp)

        if not self.srviHeader.SizeOfSRVI1:
            self.fileSelector += 1
            self.nextfileflag == True
            self.FileHeaderFlag == True

        self.recordheader = RecordHeader()
        self.recordheader.RHread(self.fp)
        self.RadarConst = self.recordheader.RadarConst
        dwell = self.recordheader.time_t
        npw1 = self.recordheader.npw1
        npw2 = self.recordheader.npw2

        self.dataOut.channelList = list(range(1))
        self.dataOut.nIncohInt = self.Num_inCoh
        self.dataOut.nProfiles = self.Num_Bins
        self.dataOut.nCohInt = 1
        self.dataOut.windowOfFilter = 1
        self.dataOut.utctime = dwell
        self.dataOut.timeZone = 0

        self.dataOut.outputInterval = self.dataOut.timeInterval
        self.dataOut.heightList = self.SPARrawGate1 * self.__deltaHeigth + \
            numpy.array(list(range(self.Num_Hei))) * self.__deltaHeigth

        self.HSDVsign = numpy.fromfile(self.fp, [('HSDV', numpy.str_, 4)], 1)
        self.SizeHSDV = numpy.fromfile(self.fp, [('SizeHSDV', '<i4')], 1)
        self.HSDV_Co = numpy.fromfile(
            self.fp, [('HSDV_Co', '<f4')], self.Num_Hei)
        self.HSDV_Cx = numpy.fromfile(
            self.fp, [('HSDV_Cx', '<f4')], self.Num_Hei)

        self.COFAsign = numpy.fromfile(self.fp, [('COFA', numpy.str_, 4)], 1)
        self.SizeCOFA = numpy.fromfile(self.fp, [('SizeCOFA', '<i4')], 1)
        self.COFA_Co = numpy.fromfile(
            self.fp, [('COFA_Co', '<f4')], self.Num_Hei)
        self.COFA_Cx = numpy.fromfile(
            self.fp, [('COFA_Cx', '<f4')], self.Num_Hei)

        self.ZSPCsign = numpy.fromfile(
            self.fp, [('ZSPCsign', numpy.str_, 4)], 1)
        self.SizeZSPC = numpy.fromfile(self.fp, [('SizeZSPC', '<i4')], 1)

        self.dataOut.HSDV[0] = self.HSDV_Co[:][0]
        self.dataOut.HSDV[1] = self.HSDV_Cx[:][0]

        for irg in range(self.Num_Hei):
            # Number of spectral sub pieces containing significant power
            nspc = numpy.fromfile(self.fp, [('nspc', 'int16')], 1)[0][0]

            for k in range(nspc):
                # Index of the spectral bin where the piece is beginning
                binIndex = numpy.fromfile(
                    self.fp, [('binIndex', 'int16')], 1)[0][0]
                nbins = numpy.fromfile(self.fp, [('nbins', 'int16')], 1)[
                    0][0]  # Number of bins of the piece

                # Co_Channel
                jbin = numpy.fromfile(self.fp, [('jbin', 'uint16')], nbins)[
                    0][0]  # Spectrum piece to be normaliced
                jmax = numpy.fromfile(self.fp, [('jmax', 'float32')], 1)[
                    0][0]  # Maximun piece to be normaliced

                self.data_spc[irg, binIndex:binIndex + nbins, 0] = self.data_spc[irg,
                                                                                 binIndex:binIndex + nbins, 0] + jbin / 65530. * jmax

                # Cx_Channel
                jbin = numpy.fromfile(
                    self.fp, [('jbin', 'uint16')], nbins)[0][0]
                jmax = numpy.fromfile(self.fp, [('jmax', 'float32')], 1)[0][0]

                self.data_spc[irg, binIndex:binIndex + nbins, 1] = self.data_spc[irg,
                                                                                 binIndex:binIndex + nbins, 1] + jbin / 65530. * jmax

        for bin in range(self.Num_Bins):

            self.data_spc[:, bin, 0] = self.data_spc[:,
                                                     bin, 0] - self.dataOut.HSDV[:, 0]

            self.data_spc[:, bin, 1] = self.data_spc[:,
                                                     bin, 1] - self.dataOut.HSDV[:, 1]

        numpy.set_printoptions(threshold='nan')

        self.data_spc = numpy.where(self.data_spc > 0., self.data_spc, 0)

        self.dataOut.COFA = numpy.array([self.COFA_Co, self.COFA_Cx])

        print(' ')
        print('SPC', numpy.shape(self.dataOut.data_spc))
        # print 'SPC',self.dataOut.data_spc

        noinor1 = 713031680
        noinor2 = 30

        npw1 = 1  # 0**(npw1/10) * noinor1 * noinor2
        npw2 = 1  # 0**(npw2/10) * noinor1 * noinor2
        self.dataOut.NPW = numpy.array([npw1, npw2])

        print(' ')

        self.data_spc = numpy.transpose(self.data_spc, (2, 1, 0))
        self.data_spc = numpy.fft.fftshift(self.data_spc, axes=1)

        self.data_spc = numpy.fliplr(self.data_spc)

        self.data_spc = numpy.where(self.data_spc > 0., self.data_spc, 0)
        self.dataOut_spc = numpy.ones([1, self.Num_Bins, self.Num_Hei])
        self.dataOut_spc[0, :, :] = self.data_spc[0, :, :]
        # print 'SHAPE', self.dataOut_spc.shape
        # For nyquist correction:
        # fix = 20 # ~3m/s
        #shift = self.Num_Bins/2 + fix
        #self.data_spc = numpy.array([ self.data_spc[: , self.Num_Bins-shift+1: , :] , self.data_spc[: , 0:self.Num_Bins-shift , :]])

        '''Block Reading, the Block Data is received and Reshape is used to give it
        shape.
        '''

        self.PointerReader = self.fp.tell()