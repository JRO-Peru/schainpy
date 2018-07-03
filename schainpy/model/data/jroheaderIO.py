'''

$Author: murco $
$Id: JROHeaderIO.py 151 2012-10-31 19:00:51Z murco $
'''
import sys
import numpy
import copy
import datetime
import inspect
from schainpy.utils import log

SPEED_OF_LIGHT = 299792458
SPEED_OF_LIGHT = 3e8

BASIC_STRUCTURE = numpy.dtype([
    ('nSize', '<u4'),
    ('nVersion', '<u2'),
    ('nDataBlockId', '<u4'),
    ('nUtime', '<u4'),
    ('nMilsec', '<u2'),
    ('nTimezone', '<i2'),
    ('nDstflag', '<i2'),
    ('nErrorCount', '<u4')
])

SYSTEM_STRUCTURE = numpy.dtype([
    ('nSize', '<u4'),
    ('nNumSamples', '<u4'),
    ('nNumProfiles', '<u4'),
    ('nNumChannels', '<u4'),
    ('nADCResolution', '<u4'),
    ('nPCDIOBusWidth', '<u4'),
])

RADAR_STRUCTURE = numpy.dtype([
                             ('nSize', '<u4'),
                             ('nExpType', '<u4'),
                             ('nNTx', '<u4'),
                             ('fIpp', '<f4'),
                             ('fTxA', '<f4'),
                             ('fTxB', '<f4'),
                             ('nNumWindows', '<u4'),
                             ('nNumTaus', '<u4'),
                             ('nCodeType', '<u4'),
                             ('nLine6Function', '<u4'),
                             ('nLine5Function', '<u4'),
                             ('fClock', '<f4'),
                             ('nPrePulseBefore', '<u4'),
                             ('nPrePulseAfter', '<u4'),
                             ('sRangeIPP', '<a20'),
                             ('sRangeTxA', '<a20'),
                             ('sRangeTxB', '<a20'),
])

SAMPLING_STRUCTURE = numpy.dtype(
    [('h0', '<f4'), ('dh', '<f4'), ('nsa', '<u4')])


PROCESSING_STRUCTURE = numpy.dtype([
    ('nSize', '<u4'),
    ('nDataType', '<u4'),
    ('nSizeOfDataBlock', '<u4'),
    ('nProfilesperBlock', '<u4'),
    ('nDataBlocksperFile', '<u4'),
    ('nNumWindows', '<u4'),
    ('nProcessFlags', '<u4'),
    ('nCoherentIntegrations', '<u4'),
    ('nIncoherentIntegrations', '<u4'),
    ('nTotalSpectra', '<u4')
])


class Header(object):

    def __init__(self):
        raise NotImplementedError

    def copy(self):
        return copy.deepcopy(self)

    def read(self):

        raise NotImplementedError

    def write(self):

        raise NotImplementedError

    def getAllowedArgs(self):
        args = inspect.getargspec(self.__init__).args
        try:
            args.remove('self')
        except:
            pass
        return args

    def getAsDict(self):
        args = self.getAllowedArgs()
        asDict = {}
        for x in args:
            asDict[x] = self[x]
        return asDict

    def __getitem__(self, name):
        return getattr(self, name)

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

        print(message)


class BasicHeader(Header):

    size = None
    version = None
    dataBlock = None
    utc = None
    ltc = None
    miliSecond = None
    timeZone = None
    dstFlag = None
    errorCount = None
    datatime = None
    structure = BASIC_STRUCTURE
    __LOCALTIME = None

    def __init__(self, useLocalTime=True):

        self.size = 24
        self.version = 0
        self.dataBlock = 0
        self.utc = 0
        self.miliSecond = 0
        self.timeZone = 0
        self.dstFlag = 0
        self.errorCount = 0

        self.useLocalTime = useLocalTime

    def read(self, fp):

        self.length = 0
        try:
            if hasattr(fp, 'read'):
                header = numpy.fromfile(fp, BASIC_STRUCTURE, 1)
            else:
                header = numpy.fromstring(fp, BASIC_STRUCTURE, 1)
        except Exception as e:
            print("BasicHeader: ")
            print(e)
            return 0

        self.size = int(header['nSize'][0])
        self.version = int(header['nVersion'][0])
        self.dataBlock = int(header['nDataBlockId'][0])
        self.utc = int(header['nUtime'][0])
        self.miliSecond = int(header['nMilsec'][0])
        self.timeZone = int(header['nTimezone'][0])
        self.dstFlag = int(header['nDstflag'][0])
        self.errorCount = int(header['nErrorCount'][0])

        if self.size < 24:
            return 0

        self.length = header.nbytes
        return 1

    def write(self, fp):

        headerTuple = (self.size, self.version, self.dataBlock, self.utc,
                       self.miliSecond, self.timeZone, self.dstFlag, self.errorCount)
        header = numpy.array(headerTuple, BASIC_STRUCTURE)
        header.tofile(fp)

        return 1

    def get_ltc(self):

        return self.utc - self.timeZone * 60

    def set_ltc(self, value):

        self.utc = value + self.timeZone * 60

    def get_datatime(self):

        return datetime.datetime.utcfromtimestamp(self.ltc)

    ltc = property(get_ltc, set_ltc)
    datatime = property(get_datatime)


