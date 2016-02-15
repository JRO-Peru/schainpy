import sys
import numpy

from jroproc_base import ProcessingUnit, Operation
from schainpy.model.data.jrodata import Voltage

class VoltageProc(ProcessingUnit):
    
    
    def __init__(self):
        
        ProcessingUnit.__init__(self)
        
#         self.objectDict = {}
        self.dataOut = Voltage()
        self.flip = 1

    def run(self):
        if self.dataIn.type == 'AMISR':
            self.__updateObjFromAmisrInput()
        
        if self.dataIn.type == 'Voltage':
            self.dataOut.copy(self.dataIn)
            
#         self.dataOut.copy(self.dataIn)

    def __updateObjFromAmisrInput(self):
        
        self.dataOut.timeZone = self.dataIn.timeZone
        self.dataOut.dstFlag = self.dataIn.dstFlag
        self.dataOut.errorCount = self.dataIn.errorCount
        self.dataOut.useLocalTime = self.dataIn.useLocalTime
        
        self.dataOut.flagNoData = self.dataIn.flagNoData
        self.dataOut.data = self.dataIn.data
        self.dataOut.utctime = self.dataIn.utctime
        self.dataOut.channelList = self.dataIn.channelList
#         self.dataOut.timeInterval = self.dataIn.timeInterval
        self.dataOut.heightList = self.dataIn.heightList
        self.dataOut.nProfiles = self.dataIn.nProfiles
        
        self.dataOut.nCohInt = self.dataIn.nCohInt
        self.dataOut.ippSeconds = self.dataIn.ippSeconds
        self.dataOut.frequency = self.dataIn.frequency
        
        self.dataOut.azimuth = self.dataIn.azimuth
        self.dataOut.zenith = self.dataIn.zenith
        
        self.dataOut.beam.codeList = self.dataIn.beam.codeList
        self.dataOut.beam.azimuthList = self.dataIn.beam.azimuthList
        self.dataOut.beam.zenithList = self.dataIn.beam.zenithList
#        
#        pass#
#
#    def init(self):
#        
#        
#        if self.dataIn.type == 'AMISR':
#            self.__updateObjFromAmisrInput()
#        
#        if self.dataIn.type == 'Voltage':
#            self.dataOut.copy(self.dataIn) 
#        # No necesita copiar en cada init() los atributos de dataIn
#        # la copia deberia hacerse por cada nuevo bloque de datos
        
    def selectChannels(self, channelList):
        
        channelIndexList = []
        
        for channel in channelList:
            if channel not in self.dataOut.channelList:
                raise ValueError, "Channel %d is not in %s" %(channel, str(self.dataOut.channelList))
                    
            index = self.dataOut.channelList.index(channel)
            channelIndexList.append(index)
        
        self.selectChannelsByIndex(channelIndexList)
        
    def selectChannelsByIndex(self, channelIndexList):
        """
        Selecciona un bloque de datos en base a canales segun el channelIndexList 
        
        Input:
            channelIndexList    :    lista sencilla de canales a seleccionar por ej. [2,3,7] 
            
        Affected:
            self.dataOut.data
            self.dataOut.channelIndexList
            self.dataOut.nChannels
            self.dataOut.m_ProcessingHeader.totalSpectra
            self.dataOut.systemHeaderObj.numChannels
            self.dataOut.m_ProcessingHeader.blockSize
            
        Return:
            None
        """

        for channelIndex in channelIndexList:
            if channelIndex not in self.dataOut.channelIndexList:
                print channelIndexList
                raise ValueError, "The value %d in channelIndexList is not valid" %channelIndex
        
        if self.dataOut.flagDataAsBlock:
            """
            Si la data es obtenida por bloques, dimension = [nChannels, nProfiles, nHeis]
            """
            data = self.dataOut.data[channelIndexList,:,:]
        else:
            data = self.dataOut.data[channelIndexList,:]
        
        self.dataOut.data = data
        self.dataOut.channelList = [self.dataOut.channelList[i] for i in channelIndexList]
