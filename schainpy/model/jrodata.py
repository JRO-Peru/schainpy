'''

$Author: murco $
$Id: JROData.py 173 2012-11-20 15:06:21Z murco $
'''

import os, sys
import copy
import numpy
import datetime

from jroheaderIO import SystemHeader, RadarControllerHeader

def hildebrand_sekhon(data, navg):
    """
    This method is for the objective determination of de noise level in Doppler spectra. This 
    implementation technique is based on the fact that the standard deviation of the spectral 
    densities is equal to the mean spectral density for white Gaussian noise
    
    Inputs:
        Data    :    heights
        navg    :    numbers of averages
        
    Return:
        -1        :    any error
        anoise    :    noise's level
    """
    
    dataflat = data.copy().reshape(-1)
    dataflat.sort()
    npts = dataflat.size #numbers of points of the data
    npts_noise = 0.2*npts
    
    if npts < 32:
        print "error in noise - requires at least 32 points"
        return -1.0
    
    dataflat2 = numpy.power(dataflat,2)
    
    cs = numpy.cumsum(dataflat)
    cs2 = numpy.cumsum(dataflat2)
    
    # data sorted in ascending order
    nmin = int((npts + 7.)/8)
    
    for i in range(nmin, npts):
        s = cs[i]
        s2 = cs2[i]
        p  = s / float(i);
        p2 = p**2;
        q  = s2 / float(i) - p2;
        leftc = p2;
        rightc = q * float(navg);
        R2 = leftc/rightc
        
        # Signal detect: R2 < 1 (R2 = leftc/rightc)
        if R2 < 1: 
            npts_noise = i
            break
        
            
    anoise = numpy.average(dataflat[0:npts_noise])

    return anoise;

def sorting_bruce(data, navg):
    
    data = data.copy()
    
    sortdata = numpy.sort(data)
    lenOfData = len(data)
    nums_min = lenOfData/10
    
    if (lenOfData/10) > 0:
        nums_min = lenOfData/10
    else:
        nums_min = 0
        
    rtest = 1.0 + 1.0/navg
    
    sump = 0.
    
    sumq = 0.
    
    j = 0
    
    cont = 1
    
    while((cont==1)and(j<lenOfData)):
        
        sump += sortdata[j]
        
        sumq += sortdata[j]**2
        
        j += 1
        
        if j > nums_min:
            if ((sumq*j) <= (rtest*sump**2)):
                lnoise = sump / j
            else:
                j = j - 1
                sump  = sump - sortdata[j]
                sumq =  sumq - sortdata[j]**2
                cont = 0
                
        if j == nums_min:
            lnoise = sump /j
    
    return lnoise   

class JROData:
    
#    m_BasicHeader = BasicHeader()
#    m_ProcessingHeader = ProcessingHeader()

    systemHeaderObj = SystemHeader()
    
    radarControllerHeaderObj = RadarControllerHeader()

#    data = None
    
    type = None
    
    dtype = None
    
#    nChannels = None
    
#    nHeights = None
    
    nProfiles = None
    
    heightList = None
    
    channelList = None
    
    flagNoData = True
    
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
    
    ippSeconds = None
    
    timeInterval = None
    
    nCohInt = None
    
    noise = None
    
    windowOfFilter = 1
    
    #Speed of ligth
    C = 3e8
    
    frequency = 49.92e6
    
    realtime = False

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
        
        datatime = datetime.datetime.utcfromtimestamp(self.ltctime)
        return datatime
    
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
    
    nChannels = property(getNChannels, "I'm the 'nChannel' property.")
    channelIndexList = property(getChannelIndexList, "I'm the 'channelIndexList' property.")
    nHeights = property(getNHeights, "I'm the 'nHeights' property.")
    noise = property(getNoise, "I'm the 'nHeights' property.")
    datatime = property(getDatatime, "I'm the 'datatime' property")
    ltctime = property(getltctime, "I'm the 'ltctime' property")
    
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
        
        self.dtype = None
        
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
        
class Spectra(JROData):
    
    #data es un numpy array de 2 dmensiones (canales, perfiles, alturas)
    data_spc = None
    
    #data es un numpy array de 2 dmensiones (canales, pares, alturas)
    data_cspc = None
    
    #data es un numpy array de 2 dmensiones (canales, alturas)
    data_dc = None
    
    nFFTPoints = None
    
    nPairs = None
    
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
        
        self.dtype = None
        
#        self.nChannels = 0
        
#        self.nHeights = 0
        
        self.nProfiles = None
        
        self.heightList = None
        
        self.channelList = None
        
#        self.channelIndexList = None
        
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
    
    def getNoisebyHildebrand(self):
        """
        Determino el nivel de ruido usando el metodo Hildebrand-Sekhon
        
        Return:
            noiselevel
        """

        for channel in range(self.nChannels):
            daux = self.data_spc[channel,:,:]
            self.noise[channel] = hildebrand_sekhon(daux, self.nIncohInt)
        
        return self.noise 
    
    def getNoisebyWindow(self, heiIndexMin=0, heiIndexMax=-1, freqIndexMin=0, freqIndexMax=-1):
        """
        Determina el ruido del canal utilizando la ventana indicada con las coordenadas: 
        (heiIndexMIn, freqIndexMin) hasta (heiIndexMax, freqIndexMAx)
        
        Inputs:
            heiIndexMin: Limite inferior del eje de alturas
            heiIndexMax: Limite superior del eje de alturas
            freqIndexMin: Limite inferior del eje de frecuencia
            freqIndexMax: Limite supoerior del eje de frecuencia
        """
        
        data = self.data_spc[:, heiIndexMin:heiIndexMax, freqIndexMin:freqIndexMax]
        
        for channel in range(self.nChannels):
            daux = data[channel,:,:]
            self.noise[channel] = numpy.average(daux)
        
        return self.noise
    
    def getNoisebySort(self):
        
        for channel in range(self.nChannels):
            daux = self.data_spc[channel,:,:]
            self.noise[channel] = sorting_bruce(daux, self.nIncohInt)
            
        return self.noise 
    
    def getNoise(self, type = 1):
        
        self.noise = numpy.zeros(self.nChannels)
        
        if type == 1:
            noise = self.getNoisebyHildebrand()
        
        if type == 2:
            noise = self.getNoisebySort()
        
        if type == 3:
            noise = self.getNoisebyWindow()
        
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
        normFactor = min(self.nFFTPoints,self.nProfiles)*self.nIncohInt*self.nCohInt*pwcode
        
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
        
class SpectraHeis(JROData):
    
    data_spc = None
    
    data_cspc = None
    
    data_dc = None
    
    nFFTPoints = None
    
    nPairs = None
    
    pairsList = None
    
    nIncohInt = None
    
    def __init__(self):
        
        self.radarControllerHeaderObj = RadarControllerHeader()
    
        self.systemHeaderObj = SystemHeader()
        
        self.type = "SpectraHeis"
        
        self.dtype = None
        
#        self.nChannels = 0
        
#        self.nHeights = 0
        
        self.nProfiles = None
        
        self.heightList = None
        
        self.channelList = None
        
#        self.channelIndexList = None
        
        self.flagNoData = True
        
        self.flagTimeBlock = False
                
        self.nPairs = 0
        
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
    
    ippSeconds = None
    
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