class SystemHeader(Header):

    size = None
    nSamples = None
    nProfiles = None
    nChannels = None
    adcResolution = None
    pciDioBusWidth = None
    structure = SYSTEM_STRUCTURE

    def __init__(self, nSamples=0, nProfiles=0, nChannels=0, adcResolution=14, pciDioBusWidth=0):

        self.size = 24
        self.nSamples = nSamples
        self.nProfiles = nProfiles
        self.nChannels = nChannels
        self.adcResolution = adcResolution
        self.pciDioBusWidth = pciDioBusWidth

    def read(self, fp):
        self.length = 0
        try:
            startFp = fp.tell()
        except Exception as e:
            startFp = None
            pass

        try:
            if hasattr(fp, 'read'):
                header = numpy.fromfile(fp, SYSTEM_STRUCTURE, 1)
            else:
                header = numpy.fromstring(fp, SYSTEM_STRUCTURE, 1)
        except Exception as e:
            print("System Header: " + str(e))
            return 0

        self.size = header['nSize'][0]
        self.nSamples = header['nNumSamples'][0]
        self.nProfiles = header['nNumProfiles'][0]
        self.nChannels = header['nNumChannels'][0]
        self.adcResolution = header['nADCResolution'][0]
        self.pciDioBusWidth = header['nPCDIOBusWidth'][0]

        if startFp is not None:
            endFp = self.size + startFp

            if fp.tell() > endFp:
                sys.stderr.write(
                    "Warning %s: Size value read from System Header is lower than it has to be\n" % fp.name)
                return 0

            if fp.tell() < endFp:
                sys.stderr.write(
                    "Warning %s: Size value read from System Header size is greater than it has to be\n" % fp.name)
                return 0

        self.length = header.nbytes
        return 1

    def write(self, fp):

        headerTuple = (self.size, self.nSamples, self.nProfiles,
                       self.nChannels, self.adcResolution, self.pciDioBusWidth)
        header = numpy.array(headerTuple, SYSTEM_STRUCTURE)
        header.tofile(fp)

        return 1


class RadarControllerHeader(Header):

    expType = None
    nTx = None
    ipp = None
    txA = None
    txB = None
    nWindows = None
    numTaus = None
    codeType = None
    line6Function = None
    line5Function = None
    fClock = None
    prePulseBefore = None
    prePulseAfter = None
    rangeIpp = None
    rangeTxA = None
    rangeTxB = None
    structure = RADAR_STRUCTURE
    __size = None

    def __init__(self, expType=2, nTx=1,
                 ipp=None, txA=0, txB=0,
                 nWindows=None, nHeights=None, firstHeight=None, deltaHeight=None,
                 numTaus=0, line6Function=0, line5Function=0, fClock=None,
                 prePulseBefore=0, prePulseAfter=0,
                 codeType=0, nCode=0, nBaud=0, code=None,
                 flip1=0, flip2=0):

        #         self.size = 116
        self.expType = expType
        self.nTx = nTx
        self.ipp = ipp
        self.txA = txA
        self.txB = txB
        self.rangeIpp = ipp
        self.rangeTxA = txA
        self.rangeTxB = txB

        self.nWindows = nWindows
        self.numTaus = numTaus
        self.codeType = codeType
        self.line6Function = line6Function
        self.line5Function = line5Function
        self.fClock = fClock
        self.prePulseBefore = prePulseBefore
        self.prePulseAfter = prePulseAfter

        self.nHeights = nHeights
        self.firstHeight = firstHeight
        self.deltaHeight = deltaHeight
        self.samplesWin = nHeights

        self.nCode = nCode
        self.nBaud = nBaud
        self.code = code
        self.flip1 = flip1
        self.flip2 = flip2

        self.code_size = int(numpy.ceil(self.nBaud / 32.)) * self.nCode * 4