#        self.dataOut.nChannels = nChannels
        
        return 1
    
    def selectHeights(self, minHei=None, maxHei=None):
        """
        Selecciona un bloque de datos en base a un grupo de valores de alturas segun el rango
        minHei <= height <= maxHei
        
        Input:
            minHei    :    valor minimo de altura a considerar 
            maxHei    :    valor maximo de altura a considerar
            
        Affected:
            Indirectamente son cambiados varios valores a travez del metodo selectHeightsByIndex
            
        Return:
            1 si el metodo se ejecuto con exito caso contrario devuelve 0
        """
        
        if minHei == None:
            minHei = self.dataOut.heightList[0]
            
        if maxHei == None:
            maxHei = self.dataOut.heightList[-1]
            
        if (minHei < self.dataOut.heightList[0]):
            minHei = self.dataOut.heightList[0]

        if (maxHei > self.dataOut.heightList[-1]):
            maxHei = self.dataOut.heightList[-1]
            
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

        self.selectHeightsByIndex(minIndex, maxIndex)
        
        return 1

    
    def selectHeightsByIndex(self, minIndex, maxIndex):
        """
        Selecciona un bloque de datos en base a un grupo indices de alturas segun el rango
        minIndex <= index <= maxIndex
        
        Input:
            minIndex    :    valor de indice minimo de altura a considerar 
            maxIndex    :    valor de indice maximo de altura a considerar
            
        Affected:
            self.dataOut.data
            self.dataOut.heightList
            
        Return:
            1 si el metodo se ejecuto con exito caso contrario devuelve 0
        """
        
        if (minIndex < 0) or (minIndex > maxIndex):
            raise ValueError, "Height index range (%d,%d) is not valid" % (minIndex, maxIndex)
        
        if (maxIndex >= self.dataOut.nHeights):
            maxIndex = self.dataOut.nHeights
            
        #voltage
        if self.dataOut.flagDataAsBlock:
            """
            Si la data es obtenida por bloques, dimension = [nChannels, nProfiles, nHeis]
            """
            data = self.dataOut.data[:,:, minIndex:maxIndex]
        else:
            data = self.dataOut.data[:, minIndex:maxIndex]

#         firstHeight = self.dataOut.heightList[minIndex]

        self.dataOut.data = data
        self.dataOut.heightList = self.dataOut.heightList[minIndex:maxIndex]
        
        if self.dataOut.nHeights <= 1:
            raise ValueError, "selectHeights: Too few heights. Current number of heights is %d" %(self.dataOut.nHeights)
        
        return 1
    
 
    def filterByHeights(self, window):
        
        deltaHeight = self.dataOut.heightList[1] - self.dataOut.heightList[0]
        
        if window == None:
            window = (self.dataOut.radarControllerHeaderObj.txA/self.dataOut.radarControllerHeaderObj.nBaud) / deltaHeight
        
        newdelta = deltaHeight * window
        r = self.dataOut.nHeights % window
        newheights = (self.dataOut.nHeights-r)/window
        
        if newheights <= 1:
            raise ValueError, "filterByHeights: Too few heights. Current number of heights is %d and window is %d" %(self.dataOut.nHeights, window)
            
        if self.dataOut.flagDataAsBlock:
            """
            Si la data es obtenida por bloques, dimension = [nChannels, nProfiles, nHeis]
            """
            buffer = self.dataOut.data[:, :, 0:self.dataOut.nHeights-r]
            buffer = buffer.reshape(self.dataOut.nChannels,self.dataOut.nProfiles,self.dataOut.nHeights/window,window)
            buffer = numpy.sum(buffer,3)
        
        else:
            buffer = self.dataOut.data[:,0:self.dataOut.nHeights-r] 
            buffer = buffer.reshape(self.dataOut.nChannels,self.dataOut.nHeights/window,window)
            buffer = numpy.sum(buffer,2)

        self.dataOut.data = buffer
        self.dataOut.heightList = self.dataOut.heightList[0] + numpy.arange( newheights )*newdelta
        self.dataOut.windowOfFilter = window

    def setH0(self, h0, deltaHeight = None):
        
        if not deltaHeight:
            deltaHeight = self.dataOut.heightList[1] - self.dataOut.heightList[0]
        
        nHeights = self.dataOut.nHeights
        
        newHeiRange = h0 + numpy.arange(nHeights)*deltaHeight
        
        self.dataOut.heightList = newHeiRange
        
    def deFlip(self, channelList = []):
        
        data = self.dataOut.data.copy()
        
        if self.dataOut.flagDataAsBlock:
            flip = self.flip
            profileList = range(self.dataOut.nProfiles)
            
            if not channelList:
                for thisProfile in profileList:
                    data[:,thisProfile,:] = data[:,thisProfile,:]*flip
                    flip *= -1.0
            else:
                for thisChannel in channelList:
                    if thisChannel not in self.dataOut.channelList:
                        continue
                    
                    for thisProfile in profileList:
                        data[thisChannel,thisProfile,:] = data[thisChannel,thisProfile,:]*flip
                        flip *= -1.0
            
            self.flip = flip
            
        else:
            if not channelList:
                data[:,:] = data[:,:]*self.flip
            else:
                for thisChannel in channelList:
                    if thisChannel not in self.dataOut.channelList:
                        continue
                    
                    data[thisChannel,:] = data[thisChannel,:]*self.flip
            
            self.flip *= -1.
            
        self.dataOut.data = data
        
    def setRadarFrequency(self, frequency=None):
        
        if frequency != None:
            self.dataOut.frequency = frequency
        
        return 1
    
