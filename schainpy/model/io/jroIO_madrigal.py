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

import schainpy.admin
from schainpy.model.io.jroIO_base import LOCALTIME, Reader
from schainpy.model.proc.jroproc_base import ProcessingUnit, Operation, MPDecorator
from schainpy.model.data.jrodata import Parameters
from schainpy.utils import log

try:
    import madrigal.cedar
except:
    pass

try:
    basestring
except:
    basestring = str

DEF_CATALOG = {
    'principleInvestigator': 'Marco Milla',
    'expPurpose': '',
    'cycleTime': '',
    'correlativeExp': '',
    'sciRemarks': '',
    'instRemarks': ''
    }
    
DEF_HEADER = {
    'kindatDesc': '',
    'analyst': 'Jicamarca User',
    'comments': '',
    'history': ''
    }

MNEMONICS = {
    10: 'jro',
    11: 'jbr',
    840: 'jul',
    13: 'jas',
    1000: 'pbr',
    1001: 'hbr',
    1002: 'obr',
    400: 'clr'

}

UT1970 = datetime.datetime(1970, 1, 1) - datetime.timedelta(seconds=time.timezone)

def load_json(obj):
    '''
    Parse json as string instead of unicode
    '''

    if isinstance(obj, str):
        iterable = json.loads(obj)
    else:
        iterable = obj

    if isinstance(iterable, dict):
        return {str(k): load_json(v) if isinstance(v, dict) else str(v) if isinstance(v, basestring) else v
            for k, v in list(iterable.items())}
    elif isinstance(iterable, (list, tuple)):
        return [str(v) if isinstance(v, basestring) else v for v in iterable]
    
    return iterable


