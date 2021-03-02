# Copyright (c) 2012-2020 Jicamarca Radio Observatory
# All rights reserved.
#
# Distributed under the terms of the BSD 3-clause license.
"""Spectra processing Unit and operations

Here you will find the processing unit `SpectraProc` and several operations
to work with Spectra data type
"""

import time
import itertools

import numpy

from schainpy.model.proc.jroproc_base import ProcessingUnit, MPDecorator, Operation
from schainpy.model.data.jrodata import Spectra
from schainpy.model.data.jrodata import hildebrand_sekhon
from schainpy.utils import log


class SpectraProc(ProcessingUnit):

    def __init__(self):

        ProcessingUnit.__init__(self)

        self.buffer = None
        self.firstdatatime = None
        self.profIndex = 0
        self.dataOut = Spectra()
        self.id_min = None
        self.id_max = None
        self.setupReq = False #Agregar a todas las unidades de proc

    def __updateSpecFromVoltage(self):

        self.dataOut.timeZone = self.dataIn.timeZone
        self.dataOut.dstFlag = self.dataIn.dstFlag
        self.dataOut.errorCount = self.dataIn.errorCount
        self.dataOut.useLocalTime = self.dataIn.useLocalTime
        try:
            self.dataOut.processingHeaderObj = self.dataIn.processingHeaderObj.copy()
        except:
            pass
        self.dataOut.radarControllerHeaderObj = self.dataIn.radarControllerHeaderObj.copy()
        self.dataOut.systemHeaderObj = self.dataIn.systemHeaderObj.copy()
        self.dataOut.channelList = self.dataIn.channelList
        self.dataOut.heightList = self.dataIn.heightList
        self.dataOut.dtype = numpy.dtype([('real', '<f4'), ('imag', '<f4')])
        self.dataOut.nProfiles = self.dataOut.nFFTPoints
        self.dataOut.flagDiscontinuousBlock = self.dataIn.flagDiscontinuousBlock
        self.dataOut.utctime = self.firstdatatime
        self.dataOut.flagDecodeData = self.dataIn.flagDecodeData
        self.dataOut.flagDeflipData = self.dataIn.flagDeflipData
        self.dataOut.flagShiftFFT = False
        self.dataOut.nCohInt = self.dataIn.nCohInt
        self.dataOut.nIncohInt = 1
        self.dataOut.windowOfFilter = self.dataIn.windowOfFilter
        self.dataOut.frequency = self.dataIn.frequency
        self.dataOut.realtime = self.dataIn.realtime
        self.dataOut.azimuth = self.dataIn.azimuth
        self.dataOut.zenith = self.dataIn.zenith
        self.dataOut.beam.codeList = self.dataIn.beam.codeList
        self.dataOut.beam.azimuthList = self.dataIn.beam.azimuthList
        self.dataOut.beam.zenithList = self.dataIn.beam.zenithList

    def __getFft(self):
        """
        Convierte valores de Voltaje a Spectra

        Affected:
            self.dataOut.data_spc
            self.dataOut.data_cspc
            self.dataOut.data_dc
            self.dataOut.heightList
            self.profIndex
            self.buffer
            self.dataOut.flagNoData
        """
        fft_volt = numpy.fft.fft(
            self.buffer, n=self.dataOut.nFFTPoints, axis=1)
        fft_volt = fft_volt.astype(numpy.dtype('complex'))
        dc = fft_volt[:, 0, :]

        # calculo de self-spectra
        fft_volt = numpy.fft.fftshift(fft_volt, axes=(1,))
        spc = fft_volt * numpy.conjugate(fft_volt)
        spc = spc.real

        blocksize = 0
        blocksize += dc.size
        blocksize += spc.size

        cspc = None
        pairIndex = 0
        if self.dataOut.pairsList != None:
            # calculo de cross-spectra
            cspc = numpy.zeros(
                (self.dataOut.nPairs, self.dataOut.nFFTPoints, self.dataOut.nHeights), dtype='complex')
            for pair in self.dataOut.pairsList:
                if pair[0] not in self.dataOut.channelList:
                    raise ValueError("Error getting CrossSpectra: pair 0 of %s is not in channelList = %s" % (
                        str(pair), str(self.dataOut.channelList)))
                if pair[1] not in self.dataOut.channelList:
                    raise ValueError("Error getting CrossSpectra: pair 1 of %s is not in channelList = %s" % (
                        str(pair), str(self.dataOut.channelList)))

                cspc[pairIndex, :, :] = fft_volt[pair[0], :, :] * \
                    numpy.conjugate(fft_volt[pair[1], :, :])
                pairIndex += 1
            blocksize += cspc.size

        self.dataOut.data_spc = spc
        self.dataOut.data_cspc = cspc
        self.dataOut.data_dc = dc
        self.dataOut.blockSize = blocksize
        self.dataOut.flagShiftFFT = False

    def run(self, nProfiles=None, nFFTPoints=None, pairsList=None, ippFactor=None, shift_fft=False):
        
        if self.dataIn.type == "Spectra":
            self.dataOut.copy(self.dataIn)
            if shift_fft:
                #desplaza a la derecha en el eje 2 determinadas posiciones
                shift = int(self.dataOut.nFFTPoints/2)
                self.dataOut.data_spc = numpy.roll(self.dataOut.data_spc, shift , axis=1)

                if self.dataOut.data_cspc is not None:
                    #desplaza a la derecha en el eje 2 determinadas posiciones
                    self.dataOut.data_cspc = numpy.roll(self.dataOut.data_cspc, shift, axis=1)
            if pairsList:
                self.__selectPairs(pairsList)

        elif self.dataIn.type == "Voltage":

            self.dataOut.flagNoData = True

            if nFFTPoints == None:
                raise ValueError("This SpectraProc.run() need nFFTPoints input variable")

            if nProfiles == None:
                nProfiles = nFFTPoints

            if ippFactor == None:
                self.dataOut.ippFactor = 1
            
            self.dataOut.nFFTPoints = nFFTPoints

            if self.buffer is None:
                self.buffer = numpy.zeros((self.dataIn.nChannels,
                                           nProfiles,
                                           self.dataIn.nHeights),
                                          dtype='complex')

            if self.dataIn.flagDataAsBlock:
                nVoltProfiles = self.dataIn.data.shape[1]

                if nVoltProfiles == nProfiles:
                    self.buffer = self.dataIn.data.copy()
                    self.profIndex = nVoltProfiles

                elif nVoltProfiles < nProfiles:

                    if self.profIndex == 0:
                        self.id_min = 0
                        self.id_max = nVoltProfiles

                    self.buffer[:, self.id_min:self.id_max,
                                :] = self.dataIn.data
                    self.profIndex += nVoltProfiles
                    self.id_min += nVoltProfiles
                    self.id_max += nVoltProfiles
                else:
                    raise ValueError("The type object %s has %d profiles, it should just has %d profiles" % (
                        self.dataIn.type, self.dataIn.data.shape[1], nProfiles))
                    self.dataOut.flagNoData = True
            else:
                self.buffer[:, self.profIndex, :] = self.dataIn.data.copy()
                self.profIndex += 1

            if self.firstdatatime == None:
                self.firstdatatime = self.dataIn.utctime

            if self.profIndex == nProfiles:
                self.__updateSpecFromVoltage()
                if pairsList == None:
                    self.dataOut.pairsList = [pair for pair in itertools.combinations(self.dataOut.channelList, 2)]
                else:
                    self.dataOut.pairsList = pairsList
                self.__getFft()
                self.dataOut.flagNoData = False
                self.firstdatatime = None
                self.profIndex = 0
        else:
            raise ValueError("The type of input object '%s' is not valid".format(
                self.dataIn.type))

    def __selectPairs(self, pairsList):

        if not pairsList:
            return

        pairs = []
        pairsIndex = []

        for pair in pairsList:
            if pair[0] not in self.dataOut.channelList or pair[1] not in self.dataOut.channelList:
                continue
            pairs.append(pair)
            pairsIndex.append(pairs.index(pair))

        self.dataOut.data_cspc = self.dataOut.data_cspc[pairsIndex]
        self.dataOut.pairsList = pairs

        return
    
    def selectFFTs(self, minFFT, maxFFT ):
        """
        Selecciona un bloque de datos en base a un grupo de valores de puntos FFTs segun el rango 
        minFFT<= FFT <= maxFFT
        """
        
        if (minFFT > maxFFT):
            raise ValueError("Error selecting heights: Height range (%d,%d) is not valid" % (minFFT, maxFFT))

        if (minFFT < self.dataOut.getFreqRange()[0]):
            minFFT = self.dataOut.getFreqRange()[0]

        if (maxFFT > self.dataOut.getFreqRange()[-1]):
            maxFFT = self.dataOut.getFreqRange()[-1]

        minIndex = 0
        maxIndex = 0
        FFTs = self.dataOut.getFreqRange()

        inda = numpy.where(FFTs >= minFFT)
        indb = numpy.where(FFTs <= maxFFT)

        try:
            minIndex = inda[0][0]
        except:
            minIndex = 0

        try:
            maxIndex = indb[0][-1]
        except:
            maxIndex = len(FFTs)

        self.selectFFTsByIndex(minIndex, maxIndex)

        return 1
    
    def getBeaconSignal(self, tauindex=0, channelindex=0, hei_ref=None):
        newheis = numpy.where(
            self.dataOut.heightList > self.dataOut.radarControllerHeaderObj.Taus[tauindex])

        if hei_ref != None:
            newheis = numpy.where(self.dataOut.heightList > hei_ref)

        minIndex = min(newheis[0])
        maxIndex = max(newheis[0])
        data_spc = self.dataOut.data_spc[:, :, minIndex:maxIndex + 1]
        heightList = self.dataOut.heightList[minIndex:maxIndex + 1]

        # determina indices
        nheis = int(self.dataOut.radarControllerHeaderObj.txB /
                    (self.dataOut.heightList[1] - self.dataOut.heightList[0]))
        avg_dB = 10 * \
            numpy.log10(numpy.sum(data_spc[channelindex, :, :], axis=0))
        beacon_dB = numpy.sort(avg_dB)[-nheis:]
        beacon_heiIndexList = []
        for val in avg_dB.tolist():
            if val >= beacon_dB[0]:
                beacon_heiIndexList.append(avg_dB.tolist().index(val))

        #data_spc = data_spc[:,:,beacon_heiIndexList]
        data_cspc = None
        if self.dataOut.data_cspc is not None:
            data_cspc = self.dataOut.data_cspc[:, :, minIndex:maxIndex + 1]
            #data_cspc = data_cspc[:,:,beacon_heiIndexList]

        data_dc = None
        if self.dataOut.data_dc is not None:
            data_dc = self.dataOut.data_dc[:, minIndex:maxIndex + 1]
            #data_dc = data_dc[:,beacon_heiIndexList]

        self.dataOut.data_spc = data_spc
        self.dataOut.data_cspc = data_cspc
        self.dataOut.data_dc = data_dc
        self.dataOut.heightList = heightList
        self.dataOut.beacon_heiIndexList = beacon_heiIndexList

        return 1

    def selectFFTsByIndex(self, minIndex, maxIndex):
        """
        
        """

        if (minIndex < 0) or (minIndex > maxIndex):
            raise ValueError("Error selecting heights: Index range (%d,%d) is not valid" % (minIndex, maxIndex))

        if (maxIndex >= self.dataOut.nProfiles):
            maxIndex = self.dataOut.nProfiles-1

        #Spectra
        data_spc = self.dataOut.data_spc[:,minIndex:maxIndex+1,:]

        data_cspc = None
        if self.dataOut.data_cspc is not None:
            data_cspc = self.dataOut.data_cspc[:,minIndex:maxIndex+1,:]

        data_dc = None
        if self.dataOut.data_dc is not None:
            data_dc = self.dataOut.data_dc[minIndex:maxIndex+1,:]

        self.dataOut.data_spc = data_spc
        self.dataOut.data_cspc = data_cspc
        self.dataOut.data_dc = data_dc
        
        self.dataOut.ippSeconds = self.dataOut.ippSeconds*(self.dataOut.nFFTPoints / numpy.shape(data_cspc)[1])
        self.dataOut.nFFTPoints = numpy.shape(data_cspc)[1]
        self.dataOut.profilesPerBlock = numpy.shape(data_cspc)[1]

        return 1

    def getNoise(self, minHei=None, maxHei=None, minVel=None, maxVel=None):
        # validacion de rango
        if minHei == None:
            minHei = self.dataOut.heightList[0]

        if maxHei == None:
            maxHei = self.dataOut.heightList[-1]

        if (minHei < self.dataOut.heightList[0]) or (minHei > maxHei):
            print('minHei: %.2f is out of the heights range' % (minHei))
            print('minHei is setting to %.2f' % (self.dataOut.heightList[0]))
            minHei = self.dataOut.heightList[0]

        if (maxHei > self.dataOut.heightList[-1]) or (maxHei < minHei):
            print('maxHei: %.2f is out of the heights range' % (maxHei))
            print('maxHei is setting to %.2f' % (self.dataOut.heightList[-1]))
            maxHei = self.dataOut.heightList[-1]

        # validacion de velocidades
        velrange = self.dataOut.getVelRange(1)

        if minVel == None:
            minVel = velrange[0]

        if maxVel == None:
            maxVel = velrange[-1]

        if (minVel < velrange[0]) or (minVel > maxVel):
            print('minVel: %.2f is out of the velocity range' % (minVel))
            print('minVel is setting to %.2f' % (velrange[0]))
            minVel = velrange[0]

        if (maxVel > velrange[-1]) or (maxVel < minVel):
            print('maxVel: %.2f is out of the velocity range' % (maxVel))
            print('maxVel is setting to %.2f' % (velrange[-1]))
            maxVel = velrange[-1]

        # seleccion de indices para rango
        minIndex = 0
        maxIndex = 0
        heights = self.dataOut.heightList

        inda = numpy.where(heights >= minHei)
        indb = numpy.where(heights <= maxHei)

        try:
            minIndex = inda[0][0]
        except:
            minIndex = 0

        try:
            maxIndex = indb[0][-1]
        except:
            maxIndex = len(heights)

        if (minIndex < 0) or (minIndex > maxIndex):
            raise ValueError("some value in (%d,%d) is not valid" % (
                minIndex, maxIndex))

        if (maxIndex >= self.dataOut.nHeights):
            maxIndex = self.dataOut.nHeights - 1

        # seleccion de indices para velocidades
        indminvel = numpy.where(velrange >= minVel)
        indmaxvel = numpy.where(velrange <= maxVel)
        try:
            minIndexVel = indminvel[0][0]
        except:
            minIndexVel = 0

        try:
            maxIndexVel = indmaxvel[0][-1]
        except:
            maxIndexVel = len(velrange)

        # seleccion del espectro
        data_spc = self.dataOut.data_spc[:,
                                         minIndexVel:maxIndexVel + 1, minIndex:maxIndex + 1]
        # estimacion de ruido
        noise = numpy.zeros(self.dataOut.nChannels)

        for channel in range(self.dataOut.nChannels):
            daux = data_spc[channel, :, :]
            sortdata = numpy.sort(daux, axis=None)
            noise[channel] = hildebrand_sekhon(sortdata, self.dataOut.nIncohInt)

        self.dataOut.noise_estimation = noise.copy()

        return 1

