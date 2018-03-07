import numpy
import math
from scipy import optimize, interpolate, signal, stats, ndimage
import scipy
import re
import datetime
import copy
import sys
import importlib
import itertools
from multiprocessing import Pool, TimeoutError 
from multiprocessing.pool import ThreadPool
import copy_reg
import cPickle
import types
from functools import partial
import time
#from sklearn.cluster import KMeans 

import matplotlib.pyplot as plt

from scipy.optimize import fmin_l_bfgs_b #optimize with bounds on state papameters
from jroproc_base import ProcessingUnit, Operation
from schainpy.model.data.jrodata import Parameters, hildebrand_sekhon
from scipy import asarray as ar,exp
from scipy.optimize import curve_fit

import warnings
from numpy import NaN
from scipy.optimize.optimize import OptimizeWarning
from IPython.parallel.controller.scheduler import numpy
warnings.filterwarnings('ignore')


SPEED_OF_LIGHT = 299792458


'''solving pickling issue'''

def _pickle_method(method):
    func_name = method.im_func.__name__
    obj = method.im_self
    cls = method.im_class
    return _unpickle_method, (func_name, obj, cls)

def _unpickle_method(func_name, obj, cls):
    for cls in cls.mro():
        try:
            func = cls.__dict__[func_name]
        except KeyError:
            pass
        else:
            break
    return func.__get__(obj, cls)

class ParametersProc(ProcessingUnit):
    
    nSeconds = None

    def __init__(self):
        ProcessingUnit.__init__(self)
        
#         self.objectDict = {}
        self.buffer = None
        self.firstdatatime = None
        self.profIndex = 0
        self.dataOut = Parameters()
        
    def __updateObjFromInput(self):
        
        self.dataOut.inputUnit = self.dataIn.type
        
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
#         self.dataOut.utctime = self.firstdatatime
        self.dataOut.utctime = self.dataIn.utctime
        self.dataOut.flagDecodeData = self.dataIn.flagDecodeData #asumo q la data esta decodificada
        self.dataOut.flagDeflipData = self.dataIn.flagDeflipData #asumo q la data esta sin flip
        self.dataOut.nCohInt = self.dataIn.nCohInt
#        self.dataOut.nIncohInt = 1
        self.dataOut.ippSeconds = self.dataIn.ippSeconds
#        self.dataOut.windowOfFilter = self.dataIn.windowOfFilter
        self.dataOut.timeInterval1 = self.dataIn.timeInterval
        self.dataOut.heightList = self.dataIn.getHeiRange()   
        self.dataOut.frequency = self.dataIn.frequency
        self.dataOut.noise = self.dataIn.noise
        
        
        
    def run(self):
        
        #----------------------    Voltage Data    ---------------------------
        
        if self.dataIn.type == "Voltage":

            self.__updateObjFromInput()
            self.dataOut.data_pre = self.dataIn.data.copy()
            self.dataOut.flagNoData = False
            self.dataOut.utctimeInit = self.dataIn.utctime
            self.dataOut.paramInterval = self.dataIn.nProfiles*self.dataIn.nCohInt*self.dataIn.ippSeconds  
            return
        
        #----------------------    Spectra Data    ---------------------------
        
        if self.dataIn.type == "Spectra":

            self.dataOut.data_pre = (self.dataIn.data_spc  ,  self.dataIn.data_cspc)
            print 'self.dataIn.data_spc', self.dataIn.data_spc.shape
            self.dataOut.abscissaList = self.dataIn.getVelRange(1)
            self.dataOut.spc_noise = self.dataIn.getNoise()
            self.dataOut.spc_range = numpy.asanyarray((self.dataIn.getFreqRange(1) , self.dataIn.getAcfRange(1) , self.dataIn.getVelRange(1) ))
            
            self.dataOut.normFactor = self.dataIn.normFactor
            #self.dataOut.outputInterval = self.dataIn.outputInterval
            self.dataOut.groupList = self.dataIn.pairsList
            self.dataOut.flagNoData = False
            #print 'datain chandist ',self.dataIn.ChanDist
            if hasattr(self.dataIn, 'ChanDist'): #Distances of receiver channels
                self.dataOut.ChanDist = self.dataIn.ChanDist
            else: self.dataOut.ChanDist = None
                
            print 'datain chandist ',self.dataOut.ChanDist
            
            #if hasattr(self.dataIn, 'VelRange'): #Velocities range
            #    self.dataOut.VelRange = self.dataIn.VelRange
            #else: self.dataOut.VelRange = None
            
            if hasattr(self.dataIn, 'RadarConst'): #Radar Constant
                self.dataOut.RadarConst = self.dataIn.RadarConst
                
            if hasattr(self.dataIn, 'NPW'): #NPW
                self.dataOut.NPW = self.dataIn.NPW
                
            if hasattr(self.dataIn, 'COFA'): #COFA
                self.dataOut.COFA = self.dataIn.COFA
                
                
                
        #----------------------    Correlation Data    ---------------------------
        
        if self.dataIn.type == "Correlation":
            acf_ind, ccf_ind, acf_pairs, ccf_pairs, data_acf, data_ccf = self.dataIn.splitFunctions()
            
            self.dataOut.data_pre = (self.dataIn.data_cf[acf_ind,:], self.dataIn.data_cf[ccf_ind,:,:])
            self.dataOut.normFactor = (self.dataIn.normFactor[acf_ind,:], self.dataIn.normFactor[ccf_ind,:])
            self.dataOut.groupList = (acf_pairs, ccf_pairs)
            
            self.dataOut.abscissaList = self.dataIn.lagRange
            self.dataOut.noise = self.dataIn.noise
            self.dataOut.data_SNR = self.dataIn.SNR
            self.dataOut.flagNoData = False
            self.dataOut.nAvg = self.dataIn.nAvg
        
        #----------------------    Parameters Data    ---------------------------
        
        if self.dataIn.type == "Parameters":
            self.dataOut.copy(self.dataIn)
            self.dataOut.flagNoData = False
            
            return True
            
        self.__updateObjFromInput()
        self.dataOut.utctimeInit = self.dataIn.utctime
        self.dataOut.paramInterval = self.dataIn.timeInterval
        
        return


def target(tups):
    
    obj, args = tups
    #print 'TARGETTT', obj, args
    return obj.FitGau(args)
    
    
class SpectralFilters(Operation):
    
    '''This class allows the Rainfall / Wind Selection for CLAIRE RADAR
    
        LimitR :    It is the limit in m/s of Rainfall
        LimitW :    It is the limit in m/s for Winds
        
        Input:
        
        self.dataOut.data_pre :        SPC and CSPC
        self.dataOut.spc_range :       To select wind and rainfall velocities
        
        Affected:
        
        self.dataOut.data_pre :        It is used for the new SPC and CSPC ranges of wind
        self.dataOut.spcparam_range :  Used in SpcParamPlot 
        self.dataOut.SPCparam :        Used in PrecipitationProc
        
    
    '''
    
    def __init__(self, **kwargs):
        Operation.__init__(self, **kwargs)
        self.i=0
        
    def run(self, dataOut, Rain_Velocity_Limit=1.5, Wind_Velocity_Limit=2.5):    
        
        #Limite de vientos 
        LimitR = Rain_Velocity_Limit
        LimitW = Wind_Velocity_Limit
        
        self.spc = dataOut.data_pre[0].copy()
        self.cspc = dataOut.data_pre[1].copy()
        
        self.Num_Hei = self.spc.shape[2]
        self.Num_Bin = self.spc.shape[1]
        self.Num_Chn = self.spc.shape[0]
        
        VelRange = dataOut.spc_range[2]
        TimeRange = dataOut.spc_range[1]
        FrecRange = dataOut.spc_range[0]
        
        Vmax= 2*numpy.max(dataOut.spc_range[2])
        Tmax= 2*numpy.max(dataOut.spc_range[1])
        Fmax= 2*numpy.max(dataOut.spc_range[0])
        
        Breaker1R=VelRange[numpy.abs(VelRange-(-LimitR)).argmin()]
        Breaker1R=numpy.where(VelRange == Breaker1R)
        
        Breaker1W=VelRange[numpy.abs(VelRange-(-LimitW)).argmin()]
        Breaker1W=numpy.where(VelRange == Breaker1W)
        
        Breaker2W=VelRange[numpy.abs(VelRange-(LimitW)).argmin()]
        Breaker2W=numpy.where(VelRange == Breaker2W)
        
        
        '''Reacomodando SPCrange'''
        
        VelRange=numpy.roll(VelRange,-Breaker1R[0],axis=0)
        
        VelRange[-int(Breaker1R[0]):]+= Vmax
        
        FrecRange=numpy.roll(FrecRange,-Breaker1R[0],axis=0)
        
        FrecRange[-int(Breaker1R[0]):]+= Fmax
        
        TimeRange=numpy.roll(TimeRange,-Breaker1R[0],axis=0)
        
        TimeRange[-int(Breaker1R[0]):]+= Tmax
        
        ''' ------------------ '''
        
        Breaker2R=VelRange[numpy.abs(VelRange-(LimitR)).argmin()]
        Breaker2R=numpy.where(VelRange == Breaker2R)
        
        
        
        
        SPCroll = numpy.roll(self.spc,-Breaker1R[0],axis=1)
        
        SPCcut = SPCroll.copy()
        for i in range(self.Num_Chn):
            SPCcut[i,0:int(Breaker2R[0]),:] = dataOut.noise[i]
            
            self.spc[i, 0:int(Breaker1W[0]) ,:] = dataOut.noise[i]
            self.spc[i, int(Breaker2W[0]):self.Num_Bin ,:] = dataOut.noise[i]
            
            self.cspc[i, 0:int(Breaker1W[0]) ,:] = dataOut.noise[i]
            self.cspc[i, int(Breaker2W[0]):self.Num_Bin ,:] = dataOut.noise[i]
            
        
        SPC_ch1 = SPCroll
        
        SPC_ch2 = SPCcut
        
        SPCparam = (SPC_ch1, SPC_ch2, self.spc)
        dataOut.SPCparam = numpy.asarray(SPCparam) 
        
        dataOut.data_pre= (self.spc  ,  self.cspc)
        
        #dataOut.data_preParam = (self.spc  ,  self.cspc)
        
        dataOut.spcparam_range=numpy.zeros([self.Num_Chn,self.Num_Bin+1])
        
        dataOut.spcparam_range[2]=VelRange
        dataOut.spcparam_range[1]=TimeRange
        dataOut.spcparam_range[0]=FrecRange
        

        
        
class GaussianFit(Operation):
    
    '''
        Function that fit of one and two generalized gaussians (gg) based 
        on the PSD shape across an "power band" identified from a cumsum of 
        the measured spectrum - noise.
        
        Input:
            self.dataOut.data_pre    :    SelfSpectra
            
        Output:
            self.dataOut.SPCparam :    SPC_ch1, SPC_ch2
    
    '''
    def __init__(self, **kwargs):
        Operation.__init__(self, **kwargs)
        self.i=0
        
    
    def run(self, dataOut, num_intg=7, pnoise=1., SNRlimit=-9): #num_intg: Incoherent integrations, pnoise: Noise, vel_arr: range of velocities, similar to the ftt points
        """This routine will find a couple of generalized Gaussians to a power spectrum
        input: spc
        output:
            Amplitude0,shift0,width0,p0,Amplitude1,shift1,width1,p1,noise
        """
        
        self.spc = dataOut.data_pre[0].copy()
        
        
        print 'SelfSpectra Shape', numpy.asarray(self.spc).shape
        
        
        #plt.figure(50)
        #plt.subplot(121)
        #plt.plot(self.spc,'k',label='spc(66)')
        #plt.plot(xFrec,ySamples[1],'g',label='Ch1')
        #plt.plot(xFrec,ySamples[2],'r',label='Ch2')
        #plt.plot(xFrec,FitGauss,'yo:',label='fit')
        #plt.legend()
        #plt.title('DATOS A ALTURA DE 7500 METROS')
        #plt.show()
        
        self.Num_Hei = self.spc.shape[2]
        #self.Num_Bin = len(self.spc)
        self.Num_Bin = self.spc.shape[1]
        self.Num_Chn = self.spc.shape[0]
        Vrange = dataOut.abscissaList
        
        GauSPC = numpy.empty([self.Num_Chn,self.Num_Bin,self.Num_Hei])
        SPC_ch1 = numpy.empty([self.Num_Bin,self.Num_Hei])
        SPC_ch2 = numpy.empty([self.Num_Bin,self.Num_Hei])
        SPC_ch1[:] = numpy.NaN
        SPC_ch2[:] = numpy.NaN

        
        start_time = time.time()
        
        noise_ = dataOut.spc_noise[0].copy()
        
        
        pool = Pool(processes=self.Num_Chn)     
        args = [(Vrange, Ch, pnoise, noise_, num_intg, SNRlimit) for Ch in range(self.Num_Chn)]
        objs = [self for __ in range(self.Num_Chn)]          
        attrs = zip(objs, args)          
        gauSPC = pool.map(target, attrs)
        dataOut.SPCparam = numpy.asarray(SPCparam)

 
        
        print '========================================================'
        print 'total_time: ', time.time()-start_time
        
                # re-normalizing spc and noise
                # This part differs from gg1
        
        
                
        ''' Parameters:
            1. Amplitude
            2. Shift
            3. Width
            4. Power
               '''
        
        
        ###############################################################################    
    def FitGau(self, X):
        
        Vrange, ch, pnoise, noise_, num_intg, SNRlimit = X
        #print 'VARSSSS', ch, pnoise, noise, num_intg
        
        #print 'HEIGHTS', self.Num_Hei
        
        SPCparam = []
        SPC_ch1 = numpy.empty([self.Num_Bin,self.Num_Hei])
        SPC_ch2 = numpy.empty([self.Num_Bin,self.Num_Hei])
        SPC_ch1[:] = 0#numpy.NaN
        SPC_ch2[:] = 0#numpy.NaN
        
        
        
        for ht in range(self.Num_Hei):
            #print (numpy.asarray(self.spc).shape)
            
            #print 'TTTTT', ch , ht
            #print self.spc.shape
            
            
            spc =  numpy.asarray(self.spc)[ch,:,ht]
            
            #############################################
            # normalizing spc and noise
            # This part differs from gg1
            spc_norm_max = max(spc)
            #spc = spc / spc_norm_max
            pnoise = pnoise #/ spc_norm_max
            #############################################
            
            fatspectra=1.0
            
            wnoise = noise_ #/ spc_norm_max
                #wnoise,stdv,i_max,index =enoise(spc,num_intg) #noise estimate using Hildebrand Sekhon, only wnoise is used
                #if wnoise>1.1*pnoise: # to be tested later 
                #    wnoise=pnoise
            noisebl=wnoise*0.9; 
            noisebh=wnoise*1.1
            spc=spc-wnoise
            # print 'wnoise', noise_[0], spc_norm_max, wnoise    
            minx=numpy.argmin(spc)
            #spcs=spc.copy() 
            spcs=numpy.roll(spc,-minx)
            cum=numpy.cumsum(spcs)
            tot_noise=wnoise * self.Num_Bin  #64;
            #print 'spc' , spcs[5:8] , 'tot_noise', tot_noise
            #tot_signal=sum(cum[-5:])/5.; ''' How does this line work? ''' 
            #snr=tot_signal/tot_noise
            #snr=cum[-1]/tot_noise
            snr = sum(spcs)/tot_noise
            snrdB=10.*numpy.log10(snr)
            
            if snrdB < SNRlimit :
                snr = numpy.NaN
                SPC_ch1[:,ht] = 0#numpy.NaN
                SPC_ch1[:,ht] = 0#numpy.NaN
                SPCparam = (SPC_ch1,SPC_ch2)
                continue
            #print 'snr',snrdB #, sum(spcs) , tot_noise
            
            
            
            #if snrdB<-18 or numpy.isnan(snrdB) or num_intg<4:
            #    return [None,]*4,[None,]*4,None,snrdB,None,None,[None,]*5,[None,]*9,None
            
            cummax=max(cum); 
            epsi=0.08*fatspectra # cumsum to narrow down the energy region
            cumlo=cummax*epsi; 
            cumhi=cummax*(1-epsi)
            powerindex=numpy.array(numpy.where(numpy.logical_and(cum>cumlo, cum<cumhi))[0])
            
            
            if len(powerindex) < 1:# case for powerindex 0
                continue
            powerlo=powerindex[0]
            powerhi=powerindex[-1]
            powerwidth=powerhi-powerlo
            
            firstpeak=powerlo+powerwidth/10.# first gaussian energy location
            secondpeak=powerhi-powerwidth/10.#second gaussian energy location
            midpeak=(firstpeak+secondpeak)/2.
            firstamp=spcs[int(firstpeak)]
            secondamp=spcs[int(secondpeak)]
            midamp=spcs[int(midpeak)]
            
            x=numpy.arange( self.Num_Bin )
            y_data=spc+wnoise
            
            '''    single Gaussian    '''
            shift0=numpy.mod(midpeak+minx, self.Num_Bin )
            width0=powerwidth/4.#Initialization entire power of spectrum divided by 4
            power0=2.
            amplitude0=midamp
            state0=[shift0,width0,amplitude0,power0,wnoise]
            bnds=(( 0,(self.Num_Bin-1) ),(1,powerwidth),(0,None),(0.5,3.),(noisebl,noisebh))
            lsq1=fmin_l_bfgs_b(self.misfit1,state0,args=(y_data,x,num_intg),bounds=bnds,approx_grad=True)
            
            chiSq1=lsq1[1]; 

            
            if fatspectra<1.0 and powerwidth<4:
                    choice=0
                    Amplitude0=lsq1[0][2]
                    shift0=lsq1[0][0]
                    width0=lsq1[0][1]
                    p0=lsq1[0][3]
                    Amplitude1=0.
                    shift1=0.
                    width1=0.
                    p1=0.
                    noise=lsq1[0][4]
                    #return (numpy.array([shift0,width0,Amplitude0,p0]),
                    #        numpy.array([shift1,width1,Amplitude1,p1]),noise,snrdB,chiSq1,6.,sigmas1,[None,]*9,choice)
        
            '''    two gaussians    '''
            #shift0=numpy.mod(firstpeak+minx,64); shift1=numpy.mod(secondpeak+minx,64)
            shift0=numpy.mod(firstpeak+minx, self.Num_Bin ); 
            shift1=numpy.mod(secondpeak+minx, self.Num_Bin )
            width0=powerwidth/6.; 
            width1=width0
            power0=2.; 
            power1=power0
            amplitude0=firstamp; 
            amplitude1=secondamp
            state0=[shift0,width0,amplitude0,power0,shift1,width1,amplitude1,power1,wnoise]
            #bnds=((0,63),(1,powerwidth/2.),(0,None),(0.5,3.),(0,63),(1,powerwidth/2.),(0,None),(0.5,3.),(noisebl,noisebh))
            bnds=(( 0,(self.Num_Bin-1) ),(1,powerwidth/2.),(0,None),(0.5,3.),( 0,(self.Num_Bin-1)),(1,powerwidth/2.),(0,None),(0.5,3.),(noisebl,noisebh))
            #bnds=(( 0,(self.Num_Bin-1) ),(1,powerwidth/2.),(0,None),(0.5,3.),( 0,(self.Num_Bin-1)),(1,powerwidth/2.),(0,None),(0.5,3.),(0.1,0.5))
            
            lsq2 = fmin_l_bfgs_b( self.misfit2 , state0 , args=(y_data,x,num_intg) , bounds=bnds , approx_grad=True )
            
            
            chiSq2=lsq2[1]; 
            
            
            
            oneG=(chiSq1<5 and chiSq1/chiSq2<2.0) and (abs(lsq2[0][0]-lsq2[0][4])<(lsq2[0][1]+lsq2[0][5])/3. or abs(lsq2[0][0]-lsq2[0][4])<10)
            
            if snrdB>-12: # when SNR is strong pick the peak with least shift (LOS velocity) error
                if oneG:
                    choice=0
                else:
                    w1=lsq2[0][1]; w2=lsq2[0][5]
                    a1=lsq2[0][2]; a2=lsq2[0][6]
                    p1=lsq2[0][3]; p2=lsq2[0][7]
                    s1=(2**(1+1./p1))*scipy.special.gamma(1./p1)/p1; 
                    s2=(2**(1+1./p2))*scipy.special.gamma(1./p2)/p2;
                    gp1=a1*w1*s1; gp2=a2*w2*s2 # power content of each ggaussian with proper p scaling
                    
                    if gp1>gp2:
                        if a1>0.7*a2:
                            choice=1
                        else:
                            choice=2
                    elif gp2>gp1:
                        if a2>0.7*a1:
                            choice=2
                        else:
                            choice=1
                    else:
                        choice=numpy.argmax([a1,a2])+1
                        #else:
                        #choice=argmin([std2a,std2b])+1
                        
            else: # with low SNR go to the most energetic peak
                choice=numpy.argmax([lsq1[0][2]*lsq1[0][1],lsq2[0][2]*lsq2[0][1],lsq2[0][6]*lsq2[0][5]])
            
            
            shift0=lsq2[0][0]; 
            vel0=Vrange[0] + shift0*(Vrange[1]-Vrange[0])
            shift1=lsq2[0][4]; 
            vel1=Vrange[0] + shift1*(Vrange[1]-Vrange[0])
            
            max_vel = 1.0
            
            #first peak will be 0, second peak will be 1
            if vel0 > -1.0 and vel0 < max_vel : #first peak is in the correct range
                shift0=lsq2[0][0]
                width0=lsq2[0][1]
                Amplitude0=lsq2[0][2]
                p0=lsq2[0][3]
                
                shift1=lsq2[0][4]
                width1=lsq2[0][5]
                Amplitude1=lsq2[0][6]
                p1=lsq2[0][7]
                noise=lsq2[0][8]                
            else:
                shift1=lsq2[0][0]
                width1=lsq2[0][1]
                Amplitude1=lsq2[0][2]
                p1=lsq2[0][3]
                
                shift0=lsq2[0][4]
                width0=lsq2[0][5]
                Amplitude0=lsq2[0][6]
                p0=lsq2[0][7]    
                noise=lsq2[0][8]                            
                
            if Amplitude0<0.05: # in case the peak is noise
                shift0,width0,Amplitude0,p0 = [0,0,0,0]#4*[numpy.NaN]  
            if Amplitude1<0.05:
                shift1,width1,Amplitude1,p1 = [0,0,0,0]#4*[numpy.NaN]  
            
            
