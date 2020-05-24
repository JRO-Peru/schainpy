'''
Created on Oct 24, 2016

@author: roj- LouVD
'''

import numpy
import copy
import datetime
import time
from time import gmtime

from numpy import transpose

from schainpy.model.proc.jroproc_base import ProcessingUnit, Operation, MPDecorator
from schainpy.model.data.jrodata import Parameters


class BLTRParametersProc(ProcessingUnit):    
    '''
    Processing unit for BLTR parameters data (winds)

    Inputs:
        self.dataOut.nmodes - Number of operation modes
        self.dataOut.nchannels - Number of channels
        self.dataOut.nranges - Number of ranges

        self.dataOut.data_SNR - SNR array 
        self.dataOut.data_output - Zonal, Vertical and Meridional velocity array
        self.dataOut.height - Height array (km)
        self.dataOut.time - Time array (seconds)

        self.dataOut.fileIndex -Index of the file currently read
        self.dataOut.lat - Latitude coordinate of BLTR location

        self.dataOut.doy - Experiment doy (number of the day in the current year) 
        self.dataOut.month - Experiment month
        self.dataOut.day - Experiment day
        self.dataOut.year - Experiment year
    '''

    def __init__(self):
        '''
        Inputs: None           
        '''
        ProcessingUnit.__init__(self)
        self.dataOut = Parameters()

    def setup(self, mode):
        '''
        '''
        self.dataOut.mode = mode

    def run(self, mode, snr_threshold=None):
        '''
        Inputs:
            mode = High resolution (0) or Low resolution (1) data
            snr_threshold = snr filter value
        '''

        if not self.isConfig:
            self.setup(mode)
            self.isConfig = True

        if self.dataIn.type == 'Parameters':
            self.dataOut.copy(self.dataIn)
        
        self.dataOut.data_param = self.dataOut.data[mode]
        self.dataOut.heightList = self.dataOut.height[0]
        self.dataOut.data_SNR = self.dataOut.data_SNR[mode]

        if snr_threshold is not None:
            SNRavg = numpy.average(self.dataOut.data_SNR, axis=0)
            SNRavgdB = 10*numpy.log10(SNRavg)
            for i in range(3):
                self.dataOut.data_param[i][SNRavgdB <= snr_threshold] = numpy.nan

# TODO