class MADReader(Reader, ProcessingUnit):

    def __init__(self):

        ProcessingUnit.__init__(self)

        self.dataOut = Parameters()    
        self.counter_records = 0
        self.nrecords = None
        self.flagNoMoreFiles = 0
        self.filename = None        
        self.intervals = set()
        self.datatime = datetime.datetime(1900,1,1)
        self.format = None
        self.filefmt = "***%Y%m%d*******"
        
    def setup(self, **kwargs):
                
        self.set_kwargs(**kwargs)
        self.oneDDict = load_json(self.oneDDict)
        self.twoDDict = load_json(self.twoDDict)
        self.ind2DList = load_json(self.ind2DList)
        self.independentParam = self.ind2DList[0]

        if self.path is None:
            raise ValueError('The path is not valid')

        self.open_file = open
        self.open_mode = 'rb'

        if self.format is None:
            raise ValueError('The format is not valid choose simple or hdf5')
        elif self.format.lower() in ('simple', 'txt'):
            self.ext = '.txt'
        elif self.format.lower() in ('cedar',):
            self.ext = '.001'
        else:
            self.ext = '.hdf5'
            self.open_file = h5py.File
            self.open_mode = 'r'

        if self.online:
            log.log("Searching files in online mode...", self.name)

            for nTries in range(self.nTries):
                fullpath = self.searchFilesOnLine(self.path, self.startDate,
                    self.endDate, self.expLabel, self.ext, self.walk, 
                    self.filefmt, self.folderfmt)

                try:
                    fullpath = next(fullpath)
                except:
                    fullpath = None
                
                if fullpath:
                    break

                log.warning(
                    'Waiting {} sec for a valid file in {}: try {} ...'.format(
                        self.delay, self.path, nTries + 1), 
                    self.name)
                time.sleep(self.delay)

            if not(fullpath):
                raise schainpy.admin.SchainError(
                    'There isn\'t any valid file in {}'.format(self.path))            
           
        else:
            log.log("Searching files in {}".format(self.path), self.name)
            self.filenameList = self.searchFilesOffLine(self.path, self.startDate, 
                self.endDate, self.expLabel, self.ext, self.walk, self.filefmt, self.folderfmt)
        
        self.setNextFile()

    def readFirstHeader(self):
        '''Read header and data'''

        self.parseHeader()
        self.parseData()
        self.blockIndex = 0
        
        return        

    def parseHeader(self):
        '''
        '''

        self.output = {}
        self.version = '2'
        s_parameters = None
        if self.ext == '.txt':
            self.parameters = [s.strip().lower() for s in self.fp.readline().decode().strip().split(' ') if s]
        elif self.ext == '.hdf5':
            self.metadata = self.fp['Metadata']
            if '_record_layout' in self.metadata:
                s_parameters = [s[0].lower().decode() for s in self.metadata['Independent Spatial Parameters']]
                self.version = '3'
            self.parameters = [s[0].lower().decode() for s in self.metadata['Data Parameters']]

        log.success('Parameters found: {}'.format(self.parameters),
                    'MADReader')
        if s_parameters:
            log.success('Spatial parameters found: {}'.format(s_parameters),
                        'MADReader')
        
        for param in list(self.oneDDict.keys()):
            if param.lower() not in self.parameters:
                log.warning(
                    'Parameter {} not found will be ignored'.format(
                        param),
                    'MADReader')
                self.oneDDict.pop(param, None)
        
        for param, value in list(self.twoDDict.items()):
            if param.lower() not in self.parameters:
                log.warning(
                    'Parameter {} not found, it will be ignored'.format(
                        param),
                    'MADReader')
                self.twoDDict.pop(param, None)
                continue
            if isinstance(value, list):
                if value[0] not in self.output:
                    self.output[value[0]] = []
                self.output[value[0]].append([])

    def parseData(self):
        '''
        '''

        if self.ext == '.txt':
            self.data = numpy.genfromtxt(self.fp, missing_values=('missing'))
            self.nrecords = self.data.shape[0]
            self.ranges = numpy.unique(self.data[:,self.parameters.index(self.independentParam.lower())])
            self.counter_records = 0
        elif self.ext == '.hdf5':
            self.data = self.fp['Data']
            self.ranges = numpy.unique(self.data['Table Layout'][self.independentParam.lower()])
            self.times = numpy.unique(self.data['Table Layout']['ut1_unix'])
            self.counter_records = int(self.data['Table Layout']['recno'][0])
            self.nrecords = int(self.data['Table Layout']['recno'][-1])

    def readNextBlock(self):

        while True:
            self.flagDiscontinuousBlock = 0
            if self.counter_records == self.nrecords:
                self.setNextFile()                

            self.readBlock()
            
            if (self.datatime < datetime.datetime.combine(self.startDate, self.startTime)) or \
               (self.datatime > datetime.datetime.combine(self.endDate, self.endTime)):
                log.warning(
                    'Reading Record No. {}/{} -> {} [Skipping]'.format(
                        self.counter_records,
                        self.nrecords,
                        self.datatime.ctime()),
                    'MADReader')
                continue
            break

        log.log(
            'Reading Record No. {}/{} -> {}'.format(
                self.counter_records,
                self.nrecords,
                self.datatime.ctime()),
            'MADReader')

        return 1

    def readBlock(self):
        '''
        '''
        dum = []
        if self.ext == '.txt':
            dt = self.data[self.counter_records][:6].astype(int)
            if datetime.datetime(dt[0], dt[1], dt[2], dt[3], dt[4], dt[5]).date() > self.datatime.date():
                self.flagDiscontinuousBlock = 1
            self.datatime = datetime.datetime(dt[0], dt[1], dt[2], dt[3], dt[4], dt[5])
            while True:
                dt = self.data[self.counter_records][:6].astype(int)
                datatime = datetime.datetime(dt[0], dt[1], dt[2], dt[3], dt[4], dt[5])
                if datatime == self.datatime:
                    dum.append(self.data[self.counter_records])
                    self.counter_records += 1
                    if self.counter_records == self.nrecords:
                        break
                    continue
                self.intervals.add((datatime-self.datatime).seconds)                
                break
        elif self.ext == '.hdf5':
            datatime = datetime.datetime.utcfromtimestamp(
                self.times[self.counter_records])
            dum = self.data['Table Layout'][self.data['Table Layout']['recno']==self.counter_records]
            self.intervals.add((datatime-self.datatime).seconds)
            if datatime.date()>self.datatime.date():
                self.flagDiscontinuousBlock = 1
            self.datatime = datatime
            self.counter_records += 1            
        
        self.buffer = numpy.array(dum)
        return

    def set_output(self):
        '''
        Storing data from buffer to dataOut object
        '''        

        parameters = [None for __ in self.parameters]

        for param, attr in list(self.oneDDict.items()):            
            x = self.parameters.index(param.lower())
            setattr(self.dataOut, attr, self.buffer[0][x])

        for param, value in list(self.twoDDict.items()):
            dummy = numpy.zeros(self.ranges.shape) + numpy.nan               
            if self.ext == '.txt':
                x = self.parameters.index(param.lower())
                y = self.parameters.index(self.independentParam.lower())            
                ranges = self.buffer[:,y]
                #if self.ranges.size == ranges.size:
                #    continue
                index = numpy.where(numpy.in1d(self.ranges, ranges))[0]
                dummy[index] = self.buffer[:,x]
            else:
                ranges = self.buffer[self.independentParam.lower()]
                index = numpy.where(numpy.in1d(self.ranges, ranges))[0]
                dummy[index] = self.buffer[param.lower()]
            
            if isinstance(value, str):
                if value not in self.independentParam:             
                    setattr(self.dataOut, value, dummy.reshape(1,-1))
            elif isinstance(value, list):                
                self.output[value[0]][value[1]] = dummy
                parameters[value[1]] = param
        for key, value in list(self.output.items()):
            setattr(self.dataOut, key, numpy.array(value))
        
        self.dataOut.parameters = [s for s in parameters if s]
        self.dataOut.heightList = self.ranges
        self.dataOut.utctime = (self.datatime - datetime.datetime(1970, 1, 1)).total_seconds()
        self.dataOut.utctimeInit = self.dataOut.utctime  
        self.dataOut.paramInterval = min(self.intervals)
        self.dataOut.useLocalTime = False        
        self.dataOut.flagNoData = False        
        self.dataOut.nrecords = self.nrecords
        self.dataOut.flagDiscontinuousBlock = self.flagDiscontinuousBlock

    def getData(self):
        '''
        Storing data from databuffer to dataOut object
        '''

        if not  self.readNextBlock():
            self.dataOut.flagNoData = True
            return 0

        self.set_output()

        return 1

    def run(self, **kwargs):

        if not(self.isConfig):
            self.setup(**kwargs)
            self.isConfig = True

        self.getData()

        return

