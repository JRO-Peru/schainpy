# Copyright (c) 2012-2020 Jicamarca Radio Observatory
# All rights reserved.
#
# Distributed under the terms of the BSD 3-clause license.
"""Definition of diferent Data objects for different types of data

Here you will find the diferent data objects for the different types
of data, this data objects must be used as dataIn or dataOut objects in
processing units and operations. Currently the supported data objects are:
Voltage, Spectra, SpectraHeis, Fits, Correlation and Parameters
"""

import copy
import numpy
import datetime
import json

import schainpy.admin
from schainpy.utils import log
from .jroheaderIO import SystemHeader, RadarControllerHeader
from schainpy.model.data import _noise


def getNumpyDtype(dataTypeCode):

    if dataTypeCode == 0:
        numpyDtype = numpy.dtype([('real', '<i1'), ('imag', '<i1')])
    elif dataTypeCode == 1:
        numpyDtype = numpy.dtype([('real', '<i2'), ('imag', '<i2')])
    elif dataTypeCode == 2:
        numpyDtype = numpy.dtype([('real', '<i4'), ('imag', '<i4')])
    elif dataTypeCode == 3:
        numpyDtype = numpy.dtype([('real', '<i8'), ('imag', '<i8')])
    elif dataTypeCode == 4:
        numpyDtype = numpy.dtype([('real', '<f4'), ('imag', '<f4')])
    elif dataTypeCode == 5:
        numpyDtype = numpy.dtype([('real', '<f8'), ('imag', '<f8')])
    else:
        raise ValueError('dataTypeCode was not defined')

    return numpyDtype


def getDataTypeCode(numpyDtype):

    if numpyDtype == numpy.dtype([('real', '<i1'), ('imag', '<i1')]):
        datatype = 0
    elif numpyDtype == numpy.dtype([('real', '<i2'), ('imag', '<i2')]):
        datatype = 1
    elif numpyDtype == numpy.dtype([('real', '<i4'), ('imag', '<i4')]):
        datatype = 2
    elif numpyDtype == numpy.dtype([('real', '<i8'), ('imag', '<i8')]):
        datatype = 3
    elif numpyDtype == numpy.dtype([('real', '<f4'), ('imag', '<f4')]):
        datatype = 4
    elif numpyDtype == numpy.dtype([('real', '<f8'), ('imag', '<f8')]):
        datatype = 5
    else:
        datatype = None

    return datatype


def hildebrand_sekhon(data, navg):
    """
    This method is for the objective determination of the noise level in Doppler spectra. This
    implementation technique is based on the fact that the standard deviation of the spectral
    densities is equal to the mean spectral density for white Gaussian noise

    Inputs:
        Data    :    heights
        navg    :    numbers of averages

    Return:
        mean    :    noise's level
    """

    sortdata = numpy.sort(data, axis=None)
    '''
    lenOfData = len(sortdata)
    nums_min = lenOfData*0.2

    if nums_min <= 5:

        nums_min = 5

    sump = 0.
    sumq = 0.

    j = 0
    cont = 1

    while((cont == 1)and(j < lenOfData)):

        sump += sortdata[j]
        sumq += sortdata[j]**2

        if j > nums_min:
            rtest = float(j)/(j-1) + 1.0/navg
            if ((sumq*j) > (rtest*sump**2)):
                j = j - 1
                sump = sump - sortdata[j]
                sumq = sumq - sortdata[j]**2
                cont = 0

        j += 1

    lnoise = sump / j
    '''
    return _noise.hildebrand_sekhon(sortdata, navg)


class Beam:

    def __init__(self):
        self.codeList = []
        self.azimuthList = []
        self.zenithList = []


class GenericData(object):

    flagNoData = True

    def copy(self, inputObj=None):

        if inputObj == None:
            return copy.deepcopy(self)

        for key in list(inputObj.__dict__.keys()):

            attribute = inputObj.__dict__[key]

            # If this attribute is a tuple or list
            if type(inputObj.__dict__[key]) in (tuple, list):
                self.__dict__[key] = attribute[:]
                continue

            # If this attribute is another object or instance
            if hasattr(attribute, '__dict__'):
                self.__dict__[key] = attribute.copy()
                continue

            self.__dict__[key] = inputObj.__dict__[key]

    def deepcopy(self):

        return copy.deepcopy(self)

    def isEmpty(self):

        return self.flagNoData

    def isReady(self):

        return not self.flagNoData