class CohInt(Operation):
    
    isConfig = False
    
    __profIndex = 0
    __withOverapping  = False
    
    __byTime = False
    __initime = None
    __lastdatatime = None
    __integrationtime = None
    
    __buffer = None
    
    __dataReady = False
    
    n = None
    
    
    def __init__(self):
        
        Operation.__init__(self)
        
#         self.isConfig = False
    
    def setup(self, n=None, timeInterval=None, overlapping=False, byblock=False):
        """
        Set the parameters of the integration class.
        
        Inputs:
        
            n        :    Number of coherent integrations
            timeInterval   :    Time of integration. If the parameter "n" is selected this one does not work
            overlapping    :    
            
        """
        
        self.__initime = None
        self.__lastdatatime = 0
        self.__buffer = None
        self.__dataReady = False
        self.byblock = byblock
        
        if n == None and timeInterval == None:
            raise ValueError, "n or timeInterval should be specified ..." 
        
        if n != None:
            self.n = n
            self.__byTime = False
        else:
            self.__integrationtime = timeInterval #* 60. #if (type(timeInterval)!=integer) -> change this line
            self.n = 9999
            self.__byTime = True
        
        if overlapping:
            self.__withOverapping = True
            self.__buffer = None
        else:
            self.__withOverapping = False
            self.__buffer = 0
        
        self.__profIndex = 0
    
    def putData(self, data):
        
        """
        Add a profile to the __buffer and increase in one the __profileIndex
        
        """
            
        if not self.__withOverapping:
            self.__buffer += data.copy()
            self.__profIndex += 1            
            return
        
        #Overlapping data
        nChannels, nHeis = data.shape
        data = numpy.reshape(data, (1, nChannels, nHeis))
        
        #If the buffer is empty then it takes the data value
        if self.__buffer is None:
            self.__buffer = data
            self.__profIndex += 1
            return
        
        #If the buffer length is lower than n then stakcing the data value
        if self.__profIndex < self.n:
            self.__buffer = numpy.vstack((self.__buffer, data))
            self.__profIndex += 1
            return
        
        #If the buffer length is equal to n then replacing the last buffer value with the data value 
        self.__buffer = numpy.roll(self.__buffer, -1, axis=0)
        self.__buffer[self.n-1] = data
        self.__profIndex = self.n
        return
        
        
    def pushData(self):
        """
        Return the sum of the last profiles and the profiles used in the sum.
        
        Affected:
        
        self.__profileIndex
        
        """
        
        if not self.__withOverapping:
            data = self.__buffer
            n = self.__profIndex
        
            self.__buffer = 0
            self.__profIndex = 0
            
            return data, n
        
        #Integration with Overlapping
        data = numpy.sum(self.__buffer, axis=0)
        n = self.__profIndex
        
        return data, n
    
    def byProfiles(self, data):
        
        self.__dataReady = False
        avgdata = None