#             if choice==0: # pick the single gaussian fit
#                 Amplitude0=lsq1[0][2]
#                 shift0=lsq1[0][0]
#                 width0=lsq1[0][1]
#                 p0=lsq1[0][3]
#                 Amplitude1=0.
#                 shift1=0.
#                 width1=0.
#                 p1=0.
#                 noise=lsq1[0][4]
#             elif choice==1: # take the first one of the 2 gaussians fitted
#                 Amplitude0 = lsq2[0][2]
#                 shift0     = lsq2[0][0]
#                 width0     = lsq2[0][1]
#                 p0         = lsq2[0][3]
#                 Amplitude1 = lsq2[0][6]     # This is 0 in gg1
#                 shift1     = lsq2[0][4]     # This is 0 in gg1
#                 width1     = lsq2[0][5]     # This is 0 in gg1
#                 p1         = lsq2[0][7]     # This is 0 in gg1
#                 noise      = lsq2[0][8]
#             else: # the second one
#                 Amplitude0 = lsq2[0][6]
#                 shift0     = lsq2[0][4]
#                 width0     = lsq2[0][5]
#                 p0         = lsq2[0][7]
#                 Amplitude1 = lsq2[0][2]     # This is 0 in gg1
#                 shift1     = lsq2[0][0]     # This is 0 in gg1
#                 width1     = lsq2[0][1]     # This is 0 in gg1
#                 p1         = lsq2[0][3]     # This is 0 in gg1
#                 noise      = lsq2[0][8]
            
            #print len(noise + Amplitude0*numpy.exp(-0.5*(abs(x-shift0))/width0)**p0)
            SPC_ch1[:,ht] = noise + Amplitude0*numpy.exp(-0.5*(abs(x-shift0))/width0)**p0
            SPC_ch2[:,ht] = noise + Amplitude1*numpy.exp(-0.5*(abs(x-shift1))/width1)**p1
            #print 'SPC_ch1.shape',SPC_ch1.shape
            #print 'SPC_ch2.shape',SPC_ch2.shape
            #dataOut.data_param = SPC_ch1
            SPCparam = (SPC_ch1,SPC_ch2)
            #GauSPC[1] = SPC_ch2 
            
#         print 'shift0', shift0
#         print 'Amplitude0', Amplitude0
#         print 'width0', width0
#         print 'p0', p0
#         print '========================'
#         print 'shift1', shift1
#         print 'Amplitude1', Amplitude1
#         print 'width1', width1
#         print 'p1', p1
#         print 'noise', noise
#         print 's_noise', wnoise
        
        return GauSPC
    
    def y_model1(self,x,state):
        shift0,width0,amplitude0,power0,noise=state
        model0=amplitude0*numpy.exp(-0.5*abs((x-shift0)/width0)**power0)
        
        model0u=amplitude0*numpy.exp(-0.5*abs((x-shift0- self.Num_Bin )/width0)**power0)
        
        model0d=amplitude0*numpy.exp(-0.5*abs((x-shift0+ self.Num_Bin )/width0)**power0)
        return model0+model0u+model0d+noise
    
    def y_model2(self,x,state): #Equation for two generalized Gaussians with Nyquist 
        shift0,width0,amplitude0,power0,shift1,width1,amplitude1,power1,noise=state
        model0=amplitude0*numpy.exp(-0.5*abs((x-shift0)/width0)**power0)
        
        model0u=amplitude0*numpy.exp(-0.5*abs((x-shift0- self.Num_Bin )/width0)**power0)
        
        model0d=amplitude0*numpy.exp(-0.5*abs((x-shift0+ self.Num_Bin )/width0)**power0)
        model1=amplitude1*numpy.exp(-0.5*abs((x-shift1)/width1)**power1)
        
        model1u=amplitude1*numpy.exp(-0.5*abs((x-shift1- self.Num_Bin )/width1)**power1)
        
        model1d=amplitude1*numpy.exp(-0.5*abs((x-shift1+ self.Num_Bin )/width1)**power1)
        return model0+model0u+model0d+model1+model1u+model1d+noise
    
    def misfit1(self,state,y_data,x,num_intg): # This function compares how close real data is with the model data, the close it is, the better it is. 

        return num_intg*sum((numpy.log(y_data)-numpy.log(self.y_model1(x,state)))**2)#/(64-5.) # /(64-5.) can be commented
    
    def misfit2(self,state,y_data,x,num_intg):
        return num_intg*sum((numpy.log(y_data)-numpy.log(self.y_model2(x,state)))**2)#/(64-9.)
    
    

class PrecipitationProc(Operation):
    
    '''
         Operator that estimates Reflectivity factor (Z), and estimates rainfall Rate (R)
         
         Input:    
            self.dataOut.data_pre    :    SelfSpectra
            
         Output:    
        
            self.dataOut.data_output :    Reflectivity factor, rainfall Rate 
        
        
         Parameters affected:    
    '''
    def gaus(self,xSamples,Amp,Mu,Sigma):
        return ( Amp / ((2*numpy.pi)**0.5 * Sigma) ) * numpy.exp( -( xSamples - Mu )**2 / ( 2 * (Sigma**2) ))
    
    
        
    def Moments(self, ySamples, xSamples):
        Pot = numpy.nansum( ySamples )                              # Potencia, momento 0
        yNorm = ySamples / Pot
        
        Vr = numpy.nansum( yNorm * xSamples )                       # Velocidad radial, mu, corrimiento doppler, primer momento
        Sigma2 = abs(numpy.nansum( yNorm * ( xSamples - Vr )**2 ))  # Segundo Momento 
        Desv = Sigma2**0.5                                          # Desv. Estandar, Ancho espectral
        
        return numpy.array([Pot, Vr, Desv])        
    
    def run(self, dataOut, radar=None, Pt=5000, Gt=295.1209, Gr=70.7945, Lambda=0.6741, aL=2.5118, 
            tauW=4e-06, ThetaT=0.1656317, ThetaR=0.36774087, Km = 0.93, Altitude=3350):
        
        
        Velrange = dataOut.spc_range[2]
        FrecRange = dataOut.spc_range[0]
        
        dV= Velrange[1]-Velrange[0]
        dF= FrecRange[1]-FrecRange[0]
        
        if radar == "MIRA35C" :
            
            self.spc = dataOut.data_pre[0].copy()
            self.Num_Hei = self.spc.shape[2]
            self.Num_Bin = self.spc.shape[1]
            self.Num_Chn = self.spc.shape[0]
            Ze = self.dBZeMODE2(dataOut)
            
        else:
            
            self.spc = dataOut.SPCparam[1] #dataOut.data_pre[0].copy() #
            self.Num_Hei = self.spc.shape[2]
            self.Num_Bin = self.spc.shape[1]
            self.Num_Chn = self.spc.shape[0]
            print '==================== SPC SHAPE',numpy.shape(self.spc)
            
            
            ''' Se obtiene la constante del RADAR '''
            
            self.Pt = Pt
            self.Gt = Gt
            self.Gr = Gr
            self.Lambda = Lambda
            self.aL = aL
            self.tauW = tauW
            self.ThetaT = ThetaT
            self.ThetaR = ThetaR
            
            Numerator = ( (4*numpy.pi)**3 * aL**2 * 16 * numpy.log(2) )
            Denominator = ( Pt * Gt * Gr * Lambda**2 * SPEED_OF_LIGHT * tauW * numpy.pi * ThetaT * ThetaR)
            RadarConstant = 4.1396e+08# Numerator / Denominator
            print '***'
            print '*** RadarConstant' , RadarConstant, '****'
            print '***'
            ''' =============================  '''
            
            SPCmean = numpy.mean(self.spc,0)
            ETAf = numpy.zeros([self.Num_Bin,self.Num_Hei])
            ETAv = numpy.zeros([self.Num_Bin,self.Num_Hei])
            ETAd = numpy.zeros([self.Num_Bin,self.Num_Hei])
            
            Pr = self.spc[0,:,:]
            
            VelMeteoro = numpy.mean(SPCmean,axis=0)
            
            #print '==================== Vel SHAPE',VelMeteoro
            
            D_range = numpy.zeros([self.Num_Bin,self.Num_Hei])
            SIGMA = numpy.zeros([self.Num_Bin,self.Num_Hei])
            N_dist = numpy.zeros([self.Num_Bin,self.Num_Hei])
            D_mean = numpy.zeros(self.Num_Hei)
            del_V = numpy.zeros(self.Num_Hei)
            Z = numpy.zeros(self.Num_Hei)
            Ze = numpy.zeros(self.Num_Hei)
            RR = numpy.zeros(self.Num_Hei)
            
            
            for R in range(self.Num_Hei):
                
                h = R*75 + Altitude #Range from ground to radar pulse altitude
                del_V[R] = 1 + 3.68 * 10**-5 * h + 1.71 * 10**-9 * h**2    #Density change correction for velocity
                
                D_range[:,R] = numpy.log( (9.65 - (Velrange[0:self.Num_Bin] / del_V[R])) / 10.3 ) / -0.6 #Range of Diameter of drops related to velocity
                
                ETAf[:,R] = 1/RadarConstant * Pr[:,R] * (R*0.075)**2 #Reflectivity (ETA)
                
                ETAv[:,R]=ETAf[:,R]*dF/dV
                
                ETAd[:,R]=ETAv[:,R]*6.18*exp(-0.6*D_range[:,R])
                
                SIGMA[:,R] = numpy.pi**5 / Lambda**4 * Km * D_range[:,R]**6     #Equivalent Section of drops (sigma)
                
                N_dist[:,R] = ETAd[:,R] / SIGMA[:,R]    
                
                DMoments = self.Moments(Pr[:,R], D_range[:,R])
                
                try:
                    popt01,pcov = curve_fit(self.gaus, D_range[:,R] , Pr[:,R] , p0=DMoments)
                except: 
                    popt01=numpy.zeros(3)
                    popt01[1]= DMoments[1]
                D_mean[R]=popt01[1]
            
                Z[R] = numpy.nansum( N_dist[:,R] * D_range[:,R]**6 )
                
                RR[R] = 6*10**-4.*numpy.pi * numpy.nansum( D_range[:,R]**3 * N_dist[:,R] * Velrange[0:self.Num_Bin] ) #Rainfall rate
            
                Ze[R] = (numpy.nansum(ETAd[:,R]) * Lambda**4) / (numpy.pi * Km)
            
        
        
        RR2 = (Z/200)**(1/1.6)
        dBRR = 10*numpy.log10(RR)
        dBRR2 = 10*numpy.log10(RR2)
        
        dBZe = 10*numpy.log10(Ze)
        dBZ = 10*numpy.log10(Z)
        
        dataOut.data_output = Z
        dataOut.data_param = numpy.ones([3,self.Num_Hei])
        dataOut.channelList = [0,1,2]
        
        dataOut.data_param[0]=dBZ
        dataOut.data_param[1]=dBZe
        dataOut.data_param[2]=dBRR2
        
        print 'RR SHAPE', dBRR.shape
        #print 'Ze ', dBZe
        print 'Z ', dBZ
        print 'RR ', dBRR
        #print 'RR2 ', dBRR2
        #print 'D_mean', D_mean
        #print 'del_V', del_V
        #print 'D_range',D_range.shape, D_range[:,30] 
        #print 'Velrange', Velrange
        #print 'numpy.nansum( N_dist[:,R]', numpy.nansum( N_dist, axis=0)
        #print 'dataOut.data_param SHAPE', dataOut.data_param.shape
        
        
    def dBZeMODE2(self, dataOut): #    Processing for MIRA35C
        
        NPW = dataOut.NPW
        COFA = dataOut.COFA
        
        SNR = numpy.array([self.spc[0,:,:] / NPW[0]]) #, self.spc[1,:,:] / NPW[1]])
        RadarConst = dataOut.RadarConst
        #frequency = 34.85*10**9
        
        ETA = numpy.zeros(([self.Num_Chn ,self.Num_Hei]))
        data_output = numpy.ones([self.Num_Chn , self.Num_Hei])*numpy.NaN
        
        ETA = numpy.sum(SNR,1)
        print 'ETA' , ETA
        ETA = numpy.where(ETA is not 0. , ETA, numpy.NaN)
        
        Ze = numpy.ones([self.Num_Chn, self.Num_Hei] )
        
        for r in range(self.Num_Hei):
            
            Ze[0,r] =  ( ETA[0,r] ) * COFA[0,r][0] * RadarConst * ((r/5000.)**2)
            #Ze[1,r] =  ( ETA[1,r] ) * COFA[1,r][0] * RadarConst * ((r/5000.)**2)
            
        return Ze
    
#     def GetRadarConstant(self):
#     
#         """ 
#         Constants:
#          
#         Pt:     Transmission Power               dB        5kW                5000
#         Gt:     Transmission Gain                dB        24.7 dB            295.1209
#         Gr:     Reception Gain                   dB        18.5 dB            70.7945
#         Lambda: Wavelenght                       m         0.6741 m           0.6741
#         aL:     Attenuation loses                dB        4dB                2.5118
#         tauW:   Width of transmission pulse      s         4us                4e-6
#         ThetaT: Transmission antenna bean angle  rad       0.1656317 rad      0.1656317
#         ThetaR: Reception antenna beam angle     rad       0.36774087 rad     0.36774087
#          
#         """
#         
#         Numerator = ( (4*numpy.pi)**3 * aL**2 * 16 * numpy.log(2) )
#         Denominator = ( Pt * Gt * Gr * Lambda**2 * SPEED_OF_LIGHT * TauW * numpy.pi * ThetaT * TheraR)
#         RadarConstant =  Numerator / Denominator
#         
#         return RadarConstant
    
    
    
class FullSpectralAnalysis(Operation): 
    
    """
        Function that implements Full Spectral Analisys technique.
        
        Input:    
            self.dataOut.data_pre    :    SelfSpectra and CrossSPectra data
            self.dataOut.groupList   :    Pairlist of channels
            self.dataOut.ChanDist    :    Physical distance between receivers
        
        
        Output:    
        
            self.dataOut.data_output :    Zonal wind, Meridional wind and Vertical wind 
        
        
        Parameters affected:    Winds, height range, SNR
        
    """
    def run(self, dataOut, E01=None, E02=None, E12=None, N01=None, N02=None, N12=None, SNRlimit=7):
        
        self.indice=int(numpy.random.rand()*1000) 
        
        spc = dataOut.data_pre[0].copy()
        cspc = dataOut.data_pre[1]
        
        nChannel = spc.shape[0]
        nProfiles = spc.shape[1]
        nHeights = spc.shape[2]
        
        pairsList = dataOut.groupList
        if dataOut.ChanDist is not None :
            ChanDist = dataOut.ChanDist
        else:
            ChanDist = numpy.array([[E01, N01],[E02,N02],[E12,N12]])
        
        FrecRange = dataOut.spc_range[0]
        
        ySamples=numpy.ones([nChannel,nProfiles])
        phase=numpy.ones([nChannel,nProfiles])
        CSPCSamples=numpy.ones([nChannel,nProfiles],dtype=numpy.complex_)
        coherence=numpy.ones([nChannel,nProfiles])
        PhaseSlope=numpy.ones(nChannel)
        PhaseInter=numpy.ones(nChannel)
        data_SNR=numpy.zeros([nProfiles])
        
        data = dataOut.data_pre
        noise = dataOut.noise
        
        dataOut.data_SNR = (numpy.mean(spc,axis=1)- noise[0]) / noise[0]
        
        
        
        print dataOut.data_SNR.shape
        #FirstMoment = dataOut.moments[0,1,:]#numpy.average(dataOut.data_param[:,1,:],0)
        #SecondMoment = numpy.average(dataOut.moments[:,2,:],0)
        
        #SNRdBMean = []
 
        data_output=numpy.ones([spc.shape[0],spc.shape[2]])*numpy.NaN
        
        velocityX=[]
        velocityY=[]
        velocityV=[]
        PhaseLine=[]
        
        dbSNR = 10*numpy.log10(dataOut.data_SNR)
        dbSNR = numpy.average(dbSNR,0)
        
        for Height in range(nHeights):
            
            [Vzon,Vmer,Vver, GaussCenter, PhaseSlope, FitGaussCSPC]= self.WindEstimation(spc, cspc, pairsList, ChanDist, Height, noise, dataOut.spc_range.copy(), dbSNR[Height], SNRlimit)
            PhaseLine = numpy.append(PhaseLine, PhaseSlope)
            
            if abs(Vzon)<100. and abs(Vzon)> 0.:
                velocityX=numpy.append(velocityX, -Vzon)#Vmag
               
            else:
                #print 'Vzon',Vzon
                velocityX=numpy.append(velocityX, numpy.NaN)
                
            if abs(Vmer)<100. and abs(Vmer) > 0.:
                velocityY=numpy.append(velocityY, -Vmer)#Vang
                
            else:
                #print 'Vmer',Vmer
                velocityY=numpy.append(velocityY, numpy.NaN)
            
            if dbSNR[Height] > SNRlimit:
                velocityV=numpy.append(velocityV, -Vver)#FirstMoment[Height])
            else:
                velocityV=numpy.append(velocityV, numpy.NaN)
                #FirstMoment[Height]= numpy.NaN
#             if SNRdBMean[Height]  <12:
#                 FirstMoment[Height] = numpy.NaN
#                 velocityX[Height] = numpy.NaN
#                 velocityY[Height] = numpy.NaN
        
        
        
        data_output[0] = numpy.array(velocityX)  #self.moving_average(numpy.array(velocityX) , N=1)
        data_output[1] = numpy.array(velocityY)  #self.moving_average(numpy.array(velocityY) , N=1)
        data_output[2] = -velocityV#FirstMoment
   
        print 'FirstMoment', data_output[2]
        #print FirstMoment
#         print 'velocityX',numpy.shape(data_output[0])
#         print 'velocityX',data_output[0]
#         print ' '
#         print 'velocityY',numpy.shape(data_output[1])
#         print 'velocityY',data_output[1]
#         print 'velocityV',data_output[2]
#         print 'PhaseLine',PhaseLine
        #print numpy.array(velocityY)
        #print 'SNR'
        #print 10*numpy.log10(dataOut.data_SNR)
        #print numpy.shape(10*numpy.log10(dataOut.data_SNR))
        print ' '
        
        xFrec=FrecRange[0:spc.shape[1]]
        
        dataOut.data_output=data_output
        
        return
    
    
    def moving_average(self,x, N=2):
        return numpy.convolve(x, numpy.ones((N,))/N)[(N-1):]
    
    def gaus(self,xSamples,Amp,Mu,Sigma):
        return ( Amp / ((2*numpy.pi)**0.5 * Sigma) ) * numpy.exp( -( xSamples - Mu )**2 / ( 2 * (Sigma**2) ))
    
    
        
    def Moments(self, ySamples, xSamples):
        Pot = numpy.nansum( ySamples )                              # Potencia, momento 0
        yNorm = ySamples / Pot
        
        Vr = numpy.nansum( yNorm * xSamples )                       # Velocidad radial, mu, corrimiento doppler, primer momento
        Sigma2 = abs(numpy.nansum( yNorm * ( xSamples - Vr )**2 ))  # Segundo Momento 
        Desv = Sigma2**0.5                                          # Desv. Estandar, Ancho espectral
        
        return numpy.array([Pot, Vr, Desv])
    
    def WindEstimation(self, spc, cspc, pairsList, ChanDist, Height, noise, AbbsisaRange, dbSNR, SNRlimit):
        