class JROData(GenericData):

    systemHeaderObj = SystemHeader()
    radarControllerHeaderObj = RadarControllerHeader()
    type = None
    datatype = None  # dtype but in string
    nProfiles = None
    heightList = None
    channelList = None
    flagDiscontinuousBlock = False
    useLocalTime = False
    utctime = None
    timeZone = None
    dstFlag = None
    errorCount = None
    blocksize = None
    flagDecodeData = False  # asumo q la data no esta decodificada
    flagDeflipData = False  # asumo q la data no esta sin flip
    flagShiftFFT = False
    nCohInt = None
    windowOfFilter = 1
    C = 3e8
    frequency = 49.92e6
    realtime = False
    beacon_heiIndexList = None
    last_block = None
    blocknow = None
    azimuth = None
    zenith = None
    beam = Beam()
    profileIndex = None
    error = None
    data = None
    nmodes = None
    metadata_list = ['heightList', 'timeZone', 'type']

    def __str__(self):

        return '{} - {}'.format(self.type, self.datatime())

    def getNoise(self):

        raise NotImplementedError

    @property
    def nChannels(self):

        return len(self.channelList)

    @property
    def channelIndexList(self):

        return list(range(self.nChannels))

    @property
    def nHeights(self):

        return len(self.heightList)

    def getDeltaH(self):

        return self.heightList[1] - self.heightList[0]

    @property
    def ltctime(self):

        if self.useLocalTime:
            return self.utctime - self.timeZone * 60

        return self.utctime

    @property
    def datatime(self):

        datatimeValue = datetime.datetime.utcfromtimestamp(self.ltctime)
        return datatimeValue

    def getTimeRange(self):

        datatime = []

        datatime.append(self.ltctime)
        datatime.append(self.ltctime + self.timeInterval + 1)

        datatime = numpy.array(datatime)

        return datatime

    def getFmaxTimeResponse(self):

        period = (10**-6) * self.getDeltaH() / (0.15)

        PRF = 1. / (period * self.nCohInt)

        fmax = PRF

        return fmax

    def getFmax(self):
        PRF = 1. / (self.ippSeconds * self.nCohInt)

        fmax = PRF
        return fmax

    def getVmax(self):

        _lambda = self.C / self.frequency

        vmax = self.getFmax() * _lambda / 2

        return vmax

    @property
    def ippSeconds(self):
        '''
        '''
        return self.radarControllerHeaderObj.ippSeconds
    
    @ippSeconds.setter
    def ippSeconds(self, ippSeconds):
        '''
        '''
        self.radarControllerHeaderObj.ippSeconds = ippSeconds
    
    @property
    def code(self):
        '''
        '''
        return self.radarControllerHeaderObj.code

    @code.setter
    def code(self, code):
        '''
        '''
        self.radarControllerHeaderObj.code = code

    @property
    def nCode(self):
        '''
        '''
        return self.radarControllerHeaderObj.nCode

    @nCode.setter
    def nCode(self, ncode):
        '''
        '''
        self.radarControllerHeaderObj.nCode = ncode

    @property
    def nBaud(self):
        '''
        '''
        return self.radarControllerHeaderObj.nBaud

    @nBaud.setter
    def nBaud(self, nbaud):
        '''
        '''
        self.radarControllerHeaderObj.nBaud = nbaud

    @property
    def ipp(self):
        '''
        '''
        return self.radarControllerHeaderObj.ipp

    @ipp.setter
    def ipp(self, ipp):
        '''
        '''
        self.radarControllerHeaderObj.ipp = ipp

    @property
    def metadata(self):
        '''
        '''

        return {attr: getattr(self, attr) for attr in self.metadata_list}


