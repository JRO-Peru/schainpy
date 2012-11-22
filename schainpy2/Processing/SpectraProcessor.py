'''

$Author$
$Id$
'''

import os, sys
import numpy
import time
import datetime
path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from Data.JROData import Spectra, SpectraHeis
from IO.SpectraIO import SpectraWriter,SpectraHeisWriter
#from Graphics.schainPlotTypes import ScopeFigure, SpcFigure, RTIFigure
from Graphics.BaseGraph_mpl import LinearPlot
#from JRONoise import Noise

class SpectraProcessor:
    '''
    classdocs
    '''
    
    dataInObj = None        
    
    dataOutObj = None
        
    noiseObj = None
    
    integratorObjList = []
    
    writerObjList = []
    
    integratorObjIndex = None
    
    writerObjIndex = None
    
    profIndex = 0 # Se emplea cuando el objeto de entrada es un Voltage

    firstdatatime = None
    
    def __init__(self):
        '''
        Constructor
        '''
        
        self.integratorObjIndex = None
        self.writerObjIndex = None
        self.plotObjIndex = None
        self.integratorOst = []
        self.plotObjList = []
        self.noiseObj = []
        self.writerObjList = []
        self.buffer = None
        self.firstdatatime = None
        self.profIndex = 0
        
    def setup(self, dataInObj=None, dataOutObj=None, nFFTPoints=None, pairsList=None, wavelength=6):
        
        if dataInObj == None:
            raise ValueError, "This SpectraProcessor.setup() function needs dataInObj input variable"
        
        if dataInObj.type == "Voltage":
            if nFFTPoints == None: 
                raise ValueError, "This SpectraProcessor.setup() function needs nFFTPoints input variable"
            
            
        
        if dataInObj.type == "Spectra":
            if nFFTPoints != None: 
                raise ValueError, "The nFFTPoints cannot be selected to this object type"
            
            nFFTPoints = dataInObj.nFFTPoints
            
            if pairsList == None:
                pairsList = dataInObj.pairsList
        
        if pairsList == None:
            nPairs = 0
        else:
            nPairs = len(pairsList)
        
        self.dataInObj = dataInObj        
        
        if dataOutObj == None:
            dataOutObj = Spectra()
            
        self.dataOutObj = dataOutObj
        self.dataOutObj.nFFTPoints = nFFTPoints
        self.dataOutObj.pairsList = pairsList
        self.dataOutObj.nPairs = nPairs
        self.dataOutObj.wavelength = wavelength
        
        return self.dataOutObj
    
    def init(self):
        
        """
        
        Este metodo reinicia los contadores de los objetos integrator, writer y plotter
        y actualiza los parametros del objeto de salida dataOutObj a partir del objeto de entrada.       
        
        """
        
        self.dataOutObj.flagNoData = True
        
        if self.dataInObj.flagNoData:
            return 0
        
        self.integratorObjIndex = 0
        self.writerObjIndex = 0
        self.plotObjIndex = 0
        
        
        if self.dataInObj.type == "Spectra":
            
            self.dataOutObj.copy(self.dataInObj)
            self.dataOutObj.flagNoData = False
            return
        
        if self.dataInObj.type == "Voltage":
            
            if self.buffer == None:
                self.buffer = numpy.zeros((self.dataInObj.nChannels,
                                           self.dataOutObj.nFFTPoints,
                                           self.dataInObj.nHeights), 
                                          dtype='complex')
            
            self.buffer[:,self.profIndex,:] = self.dataInObj.data
            self.profIndex += 1
            
            if self.firstdatatime == None:
                self.firstdatatime = self.dataInObj.utctime
                
            if self.profIndex == self.dataOutObj.nFFTPoints:
                
                self.__updateObjFromInput()
                self.__getFft()
                
                self.dataOutObj.flagNoData = False
                
                self.buffer = None
                self.firstdatatime = None
                self.profIndex = 0
            
            return
        
        #Other kind of data        
        raise ValueError, "The type object %(s) is not valid " %(self.dataOutObj.type)

    def __getFft(self):
        """
        Convierte valores de Voltaje a Spectra
        
        Affected:
            self.dataOutObj.data_spc
            self.dataOutObj.data_cspc
            self.dataOutObj.data_dc
            self.dataOutObj.heightList
            self.dataOutObj.m_BasicHeader
            self.dataOutObj.m_ProcessingHeader
            self.dataOutObj.radarControllerHeaderObj
            self.dataOutObj.systemHeaderObj
            self.profIndex  
            self.buffer
            self.dataOutObj.flagNoData
            self.dataOutObj.dtype
            self.dataOutObj.nPairs
            self.dataOutObj.nChannels
            self.dataOutObj.nProfiles
            self.dataOutObj.systemHeaderObj.numChannels
            self.dataOutObj.m_ProcessingHeader.totalSpectra 
            self.dataOutObj.m_ProcessingHeader.profilesPerBlock
            self.dataOutObj.m_ProcessingHeader.numHeights
            self.dataOutObj.m_ProcessingHeader.spectraComb
            self.dataOutObj.m_ProcessingHeader.shif_fft
        """
            
        fft_volt = numpy.fft.fft(self.buffer,axis=1)
        dc = fft_volt[:,0,:]
        
        #calculo de self-spectra
        fft_volt = numpy.fft.fftshift(fft_volt,axes=(1,))
        spc = (fft_volt * numpy.conjugate(fft_volt))
        spc = spc.real
        
        blocksize = 0
        blocksize += dc.size
        blocksize += spc.size
        
        cspc = None
        pairIndex = 0
        if self.dataOutObj.pairsList != None:
            #calculo de cross-spectra
            cspc = numpy.zeros((self.dataOutObj.nPairs, self.dataOutObj.nFFTPoints, self.dataOutObj.nHeights), dtype='complex')
            for pair in self.dataOutObj.pairsList:
                cspc[pairIndex,:,:] = numpy.abs(fft_volt[pair[0],:,:] * numpy.conjugate(fft_volt[pair[1],:,:]))
                pairIndex += 1
            blocksize += cspc.size
        
        self.dataOutObj.data_spc = spc
        self.dataOutObj.data_cspc = cspc
        self.dataOutObj.data_dc = dc
        self.dataOutObj.blockSize = blocksize
        
