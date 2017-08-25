'''
Created on Aug 1, 2017

@author: Juan C. Espinoza
'''

import os
import sys
import time
import datetime

import numpy

from schainpy.model.proc.jroproc_base import ProcessingUnit, Operation
from schainpy.model.data.jrodata import Parameters
from schainpy.model.data.jroheaderIO import RadarControllerHeader, SystemHeader
from schainpy.model.graphics.jroplot_parameters import WindProfilerPlot
from schainpy.model.io.jroIO_base import *

try:
    import madrigal
    import madrigal.cedar
    from madrigal.cedar import MadrigalCatalogRecord
except:
    print 'You should install "madrigal library" module if you want to read/write Madrigal data'


class MADWriter(Operation):
    
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
    
