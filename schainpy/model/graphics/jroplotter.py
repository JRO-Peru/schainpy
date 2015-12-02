'''
Created on Jul 9, 2014

@author: roj-idl71
'''
import os
import datetime
import numpy

from figure import Figure

class Plotter(Figure):
    
    isConfig = None
    name = None
    plotterQueue = None
    
    def __init__(self, plotter_name, plotter_queue=None):
        
        self.isConfig = False
        self.name = plotter_name
        self.plotterQueue = plotter_queue
    
    def getSubplots(self):
        
        nrow = self.nplots
        ncol = 1
        return nrow, ncol
    
    def setup(self, **kwargs):
        
#         self.nplots = nplots
#          
#         self.createFigure(id=id, 
#                           wintitle=wintitle, 
#                           show=show)
#         
#         nrow,ncol = self.getSubplots()
#         colspan = 3
#         rowspan = 1
#         
#         for i in range(nplots):
#             self.addAxes(nrow, ncol, i, 0, colspan, rowspan)
            
        
        
        print "Initializing ..."
    
    
    def run(self, dataOut, **kwargs):
        
        """
        
        Input:
            dataOut         :
            id              :
            wintitle        :
            channelList     :
            show            :
        """
        
        if not self.isConfig:
            self.setup(**kwargs)
            self.isConfig=True
            
        print "Putting data on %s queue:" %self.name
        print kwargs
        
