'''
Created on Oct 24, 2016

@author: roj- LouVD
'''

import numpy
import copy
import datetime
import time
from time import gmtime

from jroproc_base import ProcessingUnit
from schainpy.model.data.jrodata import Parameters
from numpy import transpose

from matplotlib import cm
import matplotlib.pyplot as plt
from matplotlib.mlab import griddata




class BLTRProcess(ProcessingUnit):
    isConfig = False
    '''
    Processing unit for BLTR rawdata
    
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

        # Filters
        snr_val = None
        value = None
        svalue2 = None
        method = None
        factor = None
        filter = None
        npoints = None
        status_value = None
        width = None    
        self.flagfirstmode = 0
                         
    def run (self):
        if self.dataIn.type == "Parameters":
            self.dataOut.copy(self.dataIn)
            

    def TimeSelect(self):
        '''
        Selecting the time array according to the day of the experiment with a duration of 24 hours 
        '''
        
        k1 = datetime.datetime(self.dataOut.year, self.dataOut.month, self.dataOut.day) - datetime.timedelta(hours=5)
        k2 = datetime.datetime(self.dataOut.year, self.dataOut.month, self.dataOut.day) + datetime.timedelta(hours=25) - datetime.timedelta(hours=5)
        limit_sec1 = time.mktime(k1.timetuple())
        limit_sec2 = time.mktime(k2.timetuple())
        valid_data = 0
        
        doy = self.dataOut.doy
        t1 = numpy.where(self.dataOut.time[0, :] >= limit_sec1) 
        t2 = numpy.where(self.dataOut.time[0, :] < limit_sec2) 
        time_select = []
        for val_sec in t1[0]:
            if val_sec in t2[0]:
                time_select.append(val_sec)
        
        time_select = numpy.array(time_select, dtype='int')       
        valid_data = valid_data + len(time_select)


        if len(time_select) > 0:
            self.f_timesec = self.dataOut.time[:, time_select]
            snr = self.dataOut.data_SNR[time_select, :, :, :]
            zon = self.dataOut.data_output[0][time_select, :, :]
            mer = self.dataOut.data_output[1][time_select, :, :]
            ver = self.dataOut.data_output[2][time_select, :, :]

        if valid_data > 0:
            self.timesec1 = self.f_timesec[0, :]
            self.f_height = self.dataOut.height 
            self.f_zon = zon
            self.f_mer = mer
            self.f_ver = ver
            self.f_snr = snr
            self.f_timedate = []
            self.f_time = []
            
            for valuet in self.timesec1:             
                time_t = time.gmtime(valuet)
                year = time_t.tm_year 
                month = time_t.tm_mon
                day = time_t.tm_mday
                hour = time_t.tm_hour
                minute = time_t.tm_min
                second = time_t.tm_sec
                f_timedate_0 = datetime.datetime(year, month, day, hour, minute, second)
                self.f_timedate.append(f_timedate_0)

            return self.f_timedate, self.f_timesec, self.f_height, self.f_zon, self.f_mer, self.f_ver, self.f_snr
        
        else:
            self.f_timesec = None
            self.f_timedate = None
            self.f_height = None
            self.f_zon = None
            self.f_mer = None
            self.f_ver = None
            self.f_snr = None
            print 'Invalid time'
   
            return self.f_timedate, self.f_height, self.f_zon, self.f_mer, self.f_ver, self.f_snr
            
    def SnrFilter(self, snr_val,modetofilter):
        '''
        Inputs: snr_val - Threshold value
        
        '''
        if modetofilter!=2 and modetofilter!=1 :
            raise ValueError,'Mode to filter should be "1" or "2". {} is not valid, check "Modetofilter" value.'.format(modetofilter)
        m = modetofilter-1
        
        print '    SNR filter [mode {}]: SNR <= {}: data_output = NA'.format(modetofilter,snr_val)       
        for k in range(self.dataOut.nchannels):
            for r in range(self.dataOut.nranges):
                if self.dataOut.data_SNR[r,k,m] <= snr_val:
                    self.dataOut.data_output[2][r,m] = numpy.nan
                    self.dataOut.data_output[1][r,m] = numpy.nan
                    self.dataOut.data_output[0][r,m] = numpy.nan


                    
    def OutliersFilter(self,modetofilter,svalue,svalue2,method,factor,filter,npoints):   
        '''
        Inputs:
            svalue    -  string to select array velocity
            svalue2    -  string to choose axis filtering
            method    - 0 for SMOOTH or 1 for MEDIAN
            factor    - number used to set threshold 
            filter    - 1 for data filtering using the standard deviation criteria else 0
            npoints    - number of points for mask filter
            
        ''' 
        if modetofilter!=2 and modetofilter!=1 :
            raise ValueError,'Mode to filter should be "1" or "2". {} is not valid, check "Modetofilter" value.'.format(modetofilter)
        
        m = modetofilter-1
                
        print '    Outliers Filter [mode {}]: {} {} / threshold = {}'.format(modetofilter,svalue,svalue,factor)
        
        npoints = 9
        novalid = 0.1
        if svalue == 'zonal':
            value = self.dataOut.data_output[0]
                        
        elif svalue == 'meridional':
            value = self.dataOut.data_output[1]
          
        elif svalue == 'vertical':
            value = self.dataOut.data_output[2]
         
        else:
            print 'value is not defined'
            return
        
        if svalue2 == 'inTime':            
            yaxis = self.dataOut.height
            xaxis = numpy.array([[self.dataOut.time1],[self.dataOut.time1]])
            
        elif svalue2 == 'inHeight':
            yaxis = numpy.array([[self.dataOut.time1],[self.dataOut.time1]])
            xaxis = self.dataOut.height
                    
        else:
            print 'svalue2 is required, either inHeight or inTime'
            return

        output_array = value

        value_temp = value[:,m] 
        error = numpy.zeros(len(self.dataOut.time[m,:])) 
        if svalue2 == 'inHeight':
            value_temp = numpy.transpose(value_temp)
            error = numpy.zeros(len(self.dataOut.height))
        
        htemp = yaxis[m,:]
        std = value_temp
        for h in range(len(htemp)):
            if filter: #standard deviation filtering 
                std[h] = numpy.std(value_temp[h],ddof = npoints)
                value_temp[numpy.where(std[h] > 5),h] = numpy.nan
                error[numpy.where(std[h] > 5)] = error[numpy.where(std[h] > 5)] + 1 


            nvalues_valid = len(numpy.where(numpy.isfinite(value_temp[h]))[0])
            minvalid = novalid*len(xaxis[m,:])
            if minvalid <= npoints:
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
      
      
    def prePlot(self,modeselect=None):

        '''
      Inputs: 
      
          self.dataOut.data_output - Zonal, Meridional and Vertical velocity array  
          self.dataOut.height - height array
          self.dataOut.time  - Time array (seconds)
          self.dataOut.data_SNR - SNR array
  
          '''  

        m = modeselect -1
        
        print '    [Plotting mode {}]'.format(modeselect)
        if not (m ==1 or m==0):
            raise IndexError("'Mode' must be egual to : 1 or 2")
#         
        if self.flagfirstmode==0:
            #copy of the data
            self.data_output_copy = self.dataOut.data_output.copy()
            self.data_height_copy = self.dataOut.height.copy()
            self.data_time_copy = self.dataOut.time.copy()
            self.data_SNR_copy = self.dataOut.data_SNR.copy()    
            self.flagfirstmode = 1
        
        else:
            self.dataOut.data_output = self.data_output_copy
            self.dataOut.height = self.data_height_copy
            self.dataOut.time = self.data_time_copy
            self.dataOut.data_SNR = self.data_SNR_copy
            self.flagfirstmode = 0
        
        
        #select data for mode m
        #self.dataOut.data_output = self.dataOut.data_output[:,:,m]
        self.dataOut.heightList = self.dataOut.height[0,:]

        data_SNR = self.dataOut.data_SNR[:,:,m]
        self.dataOut.data_SNR= transpose(data_SNR)
        
        if m==1 and self.dataOut.counter_records%2==0:
            print '*********'
            print 'MODO 2'
            #print 'Zonal', self.dataOut.data_output[0]
            #print 'Meridional', self.dataOut.data_output[1]
            #print 'Vertical', self.dataOut.data_output[2]
            
            print '*********'
            
            Vx=self.dataOut.data_output[0,:,m]
            Vy=self.dataOut.data_output[1,:,m]
            
            Vmag=numpy.sqrt(Vx**2+Vy**2)
            Vang=numpy.arctan2(Vy,Vx)
            #print 'Vmag', Vmag
            #print 'Vang', Vang
            
            self.dataOut.data_output[0,:,m]=Vmag
            self.dataOut.data_output[1,:,m]=Vang 
            
            prin= self.dataOut.data_output[0,:,m][~numpy.isnan(self.dataOut.data_output[0,:,m])]
            print ' '
            print 'VmagAverage',numpy.mean(prin) 
            print ' '
        self.dataOut.data_output = self.dataOut.data_output[:,:,m]
            

  