#         print ' '
#         print '######################## Height',Height, (1000 + 75*Height), '##############################' 
#         print ' '
        
        ySamples=numpy.ones([spc.shape[0],spc.shape[1]])
        phase=numpy.ones([spc.shape[0],spc.shape[1]])
        CSPCSamples=numpy.ones([spc.shape[0],spc.shape[1]],dtype=numpy.complex_)
        coherence=numpy.ones([spc.shape[0],spc.shape[1]])
        PhaseSlope=numpy.zeros(spc.shape[0])
        PhaseInter=numpy.ones(spc.shape[0])
        xFrec=AbbsisaRange[0][0:spc.shape[1]]
        xVel =AbbsisaRange[2][0:spc.shape[1]]
        Vv=numpy.empty(spc.shape[2])*0
        SPCav = numpy.average(spc, axis=0)-numpy.average(noise) #spc[0]-noise[0]#
        
        SPCmoments = self.Moments(SPCav[:,Height], xVel ) 
        CSPCmoments = []
        cspcNoise = numpy.empty(3)
        
        '''Getting Eij and Nij'''
        
        E01=ChanDist[0][0]
        N01=ChanDist[0][1]
        
        E02=ChanDist[1][0]
        N02=ChanDist[1][1]
        
        E12=ChanDist[2][0]
        N12=ChanDist[2][1]
        
        z = spc.copy()
        z = numpy.where(numpy.isfinite(z), z, numpy.NAN)
        
        for i in range(spc.shape[0]):  
            
            '''****** Line of Data SPC ******'''
            zline=z[i,:,Height].copy() - noise[i]   # Se resta ruido
            
            '''****** SPC is normalized ******'''
            SmoothSPC =self.moving_average(zline.copy(),N=1)     # Se suaviza el ruido
            FactNorm = SmoothSPC/numpy.nansum(SmoothSPC)         # SPC Normalizado y suavizado 
            
            xSamples = xFrec                   # Se toma el rango de frecuncias
            ySamples[i] = FactNorm             # Se toman los valores de SPC normalizado
        
        for i in range(spc.shape[0]):
            
            '''****** Line of Data CSPC ******'''
            cspcLine = ( cspc[i,:,Height].copy())# - noise[i] )     # no! Se resta el ruido
            SmoothCSPC =self.moving_average(cspcLine,N=1)         # Se suaviza el ruido
            cspcNorm = SmoothCSPC/numpy.nansum(SmoothCSPC)        # CSPC normalizado y suavizado
            
            '''****** CSPC is normalized with respect to Briggs and Vincent ******'''
            chan_index0 = pairsList[i][0]
            chan_index1 = pairsList[i][1]
            
            CSPCFactor= numpy.abs(numpy.nansum(ySamples[chan_index0]))**2  *  numpy.abs(numpy.nansum(ySamples[chan_index1]))**2 
            CSPCNorm = cspcNorm / numpy.sqrt(CSPCFactor)
            
            CSPCSamples[i] = CSPCNorm
            
            coherence[i] = numpy.abs(CSPCSamples[i]) / numpy.sqrt(CSPCFactor)
            
            #coherence[i]= self.moving_average(coherence[i],N=1)
            
            phase[i] = self.moving_average( numpy.arctan2(CSPCSamples[i].imag, CSPCSamples[i].real),N=1)#*180/numpy.pi
        
        CSPCmoments = numpy.vstack([self.Moments(numpy.abs(CSPCSamples[0]), xSamples),
                                    self.Moments(numpy.abs(CSPCSamples[1]), xSamples),
                                    self.Moments(numpy.abs(CSPCSamples[2]), xSamples)]) 
        
        #print '##### SUMA de SPC #####', len(ySamples)
        #print numpy.sum(ySamples[0])
        #print '##### SUMA de CSPC #####', len(coherence)
        #print numpy.sum(numpy.abs(CSPCNorm))
        #print numpy.sum(coherence[0])
#         print 'len',len(xSamples)
#         print 'CSPCmoments', numpy.shape(CSPCmoments)
#         print CSPCmoments
#         print '#######################' 
        
        popt=[1e-10,1e-10,1e-10]
        popt01, popt02, popt12 = [1e-10,1e-10,1e-10], [1e-10,1e-10,1e-10] ,[1e-10,1e-10,1e-10]  
        FitGauss01, FitGauss02, FitGauss12 = numpy.empty(len(xSamples))*0, numpy.empty(len(xSamples))*0, numpy.empty(len(xSamples))*0
        
        CSPCMask01 = numpy.abs(CSPCSamples[0])
        CSPCMask02 = numpy.abs(CSPCSamples[1])
        CSPCMask12 = numpy.abs(CSPCSamples[2])
        
        mask01 = ~numpy.isnan(CSPCMask01)
        mask02 = ~numpy.isnan(CSPCMask02)
        mask12 = ~numpy.isnan(CSPCMask12)
        
        #mask = ~numpy.isnan(CSPCMask01)
        CSPCMask01 = CSPCMask01[mask01]
        CSPCMask02 = CSPCMask02[mask02]
        CSPCMask12 = CSPCMask12[mask12]
        #CSPCMask01 = numpy.ma.masked_invalid(CSPCMask01)
        
        
        
        '''***Fit Gauss CSPC01***'''
        if dbSNR > SNRlimit:
            try:
                popt01,pcov = curve_fit(self.gaus,xSamples[mask01],numpy.abs(CSPCMask01),p0=CSPCmoments[0])
                popt02,pcov = curve_fit(self.gaus,xSamples[mask02],numpy.abs(CSPCMask02),p0=CSPCmoments[1])
                popt12,pcov = curve_fit(self.gaus,xSamples[mask12],numpy.abs(CSPCMask12),p0=CSPCmoments[2])
                FitGauss01 = self.gaus(xSamples,*popt01)
                FitGauss02 = self.gaus(xSamples,*popt02)
                FitGauss12 = self.gaus(xSamples,*popt12)
            except:
                FitGauss01=numpy.ones(len(xSamples))*numpy.mean(numpy.abs(CSPCSamples[0]))
                FitGauss02=numpy.ones(len(xSamples))*numpy.mean(numpy.abs(CSPCSamples[1]))
                FitGauss12=numpy.ones(len(xSamples))*numpy.mean(numpy.abs(CSPCSamples[2]))
        
        
        CSPCopt = numpy.vstack([popt01,popt02,popt12])
        
        '''****** Getting fij width ******'''
        
        yMean = numpy.average(ySamples, axis=0)  # ySamples[0]   
        
        '''******* Getting fitting Gaussian *******'''
        meanGauss = sum(xSamples*yMean) / len(xSamples)              # Mu, velocidad radial (frecuencia) 
        sigma2 = sum(yMean*(xSamples-meanGauss)**2) / len(xSamples)  # Varianza, Ancho espectral (frecuencia) 
        
        yMoments = self.Moments(yMean, xSamples)
        
        if dbSNR > SNRlimit: # and abs(meanGauss/sigma2) > 0.00001:
            try:
                popt,pcov = curve_fit(self.gaus,xSamples,yMean,p0=yMoments)
                FitGauss=self.gaus(xSamples,*popt)
                
            except :#RuntimeError:
                FitGauss=numpy.ones(len(xSamples))*numpy.mean(yMean)
                
                
        else:
            FitGauss=numpy.ones(len(xSamples))*numpy.mean(yMean)
        
        
        
        '''****** Getting Fij ******'''
        Fijcspc = CSPCopt[:,2]/2*3
        
        #GauWidth = (popt[2]/2)*3   
        GaussCenter = popt[1] #xFrec[GCpos]
        #Punto en Eje X de la Gaussiana donde se encuentra el centro
        ClosestCenter = xSamples[numpy.abs(xSamples-GaussCenter).argmin()]
        PointGauCenter = numpy.where(xSamples==ClosestCenter)[0][0]
        
        #Punto e^-1 hubicado en la Gaussiana  
        PeMinus1 = numpy.max(FitGauss)* numpy.exp(-1)
        FijClosest = FitGauss[numpy.abs(FitGauss-PeMinus1).argmin()] # El punto mas cercano a "Peminus1" dentro de "FitGauss"
        PointFij = numpy.where(FitGauss==FijClosest)[0][0]
        
        if xSamples[PointFij] > xSamples[PointGauCenter]:
            Fij = xSamples[PointFij] - xSamples[PointGauCenter]
            
        else:
            Fij = xSamples[PointGauCenter] - xSamples[PointFij]
            
#         print 'CSPCopt'
#         print CSPCopt
#         print 'popt'
#         print popt
#         print '#######################################'
        #print 'dataOut.data_param', numpy.shape(data_param)
        #print 'dataOut.data_param0', data_param[0,0,Height]
        #print 'dataOut.data_param1', data_param[0,1,Height]
        #print 'dataOut.data_param2', data_param[0,2,Height]
        
        
#         print 'yMoments', yMoments
#         print 'Moments', SPCmoments
#         print 'Fij2 Moment', Fij
#         #print 'Fij', Fij, 'popt[2]/2',popt[2]/2
#         print 'Fijcspc',Fijcspc
#         print '#######################################'
        
       
        '''****** Taking frequency ranges from SPCs ******'''
        
        
        #GaussCenter = popt[1]     #Primer momento 01
        GauWidth = popt[2] *3/2        #Ancho de banda de Gau01
        Range = numpy.empty(2)
        Range[0] = GaussCenter - GauWidth
        Range[1] = GaussCenter + GauWidth 
        #Punto en Eje X de la Gaussiana donde se encuentra ancho de banda (min:max) 
        ClosRangeMin = xSamples[numpy.abs(xSamples-Range[0]).argmin()]
        ClosRangeMax = xSamples[numpy.abs(xSamples-Range[1]).argmin()]
        
        PointRangeMin = numpy.where(xSamples==ClosRangeMin)[0][0]
        PointRangeMax = numpy.where(xSamples==ClosRangeMax)[0][0]
        
        Range=numpy.array([ PointRangeMin, PointRangeMax ])
        
        FrecRange = xFrec[ Range[0] : Range[1] ]
        VelRange  = xVel[ Range[0] : Range[1] ]
        
        
        #print 'RANGE: ', Range 
        #print 'FrecRange', numpy.shape(FrecRange)#,FrecRange
        #print 'len: ', len(FrecRange)
        
        '''****** Getting SCPC Slope ******'''
        
        for i in range(spc.shape[0]):
            
            if len(FrecRange)>5 and len(FrecRange)<spc.shape[1]*0.6:
                PhaseRange=self.moving_average(phase[i,Range[0]:Range[1]],N=3) 
                
                #print 'Ancho espectral Frecuencias', FrecRange[-1]-FrecRange[0], 'Hz'
                #print 'Ancho espectral Velocidades', VelRange[-1]-VelRange[0], 'm/s'
                #print 'FrecRange', len(FrecRange) , FrecRange
                #print 'VelRange', len(VelRange) , VelRange
                #print 'PhaseRange', numpy.shape(PhaseRange), PhaseRange
                #print ' '
                
                '''***********************VelRange******************'''
                
                mask = ~numpy.isnan(FrecRange) & ~numpy.isnan(PhaseRange)
                
                if len(FrecRange) == len(PhaseRange):
                    try:
                        slope, intercept, r_value, p_value, std_err = stats.linregress(FrecRange[mask], PhaseRange[mask])
                        PhaseSlope[i]=slope
                        PhaseInter[i]=intercept
                    except:
                        PhaseSlope[i]=0
                        PhaseInter[i]=0
                else:
                    PhaseSlope[i]=0
                    PhaseInter[i]=0
            else:
                PhaseSlope[i]=0
                PhaseInter[i]=0
            
            
            '''Getting constant C'''
            cC=(Fij*numpy.pi)**2
            
            '''****** Getting constants F and G ******'''
            MijEijNij=numpy.array([[E02,N02], [E12,N12]])
            MijResult0=(-PhaseSlope[1]*cC) / (2*numpy.pi)
            MijResult1=(-PhaseSlope[2]*cC) / (2*numpy.pi) 
            MijResults=numpy.array([MijResult0,MijResult1])
            (cF,cG) = numpy.linalg.solve(MijEijNij, MijResults)
            
            '''****** Getting constants A, B and H ******'''
            W01=numpy.nanmax( FitGauss01 ) #numpy.abs(CSPCSamples[0]))
            W02=numpy.nanmax( FitGauss02 ) #numpy.abs(CSPCSamples[1]))
            W12=numpy.nanmax( FitGauss12 ) #numpy.abs(CSPCSamples[2]))
            
            WijResult0=((cF*E01+cG*N01)**2)/cC - numpy.log(W01 / numpy.sqrt(numpy.pi/cC))
            WijResult1=((cF*E02+cG*N02)**2)/cC - numpy.log(W02 / numpy.sqrt(numpy.pi/cC))
            WijResult2=((cF*E12+cG*N12)**2)/cC - numpy.log(W12 / numpy.sqrt(numpy.pi/cC))
            
            WijResults=numpy.array([WijResult0, WijResult1, WijResult2])
            
            WijEijNij=numpy.array([ [E01**2, N01**2, 2*E01*N01] , [E02**2, N02**2, 2*E02*N02] , [E12**2, N12**2, 2*E12*N12] ])    
            (cA,cB,cH) = numpy.linalg.solve(WijEijNij, WijResults)
            
            VxVy=numpy.array([[cA,cH],[cH,cB]])
            VxVyResults=numpy.array([-cF,-cG])
            (Vx,Vy) = numpy.linalg.solve(VxVy, VxVyResults)
            
            #print 'MijResults, cC, PhaseSlope', MijResults, cC, PhaseSlope
            #print 'W01,02,12', W01, W02, W12
            #print 'WijResult0,1,2',WijResult0, WijResult1, WijResult2, 'Results', WijResults
            #print 'cA,cB,cH, cF, cG', cA, cB, cH, cF, cG
            #print 'VxVy', VxVyResults
            #print '###########################****************************************'
            Vzon = Vy
            Vmer = Vx
            Vmag=numpy.sqrt(Vzon**2+Vmer**2)
            Vang=numpy.arctan2(Vmer,Vzon)
            Vver=SPCmoments[1]
            FitGaussCSPC = numpy.array([FitGauss01,FitGauss02,FitGauss12])
            
            
#             ''' Ploteo por altura '''
#         if Height == 28:    
#             for i in range(3):
#                 #print 'FASE', numpy.shape(phase), y[25]
#                 #print numpy.shape(coherence)
#                 fig = plt.figure(10+self.indice)
#                 #plt.plot( x[0:256],coherence[:,25] )
#                 #cohAv = numpy.average(coherence[i],1)
#                 Pendiente = FrecRange * PhaseSlope[i]                
#                 plt.plot( FrecRange, Pendiente)
#                 plt.plot( xFrec,phase[i])
#                  
#                 CSPCmean = numpy.mean(numpy.abs(CSPCSamples),0)
#                 #plt.plot(xFrec, FitGauss01)
#                 #plt.plot(xFrec, CSPCmean)
#                 #plt.plot(xFrec, numpy.abs(CSPCSamples[0]))
#                 #plt.plot(xFrec, FitGauss)
#                 #plt.plot(xFrec, yMean)
#                 #plt.plot(xFrec, numpy.abs(coherence[0]))
#                  
#                 #plt.axis([-12, 12, 15, 50])
#                 #plt.title("%s" %(  '%s %s, Channel %s'%(thisDatetime.strftime("%Y/%m/%d"),thisDatetime.strftime("%H:%M:%S") , i)))
#                 plt.ylabel('Desfase [rad]')
#                 #plt.ylabel('CSPC normalizado')
#                 plt.xlabel('Frec range [Hz]')
                 
                #fig.savefig('/home/erick/Documents/Pics/to{}.png'.format(self.indice))
                 
#                plt.show()
#                self.indice=self.indice+1    
            
        
         
        
        
#         print 'vzon y vmer', Vzon, Vmer
        return Vzon, Vmer, Vver, GaussCenter, PhaseSlope, FitGaussCSPC
        
class SpectralMoments(Operation):
    
    '''
        Function SpectralMoments()
        
        Calculates moments (power, mean, standard deviation) and SNR of the signal
        
        Type of dataIn:    Spectra
        
        Configuration Parameters:
        
            dirCosx    :     Cosine director in X axis
            dirCosy    :     Cosine director in Y axis
        
            elevation  :
            azimuth    :
        
        Input:
            channelList    :    simple channel list to select e.g. [2,3,7] 
            self.dataOut.data_pre        :    Spectral data
            self.dataOut.abscissaList    :    List of frequencies
            self.dataOut.noise           :    Noise level per channel
            
        Affected:
            self.dataOut.moments      :    Parameters per channel
            self.dataOut.data_SNR        :    SNR per channel
            
    '''
    
    def run(self, dataOut):
        
        #dataOut.data_pre = dataOut.data_pre[0]
        data = dataOut.data_pre[0]
        absc = dataOut.abscissaList[:-1]
        noise = dataOut.noise
        nChannel = data.shape[0]
        data_param = numpy.zeros((nChannel, 4, data.shape[2]))
                
        for ind in range(nChannel):
            data_param[ind,:,:] = self.__calculateMoments( data[ind,:,:] , absc , noise[ind] )
        
        dataOut.moments = data_param[:,1:,:]
        dataOut.data_SNR = data_param[:,0]
        return
    
    def __calculateMoments(self, oldspec, oldfreq, n0, 
                           nicoh = None, graph = None, smooth = None, type1 = None, fwindow = None, snrth = None, dc = None, aliasing = None, oldfd = None, wwauto = None):
        
        if (nicoh == None): nicoh = 1
        if (graph == None): graph = 0    
        if (smooth == None): smooth = 0
        elif (self.smooth < 3): smooth = 0

        if (type1 == None): type1 = 0
        if (fwindow == None): fwindow = numpy.zeros(oldfreq.size) + 1
        if (snrth == None): snrth = -3
        if (dc == None): dc = 0
        if (aliasing == None): aliasing = 0
        if (oldfd == None): oldfd = 0
        if (wwauto == None): wwauto = 0
        
        if (n0 < 1.e-20):   n0 = 1.e-20
        
        freq = oldfreq
        vec_power = numpy.zeros(oldspec.shape[1])
        vec_fd = numpy.zeros(oldspec.shape[1])
        vec_w = numpy.zeros(oldspec.shape[1])
        vec_snr = numpy.zeros(oldspec.shape[1])
        
        oldspec = numpy.ma.masked_invalid(oldspec)

        for ind in range(oldspec.shape[1]):
                        
            spec = oldspec[:,ind]
            aux = spec*fwindow
            max_spec = aux.max()
            m = list(aux).index(max_spec)
                       
            #Smooth    
            if (smooth == 0):   spec2 = spec
            else:   spec2 = scipy.ndimage.filters.uniform_filter1d(spec,size=smooth)
    
            #    Calculo de Momentos
            bb = spec2[range(m,spec2.size)]
            bb = (bb<n0).nonzero()
            bb = bb[0]
            
            ss = spec2[range(0,m + 1)]
            ss = (ss<n0).nonzero()
            ss = ss[0]
            
            if (bb.size == 0):
                bb0 = spec.size - 1 - m
            else:   
                bb0 = bb[0] - 1
                if (bb0 < 0):
                    bb0 = 0
                    
            if (ss.size == 0):   ss1 = 1
            else: ss1 = max(ss) + 1
            
            if (ss1 > m):   ss1 = m
            
            valid = numpy.asarray(range(int(m + bb0 - ss1 + 1))) + ss1               
            power = ( (spec2[valid] - n0) * fwindow[valid] ).sum()
            fd = ( (spec2[valid]- n0) * freq[valid] * fwindow[valid] ).sum() / power
            w = math.sqrt(((spec2[valid] - n0)*fwindow[valid]*(freq[valid]- fd)**2).sum()/power)
            snr = (spec2.mean()-n0)/n0               
            
            if (snr < 1.e-20) :  
                snr = 1.e-20
            
            vec_power[ind] = power
            vec_fd[ind] = fd
            vec_w[ind] = w
            vec_snr[ind] = snr
        
        moments = numpy.vstack((vec_snr, vec_power, vec_fd, vec_w))
        return moments
    
    #------------------    Get SA Parameters    --------------------------
    
    def GetSAParameters(self):
        #SA en frecuencia
        pairslist = self.dataOut.groupList
        num_pairs = len(pairslist)
        
        vel = self.dataOut.abscissaList
        spectra = self.dataOut.data_pre
        cspectra = self.dataIn.data_cspc
        delta_v = vel[1] - vel[0] 
        
        #Calculating the power spectrum
        spc_pow = numpy.sum(spectra, 3)*delta_v
        #Normalizing Spectra
        norm_spectra = spectra/spc_pow
        #Calculating the norm_spectra at peak
        max_spectra = numpy.max(norm_spectra, 3)  
        
        #Normalizing Cross Spectra
        norm_cspectra = numpy.zeros(cspectra.shape)
        
        for i in range(num_chan):
            norm_cspectra[i,:,:] = cspectra[i,:,:]/numpy.sqrt(spc_pow[pairslist[i][0],:]*spc_pow[pairslist[i][1],:])
        
        max_cspectra = numpy.max(norm_cspectra,2)
        max_cspectra_index = numpy.argmax(norm_cspectra, 2)
        
        for i in range(num_pairs):
            cspc_par[i,:,:] = __calculateMoments(norm_cspectra)
    #-------------------    Get Lags    ----------------------------------
    