class Voltage(JROData):

    dataPP_POW   = None
    dataPP_DOP   = None
    dataPP_WIDTH = None
    dataPP_SNR   = None

    def __init__(self):
        '''
        Constructor
        '''

        self.useLocalTime = True
        self.radarControllerHeaderObj = RadarControllerHeader()
        self.systemHeaderObj = SystemHeader()
        self.type = "Voltage"
        self.data = None
        self.nProfiles = None
        self.heightList = None
        self.channelList = None
        self.flagNoData = True
        self.flagDiscontinuousBlock = False
        self.utctime = None
        self.timeZone = 0
        self.dstFlag = None
        self.errorCount = None
        self.nCohInt = None
        self.blocksize = None
        self.flagCohInt = False
        self.flagDecodeData = False  # asumo q la data no esta decodificada
        self.flagDeflipData = False  # asumo q la data no esta sin flip
        self.flagShiftFFT = False
        self.flagDataAsBlock = False  # Asumo que la data es leida perfil a perfil
        self.profileIndex = 0
        self.metadata_list = ['type', 'heightList', 'timeZone', 'nProfiles', 'channelList', 'nCohInt', 
            'code', 'nCode', 'nBaud', 'ippSeconds', 'ipp']

    def getNoisebyHildebrand(self, channel=None):
        """
        Determino el nivel de ruido usando el metodo Hildebrand-Sekhon

        Return:
            noiselevel
        """

        if channel != None:
            data = self.data[channel]
            nChannels = 1
        else:
            data = self.data
            nChannels = self.nChannels

        noise = numpy.zeros(nChannels)
        power = data * numpy.conjugate(data)

        for thisChannel in range(nChannels):
            if nChannels == 1:
                daux = power[:].real
            else:
                daux = power[thisChannel, :].real
            noise[thisChannel] = hildebrand_sekhon(daux, self.nCohInt)

        return noise

    def getNoise(self, type=1, channel=None):

        if type == 1:
            noise = self.getNoisebyHildebrand(channel)

        return noise

    def getPower(self, channel=None):

        if channel != None:
            data = self.data[channel]
        else:
            data = self.data

        power = data * numpy.conjugate(data)
        powerdB = 10 * numpy.log10(power.real)
        powerdB = numpy.squeeze(powerdB)

        return powerdB

    @property
    def timeInterval(self):

        return self.ippSeconds * self.nCohInt

    noise = property(getNoise, "I'm the 'nHeights' property.")


