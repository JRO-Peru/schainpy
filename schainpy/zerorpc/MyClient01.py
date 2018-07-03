'''
Created on Jul 11, 2014

@author: roj-idl71
'''
import time
from gevent import sleep

import zerorpc
from schainpy.model import *
from schainpy.serializer.DataTranslate import serial2Obj, serial2Dict
# import schainpy.model.io.jroIO_usrp

def createObjVolt():
    '''
    This function creates a processing object "VoltProc" with some operations.
    such as: "CohInt", "Scope", etc
    These class are found inside schainpy.model.proc and schainpy.model.graphics
    '''
    procObj = VoltageProc()
    
    opObj = CohInt()
    procObj.addOperation(opObj, 1)
    
    opObj = Scope()
    procObj.addOperation(opObj, 2)
    
    return procObj

def createObjSpec():
    '''
    This function creates a processing object "SpecProc" with some operation objects
    such as: "IncohInt", "SpectraPlot", "RTIPlot", etc
    These class are found inside schainpy.model.proc and schainpy.model.graphics
    '''
    
    procObj = SpectraProc()
    
    opObj = IncohInt()
    procObj.addOperation(opObj, objId = 1)
    
    opObj = SpectraPlot()
    procObj.addOperation(opObj, objId = 2)
    
    opObj = RTIPlot()
    procObj.addOperation(opObj, objId = 3)
    
    opObj = SpectraPlot()
    procObj.addOperation(opObj, objId = 4)
    
    opObj = RTIPlot()
    procObj.addOperation(opObj, objId = 5)
    
    return procObj

def processingSpec(procObj, dataInObj):
    
    procObj.setInput(dataInObj)
    procObj.run(nFFTPoints = 16)
    
    procObj.call(opType = "external",
                 opId = 1,
                 n=1)
    
    procObj.call(opType = "external",
                 opId = 2,
                 id=191,
                 zmin=-100,
                 zmax=-40)

    procObj.call(opType = "external",
                 opId = 3,
                 id=192,
                 zmin=-100,
                 zmax=-40,
                 timerange=10*60)
    
#     procObj.call(opType = "self",
#                  opName = "selectChannels",
#                  channelList = [0,1])
#     
#     procObj.call(opType = "self",
#                  opName = "selectHeights",
#                  minHei = 300,
#                  maxHei = 400)
#     
#     procObj.call(opType = "external",
#                  opId = 4,
#                  id=193,
#                  zmin=-100,
#                  zmax=-40)
# 
#     procObj.call(opType = "external",
#                  opId = 5,
#                  id=194,
#                  zmin=-100,
#                  zmax=-40,
#                  timerange=10*60)

def printSpeed(deltaTime, mySerial):
    
    ####################
    size = len(mySerial)/1024.
    vel = 1.0*size / deltaTime
    
    print("Index [", replayerObj.getProfileIndex(), "]: ", end=' ')
    print("Total time %5.2f ms, Data size %5.2f KB, Speed %5.2f MB/s" %(deltaTime, size, vel))
    ####################
        
if __name__ == '__main__':
    
    procObj = createObjSpec()
    
    replayerObj = zerorpc.Client()
    replayerObj.connect("tcp://127.0.0.1:4242")
    
    serializer = replayerObj.getSerializer()
    
    ini = time.time()
    mySerialMetadata = replayerObj.getSerialMetaData()
    deltaTime = (time.time() - ini)*1024
    
    printSpeed(deltaTime, mySerialMetadata)
    
    myMetaDict = serial2Dict(mySerialMetadata,
                             serializer = serializer)
#     print myMetaDict
    while True:
        ini = time.time()
        mySerialData = replayerObj.getSerialData()
        deltaTime = (time.time() - ini)*1024
        
        if not mySerialData:
            print("No more data")
            break
        
#         myDataDict = SERIALIZER.loads(mySerialData)
#         print myDataDict
#         continue
    
        printSpeed(deltaTime, mySerialData)
        
        dataInObj = serial2Obj(mySerialData,
                               metadataDict=myMetaDict,
                               serializer = serializer)
        processingSpec(procObj, dataInObj)
        sleep(1e-1)