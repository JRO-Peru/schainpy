'''
Created on Nov 9, 2016

@author: roj- LouVD
'''

import numpy 
import os.path
import sys
import time
import datetime
from sys import path
from os.path import dirname
from mimify import HeaderFile
from numpy import size, asarray
from datetime import datetime
from schainpy.model.proc.jroproc_base import ProcessingUnit, Operation
from schainpy.model.data.jrodata import Parameters
from schainpy.model.data.jroheaderIO import RadarControllerHeader, SystemHeader
from schainpy.model.graphics.jroplot_parameters import WindProfilerPlot
from schainpy.model.io.jroIO_base import *

import schainpy
#import madrigal
#import madrigal.cedar
#from madrigal.cedar import MadrigalCatalogRecord

import warnings
from time import gmtime
from math import floor

warnings.simplefilter("error")
from numpy.lib.nanfunctions import nansum
warnings.simplefilter('ignore', FutureWarning)


class testBLTRReader(ProcessingUnit):

    
    def __init__(self, **kwargs):
        
        path = None
        startDate = None
        endDate = None
        startTime = None
        endTime = None
        startTime = None
        endTime = None
        
        isConfig = False
        dataOut = None
        walk = None  
        ext = 'swwma'
        fileList = []
        fileIndex = -1
        timezone = None
        filename = None
        
        timearray = None
        height = None
        snr_ref = None
        zon_ref = None
        ver_ref = None
        mer_ref = None
        nmodes = None
        nchannels = None
        nranges = None
        year = None
        month = None
        day = None
        lat = None
        lon = None 
        siteFile = None
        
        ProcessingUnit.__init__(self , **kwargs) 
        self.dataOut = self.createObjByDefault()         
        self.imode = 0
        self.counter_records = 0

        self.isConfig = False
        self.flagNoMoreFiles = 0
    
        self.buffer = None


    def createObjByDefault(self):
               
        dataObj = Parameters()
        
        return dataObj 
    
    def info(self):
        '''
        Experience information
        
        '''
        self.hoy = datetime.datetime.now()
        place = 'Jicamarca Radio Observatory'
        signalchainweb='http://jro-dev.igp.gob.pe:3000/projects/signal-chain/wiki/Manual_de_Desarrollador'
        print '{} at {}'.format(self.hoy,place)
        print 'Boundary Layer and Tropospheric Radar (BLTR) script, Wind velocities and SNR from *.sswma files'
        print '{}  \n'.format(signalchainweb)

    def run(self, path, startDate, endDate, ext, startTime, endTime, queue=None):

        if not(self.isConfig):
            self.setup(path, startDate, endDate, ext)
            self.isConfig = True

        self.getData()
        
    def setup(self,
              path=None,
              startDate=None,
              endDate=None,
              ext=None,
              startTime=datetime.time(0, 0, 0),
              endTime=datetime.time(23, 59, 59),
              timezone=0):
        
        self.info()
        self.path = path 
        if self.path == None:
            raise ValueError, "The path is not valid"
        
        if ext == None:
            ext = self.ext
        
        self.searchFiles(self.path, startDate, endDate, ext)
        
        self.timezone = timezone
        self.ext = ext    
        self.fileIndex = -1       
        
        if not(self.fileList):
            raise  Warning, "There is no files matching these date in the folder: %s. \n Check 'startDate' and 'endDate' "%(path)       

        
        if not(self.setNextFile()):

            print 'not next file'
            if (startDate!=None) and (endDate!=None):
                print "No files in range: %s - %s" %(datetime.datetime.combine(startDate,startTime).ctime(), datetime.datetime.combine(endDate,endTime).ctime())
            elif startDate != None:
                print "No files in range: %s" %(datetime.datetime.combine(startDate,startTime).ctime())
            else:
                print "No files"

            sys.exit(-1)
        
    def searchFiles(self, path, startDate, endDate, ext=None):
        '''
         Searching for BLTR rawdata file in path
         Creating a list of file to proces included in [startDate,endDate]
         
         Input: 
             path - Path to find BLTR rawdata files
             startDate - Select file from this date
             enDate - Select file until this date
             ext - Extension of the file to read
              
        '''    

        fullpath = path
        foldercounter = 0

        print 'Searching file in %s ' % (fullpath)
        fileList0 = glob.glob1(fullpath, "*%s" % ext)
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

            if not ((startDate <= dateFile) and (endDate > dateFile)):
                continue
            
            self.fileList.append(thisFile)
            self.dateFileList.append(dateFile)

        return 1      


    def setNextFile(self):
        
        idFile = self.fileIndex

        while (True):
            idFile += 1  
            if idFile >= len(self.fileList): 
                print '\nNo more files in the folder'
                print 'Total number of file(s) read : {}'.format(self.fileIndex + 1)
                print  'Time of processing : {}'.format(datetime.datetime.now()- self.hoy)
                self.flagNoMoreFiles = 1
                return 0
            if self.isConfig: print '------------------------[Next File]---------------------------'
            filename = os.path.join(self.path, self.fileList[idFile])                        
            self.Open(filename)
            
            print '\n[Setting file] (%s) ...' % self.fileList[idFile]
            
            break
        
        self.flagIsNewFile =0
 
        self.fileIndex = idFile
        self.filename = filename
        print 'File:',self.filename

        return 1    

    def readDataBlock(self):
                              
                
        self.readHeader()
        self.dataRecords(0)

        print '[New Record] record: {} /{} // file {}/{}'.format(self.counter_records,self.nrecords,self.fileIndex+1,len(self.fileList))  
        
        self.setDataBuffer() 
        
        self.flagIsNewBlock = 1
        
        if self.counter_records > self.nrecords: 
            self.flagIsNewFile = 1        
            return 0
        
        return 1
    
    def setDataBuffer(self):
        
        '''
        Storing data from one block
        
        '''   
        self.t = datetime.datetime(self.year, self.month, self.day)
        self.doy = time.localtime(time.mktime(self.t.timetuple())).tm_yday
        self.buffer = numpy.squeeze(numpy.array([[self.one_snr],[self.one_zonal],[self.one_vertical],[self.one_meridional],
                                    [self.time],[self.height],[self.fileIndex],
                                    [self.year],[self.month],[self.day],[self.t],[self.doy]]))

        self.dataOut.time1 = self.time1
        
    def Open(self, filename):
        '''
        Opening BLTR rawdata file defined by filename
        
        Inputs:
            
            filename    - Full path name of BLTR rawdata file   
            
        '''     
        [dir, name] = os.path.split(filename)
        strFile = name.split('.')
        self.siteFile = strFile[0]  # 'peru2' ---> Piura  -   'peru1' ---> Huancayo or Porcuya

        self.filename = filename
        if os.path.isfile(self.filename) == False:
            print 'File do not exist. Check "filename"'
            sys.exit(0)   
    
        self.h_file = numpy.dtype([                      
                          ('FMN', '<u4'),
                          ('nrec', '<u4'),
                          ('fr_offset', '<u4'),
                          ('id', '<u4'),
                          ('site', 'u1', (32,))                          
                          ])
        self.pointer = open(self.filename, 'rb')  # rb : Read Binary
        print self.filename
        self.header_file = numpy.fromfile(self.pointer, self.h_file, 1) 
        print self.header_file
        self.nrecords = self.header_file['nrec'][0]         
         
        self.sizeOfFile = os.path.getsize(self.filename)

        self.time = numpy.zeros([2, self.nrecords], dtype='u4')
        self.counter_records = 0
        self.count = 0
        self.flag_initialArray = False
 
        self.year = 0
        self.month = 0
        self.day = 0    
    
    def hasNotDataInBuffer(self):

        if self.buffer == None:
            return 1
        return 0

    def getData(self):
        '''
        Storing data from databuffer to dataOut object
        
        '''
        if self.flagNoMoreFiles==1:
            self.dataOut.flagNoData = True
            print 'No file left to process'
            return 0 
                 
        self.flagIsNewBlock = 0
        
        if self.hasNotDataInBuffer():
            
            if self.flagIsNewFile==0:
                
                self.readNextBlock() 
                '''RETURN A BLOCK OF DATA'''    
                if self.flagNoMoreFiles==0:            
                    self.dataOut.data_SNR = self.buffer[0]
                    self.dataOut.time = self.buffer[4]
                    self.dataOut.height = self.height
                    
                    self.dataOut.height= self.height
                    self.dataOut.data_output = numpy.squeeze(numpy.array([[self.buffer[1]],
                                                                        [self.buffer[3]],
                                                                        [self.buffer[2]]])) 
    
