'''
Created on Set 10, 2017

@author: Juan C. Espinoza
'''


import os
import sys
import time
import glob
import datetime

import numpy

from schainpy.model.proc.jroproc_base import ProcessingUnit
from schainpy.model.data.jrodata import Parameters
from schainpy.model.io.jroIO_base import JRODataReader, isNumber
from schainpy.utils import log

FILE_HEADER_STRUCTURE = numpy.dtype([
    ('year', 'f'),
    ('doy', 'f'),
    ('nint', 'f'),
    ('navg', 'f'),
    ('fh', 'f'),
    ('dh', 'f'),
    ('nheights', 'f'),    
    ('ipp', 'f')
])

REC_HEADER_STRUCTURE = numpy.dtype([
    ('magic', 'f'),
    ('hours', 'f'),
    ('interval', 'f'),
    ('h0', 'f'),
    ('nheights', 'f'),
    ('snr1', 'f'),
    ('snr2', 'f'),
    ('snr', 'f'),
])

DATA_STRUCTURE = numpy.dtype([
    ('range', '<u4'),
    ('status', '<u4'),
    ('zonal', '<f4'),
    ('meridional', '<f4'),
    ('vertical', '<f4'),
    ('zonal_a', '<f4'),
    ('meridional_a', '<f4'),
    ('corrected_fading', '<f4'),  # seconds
    ('uncorrected_fading', '<f4'),  # seconds
    ('time_diff', '<f4'),
    ('major_axis', '<f4'),
    ('axial_ratio', '<f4'),
    ('orientation', '<f4'),
    ('sea_power', '<u4'),
    ('sea_algorithm', '<u4')
])


