'''
Created on Jul 9, 2014

@author: roj-idl71
'''
import os, sys
import datetime
import numpy
import traceback

from time import sleep
from threading import Lock
# from threading import Thread

import schainpy
import schainpy.admin

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

    def __init__(self, plotter_name, plotter_queue=None, **kwargs):

        Operation.__init__(self, **kwargs)

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

#         packDict['data'] = obj2Dict(dataOut)
        packDict['data'] = dataOut

        self.__queue.put(packDict)

# class PlotManager(Thread):
class PlotManager():

    __err = False
    __stop = False
    __realtime = False

    controllerThreadObj = None

    plotterList = ['Scope',
                   'SpectraPlot', 'RTIPlot',
                   'SpectraCutPlot',
                   'CrossSpectraPlot', 'CoherenceMap',
                   'PowerProfilePlot', 'Noise', 'BeaconPhase',
                   'CorrelationPlot',
                   'SpectraHeisScope', 'RTIfromSpectraHeis']

    def __init__(self, plotter_queue):

#         Thread.__init__(self)
#         self.setDaemon(True)

        self.__queue = plotter_queue
        self.__lock = Lock()

        self.plotInstanceDict = {}

        self.__err = False
        self.__stop = False
        self.__realtime = False

    def __handleError(self, name="", send_email=False):

        err = traceback.format_exception(sys.exc_info()[0],
                                         sys.exc_info()[1],
                                         sys.exc_info()[2])

        print "***** Error occurred in PlotManager *****"
        print "***** [%s]: %s" %(name, err[-1])

        message = "\nError ocurred in %s:\n" %name
        message += "".join(err)

        sys.stderr.write(message)

        if not send_email:
            return

        import socket

        subject =  "SChain v%s: Error running %s\n" %(schainpy.__version__, name)

        subtitle = "%s:\n" %(name)
        subtitle += "Hostname: %s\n" %socket.gethostbyname(socket.gethostname())
        subtitle += "Working directory: %s\n" %os.path.abspath("./")
#         subtitle += "Configuration file: %s\n" %self.filename
        subtitle += "Time: %s\n" %str(datetime.datetime.now())

        adminObj = schainpy.admin.SchainNotify()
        adminObj.sendAlert(message=message,
                           subject=subject,
                           subtitle=subtitle)

    def run(self):

        if self.__queue.empty():
            return

        if self.__err:
            serial_data = self.__queue.get()
            self.__queue.task_done()
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
#             dataDict = serial_data['data']
#
#             dataPlot = dict2Obj(dataDict)

            dataPlot = serial_data['data']

            if plot_id not in self.plotInstanceDict.keys():
                className = eval(plot_name)
                self.plotInstanceDict[plot_id] = className(**kwargs)

            plotter = self.plotInstanceDict[plot_id]
            try:
                plotter.run(dataPlot, plot_id, **kwargs)
            except:
                self.__err = True
                self.__handleError(plot_name, send_email=True)
                break

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

    def isErrorDetected(self):

        self.__lock.acquire()

        err = self.__err

        self.__lock.release()

        return err
