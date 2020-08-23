'''
Created on Jan 15, 2018

@author: Juan C. Espinoza
'''

import os
import sys
import time
import glob
import datetime
import tarfile

import numpy

from .utils import folder_in_range

from schainpy.model.io.jroIO_base import JRODataReader
from schainpy.model.proc.jroproc_base import ProcessingUnit, Operation
from schainpy.model.data.jrodata import Parameters
from schainpy.utils import log

try:
    from netCDF4 import Dataset
except:
    pass

UT1970 = datetime.datetime(1970, 1, 1) - datetime.timedelta(seconds=time.timezone)


class PXReader(JRODataReader, ProcessingUnit):

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
        self.nTries = kwargs.get('nTries', 10)
        self.online = kwargs.get('online', False)
        self.delay = kwargs.get('delay', 60)
        self.ele = kwargs.get('ext', '')

        if self.path is None:
            raise ValueError('The path is not valid')

        self.search_files(path, startDate, endDate, startTime, endTime, walk)
        self.cursor = 0
        self.counter_records = 0

        if not self.files:
            raise  Warning('There is no files matching these date in the folder: {}. \n Check startDate and endDate'.format(path))
        
    def search_files(self, path, startDate, endDate, startTime, endTime, walk):
        '''
         Searching for NCDF files in path
         Creating a list of files to procces included in [startDate,endDate]
         
         Input: 
             path - Path to find files             
        '''    

        log.log('Searching files {} in {} '.format(self.ext, path), 'PXReader')
        if walk:
            paths = [os.path.join(path, p) for p in os.listdir(path) if os.path.isdir(os.path.join(path, p))]
            paths.sort()
        else:
            paths = [path]

        fileList0 = []
        
        for subpath in paths:
            if not folder_in_range(subpath.split('/')[-1], startDate, endDate, '%Y%m%d'):
                continue
            fileList0 += [os.path.join(subpath, s) for s in glob.glob1(subpath, '*') if os.path.splitext(s)[-1] in self.ext and '{}'.format(self.ele) in s]
        
        fileList0.sort()
        if self.online:
            fileList0 = fileList0[-1:]

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

        self.dates = list(self.files.keys())
        self.dates.sort()

        return

    def search_files_online(self):
        '''
         Searching for NCDF files in online mode path
         Creating a list of files to procces included in [startDate,endDate]
         
         Input: 
             path - Path to find files             
        '''    

        self.files = {}

        for n in range(self.nTries):

            if self.walk:
                paths = [os.path.join(self.path, p) for p in os.listdir(self.path) if os.path.isdir(os.path.join(self.path, p))]
                paths.sort()
                path = paths[-1]
            else:
                path = self.path

            new_files = [os.path.join(path, s) for s in glob.glob1(path, '*') if os.path.splitext(s)[-1] in self.ext and '{}'.format(self.ele) in s]            
            new_files.sort()

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
                
                dt = datetime.datetime.combine(dateFile, timeFile)
                
                if self.dt >= dt:
                    continue
                
                if dt not in self.files:
                    self.dt = dt
                    self.files[dt] = []
                
                self.files[dt].append(fullname)
                break

            if self.files:
                break
            else:
                log.warning('Waiting {} seconds for the next file, try {} ...'.format(self.delay, n + 1), 'PXReader')
                time.sleep(self.delay)

        if not self.files:
            return 0

        self.dates = list(self.files.keys())
        self.dates.sort()
        self.cursor = 0

        return 1

    def parseFile(self):
        '''
        '''

        header = {}
        
        for attr in self.fp.ncattrs():
            header[str(attr)] = getattr(self.fp, attr)

        self.header.append(header)

        self.data[header['TypeName']] = numpy.array(self.fp.variables[header['TypeName']])

    def setNextFile(self):
        '''
        Open next files for the current datetime
        '''

        cursor = self.cursor
        if not self.online_mode:
            if cursor == len(self.dates):
                if self.online:
                    cursor = 0
                    self.dt = self.dates[cursor]
                    self.online_mode = True
                    if not self.search_files_online():
                        log.success('No more files', 'PXReader')
                        return 0
                else:
                    log.success('No more files', 'PXReader')
                    self.flagNoMoreFiles = 1
                    return 0
        else:
            if not self.search_files_online():
                return 0
            cursor = self.cursor

        self.data = {}
        self.header = []

        for fullname in self.files[self.dates[cursor]]:

            log.log('Opening: {}'.format(fullname), 'PXReader')

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

            self.datatime = datetime.datetime.utcfromtimestamp(self.header[0]['Time'])
            
            if self.online:
                break

            if (self.datatime < datetime.datetime.combine(self.startDate, self.startTime)) or \
               (self.datatime > datetime.datetime.combine(self.endDate, self.endTime)):
                log.warning(
                    'Reading Record No. {}/{} -> {} [Skipping]'.format(
                        self.counter_records,
                        self.nrecords,
                        self.datatime.ctime()),
                    'PXReader')
                continue
            break

        log.log(
            'Reading Record No. {}/{} -> {}'.format(
                self.counter_records,
                self.nrecords,
                self.datatime.ctime()),
            'PXReader')

        return 1


    def set_output(self):
        '''
        Storing data from buffer to dataOut object
        '''

        self.data['Elevation'] = numpy.array(self.fp.variables['Elevation'])
        self.data['Azimuth'] = numpy.array(self.fp.variables['Azimuth'])
        self.dataOut.range = numpy.array(self.fp.variables['GateWidth'])
        self.dataOut.data = self.data
        self.dataOut.units = [h['Unit-value'] for h in self.header]
        self.dataOut.parameters = [h['TypeName'] for h in self.header]
        self.dataOut.missing = self.header[0]['MissingData']
        self.dataOut.max_range = self.header[0]['MaximumRange-value']
        self.dataOut.elevation = self.header[0]['Elevation']
        self.dataOut.azimuth = self.header[0]['Azimuth']
        self.dataOut.latitude = self.header[0]['Latitude']
        self.dataOut.longitude = self.header[0]['Longitude']
        self.dataOut.utctime = self.header[0]['Time']
        self.dataOut.utctimeInit = self.dataOut.utctime
        self.dataOut.useLocalTime = True
        self.dataOut.flagNoData = False
        self.dataOut.flagDiscontinuousBlock = self.flagDiscontinuousBlock

        log.log('Parameters found: {}'.format(','.join(self.dataOut.parameters)),
                    'PXReader')

    def getData(self):
        '''
        Storing data from databuffer to dataOut object
        '''
        if self.flagNoMoreFiles:
            self.dataOut.flagNoData = True
            log.error('No file left to process', 'PXReader')
            return 0

        if not self.readNextFile():
            self.dataOut.flagNoData = True
            return 0

        self.set_output()

        return 1