@MPDecorator
class MADWriter(Operation):
    '''Writing module for Madrigal files
    
type: external

Inputs:
            path        path where files will be created
            oneDDict    json of one-dimensional parameters in record where keys
                        are Madrigal codes (integers or mnemonics) and values the corresponding
                        dataOut attribute e.g: {
                            'gdlatr': 'lat',
                            'gdlonr': 'lon',
                            'gdlat2':'lat',
                            'glon2':'lon'}
            ind2DList   list of independent spatial two-dimensional parameters e.g:
                        ['heigthList']
            twoDDict    json of two-dimensional parameters in record where keys
                        are Madrigal codes (integers or mnemonics) and values the corresponding
                        dataOut attribute if multidimensional array specify as tupple
                        ('attr', pos) e.g: {
                            'gdalt': 'heightList',
                            'vn1p2': ('data_output', 0),
                            'vn2p2': ('data_output', 1),
                            'vn3': ('data_output', 2),
                            'snl': ('data_SNR', 'db')
                            }
            metadata    json of madrigal metadata (kinst, kindat, catalog and header)
            format      hdf5, cedar
            blocks      number of blocks per file'''

    __attrs__ = ['path', 'oneDDict', 'ind2DList', 'twoDDict','metadata', 'format', 'blocks']
    missing = -32767
    
    def __init__(self):

        Operation.__init__(self)
        self.dataOut = Parameters()
        self.counter = 0
        self.path = None
        self.fp = None

    def run(self, dataOut, path, oneDDict, ind2DList='[]', twoDDict='{}',
            metadata='{}', format='cedar', **kwargs):
        
        if not self.isConfig:
            self.setup(path, oneDDict, ind2DList, twoDDict, metadata, format, **kwargs)
            self.isConfig = True
        
        self.dataOut = dataOut        
        self.putData() 
        return 1
    
    def setup(self, path, oneDDict, ind2DList, twoDDict, metadata, format, **kwargs):
        '''
        Configure Operation        
        '''
                
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
        if format == 'cedar':
            self.ext = '.dat'
            self.extra_args = {}
        elif format == 'hdf5':
            self.ext = '.hdf5'
            self.extra_args = {'ind2DList': self.ind2DList}
        
        self.keys = [k.lower() for k in self.twoDDict]        
        if 'range' in self.keys:
            self.keys.remove('range')
        if 'gdalt' in self.keys:
            self.keys.remove('gdalt')

    def setFile(self):
        '''
        Create new cedar file object
        '''

        self.mnemonic = MNEMONICS[self.kinst]   #TODO get mnemonic from madrigal
        date = datetime.datetime.utcfromtimestamp(self.dataOut.utctime)

        filename = '{}{}{}'.format(self.mnemonic,
                                   date.strftime('%Y%m%d_%H%M%S'),
                                   self.ext)
       
        self.fullname = os.path.join(self.path, filename)
    
        if os.path.isfile(self.fullname) : 
            log.warning(
                'Destination file {} already exists, previous file deleted.'.format(
                    self.fullname),
                'MADWriter')
            os.remove(self.fullname)
        
        try:
            log.success(
                'Creating file: {}'.format(self.fullname),
                'MADWriter')
            if not os.path.exists(self.path):
                os.makedirs(self.path)
            self.fp = madrigal.cedar.MadrigalCedarFile(self.fullname, True)
        except ValueError as e:
            log.error(
                'Impossible to create a cedar object with "madrigal.cedar.MadrigalCedarFile"',
                'MADWriter')
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
        heights = self.dataOut.heightList

        if self.ext == '.dat':
            for key, value in list(self.twoDDict.items()):
                if isinstance(value, str):
                    data = getattr(self.dataOut, value)
                    invalid = numpy.isnan(data)
                    data[invalid] = self.missing
                elif isinstance(value, (tuple, list)):
                    attr, key = value
                    data = getattr(self.dataOut, attr)
                    invalid = numpy.isnan(data)
                    data[invalid] = self.missing

        out = {}
        for key, value in list(self.twoDDict.items()):
            key = key.lower()
            if isinstance(value, str):
                if 'db' in value.lower():
                    tmp = getattr(self.dataOut, value.replace('_db', ''))
                    SNRavg = numpy.average(tmp, axis=0)
                    tmp = 10*numpy.log10(SNRavg)
                else:
                    tmp = getattr(self.dataOut, value)
                out[key] = tmp.flatten()[:len(heights)]
            elif isinstance(value, (tuple, list)):
                attr, x = value
                data = getattr(self.dataOut, attr)                
                out[key] = data[int(x)][:len(heights)]
        
        a = numpy.array([out[k] for k in self.keys])
        nrows = numpy.array([numpy.isnan(a[:, x]).all() for x in range(len(heights))])
        index = numpy.where(nrows == False)[0]

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
            list(self.oneDDict.keys()),
            list(self.twoDDict.keys()),
            len(index),
            **self.extra_args
        )

        # Setting 1d values        
        for key in self.oneDDict:
            rec.set1D(key, getattr(self.dataOut, self.oneDDict[key]))

        # Setting 2d values
        nrec = 0
        for n in index:            
            for key in out:
                rec.set2D(key, nrec, out[key][n])
            nrec += 1 

        self.fp.append(rec)
        if self.ext == '.hdf5' and self.counter % 500 == 0 and self.counter > 0:
            self.fp.dump()
        if self.counter % 20 == 0 and self.counter > 0:
            log.log(
                'Writing {} records'.format(
                    self.counter),
                'MADWriter')

    def setHeader(self):
        '''
        Create an add catalog and header to cedar file
        ''' 
        
        log.success('Closing file {}'.format(self.fullname), 'MADWriter')

        if self.ext == '.dat':
            self.fp.write()
        else:
            self.fp.dump()
            self.fp.close()
        
        header = madrigal.cedar.CatalogHeaderCreator(self.fullname)        
        header.createCatalog(**self.catalog)
        header.createHeader(**self.header)
        header.write()
              
    def putData(self):

        if self.dataOut.flagNoData:
            return 0        
        
        if self.dataOut.flagDiscontinuousBlock or self.counter == self.blocks:
            if self.counter > 0:
                self.setHeader()
            self.counter = 0

        if self.counter == 0:
            self.setFile()
        
        self.writeBlock()
        self.counter += 1        
        
    def close(self):
        
        if self.counter > 0:                
            self.setHeader()