'''
Created on Jul 9, 2014

@author: roj-idl71
'''
import os
import datetime
import numpy

from time import sleep
from Queue import Queue
from threading import Thread

from schainpy.model.proc.jroproc_base import Operation
from schainpy.model.serializer.data import obj2Dict, dict2Obj
from jroplot_correlation import *
from jroplot_heispectra import *
from jroplot_parameters import *
from jroplot_spectra import *
from jroplot_voltage import *


class Plotter(Operation):
    
    isConfig = None
    name = None
    __queue = None
    
    def __init__(self, plotter_name, plotter_queue=None):
        
        Operation.__init__(self)
        
        self.isConfig = False
        self.name = plotter_name
        self.__queue = plotter_queue
    
    def getSubplots(self):
        
        nrow = self.nplots
        ncol = 1
        return nrow, ncol
    
    def setup(self, **kwargs):
        
        print "Initializing ..."
    
    
    def run(self, dataOut, id=None, **kwargs):
        
        """
        
        Input:
            dataOut         :
            id              :
        """
        
        packDict = {}
        
        packDict['id'] =  id
        packDict['name'] = self.name
        packDict['kwargs'] = kwargs
        
        packDict['data'] = obj2Dict(dataOut)
        
        self.__queue.put(packDict)

class PlotterManager(Thread):
    
    __stop = False
    
    def __init__(self, plotter_queue):
        
        Thread.__init__(self)
        
        self.setDaemon(True)
        
        self.__queue = plotter_queue
        
        self.plotInstanceDict = {}
        self.__stop = False
        
    def run(self):
        
        while True:
            
            if self.__stop:
                break
            
            if self.__queue.empty():
                sleep(0.1)
                continue
            
            serial_data = self.__queue.get(True)
            
            plot_id = serial_data['id']
            plot_name = serial_data['name']
            kwargs = serial_data['kwargs']
            dataDict = serial_data['data']
            
            dataPlot = dict2Obj(dataDict)
            
            if plot_id not in self.plotInstanceDict.keys():
                className = eval(plot_name)
                self.plotInstanceDict[plot_id] = className()
                       
            plotter = self.plotInstanceDict[plot_id]
            plotter.run(dataPlot, plot_id, **kwargs)
            
    def stop(self):
        
        self.__stop = True