#        self.getNoise()

    def __updateObjFromInput(self):
        
        self.dataOutObj.radarControllerHeaderObj = self.dataInObj.radarControllerHeaderObj.copy()
        self.dataOutObj.systemHeaderObj = self.dataInObj.systemHeaderObj.copy()
        self.dataOutObj.channelList = self.dataInObj.channelList
        self.dataOutObj.heightList = self.dataInObj.heightList
        self.dataOutObj.dtype = self.dataInObj.dtype
        self.dataOutObj.nHeights = self.dataInObj.nHeights
        self.dataOutObj.nChannels = self.dataInObj.nChannels
        self.dataOutObj.nBaud = self.dataInObj.nBaud
        self.dataOutObj.nCode = self.dataInObj.nCode
        self.dataOutObj.code = self.dataInObj.code
        self.dataOutObj.nProfiles = self.dataOutObj.nFFTPoints
        self.dataOutObj.channelIndexList = self.dataInObj.channelIndexList
        self.dataOutObj.flagTimeBlock = self.dataInObj.flagTimeBlock
        self.dataOutObj.utctime = self.firstdatatime
        self.dataOutObj.flagDecodeData = self.dataInObj.flagDecodeData #asumo q la data esta decodificada
        self.dataOutObj.flagDeflipData = self.dataInObj.flagDeflipData #asumo q la data esta sin flip
        self.dataOutObj.flagShiftFFT = self.dataInObj.flagShiftFFT
        self.dataOutObj.nCohInt = self.dataInObj.nCohInt
        self.dataOutObj.nIncohInt = 1
        self.dataOutObj.ippSeconds = self.dataInObj.ippSeconds
        self.dataOutObj.timeInterval = self.dataInObj.timeInterval*self.dataOutObj.nFFTPoints
        
    def addWriter(self, wrpath, blocksPerFile):
        
        objWriter = SpectraWriter(self.dataOutObj)
        objWriter.setup(wrpath, blocksPerFile)
        self.writerObjList.append(objWriter)
                    
    def addIntegrator(self,N,timeInterval):
        
        objIncohInt = IncoherentIntegration(N,timeInterval)
        self.integratorObjList.append(objIncohInt)
        
    def addCrossSpc(self, idfigure, nframes, wintitle, driver, colormap, colorbar, showprofile):
        crossSpcObj = CrossSpcFigure(idfigure, nframes, wintitle, driver, colormap, colorbar, showprofile)
        self.plotObjList.append(crossSpcObj)
        
    def plotCrossSpc(self, idfigure=None,
                    xmin=None,
                    xmax=None,
                    ymin=None,
                    ymax=None,
                    minvalue=None,
                    maxvalue=None,
                    wintitle='',
                    driver='plplot',
                    colormap='br_green',
                    colorbar=True,
                    showprofile=False,
                    save=False,
                    gpath=None,
                    pairsList = None):
        
        if self.dataOutObj.flagNoData:
            return 0
        
        if pairsList == None:
            pairsList = self.dataOutObj.pairsList
        
        nframes = len(pairsList)
        
        x = numpy.arange(self.dataOutObj.nFFTPoints)
                
        y = self.dataOutObj.heightList
        
        data_spc = self.dataOutObj.data_spc
        data_cspc = self.dataOutObj.data_cspc
        
        data = []
        
        
        if len(self.plotObjList) <= self.plotObjIndex:
            self.addSpc(idfigure, nframes, wintitle, driver, colormap, colorbar, showprofile)
            
            
            

        
    def addRti(self, idfigure, nframes, wintitle, driver, colormap, colorbar, showprofile):
        rtiObj = RTIFigure(idfigure, nframes, wintitle, driver, colormap, colorbar, showprofile)
        self.plotObjList.append(rtiObj)
        
    def plotRti(self, idfigure=None,
                    starttime=None,
                    endtime=None,
                    rangemin=None,
                    rangemax=None,
                    minvalue=None,
                    maxvalue=None,
                    wintitle='',
                    driver='plplot',
                    colormap='br_greeen',
                    colorbar=True,
                    showprofile=False,
                    xrangestep=None,
                    save=False,
                    gpath=None,
                    ratio=1,
                    channelList=None):
        
        if self.dataOutObj.flagNoData:
            return 0
        
        if channelList == None:
            channelList = self.dataOutObj.channelList
            
        nframes = len(channelList)
        
        if len(self.plotObjList) <= self.plotObjIndex:
            self.addRti(idfigure, nframes, wintitle, driver, colormap, colorbar, showprofile)
        
        data = 10.*numpy.log10(self.dataOutObj.data_spc[channelList,:,:])
        
        data = numpy.average(data, axis=1)
        
        currenttime = self.dataOutObj.utctime - time.timezone
        
        range = self.dataOutObj.heightList
        
        
        figuretitle = "RTI Plot for Spectra Data" #+ date
        
        cleardata = False
        
        deltax = self.dataOutObj.timeInterval
        
        plotObj = self.plotObjList[self.plotObjIndex]
        
        plotObj.plotPcolor(data=data, 
                           x=currenttime, 
                           y=range, 
                           channelList=channelList, 
                           xmin=starttime, 
                           xmax=endtime, 
                           ymin=rangemin, 
                           ymax=rangemax,
                           minvalue=minvalue, 
                           maxvalue=maxvalue, 
                           figuretitle=figuretitle, 
                           xrangestep=xrangestep,
                           deltax=deltax,
                           save=save, 
                           gpath=gpath,
                           ratio=ratio,
                           cleardata=cleardata
                           )
        
        
        
        self.plotObjIndex += 1
        
        
        
        
        
        
    
    def addSpc(self, idfigure, nframes, wintitle, driver, colormap, colorbar, showprofile):
        
        spcObj = SpcFigure(idfigure, nframes, wintitle, driver, colormap, colorbar, showprofile)
        self.plotObjList.append(spcObj)
    
    def plotSpc(self, idfigure=None,
                    xmin=None,
                    xmax=None,
                    ymin=None,
                    ymax=None,
                    minvalue=None,
                    maxvalue=None,
                    wintitle='',
                    driver='plplot',
                    colormap='br_green',
                    colorbar=True,
                    showprofile=False,
                    save=False,
                    gpath=None,
                    ratio=1,
                    channelList=None):
        
        if self.dataOutObj.flagNoData:
            return 0
        
        if channelList == None:
            channelList = self.dataOutObj.channelList
        
        nframes = len(channelList)
        
        if len(self.plotObjList) <= self.plotObjIndex:
            self.addSpc(idfigure, nframes, wintitle, driver, colormap, colorbar, showprofile)
            
        x = numpy.arange(self.dataOutObj.nFFTPoints)
                
        y = self.dataOutObj.heightList
        
        data = 10.*numpy.log10(self.dataOutObj.data_spc[channelList,:,:])    