#         self.dynamic = numpy.array([],numpy.dtype('byte'))

        if self.fClock is None and self.deltaHeight is not None:
            self.fClock = 0.15 / (deltaHeight * 1e-6)  # 0.15Km / (height * 1u)

    def read(self, fp):
        self.length = 0
        try:
            startFp = fp.tell()
        except Exception as e:
            startFp = None
            pass

        try:
            if hasattr(fp, 'read'):
                header = numpy.fromfile(fp, RADAR_STRUCTURE, 1)
            else:
                header = numpy.fromstring(fp, RADAR_STRUCTURE, 1)
            self.length += header.nbytes
        except Exception as e:
            print("RadarControllerHeader: " + str(e))
            return 0

        size = int(header['nSize'][0])
        self.expType = int(header['nExpType'][0])
        self.nTx = int(header['nNTx'][0])
        self.ipp = float(header['fIpp'][0])
        self.txA = float(header['fTxA'][0])
        self.txB = float(header['fTxB'][0])
        self.nWindows = int(header['nNumWindows'][0])
        self.numTaus = int(header['nNumTaus'][0])
        self.codeType = int(header['nCodeType'][0])
        self.line6Function = int(header['nLine6Function'][0])
        self.line5Function = int(header['nLine5Function'][0])
        self.fClock = float(header['fClock'][0])
        self.prePulseBefore = int(header['nPrePulseBefore'][0])
        self.prePulseAfter = int(header['nPrePulseAfter'][0])
        self.rangeIpp = header['sRangeIPP'][0]
        self.rangeTxA = header['sRangeTxA'][0]
        self.rangeTxB = header['sRangeTxB'][0]

        try:
            if hasattr(fp, 'read'):
                samplingWindow = numpy.fromfile(
                    fp, SAMPLING_STRUCTURE, self.nWindows)
            else:
                samplingWindow = numpy.fromstring(
                    fp[self.length:], SAMPLING_STRUCTURE, self.nWindows)
            self.length += samplingWindow.nbytes
        except Exception as e:
            print("RadarControllerHeader: " + str(e))
            return 0
        self.nHeights = int(numpy.sum(samplingWindow['nsa']))
        self.firstHeight = samplingWindow['h0']
        self.deltaHeight = samplingWindow['dh']
        self.samplesWin = samplingWindow['nsa']

        try:
            if hasattr(fp, 'read'):
                self.Taus = numpy.fromfile(fp, '<f4', self.numTaus)
            else:
                self.Taus = numpy.fromstring(
                    fp[self.length:], '<f4', self.numTaus)
            self.length += self.Taus.nbytes
        except Exception as e:
            print("RadarControllerHeader: " + str(e))
            return 0

        self.code_size = 0
        if self.codeType != 0:

            try:
                if hasattr(fp, 'read'):
                    self.nCode = numpy.fromfile(fp, '<u4', 1)[0]
                    self.length += self.nCode.nbytes
                    self.nBaud = numpy.fromfile(fp, '<u4', 1)[0]
                    self.length += self.nBaud.nbytes
                else:
                    self.nCode = numpy.fromstring(
                        fp[self.length:], '<u4', 1)[0]
                    self.length += self.nCode.nbytes
                    self.nBaud = numpy.fromstring(
                        fp[self.length:], '<u4', 1)[0]
                    self.length += self.nBaud.nbytes
            except Exception as e:
                print("RadarControllerHeader: " + str(e))
                return 0
            code = numpy.empty([self.nCode, self.nBaud], dtype='i1')

            for ic in range(self.nCode):
                try:
                    if hasattr(fp, 'read'):
                        temp = numpy.fromfile(fp, 'u4', int(
                            numpy.ceil(self.nBaud / 32.)))
                    else:
                        temp = numpy.fromstring(
                            fp, 'u4', int(numpy.ceil(self.nBaud / 32.)))
                    self.length += temp.nbytes
                except Exception as e:
                    print("RadarControllerHeader: " + str(e))
                    return 0

                for ib in range(self.nBaud - 1, -1, -1):
                    code[ic, ib] = temp[int(ib / 32)] % 2
                    temp[int(ib / 32)] = temp[int(ib / 32)] / 2

            self.code = 2.0 * code - 1.0
            self.code_size = int(numpy.ceil(self.nBaud / 32.)) * self.nCode * 4