#         n = None
            
        self.putData(data)
        
        if self.__profIndex == self.n:
            
            avgdata, n = self.pushData()
            self.__dataReady = True
        
        return avgdata
    
    def byTime(self, data, datatime):
        
        self.__dataReady = False
        avgdata = None
        n = None
        
        self.putData(data)
        
        if (datatime - self.__initime) >= self.__integrationtime:
            avgdata, n = self.pushData()
            self.n = n
            self.__dataReady = True
        
        return avgdata
        
    def integrate(self, data, datatime=None):
        
        if self.__initime == None:
            self.__initime = datatime
        
        if self.__byTime:
            avgdata = self.byTime(data, datatime)
        else:
            avgdata = self.byProfiles(data)
        
        
        self.__lastdatatime = datatime
        
        if avgdata is None:
            return None, None
        
        avgdatatime = self.__initime
        
        deltatime = datatime -self.__lastdatatime
        
        if not self.__withOverapping:
            self.__initime = datatime
        else:
            self.__initime += deltatime
            
        return avgdata, avgdatatime
    
    def integrateByBlock(self, dataOut):
        
        times = int(dataOut.data.shape[1]/self.n)
        avgdata = numpy.zeros((dataOut.nChannels, times, dataOut.nHeights), dtype=numpy.complex)
        
        id_min = 0
        id_max = self.n
        
        for i in range(times):
            junk = dataOut.data[:,id_min:id_max,:]
            avgdata[:,i,:] = junk.sum(axis=1)
            id_min += self.n
            id_max += self.n 
        
        timeInterval = dataOut.ippSeconds*self.n
        avgdatatime = (times - 1) * timeInterval + dataOut.utctime 
        self.__dataReady = True
        return avgdata, avgdatatime
    
    def run(self, dataOut, **kwargs):
        
        if not self.isConfig:
            self.setup(**kwargs)
            self.isConfig = True
        
        if dataOut.flagDataAsBlock:
            """
            Si la data es leida por bloques, dimension = [nChannels, nProfiles, nHeis]
            """
            avgdata, avgdatatime = self.integrateByBlock(dataOut)
            dataOut.nProfiles /= self.n
        else:            
            avgdata, avgdatatime = self.integrate(dataOut.data, dataOut.utctime)
        
#        dataOut.timeInterval *= n
        dataOut.flagNoData = True
        
        if self.__dataReady:
            dataOut.data = avgdata
            dataOut.nCohInt *= self.n
            dataOut.utctime = avgdatatime
#             dataOut.timeInterval = dataOut.ippSeconds * dataOut.nCohInt
            dataOut.flagNoData = False

class Decoder(Operation):
    
    isConfig = False
    __profIndex = 0
    
    code = None
    
    nCode = None 
    nBaud = None
    
    
    def __init__(self):
        
        Operation.__init__(self)
        
        self.times = None
        self.osamp = None
