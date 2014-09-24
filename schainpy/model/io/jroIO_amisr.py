'''
@author: Daniel Suarez
'''

import os
import sys
import glob
import fnmatch
import datetime
import re
import h5py
import numpy

from model.proc.jroproc_base import ProcessingUnit, Operation
from model.data.jroamisr import AMISR

class RadacHeader():
    def __init__(self, fp):
        header = 'Raw11/Data/RadacHeader'
        self.beamCodeByPulse = fp.get(header+'/BeamCode')
        self.beamCode = fp.get('Raw11/Data/Beamcodes')
        self.code = fp.get(header+'/Code')
        self.frameCount = fp.get(header+'/FrameCount')
        self.modeGroup = fp.get(header+'/ModeGroup')
        self.nsamplesPulse = fp.get(header+'/NSamplesPulse')
        self.pulseCount = fp.get(header+'/PulseCount')
        self.radacTime = fp.get(header+'/RadacTime')
        self.timeCount = fp.get(header+'/TimeCount')
        self.timeStatus = fp.get(header+'/TimeStatus')
        
        self.nrecords = self.pulseCount.shape[0] #nblocks
        self.npulses = self.pulseCount.shape[1] #nprofile
        self.nsamples = self.nsamplesPulse[0,0] #ngates
        self.nbeams = self.beamCode.shape[1]

    
    def getIndexRangeToPulse(self, idrecord=0):
        indexToZero = numpy.where(self.pulseCount.value[idrecord,:]==0)
        startPulseCountId = indexToZero[0][0]
        endPulseCountId = startPulseCountId - 1
        range1 = numpy.arange(startPulseCountId,self.npulses,1)
        range2 = numpy.arange(0,startPulseCountId,1)
        return range1, range2
    
    