#             if self.line5Function == RCfunction.FLIP:
#                 self.flip1 = numpy.fromfile(fp,'<u4',1)
#
#             if self.line6Function == RCfunction.FLIP:
#                 self.flip2 = numpy.fromfile(fp,'<u4',1)
        if startFp is not None:
            endFp = size + startFp

            if fp.tell() != endFp:
                #             fp.seek(endFp)
                print("%s: Radar Controller Header size is not consistent: from data [%d] != from header field [%d]" % (fp.name, fp.tell() - startFp, size))
    #             return 0

            if fp.tell() > endFp:
                sys.stderr.write(
                    "Warning %s: Size value read from Radar Controller header is lower than it has to be\n" % fp.name)
    #             return 0

            if fp.tell() < endFp:
                sys.stderr.write(
                    "Warning %s: Size value read from Radar Controller header is greater than it has to be\n" % fp.name)

        return 1

    def write(self, fp):

        headerTuple = (self.size,
                       self.expType,
                       self.nTx,
                       self.ipp,
                       self.txA,
                       self.txB,
                       self.nWindows,
                       self.numTaus,
                       self.codeType,
                       self.line6Function,
                       self.line5Function,
                       self.fClock,
                       self.prePulseBefore,
                       self.prePulseAfter,
                       self.rangeIpp,
                       self.rangeTxA,
                       self.rangeTxB)

        header = numpy.array(headerTuple, RADAR_STRUCTURE)
        header.tofile(fp)

        sampleWindowTuple = (
            self.firstHeight, self.deltaHeight, self.samplesWin)
        samplingWindow = numpy.array(sampleWindowTuple, SAMPLING_STRUCTURE)
        samplingWindow.tofile(fp)

        if self.numTaus > 0:
            self.Taus.tofile(fp)

        if self.codeType != 0:
            nCode = numpy.array(self.nCode, '<u4')
            nCode.tofile(fp)
            nBaud = numpy.array(self.nBaud, '<u4')
            nBaud.tofile(fp)
            code1 = (self.code + 1.0) / 2.

            for ic in range(self.nCode):
                tempx = numpy.zeros(int(numpy.ceil(self.nBaud / 32.)))
                start = 0
                end = 32
                for i in range(len(tempx)):
                    code_selected = code1[ic, start:end]
                    for j in range(len(code_selected) - 1, -1, -1):
                        if code_selected[j] == 1:
                            tempx[i] = tempx[i] + \
                                2**(len(code_selected) - 1 - j)
                    start = start + 32
                    end = end + 32

                tempx = tempx.astype('u4')
                tempx.tofile(fp)

#         if self.line5Function == RCfunction.FLIP:
#             self.flip1.tofile(fp)
#
#         if self.line6Function == RCfunction.FLIP:
#             self.flip2.tofile(fp)

        return 1

    def get_ippSeconds(self):
        '''
        '''
        ippSeconds = 2.0 * 1000 * self.ipp / SPEED_OF_LIGHT

        return ippSeconds

    def set_ippSeconds(self, ippSeconds):
        '''
        '''

        self.ipp = ippSeconds * SPEED_OF_LIGHT / (2.0 * 1000)

        return

    def get_size(self):

        self.__size = 116 + 12 * self.nWindows + 4 * self.numTaus

        if self.codeType != 0:
            self.__size += 4 + 4 + 4 * self.nCode * \
                numpy.ceil(self.nBaud / 32.)

        return self.__size

    def set_size(self, value):

        raise IOError("size is a property and it cannot be set, just read")

        return

    ippSeconds = property(get_ippSeconds, set_ippSeconds)
    size = property(get_size, set_size)