#         self.__setValues = False
        self.isConfig = False
        
    def setup(self, code, osamp, dataOut):
        
        self.__profIndex = 0
        
        self.code = code
        
        self.nCode = len(code) 
        self.nBaud = len(code[0])
        
        if (osamp != None) and (osamp >1):
            self.osamp = osamp
            self.code = numpy.repeat(code, repeats=self.osamp, axis=1)
            self.nBaud = self.nBaud*self.osamp
        
        self.__nChannels = dataOut.nChannels
        self.__nProfiles = dataOut.nProfiles
        self.__nHeis = dataOut.nHeights
        
        if self.__nHeis < self.nBaud:
            raise ValueError, 'Number of heights (%d) should be greater than number of bauds (%d)' %(self.__nHeis, self.nBaud)
        
        #Frequency
        __codeBuffer = numpy.zeros((self.nCode, self.__nHeis), dtype=numpy.complex)
        
        __codeBuffer[:,0:self.nBaud] = self.code
        
        self.fft_code = numpy.conj(numpy.fft.fft(__codeBuffer, axis=1))
            
        if dataOut.flagDataAsBlock:
            
            self.ndatadec = self.__nHeis #- self.nBaud + 1
            
            self.datadecTime = numpy.zeros((self.__nChannels, self.__nProfiles, self.ndatadec), dtype=numpy.complex)
        
        else:
            
            #Time
            self.ndatadec = self.__nHeis #- self.nBaud + 1
            
            self.datadecTime = numpy.zeros((self.__nChannels, self.ndatadec), dtype=numpy.complex)     
         
    def __convolutionInFreq(self, data):
        
        fft_code = self.fft_code[self.__profIndex].reshape(1,-1)
        
        fft_data = numpy.fft.fft(data, axis=1)
        
        conv = fft_data*fft_code
        
        data = numpy.fft.ifft(conv,axis=1)
        
        return data
        
    def __convolutionInFreqOpt(self, data):
        
        raise NotImplementedError
    
    def __convolutionInTime(self, data):
        
        code = self.code[self.__profIndex]
        
        for i in range(self.__nChannels):
            self.datadecTime[i,:] = numpy.correlate(data[i,:], code, mode='full')[self.nBaud-1:]
        
        return self.datadecTime
    
    def __convolutionByBlockInTime(self, data):
        
        repetitions = self.__nProfiles / self.nCode
        
        junk = numpy.lib.stride_tricks.as_strided(self.code, (repetitions, self.code.size), (0, self.code.itemsize))
        junk = junk.flatten()
        code_block = numpy.reshape(junk, (self.nCode*repetitions, self.nBaud))
        
        for i in range(self.__nChannels):
            for j in range(self.__nProfiles):
                self.datadecTime[i,j,:] = numpy.correlate(data[i,j,:], code_block[j,:], mode='full')[self.nBaud-1:]
        
        return self.datadecTime
    
    def __convolutionByBlockInFreq(self, data):
        
        raise NotImplementedError, "Decoder by frequency fro Blocks not implemented"


        fft_code = self.fft_code[self.__profIndex].reshape(1,-1)
        
        fft_data = numpy.fft.fft(data, axis=2)
        
        conv = fft_data*fft_code
        
        data = numpy.fft.ifft(conv,axis=2)
        
        return data
    
    def run(self, dataOut, code=None, nCode=None, nBaud=None, mode = 0, osamp=None, times=None):
        
        if dataOut.flagDecodeData:
            print "This data is already decoded, recoding again ..."
        
        if not self.isConfig:
            
            if code is None:
                if dataOut.code is None:
                    raise ValueError, "Code could not be read from %s instance. Enter a value in Code parameter" %dataOut.type
                
                code = dataOut.code
            else:
                code = numpy.array(code).reshape(nCode,nBaud)
            
            self.setup(code, osamp, dataOut)
            
            self.isConfig = True
            
            if mode == 3:
                sys.stderr.write("Decoder Warning: mode=%d is not valid, using mode=0\n" %mode)
            
            if times != None:
                sys.stderr.write("Decoder Warning: Argument 'times' in not used anymore\n")
        
        if self.code is None:
            print "Fail decoding: Code is not defined."
            return
        
        datadec = None
        if mode == 3:
            mode = 0
                
        if dataOut.flagDataAsBlock:
            """
            Decoding when data have been read as block,
            """
                
            if mode == 0:
                datadec = self.__convolutionByBlockInTime(dataOut.data)
            if mode == 1:
                datadec = self.__convolutionByBlockInFreq(dataOut.data)
        else:
            """
            Decoding when data have been read profile by profile
            """
            if mode == 0:
                datadec = self.__convolutionInTime(dataOut.data)
                
            if mode == 1:
                datadec = self.__convolutionInFreq(dataOut.data)
            
            if mode == 2:
                datadec = self.__convolutionInFreqOpt(dataOut.data)
        
        if datadec is None:
            raise ValueError, "Codification mode selected is not valid: mode=%d. Try selecting 0 or 1" %mode
        
        dataOut.code = self.code
        dataOut.nCode = self.nCode
        dataOut.nBaud = self.nBaud
        
        dataOut.data = datadec
        
        dataOut.heightList = dataOut.heightList[0:datadec.shape[-1]]
        
        dataOut.flagDecodeData = True #asumo q la data esta decodificada

        if self.__profIndex == self.nCode-1: 
            self.__profIndex = 0             
            return 1
        
        self.__profIndex += 1
        
        return 1
#        dataOut.flagDeflipData = True #asumo q la data no esta sin flip


class ProfileConcat(Operation):
    
    isConfig = False
    buffer = None
    
    def __init__(self):
        
        Operation.__init__(self)
        self.profileIndex = 0
    
    def reset(self):
        self.buffer = numpy.zeros_like(self.buffer)
        self.start_index = 0
        self.times = 1
    
    def setup(self, data, m, n=1):
        self.buffer = numpy.zeros((data.shape[0],data.shape[1]*m),dtype=type(data[0,0]))
        self.nHeights = data.nHeights
        self.start_index = 0
        self.times = 1
    
    def concat(self, data):
        
        self.buffer[:,self.start_index:self.profiles*self.times] = data.copy()
        self.start_index = self.start_index + self.nHeights 
        
    def run(self, dataOut, m):
        
        dataOut.flagNoData = True
        
        if not self.isConfig:
            self.setup(dataOut.data, m, 1)
            self.isConfig = True
            
        if dataOut.flagDataAsBlock:
            raise ValueError, "ProfileConcat can only be used when voltage have been read profile by profile, getBlock = False"
        
        else:
            self.concat(dataOut.data)
            self.times += 1
            if self.times > m:
                dataOut.data = self.buffer
                self.reset()
                dataOut.flagNoData = False
                # se deben actualizar mas propiedades del header y del objeto dataOut, por ejemplo, las alturas
                deltaHeight = dataOut.heightList[1] - dataOut.heightList[0]  
                xf = dataOut.heightList[0] + dataOut.nHeights * deltaHeight * m
                dataOut.heightList = numpy.arange(dataOut.heightList[0], xf, deltaHeight) 
                dataOut.ippSeconds *= m

