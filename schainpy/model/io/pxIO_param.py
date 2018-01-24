'''
Created on Dec 27, 2017

@author: Juan C. Espinoza
'''

import os
import sys
import time
import json
import glob
import datetime
import tarfile

import numpy
from netCDF4 import Dataset

from schainpy.model.io.jroIO_base import JRODataReader
from schainpy.model.proc.jroproc_base import ProcessingUnit, Operation
from schainpy.model.data.jrodata import Parameters
from schainpy.utils import log

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
        return {str(k): load_json(v) if isinstance(v, dict) else str(v) if isinstance(v, unicode) else v
            for k, v in iterable.items()}
    elif isinstance(iterable, (list, tuple)):
        return [str(v) if isinstance(v, unicode) else v for v in iterable]
    
    return iterable


class NCDFReader(JRODataReader, ProcessingUnit):

    def __init__(self, **kwargs):

        ProcessingUnit.__init__(self, **kwargs)

        self.dataOut = Parameters()    
        self.counter_records = 0
        self.nrecords = None
        self.flagNoMoreFiles = 0
        self.isConfig = False        
        self.filename = None        
        self.intervals = set()
        self.ext = ('.nc', '.tgz')
        self.online_mode = False
        
    def setup(self,
              path=None,
              startDate=None,
              endDate=None,
              format=None,
              startTime=datetime.time(0, 0, 0),
              endTime=datetime.time(23, 59, 59),
              walk=False,
              **kwargs):
                
        self.path = path
        self.startDate = startDate
        self.endDate = endDate
        self.startTime = startTime
        self.endTime = endTime
        self.datatime = datetime.datetime(1900,1,1)
        self.walk = walk
        self.nTries = kwargs.get('nTries', 3)
        self.online = kwargs.get('online', False)
        self.delay = kwargs.get('delay', 30)

        if self.path is None:
            raise ValueError, 'The path is not valid'

        self.search_files(path, startDate, endDate, startTime, endTime, walk)
        self.cursor = 0
        self.counter_records = 0

        if not self.files:
            raise  Warning, 'There is no files matching these date in the folder: {}. \n Check startDate and endDate'.format(path)
        
    def search_files(self, path, startDate, endDate, startTime, endTime, walk):
        '''
         Searching for NCDF files in path
         Creating a list of files to procces included in [startDate,endDate]
         
         Input: 
             path - Path to find files             
        '''    

        log.log('Searching files {} in {} '.format(self.ext, path), 'NCDFReader')
        if walk:
            paths = [os.path.join(path, p) for p in os.listdir(path) if os.path.isdir(os.path.join(path, p))]
            paths.sort()
        else:
            paths = [path]

        fileList0 = []
        
        for subpath in paths:
            fileList0 += [os.path.join(subpath, s) for s in glob.glob1(subpath, '*') if os.path.splitext(s)[-1] in self.ext]
        
        fileList0.sort()

        self.files = {}

        startDate = startDate - datetime.timedelta(1)
        endDate = endDate + datetime.timedelta(1)

        for fullname in fileList0:
            thisFile = fullname.split('/')[-1]
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
            timeFile = datetime.time(int(thisFile[12:14]), int(thisFile[14:16]), int(thisFile[16:18]))
            
            if (startDate > dateFile) or (endDate < dateFile):
                continue
            
            dt = datetime.datetime.combine(dateFile, timeFile)
            if dt not in self.files:
                self.files[dt] = []
            self.files[dt].append(fullname)

        self.dates = self.files.keys()
        self.dates.sort()

        return

    def search_files_online(self):
        '''
         Searching for NCDF files in online mode path
         Creating a list of files to procces included in [startDate,endDate]
         
         Input: 
             path - Path to find files             
        '''    

        old_files = self.files[self.dt]
        self.files = {}

        for n in range(self.nTries):

            if self.walk:
                paths = [os.path.join(self.path, p) for p in os.listdir(self.path) if os.path.isdir(os.path.join(self.path, p))]
                paths = paths[-2:]
            else:
                paths = [self.path]

            new_files = []

            for path in paths:
                new_files += [os.path.join(path, s) for s in glob.glob1(path, '*') if os.path.splitext(s)[-1] in self.ext and os.path.join(path, s not in old_files)]
            
            new_files.sort()
            
            if new_files:
                break
            else:
                log.warning('Waiting {} seconds for the next file, try {} ...'.format(self.delay, n + 1), 'NCDFReader')
                time.sleep(self.delay)

        if not new_files:
            log.error('No more files found', 'NCDFReader')
            return 0

        startDate = self.dt - datetime.timedelta(seconds=1)

        for fullname in new_files:
            thisFile = fullname.split('/')[-1]
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
            timeFile = datetime.time(int(thisFile[12:14]), int(thisFile[14:16]), int(thisFile[16:18]))
            
            if (startDate > dateFile):
                continue
            
            dt = datetime.datetime.combine(dateFile, timeFile)
            if dt not in self.files:
                self.files[dt] = []
            
            self.files[dt].append(fullname)

        self.dates = self.files.keys()
        self.dates.sort()
        self.cursor = 0

        return 1

    def parseFile(self):
        '''
        '''

        self.header = {}
        
        for attr in self.fp.ncattrs():
            self.header[str(attr)] = getattr(self.fp, attr)

        self.data[self.header['TypeName']] = numpy.array(self.fp.variables[self.header['TypeName']])
        
        if 'Azimuth' not in self.data:
            self.data['Azimuth'] = numpy.array(self.fp.variables['Azimuth'])
        

    def setNextFile(self):
        '''
        Open next files for the current datetime
        '''

        cursor = self.cursor

        if not self.online_mode:
            self.dt = self.dates[cursor]
            if cursor == len(self.dates):
                if self.online:
                    self.online_mode = True
                else:
                    log.success('No more files', 'NCDFReader')
                    self.flagNoMoreFiles = 1
                    return 0
        else:
            if not self.search_files_online():
                return 0
        
        log.log(
            'Opening: {}\'s files'.format(self.dates[cursor]),
            'NCDFReader'
            )

        self.data = {}

        for fullname in self.files[self.dates[cursor]]:

            if os.path.splitext(fullname)[-1] == '.tgz':
                tar = tarfile.open(fullname, 'r:gz')
                tar.extractall('/tmp')
                files = [os.path.join('/tmp', member.name) for member in tar.getmembers()]
            else:
                files = [fullname]
            
            for filename in files:
                if self.filename is not None:
                    self.fp.close()

                self.filename = filename
                self.filedate = self.dates[cursor]
                self.fp = Dataset(self.filename, 'r')
                self.parseFile()

        self.counter_records += 1
        self.cursor += 1
        return 1

    def readNextFile(self):

        while True:
            self.flagDiscontinuousBlock = 0
            if not self.setNextFile():                    
                return 0

            self.datatime = datetime.datetime.utcfromtimestamp(self.header['Time'])
            
            if (self.datatime < datetime.datetime.combine(self.startDate, self.startTime)) or \
               (self.datatime > datetime.datetime.combine(self.endDate, self.endTime)):
                log.warning(
                    'Reading Record No. {}/{} -> {} [Skipping]'.format(
                        self.counter_records,
                        self.nrecords,
                        self.datatime.ctime()),
                    'NCDFReader')
                continue
            break

        log.log(
            'Reading Record No. {}/{} -> {}'.format(
                self.counter_records,
                self.nrecords,
                self.datatime.ctime()),
            'NCDFReader')

        return 1


    def set_output(self):
        '''
        Storing data from buffer to dataOut object
        '''        
        
        self.dataOut.heightList = self.data.pop('Azimuth')
        
        log.log('Parameters found: {}'.format(','.join(self.data.keys())),
                    'PXReader')
        
        self.dataOut.data_param = numpy.array(self.data.values())
        self.dataOut.data_param[self.dataOut.data_param == -99900.] = numpy.nan
        self.dataOut.parameters = self.data.keys()
        self.dataOut.utctime = self.header['Time']
        self.dataOut.utctimeInit = self.dataOut.utctime
        self.dataOut.useLocalTime = False
        self.dataOut.flagNoData = False
        self.dataOut.flagDiscontinuousBlock = self.flagDiscontinuousBlock

    def getData(self):
        '''
        Storing data from databuffer to dataOut object
        '''
        if self.flagNoMoreFiles:
            self.dataOut.flagNoData = True
            log.error('No file left to process', 'NCDFReader')
            return 0

        if not self.readNextFile():
            self.dataOut.flagNoData = True
            return 0

        self.set_output()

        return 1