class ProcessingHeader(Header):

    #     size = None
    dtype = None
    blockSize = None
    profilesPerBlock = None
    dataBlocksPerFile = None
    nWindows = None
    processFlags = None
    nCohInt = None
    nIncohInt = None
    totalSpectra = None
    structure = PROCESSING_STRUCTURE
    flag_dc = None
    flag_cspc = None

    def __init__(self, dtype=0, blockSize=0, profilesPerBlock=0, dataBlocksPerFile=0, nWindows=0, processFlags=0, nCohInt=0,
                 nIncohInt=0, totalSpectra=0, nHeights=0, firstHeight=0, deltaHeight=0, samplesWin=0, spectraComb=0, nCode=0,
                 code=0, nBaud=None, shif_fft=False, flag_dc=False, flag_cspc=False, flag_decode=False, flag_deflip=False
                 ):

        #         self.size = 0
        self.dtype = dtype
        self.blockSize = blockSize
        self.profilesPerBlock = 0
        self.dataBlocksPerFile = 0
        self.nWindows = 0
        self.processFlags = 0
        self.nCohInt = 0
        self.nIncohInt = 0
        self.totalSpectra = 0

        self.nHeights = 0
        self.firstHeight = 0
        self.deltaHeight = 0
        self.samplesWin = 0
        self.spectraComb = 0
        self.nCode = None
        self.code = None
        self.nBaud = None

        self.shif_fft = False
        self.flag_dc = False
        self.flag_cspc = False
        self.flag_decode = False
        self.flag_deflip = False
        self.length = 0

    def read(self, fp):
        self.length = 0
        try:
            startFp = fp.tell()
        except Exception as e:
            startFp = None
            pass

        try:
            if hasattr(fp, 'read'):
                header = numpy.fromfile(fp, PROCESSING_STRUCTURE, 1)
            else:
                header = numpy.fromstring(fp, PROCESSING_STRUCTURE, 1)
            self.length += header.nbytes
        except Exception as e:
            print("ProcessingHeader: " + str(e))
            return 0

        size = int(header['nSize'][0])
        self.dtype = int(header['nDataType'][0])
        self.blockSize = int(header['nSizeOfDataBlock'][0])
        self.profilesPerBlock = int(header['nProfilesperBlock'][0])
        self.dataBlocksPerFile = int(header['nDataBlocksperFile'][0])
        self.nWindows = int(header['nNumWindows'][0])
        self.processFlags = header['nProcessFlags']
        self.nCohInt = int(header['nCoherentIntegrations'][0])
        self.nIncohInt = int(header['nIncoherentIntegrations'][0])
        self.totalSpectra = int(header['nTotalSpectra'][0])

        try:
            if hasattr(fp, 'read'):
                samplingWindow = numpy.fromfile(
                    fp, SAMPLING_STRUCTURE, self.nWindows)
            else:
                samplingWindow = numpy.fromstring(
                    fp[self.length:], SAMPLING_STRUCTURE, self.nWindows)
            self.length += samplingWindow.nbytes
        except Exception as e:
            print("ProcessingHeader: " + str(e))
            return 0

        self.nHeights = int(numpy.sum(samplingWindow['nsa']))
        self.firstHeight = float(samplingWindow['h0'][0])
        self.deltaHeight = float(samplingWindow['dh'][0])
        self.samplesWin = samplingWindow['nsa'][0]

        try:
            if hasattr(fp, 'read'):
                self.spectraComb = numpy.fromfile(
                    fp, 'u1', 2 * self.totalSpectra)
            else:
                self.spectraComb = numpy.fromstring(
                    fp[self.length:], 'u1', 2 * self.totalSpectra)
            self.length += self.spectraComb.nbytes
        except Exception as e:
            print("ProcessingHeader: " + str(e))
            return 0

        if ((self.processFlags & PROCFLAG.DEFINE_PROCESS_CODE) == PROCFLAG.DEFINE_PROCESS_CODE):
            self.nCode = int(numpy.fromfile(fp, '<u4', 1))
            self.nBaud = int(numpy.fromfile(fp, '<u4', 1))
            self.code = numpy.fromfile(
                fp, '<f4', self.nCode * self.nBaud).reshape(self.nCode, self.nBaud)

        if ((self.processFlags & PROCFLAG.EXP_NAME_ESP) == PROCFLAG.EXP_NAME_ESP):
            exp_name_len = int(numpy.fromfile(fp, '<u4', 1))
            exp_name = numpy.fromfile(fp, 'u1', exp_name_len + 1)

        if ((self.processFlags & PROCFLAG.SHIFT_FFT_DATA) == PROCFLAG.SHIFT_FFT_DATA):
            self.shif_fft = True
        else:
            self.shif_fft = False

        if ((self.processFlags & PROCFLAG.SAVE_CHANNELS_DC) == PROCFLAG.SAVE_CHANNELS_DC):
            self.flag_dc = True
        else:
            self.flag_dc = False

        if ((self.processFlags & PROCFLAG.DECODE_DATA) == PROCFLAG.DECODE_DATA):
            self.flag_decode = True
        else:
            self.flag_decode = False

        if ((self.processFlags & PROCFLAG.DEFLIP_DATA) == PROCFLAG.DEFLIP_DATA):
            self.flag_deflip = True
        else:
            self.flag_deflip = False

        nChannels = 0
        nPairs = 0
        pairList = []

        for i in range(0, self.totalSpectra * 2, 2):
            if self.spectraComb[i] == self.spectraComb[i + 1]:
                nChannels = nChannels + 1  # par de canales iguales
            else:
                nPairs = nPairs + 1  # par de canales diferentes
                pairList.append((self.spectraComb[i], self.spectraComb[i + 1]))

        self.flag_cspc = False
        if nPairs > 0:
            self.flag_cspc = True

        if startFp is not None:
            endFp = size + startFp
            if fp.tell() > endFp:
                sys.stderr.write(
                    "Warning: Processing header size is lower than it has to be")
                return 0

            if fp.tell() < endFp:
                sys.stderr.write(
                    "Warning: Processing header size is greater than it is considered")

        return 1

    def write(self, fp):
        # Clear DEFINE_PROCESS_CODE
        self.processFlags = self.processFlags & (~PROCFLAG.DEFINE_PROCESS_CODE)

        headerTuple = (self.size,
                       self.dtype,
                       self.blockSize,
                       self.profilesPerBlock,
                       self.dataBlocksPerFile,
                       self.nWindows,
                       self.processFlags,
                       self.nCohInt,
                       self.nIncohInt,
                       self.totalSpectra)

        header = numpy.array(headerTuple, PROCESSING_STRUCTURE)
        header.tofile(fp)

        if self.nWindows != 0:
            sampleWindowTuple = (
                self.firstHeight, self.deltaHeight, self.samplesWin)
            samplingWindow = numpy.array(sampleWindowTuple, SAMPLING_STRUCTURE)
            samplingWindow.tofile(fp)

        if self.totalSpectra != 0:
            #             spectraComb = numpy.array([],numpy.dtype('u1'))
            spectraComb = self.spectraComb
            spectraComb.tofile(fp)

