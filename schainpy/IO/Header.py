import numpy

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

class BasicHeader:
    
    size = 0
    version = 0
    dataBlock = 0
    utc = 0
    miliSecond = 0
    timeZone = 0
    dstFlag = 0
    errorCount = 0
    struct = numpy.dtype([
                          ('nSize','<u4'),
                          ('nVersion','<u2'),
                          ('nDataBlockId','<u4'),
                          ('nUtime','<u4'),
                          ('nMilsec','<u2'),     
                          ('nTimezone','<i2'),
                          ('nDstflag','<i2'),
                          ('nErrorCount','<u4')
                          ])   
        
    def __init__(self):
        pass
    
    def read(self, fp):
        
        header = numpy.fromfile(fp, self.struct,1)
        self.size = header['nSize'][0]
        self.version = header['nVersion'][0]
        self.dataBlock = header['nDataBlockId'][0]
        self.utc = header['nUtime'][0]
        self.miliSecond = header['nMilsec'][0]
        self.timeZone = header['nTimezone'][0]
        self.dstFlag = header['nDstflag'][0]
        self.errorCount = header['nErrorCount'][0]
        
        return 1
    
    def copy(self):
        
        obj = BasicHeader()
        obj.size = self.size
        
        
        return obj

class SystemHeader:
    size = 0 
    numSamples = 0
    numProfiles = 0
    numChannels = 0
    adcResolution = 0
    pciDioBusWidth = 0
    struct = numpy.dtype([
                        ('nSize','<u4'),
                        ('nNumSamples','<u4'),
                        ('nNumProfiles','<u4'),
                        ('nNumChannels','<u4'),
                        ('nADCResolution','<u4'),
                        ('nPCDIOBusWidth','<u4'),
                        ])
    
    def __init__(self):
        pass

    def read(self, fp):
        header = numpy.fromfile(fp,self.struct,1)
        self.size = header['nSize'][0]
        self.numSamples = header['nNumSamples'][0]
        self.numProfiles = header['nNumProfiles'][0]
        self.numChannels = header['nNumChannels'][0]
        self.adcResolution = header['nADCResolution'][0]
        self.pciDioBusWidth = header['nPCDIOBusWidth'][0]
        
        
        return 1

    def copy(self):
        
        obj = SystemHeader()
        obj.size = self.size
        
        
        return obj
    
class RadarControllerHeader:
    size = 0
    expType = 0
    nTx = 0
    ipp = 0
    txA = 0
    txB = 0
    numWindows = 0
    numTaus = 0
    codeType = 0
    line6Function = 0
    line5Fuction = 0
    fClock = 0
    prePulseBefore = 0
    prePulserAfter = 0
    rangeIpp = 0
    rangeTxA = 0
    rangeTxB = 0
    struct = numpy.dtype([
                         ('nSize','<u4'),
                         ('nExpType','<u4'),
                         ('nNTx','<u4'),
                         ('fIpp','<f4'),
                         ('fTxA','<f4'),
                         ('fTxB','<f4'),
                         ('nNumWindows','<u4'),
                         ('nNumTaus','<u4'),
                         ('nCodeType','<u4'),
                         ('nLine6Function','<u4'),
                         ('nLine5Function','<u4'),
                         ('fClock','<f4'),
                         ('nPrePulseBefore','<u4'),
                         ('nPrePulseAfter','<u4'),
                         ('sRangeIPP','<a20'),
                         ('sRangeTxA','<a20'),
                         ('sRangeTxB','<a20'),
                         ])
    
    
    def __init__(self):
        pass

    def read(self, fp):
        header = numpy.fromfile(fp,self.struct,1)
        self.size = header['nSize'][0]
        self.expType = header['nExpType'][0]
        self.nTx = header['nNTx'][0]
        self.ipp = header['fIpp'][0]
        self.txA = header['fTxA'][0]
        self.txB = header['fTxB'][0]
        self.numWindows = header['nNumWindows'][0]
        self.numTaus = header['nNumTaus'][0]
        self.codeType = header['nCodeType'][0]
        self.line6Function = header['nLine6Function'][0]
        self.line5Fuction = header['nLine5Function'][0]
        self.fClock = header['fClock'][0]
        self.prePulseBefore = header['nPrePulseBefore'][0]
        self.prePulserAfter = header['nPrePulseAfter'][0]
        self.rangeIpp = header['sRangeIPP'][0]
        self.rangeTxA = header['sRangeTxA'][0]
        self.rangeTxB = header['sRangeTxB'][0]
        # jump Dynamic Radar Controller Header
        jumpHeader = self.size - 116
        fp.seek(fp.tell() + jumpHeader)
        
        return 1
    
    def copy(self):
        
        obj = RadarControllerHeader()
        obj.size = self.size
        
        
        return obj
    
class ProcessingHeader:
    size = 0
    dataType = 0
    blockSize = 0
    profilesPerBlock = 0
    dataBlocksPerFile = 0
    numWindows = 0
    processFlags = 0
    coherentInt = 0
    incoherentInt = 0
    totalSpectra = 0
    struct = numpy.dtype([
                           ('nSize','<u4'),
                           ('nDataType','<u4'),
                           ('nSizeOfDataBlock','<u4'),
                           ('nProfilesperBlock','<u4'),
                           ('nDataBlocksperFile','<u4'),
                           ('nNumWindows','<u4'),
                           ('nProcessFlags','<u4'),
                           ('nCoherentIntegrations','<u4'),
                           ('nIncoherentIntegrations','<u4'),
                           ('nTotalSpectra','<u4')
                           ])
    samplingWindow = 0
    structSamplingWindow = numpy.dtype([('h0','<f4'),('dh','<f4'),('nsa','<u4')])
    numHeights = 0
    firstHeight = 0
    deltaHeight = 0
    samplesWin = 0
    spectraComb = 0
    numCode = 0
    codes = 0
    numBaud = 0
    
    def __init__(self):
        pass
    
    def read(self, fp):
        header = numpy.fromfile(fp,self.struct,1)
        self.size = header['nSize'][0]
        self.dataType = header['nDataType'][0]
        self.blockSize = header['nSizeOfDataBlock'][0]
        self.profilesPerBlock = header['nProfilesperBlock'][0]
        self.dataBlocksPerFile = header['nDataBlocksperFile'][0]
        self.numWindows = header['nNumWindows'][0]
        self.processFlags = header['nProcessFlags']
        self.coherentInt = header['nCoherentIntegrations'][0]
        self.incoherentInt = header['nIncoherentIntegrations'][0]
        self.totalSpectra = header['nTotalSpectra'][0]
        self.samplingWindow = numpy.fromfile(fp,self.structSamplingWindow,self.numWindows)
        self.numHeights = numpy.sum(self.samplingWindow['nsa'])
        self.firstHeight = self.samplingWindow['h0']
        self.deltaHeight = self.samplingWindow['dh']
        self.samplesWin = self.samplingWindow['nsa']
        self.spectraComb = numpy.fromfile(fp,'u1',2*self.totalSpectra)
        if self.processFlags & PROCFLAG.DEFINE_PROCESS_CODE == PROCFLAG.DEFINE_PROCESS_CODE:
            self.numCode = numpy.fromfile(fp,'<u4',1)
            self.numBaud = numpy.fromfile(fp,'<u4',1)
            self.codes = numpy.fromfile(fp,'<f4',self.numCode*self.numBaud).reshape(self.numBaud,self.numCode)

        
        return 1

    def copy(self):
        
        obj = ProcessingHeader()
        obj.size = self.size
        
        
        return obj