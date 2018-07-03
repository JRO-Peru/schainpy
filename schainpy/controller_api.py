import threading
from queue import Queue

from schainpy.controller import Project
from schainpy.model.graphics.jroplotter import PlotManager

class ControllerThread(threading.Thread, Project):

    def __init__(self, plotter_queue=None):

        threading.Thread.__init__(self)
        Project.__init__(self, plotter_queue)

        self.setDaemon(True)

        self.lock = threading.Lock()
        self.control = { 'stop':False, 'pause':False }
    
    def __del__(self):

        self.control['stop'] = True

    def stop(self):

        self.lock.acquire()

        self.control['stop'] = True

        self.lock.release()

    def pause(self):

        self.lock.acquire()

        self.control['pause'] = not(self.control['pause'])
        paused = self.control['pause']

        self.lock.release()

        return paused

    def isPaused(self):

        self.lock.acquire()
        paused = self.control['pause']
        self.lock.release()

        return paused

    def isStopped(self):

        self.lock.acquire()
        stopped = self.control['stop']
        self.lock.release()

        return stopped

    def run(self):
        self.control['stop'] = False
        self.control['pause'] = False

        self.writeXml()

        self.createObjects()
        self.connectObjects()
        Project.run(self)

    def isRunning(self):

        return self.is_alive()

    def isFinished(self):

        return not self.is_alive()

    def setPlotters(self):

        plotterList = PlotManager.plotterList

        for thisPUConfObj in list(self.procUnitConfObjDict.values()):

            inputId = thisPUConfObj.getInputId()

            if int(inputId) == 0:
                continue

            for thisOpObj in thisPUConfObj.getOperationObjList():

                if thisOpObj.type == "self":
                    continue

                if thisOpObj.name in plotterList:
                    thisOpObj.type = "other"

    def setPlotterQueue(self, plotter_queue):

        self.plotterQueue = plotter_queue

    def getPlotterQueue(self):

        return self.plotterQueue

    def useExternalPlotter(self):

        self.plotterQueue = Queue(10)
        self.setPlotters()

        plotManagerObj = PlotManager(self.plotterQueue)
        plotManagerObj.setController(self)

        return plotManagerObj

# from PyQt4 import QtCore
# from PyQt4.QtCore import SIGNAL
#
# class ControllerQThread(QtCore.QThread, Project):
#
#     def __init__(self, filename):
#
#         QtCore.QThread.__init__(self)
#         Project.__init__(self)
#
#         self.filename = filename
#
#         self.lock = threading.Lock()
#         self.control = {'stop':False, 'pause':False}
#
#     def __del__(self):
#
#         self.control['stop'] = True
#         self.wait()
#
#     def stop(self):
#
#         self.lock.acquire()
#
#         self.control['stop'] = True
#
#         self.lock.release()
#
#     def pause(self):
#
#         self.lock.acquire()
#
#         self.control['pause'] = not(self.control['pause'])
#         paused = self.control['pause']
#
#         self.lock.release()
#
#         return paused
#
#     def isPaused(self):
#
#         self.lock.acquire()
#         paused = self.control['pause']
#         self.lock.release()
#
#         return paused
#
#     def isStopped(self):
#
#         self.lock.acquire()
#         stopped = self.control['stop']
#         self.lock.release()
#
#         return stopped
#
#     def run(self):
#
#         self.control['stop'] = False
#         self.control['pause'] = False
#
#         self.readXml(self.filename)
#         self.createObjects()
#         self.connectObjects()
#         self.emit( SIGNAL( "jobStarted( PyQt_PyObject )" ), 1)
#         Project.run(self)
#         self.emit( SIGNAL( "jobFinished( PyQt_PyObject )" ), 1)
#