#         if self.processFlags & PROCFLAG.DEFINE_PROCESS_CODE == PROCFLAG.DEFINE_PROCESS_CODE:
#             nCode = numpy.array([self.nCode], numpy.dtype('u4')) #Probar con un dato que almacene codigo, hasta el momento no se hizo la prueba
#             nCode.tofile(fp)
#
#             nBaud = numpy.array([self.nBaud], numpy.dtype('u4'))
#             nBaud.tofile(fp)
#
#             code = self.code.reshape(self.nCode*self.nBaud)
#             code = code.astype(numpy.dtype('<f4'))
#             code.tofile(fp)

        return 1

    def get_size(self):

        self.__size = 40 + 12 * self.nWindows + 2 * self.totalSpectra

#         if self.processFlags & PROCFLAG.DEFINE_PROCESS_CODE == PROCFLAG.DEFINE_PROCESS_CODE:
#             self.__size += 4 + 4 + 4*self.nCode*numpy.ceil(self.nBaud/32.)
#             self.__size += 4 + 4 + 4 * self.nCode * self.nBaud

        return self.__size

    def set_size(self, value):

        raise IOError("size is a property and it cannot be set, just read")

        return

    size = property(get_size, set_size)


class RCfunction:
    NONE = 0
    FLIP = 1
    CODE = 2
    SAMPLING = 3
    LIN6DIV256 = 4
    SYNCHRO = 5