#                   
                    
                    self.dataOut.day, self.dataOut.month, self.dataOut.year = self.buffer[9], self.buffer[8], self.buffer[7]
    
                    self.dataOut.utctimeInit = self.time1
                    self.dataOut.utctime = self.dataOut.utctimeInit        
                    self.dataOut.counter_records = self.counter_records
                    self.dataOut.nrecords = self.nrecords
    
                    self.setHeader()
          
                    self.buffer = None
                    self.dataOut.flagNoData = False    

    def readNextBlock(self):
        
        if not(self.setNewBlock()):
            return 0

        if not(self.readDataBlock()):
            return 0

        if self.flagIsNewFile:
            self.setNextFile()
        
        return 1

    def setNewBlock(self):

        if self.pointer==None:
            return 0
        
        if self.flagIsNewFile:
            return 1
        
        if self.counter_records < self.nrecords:
            return 1  
        
        if not(self.setNextFile()):
            return 0
        
        return 1

    def readHeader(self):
        '''
        RecordHeader of BLTR rawdata file
        '''
        if self.pointer.tell() == self.sizeOfFile:
            print 'End of File'
            return
        
        self.h_rec1 = numpy.dtype([                          
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
                
        self.header_rec1 = numpy.fromfile(self.pointer, self.h_rec1, 1) 
        self.lat = self.header_rec1['lat'][0]
        self.lon = self.header_rec1['lon'][0]        
        self.nchannels = self.header_rec1['nchan'][0] / 2
        self.kchan = self.header_rec1['nrxs'][0]
        self.nranges = self.header_rec1['nranges'][0]
        self.deltha = self.header_rec1['delta_r'][0]
        
        self.correction = self.header_rec1['dmode_rngcorr'][0]
        self.nmodes = self.header_rec1['nmodes'][0]
        self.imode = self.header_rec1['dmode_index'][0]

        self.h_rec2 = numpy.dtype([                      
                          ('antenna_coord', 'f4', (2, self.nchannels)),
                          ('rx_gains', 'u4', (self.nchannels,)),
                          ('rx_analysis', 'u4', (self.nchannels,))                                                    
                          ])
        
        self.header_rec2 = numpy.fromfile(self.pointer, self.h_rec2, 1)  # header rec2
        self.antenna = self.header_rec2['antenna_coord']
        self.rx_gains = self.header_rec2['rx_gains']
        
        self.d_rec = numpy.dtype ([ 
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
                        ('sea_algorithm', '<u4'),
                        ('rx_saturation', 'u4', (self.nchannels,)),
                        ('chan_offset', 'u4', (2 * self.nchannels,)),
                        ('rx_amp', 'u4', (self.nchannels,)),
                        ('rx_snr', 'f4', (self.nchannels,)),
                        ('cross_snr', 'f4', (self.kchan,)),
                        ('sea_power_relative', 'f4', (self.kchan,))    
                ])

        # Memory allocation
        if not(self.flag_initialArray):
            self.height = numpy.zeros([2, self.nranges], dtype='f4') + numpy.nan
            self.p_zonal = numpy.zeros([self.nrecords, self.nranges, 2], dtype='f4') + numpy.nan
            self.p_meridional = numpy.zeros([self.nrecords, self.nranges, 2], dtype='f4') + numpy.nan
            self.p_vertical = numpy.zeros([self.nrecords, self.nranges, 2], dtype='f4') + numpy.nan
            self.p_snr = numpy.zeros([self.nrecords, self.nranges, self.kchan, 2], dtype='f4') + numpy.nan
            self.flag_initialArray = True

        self.time[self.imode, self.count] = self.header_rec1['time'][0]
        self.time1 = self.header_rec1['time'][0]
        tseconds = self.header_rec1['time'][0]
        local_t1 = time.localtime(tseconds)
        self.year = local_t1.tm_year
        self.month = local_t1.tm_mon
        self.day = local_t1.tm_mday
        self.t = datetime.datetime(self.year, self.month, self.day)

           
    def setHeader(self):
        '''
        Saving metada on dataOut object
        
        '''
        self.dataOut.type = 'Parameters'
        self.dataOut.useLocalTime = False
        # self.dataOut.outputInterval = 157
        self.dataOut.paramInterval = 157 
        self.dataOut.timezone = self.timezone
        self.dataOut.site = self.siteFile
        self.dataOut.nrecords = self.nrecords
        self.dataOut.sizeOfFile = self.sizeOfFile 
        self.dataOut.lat = self.lat
        self.dataOut.lon = self.lon
        self.dataOut.nchannels = self.nchannels
        self.dataOut.kchan = self.kchan
        self.dataOut.nranges = self.nranges
        self.dataOut.deltha = self.deltha
        self.dataOut.correction = self.correction
        self.dataOut.nmodes = self.nmodes
        self.dataOut.imode = self.imode
        self.dataOut.antenna = self.antenna
        self.dataOut.rx_gains = self.rx_gains
        
    def dataRecords(self, status_value):
        '''
        Reading and filtering data block record of BLTR rawdata file, filtering is according to status_value.
        
        Input:
            status_value - Array data is set to NAN for values that are not equal to status_value
        
        '''                         
        data_rec = numpy.fromfile(self.pointer, self.d_rec, self.nranges)
        status = []
        zonal = []
        meridional = []
        vertical = []
        rx_snr = []
                
        index = 0
        for rec in data_rec:
            status.append(rec['status'])
            zonal.append(rec['zonal'])
            meridional.append(rec['meridional'])
            vertical.append(rec['vertical'])
            self.height[self.imode, index] = (rec['range'] - self.correction) / 1000.
            numpy.seterr(all='ignore')
            index = index + 1
            rx_snr.append(rec['rx_snr'])
        
        status = numpy.array(status, dtype='int')       
        zonal = numpy.array(zonal, dtype='float')
        meridional = numpy.array(meridional, dtype='float')
        vertical = numpy.array(vertical, dtype='float')
        rx_snr = numpy.array(rx_snr, dtype='float') 
        

        
        rx_snr = rx_snr.reshape((self.nranges, self.nchannels))
    
        # FILTERING DATA
        stvalue = status_value        
        zonal[numpy.where(zonal == -9999.)] = numpy.nan        
        zonal[numpy.where(status != stvalue)] = numpy.nan        
        self.p_zonal[self.count, :, self.imode] = zonal
        self.one_zonal= self.p_zonal[self.count, :, :]

        meridional[numpy.where(meridional == -9999.)] = numpy.nan
        meridional[numpy.where(status != stvalue)] = numpy.nan
        self.p_meridional[self.count, :, self.imode] = meridional
        self.one_meridional = self.p_meridional[self.count, :, :]
        
        vertical[numpy.where(vertical == -9999.)] = numpy.nan
        vertical[numpy.where(status != stvalue)] = numpy.nan
        self.p_vertical[self.count, :, self.imode] = vertical 
        self.one_vertical = self.p_vertical[self.count, :, :]
        
        rx_snr[numpy.where(rx_snr == -9999.)] = numpy.nan        
        rx_snr[numpy.where(status != stvalue), :] = numpy.nan

        
        for k in range(self.kchan):    
            self.p_snr[self.count, :, k, self.imode] = numpy.power(10, rx_snr[:, k] / 10)
        
        self.one_snr = self.p_snr[self.count, :, :, :]
        if self.nmodes == 2:
            self.count = self.count + self.imode
        else:
            self.count = self.count + 1
        
        self.imode +=1
        self.counter_records = self.counter_records + 1
        
        self.zon_ref = self.p_zonal
        self.ver_ref = self.p_vertical
        self.mer_ref = self.p_meridional
        self.snr_ref = self.p_snr
        
        

    
    def Close (self):
        '''
        Closing BLTR rawdata file
        '''
        if self.pointer.tell() == self.sizeOfFile:            
            self.pointer.close()
            return



class testBLTRWriter(Operation):
 
    
    def __init__(self):
        
        Operation.__init__(self)
        self.dataOut = Parameters()
        self.path = None
        self.dataOut = None
        self.flagIsNewFile=1
        self.ext = ".hdf5"

        return
    
    def run(self, dataOut, path , modetowrite,**kwargs):

        if self.flagIsNewFile:
            flagdata = self.setup(dataOut, path, modetowrite)
            
        self.putData() 
        return
    
    def setup(self, dataOut, path, modetowrite):
        '''
        Recovering data to write in new *.hdf5 file
        Inputs:
            modew -- mode to write (1 or 2)
            path --  destination path
                   
        '''
        
        self.im = modetowrite-1  
        if  self.im!=0 and self.im!=1:
            raise ValueError, 'Check "modetowrite" value. Must be egual to 1 or 2, "{}" is not valid. '.format(modetowrite)
        
        self.dataOut = dataOut
        self.nmodes = self.dataOut.nmodes         
        self.nchannels = self.dataOut.nchannels
        self.lat = self.dataOut.lat
        self.lon = self.dataOut.lon 
        self.hcm = 3         
        self.thisDate = self.dataOut.utctimeInit     
        self.year = self.dataOut.year 
        self.month = self.dataOut.month 
        self.day = self.dataOut.day
        self.path = path
                
        self.flagIsNewFile = 0
        
        return 1   
     
    def setFile(self):
        '''
        - Determining the file name for each mode of operation
            kinst - Kind of Instrument (mnemotic)
            kindat - Kind of Data (mnemotic)        
        
        - Creating a cedarObject   
        
        ''' 
        lat_piura = -5.17
        lat_huancayo = -12.04
        lat_porcuya = -5.8 
             
        if '%2.2f' % self.lat == '%2.2f' % lat_piura:            
                self.instMnemonic = 'pbr'                
                 
        elif '%2.2f' % self.lat == '%2.2f' % lat_huancayo:            
                self.instMnemonic = 'hbr'
                     
        elif '%2.2f' % self.lat == '%2.2f' % lat_porcuya:            
                self.instMnemonic = 'obr'
        else: raise Warning, "The site of file read doesn't match any site known. Only file from Huancayo, Piura and Porcuya can be processed.\n Check the file "
        
        mode = ['_mode1','_mode2'] 
        
        self.hdf5filename = '%s%4.4d%2.2d%2.2d%s%s' % (self.instMnemonic,
                                            self.year,
                                            self.month,
                                            self.day,
                                            mode[self.im],
                                            self.ext)     
       
        self.fullname=os.path.join(self.path,self.hdf5filename)

        if os.path.isfile(self.fullname) : 
            print "Destination path '%s' already exists. Previous file deleted. " %self.fullname
            os.remove(self.fullname)
            
             # Identify kinst and kindat
        InstName = self.hdf5filename[0:3]
        KinstList = [1000, 1001, 1002]        
        KinstId = {'pbr':0, 'hbr':1, 'obr':2}  # pbr:piura, hbr:huancayo, obr:porcuya
        KindatList = [1600, 1601]  # mode 1, mode 2
        self.type = KinstId[InstName]
        self.kinst = KinstList[self.type]
        self.kindat = KindatList[self.im] 
        
        try:
            self.cedarObj = madrigal.cedar.MadrigalCedarFile(self.fullname, True)  
        except ValueError, message:
            print '[Error]: Impossible to create a cedar object with "madrigal.cedar.MadrigalCedarFile" '
            return
        
        return 1  
     
    def writeBlock(self):
        '''
        - Selecting mode of operation:
            
            bltr high resolution mode 1 - Low Atmosphere (0 - 3km) //  bltr high resolution mode 2 - High Atmosphere (0 - 10km) 
            msnr - Average Signal Noise Ratio in dB
            hcm - 3 km

        - Filling the cedarObject by a block: each array data entry is assigned a code that defines the parameter to write to the file
            
            GDLATR - Reference geod latitude (deg)
            GDLONR - Reference geographic longitude (deg)
            GDLAT2 - Geodetic latitude of second inst (deg)
            GLON2 - Geographic longitude of second inst (deg)
     
            GDALT - Geodetic altitude (height) (km)
            SNL - Log10 (signal to noise ratio)  
            VN1P2 - Neutral wind in direction 1 (eastward) (m/s), ie zonal wind
            VN2P2 - Neutral wind in direction 2 (northward) (m/s), ie meridional wind
            EL2 - Ending elevation angle (deg), ie vertical wind
            
            Other parameters: /madrigal3/metadata/parcodes.tab 
        
        '''

        self.z_zon = self.dataOut.data_output[0,:,:]
        self.z_mer =self.dataOut.data_output[1,:,:]
        self.z_ver = self.dataOut.data_output[2,:,:]

        if self.im == 0:
            h_select = numpy.where(numpy.bitwise_and(self.dataOut.height[0, :] >= 0., self.dataOut.height[0, :] <= self.hcm, numpy.isfinite(self.dataOut.height[0, :])))
        else:                                            
            h_select = numpy.where(numpy.bitwise_and(self.dataOut.height[0, :] >= 0., self.dataOut.height[0, :] < 20, numpy.isfinite(self.dataOut.height[0, :])))                            
        
        ht = h_select[0]
    
        self.o_height = self.dataOut.height[self.im, ht]
        self.o_zon = self.z_zon[ht, self.im]
        self.o_mer = self.z_mer[ht, self.im]
        self.o_ver = self.z_ver[ht, self.im]
        o_snr = self.dataOut.data_SNR[ :, :, self.im]

        o_snr = o_snr[ht, :]
    
        ndiv = numpy.nansum((numpy.isfinite(o_snr)), 1)
        ndiv = ndiv.astype(float)        
            
        sel_div = numpy.where(ndiv == 0.)
        ndiv[sel_div] = numpy.nan      
        
        if self.nchannels > 1:
            msnr = numpy.nansum(o_snr, axis=1)
        else:
            msnr = o_snr

        try:
            self.msnr = 10 * numpy.log10(msnr / ndiv)
        except ZeroDivisionError:
            self.msnr = 10 * numpy.log10(msnr /1)
            print 'Number of division (ndiv) egal to 1 by default. Check SNR'         
     
        time_t = time.gmtime(self.dataOut.time1)
        year = time_t.tm_year 
        month = time_t.tm_mon
        day = time_t.tm_mday
        hour = time_t.tm_hour
        minute = time_t.tm_min
        second = time_t.tm_sec
        timedate_0 = datetime.datetime(year, month, day, hour, minute, second)

           # 1d parameters
        GDLATR = self.lat
        GDLONR = self.lon
        GDLAT2 = self.lat
        GLON2 = self.lon
              
         # 2d parameters 
        GDALT = self.o_height

        SNL = self.msnr 
        VN1P2 = self.o_zon
        VN2P2 = self.o_mer
        EL2 = self.o_ver
        NROW = len(self.o_height)   
   
        startTime = timedate_0
        endTime = startTime
        self.dataRec = madrigal.cedar.MadrigalDataRecord(self.kinst,
                                                     self.kindat,
                                                     startTime.year,
                                                     startTime.month,
                                                     startTime.day,
                                                     startTime.hour,
                                                     startTime.minute,
                                                     startTime.second,
                                                     0,
                                                     endTime.year,
                                                     endTime.month,
                                                     endTime.day,
                                                     endTime.hour,
                                                     endTime.minute,
                                                     endTime.second,
                                                     0,
                                                     ('gdlatr', 'gdlonr', 'gdlat2', 'glon2'),
                                                     ('gdalt', 'snl', 'vn1p2', 'vn2p2', 'el2'),
                                                     NROW, ind2DList=['gdalt'])
                    
        # Setting 1d values
        self.dataRec.set1D('gdlatr', GDLATR)
        self.dataRec.set1D('gdlonr', GDLONR)
        self.dataRec.set1D('gdlat2', GDLAT2)
        self.dataRec.set1D('glon2', GLON2)

        # Setting 2d values
        for n in range(self.o_height.shape[0]):
            self.dataRec.set2D('gdalt', n, GDALT[n])
            self.dataRec.set2D('snl', n, SNL[n])
            self.dataRec.set2D('vn1p2', n, VN1P2[n])
            self.dataRec.set2D('vn2p2', n, VN2P2[n])
            self.dataRec.set2D('el2', n, EL2[n])
            
          # Appending new data record
        '''
        [MADRIGAL3]There are two ways to write to a MadrigalCedarFile.  Either this method (write) is called after all the
        records have been appended to the MadrigalCedarFile, or dump is called after a certain number of records are appended,
        and then at the end dump is called a final time if there were any records not yet dumped, followed by addArray.
        '''

        self.cedarObj.append(self.dataRec)   
        print '    [Writing] records {} (mode {}).'.format(self.dataOut.counter_records,self.im+1)
        self.cedarObj.dump()
        


            
    def setHeader(self):
        '''
        - Creating self.catHeadObj 
        - Adding information catalog
        - Writing file header

        ''' 
        self.catHeadObj = madrigal.cedar.CatalogHeaderCreator(self.fullname)
        kindatDesc, comments, analyst, history, principleInvestigator = self._info_BLTR()
              
        self.catHeadObj.createCatalog(principleInvestigator="Jarjar",
                                  expPurpose='characterize the atmospheric dynamics in this region where frequently it happens the  El Nino',
                                  sciRemarks="http://madrigal3.haystack.mit.edu/static/CEDARMadrigalHdf5Format.pdf")      
              
        self.catHeadObj.createHeader(kindatDesc, analyst, comments, history)
     
        self.catHeadObj.write()     
        
        print '[File created] path: %s' % (self.fullname) 
              
    def putData(self):

        if self.dataOut.flagNoData:
            return 0
        
        if self.dataOut.counter_records == 1:
            self.setFile()
            print '[Writing] Setting new hdf5 file for the mode {}'.format(self.im+1)
        
        if self.dataOut.counter_records <= self.dataOut.nrecords:
            self.writeBlock()

        
        if self.dataOut.counter_records == self.dataOut.nrecords:
            self.cedarObj.addArray()

            self.setHeader()
            self.flagIsNewFile = 1
                
    def _info_BLTR(self):
         
        kindatDesc = '''--This header is for KINDAT = %d''' % self.kindat
        history = None    
        analyst = '''Jarjar'''
        principleInvestigator = '''
            Jarjar
            Radio Observatorio de Jicamarca
            Instituto Geofisico del Peru
             
            ''' 
        if self.type == 1:
            comments = '''
              
            --These data are provided by two Boundary Layer and Tropospheric Radar (BLTR) deployed at two different locations at Peru(GMT-5), one of them at Piura(5.17 S, 80.64W) and another located at Huancayo (12.04 S, 75.32 W).
                              
            --The purpose of conducting these observations is to measure wind in the differents levels of height, this radar makes measurements the  Zonal(U), Meridional(V) and Vertical(W) wind velocities component in northcoast from Peru. And the main purpose of these mensurations is to characterize the atmospheric dynamics in this region where frequently it happens the  'El Nino Phenomenon'
              
            --In Kindat = 1600, contains information of wind velocities component since 0 Km to 3 Km.
              
            --In Kindat = 1601, contains information of wind velocities component since 0 Km to 10 Km.
                  
            --The Huancayo-BLTR is a VHF Profiler Radar System is a 3 channel coherent receiver pulsed radar utilising state-of-the-art software and computing techniques to acquire, decode, and translate signals obtained from partial reflection echoes in the troposphere, lower stratosphere and mesosphere.   It uses an array of three horizontal spaced and vertically directed receiving antennas. The data is recorded thirty seconds, averaged to one minute mean values of  Height, Zonal, Meridional and Vertical wind. 
              
            --The Huancayo-BLTR was installed in January 2010. This instrument was designed and constructed by Genesis Soft Pty. Ltd. Is constituted by three groups of spaced antennas (distributed) forming an isosceles triangle. 
                                         
                  
            Station _______ Geographic Coord ______ Geomagnetic Coord
                  
            _______________ Latitude _ Longitude __ Latitude _ Longitude
                  
            Huancayo (HUA) __12.04 S ___ 75.32 W _____ -12.05 ____ 352.85 
            Piura (PIU) _____ 5.17 S ___ 80.64 W ______ 5.18 ____ 350.93
                  
            WIND OBSERVATIONS 
              
            --To obtain wind the BLTR uses Spaced Antenna technique (e.g., Briggs 1984). The scatter and reflection it still provided by variations in the refractive index as in the Doppler method(Gage and Basley,1978; Balsley and Gage 1982; Larsen and Rottger 1982), but instead of using the Doppler shift to derive the velocity components, the cross-correlation between signals in an array of three horizontally spaced and vertically directed receiving antennas is used.
                  
            ......................................................................
            For more information, consult the following references:             
            - Balsley, B. B., and K. S. Gage., On the use of radars for operational wind profiling, Bull. Amer. Meteor.Soc.,63, 1009-1018, 1982.
                  
            - Briggs, B. H., The analysis of spaced sensor data by correations techniques, Handbook for MAP, Vol. 13, SCOTEP Secretariat, University of Illinois, Urbana, 166-186, 1984.
                  
            - Gage, K. S., and B.B. Balsley., Doppler radar probing of the clear atmosphere, Bull. Amer. Meteor.Soc., 59, 1074-1093, 1978.
                  
            - Larsen, M. F., The Spaced Antenna Technique for Radar Wind Profiling, Journal of Atm. and Ocean. Technology. , Vol.6, 920-937, 1989.
                  
            - Larsen, M. F., A method for single radar voracity measurements?, Handbook for MAP,SCOSTEP Secretariat, University of the Illinois, Urban, in press, 1989.
            ......................................................................
                  
            ACKNOWLEDGEMENTS:
                  
            --The Piura and Huancayo BLTR are part of the network of instruments operated by the Jicamarca Radio Observatory.
              
            --The Jicamarca Radio Observatory is a facility of the Instituto Geofisico del Peru operated with support from the NSF Cooperative Agreement ATM-0432565 through Cornell University 
                              
            ......................................................................
                  
            Further questions and comments should be addressed to:
                Radio Observatorio de Jicamarca
                Instituto Geofisico del Peru
                Lima, Peru
                Web URL: http://jro.igp.gob.pe
            ......................................................................        
    '''
         
        return kindatDesc, comments, analyst, history, principleInvestigator    
    
