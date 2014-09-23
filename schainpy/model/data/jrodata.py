'''

$Author: murco $
$Id: JROData.py 173 2012-11-20 15:06:21Z murco $
'''

import copy
import numpy
import datetime

from jroheaderIO import SystemHeader, RadarControllerHeader

def getNumpyDtype(dataTypeCode):
    
    if dataTypeCode == 0:
        numpyDtype = numpy.dtype([('real','<i1'),('imag','<i1')])
    elif dataTypeCode == 1:
        numpyDtype = numpy.dtype([('real','<i2'),('imag','<i2')])
    elif dataTypeCode == 2:
        numpyDtype = numpy.dtype([('real','<i4'),('imag','<i4')])
    elif dataTypeCode == 3:
        numpyDtype = numpy.dtype([('real','<i8'),('imag','<i8')])
    elif dataTypeCode == 4:
        numpyDtype = numpy.dtype([('real','<f4'),('imag','<f4')])
    elif dataTypeCode == 5:
        numpyDtype = numpy.dtype([('real','<f8'),('imag','<f8')])
    else:
        raise ValueError, 'dataTypeCode was not defined'
    
    return numpyDtype

def getDataTypeCode(numpyDtype):
    
    if numpyDtype == numpy.dtype([('real','<i1'),('imag','<i1')]):
        datatype = 0
    elif numpyDtype == numpy.dtype([('real','<i2'),('imag','<i2')]):
        datatype = 1
    elif numpyDtype == numpy.dtype([('real','<i4'),('imag','<i4')]):
        datatype = 2
    elif numpyDtype == numpy.dtype([('real','<i8'),('imag','<i8')]):
        datatype = 3
    elif numpyDtype == numpy.dtype([('real','<f4'),('imag','<f4')]):
        datatype = 4
    elif numpyDtype == numpy.dtype([('real','<f8'),('imag','<f8')]):
        datatype = 5
    else:
        datatype = None
    
    return datatype

def hildebrand_sekhon(data, navg):
    
    data = data.copy()
    
    sortdata = numpy.sort(data,axis=None)
    lenOfData = len(sortdata)
    nums_min = lenOfData/10
    
    if (lenOfData/10) > 2:
        nums_min = lenOfData/10
    else:
        nums_min = 2

    sump = 0.
    
    sumq = 0.
    
    j = 0
    
    cont = 1
    
    while((cont==1)and(j<lenOfData)):
        
        sump += sortdata[j]
        
        sumq += sortdata[j]**2
        
        j += 1
        
        if j > nums_min:
            rtest = float(j)/(j-1) + 1.0/navg
            if ((sumq*j) > (rtest*sump**2)):
                j = j - 1
                sump  = sump - sortdata[j]
                sumq =  sumq - sortdata[j]**2
                cont = 0

    lnoise = sump /j
    stdv = numpy.sqrt((sumq - lnoise**2)/(j - 1))
    return lnoise   

class GenericData(object):
    
    flagNoData = True
    
    def __init__(self):
        
        raise ValueError, "This class has not been implemented"
        
    def copy(self, inputObj=None):
        
        if inputObj == None:
            return copy.deepcopy(self)

        for key in inputObj.__dict__.keys():
            self.__dict__[key] = inputObj.__dict__[key]

    def deepcopy(self):
        
        return copy.deepcopy(self)
    
    def isEmpty(self):
        
        return self.flagNoData
    
class JROData(GenericData):
    
#    m_BasicHeader = BasicHeader()
#    m_ProcessingHeader = ProcessingHeader()

    systemHeaderObj = SystemHeader()
    
    radarControllerHeaderObj = RadarControllerHeader()

#    data = None
    
    type = None
    
    datatype = None #dtype but in string
    
#     dtype = None
    
#    nChannels = None
    
#    nHeights = None
    
    nProfiles = None
    
    heightList = None
    
    channelList = None
    
    flagTimeBlock = False
    
    useLocalTime = False
    
    utctime = None
    
    timeZone = None
    
    dstFlag = None
    
    errorCount = None
    
    blocksize = None
    
    nCode = None
    
    nBaud = None
    
    code = None
    
    flagDecodeData = False #asumo q la data no esta decodificada
    
    flagDeflipData = False #asumo q la data no esta sin flip
    
    flagShiftFFT = False
    
#     ippSeconds = None
    
    timeInterval = None
    
    nCohInt = None
    
    noise = None
    
    windowOfFilter = 1
    
    #Speed of ligth
    C = 3e8
    
    frequency = 49.92e6
    
    realtime = False
    
    beacon_heiIndexList = None
    
    last_block = None
    
    blocknow = None

    def __init__(self):
        
        raise ValueError, "This class has not been implemented"
    
    def getNoise(self):
        
        raise ValueError, "Not implemented"
        
    def getNChannels(self):
        
        return len(self.channelList)
        
    def getChannelIndexList(self):
        
        return range(self.nChannels)
    
    def getNHeights(self):
        
        return len(self.heightList)
    
    def getHeiRange(self, extrapoints=0):
        
        heis = self.heightList
