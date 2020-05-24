import numpy

from .jroproc_base import ProcessingUnit, Operation
from schainpy.model.data.jrodata import Correlation

class CorrelationProc(ProcessingUnit):

    pairsList = None

    data_cf = None

    def __init__(self, **kwargs):

        ProcessingUnit.__init__(self, **kwargs)

        self.objectDict = {}
        self.buffer = None
        self.firstdatatime = None
        self.profIndex = 0
        self.dataOut = Correlation()

    def __updateObjFromVoltage(self):

        self.dataOut.timeZone = self.dataIn.timeZone
        self.dataOut.dstFlag = self.dataIn.dstFlag
        self.dataOut.errorCount = self.dataIn.errorCount
        self.dataOut.useLocalTime = self.dataIn.useLocalTime

        self.dataOut.radarControllerHeaderObj = self.dataIn.radarControllerHeaderObj.copy()
        self.dataOut.systemHeaderObj = self.dataIn.systemHeaderObj.copy()
        self.dataOut.channelList = self.dataIn.channelList
        self.dataOut.heightList = self.dataIn.heightList
        self.dataOut.dtype = numpy.dtype([('real','<f4'),('imag','<f4')])
#         self.dataOut.nHeights = self.dataIn.nHeights
#         self.dataOut.nChannels = self.dataIn.nChannels
        self.dataOut.nBaud = self.dataIn.nBaud
        self.dataOut.nCode = self.dataIn.nCode
        self.dataOut.code = self.dataIn.code
#        self.dataOut.nProfiles = self.dataOut.nFFTPoints
        self.dataOut.flagDiscontinuousBlock = self.dataIn.flagDiscontinuousBlock
        self.dataOut.utctime = self.firstdatatime
        self.dataOut.flagDecodeData = self.dataIn.flagDecodeData #asumo q la data esta decodificada
        self.dataOut.flagDeflipData = self.dataIn.flagDeflipData #asumo q la data esta sin flip
        self.dataOut.nCohInt = self.dataIn.nCohInt
#        self.dataOut.nIncohInt = 1
        self.dataOut.ippSeconds = self.dataIn.ippSeconds
        self.dataOut.nProfiles = self.dataIn.nProfiles
        self.dataOut.utctime = self.dataIn.utctime
#        self.dataOut.windowOfFilter = self.dataIn.windowOfFilter

#         self.dataOut.timeInterval = self.dataIn.timeInterval*self.dataOut.nPoints


    def removeDC(self, jspectra):

        nChannel = jspectra.shape[0]

        for i in range(nChannel):
            jspectra_tmp = jspectra[i,:,:]
            jspectra_DC = numpy.mean(jspectra_tmp,axis = 0)

            jspectra_tmp = jspectra_tmp - jspectra_DC
            jspectra[i,:,:] = jspectra_tmp

        return jspectra


    def removeNoise(self, mode = 2):
        indR = numpy.where(self.dataOut.lagR == 0)[0][0]
        indT = numpy.where(self.dataOut.lagT == 0)[0][0]

        jspectra = self.dataOut.data_corr[:,:,indR,:]

        num_chan = jspectra.shape[0]
        num_hei = jspectra.shape[2]

        freq_dc = indT
        ind_vel = numpy.array([-2,-1,1,2]) + freq_dc

        NPot = self.dataOut.getNoise(mode)
        jspectra[:,freq_dc,:] = jspectra[:,freq_dc,:] - NPot
        SPot = jspectra[:,freq_dc,:]
        pairsAutoCorr = self.dataOut.getPairsAutoCorr()
#         self.dataOut.signalPotency = SPot
        self.dataOut.noise = NPot
        self.dataOut.SNR = (SPot/NPot)[pairsAutoCorr]
        self.dataOut.data_corr[:,:,indR,:] = jspectra

        return 1

    def run(self, lags=None, mode = 'time',  pairsList=None, fullBuffer=False, nAvg = 1, removeDC = False, splitCF=False):

        self.dataOut.flagNoData = True

        if self.dataIn.type == "Correlation":

            self.dataOut.copy(self.dataIn)

            return

        if self.dataIn.type == "Voltage":

            nChannels = self.dataIn.nChannels
            nProfiles = self.dataIn.nProfiles
            nHeights = self.dataIn.nHeights
            data_pre = self.dataIn.data

            #---------------    Remover DC    ------------
            if removeDC:
                data_pre = self.removeDC(data_pre)

            #---------------------------------------------
#             pairsList = list(ccfList)
#             for i in acfList:
#                 pairsList.append((i,i))
#
#             ccf_pairs = numpy.arange(len(ccfList))
#             acf_pairs = numpy.arange(len(ccfList),len(pairsList))
            self.__updateObjFromVoltage()
            #----------------------------------------------------------------------
            #Creating temporal buffers
            if fullBuffer:
                tmp = numpy.zeros((len(pairsList), len(lags), nProfiles, nHeights), dtype = 'complex')*numpy.nan
            elif mode == 'time':
                if lags == None:
                    lags = numpy.arange(-nProfiles+1, nProfiles)
                tmp = numpy.zeros((len(pairsList), len(lags), nHeights),dtype='complex')
            elif mode == 'height':
                if lags == None:
                    lags = numpy.arange(-nHeights+1, nHeights)
                tmp = numpy.zeros(len(pairsList), (len(lags), nProfiles),dtype='complex')

            #For loop
            for l in range(len(pairsList)):

                ch0 = pairsList[l][0]
                ch1 = pairsList[l][1]

                for i in range(len(lags)):
                    idx = lags[i]

                    if idx >= 0:
                        if mode == 'time':
                            ccf0 = data_pre[ch0,:nProfiles-idx,:]*numpy.conj(data_pre[ch1,idx:,:]) #time
                        else:
                            ccf0 = data_pre[ch0,:,nHeights-idx]*numpy.conj(data_pre[ch1,:,idx:])   #heights
                    else:
                        if mode == 'time':
                            ccf0 = data_pre[ch0,-idx:,:]*numpy.conj(data_pre[ch1,:nProfiles+idx,:])  #time
                        else:
                            ccf0 = data_pre[ch0,:,-idx:]*numpy.conj(data_pre[ch1,:,:nHeights+idx])   #heights

                    if fullBuffer:
                        tmp[l,i,:ccf0.shape[0],:] = ccf0
                    else:
                        tmp[l,i,:] = numpy.sum(ccf0, axis=0)

            #-----------------------------------------------------------------
            if fullBuffer:
                tmp = numpy.sum(numpy.reshape(tmp,(tmp.shape[0],tmp.shape[1],tmp.shape[2]/nAvg,nAvg,tmp.shape[3])),axis=3)
                self.dataOut.nAvg = nAvg

            self.dataOut.data_cf = tmp
            self.dataOut.mode = mode
            self.dataOut.nLags = len(lags)
            self.dataOut.pairsList = pairsList
            self.dataOut.nPairs = len(pairsList)

            #Se Calcula los factores de Normalizacion
            if mode == 'time':
                delta = self.dataIn.ippSeconds*self.dataIn.nCohInt
            else:
                delta = self.dataIn.heightList[1] - self.dataIn.heightList[0]
            self.dataOut.lagRange = numpy.array(lags)*delta
#             self.dataOut.nCohInt = self.dataIn.nCohInt*nAvg
            self.dataOut.flagNoData = False
#             a = self.dataOut.normFactor
            return
