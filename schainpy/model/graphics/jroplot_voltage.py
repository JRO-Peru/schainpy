'''
Created on Jul 9, 2014

@author: roj-idl71
'''
import os
import datetime
import numpy

from schainpy.model.graphics.jroplot_base import Plot, plt


class ScopePlot(Plot):

    '''
       Plot for Scope
    '''  

    CODE = 'scope'
    plot_name = 'Scope'
    plot_type = 'scatter'
    
    def setup(self):

        self.xaxis = 'Range (Km)'
        self.ncols = 1
        self.nrows = 1
        self.nplots = 1
        self.ylabel = 'Intensity [dB]'
        self.titles = ['Scope']
        self.colorbar = False
        self.width = 6
        self.height = 4

    def plot_iq(self, x, y, channelIndexList, thisDatetime, wintitle):
        
        yreal = y[channelIndexList,:].real
        yimag = y[channelIndexList,:].imag
        title = wintitle + " Scope: %s" %(thisDatetime.strftime("%d-%b-%Y"))
        self.xlabel = "Range (Km)"
        self.ylabel = "Intensity - IQ"
                
        self.y = yreal
        self.x = x
        self.xmin = min(x)
        self.xmax = max(x)
        

        self.titles[0] = title        

        for i,ax in enumerate(self.axes):
            title = "Channel %d" %(i)
            if ax.firsttime:
                ax.plt_r = ax.plot(x, yreal[i,:], color='b')[0]
                ax.plt_i = ax.plot(x, yimag[i,:], color='r')[0]
            else:
                ax.plt_r.set_data(x, yreal[i,:])
                ax.plt_i.set_data(x, yimag[i,:])
        
    def plot_power(self, x, y, channelIndexList, thisDatetime, wintitle):
        y = y[channelIndexList,:] * numpy.conjugate(y[channelIndexList,:])
        yreal = y.real
        self.y = yreal
        title = wintitle + " Scope: %s" %(thisDatetime.strftime("%d-%b-%Y"))
        self.xlabel = "Range (Km)"
        self.ylabel = "Intensity"
        self.xmin = min(x)
        self.xmax = max(x)
        
        
        self.titles[0] = title

        for i,ax in enumerate(self.axes):
            title = "Channel %d" %(i)
            
            ychannel = yreal[i,:]
            
            if ax.firsttime:    
                ax.plt_r = ax.plot(x, ychannel)[0]
            else:
                #pass
                ax.plt_r.set_data(x, ychannel)
        

    def plot(self):
        
        if self.channels:
            channels = self.channels
        else:
            channels = self.data.channels

        thisDatetime = datetime.datetime.utcfromtimestamp(self.data.times[-1])
        
        scope = self.data['scope']
        
        if self.data.flagDataAsBlock:
            
            for i in range(self.data.nProfiles):

                wintitle1 = " [Profile = %d] " %i

                if self.type == "power":
                    self.plot_power(self.data.heights, 
                                    scope[:,i,:],                                
                                    channels,
                                    thisDatetime, 
                                    wintitle1
                                    )

                if self.type == "iq":
                    self.plot_iq(self.data.heights, 
                                 scope[:,i,:],
                                 channels,
                                 thisDatetime, 
                                 wintitle1 
                                )
        else:
            wintitle = " [Profile = %d] " %self.data.profileIndex
            
            if self.type == "power":
                 self.plot_power(self.data.heights, 
                            scope,
                            channels,
                            thisDatetime,
                            wintitle
                            )
            
            if self.type == "iq":
                self.plot_iq(self.data.heights, 
                            scope,
                            channels,
                            thisDatetime,
                            wintitle
                            )