class Spectra(JROData):

    def __init__(self):
        '''
        Constructor
        '''

        self.useLocalTime = True
        self.radarControllerHeaderObj = RadarControllerHeader()
        self.systemHeaderObj = SystemHeader()
        self.type = "Spectra"
        self.timeZone = 0
        self.nProfiles = None
        self.heightList = None
        self.channelList = None
        self.pairsList = None
        self.flagNoData = True
        self.flagDiscontinuousBlock = False
        self.utctime = None
        self.nCohInt = None
        self.nIncohInt = None
        self.blocksize = None
        self.nFFTPoints = None
        self.wavelength = None
        self.flagDecodeData = False  # asumo q la data no esta decodificada
        self.flagDeflipData = False  # asumo q la data no esta sin flip
        self.flagShiftFFT = False
        self.ippFactor = 1
        self.beacon_heiIndexList = []
        self.noise_estimation = None
        self.metadata_list = ['type', 'heightList', 'timeZone', 'pairsList', 'channelList', 'nCohInt', 
            'code', 'nCode', 'nBaud', 'ippSeconds', 'ipp','nIncohInt', 'nFFTPoints', 'nProfiles']

    def getNoisebyHildebrand(self, xmin_index=None, xmax_index=None, ymin_index=None, ymax_index=None):
        """
        Determino el nivel de ruido usando el metodo Hildebrand-Sekhon

        Return:
            noiselevel
        """

        noise = numpy.zeros(self.nChannels)

        for channel in range(self.nChannels):
            daux = self.data_spc[channel,
                                 xmin_index:xmax_index, ymin_index:ymax_index]
            noise[channel] = hildebrand_sekhon(daux, self.nIncohInt)

        return noise

    def getNoise(self, xmin_index=None, xmax_index=None, ymin_index=None, ymax_index=None):

        if self.noise_estimation is not None:
            # this was estimated by getNoise Operation defined in jroproc_spectra.py
            return self.noise_estimation
        else:
            noise = self.getNoisebyHildebrand(
                xmin_index, xmax_index, ymin_index, ymax_index)
            return noise

    def getFreqRangeTimeResponse(self, extrapoints=0):

        deltafreq = self.getFmaxTimeResponse() / (self.nFFTPoints * self.ippFactor)
        freqrange = deltafreq * (numpy.arange(self.nFFTPoints + extrapoints) - self.nFFTPoints / 2.) - deltafreq / 2

        return freqrange

    def getAcfRange(self, extrapoints=0):

        deltafreq = 10. / (self.getFmax() / (self.nFFTPoints * self.ippFactor))
        freqrange = deltafreq * (numpy.arange(self.nFFTPoints + extrapoints) -self.nFFTPoints / 2.) - deltafreq / 2

        return freqrange

    def getFreqRange(self, extrapoints=0):

        deltafreq = self.getFmax() / (self.nFFTPoints * self.ippFactor)
        freqrange = deltafreq * (numpy.arange(self.nFFTPoints + extrapoints) -self.nFFTPoints / 2.) - deltafreq / 2

        return freqrange

    def getVelRange(self, extrapoints=0):

        deltav = self.getVmax() / (self.nFFTPoints * self.ippFactor)
        velrange = deltav * (numpy.arange(self.nFFTPoints + extrapoints) - self.nFFTPoints / 2.)

        if self.nmodes:
            return velrange/self.nmodes
        else:
            return velrange

    @property
    def nPairs(self):

        return len(self.pairsList)

    @property
    def pairsIndexList(self):

        return list(range(self.nPairs))

    @property
    def normFactor(self):

        pwcode = 1

        if self.flagDecodeData:
            pwcode = numpy.sum(self.code[0]**2)
        #normFactor = min(self.nFFTPoints,self.nProfiles)*self.nIncohInt*self.nCohInt*pwcode*self.windowOfFilter
        normFactor = self.nProfiles * self.nIncohInt * self.nCohInt * pwcode * self.windowOfFilter

        return normFactor

    @property
    def flag_cspc(self):

        if self.data_cspc is None:
            return True

        return False

    @property
    def flag_dc(self):

        if self.data_dc is None:
            return True

        return False

    @property
    def timeInterval(self):

        timeInterval = self.ippSeconds * self.nCohInt * self.nIncohInt * self.nProfiles * self.ippFactor
        if self.nmodes:
            return self.nmodes*timeInterval
        else:
            return timeInterval

    def getPower(self):

        factor = self.normFactor
        z = self.data_spc / factor
        z = numpy.where(numpy.isfinite(z), z, numpy.NAN)
        avg = numpy.average(z, axis=1)

        return 10 * numpy.log10(avg)

    def getCoherence(self, pairsList=None, phase=False):

        z = []
        if pairsList is None:
            pairsIndexList = self.pairsIndexList
        else:
            pairsIndexList = []
            for pair in pairsList:
                if pair not in self.pairsList:
                    raise ValueError("Pair %s is not in dataOut.pairsList" % (
                        pair))
                pairsIndexList.append(self.pairsList.index(pair))
        for i in range(len(pairsIndexList)):
            pair = self.pairsList[pairsIndexList[i]]
            ccf = numpy.average(self.data_cspc[pairsIndexList[i], :, :], axis=0)
            powa = numpy.average(self.data_spc[pair[0], :, :], axis=0)
            powb = numpy.average(self.data_spc[pair[1], :, :], axis=0)
            avgcoherenceComplex = ccf / numpy.sqrt(powa * powb)
            if phase:
                data = numpy.arctan2(avgcoherenceComplex.imag,
                                     avgcoherenceComplex.real) * 180 / numpy.pi
            else:
                data = numpy.abs(avgcoherenceComplex)

            z.append(data)

        return numpy.array(z)

    def setValue(self, value):

        print("This property should not be initialized")

        return
    
    noise = property(getNoise, setValue, "I'm the 'nHeights' property.")