class SALags(Operation):
    '''
    Function GetMoments()

    Input:
        self.dataOut.data_pre
        self.dataOut.abscissaList
        self.dataOut.noise
        self.dataOut.normFactor
        self.dataOut.data_SNR
        self.dataOut.groupList
        self.dataOut.nChannels
        
    Affected:
        self.dataOut.data_param
    
    '''
    def run(self, dataOut):    
        data_acf = dataOut.data_pre[0]
        data_ccf = dataOut.data_pre[1]
        normFactor_acf = dataOut.normFactor[0]
        normFactor_ccf = dataOut.normFactor[1]
        pairs_acf = dataOut.groupList[0]
        pairs_ccf = dataOut.groupList[1]
        
        nHeights = dataOut.nHeights
        absc = dataOut.abscissaList
        noise = dataOut.noise
        SNR = dataOut.data_SNR
        nChannels = dataOut.nChannels
#         pairsList = dataOut.groupList
#         pairsAutoCorr, pairsCrossCorr = self.__getPairsAutoCorr(pairsList, nChannels)

        for l in range(len(pairs_acf)):
            data_acf[l,:,:] = data_acf[l,:,:]/normFactor_acf[l,:]
            
        for l in range(len(pairs_ccf)):
            data_ccf[l,:,:] = data_ccf[l,:,:]/normFactor_ccf[l,:]
        
        dataOut.data_param = numpy.zeros((len(pairs_ccf)*2 + 1, nHeights))
        dataOut.data_param[:-1,:] = self.__calculateTaus(data_acf, data_ccf, absc)
        dataOut.data_param[-1,:] = self.__calculateLag1Phase(data_acf, absc)
        return
    
#     def __getPairsAutoCorr(self, pairsList, nChannels):
# 
#         pairsAutoCorr = numpy.zeros(nChannels, dtype = 'int')*numpy.nan
#             
#         for l in range(len(pairsList)):    
#             firstChannel = pairsList[l][0]
#             secondChannel = pairsList[l][1]
#                 
#             #Obteniendo pares de Autocorrelacion     
#             if firstChannel == secondChannel:
#                 pairsAutoCorr[firstChannel] = int(l)
#              
#         pairsAutoCorr = pairsAutoCorr.astype(int)
#         
#         pairsCrossCorr = range(len(pairsList))
#         pairsCrossCorr = numpy.delete(pairsCrossCorr,pairsAutoCorr)
#         
#         return pairsAutoCorr, pairsCrossCorr
    
    def __calculateTaus(self, data_acf, data_ccf, lagRange):
        
        lag0 = data_acf.shape[1]/2
        #Funcion de Autocorrelacion
        mean_acf = stats.nanmean(data_acf, axis = 0)
        
        #Obtencion Indice de TauCross
        ind_ccf = data_ccf.argmax(axis = 1)
        #Obtencion Indice de TauAuto
        ind_acf = numpy.zeros(ind_ccf.shape,dtype = 'int')
        ccf_lag0 = data_ccf[:,lag0,:]
        
        for i in range(ccf_lag0.shape[0]):
            ind_acf[i,:] = numpy.abs(mean_acf - ccf_lag0[i,:]).argmin(axis = 0)
            
        #Obtencion de TauCross y TauAuto
        tau_ccf = lagRange[ind_ccf]
        tau_acf  = lagRange[ind_acf]
        
        Nan1, Nan2 = numpy.where(tau_ccf == lagRange[0])
        
        tau_ccf[Nan1,Nan2] = numpy.nan
        tau_acf[Nan1,Nan2] = numpy.nan
        tau = numpy.vstack((tau_ccf,tau_acf))
        
        return tau
    
    def __calculateLag1Phase(self, data, lagTRange):
        data1 = stats.nanmean(data, axis = 0)
        lag1 = numpy.where(lagTRange == 0)[0][0] + 1

        phase = numpy.angle(data1[lag1,:])
        
        return phase
    
class SpectralFitting(Operation):
    '''
        Function GetMoments()
        
        Input:
        Output:
        Variables modified:
    '''
    
    def run(self, dataOut, getSNR = True, path=None, file=None, groupList=None):    
        
        
        if path != None:
            sys.path.append(path)
        self.dataOut.library = importlib.import_module(file)
        
        #To be inserted as a parameter
        groupArray = numpy.array(groupList)
#         groupArray = numpy.array([[0,1],[2,3]]) 
        self.dataOut.groupList = groupArray
        
        nGroups = groupArray.shape[0]
        nChannels = self.dataIn.nChannels
        nHeights=self.dataIn.heightList.size
        
        #Parameters Array
        self.dataOut.data_param = None
        
        #Set constants
        constants = self.dataOut.library.setConstants(self.dataIn)
        self.dataOut.constants = constants
        M = self.dataIn.normFactor
        N = self.dataIn.nFFTPoints
        ippSeconds = self.dataIn.ippSeconds
        K = self.dataIn.nIncohInt
        pairsArray = numpy.array(self.dataIn.pairsList)
        
        #List of possible combinations
        listComb = itertools.combinations(numpy.arange(groupArray.shape[1]),2)
        indCross = numpy.zeros(len(list(listComb)), dtype = 'int')
        
        if getSNR:
            listChannels = groupArray.reshape((groupArray.size))
            listChannels.sort()
            noise = self.dataIn.getNoise()
            self.dataOut.data_SNR = self.__getSNR(self.dataIn.data_spc[listChannels,:,:], noise[listChannels])
        
        for i in range(nGroups): 
            coord = groupArray[i,:]
            
            #Input data array
            data = self.dataIn.data_spc[coord,:,:]/(M*N)
            data = data.reshape((data.shape[0]*data.shape[1],data.shape[2]))
            
            #Cross Spectra data array for Covariance Matrixes
            ind = 0
            for pairs in listComb:
                pairsSel = numpy.array([coord[x],coord[y]])
                indCross[ind] = int(numpy.where(numpy.all(pairsArray == pairsSel, axis = 1))[0][0])
                ind += 1
            dataCross = self.dataIn.data_cspc[indCross,:,:]/(M*N)
            dataCross = dataCross**2/K
            
            for h in range(nHeights):
#                 print self.dataOut.heightList[h]
                
                #Input
                d = data[:,h]

                #Covariance Matrix
                D = numpy.diag(d**2/K)
                ind = 0
                for pairs in listComb:
                    #Coordinates in Covariance Matrix
                    x = pairs[0]    
                    y = pairs[1]
                    #Channel Index
                    S12 = dataCross[ind,:,h]
                    D12 = numpy.diag(S12)
                    #Completing Covariance Matrix with Cross Spectras
                    D[x*N:(x+1)*N,y*N:(y+1)*N] = D12
                    D[y*N:(y+1)*N,x*N:(x+1)*N] = D12
                    ind += 1
                Dinv=numpy.linalg.inv(D)
                L=numpy.linalg.cholesky(Dinv)
                LT=L.T

                dp = numpy.dot(LT,d)
                
                #Initial values
                data_spc = self.dataIn.data_spc[coord,:,h]
                
                if (h>0)and(error1[3]<5):
                    p0 = self.dataOut.data_param[i,:,h-1]
                else:
                    p0 = numpy.array(self.dataOut.library.initialValuesFunction(data_spc, constants, i))
                
                try:
                    #Least Squares
                    minp,covp,infodict,mesg,ier = optimize.leastsq(self.__residFunction,p0,args=(dp,LT,constants),full_output=True)
#                   minp,covp = optimize.leastsq(self.__residFunction,p0,args=(dp,LT,constants))
                    #Chi square error
                    error0 = numpy.sum(infodict['fvec']**2)/(2*N)
                    #Error with Jacobian
                    error1 = self.dataOut.library.errorFunction(minp,constants,LT)
                except:
                    minp = p0*numpy.nan
                    error0 = numpy.nan
                    error1 = p0*numpy.nan
                                         
                #Save
                if self.dataOut.data_param == None:
                    self.dataOut.data_param = numpy.zeros((nGroups, p0.size, nHeights))*numpy.nan
                    self.dataOut.data_error = numpy.zeros((nGroups, p0.size + 1, nHeights))*numpy.nan
                
                self.dataOut.data_error[i,:,h] = numpy.hstack((error0,error1))
                self.dataOut.data_param[i,:,h] = minp
        return
    
    def __residFunction(self, p, dp, LT, constants):

        fm = self.dataOut.library.modelFunction(p, constants)
        fmp=numpy.dot(LT,fm)
        
        return  dp-fmp

    def __getSNR(self, z, noise):
        
        avg = numpy.average(z, axis=1)
        SNR = (avg.T-noise)/noise
        SNR = SNR.T
        return SNR
    
    def __chisq(p,chindex,hindex):
        #similar to Resid but calculates CHI**2
        [LT,d,fm]=setupLTdfm(p,chindex,hindex)
        dp=numpy.dot(LT,d)
        fmp=numpy.dot(LT,fm)
        chisq=numpy.dot((dp-fmp).T,(dp-fmp))
        return chisq
    
class WindProfiler(Operation):
       
    __isConfig = False
        
    __initime = None
    __lastdatatime = None
    __integrationtime = None
    
    __buffer = None
    
    __dataReady = False
    
    __firstdata = None
    
    n = None
    
    def __init__(self, **kwargs):    
        Operation.__init__(self, **kwargs)
    
    def __calculateCosDir(self, elev, azim):
        zen = (90 - elev)*numpy.pi/180
        azim = azim*numpy.pi/180
        cosDirX = numpy.sqrt((1-numpy.cos(zen)**2)/((1+numpy.tan(azim)**2))) 
        cosDirY = numpy.sqrt(1-numpy.cos(zen)**2-cosDirX**2)
        
        signX = numpy.sign(numpy.cos(azim))
        signY = numpy.sign(numpy.sin(azim))
        
        cosDirX = numpy.copysign(cosDirX, signX)
        cosDirY = numpy.copysign(cosDirY, signY)
        return cosDirX, cosDirY
    
    def __calculateAngles(self, theta_x, theta_y, azimuth):
   
        dir_cosw = numpy.sqrt(1-theta_x**2-theta_y**2)
        zenith_arr = numpy.arccos(dir_cosw)
        azimuth_arr = numpy.arctan2(theta_x,theta_y) + azimuth*math.pi/180
        
        dir_cosu = numpy.sin(azimuth_arr)*numpy.sin(zenith_arr)
        dir_cosv = numpy.cos(azimuth_arr)*numpy.sin(zenith_arr)
        
        return azimuth_arr, zenith_arr, dir_cosu, dir_cosv, dir_cosw

    def __calculateMatA(self, dir_cosu, dir_cosv, dir_cosw, horOnly):
        
#         
        if horOnly:
            A = numpy.c_[dir_cosu,dir_cosv]
        else:
            A = numpy.c_[dir_cosu,dir_cosv,dir_cosw]
        A = numpy.asmatrix(A)
        A1 = numpy.linalg.inv(A.transpose()*A)*A.transpose()

        return A1

    def __correctValues(self, heiRang, phi, velRadial, SNR):
        listPhi = phi.tolist()
        maxid = listPhi.index(max(listPhi))
        minid = listPhi.index(min(listPhi))
        
        rango = range(len(phi))       
   #     rango = numpy.delete(rango,maxid)
        
        heiRang1 = heiRang*math.cos(phi[maxid])
        heiRangAux = heiRang*math.cos(phi[minid])
        indOut = (heiRang1 < heiRangAux[0]).nonzero()
        heiRang1 = numpy.delete(heiRang1,indOut)
        
        velRadial1 = numpy.zeros([len(phi),len(heiRang1)])
        SNR1 = numpy.zeros([len(phi),len(heiRang1)])
        
        for i in rango:
            x = heiRang*math.cos(phi[i])
            y1 = velRadial[i,:]
            f1 = interpolate.interp1d(x,y1,kind = 'cubic')
            
            x1 = heiRang1
            y11 = f1(x1)
            
            y2 = SNR[i,:]
            f2 = interpolate.interp1d(x,y2,kind = 'cubic')
            y21 = f2(x1)
            
            velRadial1[i,:] = y11
            SNR1[i,:] = y21
             
        return heiRang1, velRadial1, SNR1

    def __calculateVelUVW(self, A, velRadial):
        
        #Operacion Matricial
#         velUVW = numpy.zeros((velRadial.shape[1],3))
#         for ind in range(velRadial.shape[1]):
#             velUVW[ind,:] = numpy.dot(A,velRadial[:,ind])
#         velUVW = velUVW.transpose()
        velUVW = numpy.zeros((A.shape[0],velRadial.shape[1]))
        velUVW[:,:] = numpy.dot(A,velRadial)
        
        
        return velUVW
    
#     def techniqueDBS(self, velRadial0, dirCosx, disrCosy, azimuth, correct, horizontalOnly, heiRang, SNR0):
    
    def techniqueDBS(self, kwargs):
        """
        Function that implements Doppler Beam Swinging (DBS) technique.
        
        Input:    Radial velocities, Direction cosines (x and y) of the Beam, Antenna azimuth,
                    Direction correction (if necessary), Ranges and SNR
        
        Output:    Winds estimation (Zonal, Meridional and Vertical)
        
        Parameters affected:    Winds, height range, SNR
        """
        velRadial0 = kwargs['velRadial']
        heiRang = kwargs['heightList']
        SNR0 = kwargs['SNR']
        
        if kwargs.has_key('dirCosx') and kwargs.has_key('dirCosy'):
            theta_x = numpy.array(kwargs['dirCosx'])
            theta_y = numpy.array(kwargs['dirCosy'])
        else:
            elev = numpy.array(kwargs['elevation'])
            azim = numpy.array(kwargs['azimuth'])
            theta_x, theta_y = self.__calculateCosDir(elev, azim)
        azimuth = kwargs['correctAzimuth']    
        if kwargs.has_key('horizontalOnly'):
            horizontalOnly = kwargs['horizontalOnly']
        else:   horizontalOnly = False
        if kwargs.has_key('correctFactor'):
            correctFactor = kwargs['correctFactor']
        else:   correctFactor = 1
        if kwargs.has_key('channelList'):
            channelList = kwargs['channelList']
            if len(channelList) == 2:
                horizontalOnly = True
            arrayChannel = numpy.array(channelList)
            param = param[arrayChannel,:,:]
            theta_x = theta_x[arrayChannel]
            theta_y = theta_y[arrayChannel]
    
        azimuth_arr, zenith_arr, dir_cosu, dir_cosv, dir_cosw = self.__calculateAngles(theta_x, theta_y, azimuth) 
        heiRang1, velRadial1, SNR1 = self.__correctValues(heiRang, zenith_arr, correctFactor*velRadial0, SNR0)  
        A = self.__calculateMatA(dir_cosu, dir_cosv, dir_cosw, horizontalOnly)
          
        #Calculo de Componentes de la velocidad con DBS
        winds = self.__calculateVelUVW(A,velRadial1)
        
        return winds, heiRang1, SNR1
    
    def __calculateDistance(self, posx, posy, pairs_ccf, azimuth = None):
        
        nPairs = len(pairs_ccf)
        posx = numpy.asarray(posx)
        posy = numpy.asarray(posy)
        
        #Rotacion Inversa para alinear con el azimuth
        if azimuth!= None:
            azimuth = azimuth*math.pi/180
            posx1 = posx*math.cos(azimuth) + posy*math.sin(azimuth)
            posy1 = -posx*math.sin(azimuth) + posy*math.cos(azimuth)
        else:
            posx1 = posx
            posy1 = posy
        
        #Calculo de Distancias
        distx = numpy.zeros(nPairs)
        disty = numpy.zeros(nPairs)
        dist = numpy.zeros(nPairs)
        ang = numpy.zeros(nPairs)
        
        for i in range(nPairs):
            distx[i] = posx1[pairs_ccf[i][1]] - posx1[pairs_ccf[i][0]]
            disty[i] = posy1[pairs_ccf[i][1]] - posy1[pairs_ccf[i][0]] 
            dist[i] = numpy.sqrt(distx[i]**2 + disty[i]**2)
            ang[i] = numpy.arctan2(disty[i],distx[i])
        
        return distx, disty, dist, ang
        #Calculo de Matrices   
#         nPairs = len(pairs)
#         ang1 = numpy.zeros((nPairs, 2, 1))
#         dist1 = numpy.zeros((nPairs, 2, 1))
#         
#         for j in range(nPairs):
#             dist1[j,0,0] = dist[pairs[j][0]]
#             dist1[j,1,0] = dist[pairs[j][1]]
#             ang1[j,0,0] = ang[pairs[j][0]]
#             ang1[j,1,0] = ang[pairs[j][1]]
#             
#         return distx,disty, dist1,ang1

    
    def __calculateVelVer(self, phase, lagTRange, _lambda):

        Ts = lagTRange[1] - lagTRange[0]
        velW = -_lambda*phase/(4*math.pi*Ts)
        
        return velW
    
    def __calculateVelHorDir(self, dist, tau1, tau2, ang):
        nPairs = tau1.shape[0]
        nHeights = tau1.shape[1]
        vel = numpy.zeros((nPairs,3,nHeights))       
        dist1 = numpy.reshape(dist, (dist.size,1))
        
        angCos = numpy.cos(ang)
        angSin = numpy.sin(ang)
        
        vel0 = dist1*tau1/(2*tau2**2) 
        vel[:,0,:] = (vel0*angCos).sum(axis = 1)
        vel[:,1,:] = (vel0*angSin).sum(axis = 1)
        
        ind = numpy.where(numpy.isinf(vel))
        vel[ind] = numpy.nan
                
        return vel
    
#     def __getPairsAutoCorr(self, pairsList, nChannels):
# 
#         pairsAutoCorr = numpy.zeros(nChannels, dtype = 'int')*numpy.nan
#             
#         for l in range(len(pairsList)):    
#             firstChannel = pairsList[l][0]
#             secondChannel = pairsList[l][1]
#                 
#             #Obteniendo pares de Autocorrelacion     
#             if firstChannel == secondChannel:
#                 pairsAutoCorr[firstChannel] = int(l)
#              
#         pairsAutoCorr = pairsAutoCorr.astype(int)
#         
#         pairsCrossCorr = range(len(pairsList))
#         pairsCrossCorr = numpy.delete(pairsCrossCorr,pairsAutoCorr)
#         
#         return pairsAutoCorr, pairsCrossCorr
    
#     def techniqueSA(self, pairsSelected, pairsList, nChannels, tau, azimuth, _lambda, position_x, position_y, lagTRange, correctFactor):
    def techniqueSA(self, kwargs):
        
        """ 
        Function that implements Spaced Antenna (SA) technique.
        
        Input:    Radial velocities, Direction cosines (x and y) of the Beam, Antenna azimuth,
                    Direction correction (if necessary), Ranges and SNR
        
        Output:    Winds estimation (Zonal, Meridional and Vertical)
        
        Parameters affected:    Winds
        """
        position_x = kwargs['positionX']
        position_y = kwargs['positionY']
        azimuth = kwargs['azimuth']
        
        if kwargs.has_key('correctFactor'):
            correctFactor = kwargs['correctFactor']
        else:
            correctFactor = 1
        
        groupList = kwargs['groupList']
        pairs_ccf = groupList[1]
        tau = kwargs['tau']
        _lambda = kwargs['_lambda']
        
        #Cross Correlation pairs obtained
#         pairsAutoCorr, pairsCrossCorr = self.__getPairsAutoCorr(pairssList, nChannels)
#         pairsArray = numpy.array(pairsList)[pairsCrossCorr]
#         pairsSelArray = numpy.array(pairsSelected)
#         pairs = []
#         
#         #Wind estimation pairs obtained
#         for i in range(pairsSelArray.shape[0]/2):
#             ind1 = numpy.where(numpy.all(pairsArray == pairsSelArray[2*i], axis = 1))[0][0]
#             ind2 = numpy.where(numpy.all(pairsArray == pairsSelArray[2*i + 1], axis = 1))[0][0]
#             pairs.append((ind1,ind2))
        
        indtau = tau.shape[0]/2
        tau1 = tau[:indtau,:]
        tau2 = tau[indtau:-1,:]
#         tau1 = tau1[pairs,:]
#         tau2 = tau2[pairs,:]
        phase1 = tau[-1,:]
        
        #---------------------------------------------------------------------
        #Metodo Directo    
        distx, disty, dist, ang = self.__calculateDistance(position_x, position_y, pairs_ccf,azimuth)
        winds = self.__calculateVelHorDir(dist, tau1, tau2, ang)
        winds = stats.nanmean(winds, axis=0)
        #---------------------------------------------------------------------
        #Metodo General
