import numpy,math,random,time
import zmq
import tempfile
from io import StringIO
########## 1  Heredamos JRODatareader
from schainpy.model.io.jroIO_base import *
########## 2 Heredamos las propiedades de ProcessingUnit
from schainpy.model.proc.jroproc_base import ProcessingUnit,Operation,MPDecorator
########## 3 Importaremos las clases BascicHeader, SystemHeader, RadarControlHeader, ProcessingHeader
from schainpy.model.data.jroheaderIO import PROCFLAG, BasicHeader,SystemHeader,RadarControllerHeader, ProcessingHeader
########## 4 Importaremos el objeto Voltge
from schainpy.model.data.jrodata import Voltage

@MPDecorator
class SimulatorReader(JRODataReader, ProcessingUnit):
    incIntFactor                   = 1
    nFFTPoints                     = 0
    FixPP_IncInt                   = 1
    FixRCP_IPP                     = 1000
    FixPP_CohInt                   = 1
    Tau_0                          = 250
    AcqH0_0                        = 70
    H0                             = AcqH0_0
    AcqDH_0                        = 1.25
    DH0                            = AcqDH_0
    Bauds                          = 32
    BaudWidth                      = None
    FixRCP_TXA                     = 40
    FixRCP_TXB                     = 70
    fAngle                         = 2.0*math.pi*(1/16)
    DC_level                       = 500
    stdev                          = 8
    Num_Codes                      = 2
    #code0                          = numpy.array([1,1,1,0,1,1,0,1,1,1,1,0,0,0,1,0,1,1,1,0,1,1,0,1,0,0,0,1,1,1,0,1])
    #code1                          = numpy.array([1,1,1,0,1,1,0,1,1,1,1,0,0,0,1,0,0,0,0,1,0,0,1,0,1,1,1,0,0,0,1,0])
    #Dyn_snCode                     = numpy.array([Num_Codes,Bauds])
    Dyn_snCode                     = None
    Samples                        = 200
    channels                       = 5
    pulses                         = None
    Reference                      = None
    pulse_size                     = None
    prof_gen                       = None
    Fdoppler                       = 100
    Hdoppler                       = 36
    Adoppler                       = 300
    frequency                      = 9345
    def __init__(self):
        """
        Inicializador de la clases SimulatorReader para
        generar datos de voltage simulados.
        Input:
            dataOut: Objeto de la clase Voltage.
            Este Objeto sera utilizado apra almacenar
            un perfil de datos  cada vez qe se haga  psiversho
            un requerimiento (getData)
        """
        ProcessingUnit.__init__(self)
        print(" [ START ] init - Metodo Simulator Reader")

        self.isConfig                  = False
        self.basicHeaderObj            = BasicHeader(LOCALTIME)
        self.systemHeaderObj           = SystemHeader()
        self.radarControllerHeaderObj  = RadarControllerHeader()
        self.processingHeaderObj       = ProcessingHeader()
        self.profileIndex              = 2**32-1
        self.dataOut                   = Voltage()
        #code0                          = numpy.array([1,1,1,0,1,1,0,1,1,1,1,0,0,0,1,0,1,1,1,0,1,1,0,1,0,0,0,1,1,1,0,1])
        code0                          = numpy.array([1,1,1,-1,1,1,-1,1,1,1,1,-1,-1,-1,1,-1,1,1,1,-1,1,1,-1,1,-1,-1,-1,1,1,1,-1,1])
        #code1                          = numpy.array([1,1,1,0,1,1,0,1,1,1,1,0,0,0,1,0,0,0,0,1,0,0,1,0,1,1,1,0,0,0,1,0])
        code1                          = numpy.array([1,1,1,-1,1,1,-1,1,1,1,1,-1,-1,-1,1,-1,-1,-1,-1,1,-1,-1,1,-1,1,1,1,-1,-1,-1,1,-1])
        #self.Dyn_snCode                = numpy.array([code0,code1])
        self.Dyn_snCode                = None
        print(" [ END ] init - Metodo simulator Reader" )


    def __hasNotDataInBuffer(self):

        if self.profileIndex >= self.processingHeaderObj.profilesPerBlock* self.nTxs:
            if self.nReadBlocks>0:
                tmp                           = self.dataOut.utctime
                tmp_utc                       = int(self.dataOut.utctime)
                tmp_milisecond                = int((tmp-tmp_utc)*1000)
                self.basicHeaderObj.utc       = tmp_utc
                self.basicHeaderObj.miliSecond= tmp_milisecond
            return 1
        return 0


    def setNextFile(self):
        """Set the next file to be readed open it and parse de file header"""

        if (self.nReadBlocks >= self.processingHeaderObj.dataBlocksPerFile):
            self.nReadFiles=self.nReadFiles+1
            print('------------------- [Opening file] ------------------------------',self.nReadFiles)
            self.nReadBlocks  = 0

    def __setNewBlock(self):

        self.setNextFile()
        if self.flagIsNewFile:
            return 1

    def readNextBlock(self):
        while True:
            self.__setNewBlock()
            if not(self.readBlock()):
                return 0
            self.getBasicHeader()
            break
        if self.verbose:
            print("[Reading] Block No. %d/%d -> %s" %(self.nReadBlocks,
                                                      self.processingHeaderObj.dataBlocksPerFile,
                                                      self.dataOut.datatime.ctime()) )
        return 1

    def getFirstHeader(self):
        self.getBasicHeader()
        self.dataOut.processingHeaderObj      = self.processingHeaderObj.copy()
        self.dataOut.systemHeaderObj          = self.systemHeaderObj.copy()
        self.dataOut.radarControllerHeaderObj = self.radarControllerHeaderObj.copy()
        #ADD NEW
        self.dataOut.nProfiles   = self.processingHeaderObj.profilesPerBlock
        self.dataOut.heightList  = numpy.arange(self.processingHeaderObj.nHeights) * self.processingHeaderObj.deltaHeight + self.processingHeaderObj.firstHeight
        self.dataOut.channelList = list(range(self.systemHeaderObj.nChannels))
        self.dataOut.nCohInt     = self.processingHeaderObj.nCohInt
        # asumo q la data no esta decodificada
        self.dataOut.flagDecodeData  = self.processingHeaderObj.flag_decode
        # asumo q la data no esta sin flip
        self.dataOut.flagDeflipData  = self.processingHeaderObj.flag_deflip
        self.dataOut.flagShiftFFT    = self.processingHeaderObj.shif_fft
        #
        self.dataOut.frequency = self.frequency

    def getBasicHeader(self):

        self.dataOut.utctime = self.basicHeaderObj.utc + self.basicHeaderObj.miliSecond / \
            1000. + self.profileIndex * self.radarControllerHeaderObj.ippSeconds

        self.dataOut.flagDiscontinuousBlock = self.flagDiscontinuousBlock

        self.dataOut.timeZone = self.basicHeaderObj.timeZone

        self.dataOut.dstFlag = self.basicHeaderObj.dstFlag

        self.dataOut.errorCount = self.basicHeaderObj.errorCount

        self.dataOut.useLocalTime = self.basicHeaderObj.useLocalTime

        self.dataOut.ippSeconds = self.radarControllerHeaderObj.ippSeconds / self.nTxs

    def reshapeData(self):
        if self.nTxs==1:
            return

    def readBlock(self):

        self.jro_GenerateBlockOfData(Samples= self.samples,DC_level=self.DC_level,
                                     stdev=self.stdev,Reference= self.Reference,
                                     pulses = self.pulses,Num_Codes=self.Num_Codes,
                                     pulse_size=self.pulse_size,prof_gen=self.profiles,
                                     H0=self.H0,DH0=self.DH0)

        self.profileIndex   = 0
        self.flagIsNewFile  = 0
        self.flagIsNewBlock = 1
        self.nTotalBlocks  += 1
        self.nReadBlocks   += 1

        return 1


    def getData(self): ### metodo propio de VoltageReader

        if self.flagNoMoreFiles:
            self.dataOut.flagNodata = True
        self.flagDiscontinuousBlock = 0
        self.flagIsNewBlock         = 0
        if self.__hasNotDataInBuffer():   # aqui es verdad
            if not(self.readNextBlock()): # return 1 y por eso el if not salta  a getBasic Header
                return 0
            self.getFirstHeader()         # atributo
            self.reshapeData()            # nTxx1 =1 return , n

        if not self.getByBlock:
            self.dataOut.flagDataAsBlock = False
            self.dataOut.data = self.datablock[:, self.profileIndex, :]
            self.dataOut.profileIndex = self.profileIndex
            self.profileIndex += 1
        else:
            pass
        self.dataOut.flagNoData = False
        self.getBasicHeader()
        self.dataOut.realtime = self.online
        return self.dataOut.data

    def set_kwargs(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def set_RCH(self, expType=2, nTx=1,ipp=None, txA=0, txB=0,
                 nWindows=None, nHeights=None, firstHeight=None, deltaHeight=None,
                 numTaus=0, line6Function=0, line5Function=0, fClock=None,
                 prePulseBefore=0, prePulseAfter=0,
                 codeType=0, nCode=0, nBaud=0, code=None,
                 flip1=0, flip2=0):

        self.radarControllerHeaderObj.expType      = expType
        self.radarControllerHeaderObj.nTx          = nTx
        self.radarControllerHeaderObj.ipp          = float(ipp)
        self.radarControllerHeaderObj.txA          = float(txA)
        self.radarControllerHeaderObj.txB          = float(txB)
        self.radarControllerHeaderObj.rangeIPP     = ipp
        self.radarControllerHeaderObj.rangeTxA     = txA
        self.radarControllerHeaderObj.rangeTxB     = txB

        self.radarControllerHeaderObj.nHeights     = int(nHeights)
        self.radarControllerHeaderObj.firstHeight  = numpy.array([firstHeight])
        self.radarControllerHeaderObj.deltaHeight  = numpy.array([deltaHeight])
        self.radarControllerHeaderObj.samplesWin   = numpy.array([nHeights])


        self.radarControllerHeaderObj.nWindows      = nWindows
        self.radarControllerHeaderObj.numTaus       = numTaus
        self.radarControllerHeaderObj.codeType      = codeType
        self.radarControllerHeaderObj.line6Function = line6Function
        self.radarControllerHeaderObj.line5Function = line5Function
        self.radarControllerHeaderObj.fclock        = fClock
        self.radarControllerHeaderObj.prePulseBefore= prePulseBefore
        self.radarControllerHeaderObj.prePulseAfter = prePulseAfter

        self.radarControllerHeaderObj.nCode = nCode
        self.radarControllerHeaderObj.nBaud = nBaud
        self.radarControllerHeaderObj.code  = code
        self.radarControllerHeaderObj.flip1 = flip1
        self.radarControllerHeaderObj.flip2 = flip2

        self.radarControllerHeaderObj.code_size = int(numpy.ceil(nBaud / 32.)) * nCode * 4

        if fClock is None and deltaHeight is not None:
            self.fClock = 0.15 / (deltaHeight * 1e-6)

    def set_PH(self, dtype=0, blockSize=0, profilesPerBlock=0,
                  dataBlocksPerFile=0, nWindows=0, processFlags=0, nCohInt=0,
                  nIncohInt=0, totalSpectra=0, nHeights=0, firstHeight=0,
                  deltaHeight=0, samplesWin=0, spectraComb=0, nCode=0,
                  code=0, nBaud=None, shif_fft=False, flag_dc=False,
                  flag_cspc=False, flag_decode=False, flag_deflip=False):

        self.processingHeaderObj.profilesPerBlock  = profilesPerBlock
        self.processingHeaderObj.dataBlocksPerFile = dataBlocksPerFile
        self.processingHeaderObj.nWindows          = nWindows
        self.processingHeaderObj.nCohInt           = nCohInt
        self.processingHeaderObj.nIncohInt         = nIncohInt
        self.processingHeaderObj.totalSpectra      = totalSpectra
        self.processingHeaderObj.nHeights          = int(nHeights)
        self.processingHeaderObj.firstHeight       = firstHeight
        self.processingHeaderObj.deltaHeight       = deltaHeight
        self.processingHeaderObj.samplesWin        = nHeights

    def set_BH(self, utc = 0, miliSecond = 0, timeZone = 0):
        self.basicHeaderObj.utc                    = utc
        self.basicHeaderObj.miliSecond             = miliSecond
        self.basicHeaderObj.timeZone               = timeZone

    def set_SH(self, nSamples=0, nProfiles=0, nChannels=0, adcResolution=14, pciDioBusWidth=0):
        self.systemHeaderObj.nSamples       = nSamples
        self.systemHeaderObj.nProfiles      = nProfiles
        self.systemHeaderObj.nChannels      = nChannels
        self.systemHeaderObj.adcResolution  = adcResolution
        self.systemHeaderObj.pciDioBusWidth = pciDioBusWidth

    def setup(self,frequency=49.92e6,incIntFactor= 1, nFFTPoints = 0, FixPP_IncInt=1,FixRCP_IPP=1000,
                   FixPP_CohInt= 1,Tau_0= 250,AcqH0_0 = 70 ,AcqDH_0=1.25, Bauds= 32,
                   FixRCP_TXA = 40, FixRCP_TXB = 50, fAngle = 2.0*math.pi*(1/16),DC_level= 50,
                   stdev= 8,Num_Codes = 1 , Dyn_snCode = None, samples=200,
                   channels=2,Fdoppler=20,Hdoppler=36,Adoppler=500,
                   **kwargs):

        self.set_kwargs(**kwargs)
        self.nReadBlocks = 0
        self.nReadFiles  = 1
        print('------------------- [Opening file: ] ------------------------------',self.nReadFiles)

        tmp              = time.time()
        tmp_utc          = int(tmp)
        tmp_milisecond   = int((tmp-tmp_utc)*1000)
        print(" SETUP -basicHeaderObj.utc",datetime.datetime.utcfromtimestamp(tmp))
        if Dyn_snCode is None:
            Num_Codes=1
            Bauds    =1



        self.set_BH(utc= tmp_utc,miliSecond= tmp_milisecond,timeZone=300 )

        self.set_RCH( expType=0, nTx=150,ipp=FixRCP_IPP, txA=FixRCP_TXA, txB= FixRCP_TXB,
                 nWindows=1 , nHeights=samples, firstHeight=AcqH0_0, deltaHeight=AcqDH_0,
                 numTaus=1, line6Function=0, line5Function=0, fClock=None,
                 prePulseBefore=0, prePulseAfter=0,
                 codeType=14, nCode=Num_Codes, nBaud=32, code=Dyn_snCode,
                 flip1=0, flip2=0)

        self.set_PH(dtype=0, blockSize=0, profilesPerBlock=300,
                      dataBlocksPerFile=120, nWindows=1, processFlags=0, nCohInt=1,
                      nIncohInt=1, totalSpectra=0, nHeights=samples, firstHeight=AcqH0_0,
                      deltaHeight=AcqDH_0, samplesWin=samples, spectraComb=0, nCode=0,
                      code=0, nBaud=None, shif_fft=False, flag_dc=False,
                      flag_cspc=False, flag_decode=False, flag_deflip=False)

        self.set_SH(nSamples=samples, nProfiles=300, nChannels=channels)


        self.frequency                      = frequency
        self.incIntFactor                   = incIntFactor
        self.nFFTPoints                     = nFFTPoints
        self.FixPP_IncInt                   = FixPP_IncInt
        self.FixRCP_IPP                     = FixRCP_IPP
        self.FixPP_CohInt                   = FixPP_CohInt
        self.Tau_0                          = Tau_0
        self.AcqH0_0                        = AcqH0_0
        self.H0                             = AcqH0_0
        self.AcqDH_0                        = AcqDH_0
        self.DH0                            = AcqDH_0
        self.Bauds                          = Bauds
        self.FixRCP_TXA                     = FixRCP_TXA
        self.FixRCP_TXB                     = FixRCP_TXB
        self.fAngle                         = fAngle
        self.DC_level                       = DC_level
        self.stdev                          = stdev
        self.Num_Codes                      = Num_Codes
        self.Dyn_snCode                     = Dyn_snCode
        self.samples                        = samples
        self.channels                       = channels
        self.profiles                       = None
        self.m_nReference                   = None
        self.Baudwidth                      = None
        self.Fdoppler                       = Fdoppler
        self.Hdoppler                       = Hdoppler
        self.Adoppler                       = Adoppler

        print("IPP    ", self.FixRCP_IPP)
        print("Tau_0  ",self.Tau_0)
        print("AcqH0_0",self.AcqH0_0)
        print("samples,window ",self.samples)
        print("AcqDH_0",AcqDH_0)
        print("FixRCP_TXA",self.FixRCP_TXA)
        print("FixRCP_TXB",self.FixRCP_TXB)
        print("Dyn_snCode",Dyn_snCode)
        print("Fdoppler", Fdoppler)
        print("Hdoppler",Hdoppler)
        print("Vdopplermax",Fdoppler*(3.0e8/self.frequency)/2.0)

        self.init_acquisition()
        self.pulses,self.pulse_size=self.init_pulse(Num_Codes=self.Num_Codes,Bauds=self.Bauds,BaudWidth=self.BaudWidth,Dyn_snCode=Dyn_snCode)
        print(" [ END ] - SETUP metodo")
        return

    def run(self,**kwargs): # metodo propio
        if not(self.isConfig):
            self.setup(**kwargs)
            self.isConfig = True
        self.getData()

##################################################################
###### Aqui ingresamos las clases y metodos propios del simulador
##################################################################

#############################################
############## INIT_ACQUISITION##############
#############################################
    def init_acquisition(self):

        if self.nFFTPoints != 0:
            self.incIntFactor = m_nProfilesperBlock/self.nFFTPoints
            if (self.FixPP_IncInt > self.incIntFactor):
                self.incIntFactor = self.FixPP_IncInt/ self.incIntFactor
            elif(self.FixPP_IncInt< self.incIntFactor):
                print("False alert...")

        ProfilesperBlock  = self.processingHeaderObj.profilesPerBlock

        self.timeperblock =int(((self.FixRCP_IPP
                        *ProfilesperBlock
                        *self.FixPP_CohInt
                        *self.incIntFactor)
                       /150.0)
                      *0.9
                      +0.5)
        # para cada canal
        self.profiles     =  ProfilesperBlock*self.FixPP_CohInt
        self.profiles     =  ProfilesperBlock
        self.Reference    =  int((self.Tau_0-self.AcqH0_0)/(self.AcqDH_0)+0.5)
        self.BaudWidth    =  int((self.FixRCP_TXA/self.AcqDH_0)/self.Bauds + 0.5 )

        if (self.BaudWidth==0):
            self.BaudWidth=1
#################################################################
####################### init_pulse ##############################
################################################################

    def init_pulse(self,Num_Codes=Num_Codes,Bauds=Bauds,BaudWidth=BaudWidth,Dyn_snCode=Dyn_snCode):

        Num_Codes   = Num_Codes
        Bauds       = Bauds
        BaudWidth   = BaudWidth
        Dyn_snCode  = Dyn_snCode

        if Dyn_snCode:
            print("EXISTE")
        else:
            print("No existe")

        if Dyn_snCode: # if Bauds:
            pulses         = list(range(0,Num_Codes))
            num_codes      = Num_Codes
            for i in range(num_codes):
                pulse_size = Bauds*BaudWidth
                pulses[i]  = numpy.zeros(pulse_size)
                for j in range(Bauds):
                    for k in range(BaudWidth):
                        pulses[i][j*BaudWidth+k] = int(Dyn_snCode[i][j]*600)
        else:
            print("sin code")
            pulses     = list(range(1))
            pulse_size = int(self.FixRCP_TXB/0.15+0.5)
            pulses[0]  = numpy.ones(pulse_size)
            pulses     = 600*pulses[0]

        return pulses,pulse_size

#################################################################
##################### Generate block data
################################################################

    def jro_GenerateBlockOfData(self,Samples=Samples,DC_level= DC_level,stdev=stdev,
                                Reference= Reference,pulses= pulses,
                                Num_Codes= Num_Codes,pulse_size=pulse_size,
                                prof_gen= prof_gen,H0 = H0,DH0=DH0,
                                Adoppler=Adoppler,Fdoppler= Fdoppler,Hdoppler=Hdoppler):
        Samples    = Samples
        DC_level   = DC_level
        stdev      = stdev
        m_nR       = Reference
        pulses     = pulses
        num_codes  = Num_Codes
        ps         = pulse_size
        prof_gen   = prof_gen
        channels   = self.channels
        H0         = H0
        DH0        = DH0
        ippSec     = self.radarControllerHeaderObj.ippSeconds
        Fdoppler   = self.Fdoppler
        Hdoppler   = self.Hdoppler
        Adoppler   = self.Adoppler

        self.datablock = numpy.zeros([channels,prof_gen,Samples],dtype= numpy.complex64)
        for i in range(channels):
            for k in range(prof_gen):
                #·······················NOISE···············
                Noise_r    = numpy.random.normal(DC_level,stdev,Samples)
                Noise_i    = numpy.random.normal(DC_level,stdev,Samples)
                Noise      = numpy.zeros(Samples,dtype=complex)
                Noise.real = Noise_r
                Noise.imag = Noise_i
                #·······················PULSOS··············
                Pulso      = numpy.zeros(pulse_size,dtype=complex)
                Pulso.real =  pulses[k%num_codes]
                Pulso.imag =  pulses[k%num_codes]
                #····················· PULSES+NOISE··········
                InBuffer                    = numpy.zeros(Samples,dtype=complex)
                InBuffer[m_nR:m_nR+ps]      = Pulso
                InBuffer                    =  InBuffer+Noise
                #····················· ANGLE ·······························
                InBuffer.real[m_nR:m_nR+ps] = InBuffer.real[m_nR:m_nR+ps]*(math.cos( self.fAngle)*5)
                InBuffer.imag[m_nR:m_nR+ps] = InBuffer.imag[m_nR:m_nR+ps]*(math.sin( self.fAngle)*5)
                InBuffer=InBuffer
                self.datablock[i][k]= InBuffer
                #plot_cts(InBuffer,H0=H0,DH0=DH0)
                #wave_fft(x=InBuffer,plot_show=True)
                #time.sleep(1)
        #················DOPPLER SIGNAL...............................................
        time_vec   = numpy.linspace(0,(prof_gen-1)*ippSec,int(prof_gen))+self.nReadBlocks*ippSec*prof_gen+(self.nReadFiles-1)*ippSec*prof_gen
        fd         = Fdoppler #+(600.0/120)*self.nReadBlocks
        d_signal   = Adoppler*numpy.array(numpy.exp(1.0j*2.0*math.pi*fd*time_vec),dtype=numpy.complex64)
        #·················· DATABLOCK + DOPPLER············...........................
        HD=int(Hdoppler/self.AcqDH_0)
        for  i in range(12):
            self.datablock[:,:,HD+i]=self.datablock[:,:,HD+i]+ d_signal # RESULT
        '''
        a= numpy.zeros(10)
        for i in range(10):
            a[i]=i+self.nReadBlocks+20
        for i in a:
            self.datablock[0,:,int(i)]=self.datablock[0,:,int(i)]+ d_signal # RESULT
        '''