#        noisedB = 10.*numpy.log10(noise)
        noisedB = numpy.arange(len(channelList)+1)
        noisedB = noisedB *1.2
        titleList = []
        for i in range(len(noisedB)):
            title = "%.2f"%noisedB[i]
            titleList.append(title)
        
        thisdatetime = datetime.datetime.fromtimestamp(self.dataOutObj.utctime)
        dateTime = "%s"%(thisdatetime.strftime("%d-%b-%Y %H:%M:%S"))
        figuretitle = "Spc Radar Data: %s"%dateTime
        
        cleardata = True
        
        plotObj = self.plotObjList[self.plotObjIndex]
        
        plotObj.plotPcolor(data=data, 
                            x=x, 
                            y=y, 
                            channelList=channelList, 
                            xmin=xmin, 
                            xmax=xmax, 
                            ymin=ymin, 
                            ymax=ymax,
                            minvalue=minvalue, 
                            maxvalue=maxvalue, 
                            figuretitle=figuretitle,
                            xrangestep=None,
                            deltax=None, 
                            save=save, 
                            gpath=gpath,
                            cleardata=cleardata
                            )
        
        self.plotObjIndex += 1
    
    
    def writeData(self, wrpath, blocksPerFile):
        
        if self.dataOutObj.flagNoData:
            return 0
            
        if len(self.writerObjList) <= self.writerObjIndex:
            self.addWriter(wrpath, blocksPerFile)
        
        self.writerObjList[self.writerObjIndex].putData()
        
        self.writerObjIndex += 1
                
    def integrator(self, N=None, timeInterval=None):
        
        if self.dataOutObj.flagNoData:
                return 0
        
        if len(self.integratorObjList) <= self.integratorObjIndex:
            self.addIntegrator(N,timeInterval)
        
        myIncohIntObj = self.integratorObjList[self.integratorObjIndex]
        myIncohIntObj.exe(data=self.dataOutObj.data_spc,datatime=self.dataOutObj.utctime)
        
        if myIncohIntObj.isReady:
            self.dataOutObj.data_spc = myIncohIntObj.data
            self.dataOutObj.timeInterval *= myCohIntObj.nIncohInt
            self.dataOutObj.nIncohInt = myIncohIntObj.navg * self.dataInObj.nIncohInt
            self.dataOutObj.utctime = myIncohIntObj.firstdatatime
            self.dataOutObj.flagNoData = False
            
            """Calcular el ruido"""
            self.getNoise()
        else:
            self.dataOutObj.flagNoData = True
        
        self.integratorObjIndex += 1
        
 
