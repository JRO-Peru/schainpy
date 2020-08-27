'''

$Author: murco $
$Id: JROData.py 173 2012-11-20 15:06:21Z murco $
'''

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

    #    m_BasicHeader = BasicHeader()
    #    m_ProcessingHeader = ProcessingHeader()

    systemHeaderObj = SystemHeader()
    radarControllerHeaderObj = RadarControllerHeader()
#    data = None
    type = None
    datatype = None  # dtype but in string
#     dtype = None
#    nChannels = None
#    nHeights = None
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
#     nCode = None
#     nBaud = None
#     code = None
    flagDecodeData = False  # asumo q la data no esta decodificada
    flagDeflipData = False  # asumo q la data no esta sin flip
    flagShiftFFT = False
#     ippSeconds = None
#     timeInterval = None
    nCohInt = None
#     noise = None
    windowOfFilter = 1
    # Speed of ligth
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

    def __str__(self):

        return '{} - {}'.format(self.type, self.getDatatime())

    def getNoise(self):

        raise NotImplementedError

    def getNChannels(self):

        return len(self.channelList)

    def getChannelIndexList(self):

        return list(range(self.nChannels))

    def getNHeights(self):

        return len(self.heightList)

    def getHeiRange(self, extrapoints=0):

        heis = self.heightList
#        deltah = self.heightList[1] - self.heightList[0]
#
#        heis.append(self.heightList[-1])

        return heis

    def getDeltaH(self):

        delta = self.heightList[1] - self.heightList[0]

        return delta

    def getltctime(self):

        if self.useLocalTime:
            return self.utctime - self.timeZone * 60

        return self.utctime

    def getDatatime(self):

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

    def get_code(self):
        '''
        '''
        return self.radarControllerHeaderObj.code

    def set_code(self, code):
        '''
        '''
        self.radarControllerHeaderObj.code = code

        return

    def get_ncode(self):
        '''
        '''
        return self.radarControllerHeaderObj.nCode

    def set_ncode(self, nCode):
        '''
        '''
        self.radarControllerHeaderObj.nCode = nCode

        return

    def get_nbaud(self):
        '''
        '''
        return self.radarControllerHeaderObj.nBaud

    def set_nbaud(self, nBaud):
        '''
        '''
        self.radarControllerHeaderObj.nBaud = nBaud

        return

    nChannels = property(getNChannels, "I'm the 'nChannel' property.")
    channelIndexList = property(
        getChannelIndexList, "I'm the 'channelIndexList' property.")
    nHeights = property(getNHeights, "I'm the 'nHeights' property.")
    #noise = property(getNoise, "I'm the 'nHeights' property.")
    datatime = property(getDatatime, "I'm the 'datatime' property")
    ltctime = property(getltctime, "I'm the 'ltctime' property")
    ippSeconds = property(get_ippSeconds, set_ippSeconds)
    dtype = property(get_dtype, set_dtype)
#     timeInterval = property(getTimeInterval, "I'm the 'timeInterval' property")
    code = property(get_code, set_code)
    nCode = property(get_ncode, set_ncode)
    nBaud = property(get_nbaud, set_nbaud)


class Voltage(JROData):

    # data es un numpy array de 2 dmensiones (canales, alturas)
    data = None
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
#         self.dtype = None
#        self.nChannels = 0
#        self.nHeights = 0
        self.nProfiles = None
        self.heightList = None
        self.channelList = None
#        self.channelIndexList = None
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

    def getTimeInterval(self):

        timeInterval = self.ippSeconds * self.nCohInt

        return timeInterval

    noise = property(getNoise, "I'm the 'nHeights' property.")
    timeInterval = property(getTimeInterval, "I'm the 'timeInterval' property")


class Spectra(JROData):

    # data spc es un numpy array de 2 dmensiones (canales, perfiles, alturas)
    data_spc = None
    # data cspc es un numpy array de 2 dmensiones (canales, pares, alturas)
    data_cspc = None
    # data dc es un numpy array de 2 dmensiones (canales, alturas)
    data_dc = None
    # data power
    data_pwr = None
    nFFTPoints = None
