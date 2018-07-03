'''
Created on Nov 9, 2016

@author: roj- LouVD
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
    ('FMN', '<u4'),
    ('nrec', '<u4'),
    ('fr_offset', '<u4'),
    ('id', '<u4'),
    ('site', 'u1', (32,))
])

REC_HEADER_STRUCTURE = numpy.dtype([
    ('rmn', '<u4'),
    ('rcounter', '<u4'),
    ('nr_offset', '<u4'),
    ('tr_offset', '<u4'),
    ('time', '<u4'),
    ('time_msec', '<u4'),
    ('tag', 'u1', (32,)),
    ('comments', 'u1', (32,)),
    ('lat', '<f4'),
    ('lon', '<f4'),
    ('gps_status', '<u4'),
    ('freq', '<u4'),
    ('freq0', '<u4'),
    ('nchan', '<u4'),
    ('delta_r', '<u4'),
    ('nranges', '<u4'),
    ('r0', '<u4'),
    ('prf', '<u4'),
    ('ncoh', '<u4'),
    ('npoints', '<u4'),
    ('polarization', '<i4'),
    ('rx_filter', '<u4'),
    ('nmodes', '<u4'),
    ('dmode_index', '<u4'),
    ('dmode_rngcorr', '<u4'),
    ('nrxs', '<u4'),
    ('acf_length', '<u4'),
    ('acf_lags', '<u4'),
    ('sea_to_atmos', '<f4'),
    ('sea_notch', '<u4'),
    ('lh_sea', '<u4'),
    ('hh_sea', '<u4'),
    ('nbins_sea', '<u4'),
    ('min_snr', '<f4'),
    ('min_cc', '<f4'),
    ('max_time_diff', '<f4')
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


class BLTRParamReader(JRODataReader, ProcessingUnit):
    '''
    Boundary Layer and Tropospheric Radar (BLTR) reader, Wind velocities and SNR from *.sswma files
    '''

    ext = '.sswma'

    def __init__(self, **kwargs):

        ProcessingUnit.__init__(self, **kwargs)

        self.dataOut = Parameters()
        self.counter_records = 0
        self.flagNoMoreFiles = 0
        self.isConfig = False
        self.filename = None

    def setup(self,
              path=None,
              startDate=None,
              endDate=None,
              ext=None,
              startTime=datetime.time(0, 0, 0),
              endTime=datetime.time(23, 59, 59),
              timezone=0,
              status_value=0,
              **kwargs):

        self.path = path
        self.startDate = startDate
        self.endDate = endDate
        self.startTime = startTime
        self.endTime = endTime
        self.status_value = status_value
        self.datatime = datetime.datetime(1900,1,1)
        
        if self.path is None:
            raise ValueError("The path is not valid")

        if ext is None:
            ext = self.ext

        self.search_files(self.path, startDate, endDate, ext)
        self.timezone = timezone
        self.fileIndex = 0

        if not self.fileList:
            raise Warning("There is no files matching these date in the folder: %s. \n Check 'startDate' and 'endDate' " % (
                path))

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
        
        log.success('Searching files in {} '.format(path), 'BLTRParamReader')
        foldercounter = 0        
        fileList0 = glob.glob1(path, "*%s" % ext)
        fileList0.sort()

        self.fileList = []
        self.dateFileList = []

        for thisFile in fileList0:
            year = thisFile[-14:-10]
            if not isNumber(year):
                continue

            month = thisFile[-10:-8]
            if not isNumber(month):
                continue

            day = thisFile[-8:-6]
            if not isNumber(day):
                continue

            year, month, day = int(year), int(month), int(day)
            dateFile = datetime.date(year, month, day)

            if (startDate > dateFile) or (endDate < dateFile):
                continue

            self.fileList.append(thisFile)
            self.dateFileList.append(dateFile)

        return

    def setNextFile(self):

        file_id = self.fileIndex

        if file_id == len(self.fileList):
            log.success('No more files in the folder', 'BLTRParamReader')
            self.flagNoMoreFiles = 1
            return 0
        
        log.success('Opening {}'.format(self.fileList[file_id]), 'BLTRParamReader')
        filename = os.path.join(self.path, self.fileList[file_id])

        dirname, name = os.path.split(filename)
        # 'peru2' ---> Piura  -   'peru1' ---> Huancayo or Porcuya
        self.siteFile = name.split('.')[0]
        if self.filename is not None:
            self.fp.close()
        self.filename = filename
        self.fp = open(self.filename, 'rb')
        self.header_file = numpy.fromfile(self.fp, FILE_HEADER_STRUCTURE, 1)
        self.nrecords = self.header_file['nrec'][0]
        self.sizeOfFile = os.path.getsize(self.filename)
        self.counter_records = 0
        self.flagIsNewFile = 0
        self.fileIndex += 1

        return 1

    def readNextBlock(self):

        while True:
            if self.counter_records == self.nrecords:
                self.flagIsNewFile = 1
                if not self.setNextFile():
                    return 0

            self.readBlock()

            if (self.datatime < datetime.datetime.combine(self.startDate, self.startTime)) or \
               (self.datatime > datetime.datetime.combine(self.endDate, self.endTime)):
                log.warning(
                    'Reading Record No. {}/{} -> {} [Skipping]'.format(
                        self.counter_records,
                        self.nrecords,
                        self.datatime.ctime()),
                    'BLTRParamReader')
                continue
            break

        log.log('Reading Record No. {}/{} -> {}'.format(
            self.counter_records,
            self.nrecords,
            self.datatime.ctime()), 'BLTRParamReader')

        return 1

    def readBlock(self):

        pointer = self.fp.tell()
        header_rec = numpy.fromfile(self.fp, REC_HEADER_STRUCTURE, 1)
        self.nchannels = header_rec['nchan'][0] / 2
        self.kchan = header_rec['nrxs'][0]
        self.nmodes = header_rec['nmodes'][0]
        self.nranges = header_rec['nranges'][0]
        self.fp.seek(pointer)
        self.height = numpy.empty((self.nmodes, self.nranges))
        self.snr = numpy.empty((self.nmodes, self.nchannels, self.nranges))
        self.buffer = numpy.empty((self.nmodes, 3, self.nranges))
        self.flagDiscontinuousBlock = 0

        for mode in range(self.nmodes):
            self.readHeader()
            data = self.readData()
            self.height[mode] = (data[0] - self.correction) / 1000.
            self.buffer[mode] = data[1]
            self.snr[mode] = data[2]

        self.counter_records = self.counter_records + self.nmodes

        return

    def readHeader(self):
        '''
        RecordHeader of BLTR rawdata file
        '''

        header_structure = numpy.dtype(
            REC_HEADER_STRUCTURE.descr + [
                ('antenna_coord', 'f4', (2, self.nchannels)),
                ('rx_gains', 'u4', (self.nchannels,)),
                ('rx_analysis', 'u4', (self.nchannels,))
            ]
        )

        self.header_rec = numpy.fromfile(self.fp, header_structure, 1)
        self.lat = self.header_rec['lat'][0]
        self.lon = self.header_rec['lon'][0]
        self.delta = self.header_rec['delta_r'][0]
        self.correction = self.header_rec['dmode_rngcorr'][0]
        self.imode = self.header_rec['dmode_index'][0]
        self.antenna = self.header_rec['antenna_coord']
        self.rx_gains = self.header_rec['rx_gains']        
        self.time = self.header_rec['time'][0]               
        dt = datetime.datetime.utcfromtimestamp(self.time)
        if dt.date()>self.datatime.date():
            self.flagDiscontinuousBlock = 1
        self.datatime = dt
        
    def readData(self):
        '''
        Reading and filtering data block record of BLTR rawdata file, filtering is according to status_value.

        Input:
            status_value - Array data is set to NAN for values that are not equal to status_value

        '''

        data_structure = numpy.dtype(
            DATA_STRUCTURE.descr + [
                ('rx_saturation', 'u4', (self.nchannels,)),
                ('chan_offset', 'u4', (2 * self.nchannels,)),
                ('rx_amp', 'u4', (self.nchannels,)),
                ('rx_snr', 'f4', (self.nchannels,)),
                ('cross_snr', 'f4', (self.kchan,)),
                ('sea_power_relative', 'f4', (self.kchan,))]
        )

        data = numpy.fromfile(self.fp, data_structure, self.nranges)

        height = data['range']
        winds = numpy.array(
            (data['zonal'], data['meridional'], data['vertical']))
        snr = data['rx_snr'].T

        winds[numpy.where(winds == -9999.)] = numpy.nan
        winds[:, numpy.where(data['status'] != self.status_value)] = numpy.nan
        snr[numpy.where(snr == -9999.)] = numpy.nan
        snr[:, numpy.where(data['status'] != self.status_value)] = numpy.nan
        snr = numpy.power(10, snr / 10)

        return height, winds, snr

    def set_output(self):
        '''
        Storing data from databuffer to dataOut object
        '''

        self.dataOut.data_SNR = self.snr
        self.dataOut.height = self.height
        self.dataOut.data = self.buffer
        self.dataOut.utctimeInit = self.time
        self.dataOut.utctime = self.dataOut.utctimeInit
        self.dataOut.useLocalTime = False
        self.dataOut.paramInterval = 157
        self.dataOut.timezone = self.timezone
        self.dataOut.site = self.siteFile
        self.dataOut.nrecords = self.nrecords / self.nmodes
        self.dataOut.sizeOfFile = self.sizeOfFile
        self.dataOut.lat = self.lat
        self.dataOut.lon = self.lon
        self.dataOut.channelList = list(range(self.nchannels))
        self.dataOut.kchan = self.kchan        
        self.dataOut.delta = self.delta
        self.dataOut.correction = self.correction
        self.dataOut.nmodes = self.nmodes
        self.dataOut.imode = self.imode
        self.dataOut.antenna = self.antenna
        self.dataOut.rx_gains = self.rx_gains
        self.dataOut.flagNoData = False
        self.dataOut.flagDiscontinuousBlock = self.flagDiscontinuousBlock

    def getData(self):
        '''
        Storing data from databuffer to dataOut object
        '''
        if self.flagNoMoreFiles:
            self.dataOut.flagNoData = True
            log.success('No file left to process', 'BLTRParamReader')
            return 0

        if not self.readNextBlock():
            self.dataOut.flagNoData = True
            return 0

        self.set_output()

        return 1