#        deltah = self.heightList[1] - self.heightList[0]
#        
#        heis.append(self.heightList[-1])
        
        return heis
    
    def getltctime(self):
        
        if self.useLocalTime:
            return self.utctime - self.timeZone*60
        
        return self.utctime
    
    def getDatatime(self):
        
        datatimeValue = datetime.datetime.utcfromtimestamp(self.ltctime)
        return datatimeValue
    
    def getTimeRange(self):
        
        datatime = []
        
        datatime.append(self.ltctime)
        datatime.append(self.ltctime + self.timeInterval)
        
        datatime = numpy.array(datatime)
        
        return datatime
    
    def getFmax(self):
        
        PRF = 1./(self.ippSeconds * self.nCohInt)
        
        fmax = PRF/2.
        
        return fmax
    
    def getVmax(self):
        
        _lambda = self.C/self.frequency
        
        vmax = self.getFmax() * _lambda
        
        return vmax
    
    def get_ippSeconds(self):
        '''
        '''
        return self.radarControllerHeaderObj.ippSeconds
    
    def set_ippSeconds(self, ippSeconds):
        '''
        '''
        
        self.radarControllerHeaderObj.ippSeconds = ippSeconds
        
        return
    
    def get_dtype(self):
        '''
        '''
        return getNumpyDtype(self.datatype)
        
    def set_dtype(self, numpyDtype):
        '''
        '''
        
        self.datatype = getDataTypeCode(numpyDtype)
        
    nChannels = property(getNChannels, "I'm the 'nChannel' property.")
    channelIndexList = property(getChannelIndexList, "I'm the 'channelIndexList' property.")
    nHeights = property(getNHeights, "I'm the 'nHeights' property.")
    #noise = property(getNoise, "I'm the 'nHeights' property.")
    datatime = property(getDatatime, "I'm the 'datatime' property")
    ltctime = property(getltctime, "I'm the 'ltctime' property")
    ippSeconds = property(get_ippSeconds, set_ippSeconds)
    dtype = property(get_dtype, set_dtype)
    
class Voltage(JROData):
    
    #data es un numpy array de 2 dmensiones (canales, alturas)
    data = None
    
    def __init__(self):
        '''
        Constructor
        '''
        
        self.radarControllerHeaderObj = RadarControllerHeader()
    
        self.systemHeaderObj = SystemHeader()
        
        self.type = "Voltage"
        
        self.data = None
        
#         self.dtype = None
        
#        self.nChannels = 0
        
#        self.nHeights = 0
        
        self.nProfiles = None
        
        self.heightList = None
        
        self.channelList = None
        
#        self.channelIndexList = None
        
        self.flagNoData = True
        
        self.flagTimeBlock = False
        
        self.utctime = None
        
        self.timeZone = None
    
        self.dstFlag = None
        
        self.errorCount = None
        
        self.nCohInt = None
        
        self.blocksize = None
        
        self.flagDecodeData = False #asumo q la data no esta decodificada
    
        self.flagDeflipData = False #asumo q la data no esta sin flip
        
        self.flagShiftFFT = False
    
    
    def getNoisebyHildebrand(self):
        """
        Determino el nivel de ruido usando el metodo Hildebrand-Sekhon
        
        Return:
            noiselevel
        """

        for channel in range(self.nChannels):
            daux = self.data_spc[channel,:,:]
            self.noise[channel] = hildebrand_sekhon(daux, self.nCohInt)
        
        return self.noise
    
    def getNoise(self, type = 1):
        
        self.noise = numpy.zeros(self.nChannels)
        
        if type == 1:
            noise = self.getNoisebyHildebrand()
            
        return 10*numpy.log10(noise)
    
    noise = property(getNoise, "I'm the 'nHeights' property.")
        
class Spectra(JROData):
    
    #data es un numpy array de 2 dmensiones (canales, perfiles, alturas)
    data_spc = None
    
    #data es un numpy array de 2 dmensiones (canales, pares, alturas)
    data_cspc = None
    
    #data es un numpy array de 2 dmensiones (canales, alturas)
    data_dc = None
    
    nFFTPoints = None
    
#     nPairs = None
    
    pairsList = None
    
    nIncohInt = None
    
    wavelength = None #Necesario para cacular el rango de velocidad desde la frecuencia
    
    nCohInt = None #se requiere para determinar el valor de timeInterval
    
    ippFactor = None
    
    def __init__(self):
        '''
        Constructor
        '''
        
        self.radarControllerHeaderObj = RadarControllerHeader()
    
        self.systemHeaderObj = SystemHeader()
        
        self.type = "Spectra"
        
