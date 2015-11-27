import threading

from PyQt4 import QtCore
from PyQt4.QtCore import SIGNAL

from schainpy.controller import Project

class ControllerThread(threading.Thread, Project):
    
    def __init__(self, filename):
        
        threading.Thread.__init__(self)
        Project.__init__(self)
        
        self.setDaemon(True)
        
        self.filename = filename
        self.control = {'stop':False, 'pause':False}
    
    def __del__(self):
        
        self.control['stop'] = True
#         self.pause(1)
#         self.wait()
    
    def stop(self):
        self.control['stop'] = True
        
    def pause(self):
        self.control['pause'] = not(self.control['pause'])
        
        return self.control['pause']
    
    def __run(self):
        
        print
        print "*"*40
        print "   Starting SIGNAL CHAIN PROCESSING  "
        print "*"*40
        print
        
        keyList = self.procUnitConfObjDict.keys()
        keyList.sort()
            
        while(True):
            
            finalSts = False
            #executed proc units
            procUnitExecutedList = []
            
            for procKey in keyList:
#                 print "Running the '%s' process with %s" %(procUnitConfObj.name, procUnitConfObj.id)
                
                procUnitConfObj = self.procUnitConfObjDict[procKey]
                
                inputId = procUnitConfObj.getInputId()
                
                sts = procUnitConfObj.run()
                finalSts = finalSts or sts
                
                procUnitExecutedList.append(procUnitConfObj.id)
            
            #If every process unit finished so end process
            if not(finalSts):
                print "Every process unit have finished"
                break

            if self.control['pause']:
                print "Process suspended"
                
                while True:    
                    sleep(0.1)
                    
                    if not self.control['pause']:
                        break
                    
                    if self.control['stop']:
                        break
                print "Process reinitialized"
            
            if self.control['stop']:
#                 print "Process stopped"
                break
                
        #Closing every process
        for procKey in keyList:
            procUnitConfObj = self.procUnitConfObjDict[procKey]
            procUnitConfObj.close()
            
        print "Process finished"
        
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
        
class ControllerQThread(QtCore.QThread, Project):
    
    def __init__(self, filename):
        
        QtCore.QThread.__init__(self)
        Project.__init__(self)
        
        self.filename = filename
        self.control = {'stop':False, 'pause':False}
    
    def __del__(self):
        
        self.control['stop'] = True
        self.wait()
        
    def stop(self):
        self.control['stop'] = True
        
    def pause(self):
        self.control['pause'] = not(self.control['pause'])

    def run(self):
        self.control['stop'] = False
        self.control['pause'] = False
        
        self.readXml(self.filename)
        self.createObjects()
        self.connectObjects()
        self.emit( SIGNAL( "jobStarted( PyQt_PyObject )" ), 1)
        Project.run(self)
        self.emit( SIGNAL( "jobFinished( PyQt_PyObject )" ), 1)