class removeDC(Operation):

    def run(self, dataOut, mode=2):
        self.dataOut = dataOut
        jspectra = self.dataOut.data_spc
        jcspectra = self.dataOut.data_cspc

        num_chan = jspectra.shape[0]
        num_hei = jspectra.shape[2]

        if jcspectra is not None:
            jcspectraExist = True
            num_pairs = jcspectra.shape[0]
        else:
            jcspectraExist = False

        freq_dc = int(jspectra.shape[1] / 2)
        ind_vel = numpy.array([-2, -1, 1, 2]) + freq_dc
        ind_vel = ind_vel.astype(int)

        if ind_vel[0] < 0:
            ind_vel[list(range(0, 1))] = ind_vel[list(range(0, 1))] + self.num_prof

        if mode == 1:
            jspectra[:, freq_dc, :] = (
                jspectra[:, ind_vel[1], :] + jspectra[:, ind_vel[2], :]) / 2  # CORRECCION

            if jcspectraExist:
                jcspectra[:, freq_dc, :] = (
                    jcspectra[:, ind_vel[1], :] + jcspectra[:, ind_vel[2], :]) / 2

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

            if jcspectraExist:
                for ip in range(num_pairs):
                    yy = jcspectra[ip, ind_vel, :]
                    jcspectra[ip, freq_dc, :] = numpy.dot(xx_aux, yy)

        self.dataOut.data_spc = jspectra
        self.dataOut.data_cspc = jcspectra

        return self.dataOut