class SpectraHeisProcessor:
    
    def __init__(self):
        
        self.integratorObjIndex = None
        self.writerObjIndex = None
        self.plotObjIndex = None
        self.integratorObjList = []
        self.writerObjList = []
        self.plotObjList = []
        #self.noiseObj = Noise()
    
    def setup(self, dataInObj, dataOutObj=None, nFFTPoints=None, pairList=None):
        
        if nFFTPoints == None:
            nFFTPoints = self.dataInObj.nHeights 
            
        self.dataInObj = dataInObj        
        
        if dataOutObj == None:
            dataOutObj = SpectraHeis()
            
        self.dataOutObj = dataOutObj
        
        return self.dataOutObj
    
    def init(self):
        
        self.dataOutObj.flagNoData = True
        
        if self.dataInObj.flagNoData:
            return 0
        
        self.integratorObjIndex = 0
        self.writerObjIndex = 0
        self.plotObjIndex = 0
        
        if self.dataInObj.type == "Voltage":
            self.__updateObjFromInput()
            self.__getFft()
            self.dataOutObj.flagNoData = False
            return
            
        #Other kind of data
        if self.dataInObj.type == "SpectraHeis":
            self.dataOutObj.copy(self.dataInObj)
            self.dataOutObj.flagNoData = False
            return
        
        raise ValueError, "The type is not valid"
    
    def __updateObjFromInput(self):
        
        self.dataOutObj.radarControllerHeaderObj = self.dataInObj.radarControllerHeaderObj.copy()
        self.dataOutObj.systemHeaderObj = self.dataInObj.systemHeaderObj.copy()
        self.dataOutObj.channelList = self.dataInObj.channelList
        self.dataOutObj.heightList = self.dataInObj.heightList
        self.dataOutObj.dtype = self.dataInObj.dtype
        self.dataOutObj.nHeights = self.dataInObj.nHeights
        self.dataOutObj.nChannels = self.dataInObj.nChannels
        self.dataOutObj.nBaud = self.dataInObj.nBaud
        self.dataOutObj.nCode = self.dataInObj.nCode
        self.dataOutObj.code = self.dataInObj.code
        self.dataOutObj.nProfiles = 1
        self.dataOutObj.nFFTPoints = self.dataInObj.nHeights
        self.dataOutObj.channelIndexList = self.dataInObj.channelIndexList
        self.dataOutObj.flagNoData = self.dataInObj.flagNoData
        self.dataOutObj.flagTimeBlock = self.dataInObj.flagTimeBlock
        self.dataOutObj.utctime = self.dataInObj.utctime
        self.dataOutObj.flagDecodeData = self.dataInObj.flagDecodeData #asumo q la data esta decodificada
        self.dataOutObj.flagDeflipData = self.dataInObj.flagDeflipData #asumo q la data esta sin flip
        self.dataOutObj.flagShiftFFT = self.dataInObj.flagShiftFFT
        self.dataOutObj.nIncohInt = 1
        self.dataOutObj.ippSeconds= self.dataInObj.ippSeconds
        self.dataOutObj.set=self.dataInObj.set
        self.dataOutObj.deltaHeight=self.dataInObj.deltaHeight
        
  #  def addWriter(self,wrpath,blocksPerfile):
    def addWriter(self,wrpath):
        objWriter=SpectraHeisWriter(self.dataOutObj)
        objWriter.setup(wrpath)
        #objWriter.setup(wrpath,blocksPerfile)
        self.writerObjList.append(objWriter)
    
   # def writedata(self,wrpath,blocksPerfile):
    def writedata(self,wrpath): 
        if self.dataOutObj.flagNoData:
            return 0
            
        if len(self.writerObjList) <= self.writerObjIndex:
            #self.addWriter(wrpath, blocksPerFile)
            self.addWriter(wrpath)
        
        self.writerObjList[self.writerObjIndex].putData()
        
        self.writerObjIndex += 1 
                 
    def __getFft(self):
           
        fft_volt = numpy.fft.fft(self.dataInObj.data, axis=1)        
        #print fft_volt
        #calculo de self-spectra
        fft_volt = numpy.fft.fftshift(fft_volt,axes=(1,))
        
        spc = numpy.abs(fft_volt * numpy.conjugate(fft_volt))/(self.dataOutObj.nFFTPoints)
        self.dataOutObj.data_spc = spc
    
    def getSpectra(self):
        
        return self.dataOutObj.data_spc
    
    def getFrecuencies(self):
        
        print self.nFFTPoints
        return numpy.arange(int(self.nFFTPoints))
    
    def addIntegrator(self,N,timeInterval):
        
        objIncohInt = IncoherentIntegration(N,timeInterval)
        self.integratorObjList.append(objIncohInt)
    
    def integrator(self, N=None, timeInterval=None):
        
        if self.dataOutObj.flagNoData:
                return 0
        
        if len(self.integratorObjList) <= self.integratorObjIndex:
            self.addIntegrator(N,timeInterval)
        
        myIncohIntObj = self.integratorObjList[self.integratorObjIndex]
        myIncohIntObj.exe(data=self.dataOutObj.data_spc,datatime=self.dataOutObj.utctime)
        
        if myIncohIntObj.isReady:
            self.dataOutObj.data_spc = myIncohIntObj.data
            self.dataOutObj.nIncohInt = self.dataOutObj.nIncohInt*myIncohIntObj.navg
            self.dataOutObj.flagNoData = False
            
            #self.getNoise(type="hildebrand",parm=myIncohIntObj.navg)