class JULIAParamReader(JRODataReader, ProcessingUnit):
    '''
    Julia data (eej, spf, 150km) *.dat files
    '''

    ext = '.dat'

    def __init__(self, **kwargs):

        ProcessingUnit.__init__(self, **kwargs)

        self.dataOut = Parameters()
        self.counter_records = 0
        self.flagNoMoreFiles = 0
        self.isConfig = False
        self.filename = None
        self.clockpulse = 0.15
        self.kd = 213.6

    def setup(self,
              path=None,
              startDate=None,
              endDate=None,
              ext=None,              
              startTime=datetime.time(0, 0, 0),
              endTime=datetime.time(23, 59, 59),
              timezone=0,
              format=None,
              **kwargs):

        self.path = path
        self.startDate = startDate
        self.endDate = endDate
        self.startTime = startTime
        self.endTime = endTime
        self.datatime = datetime.datetime(1900, 1, 1)
        self.format = format        

        if self.path is None:
            raise ValueError("The path is not valid")

        if ext is None:
            ext = self.ext

        self.search_files(self.path, startDate, endDate, ext)
        self.timezone = timezone
        self.fileIndex = 0

        if not self.fileList:
            log.warning('There is no files matching these date in the folder: {}'.format(
                path), self.name)

        self.setNextFile()

    def search_files(self, path, startDate, endDate, ext):
        '''
         Searching for BLTR rawdata file in path
         Creating a list of file to proces included in [startDate,endDate]

         Input: 
             path - Path to find BLTR rawdata files
             startDate - Select file from this date
             enDate - Select file until this date
             ext - Extension of the file to read
        '''
        
        log.success('Searching files in {} '.format(path), self.name)        
        fileList0 = glob.glob1(path, '{}*{}'.format(self.format.upper(), ext))
        fileList0.sort()

        self.fileList = []
        self.dateFileList = []

        for thisFile in fileList0:            
            year = thisFile[2:4]
            if not isNumber(year):
                continue

            month = thisFile[4:6]
            if not isNumber(month):
                continue

            day = thisFile[6:8]
            if not isNumber(day):
                continue

            year, month, day = int(year), int(month), int(day)
            dateFile = datetime.date(year+2000, month, day)
            
            if (startDate > dateFile) or (endDate < dateFile):
                continue

            self.fileList.append(thisFile)
            self.dateFileList.append(dateFile)
        
        return

    def setNextFile(self):

        file_id = self.fileIndex

        if file_id == len(self.fileList):
            log.success('No more files in the folder', self.name)
            self.flagNoMoreFiles = 1
            return 0
        
        log.success('Opening {}'.format(self.fileList[file_id]), self.name)
        filename = os.path.join(self.path, self.fileList[file_id])

        dirname, name = os.path.split(filename)        
        self.siteFile = name.split('.')[0]
        if self.filename is not None:
            self.fp.close()
        self.filename = filename
        self.fp = open(self.filename, 'rb')
        
        self.header_file = numpy.fromfile(self.fp, FILE_HEADER_STRUCTURE, 1)
        yy = self.header_file['year'] - 1900 * (self.header_file['year'] > 3000)
        self.year = int(yy + 1900 * (yy < 1000))
        self.doy = int(self.header_file['doy'])
        self.dH = round(self.header_file['dh'], 2)
        self.ipp = round(self.header_file['ipp'], 2)
        self.sizeOfFile = os.path.getsize(self.filename)
        self.counter_records = 0
        self.flagIsNewFile = 0
        self.fileIndex += 1

        return 1

    def readNextBlock(self):

        while True:
            if not self.readBlock():
                self.flagIsNewFile = 1
                if not self.setNextFile():
                    return 0            

            if (self.datatime < datetime.datetime.combine(self.startDate, self.startTime)) or \
               (self.datatime > datetime.datetime.combine(self.endDate, self.endTime)):
                log.warning(
                    'Reading Record No. {} -> {} [Skipping]'.format(
                        self.counter_records,
                        self.datatime.ctime()),
                    self.name)
                continue
            break
       
        log.log('Reading Record No. {} -> {}'.format(
            self.counter_records,
            self.datatime.ctime()), self.name)

        return 1

    def readBlock(self):
        
        pointer = self.fp.tell()
        heights, dt = self.readHeader()
        self.fp.seek(pointer)
        buffer_h = []
        buffer_d = []
        while True:
            pointer = self.fp.tell()
            if pointer == self.sizeOfFile:
                return 0
            heights, datatime = self.readHeader()            
            if dt == datatime:                
                buffer_h.append(heights)
                buffer_d.append(self.readData(len(heights)))
                continue
            self.fp.seek(pointer)
            break
        
        if dt.date() > self.datatime.date():
            self.flagDiscontinuousBlock = 1
        self.datatime = dt
        self.time = (dt - datetime.datetime(1970, 1, 1)).total_seconds() + time.timezone        
        self.heights = numpy.concatenate(buffer_h)
        self.buffer = numpy.zeros((5, len(self.heights))) + numpy.nan
        self.buffer[0, :] = numpy.concatenate([buf[0] for buf in buffer_d])
        self.buffer[1, :] = numpy.concatenate([buf[1] for buf in buffer_d])
        self.buffer[2, :] = numpy.concatenate([buf[2] for buf in buffer_d])
        self.buffer[3, :] = numpy.concatenate([buf[3] for buf in buffer_d])
        self.buffer[4, :] = numpy.concatenate([buf[4] for buf in buffer_d])
        
        self.counter_records += 1

        return 1

    def readHeader(self):
        '''
        Parse recordHeader
        '''
        
        self.header_rec = numpy.fromfile(self.fp, REC_HEADER_STRUCTURE, 1)
        self.interval = self.header_rec['interval']
        if self.header_rec['magic'] == 888.:
            self.header_rec['h0'] = round(self.header_rec['h0'], 2)
            nheights = int(self.header_rec['nheights'])            
            hours = float(self.header_rec['hours'][0])
            heights = numpy.arange(nheights) * self.dH + self.header_rec['h0']
            datatime = datetime.datetime(self.year, 1, 1) + datetime.timedelta(days=self.doy-1, hours=hours)            
            return heights, datatime
        else:
            return False
        
    def readData(self, N):
        '''
        Parse data
        '''

        buffer = numpy.fromfile(self.fp, 'f', 8*N).reshape(N, 8)
        
        pow0 = buffer[:, 0]
        pow1 = buffer[:, 1]
        acf0 = (buffer[:,2] + buffer[:,3]*1j) / pow0
        acf1 = (buffer[:,4] + buffer[:,5]*1j) / pow1
        dccf = (buffer[:,6] + buffer[:,7]*1j) / (pow0*pow1)

        ### SNR
        sno = (pow0 + pow1 - self.header_rec['snr']) / self.header_rec['snr']
        sno10 = numpy.log10(sno)
        # dsno = 1.0 / numpy.sqrt(self.header_file['nint'] * self.header_file['navg']) * (1 + (1 / sno))
        
        ### Vertical Drift
        sp = numpy.sqrt(numpy.abs(acf0)*numpy.abs(acf1))
        sp[numpy.where(numpy.abs(sp) >= 1.0)] = numpy.sqrt(0.9999)
                    
        vzo = -numpy.arctan2(acf0.imag + acf1.imag,acf0.real + acf1.real)*1.5E5*1.5/(self.ipp*numpy.pi)
        dvzo = numpy.sqrt(1.0 - sp*sp)*0.338*1.5E5/(numpy.sqrt(self.header_file['nint']*self.header_file['navg'])*sp*self.ipp)            
        err = numpy.where(dvzo <= 0.1)
        dvzo[err] = 0.1

        #Zonal Drifts
        dt = self.header_file['nint']*self.ipp / 1.5E5
        coh = numpy.sqrt(numpy.abs(dccf))
        err = numpy.where(coh >= 1.0)            
        coh[err] = numpy.sqrt(0.99999)
            
        err = numpy.where(coh <= 0.1)
        coh[err] = numpy.sqrt(0.1)
                
        vxo = numpy.arctan2(dccf.imag, dccf.real)*self.header_rec['h0']*1.0E3/(self.kd*dt)
        dvxo = numpy.sqrt(1.0 - coh*coh)*self.header_rec['h0']*1.0E3/(numpy.sqrt(self.header_file['nint']*self.header_file['navg'])*coh*self.kd*dt)
        
        err = numpy.where(dvxo <= 0.1)            
        dvxo[err] = 0.1

        return vzo, dvzo, vxo, dvxo, sno10 

    def set_output(self):
        '''
        Storing data from databuffer to dataOut object
        '''
        
        self.dataOut.data_SNR = self.buffer[4].reshape(1, -1)
        self.dataOut.heightList = self.heights
        self.dataOut.data_param = self.buffer[0:4,]
        self.dataOut.utctimeInit = self.time
        self.dataOut.utctime = self.time
        self.dataOut.useLocalTime = True
        self.dataOut.paramInterval = self.interval
        self.dataOut.timezone = self.timezone
        self.dataOut.sizeOfFile = self.sizeOfFile
        self.dataOut.flagNoData = False
        self.dataOut.flagDiscontinuousBlock = self.flagDiscontinuousBlock

    def getData(self):
        '''
        Storing data from databuffer to dataOut object
        '''
        if self.flagNoMoreFiles:
            self.dataOut.flagNoData = True
            log.success('No file left to process', self.name)
            return 0

        if not self.readNextBlock():
            self.dataOut.flagNoData = True
            return 0

        self.set_output()

        return 1