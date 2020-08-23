'''
Created on Jul 3, 2014

@author: roj-idl71
'''
import os
import datetime
import numpy

try:
    from gevent import sleep
except:
    from time import sleep

from schainpy.model.data.jroheaderIO import RadarControllerHeader, SystemHeader
from schainpy.model.data.jrodata import Voltage
from schainpy.model.proc.jroproc_base import ProcessingUnit, Operation, MPDecorator

try:
    import digital_rf_hdf5
except:
    pass

class USRPReader(ProcessingUnit):
    '''
    classdocs
    '''

    def __init__(self, **kwargs):
        '''
        Constructor
        '''

        ProcessingUnit.__init__(self, **kwargs)

        self.dataOut = Voltage()
        self.__printInfo = True
        self.__flagDiscontinuousBlock = False
        self.__bufferIndex = 9999999

        self.__ippKm = None
        self.__codeType = 0
        self.__nCode = None
        self.__nBaud = None
        self.__code = None

    def __getCurrentSecond(self):

        return self.__thisUnixSample/self.__sample_rate

    thisSecond = property(__getCurrentSecond, "I'm the 'thisSecond' property.")

    def __setFileHeader(self):
        '''
        In this method will be initialized every parameter of dataOut object (header, no data)
        '''
        ippSeconds = 1.0*self.__nSamples/self.__sample_rate

        nProfiles = 1.0/ippSeconds  #Number of profiles in one second

        self.dataOut.radarControllerHeaderObj = RadarControllerHeader(ipp=self.__ippKm,
                                                                      txA=0,
                                                                      txB=0,
                                                                      nWindows=1,
                                                                      nHeights=self.__nSamples,
                                                                      firstHeight=self.__firstHeigth,
                                                                      deltaHeight=self.__deltaHeigth,
                                                                      codeType=self.__codeType,
                                                                      nCode=self.__nCode, nBaud=self.__nBaud,
                                                                      code = self.__code)

        self.dataOut.systemHeaderObj = SystemHeader(nSamples=self.__nSamples,
                                                    nProfiles=nProfiles,
                                                    nChannels=len(self.__channelList),
                                                    adcResolution=14)

        self.dataOut.type = "Voltage"

        self.dataOut.data = None

        self.dataOut.dtype = numpy.dtype([('real','<i8'),('imag','<i8')])

#        self.dataOut.nChannels = 0

#        self.dataOut.nHeights = 0

        self.dataOut.nProfiles = nProfiles

        self.dataOut.heightList = self.__firstHeigth + numpy.arange(self.__nSamples, dtype = numpy.float)*self.__deltaHeigth

        self.dataOut.channelList = self.__channelList

        self.dataOut.blocksize = self.dataOut.getNChannels() * self.dataOut.getNHeights()