#         distx, disty, dist = self.calculateDistance(position_x,position_y,pairsCrossCorr, pairsList, azimuth)
#         #Calculo Coeficientes de Funcion de Correlacion
#         F,G,A,B,H = self.calculateCoef(tau1,tau2,distx,disty,n)
#         #Calculo de Velocidades
#         winds = self.calculateVelUV(F,G,A,B,H)

        #---------------------------------------------------------------------
        winds[2,:] = self.__calculateVelVer(phase1, lagTRange, _lambda)
        winds = correctFactor*winds
        return winds
    
    def __checkTime(self, currentTime, paramInterval, outputInterval):
        
        dataTime = currentTime + paramInterval
        deltaTime = dataTime - self.__initime
        
        if deltaTime >= outputInterval or deltaTime < 0:
            self.__dataReady = True
        return 
    
    def techniqueMeteors(self, arrayMeteor, meteorThresh, heightMin, heightMax):
        '''
        Function that implements winds estimation technique with detected meteors.
        
        Input:    Detected meteors, Minimum meteor quantity to wind estimation
        
        Output:    Winds estimation (Zonal and Meridional)
        
        Parameters affected:    Winds
        '''      
#         print arrayMeteor.shape  
        #Settings
        nInt = (heightMax - heightMin)/2
#         print nInt
        nInt = int(nInt)
#         print nInt
        winds = numpy.zeros((2,nInt))*numpy.nan    
        
        #Filter errors
        error = numpy.where(arrayMeteor[:,-1] == 0)[0]
        finalMeteor = arrayMeteor[error,:]
        
        #Meteor Histogram
        finalHeights = finalMeteor[:,2]
        hist = numpy.histogram(finalHeights, bins = nInt, range = (heightMin,heightMax))
        nMeteorsPerI = hist[0]
        heightPerI = hist[1]
        
        #Sort of meteors
        indSort = finalHeights.argsort()
        finalMeteor2 = finalMeteor[indSort,:]
        
        #    Calculating winds
        ind1 = 0
        ind2 = 0   
        
        for i in range(nInt):
            nMet = nMeteorsPerI[i]
            ind1 = ind2
            ind2 = ind1 + nMet
            
            meteorAux = finalMeteor2[ind1:ind2,:]
            
            if meteorAux.shape[0] >= meteorThresh:
                vel = meteorAux[:, 6]
                zen = meteorAux[:, 4]*numpy.pi/180
                azim = meteorAux[:, 3]*numpy.pi/180
                
                n = numpy.cos(zen)
        #         m = (1 - n**2)/(1 - numpy.tan(azim)**2)
        #         l = m*numpy.tan(azim)
                l = numpy.sin(zen)*numpy.sin(azim)
                m = numpy.sin(zen)*numpy.cos(azim)
                
                A = numpy.vstack((l, m)).transpose()
                A1 = numpy.dot(numpy.linalg.inv( numpy.dot(A.transpose(),A) ),A.transpose())
                windsAux = numpy.dot(A1, vel)
                
                winds[0,i] = windsAux[0]
                winds[1,i] = windsAux[1]
                
        return winds, heightPerI[:-1]
    
    def techniqueNSM_SA(self, **kwargs):
        metArray = kwargs['metArray']
        heightList = kwargs['heightList']
        timeList = kwargs['timeList']
        
        rx_location = kwargs['rx_location']
        groupList = kwargs['groupList']
        azimuth = kwargs['azimuth']
        dfactor = kwargs['dfactor']
        k = kwargs['k']
        
        azimuth1, dist = self.__calculateAzimuth1(rx_location, groupList, azimuth)
        d = dist*dfactor
        #Phase calculation
        metArray1 = self.__getPhaseSlope(metArray, heightList, timeList)
        
        metArray1[:,-2] = metArray1[:,-2]*metArray1[:,2]*1000/(k*d[metArray1[:,1].astype(int)]) #angles into velocities
        
        velEst = numpy.zeros((heightList.size,2))*numpy.nan
        azimuth1 = azimuth1*numpy.pi/180
        
        for i in range(heightList.size):
            h = heightList[i]
            indH = numpy.where((metArray1[:,2] == h)&(numpy.abs(metArray1[:,-2]) < 100))[0]
            metHeight = metArray1[indH,:]
            if metHeight.shape[0] >= 2:
                velAux = numpy.asmatrix(metHeight[:,-2]).T    #Radial Velocities
                iazim = metHeight[:,1].astype(int)
                azimAux = numpy.asmatrix(azimuth1[iazim]).T    #Azimuths
                A = numpy.hstack((numpy.cos(azimAux),numpy.sin(azimAux)))
                A = numpy.asmatrix(A)
                A1 = numpy.linalg.pinv(A.transpose()*A)*A.transpose()
                velHor = numpy.dot(A1,velAux)
                
                velEst[i,:] = numpy.squeeze(velHor)
        return velEst
    
    def __getPhaseSlope(self, metArray, heightList, timeList):
        meteorList = []
        #utctime sec1 height SNR velRad ph0 ph1 ph2 coh0 coh1 coh2
        #Putting back together the meteor matrix
        utctime = metArray[:,0]
        uniqueTime = numpy.unique(utctime)
        
        phaseDerThresh = 0.5
        ippSeconds = timeList[1] - timeList[0]
        sec = numpy.where(timeList>1)[0][0]
        nPairs = metArray.shape[1] - 6
        nHeights = len(heightList)
        
        for t in uniqueTime:
            metArray1 = metArray[utctime==t,:]
#         phaseDerThresh = numpy.pi/4 #reducir Phase thresh
            tmet = metArray1[:,1].astype(int)
            hmet = metArray1[:,2].astype(int)
            
            metPhase = numpy.zeros((nPairs, heightList.size, timeList.size - 1))
            metPhase[:,:] = numpy.nan
            metPhase[:,hmet,tmet] = metArray1[:,6:].T
            
            #Delete short trails
            metBool = ~numpy.isnan(metPhase[0,:,:])
            heightVect = numpy.sum(metBool, axis = 1)
            metBool[heightVect<sec,:] = False
            metPhase[:,heightVect<sec,:] = numpy.nan
            
            #Derivative
            metDer = numpy.abs(metPhase[:,:,1:] - metPhase[:,:,:-1])
            phDerAux = numpy.dstack((numpy.full((nPairs,nHeights,1), False, dtype=bool),metDer > phaseDerThresh))
            metPhase[phDerAux] = numpy.nan
                
            #--------------------------METEOR DETECTION    -----------------------------------------
            indMet = numpy.where(numpy.any(metBool,axis=1))[0]
            
            for p in numpy.arange(nPairs):
                phase = metPhase[p,:,:]
                phDer = metDer[p,:,:]
                
                for h in indMet:
                    height = heightList[h]
                    phase1 = phase[h,:] #82
                    phDer1 = phDer[h,:]
                       
                    phase1[~numpy.isnan(phase1)] = numpy.unwrap(phase1[~numpy.isnan(phase1)])   #Unwrap
                       
                    indValid = numpy.where(~numpy.isnan(phase1))[0]
                    initMet = indValid[0]
                    endMet = 0
                                           
                    for i in range(len(indValid)-1):
                           
                        #Time difference
                        inow = indValid[i]
                        inext = indValid[i+1]
                        idiff = inext - inow
                        #Phase difference
                        phDiff = numpy.abs(phase1[inext] - phase1[inow]) 
                       
                        if idiff>sec or phDiff>numpy.pi/4 or inext==indValid[-1]:   #End of Meteor
                            sizeTrail = inow - initMet + 1
                            if sizeTrail>3*sec:  #Too short meteors
                                x = numpy.arange(initMet,inow+1)*ippSeconds
                                y = phase1[initMet:inow+1]
                                ynnan = ~numpy.isnan(y)
                                x = x[ynnan]
                                y = y[ynnan]
                                slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
                                ylin = x*slope + intercept
                                rsq = r_value**2
                                if rsq > 0.5:
                                    vel = slope#*height*1000/(k*d)
                                    estAux = numpy.array([utctime,p,height, vel, rsq])
                                    meteorList.append(estAux)
                            initMet = inext         
        metArray2 = numpy.array(meteorList)
        
        return metArray2
    
    def __calculateAzimuth1(self, rx_location, pairslist, azimuth0):
        
        azimuth1 = numpy.zeros(len(pairslist))
        dist = numpy.zeros(len(pairslist))
        
        for i in range(len(rx_location)):
            ch0 = pairslist[i][0]
            ch1 = pairslist[i][1]
            
            diffX = rx_location[ch0][0] - rx_location[ch1][0]
            diffY = rx_location[ch0][1] - rx_location[ch1][1]
            azimuth1[i] = numpy.arctan2(diffY,diffX)*180/numpy.pi
            dist[i] = numpy.sqrt(diffX**2 + diffY**2)
        
        azimuth1 -= azimuth0
        return azimuth1, dist
    
    def techniqueNSM_DBS(self, **kwargs):
        metArray = kwargs['metArray']
        heightList = kwargs['heightList']
        timeList = kwargs['timeList']
        zenithList = kwargs['zenithList']
        nChan = numpy.max(cmet) + 1
        nHeights = len(heightList)
        
        utctime = metArray[:,0]
        cmet = metArray[:,1]
        hmet = metArray1[:,3].astype(int)
        h1met = heightList[hmet]*zenithList[cmet]
        vmet = metArray1[:,5]
        
        for i in range(nHeights - 1):
            hmin = heightList[i]
            hmax = heightList[i + 1]
            
            vthisH = vmet[(h1met>=hmin) & (h1met<hmax)]
            
            
            
        return data_output
            
    def run(self, dataOut, technique, positionY, positionX, azimuth, **kwargs):
        
        param = dataOut.data_param
        if dataOut.abscissaList != None:
            absc = dataOut.abscissaList[:-1]
        noise = dataOut.noise
        heightList = dataOut.heightList
        SNR = dataOut.data_SNR
        
        if technique == 'DBS':
     
            kwargs['velRadial'] = param[:,1,:] #Radial velocity  
            kwargs['heightList'] = heightList
            kwargs['SNR'] = SNR
    
            dataOut.data_output, dataOut.heightList, dataOut.data_SNR = self.techniqueDBS(kwargs) #DBS Function
            dataOut.utctimeInit = dataOut.utctime
            dataOut.outputInterval = dataOut.paramInterval
            
        elif technique == 'SA':
        
            #Parameters
#             position_x = kwargs['positionX']
#             position_y = kwargs['positionY']
#             azimuth = kwargs['azimuth']
#             
#             if kwargs.has_key('crosspairsList'):
#                 pairs = kwargs['crosspairsList']
#             else:
#                 pairs = None   
# 
#             if kwargs.has_key('correctFactor'):
#                 correctFactor = kwargs['correctFactor']
#             else:
#                 correctFactor = 1
        
#             tau = dataOut.data_param
#             _lambda = dataOut.C/dataOut.frequency
#             pairsList = dataOut.groupList
#             nChannels = dataOut.nChannels
            
            kwargs['groupList'] = dataOut.groupList
            kwargs['tau'] = dataOut.data_param
            kwargs['_lambda'] = dataOut.C/dataOut.frequency
#             dataOut.data_output = self.techniqueSA(pairs, pairsList, nChannels, tau, azimuth, _lambda, position_x, position_y, absc, correctFactor)
            dataOut.data_output = self.techniqueSA(kwargs)
            dataOut.utctimeInit = dataOut.utctime
            dataOut.outputInterval = dataOut.timeInterval
            
        elif technique == 'Meteors':        
            dataOut.flagNoData = True
            self.__dataReady = False
            
            if kwargs.has_key('nHours'):
                nHours = kwargs['nHours']
            else: 
                nHours = 1
                
            if kwargs.has_key('meteorsPerBin'):
                meteorThresh = kwargs['meteorsPerBin']
            else:
                meteorThresh = 6
                
            if kwargs.has_key('hmin'):
                hmin = kwargs['hmin']
            else:   hmin = 70
            if kwargs.has_key('hmax'):
                hmax = kwargs['hmax']
            else:   hmax = 110
                     
            dataOut.outputInterval = nHours*3600
            
            if self.__isConfig == False:
#                 self.__initime = dataOut.datatime.replace(minute = 0, second = 0, microsecond = 03)
                #Get Initial LTC time
                self.__initime = datetime.datetime.utcfromtimestamp(dataOut.utctime)
                self.__initime = (self.__initime.replace(minute = 0, second = 0, microsecond = 0) - datetime.datetime(1970, 1, 1)).total_seconds()

                self.__isConfig = True
                
            if self.__buffer == None:
                self.__buffer = dataOut.data_param
                self.__firstdata = copy.copy(dataOut)

            else:
                self.__buffer = numpy.vstack((self.__buffer, dataOut.data_param))
            
            self.__checkTime(dataOut.utctime, dataOut.paramInterval, dataOut.outputInterval) #Check if the buffer is ready
            
            if self.__dataReady:
                dataOut.utctimeInit = self.__initime
                
                self.__initime += dataOut.outputInterval #to erase time offset
                
                dataOut.data_output, dataOut.heightList = self.techniqueMeteors(self.__buffer, meteorThresh, hmin, hmax)
                dataOut.flagNoData = False
                self.__buffer = None
                
        elif technique == 'Meteors1':
            dataOut.flagNoData = True
            self.__dataReady = False
            
            if kwargs.has_key('nMins'):
                nMins = kwargs['nMins']
            else: nMins = 20
            if kwargs.has_key('rx_location'):
                rx_location = kwargs['rx_location']
            else: rx_location = [(0,1),(1,1),(1,0)]
            if kwargs.has_key('azimuth'):
                azimuth = kwargs['azimuth']
            else: azimuth = 51
            if kwargs.has_key('dfactor'):
                dfactor = kwargs['dfactor']
            if kwargs.has_key('mode'):
                mode = kwargs['mode']
            else: mode = 'SA' 
            
            #Borrar luego esto
            if dataOut.groupList == None:
                dataOut.groupList = [(0,1),(0,2),(1,2)]
            groupList = dataOut.groupList
            C = 3e8
            freq = 50e6
            lamb = C/freq
            k = 2*numpy.pi/lamb
            
            timeList = dataOut.abscissaList
            heightList = dataOut.heightList
            
            if self.__isConfig == False:
                dataOut.outputInterval = nMins*60
#                 self.__initime = dataOut.datatime.replace(minute = 0, second = 0, microsecond = 03)
                #Get Initial LTC time
                initime = datetime.datetime.utcfromtimestamp(dataOut.utctime)
                minuteAux = initime.minute
                minuteNew = int(numpy.floor(minuteAux/nMins)*nMins)
                self.__initime = (initime.replace(minute = minuteNew, second = 0, microsecond = 0) - datetime.datetime(1970, 1, 1)).total_seconds()

                self.__isConfig = True
                
            if self.__buffer == None:
                self.__buffer = dataOut.data_param
                self.__firstdata = copy.copy(dataOut)

            else:
                self.__buffer = numpy.vstack((self.__buffer, dataOut.data_param))
            
            self.__checkTime(dataOut.utctime, dataOut.paramInterval, dataOut.outputInterval) #Check if the buffer is ready
            
            if self.__dataReady:
                dataOut.utctimeInit = self.__initime
                self.__initime += dataOut.outputInterval #to erase time offset
                
                metArray = self.__buffer
                if mode == 'SA':
                    dataOut.data_output = self.techniqueNSM_SA(rx_location=rx_location, groupList=groupList, azimuth=azimuth, dfactor=dfactor, k=k,metArray=metArray, heightList=heightList,timeList=timeList)
                elif mode == 'DBS':
                    dataOut.data_output = self.techniqueNSM_DBS(metArray=metArray,heightList=heightList,timeList=timeList)
                dataOut.data_output = dataOut.data_output.T
                dataOut.flagNoData = False
                self.__buffer = None

        return
    
class EWDriftsEstimation(Operation):
       
    def __init__(self):    
        Operation.__init__(self)    
    
    def __correctValues(self, heiRang, phi, velRadial, SNR):
        listPhi = phi.tolist()
        maxid = listPhi.index(max(listPhi))
        minid = listPhi.index(min(listPhi))
        
        rango = range(len(phi))       
   #     rango = numpy.delete(rango,maxid)
        
        heiRang1 = heiRang*math.cos(phi[maxid])
        heiRangAux = heiRang*math.cos(phi[minid])
        indOut = (heiRang1 < heiRangAux[0]).nonzero()
        heiRang1 = numpy.delete(heiRang1,indOut)
        
        velRadial1 = numpy.zeros([len(phi),len(heiRang1)])
        SNR1 = numpy.zeros([len(phi),len(heiRang1)])
        
        for i in rango:
            x = heiRang*math.cos(phi[i])
            y1 = velRadial[i,:]
            f1 = interpolate.interp1d(x,y1,kind = 'cubic')
            
            x1 = heiRang1
            y11 = f1(x1)
            
            y2 = SNR[i,:]
            f2 = interpolate.interp1d(x,y2,kind = 'cubic')
            y21 = f2(x1)
            
            velRadial1[i,:] = y11
            SNR1[i,:] = y21
             
        return heiRang1, velRadial1, SNR1

    def run(self, dataOut, zenith, zenithCorrection):
        heiRang = dataOut.heightList
        velRadial = dataOut.data_param[:,3,:]
        SNR = dataOut.data_SNR
        
        zenith = numpy.array(zenith)
        zenith -= zenithCorrection 
        zenith *= numpy.pi/180
        
        heiRang1, velRadial1, SNR1 = self.__correctValues(heiRang, numpy.abs(zenith), velRadial, SNR)
 
        alp = zenith[0]
        bet = zenith[1]
        
        w_w = velRadial1[0,:]
        w_e = velRadial1[1,:]
        
        w = (w_w*numpy.sin(bet) - w_e*numpy.sin(alp))/(numpy.cos(alp)*numpy.sin(bet) - numpy.cos(bet)*numpy.sin(alp))   
        u = (w_w*numpy.cos(bet) - w_e*numpy.cos(alp))/(numpy.sin(alp)*numpy.cos(bet) - numpy.sin(bet)*numpy.cos(alp))   
        
        winds = numpy.vstack((u,w))
        
        dataOut.heightList = heiRang1
        dataOut.data_output = winds
        dataOut.data_SNR = SNR1
        
        dataOut.utctimeInit = dataOut.utctime
        dataOut.outputInterval = dataOut.timeInterval
        return

#---------------    Non Specular Meteor    ----------------

class NonSpecularMeteorDetection(Operation):

    def run(self, mode, SNRthresh=8, phaseDerThresh=0.5, cohThresh=0.8, allData = False):
        data_acf = self.dataOut.data_pre[0]
        data_ccf = self.dataOut.data_pre[1]
        
        lamb = self.dataOut.C/self.dataOut.frequency
        tSamp = self.dataOut.ippSeconds*self.dataOut.nCohInt
        paramInterval = self.dataOut.paramInterval
        
        nChannels = data_acf.shape[0]
        nLags = data_acf.shape[1]
        nProfiles = data_acf.shape[2]
        nHeights = self.dataOut.nHeights
        nCohInt = self.dataOut.nCohInt
        sec = numpy.round(nProfiles/self.dataOut.paramInterval)
        heightList = self.dataOut.heightList
        ippSeconds = self.dataOut.ippSeconds*self.dataOut.nCohInt*self.dataOut.nAvg
        utctime = self.dataOut.utctime
        
        self.dataOut.abscissaList = numpy.arange(0,paramInterval+ippSeconds,ippSeconds)
        
        #------------------------    SNR    --------------------------------------
        power = data_acf[:,0,:,:].real
        noise = numpy.zeros(nChannels)
        SNR = numpy.zeros(power.shape)
        for i in range(nChannels):
            noise[i] = hildebrand_sekhon(power[i,:], nCohInt)
            SNR[i] = (power[i]-noise[i])/noise[i]
        SNRm = numpy.nanmean(SNR, axis = 0)
        SNRdB = 10*numpy.log10(SNR)
            
        if mode == 'SA':
            nPairs = data_ccf.shape[0]  
            #----------------------    Coherence and Phase   --------------------------
            phase = numpy.zeros(data_ccf[:,0,:,:].shape)
#             phase1 = numpy.copy(phase)
            coh1 = numpy.zeros(data_ccf[:,0,:,:].shape)
            
            for p in range(nPairs):
                ch0 = self.dataOut.groupList[p][0]
                ch1 = self.dataOut.groupList[p][1]
                ccf = data_ccf[p,0,:,:]/numpy.sqrt(data_acf[ch0,0,:,:]*data_acf[ch1,0,:,:])
                phase[p,:,:] = ndimage.median_filter(numpy.angle(ccf), size = (5,1)) #median filter 
#                 phase1[p,:,:] = numpy.angle(ccf) #median filter 
                coh1[p,:,:] = ndimage.median_filter(numpy.abs(ccf), 5) #median filter 
#                 coh1[p,:,:] = numpy.abs(ccf) #median filter 
            coh = numpy.nanmax(coh1, axis = 0)
