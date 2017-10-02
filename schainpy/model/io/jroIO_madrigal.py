'''
Created on Aug 1, 2017

@author: Juan C. Espinoza
'''

import os
import sys
import time
import json
import glob
import datetime

import numpy
import h5py

try:
    import madrigal
    import madrigal.cedar
except:
    print 'You should install "madrigal library" module if you want to read/write Madrigal data'

from schainpy.model.io.jroIO_base import JRODataReader 
from schainpy.model.proc.jroproc_base import ProcessingUnit, Operation
from schainpy.model.data.jrodata import Parameters
from schainpy.utils import log


DEF_CATALOG = {
    'principleInvestigator': 'Marco Milla',
    'expPurpose': None,
    'expMode': None,
    'cycleTime': None,
    'correlativeExp': None,
    'sciRemarks': None,
    'instRemarks': None
    }
DEF_HEADER = {
    'kindatDesc': None,
    'analyst': 'Jicamarca User',
    'comments': None,
    'history': None
    }
MNEMONICS = {
    10: 'jro',
    11: 'jbr',
    840: 'jul',
    13: 'jas',
    1000: 'pbr',
    1001: 'hbr',
    1002: 'obr',
}

UT1970 = datetime.datetime(1970, 1, 1) - datetime.timedelta(seconds=time.timezone)

def load_json(obj):
    '''
    Parse json as string instead of unicode
    '''

    if isinstance(obj, str):
        iterable = json.loads(obj)

    if isinstance(iterable, dict):
        return {str(k): load_json(v) if isinstance(v, dict) else str(v) if isinstance(v, unicode) else v
            for k, v in iterable.items()}
    elif isinstance(iterable, (list, tuple)):
        return [str(v) if isinstance(v, unicode) else v for v in iterable]
    
    return iterable