class nCodeType:
    NONE = 0
    USERDEFINE = 1
    BARKER2 = 2
    BARKER3 = 3
    BARKER4 = 4
    BARKER5 = 5
    BARKER7 = 6
    BARKER11 = 7
    BARKER13 = 8
    AC128 = 9
    COMPLEMENTARYCODE2 = 10
    COMPLEMENTARYCODE4 = 11
    COMPLEMENTARYCODE8 = 12
    COMPLEMENTARYCODE16 = 13
    COMPLEMENTARYCODE32 = 14
    COMPLEMENTARYCODE64 = 15
    COMPLEMENTARYCODE128 = 16
    CODE_BINARY28 = 17


class PROCFLAG:

    COHERENT_INTEGRATION = numpy.uint32(0x00000001)
    DECODE_DATA = numpy.uint32(0x00000002)
    SPECTRA_CALC = numpy.uint32(0x00000004)
    INCOHERENT_INTEGRATION = numpy.uint32(0x00000008)
    POST_COHERENT_INTEGRATION = numpy.uint32(0x00000010)
    SHIFT_FFT_DATA = numpy.uint32(0x00000020)

    DATATYPE_CHAR = numpy.uint32(0x00000040)
    DATATYPE_SHORT = numpy.uint32(0x00000080)
    DATATYPE_LONG = numpy.uint32(0x00000100)
    DATATYPE_INT64 = numpy.uint32(0x00000200)
    DATATYPE_FLOAT = numpy.uint32(0x00000400)
    DATATYPE_DOUBLE = numpy.uint32(0x00000800)

    DATAARRANGE_CONTIGUOUS_CH = numpy.uint32(0x00001000)
    DATAARRANGE_CONTIGUOUS_H = numpy.uint32(0x00002000)
    DATAARRANGE_CONTIGUOUS_P = numpy.uint32(0x00004000)

    SAVE_CHANNELS_DC = numpy.uint32(0x00008000)
    DEFLIP_DATA = numpy.uint32(0x00010000)
    DEFINE_PROCESS_CODE = numpy.uint32(0x00020000)

    ACQ_SYS_NATALIA = numpy.uint32(0x00040000)
    ACQ_SYS_ECHOTEK = numpy.uint32(0x00080000)
    ACQ_SYS_ADRXD = numpy.uint32(0x000C0000)
    ACQ_SYS_JULIA = numpy.uint32(0x00100000)
    ACQ_SYS_XXXXXX = numpy.uint32(0x00140000)

    EXP_NAME_ESP = numpy.uint32(0x00200000)
    CHANNEL_NAMES_ESP = numpy.uint32(0x00400000)

    OPERATION_MASK = numpy.uint32(0x0000003F)
    DATATYPE_MASK = numpy.uint32(0x00000FC0)
    DATAARRANGE_MASK = numpy.uint32(0x00007000)
    ACQ_SYS_MASK = numpy.uint32(0x001C0000)


dtype0 = numpy.dtype([('real', '<i1'), ('imag', '<i1')])
dtype1 = numpy.dtype([('real', '<i2'), ('imag', '<i2')])
dtype2 = numpy.dtype([('real', '<i4'), ('imag', '<i4')])
dtype3 = numpy.dtype([('real', '<i8'), ('imag', '<i8')])
dtype4 = numpy.dtype([('real', '<f4'), ('imag', '<f4')])
dtype5 = numpy.dtype([('real', '<f8'), ('imag', '<f8')])

NUMPY_DTYPE_LIST = [dtype0, dtype1, dtype2, dtype3, dtype4, dtype5]

PROCFLAG_DTYPE_LIST = [PROCFLAG.DATATYPE_CHAR,
                       PROCFLAG.DATATYPE_SHORT,
                       PROCFLAG.DATATYPE_LONG,
                       PROCFLAG.DATATYPE_INT64,
                       PROCFLAG.DATATYPE_FLOAT,
                       PROCFLAG.DATATYPE_DOUBLE]

DTYPE_WIDTH = [1, 2, 4, 8, 4, 8]


def get_dtype_index(numpy_dtype):

    index = None

    for i in range(len(NUMPY_DTYPE_LIST)):
        if numpy_dtype == NUMPY_DTYPE_LIST[i]:
            index = i
            break

    return index


def get_numpy_dtype(index):

    return NUMPY_DTYPE_LIST[index]


def get_procflag_dtype(index):

    return PROCFLAG_DTYPE_LIST[index]


def get_dtype_width(index):

    return DTYPE_WIDTH[index]