#        self.data = None
        
#         self.dtype = None
        
#        self.nChannels = 0
        
#        self.nHeights = 0
        
        self.nProfiles = None
        
        self.heightList = None
        
        self.channelList = None
        
#        self.channelIndexList = None

        self.pairsList = None
        
        self.flagNoData = True
        
        self.flagTimeBlock = False
        
        self.utctime = None
        
        self.nCohInt = None
        
        self.nIncohInt = None
        
        self.blocksize = None
        
        self.nFFTPoints = None
        
        self.wavelength = None
        
        self.flagDecodeData = False #asumo q la data no esta decodificada
    
        self.flagDeflipData = False #asumo q la data no esta sin flip
        
        self.flagShiftFFT = False
        
        self.ippFactor = 1
        
        #self.noise = None
        
        self.beacon_heiIndexList = []
        
        self.noise_estimation = None
        
    
    def getNoisebyHildebrand(self):
        """
        Determino el nivel de ruido usando el metodo Hildebrand-Sekhon
        
        Return:
            noiselevel
        """
        
        noise = numpy.zeros(self.nChannels)
        for channel in range(self.nChannels):
            daux = self.data_spc[channel,:,:]
            noise[channel] = hildebrand_sekhon(daux, self.nIncohInt)
        
        return noise 
        
    def getNoise(self):
        if self.noise_estimation != None:
            return self.noise_estimation #this was estimated by getNoise Operation defined in jroproc_spectra.py
        else:
            noise = self.getNoisebyHildebrand()
            return noise

    
    def getFreqRange(self, extrapoints=0):
        
        deltafreq = self.getFmax() / (self.nFFTPoints*self.ippFactor)
        freqrange = deltafreq*(numpy.arange(self.nFFTPoints+extrapoints)-self.nFFTPoints/2.) - deltafreq/2
        
        return freqrange

    def getVelRange(self, extrapoints=0):
        
        deltav = self.getVmax() / (self.nFFTPoints*self.ippFactor)
        velrange = deltav*(numpy.arange(self.nFFTPoints+extrapoints)-self.nFFTPoints/2.) - deltav/2       
        
        return velrange
    
    def getNPairs(self):
        
        return len(self.pairsList)
        
    def getPairsIndexList(self):
        
        return range(self.nPairs)
    
    def getNormFactor(self):
        pwcode = 1
        if self.flagDecodeData:
            pwcode = numpy.sum(self.code[0]**2)
        #normFactor = min(self.nFFTPoints,self.nProfiles)*self.nIncohInt*self.nCohInt*pwcode*self.windowOfFilter
        normFactor = self.nProfiles*self.nIncohInt*self.nCohInt*pwcode*self.windowOfFilter
        
        return normFactor
    
    def getFlagCspc(self):
        
        if self.data_cspc == None:
            return True
        
        return False
    
    def getFlagDc(self):
        
        if self.data_dc == None:
            return True
            
        return False
    
    nPairs = property(getNPairs, "I'm the 'nPairs' property.")
    pairsIndexList = property(getPairsIndexList, "I'm the 'pairsIndexList' property.")
    normFactor = property(getNormFactor, "I'm the 'getNormFactor' property.")
    flag_cspc = property(getFlagCspc)
    flag_dc = property(getFlagDc)
    noise = property(getNoise, "I'm the 'nHeights' property.")
        
class SpectraHeis(Spectra):
    
    data_spc = None
    
    data_cspc = None
    
    data_dc = None
    
    nFFTPoints = None
    
#     nPairs = None
    
    pairsList = None
    
    nIncohInt = None
    
    def __init__(self):
        
        self.radarControllerHeaderObj = RadarControllerHeader()
    
        self.systemHeaderObj = SystemHeader()
        
        self.type = "SpectraHeis"
        
#         self.dtype = None
        
#        self.nChannels = 0
        
#        self.nHeights = 0
        
        self.nProfiles = None
        
        self.heightList = None
        
        self.channelList = None
        
#        self.channelIndexList = None
        
        self.flagNoData = True
        
        self.flagTimeBlock = False
                
#         self.nPairs = 0
        
        self.utctime = None
        
        self.blocksize = None

class Fits:
    
    heightList = None
    
    channelList = None
    
    flagNoData = True
    
    flagTimeBlock = False
    
    useLocalTime = False
    
    utctime = None
    
    timeZone = None
    
#     ippSeconds = None
    
    timeInterval = None
    
    nCohInt = None
    
    nIncohInt = None
    
    noise = None
    
    windowOfFilter = 1
    
    #Speed of ligth
    C = 3e8
    
    frequency = 49.92e6
    
    realtime = False

    
    def __init__(self):
        
        self.type = "Fits"
        
        self.nProfiles = None
        
        self.heightList = None
        
        self.channelList = None
        