class MADReader(JRODataReader, ProcessingUnit):

    def __init__(self, **kwargs):

        ProcessingUnit.__init__(self, **kwargs)

        self.dataOut = Parameters()    
        self.counter_records = 0
        self.nrecords = None
        self.flagNoMoreFiles = 0
        self.isConfig = False        
        self.filename = None        
        self.intervals = set()
        
    def setup(self,
              path=None,
              startDate=None,
              endDate=None,
              format=None,
              startTime=datetime.time(0, 0, 0),
              endTime=datetime.time(23, 59, 59),
              **kwargs):
        
        self.started = True
        self.path = path
        self.startDate = startDate
        self.endDate = endDate
        self.startTime = startTime
        self.endTime = endTime
        self.datatime = datetime.datetime(1900,1,1)
        self.oneDDict = load_json(kwargs.get('oneDDict', 
                                             "{\"GDLATR\":\"lat\", \"GDLONR\":\"lon\"}"))
        self.twoDDict = load_json(kwargs.get('twoDDict',
                                             "{\"GDALT\": \"heightList\"}"))
        self.ind2DList = load_json(kwargs.get('ind2DList',
                                              "[\"GDALT\"]"))
        if self.path is None:
            raise ValueError, 'The path is not valid'

        if format is None:
            raise ValueError, 'The format is not valid choose simple or hdf5'
        elif format.lower() in ('simple', 'txt'):
            self.ext = '.txt'
        elif format.lower() in ('cedar',):
            self.ext = '.001'
        else:
            self.ext = '.hdf5'

        self.search_files(self.path)
        self.fileId = 0

        if not self.fileList:
            raise  Warning, 'There is no files matching these date in the folder: {}. \n Check startDate and endDate'.format(path)

        self.setNextFile()
        
    def search_files(self, path):
        '''
         Searching for madrigal files in path
         Creating a list of files to procces included in [startDate,endDate]
         
         Input: 
             path - Path to find files             
        '''    

        print 'Searching files {} in {} '.format(self.ext, path)
        foldercounter = 0        
        fileList0 = glob.glob1(path, '*{}'.format(self.ext))
        fileList0.sort()

        self.fileList = []
        self.dateFileList = []

        startDate = self.startDate - datetime.timedelta(1)
        endDate = self.endDate + datetime.timedelta(1)

        for thisFile in fileList0:
            year = thisFile[3:7]
            if not year.isdigit():
                continue

            month = thisFile[7:9]
            if not month.isdigit():
                continue

            day = thisFile[9:11]
            if not day.isdigit():
                continue

            year, month, day = int(year), int(month), int(day)
            dateFile = datetime.date(year, month, day)

            if (startDate > dateFile) or (endDate < dateFile):
                continue

            self.fileList.append(thisFile)
            self.dateFileList.append(dateFile)

        return

    def parseHeader(self):
        '''
        '''

        self.output = {}
        self.version = '2'
        s_parameters = None
        if self.ext == '.txt':
            self.parameters = [s.strip().lower() for s in self.fp.readline().strip().split(' ') if s]
        elif self.ext == '.hdf5':
            metadata = self.fp['Metadata']
            data = self.fp['Data']['Array Layout']
            if 'Independent Spatial Parameters' in metadata:
                s_parameters = [s[0].lower() for s in metadata['Independent Spatial Parameters']]
                self.version = '3'
            one = [s[0].lower() for s in data['1D Parameters']['Data Parameters']]
            one_d = [1 for s in one]
            two = [s[0].lower() for s in data['2D Parameters']['Data Parameters']]
            two_d = [2 for s in two]
            self.parameters = one + two
            self.parameters_d = one_d + two_d

        log.success('Parameters found: {}'.format(','.join(self.parameters)),
                    'MADReader')
        if s_parameters:
            log.success('Spatial parameters: {}'.format(','.join(s_parameters)),
                        'MADReader')
        
        for param in self.oneDDict.keys():
            if param.lower() not in self.parameters:
                print('\x1b[33m[Warning]\x1b[0m Parameter \x1b[1;32m{}\x1b[0m not found will be ignored'.format(
                    param
                ))
                self.oneDDict.pop(param, None)
        
        for param, value in self.twoDDict.items():
            if param.lower() not in self.parameters:
                print('\x1b[33m[Warning]\x1b[0m Parameter \x1b[1;32m{}\x1b[0m not found will be ignored'.format(
                    param
                ))
                self.twoDDict.pop(param, None)
                continue
            if isinstance(value, list):
                if value[0] not in self.output:
                    self.output[value[0]] = []
                self.output[value[0]].append(None)

    def parseData(self):
        '''
        '''

        if self.ext == '.txt':
            self.data = numpy.genfromtxt(self.fp, missing_values=('missing'))
            self.nrecords = self.data.shape[0]
            self.ranges = numpy.unique(self.data[:,self.parameters.index(self.ind2DList[0].lower())])
        elif self.ext == '.hdf5':
            self.data = self.fp['Data']['Array Layout']
            self.nrecords = len(self.data['timestamps'].value) 
            self.ranges = self.data['range'].value

    def setNextFile(self):
        '''
        '''

        file_id = self.fileId

        if file_id == len(self.fileList):
            print '\nNo more files in the folder'
            print 'Total number of file(s) read : {}'.format(self.fileId)            
            self.flagNoMoreFiles = 1
            return 0
        
        print('\x1b[32m[Info]\x1b[0m Opening: {}'.format(
            self.fileList[file_id]
            ))
        filename = os.path.join(self.path, self.fileList[file_id])
        
        if self.filename is not None:
            self.fp.close()
        
        self.filename = filename
        self.filedate = self.dateFileList[file_id]

        if self.ext=='.hdf5':
            self.fp = h5py.File(self.filename, 'r')
        else:
            self.fp = open(self.filename, 'rb')

        self.parseHeader()
        self.parseData()
        self.sizeOfFile = os.path.getsize(self.filename)
        self.counter_records = 0
        self.flagIsNewFile = 0
        self.fileId += 1

        return 1

    def readNextBlock(self):

        while True:

            if self.flagIsNewFile:                
                if not self.setNextFile():                    
                    return 0

            self.readBlock()
            
            if (self.datatime < datetime.datetime.combine(self.startDate, self.startTime)) or \
               (self.datatime > datetime.datetime.combine(self.endDate, self.endTime)):
                print "\x1b[32m[Reading]\x1b[0m Record No. %d/%d -> %s \x1b[33m[Skipping]\x1b[0m" %(
                    self.counter_records,
                    self.nrecords,
                    self.datatime.ctime())
                continue
            break

        print "\x1b[32m[Reading]\x1b[0m Record No. %d/%d -> %s" %(
            self.counter_records,
            self.nrecords,
            self.datatime.ctime())

        return 1

    def readBlock(self):
        '''
        '''
        dum = []
        if self.ext == '.txt':
            dt = self.data[self.counter_records][:6].astype(int)
            self.datatime = datetime.datetime(dt[0], dt[1], dt[2], dt[3], dt[4], dt[5])
            while True:
                dt = self.data[self.counter_records][:6].astype(int)
                datatime = datetime.datetime(dt[0], dt[1], dt[2], dt[3], dt[4], dt[5])
                if datatime == self.datatime:
                    dum.append(self.data[self.counter_records])
                    self.counter_records += 1
                    if self.counter_records == self.nrecords:
                        self.flagIsNewFile = True
                        break
                    continue
                self.intervals.add((datatime-self.datatime).seconds)
                break
        elif self.ext == '.hdf5':
            datatime = datetime.datetime.utcfromtimestamp(
                self.data['timestamps'][self.counter_records])
            nHeights = len(self.ranges)
            for n, param in enumerate(self.parameters):
                if self.parameters_d[n] == 1:
                    dum.append(numpy.ones(nHeights)*self.data['1D Parameters'][param][self.counter_records])
                else:
                    if self.version == '2':
                        dum.append(self.data['2D Parameters'][param][self.counter_records])
                    else:
                        tmp = self.data['2D Parameters'][param].value.T
                        dum.append(tmp[self.counter_records])
            self.intervals.add((datatime-self.datatime).seconds)
            self.datatime = datatime
            self.counter_records += 1
            if self.counter_records == self.nrecords:
                self.flagIsNewFile = True
        
        self.buffer = numpy.array(dum)        
        return

    def set_output(self):
        '''
        Storing data from buffer to dataOut object
        '''        

        parameters = [None for __ in self.parameters]

        for param, attr in self.oneDDict.items():            
            x = self.parameters.index(param.lower())
            setattr(self.dataOut, attr, self.buffer[0][x])
        
        for param, value in self.twoDDict.items():            
            x = self.parameters.index(param.lower())
            if self.ext == '.txt':
                y = self.parameters.index(self.ind2DList[0].lower())            
                ranges = self.buffer[:,y]
                if self.ranges.size == ranges.size:
                    continue
                index = numpy.where(numpy.in1d(self.ranges, ranges))[0]
                dummy = numpy.zeros(self.ranges.shape) + numpy.nan
                dummy[index] = self.buffer[:,x]
            else:
                
                dummy = self.buffer[x]
                
            if isinstance(value, str):
                if value not in self.ind2DList:             
                    setattr(self.dataOut, value, dummy.reshape(1,-1))
            elif isinstance(value, list):                
                self.output[value[0]][value[1]] = dummy
                parameters[value[1]] = param

        for key, value in self.output.items():
            setattr(self.dataOut, key, numpy.array(value))

        self.dataOut.parameters = [s for s in parameters if s]
        self.dataOut.heightList = self.ranges
        self.dataOut.utctime = (self.datatime - UT1970).total_seconds()
        self.dataOut.utctimeInit = self.dataOut.utctime  
        self.dataOut.paramInterval = min(self.intervals)
        self.dataOut.useLocalTime = False        
        self.dataOut.flagNoData = False
        self.dataOut.started = self.started

    def getData(self):
        '''
        Storing data from databuffer to dataOut object
        '''
        if self.flagNoMoreFiles:
            self.dataOut.flagNoData = True
            print 'No file left to process'
            return 0

        if not  self.readNextBlock():
            self.dataOut.flagNoData = True
            return 0

        self.set_output()

        return 1