class OutliersFilter(Operation):

    def __init__(self):
        '''
        '''
        Operation.__init__(self)

    def run(self, svalue2, method, factor, filter, npoints=9):
        '''
        Inputs:
            svalue    -  string to select array velocity
            svalue2    -  string to choose axis filtering
            method    - 0 for SMOOTH or 1 for MEDIAN
            factor    - number used to set threshold
            filter    - 1 for data filtering using the standard deviation criteria else 0
            npoints    - number of points for mask filter
        '''

        print('    Outliers Filter {} {} / threshold = {}'.format(svalue, svalue, factor))

        
        yaxis = self.dataOut.heightList
        xaxis = numpy.array([[self.dataOut.utctime]])        

        # Zonal
        value_temp = self.dataOut.data_output[0]

        # Zonal
        value_temp = self.dataOut.data_output[1]
        
        # Vertical
        value_temp = numpy.transpose(self.dataOut.data_output[2])

        htemp = yaxis
        std = value_temp
        for h in range(len(htemp)):
            nvalues_valid = len(numpy.where(numpy.isfinite(value_temp[h]))[0])
            minvalid = npoints
            
            #only if valid values greater than the minimum required (10%)
            if nvalues_valid > minvalid:
                
                if method == 0:
                    #SMOOTH                    
                    w = value_temp[h] - self.Smooth(input=value_temp[h], width=npoints, edge_truncate=1)
                                            
                                          
                if method == 1:
                    #MEDIAN                        
                    w = value_temp[h] - self.Median(input=value_temp[h], width = npoints)                    
                                    
                dw = numpy.std(w[numpy.where(numpy.isfinite(w))],ddof = 1)                       
                
                threshold = dw*factor
                value_temp[numpy.where(w > threshold),h] = numpy.nan
                value_temp[numpy.where(w < -1*threshold),h] = numpy.nan

                                    
        #At the end
        if svalue2 == 'inHeight':
            value_temp = numpy.transpose(value_temp)
        output_array[:,m] = value_temp
        
        if svalue == 'zonal':
            self.dataOut.data_output[0] = output_array
           
        elif svalue == 'meridional':
            self.dataOut.data_output[1] = output_array

        elif svalue == 'vertical':
            self.dataOut.data_output[2] = output_array   
  
        return self.dataOut.data_output       

    
    def Median(self,input,width):
        '''
        Inputs:
            input - Velocity array
            width - Number of points for mask filter
            
        '''
        
        if numpy.mod(width,2) == 1:
            pc = int((width - 1) / 2)    
        cont = 0
        output = []
        
        for i in range(len(input)):        
            if i >= pc and i < len(input) - pc:
                new2 = input[i-pc:i+pc+1]            
                temp = numpy.where(numpy.isfinite(new2))
                new = new2[temp] 
                value = numpy.median(new)        
                output.append(value)
                
        output = numpy.array(output)
        output = numpy.hstack((input[0:pc],output))
        output = numpy.hstack((output,input[-pc:len(input)]))
        
        return output
    
    def Smooth(self,input,width,edge_truncate = None):
        '''
        Inputs:
            input - Velocity array
            width - Number of points for mask filter
            edge_truncate - 1 for truncate the convolution product else 
        
        '''        

        if numpy.mod(width,2) == 0:
            real_width = width + 1
            nzeros = width / 2
        else:
            real_width = width
            nzeros = (width - 1) / 2
    
        half_width = int(real_width)/2
        length = len(input)
        
        gate = numpy.ones(real_width,dtype='float')
        norm_of_gate = numpy.sum(gate)
        
        nan_process = 0
        nan_id = numpy.where(numpy.isnan(input))    
        if len(nan_id[0]) > 0:
            nan_process = 1
            pb = numpy.zeros(len(input))
            pb[nan_id] = 1.
            input[nan_id] = 0.
        
        if edge_truncate == True:
            output = numpy.convolve(input/norm_of_gate,gate,mode='same') 
        elif edge_truncate == False or edge_truncate == None:
            output = numpy.convolve(input/norm_of_gate,gate,mode='valid')
            output = numpy.hstack((input[0:half_width],output))
            output = numpy.hstack((output,input[len(input)-half_width:len(input)]))
                
        if nan_process:        
            pb = numpy.convolve(pb/norm_of_gate,gate,mode='valid') 
            pb = numpy.hstack((numpy.zeros(half_width),pb))
            pb = numpy.hstack((pb,numpy.zeros(half_width)))        
            output[numpy.where(pb > 0.9999)] = numpy.nan
            input[nan_id] = numpy.nan
        return output
    
    def Average(self,aver=0,nhaver=1): 
        '''
        Inputs:
            aver - Indicates the time period over which is averaged or consensus data
            nhaver - Indicates the decimation factor in heights  
        
        '''      
        nhpoints = 48 
                
        lat_piura = -5.17
        lat_huancayo = -12.04        
        lat_porcuya = -5.8
        
        if '%2.2f'%self.dataOut.lat == '%2.2f'%lat_piura:            
            hcm = 3.
            if self.dataOut.year == 2003 :            
                if self.dataOut.doy >= 25 and self.dataOut.doy < 64:
                    nhpoints = 12                
        
        elif '%2.2f'%self.dataOut.lat == '%2.2f'%lat_huancayo:            
            hcm = 3.
            if self.dataOut.year == 2003 :
                if self.dataOut.doy >= 25 and self.dataOut.doy < 64:
                    nhpoints = 12
                
            
        elif '%2.2f'%self.dataOut.lat == '%2.2f'%lat_porcuya:            
            hcm = 5.#2
        
        pdata = 0.2
        taver = [1,2,3,4,6,8,12,24]
        t0 = 0
        tf = 24        
        ntime =(tf-t0)/taver[aver]        
        ti = numpy.arange(ntime)
        tf = numpy.arange(ntime) + taver[aver]
        
        
        old_height = self.dataOut.heightList
        
        if nhaver > 1:
            num_hei = len(self.dataOut.heightList)/nhaver/self.dataOut.nmodes
            deltha = 0.05*nhaver
            minhvalid = pdata*nhaver
            for im in range(self.dataOut.nmodes):
                new_height = numpy.arange(num_hei)*deltha + self.dataOut.height[im,0] + deltha/2.
        
        
        data_fHeigths_List = []
        data_fZonal_List = []
        data_fMeridional_List = []
        data_fVertical_List = []
        startDTList = []
        

        for i in range(ntime): 
            height = old_height
            
            start = datetime.datetime(self.dataOut.year,self.dataOut.month,self.dataOut.day) + datetime.timedelta(hours = int(ti[i])) - datetime.timedelta(hours = 5)
            stop = datetime.datetime(self.dataOut.year,self.dataOut.month,self.dataOut.day) + datetime.timedelta(hours = int(tf[i])) - datetime.timedelta(hours = 5)
               
                        
            limit_sec1 = time.mktime(start.timetuple())
            limit_sec2 = time.mktime(stop.timetuple())
            
            t1 = numpy.where(self.f_timesec >= limit_sec1) 
            t2 = numpy.where(self.f_timesec < limit_sec2) 
            time_select = []
            for val_sec in t1[0]:
                if val_sec in t2[0]:
                    time_select.append(val_sec)
            
            
            time_select = numpy.array(time_select,dtype = 'int')
            minvalid = numpy.ceil(pdata*nhpoints)
            
            zon_aver = numpy.zeros([self.dataOut.nranges,self.dataOut.nmodes],dtype='f4') + numpy.nan
            mer_aver = numpy.zeros([self.dataOut.nranges,self.dataOut.nmodes],dtype='f4') + numpy.nan
            ver_aver = numpy.zeros([self.dataOut.nranges,self.dataOut.nmodes],dtype='f4') + numpy.nan
            
            if nhaver > 1:
                new_zon_aver = numpy.zeros([num_hei,self.dataOut.nmodes],dtype='f4') + numpy.nan
                new_mer_aver = numpy.zeros([num_hei,self.dataOut.nmodes],dtype='f4') + numpy.nan
                new_ver_aver = numpy.zeros([num_hei,self.dataOut.nmodes],dtype='f4') + numpy.nan
            
            if len(time_select) > minvalid:
                time_average = self.f_timesec[time_select]
                
                for im in range(self.dataOut.nmodes):
                    
                    for ih in range(self.dataOut.nranges):
                        if numpy.sum(numpy.isfinite(self.f_zon[time_select,ih,im])) >= minvalid:                            
                            zon_aver[ih,im] = numpy.nansum(self.f_zon[time_select,ih,im]) / numpy.sum(numpy.isfinite(self.f_zon[time_select,ih,im]))
                        
                        if numpy.sum(numpy.isfinite(self.f_mer[time_select,ih,im])) >= minvalid:
                            mer_aver[ih,im] = numpy.nansum(self.f_mer[time_select,ih,im]) / numpy.sum(numpy.isfinite(self.f_mer[time_select,ih,im]))
                        
                        if numpy.sum(numpy.isfinite(self.f_ver[time_select,ih,im])) >= minvalid:                            
                            ver_aver[ih,im] = numpy.nansum(self.f_ver[time_select,ih,im]) / numpy.sum(numpy.isfinite(self.f_ver[time_select,ih,im]))
                    
                    if nhaver > 1:
                        for ih in range(num_hei):
                            hvalid = numpy.arange(nhaver) + nhaver*ih
                            
                            if numpy.sum(numpy.isfinite(zon_aver[hvalid,im])) >= minvalid:
                                new_zon_aver[ih,im] = numpy.nansum(zon_aver[hvalid,im]) /  numpy.sum(numpy.isfinite(zon_aver[hvalid,im]))
                            
                            if numpy.sum(numpy.isfinite(mer_aver[hvalid,im])) >= minvalid:
                                new_mer_aver[ih,im] = numpy.nansum(mer_aver[hvalid,im]) /  numpy.sum(numpy.isfinite(mer_aver[hvalid,im]))
                            
                            if numpy.sum(numpy.isfinite(ver_aver[hvalid,im])) >= minvalid:
                                new_ver_aver[ih,im] = numpy.nansum(ver_aver[hvalid,im]) /  numpy.sum(numpy.isfinite(ver_aver[hvalid,im]))
                if nhaver > 1:
                    zon_aver = new_zon_aver
                    mer_aver = new_mer_aver
                    ver_aver = new_ver_aver
                    height = new_height
                
                                
                tstart = time_average[0]
                tend = time_average[-1]
                startTime = time.gmtime(tstart)
                                
                year = startTime.tm_year
                month = startTime.tm_mon
                day = startTime.tm_mday
                hour = startTime.tm_hour
                minute = startTime.tm_min            
                second = startTime.tm_sec
                
                startDTList.append(datetime.datetime(year,month,day,hour,minute,second))
                
                
                o_height = numpy.array([])
                o_zon_aver = numpy.array([])
                o_mer_aver = numpy.array([])
                o_ver_aver = numpy.array([])
                if self.dataOut.nmodes > 1:
                    for im in range(self.dataOut.nmodes):
                        
                        if im == 0:
                            h_select = numpy.where(numpy.bitwise_and(height[0,:] >=0,height[0,:] <= hcm,numpy.isfinite(height[0,:])))
                        else:                            
                            h_select = numpy.where(numpy.bitwise_and(height[1,:] > hcm,height[1,:] < 20,numpy.isfinite(height[1,:])))

                                                
                        ht = h_select[0]
                        
                        o_height = numpy.hstack((o_height,height[im,ht]))
                        o_zon_aver = numpy.hstack((o_zon_aver,zon_aver[ht,im]))
                        o_mer_aver = numpy.hstack((o_mer_aver,mer_aver[ht,im]))
                        o_ver_aver = numpy.hstack((o_ver_aver,ver_aver[ht,im]))

                    data_fHeigths_List.append(o_height)
                    data_fZonal_List.append(o_zon_aver)
                    data_fMeridional_List.append(o_mer_aver)
                    data_fVertical_List.append(o_ver_aver)
                        
 
                else:
                    h_select = numpy.where(numpy.bitwise_and(height[0,:] <= hcm,numpy.isfinite(height[0,:])))
                    ht = h_select[0]
                    o_height = numpy.hstack((o_height,height[im,ht]))
                    o_zon_aver = numpy.hstack((o_zon_aver,zon_aver[ht,im]))
                    o_mer_aver = numpy.hstack((o_mer_aver,mer_aver[ht,im]))
                    o_ver_aver = numpy.hstack((o_ver_aver,ver_aver[ht,im]))

                    data_fHeigths_List.append(o_height)
                    data_fZonal_List.append(o_zon_aver)
                    data_fMeridional_List.append(o_mer_aver)
                    data_fVertical_List.append(o_ver_aver)
                  
        
        return startDTList, data_fHeigths_List, data_fZonal_List, data_fMeridional_List, data_fVertical_List