#            self.getNoise(type="sort", parm=16)
            
        else:
            self.dataOutObj.flagNoData = True
        
        self.integratorObjIndex += 1

        
    def addScope(self, idfigure, nframes, wintitle, driver):
        
        if idfigure==None:
            idfigure = self.plotObjIndex
            
        scopeObj = ScopeFigure(idfigure, nframes, wintitle, driver)
        self.plotObjList.append(scopeObj)
    
    def plotScope(self,
                    idfigure=None,
                    minvalue=None,
                    maxvalue=None,
                    xmin=None,
                    xmax=None,
                    wintitle='',
                    driver='plplot',
                    save=False,
                    gpath=None,
                    titleList=None,
                    xlabelList=None,
                    ylabelList=None):
        
        if self.dataOutObj.flagNoData:
            return 0
        
        nframes = len(self.dataOutObj.channelList)
        
        if len(self.plotObjList) <= self.plotObjIndex:
            self.addScope(idfigure, nframes, wintitle, driver)
            
            
        data1D = self.dataOutObj.data_spc
        
        x = numpy.arange(self.dataOutObj.nHeights)
        
        thisDatetime = datetime.datetime.fromtimestamp(self.dataOutObj.utctime)
        
        dateTime = "%s"%(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
        date = "%s"%(thisDatetime.strftime("%d-%b-%Y"))
        
        figureTitle = "Scope Plot Radar Data: " + date
        
        plotObj = self.plotObjList[self.plotObjIndex]
        
        plotObj.plot1DArray(data1D, 
                             x, 
                             self.dataOutObj.channelList, 
                             xmin, 
                             xmax, 
                             minvalue, 
                             maxvalue,
                             figureTitle,
                             save, 
                             gpath)
                
        self.plotObjIndex += 1
    
    
    def addPlotMatScope(self, indexPlot,nsubplot,winTitle):
        linearObj = LinearPlot(indexPlot,nsubplot,winTitle)
        self.plotObjList.append(linearObj)
        
    def plotMatScope(self, idfigure,
                            channelList=None,
                            wintitle="",
                            save=None,
                            gpath=None):
        
        if self.dataOutObj.flagNoData:
            return 0
        
        if channelList == None:
            channelList = self.dataOutObj.channelList
        
        nchannels = len(channelList)
        
        thisDatetime = datetime.datetime.fromtimestamp(self.dataOutObj.utctime)
        dateTime = "%s"%(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
        winTitle = "Spectra Profile" #+ dateTime 
        
        if len(self.plotObjList) <= self.plotObjIndex:
            self.addPlotMatScope(idfigure,nchannels,winTitle)
        c   =  3E8  
        x=numpy.arange(-1*self.dataOutObj.nHeights/2.,self.dataOutObj.nHeights/2.)*(c/(2*self.dataOutObj.deltaHeight*self.dataOutObj.nHeights*1000))
        x= x/(10000.0)
        
        data = 10*numpy.log10(self.dataOutObj.data_spc)
             
        subplotTitle = "Channel No."
        xlabel = "Frecuencias(hz)*10K"
        ylabel = "Potencia(dB)"
        
        isPlotIni=False
        isPlotConfig=False
        
        ntimes=2     
        nsubplot= nchannels
        
        plotObj = self.plotObjList[self.plotObjIndex]
        
#        for i in range(ntimes):
            #Creacion de Subplots
        if not(plotObj.isPlotIni):
           for  index in range(nsubplot):
                indexplot = index + 1 
                title = subplotTitle + '%d'%indexplot
                xmin = numpy.min(x)
                xmax = numpy.max(x)
                ymin = numpy.min(data[index,:])
                ymax = numpy.max(data[index,:])
                plotObj.createObjects(indexplot,xmin,xmax,ymin,ymax,title,xlabel,ylabel)
           plotObj.isPlotIni =True
                
        # Inicializa el grafico en cada itearcion
        plotObj.setFigure(idfigure)
        plotObj.setFigure("")
        
        for index in range(nsubplot):
            subplot = index
            plotObj.iniPlot(subplot+1)
        #Ploteo de datos
            
        for channel in range(nsubplot):
            y=data[channel,:]
            plotObj.plot(channel+1,x,y,type='simple')
            
        plotObj.refresh()
            
            #time.sleep(0.05)
            
#        plotObj.show()
    
        self.plotObjIndex += 1    
        #print "Ploteo Finalizado"           

    def rti(self):
        if self.dataOutObj.flagNoData:
           return 0
        
        data=numpy.average(self.dataOutObj.data_spc,axis=1)
        data[0]
        print data[0]
        x = numpy.arange(100000)
        
        print "test"
        #print self.dataOutObj.data_spc.average(axis=1)
       
class IncoherentIntegration:

    integ_counter = None
    data = None
    navg = None
    buffer = None
    nIncohInt = None
    firstdatatime = None
    
    def __init__(self, N = None, timeInterval = None):
        """
        N 
        timeInterval - interval time [min], integer value
        """
        
        self.data = None
        self.navg = None
        self.buffer = None
        self.timeOut = None
        self.exitCondition = False
        self.isReady = False
        self.nIncohInt = N
        self.integ_counter = 0
        self.firstdatatime = None
        
        if timeInterval!=None:
            self.timeIntervalInSeconds = timeInterval * 60. #if (type(timeInterval)!=integer) -> change this line
        
        if ((timeInterval==None) and (N==None)):
             print 'N = None ; timeInterval = None'
             sys.exit(0)
        elif timeInterval == None:
            self.timeFlag = False
        else:
            self.timeFlag = True
            
            
    def exe(self,data,datatime):
        """
        data
        
        datatime [seconds]
        """
        if self.firstdatatime == None or self.isReady:
            self.firstdatatime = datatime

        if self.timeFlag:
            if self.timeOut == None:
                self.timeOut = datatime + self.timeIntervalInSeconds
            
            if datatime < self.timeOut:
                if self.buffer == None:
                    self.buffer = data
                else:
                    self.buffer = self.buffer + data
                self.integ_counter += 1
            else:
                self.exitCondition = True
                
        else:
            if self.integ_counter < self.nIncohInt:
                if self.buffer == None:
                    self.buffer = data
                else:
                    self.buffer = self.buffer + data
            
                self.integ_counter += 1

            if self.integ_counter == self.nIncohInt:
                self.exitCondition = True
                
        if self.exitCondition:
            self.data = self.buffer
            self.navg = self.integ_counter
            self.isReady = True
            self.buffer = None
            self.timeOut = None
            self.integ_counter = 0
            self.exitCondition = False
            
            if self.timeFlag:
                self.buffer = data
                self.timeOut = datatime + self.timeIntervalInSeconds
        else:
            self.isReady = False
            