class ProfileSelector(Operation):
    
    profileIndex = None
    # Tamanho total de los perfiles
    nProfiles = None
    
    def __init__(self):
        
        Operation.__init__(self)
        self.profileIndex = 0
    
    def incProfileIndex(self):
        
        self.profileIndex += 1
        
        if self.profileIndex >= self.nProfiles:
            self.profileIndex = 0
    
    def isThisProfileInRange(self, profileIndex, minIndex, maxIndex):
        
        if profileIndex < minIndex:
            return False
        
        if profileIndex > maxIndex:
            return False
        
        return True
    
    def isThisProfileInList(self, profileIndex, profileList):
        
        if profileIndex not in profileList:
            return False
        
        return True
    
    def run(self, dataOut, profileList=None, profileRangeList=None, beam=None, byblock=False, rangeList = None, nProfiles=None):

        """
        ProfileSelector:
        
        Inputs:
            profileList        :    Index of profiles selected. Example: profileList = (0,1,2,7,8)     
            
            profileRangeList    :    Minimum and maximum profile indexes. Example: profileRangeList = (4, 30)
            
            rangeList            :    List of profile ranges. Example: rangeList = ((4, 30), (32, 64), (128, 256))
        
        """
        
        if rangeList is not None:
            if type(rangeList[0]) not in (tuple, list):
                rangeList = [rangeList]
        
        dataOut.flagNoData = True
            
        if dataOut.flagDataAsBlock:
            """
            data dimension  = [nChannels, nProfiles, nHeis]
            """
            if profileList != None:
                dataOut.data = dataOut.data[:,profileList,:]
                
            if profileRangeList != None:
                minIndex = profileRangeList[0]
                maxIndex = profileRangeList[1]
                profileList = range(minIndex, maxIndex+1)
                
                dataOut.data = dataOut.data[:,minIndex:maxIndex+1,:]
            
            if rangeList != None:
            
                profileList = []
                
                for thisRange in rangeList:
                    minIndex = thisRange[0]
                    maxIndex = thisRange[1]
                    
                    profileList.extend(range(minIndex, maxIndex+1))
                
                dataOut.data = dataOut.data[:,profileList,:]
                
            dataOut.nProfiles = len(profileList)
            dataOut.profileIndex = dataOut.nProfiles - 1
            dataOut.flagNoData = False
            
            return True
    
        """
        data dimension  = [nChannels, nHeis]
        """
        
        if profileList != None:
            
            if self.isThisProfileInList(dataOut.profileIndex, profileList):
                
                self.nProfiles = len(profileList)
                dataOut.nProfiles = self.nProfiles
                dataOut.profileIndex = self.profileIndex
                dataOut.flagNoData = False
                
                self.incProfileIndex()
            return True
        
        if profileRangeList != None:
            
            minIndex = profileRangeList[0]
            maxIndex = profileRangeList[1]
            
            if self.isThisProfileInRange(dataOut.profileIndex, minIndex, maxIndex):
                
                self.nProfiles = maxIndex - minIndex + 1
                dataOut.nProfiles = self.nProfiles
                dataOut.profileIndex = self.profileIndex
                dataOut.flagNoData = False
                
                self.incProfileIndex()
            return True
        
        if rangeList != None:
            
            nProfiles = 0
            
            for thisRange in rangeList:
                minIndex = thisRange[0]
                maxIndex = thisRange[1]
            
                nProfiles += maxIndex - minIndex + 1
            
            for thisRange in rangeList:
                
                minIndex = thisRange[0]
                maxIndex = thisRange[1]
            
                if self.isThisProfileInRange(dataOut.profileIndex, minIndex, maxIndex):
                    
                    self.nProfiles = nProfiles
                    dataOut.nProfiles = self.nProfiles
                    dataOut.profileIndex = self.profileIndex
                    dataOut.flagNoData = False
                
                    self.incProfileIndex()
                    
                    break
                
            return True
                    
                
        if beam != None: #beam is only for AMISR data
            if self.isThisProfileInList(dataOut.profileIndex, dataOut.beamRangeDict[beam]):
                dataOut.flagNoData = False
                dataOut.profileIndex = self.profileIndex
                
                self.incProfileIndex()
                
            return True
        
        raise ValueError, "ProfileSelector needs profileList, profileRangeList or rangeList parameter"
        
        return False    

        
        