#        self.dataOut.channelIndexList = None

        self.dataOut.flagNoData = True

        #Set to TRUE if the data is discontinuous
        self.dataOut.flagDiscontinuousBlock = False

        self.dataOut.utctime = None

        self.dataOut.timeZone = self.__timezone/60  #timezone like jroheader, difference in minutes between UTC and localtime

        self.dataOut.dstFlag = 0

        self.dataOut.errorCount = 0

        self.dataOut.nCohInt = 1

        self.dataOut.flagDecodeData = False #asumo que la data esta decodificada

        self.dataOut.flagDeflipData = False #asumo que la data esta sin flip

        self.dataOut.flagShiftFFT = False

        self.dataOut.ippSeconds = ippSeconds

        #Time interval between profiles
        #self.dataOut.timeInterval = self.dataOut.ippSeconds * self.dataOut.nCohInt

        self.dataOut.frequency = self.__frequency

        self.dataOut.realtime = self.__online

    def findDatafiles(self, path, startDate=None, endDate=None):

        if not os.path.isdir(path):
            return []

        try:
            digitalReadObj = digital_rf_hdf5.read_hdf5(path, load_all_metadata=True)
        except:
            digitalReadObj = digital_rf_hdf5.read_hdf5(path)

        channelNameList = digitalReadObj.get_channels()

        if not channelNameList:
            return []

        metadata_dict = digitalReadObj.get_rf_file_metadata(channelNameList[0])

        sample_rate = metadata_dict['sample_rate'][0]

        this_metadata_file = digitalReadObj.get_metadata(channelNameList[0])

        try:
            timezone = this_metadata_file['timezone'].value
        except:
            timezone = 0

        startUTCSecond, endUTCSecond = digitalReadObj.get_bounds(channelNameList[0])/sample_rate - timezone

        startDatetime = datetime.datetime.utcfromtimestamp(startUTCSecond)
        endDatatime = datetime.datetime.utcfromtimestamp(endUTCSecond)

        if not startDate:
            startDate = startDatetime.date()

        if not endDate:
            endDate = endDatatime.date()

        dateList = []

        thisDatetime = startDatetime

        while(thisDatetime<=endDatatime):

            thisDate = thisDatetime.date()

            if thisDate < startDate:
                continue

            if thisDate > endDate:
                break

            dateList.append(thisDate)
            thisDatetime += datetime.timedelta(1)

        return dateList

    def setup(self, path = None,
                    startDate = None,
                    endDate = None,
                    startTime = datetime.time(0,0,0),
                    endTime = datetime.time(23,59,59),
                    channelList = None,
                    nSamples = None,
                    ippKm = 60,
                    online = False,
                    delay = 60,
                    buffer_size = 1024,
                    **kwargs):
        '''
        In this method we should set all initial parameters.

        Inputs:
            path
            startDate
            endDate
            startTime
            endTime
            set
            expLabel
            ext
            online
            delay
        '''

        if not os.path.isdir(path):
            raise ValueError("[Reading] Directory %s does not exist" %path)

        try:
            self.digitalReadObj = digital_rf_hdf5.read_hdf5(path, load_all_metadata=True)
        except:
            self.digitalReadObj = digital_rf_hdf5.read_hdf5(path)

        channelNameList = self.digitalReadObj.get_channels()

        if not channelNameList:
            raise ValueError("[Reading] Directory %s does not have any files" %path)

        if not channelList:
            channelList = list(range(len(channelNameList)))

        ##########  Reading metadata ######################

        metadata_dict = self.digitalReadObj.get_rf_file_metadata(channelNameList[channelList[0]])

        self.__sample_rate = metadata_dict['sample_rate'][0]
#         self.__samples_per_file = metadata_dict['samples_per_file'][0]
        self.__deltaHeigth = 1e6*0.15/self.__sample_rate

        this_metadata_file = self.digitalReadObj.get_metadata(channelNameList[channelList[0]])

        self.__frequency = None
        try:
            self.__frequency = this_metadata_file['center_frequencies'].value
        except:
            self.__frequency = this_metadata_file['fc'].value

        if not self.__frequency:
            raise ValueError("Center Frequency is not defined in metadata file")

        try:
            self.__timezone = this_metadata_file['timezone'].value
        except:
            self.__timezone = 0

        self.__firstHeigth = 0

        try:
            codeType = this_metadata_file['codeType'].value
        except:
            codeType = 0

        nCode = 1
        nBaud = 1
        code = numpy.ones((nCode, nBaud), dtype=numpy.int)

        if codeType:
            nCode = this_metadata_file['nCode'].value
            nBaud = this_metadata_file['nBaud'].value
            code = this_metadata_file['code'].value

        if not ippKm:
            try:
                #seconds to km
                ippKm = 1e6*0.15*this_metadata_file['ipp'].value
            except:
                ippKm = None

        ####################################################
        startUTCSecond = None
        endUTCSecond = None

        if startDate:
            startDatetime = datetime.datetime.combine(startDate, startTime)
            startUTCSecond = (startDatetime-datetime.datetime(1970,1,1)).total_seconds() + self.__timezone

        if endDate:
            endDatetime = datetime.datetime.combine(endDate, endTime)
            endUTCSecond = (endDatetime-datetime.datetime(1970,1,1)).total_seconds() + self.__timezone

        start_index, end_index = self.digitalReadObj.get_bounds(channelNameList[channelList[0]])

        if not startUTCSecond:
            startUTCSecond = start_index/self.__sample_rate

        if start_index > startUTCSecond*self.__sample_rate:
            startUTCSecond = start_index/self.__sample_rate

        if not endUTCSecond:
            endUTCSecond = end_index/self.__sample_rate

        if end_index < endUTCSecond*self.__sample_rate:
            endUTCSecond = end_index/self.__sample_rate

        if not nSamples:
            if not ippKm:
                raise ValueError("[Reading] nSamples or ippKm should be defined")

            nSamples = int(ippKm / (1e6*0.15/self.__sample_rate))

        channelBoundList = []
        channelNameListFiltered = []

        for thisIndexChannel in channelList:
            thisChannelName =  channelNameList[thisIndexChannel]
            start_index, end_index = self.digitalReadObj.get_bounds(thisChannelName)
            channelBoundList.append((start_index, end_index))
            channelNameListFiltered.append(thisChannelName)

        self.profileIndex = 0

        self.__delay = delay
        self.__ippKm = ippKm
        self.__codeType = codeType
        self.__nCode = nCode
        self.__nBaud = nBaud
        self.__code = code

        self.__datapath = path
        self.__online = online
        self.__channelList = channelList
        self.__channelNameList = channelNameListFiltered
        self.__channelBoundList = channelBoundList
        self.__nSamples = nSamples
        self.__samples_to_read = int(buffer_size*nSamples)
        self.__nChannels = len(self.__channelList)

        self.__startUTCSecond = startUTCSecond
        self.__endUTCSecond = endUTCSecond

        self.__timeInterval = 1.0 * self.__samples_to_read/self.__sample_rate #Time interval

        if online:
#             self.__thisUnixSample = int(endUTCSecond*self.__sample_rate - 4*self.__samples_to_read)
            startUTCSecond = numpy.floor(endUTCSecond)

        self.__thisUnixSample = int(startUTCSecond*self.__sample_rate) - self.__samples_to_read

        self.__data_buffer = numpy.zeros((self.__nChannels, self.__samples_to_read), dtype = numpy.complex)

        self.__setFileHeader()
        self.isConfig = True

        print("[Reading] USRP Data was found from %s to %s " %(
                                                      datetime.datetime.utcfromtimestamp(self.__startUTCSecond - self.__timezone),
                                                      datetime.datetime.utcfromtimestamp(self.__endUTCSecond - self.__timezone)
                                                      ))

        print("[Reading] Starting process from %s to %s" %(datetime.datetime.utcfromtimestamp(startUTCSecond - self.__timezone),
                                                           datetime.datetime.utcfromtimestamp(endUTCSecond - self.__timezone)
                                                           ))

    def __reload(self):

        if not self.__online:
            return

#         print
#         print "%s not in range [%s, %s]" %(
#                                           datetime.datetime.utcfromtimestamp(self.thisSecond - self.__timezone),
#                                           datetime.datetime.utcfromtimestamp(self.__startUTCSecond - self.__timezone),
#                                           datetime.datetime.utcfromtimestamp(self.__endUTCSecond - self.__timezone)
#                                           )
        print("[Reading] reloading metadata ...")

        try:
            self.digitalReadObj.reload(complete_update=True)
        except:
            self.digitalReadObj.reload()

        start_index, end_index = self.digitalReadObj.get_bounds(self.__channelNameList[self.__channelList[0]])

        if start_index > self.__startUTCSecond*self.__sample_rate:
            self.__startUTCSecond = 1.0*start_index/self.__sample_rate

        if end_index > self.__endUTCSecond*self.__sample_rate:
            self.__endUTCSecond = 1.0*end_index/self.__sample_rate
            print()
            print("[Reading] New timerange found [%s, %s] " %(
                                                      datetime.datetime.utcfromtimestamp(self.__startUTCSecond - self.__timezone),
                                                      datetime.datetime.utcfromtimestamp(self.__endUTCSecond - self.__timezone)
                                                      ))

            return True

        return False

    def __readNextBlock(self, seconds=30, volt_scale = 218776):
        '''
        '''

        #Set the next data
        self.__flagDiscontinuousBlock = False
        self.__thisUnixSample += self.__samples_to_read

        if self.__thisUnixSample + 2*self.__samples_to_read > self.__endUTCSecond*self.__sample_rate:
            print("[Reading] There are no more data into selected time-range")

            self.__reload()

            if self.__thisUnixSample + 2*self.__samples_to_read > self.__endUTCSecond*self.__sample_rate:
                self.__thisUnixSample -=  self.__samples_to_read
                return False

        indexChannel = 0

        dataOk = False

        for thisChannelName in self.__channelNameList:

            try:
                result = self.digitalReadObj.read_vector_c81d(self.__thisUnixSample,
                                                              self.__samples_to_read,
                                                              thisChannelName)

            except IOError as e:
                #read next profile
                self.__flagDiscontinuousBlock = True
                print("[Reading] %s" %datetime.datetime.utcfromtimestamp(self.thisSecond - self.__timezone), e)
                break

            if result.shape[0] != self.__samples_to_read:
                self.__flagDiscontinuousBlock = True
                print("[Reading] %s: Too few samples were found, just %d/%d  samples" %(datetime.datetime.utcfromtimestamp(self.thisSecond - self.__timezone),
                                                                                result.shape[0],
                                                                                self.__samples_to_read))
                break

            self.__data_buffer[indexChannel,:] = result*volt_scale

            indexChannel += 1

            dataOk = True

        self.__utctime = self.__thisUnixSample/self.__sample_rate

        if not dataOk:
            return False

        print("[Reading] %s: %d samples <> %f sec" %(datetime.datetime.utcfromtimestamp(self.thisSecond - self.__timezone),
                                                         self.__samples_to_read,
                                                         self.__timeInterval))

        self.__bufferIndex = 0

        return True

    def __isBufferEmpty(self):

        if self.__bufferIndex <= self.__samples_to_read - self.__nSamples:
            return False

        return True

    def getData(self, seconds=30, nTries=5):

        '''
        This method gets the data from files and put the data into the dataOut object

        In addition, increase el the buffer counter in one.

        Return:
            data    :    retorna un perfil de voltages (alturas * canales) copiados desde el
                         buffer. Si no hay mas archivos a leer retorna None.

        Affected:
            self.dataOut
            self.profileIndex
            self.flagDiscontinuousBlock
            self.flagIsNewBlock
        '''

        err_counter = 0
        self.dataOut.flagNoData = True

        if self.__isBufferEmpty():

            self.__flagDiscontinuousBlock = False

            while True:
                if self.__readNextBlock():
                    break

                if self.__thisUnixSample > self.__endUTCSecond*self.__sample_rate:
                    return False

                if self.__flagDiscontinuousBlock:
                    print('[Reading] discontinuous block found ... continue with the next block')
                    continue

                if not self.__online:
                    return False

                err_counter += 1
                if err_counter > nTries:
                    return False

                print('[Reading] waiting %d seconds to read a new block' %seconds)
                sleep(seconds)

        self.dataOut.data = self.__data_buffer[:,self.__bufferIndex:self.__bufferIndex+self.__nSamples]
        self.dataOut.utctime = (self.__thisUnixSample + self.__bufferIndex)/self.__sample_rate
        self.dataOut.flagNoData = False
        self.dataOut.flagDiscontinuousBlock = self.__flagDiscontinuousBlock
        self.dataOut.profileIndex = self.profileIndex

        self.__bufferIndex += self.__nSamples
        self.profileIndex += 1

        if self.profileIndex == self.dataOut.nProfiles:
            self.profileIndex = 0

        return True

    def printInfo(self):
        '''
        '''
        if self.__printInfo == False:
            return