#     nPairs = None
    pairsList = None
    nIncohInt = None
    wavelength = None  # Necesario para cacular el rango de velocidad desde la frecuencia
    nCohInt = None  # se requiere para determinar el valor de timeInterval
    ippFactor = None
    profileIndex = 0
    plotting = "spectra"

    def __init__(self):
        '''
        Constructor
        '''

        self.useLocalTime = True
        self.radarControllerHeaderObj = RadarControllerHeader()
        self.systemHeaderObj = SystemHeader()
        self.type = "Spectra"
        self.timeZone = 0
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
        #self.noise = None
        self.beacon_heiIndexList = []
        self.noise_estimation = None

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

    def getNPairs(self):

        return len(self.pairsList)

    def getPairsIndexList(self):

        return list(range(self.nPairs))

    def getNormFactor(self):

        pwcode = 1

        if self.flagDecodeData:
            pwcode = numpy.sum(self.code[0]**2)
        #normFactor = min(self.nFFTPoints,self.nProfiles)*self.nIncohInt*self.nCohInt*pwcode*self.windowOfFilter
        normFactor = self.nProfiles * self.nIncohInt * self.nCohInt * pwcode * self.windowOfFilter

        return normFactor

    def getFlagCspc(self):

        if self.data_cspc is None:
            return True

        return False

    def getFlagDc(self):

        if self.data_dc is None:
            return True

        return False

    def getTimeInterval(self):

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

    nPairs = property(getNPairs, setValue, "I'm the 'nPairs' property.")
    pairsIndexList = property(
        getPairsIndexList, setValue, "I'm the 'pairsIndexList' property.")
    normFactor = property(getNormFactor, setValue,
                          "I'm the 'getNormFactor' property.")
    flag_cspc = property(getFlagCspc, setValue)
    flag_dc = property(getFlagDc, setValue)
    noise = property(getNoise, setValue, "I'm the 'nHeights' property.")
    timeInterval = property(getTimeInterval, setValue,
                            "I'm the 'timeInterval' property")


class SpectraHeis(Spectra):

    data_spc = None
    data_cspc = None
    data_dc = None
    nFFTPoints = None
#     nPairs = None
    pairsList = None
    nCohInt = None
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

        self.flagDiscontinuousBlock = False

#         self.nPairs = 0

        self.utctime = None

        self.blocksize = None

        self.profileIndex = 0

        self.nCohInt = 1

        self.nIncohInt = 1

    def getNormFactor(self):
        pwcode = 1
        if self.flagDecodeData:
            pwcode = numpy.sum(self.code[0]**2)

        normFactor = self.nIncohInt * self.nCohInt * pwcode

        return normFactor

    def getTimeInterval(self):

        timeInterval = self.ippSeconds * self.nCohInt * self.nIncohInt

        return timeInterval

    normFactor = property(getNormFactor, "I'm the 'getNormFactor' property.")
    timeInterval = property(getTimeInterval, "I'm the 'timeInterval' property")


class Fits(JROData):

    heightList = None
    channelList = None
    flagNoData = True
    flagDiscontinuousBlock = False
    useLocalTime = False
    utctime = None
#     ippSeconds = None
#     timeInterval = None
    nCohInt = None
    nIncohInt = None
    noise = None
    windowOfFilter = 1
    # Speed of ligth
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

        self.nCohInt = 1

        self.nIncohInt = 1

        self.useLocalTime = True

        self.profileIndex = 0

#         self.utctime = None
        self.timeZone = 0
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
            return self.utctime - self.timeZone * 60

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

    def getNHeights(self):

        return len(self.heightList)

    def getNChannels(self):

        return len(self.channelList)

    def getChannelIndexList(self):

        return list(range(self.nChannels))

    def getNoise(self, type=1):

        #noise = numpy.zeros(self.nChannels)

        if type == 1:
            noise = self.getNoisebyHildebrand()

        if type == 2:
            noise = self.getNoisebySort()

        if type == 3:
            noise = self.getNoisebyWindow()

        return noise

    def getTimeInterval(self):

        timeInterval = self.ippSeconds * self.nCohInt * self.nIncohInt

        return timeInterval

    def get_ippSeconds(self):
        '''
        '''
        return self.ipp_sec


    datatime = property(getDatatime, "I'm the 'datatime' property")
    nHeights = property(getNHeights, "I'm the 'nHeights' property.")
    nChannels = property(getNChannels, "I'm the 'nChannel' property.")
    channelIndexList = property(
        getChannelIndexList, "I'm the 'channelIndexList' property.")
    noise = property(getNoise, "I'm the 'nHeights' property.")

    ltctime = property(getltctime, "I'm the 'ltctime' property")
    timeInterval = property(getTimeInterval, "I'm the 'timeInterval' property")
    ippSeconds = property(get_ippSeconds, '')

class Correlation(JROData):

    noise = None
    SNR = None
    #--------------------------------------------------
    mode = None
    split = False
    data_cf = None
    lags = None
    lagRange = None
    pairsList = None
    normFactor = None
    #--------------------------------------------------