#             struc = numpy.ones((5,1))
#             coh = ndimage.morphology.grey_dilation(coh, size=(10,1))
            #----------------------    Radial Velocity    ----------------------------
            phaseAux = numpy.mean(numpy.angle(data_acf[:,1,:,:]), axis = 0)
            velRad = phaseAux*lamb/(4*numpy.pi*tSamp)
            
            if allData:
                boolMetFin = ~numpy.isnan(SNRm)
#                 coh[:-1,:] = numpy.nanmean(numpy.abs(phase[:,1:,:] - phase[:,:-1,:]),axis=0)
            else:
                #------------------------    Meteor mask    ---------------------------------
#                 #SNR mask
#                 boolMet = (SNRdB>SNRthresh)#|(~numpy.isnan(SNRdB))
#                 
#                 #Erase small objects
#                 boolMet1 = self.__erase_small(boolMet, 2*sec, 5)   
#                 
#                 auxEEJ = numpy.sum(boolMet1,axis=0)
#                 indOver = auxEEJ>nProfiles*0.8  #Use this later
#                 indEEJ = numpy.where(indOver)[0]
#                 indNEEJ = numpy.where(~indOver)[0]
#                 
#                 boolMetFin = boolMet1
#                 
#                 if indEEJ.size > 0:
#                     boolMet1[:,indEEJ] = False  #Erase heights with EEJ            
#                     
#                     boolMet2 = coh > cohThresh
#                     boolMet2 = self.__erase_small(boolMet2, 2*sec,5)
#                                   
#                     #Final Meteor mask
#                     boolMetFin = boolMet1|boolMet2
                
                #Coherence mask
                boolMet1 = coh > 0.75
                struc = numpy.ones((30,1))
                boolMet1 = ndimage.morphology.binary_dilation(boolMet1, structure=struc)
                
                #Derivative mask
                derPhase = numpy.nanmean(numpy.abs(phase[:,1:,:] - phase[:,:-1,:]),axis=0)
                boolMet2 = derPhase < 0.2
#                 boolMet2 = ndimage.morphology.binary_opening(boolMet2)
#                 boolMet2 = ndimage.morphology.binary_closing(boolMet2, structure = numpy.ones((10,1)))
                boolMet2 = ndimage.median_filter(boolMet2,size=5)
                boolMet2 = numpy.vstack((boolMet2,numpy.full((1,nHeights), True, dtype=bool)))
#                 #Final mask
#                 boolMetFin = boolMet2
                boolMetFin = boolMet1&boolMet2
#                 boolMetFin = ndimage.morphology.binary_dilation(boolMetFin)
            #Creating data_param
            coordMet = numpy.where(boolMetFin)

            tmet = coordMet[0]
            hmet = coordMet[1]
            
            data_param = numpy.zeros((tmet.size, 6 + nPairs))
            data_param[:,0] = utctime
            data_param[:,1] = tmet
            data_param[:,2] = hmet
            data_param[:,3] = SNRm[tmet,hmet]
            data_param[:,4] = velRad[tmet,hmet]
            data_param[:,5] = coh[tmet,hmet]
            data_param[:,6:] = phase[:,tmet,hmet].T
        
        elif mode == 'DBS':
            self.dataOut.groupList = numpy.arange(nChannels)
            
            #Radial Velocities
#             phase = numpy.angle(data_acf[:,1,:,:])
            phase = ndimage.median_filter(numpy.angle(data_acf[:,1,:,:]), size = (1,5,1))
            velRad = phase*lamb/(4*numpy.pi*tSamp)
            
            #Spectral width
            acf1 = ndimage.median_filter(numpy.abs(data_acf[:,1,:,:]), size = (1,5,1))
            acf2 = ndimage.median_filter(numpy.abs(data_acf[:,2,:,:]), size = (1,5,1))
            
            spcWidth = (lamb/(2*numpy.sqrt(6)*numpy.pi*tSamp))*numpy.sqrt(numpy.log(acf1/acf2))
#             velRad = ndimage.median_filter(velRad, size = (1,5,1))
            if allData:
                boolMetFin = ~numpy.isnan(SNRdB)
            else:
                #SNR
                boolMet1 = (SNRdB>SNRthresh) #SNR mask
                boolMet1 = ndimage.median_filter(boolMet1, size=(1,5,5))
              
                #Radial velocity
                boolMet2 = numpy.abs(velRad) < 30
                boolMet2 = ndimage.median_filter(boolMet2, (1,5,5))
                
                #Spectral Width
                boolMet3 = spcWidth < 30
                boolMet3 = ndimage.median_filter(boolMet3, (1,5,5))
#                 boolMetFin = self.__erase_small(boolMet1, 10,5)
                boolMetFin = boolMet1&boolMet2&boolMet3
                
            #Creating data_param
            coordMet = numpy.where(boolMetFin)

            cmet = coordMet[0]
            tmet = coordMet[1]
            hmet = coordMet[2]
            
            data_param = numpy.zeros((tmet.size, 7))
            data_param[:,0] = utctime
            data_param[:,1] = cmet
            data_param[:,2] = tmet
            data_param[:,3] = hmet
            data_param[:,4] = SNR[cmet,tmet,hmet].T
            data_param[:,5] = velRad[cmet,tmet,hmet].T
            data_param[:,6] = spcWidth[cmet,tmet,hmet].T
            
#         self.dataOut.data_param = data_int
        if len(data_param) == 0:
            self.dataOut.flagNoData = True
        else:
            self.dataOut.data_param = data_param

    def __erase_small(self, binArray, threshX, threshY):
        labarray, numfeat = ndimage.measurements.label(binArray)
        binArray1 = numpy.copy(binArray)
        
        for i in range(1,numfeat + 1):
            auxBin = (labarray==i)
            auxSize = auxBin.sum()
            
            x,y = numpy.where(auxBin)
            widthX = x.max() - x.min()
            widthY = y.max() - y.min()
            
            #width X: 3 seg -> 12.5*3
            #width Y: 
            
            if (auxSize < 50) or (widthX < threshX) or (widthY < threshY):
                binArray1[auxBin] = False
            
        return binArray1

#---------------    Specular Meteor    ----------------

class SMDetection(Operation):
    '''
        Function DetectMeteors()
            Project developed with paper:
            HOLDSWORTH ET AL. 2004
            
        Input:
            self.dataOut.data_pre
        
            centerReceiverIndex:      From the channels, which is the center receiver
            
            hei_ref:                  Height reference for the Beacon signal extraction
            tauindex:
            predefinedPhaseShifts:    Predefined phase offset for the voltge signals
            
            cohDetection:             Whether to user Coherent detection or not
            cohDet_timeStep:          Coherent Detection calculation time step
            cohDet_thresh:            Coherent Detection phase threshold to correct phases
            
            noise_timeStep:           Noise calculation time step
            noise_multiple:           Noise multiple to define signal threshold
            
            multDet_timeLimit:        Multiple Detection Removal time limit in seconds
            multDet_rangeLimit:       Multiple Detection Removal range limit in km
            
            phaseThresh:              Maximum phase difference between receiver to be consider a meteor
            SNRThresh:                Minimum SNR threshold of the meteor signal to be consider a meteor 
            
            hmin:                     Minimum Height of the meteor to use it in the further wind estimations
            hmax:                     Maximum Height of the meteor to use it in the further wind estimations
            azimuth:                  Azimuth angle correction
            
        Affected:
            self.dataOut.data_param
        
        Rejection Criteria (Errors):
            0: No error; analysis OK
            1: SNR < SNR threshold
            2: angle of arrival (AOA) ambiguously determined
            3: AOA estimate not feasible
            4: Large difference in AOAs obtained from different antenna baselines
            5: echo at start or end of time series
            6: echo less than 5 examples long; too short for analysis
            7: echo rise exceeds 0.3s
            8: echo decay time less than twice rise time
            9: large power level before echo
            10: large power level after echo
            11: poor fit to amplitude for estimation of decay time
            12: poor fit to CCF phase variation for estimation of radial drift velocity
            13: height unresolvable echo: not valid height within 70 to 110 km
            14: height ambiguous echo: more then one possible height within 70 to 110 km
            15: radial drift velocity or projected horizontal velocity exceeds 200 m/s
            16: oscilatory echo, indicating event most likely not an underdense echo
            
            17: phase difference in meteor Reestimation
        
        Data Storage:
            Meteors for Wind Estimation   (8):
            Utc Time   |    Range    Height
            Azimuth    Zenith    errorCosDir
            VelRad    errorVelRad
            Phase0 Phase1 Phase2 Phase3
            TypeError
        
         ''' 
    
    def run(self, dataOut, hei_ref = None, tauindex = 0,
                      phaseOffsets = None,
                      cohDetection = False, cohDet_timeStep = 1, cohDet_thresh = 25, 
                      noise_timeStep = 4, noise_multiple = 4,
                      multDet_timeLimit = 1, multDet_rangeLimit = 3,
                      phaseThresh = 20, SNRThresh = 5,
                      hmin = 50, hmax=150, azimuth = 0,
                      channelPositions = None) :
        
           
        #Getting Pairslist
        if channelPositions == None:
#             channelPositions = [(2.5,0), (0,2.5), (0,0), (0,4.5), (-2,0)]   #T
            channelPositions = [(4.5,2), (2,4.5), (2,2), (2,0), (0,2)]   #Estrella
        meteorOps = SMOperations()
        pairslist0, distances = meteorOps.getPhasePairs(channelPositions)
        heiRang = dataOut.getHeiRange()
        #Get Beacon signal - No Beacon signal anymore
#         newheis = numpy.where(self.dataOut.heightList>self.dataOut.radarControllerHeaderObj.Taus[tauindex])
#         
#         if hei_ref != None:
#             newheis = numpy.where(self.dataOut.heightList>hei_ref)
#         
        
            
        #****************REMOVING HARDWARE PHASE DIFFERENCES***************
        # see if the user put in pre defined phase shifts
        voltsPShift = dataOut.data_pre.copy()
        
#         if predefinedPhaseShifts != None:
#             hardwarePhaseShifts = numpy.array(predefinedPhaseShifts)*numpy.pi/180
#         
# #         elif beaconPhaseShifts:
# #             #get hardware phase shifts using beacon signal
# #             hardwarePhaseShifts = self.__getHardwarePhaseDiff(self.dataOut.data_pre, pairslist, newheis, 10)
# #             hardwarePhaseShifts = numpy.insert(hardwarePhaseShifts,centerReceiverIndex,0)
#             
#         else:
#             hardwarePhaseShifts = numpy.zeros(5)                     
# 
#         voltsPShift = numpy.zeros((self.dataOut.data_pre.shape[0],self.dataOut.data_pre.shape[1],self.dataOut.data_pre.shape[2]), dtype = 'complex')
#         for i in range(self.dataOut.data_pre.shape[0]):
#             voltsPShift[i,:,:] = self.__shiftPhase(self.dataOut.data_pre[i,:,:], hardwarePhaseShifts[i])

        #******************END OF REMOVING HARDWARE PHASE DIFFERENCES*********
    
        #Remove DC
        voltsDC = numpy.mean(voltsPShift,1)
        voltsDC = numpy.mean(voltsDC,1)
        for i in range(voltsDC.shape[0]):
            voltsPShift[i] = voltsPShift[i] - voltsDC[i]
            
        #Don't considerate last heights, theyre used to calculate Hardware Phase Shift    
#         voltsPShift = voltsPShift[:,:,:newheis[0][0]]
        
        #************ FIND POWER OF DATA W/COH OR NON COH DETECTION (3.4) **********
        #Coherent Detection
        if cohDetection:
            #use coherent detection to get the net power
            cohDet_thresh = cohDet_thresh*numpy.pi/180
            voltsPShift = self.__coherentDetection(voltsPShift, cohDet_timeStep, dataOut.timeInterval, pairslist0, cohDet_thresh)
        
        #Non-coherent detection!
        powerNet = numpy.nansum(numpy.abs(voltsPShift[:,:,:])**2,0)
        #********** END OF COH/NON-COH POWER CALCULATION**********************
    
        #********** FIND THE NOISE LEVEL AND POSSIBLE METEORS ****************
        #Get noise
        noise, noise1 = self.__getNoise(powerNet, noise_timeStep, dataOut.timeInterval)
#         noise = self.getNoise1(powerNet, noise_timeStep, self.dataOut.timeInterval)
        #Get signal threshold
        signalThresh = noise_multiple*noise
        #Meteor echoes detection
        listMeteors = self.__findMeteors(powerNet, signalThresh)
        #******* END OF NOISE LEVEL AND POSSIBLE METEORS CACULATION **********
        
        #************** REMOVE MULTIPLE DETECTIONS (3.5) ***************************
        #Parameters
        heiRange = dataOut.getHeiRange()
        rangeInterval = heiRange[1] - heiRange[0]
        rangeLimit = multDet_rangeLimit/rangeInterval
        timeLimit = multDet_timeLimit/dataOut.timeInterval
        #Multiple detection removals
        listMeteors1 = self.__removeMultipleDetections(listMeteors, rangeLimit, timeLimit)
        #************ END OF REMOVE MULTIPLE DETECTIONS **********************
        
        #*********************     METEOR REESTIMATION  (3.7, 3.8, 3.9, 3.10)   ********************
        #Parameters
        phaseThresh = phaseThresh*numpy.pi/180
        thresh = [phaseThresh, noise_multiple, SNRThresh]
        #Meteor reestimation  (Errors N 1, 6, 12, 17)
        listMeteors2, listMeteorsPower, listMeteorsVolts = self.__meteorReestimation(listMeteors1, voltsPShift, pairslist0, thresh, noise, dataOut.timeInterval, dataOut.frequency)
#         listMeteors2, listMeteorsPower, listMeteorsVolts = self.meteorReestimation3(listMeteors2, listMeteorsPower, listMeteorsVolts, voltsPShift, pairslist, thresh, noise)
        #Estimation of decay times (Errors N 7, 8, 11)
        listMeteors3 = self.__estimateDecayTime(listMeteors2, listMeteorsPower, dataOut.timeInterval, dataOut.frequency)
        #*******************     END OF METEOR REESTIMATION    *******************
        
        #*********************    METEOR PARAMETERS CALCULATION (3.11, 3.12, 3.13)    **************************
        #Calculating Radial Velocity (Error N 15)
        radialStdThresh = 10
        listMeteors4 = self.__getRadialVelocity(listMeteors3, listMeteorsVolts, radialStdThresh, pairslist0, dataOut.timeInterval)    

        if len(listMeteors4) > 0:
            #Setting New Array
            date = dataOut.utctime
            arrayParameters = self.__setNewArrays(listMeteors4, date, heiRang)
            
            #Correcting phase offset
            if phaseOffsets != None:
                phaseOffsets = numpy.array(phaseOffsets)*numpy.pi/180
                arrayParameters[:,8:12] = numpy.unwrap(arrayParameters[:,8:12] + phaseOffsets)
            
            #Second Pairslist
            pairsList = []
            pairx = (0,1)
            pairy = (2,3)
            pairsList.append(pairx)
            pairsList.append(pairy)
            
            jph = numpy.array([0,0,0,0])
            h = (hmin,hmax)
            arrayParameters = meteorOps.getMeteorParams(arrayParameters, azimuth, h, pairsList, distances, jph)
            
#             #Calculate AOA (Error N 3, 4)
#             #JONES ET AL. 1998
#             error = arrayParameters[:,-1]
#             AOAthresh = numpy.pi/8
#             phases = -arrayParameters[:,9:13]
#             arrayParameters[:,4:7], arrayParameters[:,-1] = meteorOps.getAOA(phases, pairsList, error, AOAthresh, azimuth)
#             
#             #Calculate Heights (Error N 13 and 14)
#             error = arrayParameters[:,-1]
#             Ranges = arrayParameters[:,2]
#             zenith = arrayParameters[:,5]
#             arrayParameters[:,3], arrayParameters[:,-1] = meteorOps.getHeights(Ranges, zenith, error, hmin, hmax)
#             error = arrayParameters[:,-1]
        #*********************    END OF PARAMETERS CALCULATION    **************************
                
        #***************************+     PASS DATA TO NEXT STEP    **********************                       
#             arrayFinal = arrayParameters.reshape((1,arrayParameters.shape[0],arrayParameters.shape[1]))
            dataOut.data_param = arrayParameters
            
            if arrayParameters == None:
                dataOut.flagNoData = True
        else:
            dataOut.flagNoData = True
            
        return
        
    def __getHardwarePhaseDiff(self, voltage0, pairslist, newheis, n):
           
        minIndex = min(newheis[0])
        maxIndex = max(newheis[0])
        
        voltage = voltage0[:,:,minIndex:maxIndex+1]
        nLength = voltage.shape[1]/n
        nMin = 0
        nMax = 0
        phaseOffset = numpy.zeros((len(pairslist),n))
        
        for i in range(n):
            nMax += nLength
            phaseCCF = -numpy.angle(self.__calculateCCF(voltage[:,nMin:nMax,:], pairslist, [0]))
            phaseCCF = numpy.mean(phaseCCF, axis = 2)
            phaseOffset[:,i] = phaseCCF.transpose() 
            nMin = nMax
#         phaseDiff, phaseArrival = self.estimatePhaseDifference(voltage, pairslist)
        
        #Remove Outliers
        factor = 2
        wt = phaseOffset - signal.medfilt(phaseOffset,(1,5))
        dw = numpy.std(wt,axis = 1)
        dw = dw.reshape((dw.size,1))
        ind = numpy.where(numpy.logical_or(wt>dw*factor,wt<-dw*factor)) 
        phaseOffset[ind] = numpy.nan
        phaseOffset = stats.nanmean(phaseOffset, axis=1) 
        
        return phaseOffset
    
    def __shiftPhase(self, data, phaseShift):
        #this will shift the phase of a complex number
        dataShifted = numpy.abs(data) * numpy.exp((numpy.angle(data)+phaseShift)*1j)   
        return dataShifted
    
    def __estimatePhaseDifference(self, array, pairslist):
        nChannel = array.shape[0]
        nHeights = array.shape[2]
        numPairs = len(pairslist)
#         phaseCCF = numpy.zeros((nChannel, 5, nHeights))
        phaseCCF = numpy.angle(self.__calculateCCF(array, pairslist, [-2,-1,0,1,2]))
        
        #Correct phases
        derPhaseCCF = phaseCCF[:,1:,:] - phaseCCF[:,0:-1,:]
        indDer = numpy.where(numpy.abs(derPhaseCCF) > numpy.pi)
        
        if indDer[0].shape[0] > 0:  
            for i in range(indDer[0].shape[0]):
                signo = -numpy.sign(derPhaseCCF[indDer[0][i],indDer[1][i],indDer[2][i]])
                phaseCCF[indDer[0][i],indDer[1][i]+1:,:] += signo*2*numpy.pi
    
#         for j in range(numSides):
#             phaseCCFAux = self.calculateCCF(arrayCenter, arraySides[j,:,:], [-2,1,0,1,2])
#             phaseCCF[j,:,:] = numpy.angle(phaseCCFAux)
#             
        #Linear
        phaseInt = numpy.zeros((numPairs,1))
        angAllCCF = phaseCCF[:,[0,1,3,4],0]
        for j in range(numPairs):
            fit = stats.linregress([-2,-1,1,2],angAllCCF[j,:])
            phaseInt[j] = fit[1]
        #Phase Differences
        phaseDiff = phaseInt - phaseCCF[:,2,:]
        phaseArrival = phaseInt.reshape(phaseInt.size)
        
        #Dealias
        phaseArrival = numpy.angle(numpy.exp(1j*phaseArrival))
#         indAlias = numpy.where(phaseArrival > numpy.pi)
#         phaseArrival[indAlias] -= 2*numpy.pi
#         indAlias = numpy.where(phaseArrival < -numpy.pi)
#         phaseArrival[indAlias] += 2*numpy.pi
        
        return phaseDiff, phaseArrival
    
    def __coherentDetection(self, volts, timeSegment, timeInterval, pairslist, thresh):
        #this function will run the coherent detection used in Holdworth et al. 2004 and return the net power
        #find the phase shifts of each channel over 1 second intervals
        #only look at ranges below the beacon signal
        numProfPerBlock = numpy.ceil(timeSegment/timeInterval)
        numBlocks = int(volts.shape[1]/numProfPerBlock)
        numHeights = volts.shape[2]
        nChannel = volts.shape[0]
        voltsCohDet = volts.copy()
        
        pairsarray = numpy.array(pairslist)
        indSides = pairsarray[:,1]
#         indSides = numpy.array(range(nChannel))
#         indSides = numpy.delete(indSides, indCenter)
#         
#         listCenter = numpy.array_split(volts[indCenter,:,:], numBlocks, 0)
        listBlocks = numpy.array_split(volts, numBlocks, 1)
        
        startInd = 0
        endInd = 0
            
        for i in range(numBlocks):
            startInd = endInd
            endInd = endInd + listBlocks[i].shape[1]   
            
            arrayBlock = listBlocks[i]