class Reshaper(Operation):
    
    def __init__(self):
        
        Operation.__init__(self)
        
        self.__buffer = None
        self.__nitems = 0
        
    def __appendProfile(self, dataOut, nTxs):
        
        if self.__buffer is None:
            shape = (dataOut.nChannels, int(dataOut.nHeights/nTxs) )
            self.__buffer = numpy.empty(shape, dtype = dataOut.data.dtype)
            
        ini = dataOut.nHeights * self.__nitems
        end = ini + dataOut.nHeights
        
        self.__buffer[:, ini:end] = dataOut.data
        
        self.__nitems += 1
        
        return int(self.__nitems*nTxs)
    
    def __getBuffer(self):
        
        if self.__nitems == int(1./self.__nTxs):
            
            self.__nitems = 0
        
            return self.__buffer.copy()
        
        return None
    
    def __checkInputs(self, dataOut, shape, nTxs):
        
        if shape is None and nTxs is None:
            raise ValueError, "Reshaper: shape of factor should be defined"
        
        if nTxs:
            if nTxs < 0:
                raise ValueError, "nTxs should be greater than 0"
            
            if nTxs < 1 and dataOut.nProfiles % (1./nTxs) != 0:
                raise ValueError, "nProfiles= %d is not divisibled by (1./nTxs) = %f" %(dataOut.nProfiles, (1./nTxs))
            
            shape = [dataOut.nChannels, dataOut.nProfiles*nTxs, dataOut.nHeights/nTxs]
            
            return shape, nTxs
        
        if len(shape) != 2 and len(shape) !=  3:
            raise ValueError, "shape dimension should be equal to 2 or 3. shape = (nProfiles, nHeis) or (nChannels, nProfiles, nHeis). Actually shape = (%d, %d, %d)" %(dataOut.nChannels, dataOut.nProfiles, dataOut.nHeights)
        
        if len(shape) == 2:
            shape_tuple = [dataOut.nChannels]
            shape_tuple.extend(shape)
        else:
            shape_tuple = list(shape)
                
        nTxs = 1.0*shape_tuple[1]/dataOut.nProfiles
            
        return shape_tuple, nTxs
            
    def run(self, dataOut, shape=None, nTxs=None):
        
        shape_tuple, self.__nTxs = self.__checkInputs(dataOut, shape, nTxs)
        
        dataOut.flagNoData = True
        profileIndex = None
        
        if dataOut.flagDataAsBlock:
                
            dataOut.data = numpy.reshape(dataOut.data, shape_tuple)
            dataOut.flagNoData = False
            
            profileIndex = int(dataOut.nProfiles*self.__nTxs) - 1
            
        else:
            
            if self.__nTxs < 1:
                
                self.__appendProfile(dataOut, self.__nTxs)
                new_data = self.__getBuffer()
                
                if new_data is not None:
                    dataOut.data = new_data
                    dataOut.flagNoData = False
                    
                    profileIndex = dataOut.profileIndex*nTxs
                    
            else:
                raise ValueError, "nTxs should be greater than 0 and lower than 1, or use VoltageReader(..., getblock=True)"
        
        deltaHeight = dataOut.heightList[1] - dataOut.heightList[0]
        
        dataOut.heightList = numpy.arange(dataOut.nHeights/self.__nTxs) * deltaHeight + dataOut.heightList[0]
        
        dataOut.nProfiles = int(dataOut.nProfiles*self.__nTxs)
        
        dataOut.profileIndex = profileIndex
        
        dataOut.ippSeconds /= self.__nTxs