#     calculateVelocity = None
    nLags = None
    nPairs = None
    nAvg = None

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

    def getTimeInterval(self):

        timeInterval = self.ippSeconds * self.nCohInt * self.nProfiles

        return timeInterval

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

    def getNormFactor(self):
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

    timeInterval = property(getTimeInterval, "I'm the 'timeInterval' property")
    normFactor = property(getNormFactor, "I'm the 'normFactor property'")


class Parameters(Spectra):

    experimentInfo = None  # Information about the experiment
    # Information from previous data
    inputUnit = None  # Type of data to be processed
    operation = None  # Type of operation to parametrize
    # normFactor = None       #Normalization Factor
    groupList = None  # List of Pairs, Groups, etc
    # Parameters
    data_param = None  # Parameters obtained
    data_pre = None  # Data Pre Parametrization
    data_SNR = None  # Signal to Noise Ratio
#     heightRange = None      #Heights
    abscissaList = None  # Abscissa, can be velocities, lags or time
#    noise = None            #Noise Potency
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

    def getTimeInterval(self):

        if hasattr(self, 'timeInterval1'):
            return self.timeInterval1
        else:
            return self.paramInterval

    def setValue(self, value):

        print("This property should not be initialized")

        return

    def getNoise(self):

        return self.spc_noise

    timeInterval = property(getTimeInterval)
    noise = property(getNoise, setValue, "I'm the 'Noise' property.")


