import threading

from schainpy.controller import Project

class ControllerThread(threading.Thread, Project):
    
    def __init__(self, filename=None, plotter_queue=None):
        
        threading.Thread.__init__(self)
        Project.__init__(self, filename, plotter_queue)
        
        self.setDaemon(True)
        
        self.lock = threading.Lock()
        self.control = {'stop':False, 'pause':False}
    
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
        
        self.readXml(self.filename)
        self.createObjects()
        self.connectObjects()
        Project.run(self)
        
    def isRunning(self):
        
        return self.is_alive()
    
    def isFinished(self):
        
        return not self.is_alive()

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