#             
# import collections
# from scipy.stats import mode
# 
# class Synchronize(Operation):
#     
#     isConfig = False
#     __profIndex = 0
#     
#     def __init__(self):
#         
#         Operation.__init__(self)
# #         self.isConfig = False
#         self.__powBuffer = None
#         self.__startIndex = 0
#         self.__pulseFound = False
#     
#     def __findTxPulse(self, dataOut, channel=0, pulse_with = None):
#         
#         #Read data
#         
#         powerdB = dataOut.getPower(channel = channel)
#         noisedB = dataOut.getNoise(channel = channel)[0]
#         
#         self.__powBuffer.extend(powerdB.flatten())
#         
#         dataArray = numpy.array(self.__powBuffer)
#         
#         filteredPower = numpy.correlate(dataArray, dataArray[0:self.__nSamples], "same")
#         
#         maxValue = numpy.nanmax(filteredPower)
#         
#         if maxValue < noisedB + 10:
#             #No se encuentra ningun pulso de transmision
#             return None
#         
#         maxValuesIndex = numpy.where(filteredPower > maxValue - 0.1*abs(maxValue))[0]
#         
#         if len(maxValuesIndex) < 2:
#             #Solo se encontro un solo pulso de transmision de un baudio, esperando por el siguiente TX
#             return None
#         
#         phasedMaxValuesIndex = maxValuesIndex - self.__nSamples
#         
#         #Seleccionar solo valores con un espaciamiento de nSamples
#         pulseIndex = numpy.intersect1d(maxValuesIndex, phasedMaxValuesIndex)
#         
#         if len(pulseIndex) < 2:
#             #Solo se encontro un pulso de transmision con ancho mayor a 1
#             return None
#         
#         spacing = pulseIndex[1:] - pulseIndex[:-1]
#         
#         #remover senales que se distancien menos de 10 unidades o muestras
#         #(No deberian existir IPP menor a 10 unidades)
#         
#         realIndex = numpy.where(spacing > 10 )[0]
#         
#         if len(realIndex) < 2:
#             #Solo se encontro un pulso de transmision con ancho mayor a 1
#             return None
#         
#         #Eliminar pulsos anchos (deja solo la diferencia entre IPPs)
#         realPulseIndex = pulseIndex[realIndex]
#         
#         period = mode(realPulseIndex[1:] - realPulseIndex[:-1])[0][0]
#         
#         print "IPP = %d samples" %period
#         
#         self.__newNSamples = dataOut.nHeights #int(period)
#         self.__startIndex = int(realPulseIndex[0])
#         
#         return 1
#         
#     
#     def setup(self, nSamples, nChannels, buffer_size = 4):
#         
#         self.__powBuffer = collections.deque(numpy.zeros( buffer_size*nSamples,dtype=numpy.float),
#                                           maxlen = buffer_size*nSamples)
#         
#         bufferList = []
#         
#         for i in range(nChannels):
#             bufferByChannel = collections.deque(numpy.zeros( buffer_size*nSamples, dtype=numpy.complex) +  numpy.NAN,
#                                           maxlen = buffer_size*nSamples)
#             
#             bufferList.append(bufferByChannel)
#             
#         self.__nSamples = nSamples
#         self.__nChannels = nChannels
#         self.__bufferList = bufferList
#     
#     def run(self, dataOut, channel = 0):
#             
#         if not self.isConfig:
#             nSamples = dataOut.nHeights
#             nChannels = dataOut.nChannels
#             self.setup(nSamples, nChannels)
#             self.isConfig = True
#         
#         #Append new data to internal buffer
#         for thisChannel in range(self.__nChannels):
#             bufferByChannel = self.__bufferList[thisChannel]
#             bufferByChannel.extend(dataOut.data[thisChannel])
#             
#         if self.__pulseFound:
#             self.__startIndex -= self.__nSamples
#         
#         #Finding Tx Pulse
#         if not self.__pulseFound:
#             indexFound = self.__findTxPulse(dataOut, channel)
#             
#             if indexFound == None:
#                 dataOut.flagNoData = True
#                 return
#             
#             self.__arrayBuffer = numpy.zeros((self.__nChannels, self.__newNSamples), dtype = numpy.complex)
#             self.__pulseFound = True
#             self.__startIndex = indexFound
#         
#         #If pulse was found ...
#         for thisChannel in range(self.__nChannels):
#             bufferByChannel = self.__bufferList[thisChannel]
#             #print self.__startIndex 
#             x = numpy.array(bufferByChannel)
#             self.__arrayBuffer[thisChannel] = x[self.__startIndex:self.__startIndex+self.__newNSamples]
#         
#         deltaHeight = dataOut.heightList[1] - dataOut.heightList[0]
#         dataOut.heightList = numpy.arange(self.__newNSamples)*deltaHeight
# #             dataOut.ippSeconds = (self.__newNSamples / deltaHeight)/1e6
#         
#         dataOut.data = self.__arrayBuffer
#         
#         self.__startIndex += self.__newNSamples
#             
#         return