class removeInterference(Operation):

    def removeInterference2(self):
        
        cspc = self.dataOut.data_cspc
        spc = self.dataOut.data_spc
        Heights = numpy.arange(cspc.shape[2]) 
        realCspc = numpy.abs(cspc)
        
        for i in range(cspc.shape[0]):
            LinePower= numpy.sum(realCspc[i], axis=0)
            Threshold = numpy.amax(LinePower)-numpy.sort(LinePower)[len(Heights)-int(len(Heights)*0.1)]
            SelectedHeights = Heights[ numpy.where( LinePower < Threshold ) ]
            InterferenceSum = numpy.sum( realCspc[i,:,SelectedHeights], axis=0 )
            InterferenceThresholdMin = numpy.sort(InterferenceSum)[int(len(InterferenceSum)*0.98)]
            InterferenceThresholdMax = numpy.sort(InterferenceSum)[int(len(InterferenceSum)*0.99)]
            
            
            InterferenceRange = numpy.where( ([InterferenceSum > InterferenceThresholdMin]))# , InterferenceSum < InterferenceThresholdMax]) )
            #InterferenceRange = numpy.where( ([InterferenceRange < InterferenceThresholdMax]))
            if len(InterferenceRange)<int(cspc.shape[1]*0.3):
                cspc[i,InterferenceRange,:] = numpy.NaN
            
        self.dataOut.data_cspc = cspc
        
    def removeInterference(self, interf = 2, hei_interf = None, nhei_interf = None, offhei_interf = None):

        jspectra = self.dataOut.data_spc
        jcspectra = self.dataOut.data_cspc
        jnoise = self.dataOut.getNoise()
        num_incoh = self.dataOut.nIncohInt

        num_channel = jspectra.shape[0]
        num_prof = jspectra.shape[1]
        num_hei = jspectra.shape[2]

        # hei_interf
        if hei_interf is None:
            count_hei = int(num_hei / 2)
            hei_interf = numpy.asmatrix(list(range(count_hei))) + num_hei - count_hei
            hei_interf = numpy.asarray(hei_interf)[0]
        # nhei_interf
        if (nhei_interf == None):
            nhei_interf = 5
        if (nhei_interf < 1):
            nhei_interf = 1
        if (nhei_interf > count_hei):
            nhei_interf = count_hei
        if (offhei_interf == None):
            offhei_interf = 0

        ind_hei = list(range(num_hei))