#             arrayBlockCenter = listCenter[i]
            
            #Estimate the Phase Difference
            phaseDiff, aux = self.__estimatePhaseDifference(arrayBlock, pairslist)
            #Phase Difference RMS
            arrayPhaseRMS = numpy.abs(phaseDiff)
            phaseRMSaux = numpy.sum(arrayPhaseRMS < thresh,0)
            indPhase = numpy.where(phaseRMSaux==4)
            #Shifting
            if indPhase[0].shape[0] > 0:
                for j in range(indSides.size):
                    arrayBlock[indSides[j],:,indPhase] = self.__shiftPhase(arrayBlock[indSides[j],:,indPhase], phaseDiff[j,indPhase].transpose())
                voltsCohDet[:,startInd:endInd,:] = arrayBlock
         
        return voltsCohDet
   
    def __calculateCCF(self, volts, pairslist ,laglist):
        
        nHeights = volts.shape[2]
        nPoints = volts.shape[1] 
        voltsCCF = numpy.zeros((len(pairslist), len(laglist), nHeights),dtype = 'complex')
        
        for i in range(len(pairslist)):
            volts1 = volts[pairslist[i][0]]
            volts2 = volts[pairslist[i][1]]   
            
            for t in range(len(laglist)):
                idxT = laglist[t]                     
                if idxT >= 0:
                    vStacked = numpy.vstack((volts2[idxT:,:],
                                           numpy.zeros((idxT, nHeights),dtype='complex')))
                else:
                    vStacked = numpy.vstack((numpy.zeros((-idxT, nHeights),dtype='complex'),
                                           volts2[:(nPoints + idxT),:]))
                voltsCCF[i,t,:] = numpy.sum((numpy.conjugate(volts1)*vStacked),axis=0)
    
                vStacked = None
        return voltsCCF
        
    def __getNoise(self, power, timeSegment, timeInterval):
        numProfPerBlock = numpy.ceil(timeSegment/timeInterval)
        numBlocks = int(power.shape[0]/numProfPerBlock)
        numHeights = power.shape[1]

        listPower = numpy.array_split(power, numBlocks, 0)
        noise = numpy.zeros((power.shape[0], power.shape[1]))
        noise1 = numpy.zeros((power.shape[0], power.shape[1]))
        
        startInd = 0
        endInd = 0
        
        for i in range(numBlocks):             #split por canal
            startInd = endInd
            endInd = endInd + listPower[i].shape[0]  
            
            arrayBlock = listPower[i]
            noiseAux = numpy.mean(arrayBlock, 0)
#             noiseAux = numpy.median(noiseAux)
#             noiseAux = numpy.mean(arrayBlock)
            noise[startInd:endInd,:] = noise[startInd:endInd,:] + noiseAux 
            
            noiseAux1 = numpy.mean(arrayBlock)
            noise1[startInd:endInd,:] = noise1[startInd:endInd,:] + noiseAux1 
            
        return noise, noise1
      
    def __findMeteors(self, power, thresh):
        nProf = power.shape[0]
        nHeights = power.shape[1]
        listMeteors = []
        
        for i in range(nHeights):
            powerAux = power[:,i]
            threshAux = thresh[:,i]
            
            indUPthresh = numpy.where(powerAux > threshAux)[0]
            indDNthresh = numpy.where(powerAux <= threshAux)[0]
            
            j = 0
            
            while (j < indUPthresh.size - 2):
                if (indUPthresh[j + 2] == indUPthresh[j] + 2):
                    indDNAux = numpy.where(indDNthresh > indUPthresh[j])
                    indDNthresh = indDNthresh[indDNAux]
                    
                    if (indDNthresh.size > 0):
                        indEnd = indDNthresh[0] - 1
                        indInit = indUPthresh[j]
                        
                        meteor = powerAux[indInit:indEnd + 1]
                        indPeak = meteor.argmax() + indInit
                        FLA = sum(numpy.conj(meteor)*numpy.hstack((meteor[1:],0)))
                        
                        listMeteors.append(numpy.array([i,indInit,indPeak,indEnd,FLA])) #CHEQUEAR!!!!!
                        j = numpy.where(indUPthresh == indEnd)[0] + 1
                    else: j+=1
                else: j+=1
                    
        return listMeteors
    
    def __removeMultipleDetections(self,listMeteors, rangeLimit, timeLimit):
        
        arrayMeteors = numpy.asarray(listMeteors) 
        listMeteors1 = []
        
        while arrayMeteors.shape[0] > 0:
            FLAs = arrayMeteors[:,4]
            maxFLA = FLAs.argmax()
            listMeteors1.append(arrayMeteors[maxFLA,:])
            
            MeteorInitTime = arrayMeteors[maxFLA,1]
            MeteorEndTime = arrayMeteors[maxFLA,3]
            MeteorHeight = arrayMeteors[maxFLA,0]
            
            #Check neighborhood
            maxHeightIndex = MeteorHeight + rangeLimit
            minHeightIndex = MeteorHeight - rangeLimit
            minTimeIndex = MeteorInitTime - timeLimit
            maxTimeIndex = MeteorEndTime + timeLimit
            
            #Check Heights
            indHeight = numpy.logical_and(arrayMeteors[:,0] >= minHeightIndex, arrayMeteors[:,0] <= maxHeightIndex)
            indTime = numpy.logical_and(arrayMeteors[:,3] >= minTimeIndex, arrayMeteors[:,1] <= maxTimeIndex)
            indBoth = numpy.where(numpy.logical_and(indTime,indHeight))
            
            arrayMeteors = numpy.delete(arrayMeteors, indBoth, axis = 0)
        
        return listMeteors1
    
    def __meteorReestimation(self, listMeteors, volts, pairslist, thresh, noise, timeInterval,frequency):
        numHeights = volts.shape[2]
        nChannel = volts.shape[0]
        
        thresholdPhase = thresh[0]
        thresholdNoise = thresh[1]
        thresholdDB = float(thresh[2])
        
        thresholdDB1 = 10**(thresholdDB/10)
        pairsarray = numpy.array(pairslist)
        indSides = pairsarray[:,1]
        
        pairslist1 = list(pairslist)
        pairslist1.append((0,1))
        pairslist1.append((3,4))

        listMeteors1 = []
        listPowerSeries = []
        listVoltageSeries = []
        #volts has the war data
        
        if frequency == 30e6:
            timeLag = 45*10**-3
        else:
            timeLag = 15*10**-3
        lag = numpy.ceil(timeLag/timeInterval)
        
        for i in range(len(listMeteors)):
            
            ######################   3.6 - 3.7 PARAMETERS REESTIMATION    #########################
            meteorAux = numpy.zeros(16)
            
            #Loading meteor Data (mHeight, mStart, mPeak, mEnd)
            mHeight = listMeteors[i][0]
            mStart = listMeteors[i][1]
            mPeak = listMeteors[i][2]
            mEnd = listMeteors[i][3]
            
            #get the volt data between the start and end times of the meteor
            meteorVolts = volts[:,mStart:mEnd+1,mHeight]
            meteorVolts = meteorVolts.reshape(meteorVolts.shape[0], meteorVolts.shape[1], 1)
            
            #3.6. Phase Difference estimation
            phaseDiff, aux = self.__estimatePhaseDifference(meteorVolts, pairslist)
            
            #3.7. Phase difference removal & meteor start, peak and end times reestimated
            #meteorVolts0.- all Channels, all Profiles
            meteorVolts0 = volts[:,:,mHeight]
            meteorThresh = noise[:,mHeight]*thresholdNoise
            meteorNoise = noise[:,mHeight]
            meteorVolts0[indSides,:] = self.__shiftPhase(meteorVolts0[indSides,:], phaseDiff) #Phase Shifting
            powerNet0 = numpy.nansum(numpy.abs(meteorVolts0)**2, axis = 0)  #Power
            
            #Times reestimation
            mStart1 = numpy.where(powerNet0[:mPeak] < meteorThresh[:mPeak])[0]
            if mStart1.size > 0:
                mStart1 = mStart1[-1] + 1
                
            else: 
                mStart1 = mPeak
                
            mEnd1 = numpy.where(powerNet0[mPeak:] < meteorThresh[mPeak:])[0][0] + mPeak - 1
            mEndDecayTime1 = numpy.where(powerNet0[mPeak:] < meteorNoise[mPeak:])[0]
            if mEndDecayTime1.size == 0:
                mEndDecayTime1 = powerNet0.size
            else:
                mEndDecayTime1 = mEndDecayTime1[0] + mPeak - 1
#             mPeak1 = meteorVolts0[mStart1:mEnd1 + 1].argmax()
            
            #meteorVolts1.- all Channels, from start to end
            meteorVolts1 = meteorVolts0[:,mStart1:mEnd1 + 1]
            meteorVolts2 = meteorVolts0[:,mPeak + lag:mEnd1 + 1]
            if meteorVolts2.shape[1] == 0:
                meteorVolts2 = meteorVolts0[:,mPeak:mEnd1 + 1]
            meteorVolts1 = meteorVolts1.reshape(meteorVolts1.shape[0], meteorVolts1.shape[1], 1)
            meteorVolts2 = meteorVolts2.reshape(meteorVolts2.shape[0], meteorVolts2.shape[1], 1)
            #####################    END PARAMETERS REESTIMATION    #########################
            
            #####################   3.8 PHASE DIFFERENCE REESTIMATION  ########################
#             if mEnd1 - mStart1 > 4:       #Error Number 6: echo less than 5 samples long; too short for analysis
            if meteorVolts2.shape[1] > 0:        
                #Phase Difference re-estimation
                phaseDiff1, phaseDiffint = self.__estimatePhaseDifference(meteorVolts2, pairslist1)   #Phase Difference Estimation
#                 phaseDiff1, phaseDiffint = self.estimatePhaseDifference(meteorVolts2, pairslist)
                meteorVolts2 = meteorVolts2.reshape(meteorVolts2.shape[0], meteorVolts2.shape[1])
                phaseDiff11 = numpy.reshape(phaseDiff1, (phaseDiff1.shape[0],1))
                meteorVolts2[indSides,:] = self.__shiftPhase(meteorVolts2[indSides,:], phaseDiff11[0:4])     #Phase Shifting
                
                #Phase Difference RMS
                phaseRMS1 = numpy.sqrt(numpy.mean(numpy.square(phaseDiff1)))
                powerNet1 = numpy.nansum(numpy.abs(meteorVolts1[:,:])**2,0)
                #Data from Meteor
                mPeak1 = powerNet1.argmax() + mStart1
                mPeakPower1 = powerNet1.max()
                noiseAux = sum(noise[mStart1:mEnd1 + 1,mHeight])
                mSNR1 = (sum(powerNet1)-noiseAux)/noiseAux
                Meteor1 = numpy.array([mHeight, mStart1, mPeak1, mEnd1, mPeakPower1, mSNR1, phaseRMS1])
                Meteor1 = numpy.hstack((Meteor1,phaseDiffint))
                PowerSeries  = powerNet0[mStart1:mEndDecayTime1 + 1]
                #Vectorize
                meteorAux[0:7] = [mHeight, mStart1, mPeak1, mEnd1, mPeakPower1, mSNR1, phaseRMS1]
                meteorAux[7:11] = phaseDiffint[0:4]
                
                #Rejection Criterions
                if phaseRMS1 > thresholdPhase:  #Error Number 17: Phase variation
                    meteorAux[-1] = 17
                elif mSNR1 < thresholdDB1:      #Error Number 1: SNR < threshold dB
                    meteorAux[-1] = 1
                
            
            else:       
                meteorAux[0:4] = [mHeight, mStart, mPeak, mEnd]
                meteorAux[-1] = 6 #Error Number 6: echo less than 5 samples long; too short for analysis
                PowerSeries = 0
                    
            listMeteors1.append(meteorAux)
            listPowerSeries.append(PowerSeries)
            listVoltageSeries.append(meteorVolts1)
                      
        return listMeteors1, listPowerSeries, listVoltageSeries       
         
    def __estimateDecayTime(self, listMeteors, listPower, timeInterval, frequency):
        
        threshError = 10
        #Depending if it is 30 or 50 MHz
        if frequency == 30e6:
            timeLag = 45*10**-3
        else:
            timeLag = 15*10**-3
        lag = numpy.ceil(timeLag/timeInterval)
        
        listMeteors1 = []
        
        for i in range(len(listMeteors)):
            meteorPower = listPower[i]
            meteorAux = listMeteors[i]
            
            if meteorAux[-1] == 0:

                try:                    
                    indmax = meteorPower.argmax()
                    indlag = indmax + lag
                    
                    y = meteorPower[indlag:]
                    x = numpy.arange(0, y.size)*timeLag
                    
                    #first guess
                    a = y[0]
                    tau = timeLag
                    #exponential fit
                    popt, pcov = optimize.curve_fit(self.__exponential_function, x, y, p0 = [a, tau])
                    y1 = self.__exponential_function(x, *popt)
                    #error estimation
                    error = sum((y - y1)**2)/(numpy.var(y)*(y.size - popt.size))
                    
                    decayTime = popt[1]
                    riseTime = indmax*timeInterval
                    meteorAux[11:13] = [decayTime, error]
                    
                    #Table items 7, 8 and 11
                    if (riseTime > 0.3):            #Number 7: Echo rise exceeds 0.3s
                        meteorAux[-1] = 7 
                    elif (decayTime < 2*riseTime) : #Number 8: Echo decay time less than than twice rise time
                        meteorAux[-1] = 8
                    if (error > threshError):       #Number 11: Poor fit to amplitude for estimation of decay time
                        meteorAux[-1] = 11   
                    
                   
                except:
                    meteorAux[-1] = 11 
                
            
            listMeteors1.append(meteorAux)
        
        return listMeteors1

    #Exponential Function

    def __exponential_function(self, x, a, tau):
        y = a*numpy.exp(-x/tau)
        return y
    
    def __getRadialVelocity(self, listMeteors, listVolts, radialStdThresh, pairslist,  timeInterval):
        
        pairslist1 = list(pairslist)
        pairslist1.append((0,1))
        pairslist1.append((3,4))
        numPairs = len(pairslist1)
        #Time Lag
        timeLag = 45*10**-3
        c = 3e8
        lag = numpy.ceil(timeLag/timeInterval)
        freq = 30e6
        
        listMeteors1 = []
        
        for i in range(len(listMeteors)):
            meteorAux = listMeteors[i]
            if meteorAux[-1] == 0:
                mStart = listMeteors[i][1]
                mPeak = listMeteors[i][2]         
                mLag = mPeak - mStart + lag
                
                #get the volt data between the start and end times of the meteor
                meteorVolts = listVolts[i]
                meteorVolts = meteorVolts.reshape(meteorVolts.shape[0], meteorVolts.shape[1], 1)

                #Get CCF
                allCCFs = self.__calculateCCF(meteorVolts, pairslist1, [-2,-1,0,1,2])
                
                #Method 2
                slopes = numpy.zeros(numPairs)
                time = numpy.array([-2,-1,1,2])*timeInterval
                angAllCCF = numpy.angle(allCCFs[:,[0,1,3,4],0])
                
                #Correct phases
                derPhaseCCF = angAllCCF[:,1:] - angAllCCF[:,0:-1]
                indDer = numpy.where(numpy.abs(derPhaseCCF) > numpy.pi)
                
                if indDer[0].shape[0] > 0:  
                    for i in range(indDer[0].shape[0]):
                        signo = -numpy.sign(derPhaseCCF[indDer[0][i],indDer[1][i]])
                        angAllCCF[indDer[0][i],indDer[1][i]+1:] += signo*2*numpy.pi

#                     fit = scipy.stats.linregress(numpy.array([-2,-1,1,2])*timeInterval, numpy.array([phaseLagN2s[i],phaseLagN1s[i],phaseLag1s[i],phaseLag2s[i]]))
                for j in range(numPairs):
                    fit = stats.linregress(time, angAllCCF[j,:])
                    slopes[j] = fit[0]
                
                #Remove Outlier
#                 indOut = numpy.argmax(numpy.abs(slopes - numpy.mean(slopes)))
#                 slopes = numpy.delete(slopes,indOut)
#                 indOut = numpy.argmax(numpy.abs(slopes - numpy.mean(slopes)))
#                 slopes = numpy.delete(slopes,indOut)
                   
                radialVelocity = -numpy.mean(slopes)*(0.25/numpy.pi)*(c/freq)
                radialError = numpy.std(slopes)*(0.25/numpy.pi)*(c/freq)
                meteorAux[-2] = radialError
                meteorAux[-3] = radialVelocity
                
                #Setting Error
                #Number 15: Radial Drift velocity or projected horizontal velocity exceeds 200 m/s
                if numpy.abs(radialVelocity) > 200: 
                    meteorAux[-1] = 15
                #Number 12: Poor fit to CCF variation for estimation of radial drift velocity
                elif radialError > radialStdThresh:
                    meteorAux[-1] = 12
                
            listMeteors1.append(meteorAux)
        return listMeteors1
    
    def __setNewArrays(self, listMeteors, date, heiRang):
        
        #New arrays
        arrayMeteors = numpy.array(listMeteors)
        arrayParameters = numpy.zeros((len(listMeteors), 13))
        
        #Date inclusion
#         date = re.findall(r'\((.*?)\)', date)
#         date = date[0].split(',')
#         date = map(int, date)
#         
#         if len(date)<6:
#             date.append(0)
#             
#         date = [date[0]*10000 + date[1]*100 + date[2], date[3]*10000 + date[4]*100 + date[5]]
#         arrayDate = numpy.tile(date, (len(listMeteors), 1))
        arrayDate = numpy.tile(date, (len(listMeteors)))
        
        #Meteor array
#         arrayMeteors[:,0] = heiRang[arrayMeteors[:,0].astype(int)]
#         arrayMeteors = numpy.hstack((arrayDate, arrayMeteors))
        
        #Parameters Array
        arrayParameters[:,0] = arrayDate #Date
        arrayParameters[:,1] = heiRang[arrayMeteors[:,0].astype(int)] #Range
        arrayParameters[:,6:8] = arrayMeteors[:,-3:-1] #Radial velocity and its error
        arrayParameters[:,8:12] = arrayMeteors[:,7:11]  #Phases
        arrayParameters[:,-1] = arrayMeteors[:,-1]  #Error

        
        return arrayParameters
           
class CorrectSMPhases(Operation):
    
    def run(self, dataOut, phaseOffsets, hmin = 50, hmax = 150, azimuth = 45, channelPositions = None):
    
        arrayParameters = dataOut.data_param
        pairsList = []
        pairx = (0,1)
        pairy = (2,3)
        pairsList.append(pairx)
        pairsList.append(pairy)
        jph = numpy.zeros(4)
        
        phaseOffsets = numpy.array(phaseOffsets)*numpy.pi/180
    #         arrayParameters[:,8:12] = numpy.unwrap(arrayParameters[:,8:12] + phaseOffsets)
        arrayParameters[:,8:12] = numpy.angle(numpy.exp(1j*(arrayParameters[:,8:12] + phaseOffsets)))
        
        meteorOps = SMOperations()
        if channelPositions == None:
    #             channelPositions = [(2.5,0), (0,2.5), (0,0), (0,4.5), (-2,0)]   #T
            channelPositions = [(4.5,2), (2,4.5), (2,2), (2,0), (0,2)]   #Estrella
    
        pairslist0, distances = meteorOps.getPhasePairs(channelPositions)
        h = (hmin,hmax)
    
        arrayParameters = meteorOps.getMeteorParams(arrayParameters, azimuth, h, pairsList, distances, jph)
        
        dataOut.data_param = arrayParameters
        return

class SMPhaseCalibration(Operation):
    
    __buffer = None

    __initime = None

    __dataReady = False
    
    __isConfig = False
    
    def __checkTime(self, currentTime, initTime, paramInterval, outputInterval):
        
        dataTime = currentTime + paramInterval
        deltaTime = dataTime - initTime
        
        if deltaTime >= outputInterval or deltaTime < 0:
            return True
        
        return False
    
    def __getGammas(self, pairs, d, phases):
        gammas = numpy.zeros(2)
    
        for i in range(len(pairs)):
     
            pairi = pairs[i]
            
            phip3 = phases[:,pairi[1]]
            d3 = d[pairi[1]]
            phip2 = phases[:,pairi[0]]
            d2 = d[pairi[0]]
            #Calculating gamma
#             jdcos = alp1/(k*d1)
#             jgamma = numpy.angle(numpy.exp(1j*(d0*alp1/d1 - alp0)))
            jgamma = -phip2*d3/d2 - phip3
            jgamma = numpy.angle(numpy.exp(1j*jgamma))
