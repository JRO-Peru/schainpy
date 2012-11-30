'''

$Author: murco $
$Id: JROData.py 173 2012-11-20 15:06:21Z murco $
'''

import os, sys
import copy
import numpy

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
    
    dataflat = data.reshape(-1)
    dataflat.sort()
    npts = dataflat.size #numbers of points of the data
    
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

def sorting_bruce(Data, navg):
    sortdata = numpy.sort(Data)
    lenOfData = len(Data)
    nums_min = lenOfData/10
    
    if (lenOfData/10) > 0:
        nums_min = lenOfData/10
    else:
        nums_min = 0
        
    rtest = 1.0 + 1.0/navg
    
    sum = 0.
    
    sumq = 0.
    
    j = 0
    
    cont = 1
    
    while((cont==1)and(j<lenOfData)):
        
        sum += sortdata[j]
        
        sumq += sortdata[j]**2
        
        j += 1
        
        if j > nums_min:
            if ((sumq*j) <= (rtest*sum**2)):
                lnoise = sum / j
            else:
                j = j - 1
                sum  = sum - sordata[j]
                sumq =  sumq - sordata[j]**2
                cont = 0
                
        if j == nums_min:
            lnoise = sum /j
    
    return lnoise   

class JROData:
    
#    m_BasicHeader = BasicHeader()
#    m_ProcessingHeader = ProcessingHeader()

    systemHeaderObj = SystemHeader()
    
    radarControllerHeaderObj = RadarControllerHeader()

#    data = None
    
    type = None
    
    dtype = None
    
    nChannels = None
    
    nHeights = None
    
    nProfiles = None
    
    heightList = None
    
    channelList = None
    
    channelIndexList = None
    
    flagNoData = True
    
    flagTimeBlock = False
    
    utctime = None
    
    blocksize = None
    
    nCode = None
    
    nBaud = None
    
    code = None
    
    flagDecodeData = True #asumo q la data esta decodificada
    
    flagDeflipData = True #asumo q la data esta sin flip
    
    flagShiftFFT = False
    
    ippSeconds = None
    
    timeInterval = None
    
    nCohInt = None
    
    noise = None

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
        
        self.nChannels = 0
        
        self.nHeights = 0
        
        self.nProfiles = None
        
        self.heightList = None
        
        self.channelList = None
        
        self.channelIndexList = None
        
        self.flagNoData = True
        
        self.flagTimeBlock = False
        
        self.utctime = None
        
        self.nCohInt = None
        
        self.blocksize = None
    
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
    
    def __init__(self):
        '''
        Constructor
        '''
        
        self.radarControllerHeaderObj = RadarControllerHeader()
    
        self.systemHeaderObj = SystemHeader()
        
        self.type = "Spectra"
        
#        self.data = None
        
        self.dtype = None
        
        self.nChannels = 0
        
        self.nHeights = 0
        
        self.nProfiles = None
        
        self.heightList = None
        
        self.channelList = None
        
        self.channelIndexList = None
        
        self.flagNoData = True
        
        self.flagTimeBlock = False
        
        self.utctime = None
        
        self.nCohInt = None
        
        self.nIncohInt = None
        
        self.blocksize = None
        
        self.nFFTPoints = None
        
        self.wavelength = None
    
    def getFrequencies(self):
        
        xrange = numpy.arange(self.nFFTPoints)
        xrange = xrange  
        return None
    
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
        
        return 10*numpy.log10(noise)
        
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
        
        self.nChannels = 0
        
        self.nHeights = 0
        
        self.nProfiles = None
        
        self.heightList = None
        
        self.channelList = None
        
        self.channelIndexList = None
        
        self.flagNoData = True
        
        self.flagTimeBlock = False
                
        self.nPairs = 0
        
        self.utctime = None
        
        self.blocksize = None
