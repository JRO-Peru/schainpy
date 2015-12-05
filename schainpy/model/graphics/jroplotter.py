'''
Created on Jul 9, 2014

@author: roj-idl71
'''
import os
import datetime
import numpy

from time import sleep
from Queue import Queue
from threading import Lock
# from threading import Thread

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

# class PlotManager(Thread):
class PlotManager():
    __stop = False
    controllerThreadObj = None
    
    def __init__(self, plotter_queue):
        
#         Thread.__init__(self)
#         self.setDaemon(True)
        
        self.__queue = plotter_queue
        self.__lock = Lock()
        
        self.plotInstanceDict = {}
        self.__stop = False
        
    def run(self):
        
        if self.__queue.empty():
            return
        
        self.__lock.acquire()
        
#         if self.__queue.full():
#             for i in range(int(self.__queue.qsize()/2)):
#                 serial_data = self.__queue.get()
#                 self.__queue.task_done()
            
        n = int(self.__queue.qsize()/3 + 1)
        
        for i in range(n):
            
            if self.__queue.empty():
                break
        
            serial_data = self.__queue.get()
            self.__queue.task_done()
            
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
            
        self.__lock.release()
    
    def isEmpty(self):
        
        return self.__queue.empty()
        
    def stop(self):
        
        self.__lock.acquire()
        
        self.__stop = True
        
        self.__lock.release()
        
    def close(self):
        
        self.__lock.acquire()
        
        for plot_id in self.plotInstanceDict.keys():
            plotter = self.plotInstanceDict[plot_id]
            plotter.close()
        
        self.__lock.release()
    
    def setController(self, controllerThreadObj):
        
        self.controllerThreadObj = controllerThreadObj
        
    def start(self):
        
        if not self.controllerThreadObj.isRunning():
            raise RuntimeError, "controllerThreadObj has not been initialized. Use controllerThreadObj.start() before call this method"
        
        self.join()
        
    def join(self):
        
        #Execute plotter while controller is running
        while self.controllerThreadObj.isRunning():
            self.run()
        
        self.controllerThreadObj.stop()
        
        #Wait until plotter queue is empty
        while not self.isEmpty():
            self.run()
        
        self.close()