class AMISRReader(ProcessingUnit):
    
    path = None
    startDate = None
    endDate = None
    startTime = None
    endTime = None
    walk = None
    isConfig = False
    
    def __init__(self):
        self.set = None
        self.subset = None
        self.extension_file = '.h5'
        self.dtc_str = 'dtc'
        self.dtc_id = 0
        self.status = True
        self.isConfig = False
        self.dirnameList = []
        self.filenameList = []
        self.fileIndex = None
        self.flagNoMoreFiles = False
        self.flagIsNewFile = 0
        self.filename = ''
        self.amisrFilePointer = None
        self.radacHeaderObj = None
        self.dataOut = self.__createObjByDefault()
        self.datablock = None
        self.rest_datablock = None
        self.range = None
        self.idrecord_count = 0
        self.profileIndex = 0
        self.idpulse_range1 = None 
        self.idpulse_range2 = None
        self.beamCodeByFrame = None
        self.radacTimeByFrame = None
        #atributos originales tal y como esta en el archivo de datos
        self.beamCodesFromFile = None
        self.radacTimeFromFile = None
        self.rangeFromFile = None
        self.dataByFrame = None
        self.dataset = None
        
        self.beamCodeDict = {}
        self.beamRangeDict = {}
        
        #experiment cgf file
        self.npulsesint_fromfile = None
        self.recordsperfile_fromfile = None
        self.nbeamcodes_fromfile = None
        self.ngates_fromfile = None
        self.ippSeconds_fromfile = None
        self.frequency_h5file = None
        
        
        self.__firstFile = True
        self.buffer_radactime = None
        
    def __createObjByDefault(self):
        
        dataObj = AMISR()
        
        return dataObj
    
    def __setParameters(self,path,startDate,endDate,startTime,endTime,walk):
        self.path = path
        self.startDate = startDate
        self.endDate = endDate
        self.startTime = startTime
        self.endTime = endTime
        self.walk = walk
    
    def __checkPath(self):
        if os.path.exists(self.path):
            self.status = 1
        else:
            self.status = 0
            print 'Path:%s does not exists'%self.path
            
        return
    
    def __selDates(self, amisr_dirname_format):
        try:
            year = int(amisr_dirname_format[0:4])
            month = int(amisr_dirname_format[4:6])
            dom = int(amisr_dirname_format[6:8])
            thisDate = datetime.date(year,month,dom)
            
            if (thisDate>=self.startDate and thisDate <= self.endDate):
                return amisr_dirname_format
        except:
            return None
    
    def __findDataForDates(self):
        
        
        
        if not(self.status):
            return None
        
        pat = '\d+.\d+'
        dirnameList = [re.search(pat,x) for x in os.listdir(self.path)]
        dirnameList = filter(lambda x:x!=None,dirnameList)
        dirnameList = [x.string for x in dirnameList]
        dirnameList = [self.__selDates(x) for x in dirnameList]
        dirnameList = filter(lambda x:x!=None,dirnameList)
        if len(dirnameList)>0:
            self.status = 1
            self.dirnameList = dirnameList
            self.dirnameList.sort()
        else:
            self.status = 0
            return None
    
    def __getTimeFromData(self):
        pass
    
    def __filterByGlob1(self, dirName):
        filter_files = glob.glob1(dirName, '*.*%s'%self.extension_file)
        filterDict = {}
        filterDict.setdefault(dirName)
        filterDict[dirName] = filter_files
        return filterDict
    
    def __getFilenameList(self, fileListInKeys, dirList):
        for value in fileListInKeys:
            dirName = value.keys()[0]
            for file in value[dirName]:
                filename = os.path.join(dirName, file)
                self.filenameList.append(filename)
    
    
    def __selectDataForTimes(self):
        #aun no esta implementado el filtro for tiempo
        if not(self.status):
            return None
        
        dirList = [os.path.join(self.path,x) for x in self.dirnameList]
        
        fileListInKeys = [self.__filterByGlob1(x) for x in dirList]
        
        self.__getFilenameList(fileListInKeys, dirList)
        
        if len(self.filenameList)>0:
            self.status = 1
            self.filenameList.sort()
        else:
            self.status = 0
            return None
        
    
    def __searchFilesOffline(self,
                            path,
                            startDate,
                            endDate,
                            startTime=datetime.time(0,0,0),
                            endTime=datetime.time(23,59,59),
                            walk=True):
        
        self.__setParameters(path, startDate, endDate, startTime, endTime, walk)
        
        self.__checkPath()
        
        self.__findDataForDates()
        
        self.__selectDataForTimes()
        
        for i in range(len(self.filenameList)):
            print "%s" %(self.filenameList[i])
        
        return

    def __setNextFileOffline(self):
        idFile = self.fileIndex

        while (True):
            idFile += 1
            if not(idFile < len(self.filenameList)):
                self.flagNoMoreFiles = 1
                print "No more Files"
                return 0

            filename = self.filenameList[idFile]

            amisrFilePointer = h5py.File(filename,'r')
            
            break

        self.flagIsNewFile = 1
        self.fileIndex = idFile
        self.filename = filename

        self.amisrFilePointer = amisrFilePointer

        print "Setting the file: %s"%self.filename

        return 1
    
    def __readHeader(self):
        self.radacHeaderObj = RadacHeader(self.amisrFilePointer)
        
        #update values from experiment cfg file
        if self.radacHeaderObj.nrecords == self.recordsperfile_fromfile:
            self.radacHeaderObj.nrecords = self.recordsperfile_fromfile
        self.radacHeaderObj.nbeams = self.nbeamcodes_fromfile
        self.radacHeaderObj.npulses = self.npulsesint_fromfile
        self.radacHeaderObj.nsamples = self.ngates_fromfile
        
        #get tuning frequency
        frequency_h5file_dataset = self.amisrFilePointer.get('Rx'+'/TuningFrequency')
        self.frequency_h5file = frequency_h5file_dataset[0,0]
        
        self.flagIsNewFile = 1
    
    def __getBeamCode(self):
        self.beamCodeDict = {}
        self.beamRangeDict = {}
        
        for i in range(len(self.radacHeaderObj.beamCode[0,:])):
            self.beamCodeDict.setdefault(i)
            self.beamRangeDict.setdefault(i)
            self.beamCodeDict[i] = self.radacHeaderObj.beamCode[0,i]
            
        
        just4record0 = self.radacHeaderObj.beamCodeByPulse[0,:]
        
        for i in range(len(self.beamCodeDict.values())):
            xx = numpy.where(just4record0==self.beamCodeDict.values()[i])
            self.beamRangeDict[i] = xx[0]
    
    def __getExpParameters(self):
        if not(self.status):
            return None
        
        experimentCfgPath = os.path.join(self.path, self.dirnameList[0], 'Setup')
        
        expFinder = glob.glob1(experimentCfgPath,'*.exp')
        if len(expFinder)== 0:
            self.status = 0
            return None
        
        experimentFilename = os.path.join(experimentCfgPath,expFinder[0])
        
        f = open(experimentFilename)
        lines = f.readlines()
        f.close()
        
        parmsList = ['npulsesint*','recordsperfile*','nbeamcodes*','ngates*']
        filterList = [fnmatch.filter(lines, x) for x in parmsList]

        
        values = [re.sub(r'\D',"",x[0]) for x in filterList]
        
        self.npulsesint_fromfile = int(values[0])
        self.recordsperfile_fromfile = int(values[1])
        self.nbeamcodes_fromfile = int(values[2])
        self.ngates_fromfile = int(values[3])
        
        tufileFinder = fnmatch.filter(lines, 'tufile=*')
        tufile = tufileFinder[0].split('=')[1].split('\n')[0]
        tufilename = os.path.join(experimentCfgPath,tufile)
        
        f = open(tufilename)
        lines = f.readlines()
        f.close()
        self.ippSeconds_fromfile = float(lines[1].split()[2])/1E6
        
        
        self.status = 1
    
    def __setIdsAndArrays(self):
        self.dataByFrame = self.__setDataByFrame()
        self.beamCodeByFrame = self.amisrFilePointer.get('Raw11/Data/RadacHeader/BeamCode').value[0, :]        
        self.readRanges()
        self.idpulse_range1, self.idpulse_range2 = self.radacHeaderObj.getIndexRangeToPulse(0)
        self.radacTimeByFrame = numpy.zeros(self.radacHeaderObj.npulses)
        self.buffer_radactime = numpy.zeros_like(self.radacTimeByFrame)
        
    
    def __setNextFile(self):
        
        newFile = self.__setNextFileOffline()
        
        if not(newFile):
            return 0
        
        self.__readHeader()
        
        if self.__firstFile:
            self.__setIdsAndArrays()
            self.__firstFile = False
        
        self.__getBeamCode()
        self.readDataBlock()

    
    def setup(self,path=None,
                    startDate=None, 
                    endDate=None, 
                    startTime=datetime.time(0,0,0), 
                    endTime=datetime.time(23,59,59),
                    walk=True):
        
        #Busqueda de archivos offline
        self.__searchFilesOffline(path, startDate, endDate, startTime, endTime, walk)
        
        if not(self.filenameList):
            print "There is no files into the folder: %s"%(path)
                
            sys.exit(-1)

        self.__getExpParameters()

        self.fileIndex = -1
        
        self.__setNextFile()
    
    def readRanges(self):
        dataset = self.amisrFilePointer.get('Raw11/Data/Samples/Range')
        #self.rangeFromFile = dataset.value
        self.rangeFromFile = numpy.reshape(dataset.value,(-1))
        return range
    
    
    def readRadacTime(self,idrecord, range1, range2):
        self.radacTimeFromFile = self.radacHeaderObj.radacTime.value
        
        radacTimeByFrame = numpy.zeros((self.radacHeaderObj.npulses))
        #radacTimeByFrame = dataset[idrecord - 1,range1]
        #radacTimeByFrame = dataset[idrecord,range2]
        
        return radacTimeByFrame
        
    def readBeamCode(self, idrecord, range1, range2):
        dataset = self.amisrFilePointer.get('Raw11/Data/RadacHeader/BeamCode')
        beamcodeByFrame = numpy.zeros((self.radacHeaderObj.npulses))
        self.beamCodesFromFile = dataset.value
        
        #beamcodeByFrame[range1] = dataset[idrecord - 1, range1]
        #beamcodeByFrame[range2] = dataset[idrecord, range2]
        beamcodeByFrame[range1] = dataset[idrecord, range1]
        beamcodeByFrame[range2] = dataset[idrecord, range2]
        
        return beamcodeByFrame
    
    
    def __setDataByFrame(self):
        ndata = 2 # porque es complejo
        dataByFrame = numpy.zeros((self.radacHeaderObj.npulses, self.radacHeaderObj.nsamples, ndata))
        return dataByFrame
    
    def __readDataSet(self):
        dataset = self.amisrFilePointer.get('Raw11/Data/Samples/Data')
        return dataset

    def __setDataBlock(self,):
        real = self.dataByFrame[:,:,0] #asumo que 0 es real
        imag = self.dataByFrame[:,:,1] #asumo que 1 es imaginario
        datablock = real + imag*1j #armo el complejo
        return datablock
    
    def readSamples_version1(self,idrecord):
        #estas tres primeras lineas solo se deben ejecutar una vez
        if self.flagIsNewFile:
            #reading dataset
            self.dataset = self.__readDataSet()    
            self.flagIsNewFile = 0
        
        if idrecord == 0:
            #if self.buffer_last_record == None:
            selectorById = self.radacHeaderObj.pulseCount[0,self.idpulse_range2]
            
            self.dataByFrame[selectorById,:,:] = self.dataset[0, self.idpulse_range2,:,:]
        
            self.radacTimeByFrame[selectorById] = self.radacHeaderObj.radacTime[0, self.idpulse_range2]
            
            selectorById = self.radacHeaderObj.pulseCount[0,self.idpulse_range1]
            
            self.radacTimeByFrame[selectorById] = self.buffer_radactime[selectorById]
            
            datablock = self.__setDataBlock()
            
            return datablock
                
        selectorById = self.radacHeaderObj.pulseCount[idrecord-1,self.idpulse_range1]
        self.dataByFrame[selectorById,:,:] = self.dataset[idrecord-1, self.idpulse_range1, :, :]
        self.radacTimeByFrame[selectorById] = self.radacHeaderObj.radacTime[idrecord-1, self.idpulse_range1]
        
        selectorById = self.radacHeaderObj.pulseCount[idrecord,self.idpulse_range2]#data incompleta ultimo archivo de carpeta, verifica el record real segun la dimension del arreglo de datos
        self.dataByFrame[selectorById,:,:] = self.dataset[idrecord, self.idpulse_range2, :, :]
        self.radacTimeByFrame[selectorById] = self.radacHeaderObj.radacTime[idrecord, self.idpulse_range2]
        
        datablock = self.__setDataBlock()        
        
        selectorById = self.radacHeaderObj.pulseCount[idrecord,self.idpulse_range1]
        self.dataByFrame[selectorById,:,:] = self.dataset[idrecord, self.idpulse_range1, :, :]
        self.buffer_radactime[selectorById] = self.radacHeaderObj.radacTime[idrecord, self.idpulse_range1]
        
        return datablock
        
    
    def readSamples(self,idrecord):
        if self.flagIsNewFile:
            self.dataByFrame = self.__setDataByFrame()        
            self.beamCodeByFrame = self.amisrFilePointer.get('Raw11/Data/RadacHeader/BeamCode').value[idrecord, :]
                
            #reading ranges
            self.readRanges()
            #reading dataset
            self.dataset = self.__readDataSet()
        
        self.flagIsNewFile = 0
        self.radacTimeByFrame = self.radacHeaderObj.radacTime.value[idrecord, :]
        self.dataByFrame = self.dataset[idrecord, :, :, :]
        datablock = self.__setDataBlock()
        return datablock
    
    
    def readDataBlock(self):
        
        self.datablock = self.readSamples_version1(self.idrecord_count)
        #self.datablock = self.readSamples(self.idrecord_count)
        #print 'record:', self.idrecord_count
        
        self.idrecord_count += 1 
        self.profileIndex = 0
        
        if self.idrecord_count >= self.radacHeaderObj.nrecords:
            self.idrecord_count = 0
            self.flagIsNewFile = 1
    
    def readNextBlock(self):
        
        self.readDataBlock()
        
        if self.flagIsNewFile:
            self.__setNextFile()
        pass
    
    def __hasNotDataInBuffer(self):
        #self.radacHeaderObj.npulses debe ser otra variable para considerar el numero de pulsos a tomar en el primer y ultimo record
        if self.profileIndex >= self.radacHeaderObj.npulses:
            return 1
        return 0
    
    def printUTC(self):
        print self.dataOut.utctime
        print ''
    
    def setObjProperties(self):
        self.dataOut.heightList = self.rangeFromFile/1000.0 #km
        self.dataOut.nProfiles = self.radacHeaderObj.npulses
        self.dataOut.nRecords = self.radacHeaderObj.nrecords
        self.dataOut.nBeams = self.radacHeaderObj.nbeams
        self.dataOut.ippSeconds = self.ippSeconds_fromfile
        self.dataOut.timeInterval = self.dataOut.ippSeconds * self.dataOut.nCohInt
        self.dataOut.frequency = self.frequency_h5file
        self.dataOut.nBaud = None
        self.dataOut.nCode = None
        self.dataOut.code = None
        
        self.dataOut.beamCodeDict = self.beamCodeDict
        self.dataOut.beamRangeDict = self.beamRangeDict
    
    def getData(self):
        
        if self.flagNoMoreFiles:
            self.dataOut.flagNoData = True
            print 'Process finished'
            return 0
        
        if self.__hasNotDataInBuffer():
            self.readNextBlock()

        
        if self.datablock == None: # setear esta condicion cuando no hayan datos por leers
            self.dataOut.flagNoData = True 
            return 0
        
        self.dataOut.data = numpy.reshape(self.datablock[self.profileIndex,:],(1,-1))
        
        self.dataOut.utctime = self.radacTimeByFrame[self.profileIndex]
        
        self.dataOut.flagNoData = False
        
        self.profileIndex += 1
        
        return self.dataOut.data


    def run(self, **kwargs):
        if not(self.isConfig):
            self.setup(**kwargs)
            self.setObjProperties()
            self.isConfig = True
        
        self.getData()