#         self.systemHeaderObj.printInfo()
#         self.radarControllerHeaderObj.printInfo()

        self.__printInfo = False

    def printNumberOfBlock(self):
        '''
        '''

        print(self.profileIndex)

    def run(self, **kwargs):
        '''
        This method will be called many times so here you should put all your code
        '''

        if not self.isConfig:
            self.setup(**kwargs)

        self.getData(seconds=self.__delay)

        return


@MPDecorator
class USRPWriter(Operation):
    '''
    classdocs
    '''

    def __init__(self, **kwargs):
        '''
        Constructor
        '''
        Operation.__init__(self, **kwargs)
        self.dataOut = None

    def setup(self, dataIn, path, blocksPerFile, set=0, ext=None):
        '''
        In this method we should set all initial parameters.

        Input:
            dataIn        :        Input data will also be outputa data

        '''
        self.dataOut = dataIn





        self.isConfig = True

        return

    def run(self, dataIn, **kwargs):
        '''
        This method will be called many times so here you should put all your code

        Inputs:

            dataIn        :        object with the data

        '''

        if not self.isConfig:
            self.setup(dataIn, **kwargs)


if __name__ == '__main__':

    readObj = USRPReader()

    while True:
        readObj.run(path='/Volumes/DATA/haystack/passive_radar/')
#         readObj.printInfo()
        readObj.printNumberOfBlock()