class SpectraHeis(Spectra):

    def __init__(self):

        self.radarControllerHeaderObj = RadarControllerHeader()
        self.systemHeaderObj = SystemHeader()
        self.type = "SpectraHeis"
        self.nProfiles = None
        self.heightList = None
        self.channelList = None
        self.flagNoData = True
        self.flagDiscontinuousBlock = False
        self.utctime = None
        self.blocksize = None
        self.profileIndex = 0
        self.nCohInt = 1
        self.nIncohInt = 1

    @property
    def normFactor(self):
        pwcode = 1
        if self.flagDecodeData:
            pwcode = numpy.sum(self.code[0]**2)

        normFactor = self.nIncohInt * self.nCohInt * pwcode

        return normFactor

    @property
    def timeInterval(self):

        return self.ippSeconds * self.nCohInt * self.nIncohInt


class Fits(JROData):

    def __init__(self):

        self.type = "Fits"
        self.nProfiles = None
        self.heightList = None
        self.channelList = None
        self.flagNoData = True
        self.utctime = None
        self.nCohInt = 1
        self.nIncohInt = 1
        self.useLocalTime = True
        self.profileIndex = 0
        self.timeZone = 0

    def getTimeRange(self):

        datatime = []

        datatime.append(self.ltctime)
        datatime.append(self.ltctime + self.timeInterval)

        datatime = numpy.array(datatime)

        return datatime

    def getChannelIndexList(self):

        return list(range(self.nChannels))

    def getNoise(self, type=1):


        if type == 1:
            noise = self.getNoisebyHildebrand()

        if type == 2:
            noise = self.getNoisebySort()

        if type == 3:
            noise = self.getNoisebyWindow()

        return noise

    @property
    def timeInterval(self):

        timeInterval = self.ippSeconds * self.nCohInt * self.nIncohInt

        return timeInterval

    @property
    def ippSeconds(self):
        '''
        '''
        return self.ipp_sec

    noise = property(getNoise, "I'm the 'nHeights' property.")
    