#         self.channelIndexList = None
        
        self.flagNoData = True
        
        self.utctime = None
        
        self.nCohInt = None
        
        self.nIncohInt = None
        
        self.useLocalTime = True
        
#         self.utctime = None
#         self.timeZone = None
#         self.ltctime = None
#         self.timeInterval = None
#         self.header = None
#         self.data_header = None
#         self.data = None
#         self.datatime = None
#         self.flagNoData = False
#         self.expName = ''
#         self.nChannels = None
#         self.nSamples = None
#         self.dataBlocksPerFile = None
#         self.comments = ''
#         

    
    def getltctime(self):
        
        if self.useLocalTime:
            return self.utctime - self.timeZone*60
        
        return self.utctime
    
    def getDatatime(self):
        
        datatime = datetime.datetime.utcfromtimestamp(self.ltctime)
        return datatime
    
    def getTimeRange(self):
        
        datatime = []
        
        datatime.append(self.ltctime)
        datatime.append(self.ltctime + self.timeInterval)
        
        datatime = numpy.array(datatime)
        
        return datatime
    
    def getHeiRange(self):
        
        heis = self.heightList
        
        return heis
    
    def isEmpty(self):
        
        return self.flagNoData
    
    def getNHeights(self):
        
        return len(self.heightList)
    
    def getNChannels(self):
        
        return len(self.channelList)
        
    def getChannelIndexList(self):
        
        return range(self.nChannels)
    
    def getNoise(self, type = 1):
        
        self.noise = numpy.zeros(self.nChannels)
        
        if type == 1:
            noise = self.getNoisebyHildebrand()
        
        if type == 2:
            noise = self.getNoisebySort()
        
        if type == 3:
            noise = self.getNoisebyWindow()
        
        return noise
    
    datatime = property(getDatatime, "I'm the 'datatime' property")
    nHeights = property(getNHeights, "I'm the 'nHeights' property.")
    nChannels = property(getNChannels, "I'm the 'nChannel' property.")
    channelIndexList = property(getChannelIndexList, "I'm the 'channelIndexList' property.")
    noise = property(getNoise, "I'm the 'nHeights' property.")
    datatime = property(getDatatime, "I'm the 'datatime' property")
    ltctime = property(getltctime, "I'm the 'ltctime' property")

    ltctime = property(getltctime, "I'm the 'ltctime' property")
    
class AMISR:
    def __init__(self):
        self.flagNoData = True
        self.data = None
        self.utctime = None
        self.type = "AMISR"
        
        #propiedades para compatibilidad con Voltages
        self.timeZone = 300#timezone like jroheader, difference in minutes between UTC and localtime 
        self.dstFlag = 0#self.dataIn.dstFlag
        self.errorCount = 0#self.dataIn.errorCount
        self.useLocalTime = True#self.dataIn.useLocalTime
        
        self.radarControllerHeaderObj = None#self.dataIn.radarControllerHeaderObj.copy()
        self.systemHeaderObj = None#self.dataIn.systemHeaderObj.copy()
        self.channelList = [0]#self.dataIn.channelList esto solo aplica para el caso de AMISR
        self.dtype = numpy.dtype([('real','<f4'),('imag','<f4')])
        
        self.flagTimeBlock = None#self.dataIn.flagTimeBlock
        #self.utctime = #self.firstdatatime
        self.flagDecodeData = None#self.dataIn.flagDecodeData #asumo q la data esta decodificada
        self.flagDeflipData = None#self.dataIn.flagDeflipData #asumo q la data esta sin flip

        self.nCohInt = 1#self.dataIn.nCohInt
        self.nIncohInt = 1
        self.ippSeconds = None#self.dataIn.ippSeconds, segun el filename/Setup/Tufile
        self.windowOfFilter = None#self.dataIn.windowOfFilter
        
        self.timeInterval = None#self.dataIn.timeInterval*self.dataOut.nFFTPoints*self.dataOut.nIncohInt
        self.frequency = None#self.dataIn.frequency
        self.realtime = 0#self.dataIn.realtime
        
        #actualizar en la lectura de datos
        self.heightList = None#self.dataIn.heightList
        self.nProfiles = None#Number of samples or nFFTPoints
        self.nRecords = None
        self.nBeams = None
        self.nBaud = None#self.dataIn.nBaud
        self.nCode = None#self.dataIn.nCode
        self.code = None#self.dataIn.code
        
        #consideracion para los Beams
        self.beamCodeDict = None
        self.beamRangeDict = None
        
    def copy(self, inputObj=None):
        
        if inputObj == None:
            return copy.deepcopy(self)

        for key in inputObj.__dict__.keys():
            self.__dict__[key] = inputObj.__dict__[key]

        
    def isEmpty(self):
        
        return self.flagNoData