class MAD2Writer(Operation):

    missing = -32767
    ext = '.dat'
    
    def __init__(self, **kwargs):
        
        Operation.__init__(self, **kwargs)
        self.dataOut = Parameters()
        self.path = None
        self.dataOut = None
    
    def run(self, dataOut, path, oneDDict, ind2DList='[]', twoDDict='{}', metadata='{}', **kwargs):
        '''
        Inputs:
            path - path where files will be created
            oneDDict - json of one-dimensional parameters in record where keys
            are Madrigal codes (integers or mnemonics) and values the corresponding
            dataOut attribute e.g: {
                'gdlatr': 'lat',
                'gdlonr': 'lon',
                'gdlat2':'lat',
                'glon2':'lon'}
            ind2DList - list of independent spatial two-dimensional parameters e.g:
                ['heighList']
            twoDDict - json of two-dimensional parameters in record where keys
            are Madrigal codes (integers or mnemonics) and values the corresponding
            dataOut attribute if multidimensional array specify as tupple
            ('attr', pos) e.g: {
                'gdalt': 'heightList',
                'vn1p2': ('data_output', 0),
                'vn2p2': ('data_output', 1),
                'vn3': ('data_output', 2),
                'snl': ('data_SNR', 'db')
                }
            metadata - json of madrigal metadata (kinst, kindat, catalog and header)      
        '''
        if not self.isConfig:
            self.setup(dataOut, path, oneDDict, ind2DList, twoDDict, metadata, **kwargs)
            self.isConfig = True
            
        self.putData() 
        return
    
    def setup(self, dataOut, path, oneDDict, ind2DList, twoDDict, metadata, **kwargs):
        '''
        Configure Operation        
        '''
        
        self.dataOut = dataOut
        self.nmodes = self.dataOut.nmodes     
        self.path = path
        self.blocks = kwargs.get('blocks', None)
        self.counter = 0        
        self.oneDDict = load_json(oneDDict)
        self.twoDDict = load_json(twoDDict)
        self.ind2DList = load_json(ind2DList)
        meta = load_json(metadata)        
        self.kinst = meta.get('kinst')
        self.kindat = meta.get('kindat')
        self.catalog = meta.get('catalog', DEF_CATALOG)
        self.header = meta.get('header', DEF_HEADER)

        return

    def setFile(self):
        '''
        Create new cedar file object
        '''

        self.mnemonic = MNEMONICS[self.kinst]   #TODO get mnemonic from madrigal
        date = datetime.datetime.utcfromtimestamp(self.dataOut.utctime)

        filename = '%s%s_%s%s' % (self.mnemonic,
                                  date.strftime('%Y%m%d_%H%M%S'),
                                  self.dataOut.mode,
                                  self.ext)     
       
        self.fullname = os.path.join(self.path, filename)

        if os.path.isfile(self.fullname) : 
            print "Destination path '%s' already exists. Previous file deleted. " %self.fullname
            os.remove(self.fullname)
        
        try:
            print '[Writing] creating file : %s' % (self.fullname)
            self.cedarObj = madrigal.cedar.MadrigalCedarFile(self.fullname, True)  
        except ValueError, e:
            print '[Error]: Impossible to create a cedar object with "madrigal.cedar.MadrigalCedarFile" '
            return
        
        return 1  
     
    def writeBlock(self):
        '''
        Add data records to cedar file taking data from oneDDict and twoDDict
        attributes.
        Allowed parameters in: parcodes.tab
        '''

        startTime = datetime.datetime.utcfromtimestamp(self.dataOut.utctime)
        endTime = startTime + datetime.timedelta(seconds=self.dataOut.paramInterval)
        nrows = len(getattr(self.dataOut, self.ind2DList))

        rec = madrigal.cedar.MadrigalDataRecord(
            self.kinst,
            self.kindat,
            startTime.year,
            startTime.month,
            startTime.day,
            startTime.hour,
            startTime.minute,
            startTime.second,
            startTime.microsecond/10000,
            endTime.year,
            endTime.month,
            endTime.day,
            endTime.hour,
            endTime.minute,
            endTime.second,
            endTime.microsecond/10000,
            self.oneDDict.keys(),
            self.twoDDict.keys(),
            nrows
            )
                    
        # Setting 1d values        
        for key in self.oneDDict:
            rec.set1D(key, getattr(self.dataOut, self.oneDDict[key]))

        # Setting 2d values
        invalid = numpy.isnan(self.dataOut.data_output)
        self.dataOut.data_output[invalid] = self.missing
        out = {}
        for key, value in self.twoDDict.items():
            if isinstance(value, str):
                out[key] = getattr(self.dataOut, value)
            elif isinstance(value, tuple):
                attr, x = value
                if isinstance(x, (int, float)):
                    out[key] = getattr(self.dataOut, attr)[int(x)]
                elif x.lower()=='db':
                    tmp = getattr(self.dataOut, attr)
                    SNRavg = numpy.average(tmp, axis=0)
                    out[key] = 10*numpy.log10(SNRavg)

        for n in range(nrows):
            for key in out:
                rec.set2D(key, n, out[key][n])

        self.cedarObj.append(rec)
        self.cedarObj.dump()
        print '[Writing] Record No. {} (mode {}).'.format(
            self.counter,
            self.dataOut.mode
            )

    def setHeader(self):
        '''
        Create an add catalog and header to cedar file
        ''' 
        
        header = madrigal.cedar.CatalogHeaderCreator(self.fullname)        
        header.createCatalog(**self.catalog)
        header.createHeader(**self.header)
        header.write()
              
    def putData(self):

        if self.dataOut.flagNoData:
            return 0
        
        if self.counter == 0:
            self.setFile()            
        
        if self.counter <= self.dataOut.nrecords:
            self.writeBlock()
            self.counter += 1
        
        if self.counter == self.dataOut.nrecords or self.counter == self.blocks:
            self.setHeader()
            self.counter = 0