class PlotterData(object):
    '''
    Object to hold data to be plotted
    '''

    MAXNUMX = 200
    MAXNUMY = 200

    def __init__(self, code, throttle_value, exp_code, localtime=True, buffering=True, snr=False):

        self.key = code
        self.throttle = throttle_value
        self.exp_code = exp_code
        self.buffering = buffering
        self.ready = False
        self.flagNoData = False
        self.localtime = localtime
        self.data = {}
        self.meta = {}
        self.__heights = []

        if 'snr' in code:
            self.plottypes = ['snr']
        elif code == 'spc':
            self.plottypes = ['spc', 'noise', 'rti']
        elif code == 'cspc':
            self.plottypes = ['cspc', 'spc', 'noise', 'rti']
        elif code == 'rti':
            self.plottypes = ['noise', 'rti']
        else:
            self.plottypes = [code]

        if 'snr' not in self.plottypes and snr:
            self.plottypes.append('snr')

        for plot in self.plottypes:
            self.data[plot] = {}

    def __str__(self):
        dum = ['{}{}'.format(key, self.shape(key)) for key in self.data]
        return 'Data[{}][{}]'.format(';'.join(dum), len(self.times))

    def __len__(self):
        return len(self.data[self.key])

    def __getitem__(self, key):

        if key not in self.data:
            raise KeyError(log.error('Missing key: {}'.format(key)))
        if 'spc' in key or not self.buffering:
            ret = self.data[key][self.tm]
        elif 'scope' in key:
            ret = numpy.array(self.data[key][float(self.tm)])
        else:
            ret = numpy.array([self.data[key][x] for x in self.times])
            if ret.ndim > 1:
                ret = numpy.swapaxes(ret, 0, 1)
        return ret

    def __contains__(self, key):
        return key in self.data

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
        for plot in self.plottypes:
            if 'snr' in plot:
                plot = 'snr'
            elif 'spc_moments' == plot:
                plot = 'moments'
            self.data[plot] = {}

        if 'spc' in self.data or 'rti' in self.data or 'cspc' in self.data or 'moments' in self.data:
            self.data['noise'] = {}
            self.data['rti'] = {}
            if 'noise' not in self.plottypes:
                self.plottypes.append('noise')
            if 'rti' not in self.plottypes:
                self.plottypes.append('rti')

    def shape(self, key):
        '''
        Get the shape of the one-element data for the given key
        '''

        if len(self.data[key]):
            if 'spc' in key or not self.buffering:
                return self.data[key].shape
            return self.data[key][self.times[0]].shape
        return (0,)

    def update(self, dataOut, tm):
        '''
        Update data object with new dataOut
        '''

        self.profileIndex = dataOut.profileIndex
        self.tm = tm
        self.type = dataOut.type
        self.parameters = getattr(dataOut, 'parameters', [])

        if hasattr(dataOut, 'meta'):
            self.meta.update(dataOut.meta)

        if hasattr(dataOut, 'pairsList'):
            self.pairs = dataOut.pairsList

        self.interval = dataOut.getTimeInterval()
        if True in ['spc' in ptype for ptype in self.plottypes]:
            self.xrange = (dataOut.getFreqRange(1)/1000.,
                           dataOut.getAcfRange(1), dataOut.getVelRange(1))
        self.__heights.append(dataOut.heightList)
        self.__all_heights.update(dataOut.heightList)

        for plot in self.plottypes:
            if plot in ('spc', 'spc_moments', 'spc_cut'):
                z = dataOut.data_spc/dataOut.normFactor
                buffer = 10*numpy.log10(z)
            if plot == 'cspc':
                buffer = (dataOut.data_spc, dataOut.data_cspc)
            if plot == 'noise':
                buffer = 10*numpy.log10(dataOut.getNoise()/dataOut.normFactor)
            if plot in ('rti', 'spcprofile'):
                buffer = dataOut.getPower()
            if plot == 'snr_db':
                buffer = dataOut.data_SNR
            if plot == 'snr':
                buffer = 10*numpy.log10(dataOut.data_SNR)
            if plot == 'dop':
                buffer = dataOut.data_DOP
            if plot == 'pow':
                buffer = 10*numpy.log10(dataOut.data_POW)
            if plot == 'width':
                buffer = dataOut.data_WIDTH
            if plot == 'coh':
                buffer = dataOut.getCoherence()
            if plot == 'phase':
                buffer = dataOut.getCoherence(phase=True)
            if plot == 'output':
                buffer = dataOut.data_output
            if plot == 'param':
                buffer = dataOut.data_param
            if plot == 'scope':
                buffer = dataOut.data
                self.flagDataAsBlock = dataOut.flagDataAsBlock
                self.nProfiles = dataOut.nProfiles
            if plot == 'pp_power':
                buffer = dataOut.dataPP_POWER
                self.flagDataAsBlock = dataOut.flagDataAsBlock
                self.nProfiles = dataOut.nProfiles
            if plot == 'pp_signal':
                buffer = dataOut.dataPP_POW
                self.flagDataAsBlock = dataOut.flagDataAsBlock
                self.nProfiles = dataOut.nProfiles
            if plot == 'pp_velocity':
                buffer = dataOut.dataPP_DOP
                self.flagDataAsBlock = dataOut.flagDataAsBlock
                self.nProfiles = dataOut.nProfiles
            if plot == 'pp_specwidth':
                buffer = dataOut.dataPP_WIDTH
                self.flagDataAsBlock = dataOut.flagDataAsBlock
                self.nProfiles = dataOut.nProfiles

            if plot == 'spc':
                self.data['spc'][tm] = buffer
            elif plot == 'cspc':
                self.data['cspc'][tm] = buffer
            elif plot == 'spc_moments':
                self.data['spc'][tm] = buffer
                self.data['moments'][tm] = dataOut.moments
            else:
                if self.buffering:
                    self.data[plot][tm] = buffer
                else:
                    self.data[plot][tm] = buffer

        if dataOut.channelList is None:
            self.channels = range(buffer.shape[0])
        else:
            self.channels = dataOut.channelList

        if buffer is None:
            self.flagNoData = True
            raise schainpy.admin.SchainWarning('Attribute data_{} is empty'.format(self.key))

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

        dy = int(self.heights.size/self.MAXNUMY) + 1
        if self.key in ('spc', 'cspc'):
            dx = int(self.data[self.key][tm].shape[1]/self.MAXNUMX) + 1
            data = self.roundFloats(
                self.data[self.key][tm][::, ::dx, ::dy].tolist())
        else:
            if self.key is 'noise':
                data = [[x] for x in self.roundFloats(self.data[self.key][tm].tolist())]
            else:
                data = self.roundFloats(self.data[self.key][tm][::, ::dy].tolist())

        meta = {}
        ret = {
            'plot': plot_name,
            'code': self.exp_code,
            'time': float(tm),
            'data': data,
            }
        meta['type'] = plot_type
        meta['interval'] = float(self.interval)
        meta['localtime'] = self.localtime
        meta['yrange'] = self.roundFloats(self.heights[::dy].tolist())
        if 'spc' in self.data or 'cspc' in self.data:
            meta['xrange'] = self.roundFloats(self.xrange[2][::dx].tolist())
        else:
            meta['xrange'] = []

        meta.update(self.meta)
        ret['metadata'] = meta
        return json.dumps(ret)

    @property
    def times(self):
        '''
        Return the list of times of the current data
        '''

        ret = numpy.array([t for t in self.data[self.key]])
        if self:
            ret.sort()
        return ret

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

    @property
    def heights(self):
        '''
        Return the list of heights of the current data
        '''

        return numpy.array(self.__heights[-1])

    @staticmethod
    def roundFloats(obj):
        if isinstance(obj, list):
            return list(map(PlotterData.roundFloats, obj))
        elif isinstance(obj, float):
            return round(obj, 2)