#         mask_prof = numpy.asarray(range(num_prof - 2)) + 1
#         mask_prof[range(num_prof/2 - 1,len(mask_prof))] += 1
        mask_prof = numpy.asarray(list(range(num_prof)))
        num_mask_prof = mask_prof.size
        comp_mask_prof = [0, num_prof / 2]

        # noise_exist:    Determina si la variable jnoise ha sido definida y contiene la informacion del ruido de cada canal
        if (jnoise.size < num_channel or numpy.isnan(jnoise).any()):
            jnoise = numpy.nan
        noise_exist = jnoise[0] < numpy.Inf

        # Subrutina de Remocion de la Interferencia
        for ich in range(num_channel):
            # Se ordena los espectros segun su potencia (menor a mayor)
            power = jspectra[ich, mask_prof, :]
            power = power[:, hei_interf]
            power = power.sum(axis=0)
            psort = power.ravel().argsort()

            # Se estima la interferencia promedio en los Espectros de Potencia empleando
            junkspc_interf = jspectra[ich, :, hei_interf[psort[list(range(
                offhei_interf, nhei_interf + offhei_interf))]]]

            if noise_exist:
                #    tmp_noise = jnoise[ich] / num_prof
                tmp_noise = jnoise[ich]
            junkspc_interf = junkspc_interf - tmp_noise
            #junkspc_interf[:,comp_mask_prof] = 0

            jspc_interf = junkspc_interf.sum(axis=0) / nhei_interf
            jspc_interf = jspc_interf.transpose()
            # Calculando el espectro de interferencia promedio
            noiseid = numpy.where(
                jspc_interf <= tmp_noise / numpy.sqrt(num_incoh))
            noiseid = noiseid[0]
            cnoiseid = noiseid.size
            interfid = numpy.where(
                jspc_interf > tmp_noise / numpy.sqrt(num_incoh))
            interfid = interfid[0]
            cinterfid = interfid.size

            if (cnoiseid > 0):
                jspc_interf[noiseid] = 0

            # Expandiendo los perfiles a limpiar
            if (cinterfid > 0):
                new_interfid = (
                    numpy.r_[interfid - 1, interfid, interfid + 1] + num_prof) % num_prof
                new_interfid = numpy.asarray(new_interfid)
                new_interfid = {x for x in new_interfid}
                new_interfid = numpy.array(list(new_interfid))
                new_cinterfid = new_interfid.size
            else:
                new_cinterfid = 0

            for ip in range(new_cinterfid):
                ind = junkspc_interf[:, new_interfid[ip]].ravel().argsort()
                jspc_interf[new_interfid[ip]
                            ] = junkspc_interf[ind[nhei_interf // 2], new_interfid[ip]]

            jspectra[ich, :, ind_hei] = jspectra[ich, :,
                                                 ind_hei] - jspc_interf  # Corregir indices

            # Removiendo la interferencia del punto de mayor interferencia
            ListAux = jspc_interf[mask_prof].tolist()
            maxid = ListAux.index(max(ListAux))

            if cinterfid > 0:
                for ip in range(cinterfid * (interf == 2) - 1):
                    ind = (jspectra[ich, interfid[ip], :] < tmp_noise *
                           (1 + 1 / numpy.sqrt(num_incoh))).nonzero()
                    cind = len(ind)

                    if (cind > 0):
                        jspectra[ich, interfid[ip], ind] = tmp_noise * \
                            (1 + (numpy.random.uniform(cind) - 0.5) /
                             numpy.sqrt(num_incoh))

                ind = numpy.array([-2, -1, 1, 2])
                xx = numpy.zeros([4, 4])

                for id1 in range(4):
                    xx[:, id1] = ind[id1]**numpy.asarray(list(range(4)))

                xx_inv = numpy.linalg.inv(xx)
                xx = xx_inv[:, 0]
                ind = (ind + maxid + num_mask_prof) % num_mask_prof
                yy = jspectra[ich, mask_prof[ind], :]
                jspectra[ich, mask_prof[maxid], :] = numpy.dot(
                    yy.transpose(), xx)

            indAux = (jspectra[ich, :, :] < tmp_noise *
                      (1 - 1 / numpy.sqrt(num_incoh))).nonzero()
            jspectra[ich, indAux[0], indAux[1]] = tmp_noise * \
                (1 - 1 / numpy.sqrt(num_incoh))

        # Remocion de Interferencia en el Cross Spectra
        if jcspectra is None:
            return jspectra, jcspectra
        num_pairs = int(jcspectra.size / (num_prof * num_hei))
        jcspectra = jcspectra.reshape(num_pairs, num_prof, num_hei)

        for ip in range(num_pairs):

            #-------------------------------------------

            cspower = numpy.abs(jcspectra[ip, mask_prof, :])
            cspower = cspower[:, hei_interf]
            cspower = cspower.sum(axis=0)

            cspsort = cspower.ravel().argsort()
            junkcspc_interf = jcspectra[ip, :, hei_interf[cspsort[list(range(
                offhei_interf, nhei_interf + offhei_interf))]]]
            junkcspc_interf = junkcspc_interf.transpose()
            jcspc_interf = junkcspc_interf.sum(axis=1) / nhei_interf

            ind = numpy.abs(jcspc_interf[mask_prof]).ravel().argsort()

            median_real = int(numpy.median(numpy.real(
                junkcspc_interf[mask_prof[ind[list(range(3 * num_prof // 4))]], :])))
            median_imag = int(numpy.median(numpy.imag(
                junkcspc_interf[mask_prof[ind[list(range(3 * num_prof // 4))]], :])))
            comp_mask_prof = [int(e) for e in comp_mask_prof]
            junkcspc_interf[comp_mask_prof, :] = numpy.complex(
                median_real, median_imag)

            for iprof in range(num_prof):
                ind = numpy.abs(junkcspc_interf[iprof, :]).ravel().argsort()
                jcspc_interf[iprof] = junkcspc_interf[iprof, ind[nhei_interf // 2]]

            # Removiendo la Interferencia
            jcspectra[ip, :, ind_hei] = jcspectra[ip,
                                                  :, ind_hei] - jcspc_interf

            ListAux = numpy.abs(jcspc_interf[mask_prof]).tolist()
            maxid = ListAux.index(max(ListAux))

            ind = numpy.array([-2, -1, 1, 2])
            xx = numpy.zeros([4, 4])

            for id1 in range(4):
                xx[:, id1] = ind[id1]**numpy.asarray(list(range(4)))

            xx_inv = numpy.linalg.inv(xx)
            xx = xx_inv[:, 0]

            ind = (ind + maxid + num_mask_prof) % num_mask_prof
            yy = jcspectra[ip, mask_prof[ind], :]
            jcspectra[ip, mask_prof[maxid], :] = numpy.dot(yy.transpose(), xx)

        # Guardar Resultados
        self.dataOut.data_spc = jspectra
        self.dataOut.data_cspc = jcspectra

        return 1

    def run(self, dataOut, interf = 2,hei_interf = None, nhei_interf = None, offhei_interf = None, mode=1):

        self.dataOut = dataOut

        if mode == 1:
            self.removeInterference(interf = 2,hei_interf = None, nhei_interf = None, offhei_interf = None)
        elif mode == 2:
            self.removeInterference2()

        return self.dataOut


class IncohInt(Operation):

    __profIndex = 0
    __withOverapping = False

    __byTime = False
    __initime = None
    __lastdatatime = None
    __integrationtime = None

    __buffer_spc = None
    __buffer_cspc = None
    __buffer_dc = None

    __dataReady = False

    __timeInterval = None

    n = None

    def __init__(self):

        Operation.__init__(self)

    def setup(self, n=None, timeInterval=None, overlapping=False):
        """
        Set the parameters of the integration class.

        Inputs:

            n        :    Number of coherent integrations
            timeInterval   :    Time of integration. If the parameter "n" is selected this one does not work
            overlapping    :

        """

        self.__initime = None
        self.__lastdatatime = 0

        self.__buffer_spc = 0
        self.__buffer_cspc = 0
        self.__buffer_dc = 0

        self.__profIndex = 0
        self.__dataReady = False
        self.__byTime = False

        if n is None and timeInterval is None:
            raise ValueError("n or timeInterval should be specified ...")

        if n is not None:
            self.n = int(n)
        else:
            
            self.__integrationtime = int(timeInterval)
            self.n = None
            self.__byTime = True

    def putData(self, data_spc, data_cspc, data_dc):
        """
        Add a profile to the __buffer_spc and increase in one the __profileIndex

        """

        self.__buffer_spc += data_spc

        if data_cspc is None:
            self.__buffer_cspc = None
        else:
            self.__buffer_cspc += data_cspc

        if data_dc is None:
            self.__buffer_dc = None
        else:
            self.__buffer_dc += data_dc

        self.__profIndex += 1

        return

    def pushData(self):
        """
        Return the sum of the last profiles and the profiles used in the sum.

        Affected:

        self.__profileIndex

        """

        data_spc = self.__buffer_spc
        data_cspc = self.__buffer_cspc
        data_dc = self.__buffer_dc
        n = self.__profIndex

        self.__buffer_spc = 0
        self.__buffer_cspc = 0
        self.__buffer_dc = 0
        self.__profIndex = 0

        return data_spc, data_cspc, data_dc, n

    def byProfiles(self, *args):

        self.__dataReady = False
        avgdata_spc = None
        avgdata_cspc = None
        avgdata_dc = None

        self.putData(*args)

        if self.__profIndex == self.n:

            avgdata_spc, avgdata_cspc, avgdata_dc, n = self.pushData()
            self.n = n
            self.__dataReady = True

        return avgdata_spc, avgdata_cspc, avgdata_dc

    def byTime(self, datatime, *args):

        self.__dataReady = False
        avgdata_spc = None
        avgdata_cspc = None
        avgdata_dc = None

        self.putData(*args)

        if (datatime - self.__initime) >= self.__integrationtime:
            avgdata_spc, avgdata_cspc, avgdata_dc, n = self.pushData()
            self.n = n
            self.__dataReady = True

        return avgdata_spc, avgdata_cspc, avgdata_dc

    def integrate(self, datatime, *args):

        if self.__profIndex == 0:
            self.__initime = datatime

        if self.__byTime:
            avgdata_spc, avgdata_cspc, avgdata_dc = self.byTime(
                datatime, *args)
        else:
            avgdata_spc, avgdata_cspc, avgdata_dc = self.byProfiles(*args)

        if not self.__dataReady:
            return None, None, None, None

        return self.__initime, avgdata_spc, avgdata_cspc, avgdata_dc

    def run(self, dataOut, n=None, timeInterval=None, overlapping=False):
        if n == 1:
            return dataOut
        
        dataOut.flagNoData = True

        if not self.isConfig:
            self.setup(n, timeInterval, overlapping)
            self.isConfig = True

        avgdatatime, avgdata_spc, avgdata_cspc, avgdata_dc = self.integrate(dataOut.utctime,
                                                                            dataOut.data_spc,
                                                                            dataOut.data_cspc,
                                                                            dataOut.data_dc)

        if self.__dataReady:

            dataOut.data_spc = avgdata_spc
            dataOut.data_cspc = avgdata_cspc
            dataOut.data_dc = avgdata_dc            
            dataOut.nIncohInt *= self.n
            dataOut.utctime = avgdatatime
            dataOut.flagNoData = False

        return dataOut

class dopplerFlip(Operation):
       
    def run(self, dataOut):
        # arreglo 1: (num_chan, num_profiles, num_heights)
        self.dataOut = dataOut 
        # JULIA-oblicua, indice 2
        # arreglo 2: (num_profiles, num_heights)
        jspectra = self.dataOut.data_spc[2]
        jspectra_tmp = numpy.zeros(jspectra.shape)
        num_profiles = jspectra.shape[0]
        freq_dc = int(num_profiles / 2)
        # Flip con for
        for j in range(num_profiles):
            jspectra_tmp[num_profiles-j-1]= jspectra[j]
        # Intercambio perfil de DC con perfil inmediato anterior
        jspectra_tmp[freq_dc-1]= jspectra[freq_dc-1]
        jspectra_tmp[freq_dc]= jspectra[freq_dc]
        # canal modificado es re-escrito en el arreglo de canales
        self.dataOut.data_spc[2] = jspectra_tmp

        return self.dataOut