class Correlation(JROData):

    def __init__(self):
        '''
        Constructor
        '''
        self.radarControllerHeaderObj = RadarControllerHeader()
        self.systemHeaderObj = SystemHeader()
        self.type = "Correlation"
        self.data = None
        self.dtype = None
        self.nProfiles = None
        self.heightList = None
        self.channelList = None
        self.flagNoData = True
        self.flagDiscontinuousBlock = False
        self.utctime = None
        self.timeZone = 0
        self.dstFlag = None
        self.errorCount = None
        self.blocksize = None
        self.flagDecodeData = False  # asumo q la data no esta decodificada
        self.flagDeflipData = False  # asumo q la data no esta sin flip
        self.pairsList = None
        self.nPoints = None

    def getPairsList(self):

        return self.pairsList

    def getNoise(self, mode=2):

        indR = numpy.where(self.lagR == 0)[0][0]
        indT = numpy.where(self.lagT == 0)[0][0]

        jspectra0 = self.data_corr[:, :, indR, :]
        jspectra = copy.copy(jspectra0)

        num_chan = jspectra.shape[0]
        num_hei = jspectra.shape[2]

        freq_dc = jspectra.shape[1] / 2
        ind_vel = numpy.array([-2, -1, 1, 2]) + freq_dc

        if ind_vel[0] < 0:
            ind_vel[list(range(0, 1))] = ind_vel[list(
                range(0, 1))] + self.num_prof

        if mode == 1:
            jspectra[:, freq_dc, :] = (
                jspectra[:, ind_vel[1], :] + jspectra[:, ind_vel[2], :]) / 2  # CORRECCION

        if mode == 2:

            vel = numpy.array([-2, -1, 1, 2])
            xx = numpy.zeros([4, 4])

            for fil in range(4):
                xx[fil, :] = vel[fil]**numpy.asarray(list(range(4)))

            xx_inv = numpy.linalg.inv(xx)
            xx_aux = xx_inv[0, :]

            for ich in range(num_chan):
                yy = jspectra[ich, ind_vel, :]
                jspectra[ich, freq_dc, :] = numpy.dot(xx_aux, yy)

                junkid = jspectra[ich, freq_dc, :] <= 0
                cjunkid = sum(junkid)

                if cjunkid.any():
                    jspectra[ich, freq_dc, junkid.nonzero()] = (
                        jspectra[ich, ind_vel[1], junkid] + jspectra[ich, ind_vel[2], junkid]) / 2

        noise = jspectra0[:, freq_dc, :] - jspectra[:, freq_dc, :]

        return noise

    @property
    def timeInterval(self):

        return self.ippSeconds * self.nCohInt * self.nProfiles

    def splitFunctions(self):

        pairsList = self.pairsList
        ccf_pairs = []
        acf_pairs = []
        ccf_ind = []
        acf_ind = []
        for l in range(len(pairsList)):
            chan0 = pairsList[l][0]
            chan1 = pairsList[l][1]

            # Obteniendo pares de Autocorrelacion
            if chan0 == chan1:
                acf_pairs.append(chan0)
                acf_ind.append(l)
            else:
                ccf_pairs.append(pairsList[l])
                ccf_ind.append(l)

        data_acf = self.data_cf[acf_ind]
        data_ccf = self.data_cf[ccf_ind]

        return acf_ind, ccf_ind, acf_pairs, ccf_pairs, data_acf, data_ccf

    @property
    def normFactor(self):
        acf_ind, ccf_ind, acf_pairs, ccf_pairs, data_acf, data_ccf = self.splitFunctions()
        acf_pairs = numpy.array(acf_pairs)
        normFactor = numpy.zeros((self.nPairs, self.nHeights))

        for p in range(self.nPairs):
            pair = self.pairsList[p]

            ch0 = pair[0]
            ch1 = pair[1]

            ch0_max = numpy.max(data_acf[acf_pairs == ch0, :, :], axis=1)
            ch1_max = numpy.max(data_acf[acf_pairs == ch1, :, :], axis=1)
            normFactor[p, :] = numpy.sqrt(ch0_max * ch1_max)

        return normFactor


class Parameters(Spectra):

    groupList = None  # List of Pairs, Groups, etc
    data_param = None  # Parameters obtained
    data_pre = None  # Data Pre Parametrization
    data_SNR = None  # Signal to Noise Ratio
    abscissaList = None  # Abscissa, can be velocities, lags or time
    utctimeInit = None  # Initial UTC time
    paramInterval = None  # Time interval to calculate Parameters in seconds
    useLocalTime = True
    # Fitting
    data_error = None  # Error of the estimation
    constants = None
    library = None
    # Output signal
    outputInterval = None  # Time interval to calculate output signal in seconds
    data_output = None  # Out signal
    nAvg = None
    noise_estimation = None
    GauSPC = None  # Fit gaussian SPC

    def __init__(self):
        '''
        Constructor
        '''
        self.radarControllerHeaderObj = RadarControllerHeader()
        self.systemHeaderObj = SystemHeader()
        self.type = "Parameters"
        self.timeZone = 0

    def getTimeRange1(self, interval):

        datatime = []

        if self.useLocalTime:
            time1 = self.utctimeInit - self.timeZone * 60
        else:
            time1 = self.utctimeInit

        datatime.append(time1)
        datatime.append(time1 + interval)
        datatime = numpy.array(datatime)

        return datatime

    @property
    def timeInterval(self):

        if hasattr(self, 'timeInterval1'):
            return self.timeInterval1
        else:
            return self.paramInterval

    def setValue(self, value):

        print("This property should not be initialized")

        return

    def getNoise(self):

        return self.spc_noise

    noise = property(getNoise, setValue, "I'm the 'Noise' property.")