#             jgamma[jgamma>numpy.pi] -= 2*numpy.pi
#             jgamma[jgamma<-numpy.pi] += 2*numpy.pi
            
            #Revised distribution
            jgammaArray = numpy.hstack((jgamma,jgamma+0.5*numpy.pi,jgamma-0.5*numpy.pi))

            #Histogram
            nBins = 64.0
            rmin = -0.5*numpy.pi
            rmax = 0.5*numpy.pi
            phaseHisto = numpy.histogram(jgammaArray, bins=nBins, range=(rmin,rmax))
        
            meteorsY = phaseHisto[0]
            phasesX = phaseHisto[1][:-1]
            width = phasesX[1] - phasesX[0]
            phasesX += width/2
            
            #Gaussian aproximation
            bpeak = meteorsY.argmax()
            peak = meteorsY.max()
            jmin = bpeak - 5
            jmax = bpeak + 5 + 1
            
            if jmin<0:
                jmin = 0
                jmax = 6
            elif jmax > meteorsY.size:
                jmin = meteorsY.size - 6
                jmax = meteorsY.size
            
            x0 = numpy.array([peak,bpeak,50])
            coeff = optimize.leastsq(self.__residualFunction, x0, args=(meteorsY[jmin:jmax], phasesX[jmin:jmax]))
            
            #Gammas
            gammas[i] = coeff[0][1]
        
        return gammas
    
    def __residualFunction(self, coeffs, y, t):
    
        return y - self.__gauss_function(t, coeffs)

    def __gauss_function(self, t, coeffs):
    
        return coeffs[0]*numpy.exp(-0.5*((t - coeffs[1]) / coeffs[2])**2)

    def __getPhases(self, azimuth, h, pairsList, d, gammas, meteorsArray):
        meteorOps = SMOperations()
        nchan = 4
        pairx = pairsList[0]
        pairy = pairsList[1]
        center_xangle = 0
        center_yangle = 0
        range_angle = numpy.array([10*numpy.pi,numpy.pi,numpy.pi/2,numpy.pi/4])
        ntimes = len(range_angle)
        
        nstepsx = 20.0
        nstepsy = 20.0
        
        for iz in range(ntimes):
            min_xangle = -range_angle[iz]/2 + center_xangle
            max_xangle = range_angle[iz]/2 + center_xangle
            min_yangle = -range_angle[iz]/2 + center_yangle
            max_yangle = range_angle[iz]/2 + center_yangle
        
            inc_x = (max_xangle-min_xangle)/nstepsx
            inc_y = (max_yangle-min_yangle)/nstepsy
             
            alpha_y = numpy.arange(nstepsy)*inc_y + min_yangle
            alpha_x = numpy.arange(nstepsx)*inc_x + min_xangle
            penalty = numpy.zeros((nstepsx,nstepsy))
            jph_array = numpy.zeros((nchan,nstepsx,nstepsy))
            jph = numpy.zeros(nchan)
             
            # Iterations looking for the offset
            for iy in range(int(nstepsy)):
                for ix in range(int(nstepsx)):
                    jph[pairy[1]] = alpha_y[iy]
                    jph[pairy[0]] = -gammas[1] - alpha_y[iy]*d[pairy[1]]/d[pairy[0]] 
                       
                    jph[pairx[1]] = alpha_x[ix]
                    jph[pairx[0]] = -gammas[0] - alpha_x[ix]*d[pairx[1]]/d[pairx[0]]
                        
                    jph_array[:,ix,iy] = jph
                        
                    meteorsArray1 = meteorOps.getMeteorParams(meteorsArray, azimuth, h, pairsList, d, jph)
                    error = meteorsArray1[:,-1]
                    ind1 = numpy.where(error==0)[0]
                    penalty[ix,iy] = ind1.size
             
            i,j = numpy.unravel_index(penalty.argmax(), penalty.shape)
            phOffset = jph_array[:,i,j]
        
            center_xangle = phOffset[pairx[1]]
            center_yangle = phOffset[pairy[1]]
        
        phOffset = numpy.angle(numpy.exp(1j*jph_array[:,i,j]))
        phOffset = phOffset*180/numpy.pi        
        return phOffset
            
       
    def run(self, dataOut, hmin, hmax, channelPositions=None, nHours = 1):
        
        dataOut.flagNoData = True
        self.__dataReady = False                             
        dataOut.outputInterval = nHours*3600
        
        if self.__isConfig == False:
#                 self.__initime = dataOut.datatime.replace(minute = 0, second = 0, microsecond = 03)
            #Get Initial LTC time
            self.__initime = datetime.datetime.utcfromtimestamp(dataOut.utctime)
            self.__initime = (self.__initime.replace(minute = 0, second = 0, microsecond = 0) - datetime.datetime(1970, 1, 1)).total_seconds()

            self.__isConfig = True
            
        if self.__buffer == None:
            self.__buffer = dataOut.data_param.copy()

        else:
            self.__buffer = numpy.vstack((self.__buffer, dataOut.data_param))
        
        self.__dataReady = self.__checkTime(dataOut.utctime, self.__initime, dataOut.paramInterval, dataOut.outputInterval) #Check if the buffer is ready
        
        if self.__dataReady:
            dataOut.utctimeInit = self.__initime
            self.__initime += dataOut.outputInterval #to erase time offset
            
            freq = dataOut.frequency
            c = dataOut.C #m/s
            lamb = c/freq
            k = 2*numpy.pi/lamb
            azimuth = 0
            h = (hmin, hmax)
            pairs = ((0,1),(2,3))
            
            if channelPositions == None:
#             channelPositions = [(2.5,0), (0,2.5), (0,0), (0,4.5), (-2,0)]   #T
                channelPositions = [(4.5,2), (2,4.5), (2,2), (2,0), (0,2)]   #Estrella
            meteorOps = SMOperations()
            pairslist0, distances = meteorOps.getPhasePairs(channelPositions)
        
#             distances1 = [-distances[0]*lamb, distances[1]*lamb, -distances[2]*lamb, distances[3]*lamb]
            
            meteorsArray = self.__buffer
            error = meteorsArray[:,-1]
            boolError = (error==0)|(error==3)|(error==4)|(error==13)|(error==14)
            ind1 = numpy.where(boolError)[0]
            meteorsArray = meteorsArray[ind1,:]
            meteorsArray[:,-1] = 0
            phases = meteorsArray[:,8:12]
            
            #Calculate Gammas
            gammas = self.__getGammas(pairs, distances, phases)
#             gammas = numpy.array([-21.70409463,45.76935864])*numpy.pi/180
            #Calculate Phases
            phasesOff = self.__getPhases(azimuth, h, pairs, distances, gammas, meteorsArray)
            phasesOff = phasesOff.reshape((1,phasesOff.size))
            dataOut.data_output = -phasesOff
            dataOut.flagNoData = False
            self.__buffer = None
        
        
        return
    
class SMOperations():
    
    def __init__(self):
        
        return
    
    def getMeteorParams(self, arrayParameters0, azimuth, h, pairsList, distances, jph):
        
        arrayParameters = arrayParameters0.copy()
        hmin = h[0]
        hmax = h[1]
                
        #Calculate AOA (Error N 3, 4)
        #JONES ET AL. 1998
        AOAthresh = numpy.pi/8
        error = arrayParameters[:,-1]
        phases = -arrayParameters[:,8:12] + jph
#         phases = numpy.unwrap(phases)
        arrayParameters[:,3:6], arrayParameters[:,-1] = self.__getAOA(phases, pairsList, distances, error, AOAthresh, azimuth)
        
        #Calculate Heights (Error N 13 and 14)
        error = arrayParameters[:,-1]
        Ranges = arrayParameters[:,1]
        zenith = arrayParameters[:,4]
        arrayParameters[:,2], arrayParameters[:,-1] = self.__getHeights(Ranges, zenith, error, hmin, hmax)
        
        #----------------------- Get Final data    ------------------------------------
#         error = arrayParameters[:,-1]
#         ind1 = numpy.where(error==0)[0]
#         arrayParameters = arrayParameters[ind1,:]
        
        return arrayParameters
    
    def __getAOA(self, phases, pairsList, directions, error, AOAthresh, azimuth):
        
        arrayAOA = numpy.zeros((phases.shape[0],3))
        cosdir0, cosdir = self.__getDirectionCosines(phases, pairsList,directions)
        
        arrayAOA[:,:2] = self.__calculateAOA(cosdir, azimuth)
        cosDirError = numpy.sum(numpy.abs(cosdir0 - cosdir), axis = 1)
        arrayAOA[:,2] = cosDirError
        
        azimuthAngle = arrayAOA[:,0]
        zenithAngle = arrayAOA[:,1]
        
        #Setting Error
        indError = numpy.where(numpy.logical_or(error == 3, error == 4))[0]
        error[indError] = 0
        #Number 3: AOA not fesible
        indInvalid = numpy.where(numpy.logical_and((numpy.logical_or(numpy.isnan(zenithAngle), numpy.isnan(azimuthAngle))),error == 0))[0]
        error[indInvalid] = 3 
        #Number 4: Large difference in AOAs obtained from different antenna baselines
        indInvalid = numpy.where(numpy.logical_and(cosDirError > AOAthresh,error == 0))[0]
        error[indInvalid] = 4 
        return arrayAOA, error
    
    def __getDirectionCosines(self, arrayPhase, pairsList, distances):
    
        #Initializing some variables
        ang_aux = numpy.array([-8,-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,8])*2*numpy.pi
        ang_aux = ang_aux.reshape(1,ang_aux.size)
        
        cosdir = numpy.zeros((arrayPhase.shape[0],2))
        cosdir0 = numpy.zeros((arrayPhase.shape[0],2))
        
        
        for i in range(2):
            ph0 = arrayPhase[:,pairsList[i][0]]
            ph1 = arrayPhase[:,pairsList[i][1]]
            d0 = distances[pairsList[i][0]]
            d1 = distances[pairsList[i][1]]
            
            ph0_aux = ph0 + ph1 
            ph0_aux = numpy.angle(numpy.exp(1j*ph0_aux))
#             ph0_aux[ph0_aux > numpy.pi] -= 2*numpy.pi
#             ph0_aux[ph0_aux < -numpy.pi] += 2*numpy.pi 
            #First Estimation
            cosdir0[:,i] = (ph0_aux)/(2*numpy.pi*(d0 - d1))
        
            #Most-Accurate Second Estimation
            phi1_aux =  ph0 - ph1
            phi1_aux = phi1_aux.reshape(phi1_aux.size,1)
            #Direction Cosine 1
            cosdir1 = (phi1_aux + ang_aux)/(2*numpy.pi*(d0 + d1))
            
            #Searching the correct Direction Cosine
            cosdir0_aux = cosdir0[:,i]
            cosdir0_aux = cosdir0_aux.reshape(cosdir0_aux.size,1)
            #Minimum Distance
            cosDiff = (cosdir1 - cosdir0_aux)**2
            indcos = cosDiff.argmin(axis = 1)
            #Saving Value obtained
            cosdir[:,i] = cosdir1[numpy.arange(len(indcos)),indcos]
            
        return cosdir0, cosdir
    
    def __calculateAOA(self, cosdir, azimuth):
        cosdirX = cosdir[:,0]
        cosdirY = cosdir[:,1]
        
        zenithAngle = numpy.arccos(numpy.sqrt(1 - cosdirX**2 - cosdirY**2))*180/numpy.pi
        azimuthAngle = numpy.arctan2(cosdirX,cosdirY)*180/numpy.pi + azimuth#0 deg north, 90 deg east
        angles = numpy.vstack((azimuthAngle, zenithAngle)).transpose()
        
        return angles
    
    def __getHeights(self, Ranges, zenith, error, minHeight, maxHeight):
    
        Ramb = 375  #Ramb = c/(2*PRF)
        Re = 6371   #Earth Radius
        heights = numpy.zeros(Ranges.shape)
        
        R_aux = numpy.array([0,1,2])*Ramb
        R_aux = R_aux.reshape(1,R_aux.size)

        Ranges = Ranges.reshape(Ranges.size,1)
        
        Ri = Ranges + R_aux
        hi = numpy.sqrt(Re**2 + Ri**2 + (2*Re*numpy.cos(zenith*numpy.pi/180)*Ri.transpose()).transpose()) - Re
        
        #Check if there is a height between 70 and 110 km
        h_bool = numpy.sum(numpy.logical_and(hi > minHeight, hi < maxHeight), axis = 1)
        ind_h = numpy.where(h_bool == 1)[0]
        
        hCorr = hi[ind_h, :]
        ind_hCorr = numpy.where(numpy.logical_and(hi > minHeight, hi < maxHeight))
           
        hCorr = hi[ind_hCorr]   
        heights[ind_h] = hCorr
        
        #Setting Error
        #Number 13: Height unresolvable echo: not valid height within 70 to 110 km
        #Number 14: Height ambiguous echo: more than one possible height within 70 to 110 km 
        indError = numpy.where(numpy.logical_or(error == 13, error == 14))[0]
        error[indError] = 0
        indInvalid2 = numpy.where(numpy.logical_and(h_bool > 1, error == 0))[0]    
        error[indInvalid2] = 14
        indInvalid1 = numpy.where(numpy.logical_and(h_bool == 0, error == 0))[0]
        error[indInvalid1] = 13 
        
        return heights, error
    
    def getPhasePairs(self, channelPositions):
        chanPos = numpy.array(channelPositions)
        listOper = list(itertools.combinations(range(5),2))
        
        distances = numpy.zeros(4)
        axisX = []
        axisY = []
        distX = numpy.zeros(3)
        distY = numpy.zeros(3)
        ix = 0
        iy = 0
        
        pairX = numpy.zeros((2,2))
        pairY = numpy.zeros((2,2))
        
        for i in range(len(listOper)):
            pairi = listOper[i]
                
            posDif = numpy.abs(chanPos[pairi[0],:] - chanPos[pairi[1],:])
            
            if posDif[0] == 0:
                axisY.append(pairi)
                distY[iy] = posDif[1]
                iy += 1
            elif posDif[1] == 0:
                axisX.append(pairi)
                distX[ix] = posDif[0]
                ix += 1
 
        for i in range(2):
            if i==0:
                dist0 = distX
                axis0 = axisX
            else:
                dist0 = distY
                axis0 = axisY
            
            side = numpy.argsort(dist0)[:-1]
            axis0 = numpy.array(axis0)[side,:]
            chanC = int(numpy.intersect1d(axis0[0,:], axis0[1,:])[0])
            axis1 = numpy.unique(numpy.reshape(axis0,4))
            side = axis1[axis1 != chanC]
            diff1 = chanPos[chanC,i] - chanPos[side[0],i]
            diff2 = chanPos[chanC,i] - chanPos[side[1],i]
            if diff1<0: 
                chan2 = side[0]
                d2 = numpy.abs(diff1)
                chan1 = side[1]
                d1 = numpy.abs(diff2)
            else:
                chan2 = side[1]
                d2 = numpy.abs(diff2)
                chan1 = side[0]
                d1 = numpy.abs(diff1)
                
            if i==0:
                chanCX = chanC
                chan1X = chan1
                chan2X = chan2
                distances[0:2] = numpy.array([d1,d2])
            else:
                chanCY = chanC
                chan1Y = chan1
                chan2Y = chan2
                distances[2:4] = numpy.array([d1,d2])
#         axisXsides = numpy.reshape(axisX[ix,:],4)
#         
#         channelCentX = int(numpy.intersect1d(pairX[0,:], pairX[1,:])[0])
#         channelCentY = int(numpy.intersect1d(pairY[0,:], pairY[1,:])[0])
#         
#         ind25X = numpy.where(pairX[0,:] != channelCentX)[0][0]
#         ind20X = numpy.where(pairX[1,:] != channelCentX)[0][0]
#         channel25X = int(pairX[0,ind25X])
#         channel20X = int(pairX[1,ind20X])
#         ind25Y = numpy.where(pairY[0,:] != channelCentY)[0][0]
#         ind20Y = numpy.where(pairY[1,:] != channelCentY)[0][0]
#         channel25Y = int(pairY[0,ind25Y])
#         channel20Y = int(pairY[1,ind20Y])
        
#         pairslist = [(channelCentX, channel25X),(channelCentX, channel20X),(channelCentY,channel25Y),(channelCentY, channel20Y)]
        pairslist = [(chanCX, chan1X),(chanCX, chan2X),(chanCY,chan1Y),(chanCY, chan2Y)]      
        
        return pairslist, distances
#     def __getAOA(self, phases, pairsList, error, AOAthresh, azimuth):
#         
#         arrayAOA = numpy.zeros((phases.shape[0],3))
#         cosdir0, cosdir = self.__getDirectionCosines(phases, pairsList)
#         
#         arrayAOA[:,:2] = self.__calculateAOA(cosdir, azimuth)
#         cosDirError = numpy.sum(numpy.abs(cosdir0 - cosdir), axis = 1)
#         arrayAOA[:,2] = cosDirError
#         
#         azimuthAngle = arrayAOA[:,0]
#         zenithAngle = arrayAOA[:,1]
#         
#         #Setting Error
#         #Number 3: AOA not fesible
#         indInvalid = numpy.where(numpy.logical_and((numpy.logical_or(numpy.isnan(zenithAngle), numpy.isnan(azimuthAngle))),error == 0))[0]
#         error[indInvalid] = 3 
#         #Number 4: Large difference in AOAs obtained from different antenna baselines
#         indInvalid = numpy.where(numpy.logical_and(cosDirError > AOAthresh,error == 0))[0]
#         error[indInvalid] = 4 
#         return arrayAOA, error
#     
#     def __getDirectionCosines(self, arrayPhase, pairsList):
#     
#         #Initializing some variables
#         ang_aux = numpy.array([-8,-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,8])*2*numpy.pi
#         ang_aux = ang_aux.reshape(1,ang_aux.size)
#         
#         cosdir = numpy.zeros((arrayPhase.shape[0],2))
#         cosdir0 = numpy.zeros((arrayPhase.shape[0],2))
#         
#         
#         for i in range(2):
#             #First Estimation
#             phi0_aux = arrayPhase[:,pairsList[i][0]] + arrayPhase[:,pairsList[i][1]]
#             #Dealias
#             indcsi = numpy.where(phi0_aux > numpy.pi)
#             phi0_aux[indcsi] -= 2*numpy.pi 
#             indcsi = numpy.where(phi0_aux < -numpy.pi)
#             phi0_aux[indcsi] += 2*numpy.pi 
#             #Direction Cosine 0
#             cosdir0[:,i] = -(phi0_aux)/(2*numpy.pi*0.5)
#         
#             #Most-Accurate Second Estimation
#             phi1_aux =  arrayPhase[:,pairsList[i][0]] - arrayPhase[:,pairsList[i][1]]
#             phi1_aux = phi1_aux.reshape(phi1_aux.size,1)
#             #Direction Cosine 1
#             cosdir1 = -(phi1_aux + ang_aux)/(2*numpy.pi*4.5)
#             
#             #Searching the correct Direction Cosine
#             cosdir0_aux = cosdir0[:,i]
#             cosdir0_aux = cosdir0_aux.reshape(cosdir0_aux.size,1)
#             #Minimum Distance
#             cosDiff = (cosdir1 - cosdir0_aux)**2
#             indcos = cosDiff.argmin(axis = 1)
#             #Saving Value obtained
#             cosdir[:,i] = cosdir1[numpy.arange(len(indcos)),indcos]
#             
#         return cosdir0, cosdir
#     
#     def __calculateAOA(self, cosdir, azimuth):
#         cosdirX = cosdir[:,0]
#         cosdirY = cosdir[:,1]
#         
#         zenithAngle = numpy.arccos(numpy.sqrt(1 - cosdirX**2 - cosdirY**2))*180/numpy.pi
#         azimuthAngle = numpy.arctan2(cosdirX,cosdirY)*180/numpy.pi + azimuth #0 deg north, 90 deg east
#         angles = numpy.vstack((azimuthAngle, zenithAngle)).transpose()
#         
#         return angles
#     
#     def __getHeights(self, Ranges, zenith, error, minHeight, maxHeight):
#     
#         Ramb = 375  #Ramb = c/(2*PRF)
#         Re = 6371   #Earth Radius
#         heights = numpy.zeros(Ranges.shape)
#         
#         R_aux = numpy.array([0,1,2])*Ramb
#         R_aux = R_aux.reshape(1,R_aux.size)
# 
#         Ranges = Ranges.reshape(Ranges.size,1)
#         
#         Ri = Ranges + R_aux
#         hi = numpy.sqrt(Re**2 + Ri**2 + (2*Re*numpy.cos(zenith*numpy.pi/180)*Ri.transpose()).transpose()) - Re
#         
#         #Check if there is a height between 70 and 110 km
#         h_bool = numpy.sum(numpy.logical_and(hi > minHeight, hi < maxHeight), axis = 1)
#         ind_h = numpy.where(h_bool == 1)[0]
#         
#         hCorr = hi[ind_h, :]
#         ind_hCorr = numpy.where(numpy.logical_and(hi > minHeight, hi < maxHeight))
#            
#         hCorr = hi[ind_hCorr]   
#         heights[ind_h] = hCorr
#         
#         #Setting Error
#         #Number 13: Height unresolvable echo: not valid height within 70 to 110 km
#         #Number 14: Height ambiguous echo: more than one possible height within 70 to 110 km 
#         
#         indInvalid2 = numpy.where(numpy.logical_and(h_bool > 1, error == 0))[0]    
#         error[indInvalid2] = 14
#         indInvalid1 = numpy.where(numpy.logical_and(h_bool == 0, error == 0))[0]
#         error[indInvalid1] = 13 
#         
#         return heights, error     
    