class PlotterData(object):
    '''
    Object to hold data to be plotted
    '''

    MAXNUMX = 200
    MAXNUMY = 200

    def __init__(self, code, exp_code, localtime=True):

        self.key = code
        self.exp_code = exp_code
        self.ready = False
        self.flagNoData = False
        self.localtime = localtime
        self.data = {}
        self.meta = {}
        self.__heights = []

    def __str__(self):
        dum = ['{}{}'.format(key, self.shape(key)) for key in self.data]
        return 'Data[{}][{}]'.format(';'.join(dum), len(self.times))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.data[self.times[key]]
        elif isinstance(key, str):
            ret = numpy.array([self.data[x][key] for x in self.times])
            if ret.ndim > 1:
                ret = numpy.swapaxes(ret, 0, 1)
            return ret

    def __contains__(self, key):
        return key in self.data[self.min_time]

    def setup(self):
        '''
        Configure object
        '''
        self.type = ''
        self.ready = False
        del self.data
        self.data = {}
        self.__heights = []
        self.__all_heights = set()

    def shape(self, key):
        '''
        Get the shape of the one-element data for the given key
        '''

        if len(self.data[self.min_time][key]):
            return self.data[self.min_time][key].shape
        return (0,)

    def update(self, data, tm, meta={}):
        '''
        Update data object with new dataOut
        '''

        self.data[tm] = data
        
        for key, value in meta.items():
            setattr(self, key, value)

    def normalize_heights(self):
        '''
        Ensure same-dimension of the data for different heighList
        '''

        H = numpy.array(list(self.__all_heights))
        H.sort()
        for key in self.data:
            shape = self.shape(key)[:-1] + H.shape
            for tm, obj in list(self.data[key].items()):
                h = self.__heights[self.times.tolist().index(tm)]
                if H.size == h.size:
                    continue
                index = numpy.where(numpy.in1d(H, h))[0]
                dummy = numpy.zeros(shape) + numpy.nan
                if len(shape) == 2:
                    dummy[:, index] = obj
                else:
                    dummy[index] = obj
                self.data[key][tm] = dummy

        self.__heights = [H for tm in self.times]

    def jsonify(self, tm, plot_name, plot_type, decimate=False):
        '''
        Convert data to json
        '''

        meta = {}
        meta['xrange'] = []
        dy = int(len(self.yrange)/self.MAXNUMY) + 1
        tmp = self.data[tm][self.key]
        shape = tmp.shape
        if len(shape) == 2:
            data = self.roundFloats(self.data[tm][self.key][::, ::dy].tolist())
        elif len(shape) == 3:
            dx = int(self.data[tm][self.key].shape[1]/self.MAXNUMX) + 1
            data = self.roundFloats(
                self.data[tm][self.key][::, ::dx, ::dy].tolist())
            meta['xrange'] = self.roundFloats(self.xrange[2][::dx].tolist())
        else:
            data = self.roundFloats(self.data[tm][self.key].tolist())
        
        ret = {
            'plot': plot_name,
            'code': self.exp_code,
            'time': float(tm),
            'data': data,
            }
        meta['type'] = plot_type
        meta['interval'] = float(self.interval)
        meta['localtime'] = self.localtime
        meta['yrange'] = self.roundFloats(self.yrange[::dy].tolist())
        meta.update(self.meta)
        ret['metadata'] = meta
        return json.dumps(ret)

    @property
    def times(self):
        '''
        Return the list of times of the current data
        '''

        ret = [t for t in self.data]
        ret.sort()
        return numpy.array(ret)

    @property
    def min_time(self):
        '''
        Return the minimun time value
        '''

        return self.times[0]

    @property
    def max_time(self):
        '''
        Return the maximun time value
        '''

        return self.times[-1]

    # @property
    # def heights(self):
    #     '''
    #     Return the list of heights of the current data
    #     '''

    #     return numpy.array(self.__heights[-1])

    @staticmethod
    def roundFloats(obj):
        if isinstance(obj, list):
            return list(map(PlotterData.roundFloats, obj))
        elif isinstance(obj, float):
            return round(obj, 2)
