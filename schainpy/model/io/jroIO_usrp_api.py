'''
Created on Jul 15, 2014

@author: roj-idl71
'''
import time
import threading
import pickle

# try:
#     from gevent import sleep
# except:
from time import sleep

SERIALIZER = cPickle

# from schainpy.serializer import DynamicSerializer
from schainpy.model.io.jroIO_usrp import USRPReader
from schainpy.model.serializer.data import obj2Serial

class USRPReaderAPI(USRPReader, threading.Thread):
    
#     __isBufferEmpty = True
    
    __DATAKEYLIST = ['data','utctime','flagNoData']
    
    def __init__(self, serializer='msgpack'):
        
        threading.Thread.__init__(self)
        USRPReader.__init__(self)
        
#         self.__serializerObj = DynamicSerializer.DynamicSerializer('msgpack')
        self.__mySerial = None
        self.__isBufferEmpty = True
        
        self.setSerializer(serializer)
    
    def setSerializer(self, serializer):
        
        self.__serializer = serializer
    
    def getSerializer(self):
        
        return self.__serializer
        
    def getProfileIndex(self):
        
        return self.profileIndex
    
    def getSerialMetaData(self):
        
        if self.__isBufferEmpty:
            ini = time.time()
            
            while True:
                
                if not self.__isBufferEmpty:
                    break
                
                if time.time() - ini > 20:
                    break
                
                sleep(1e-12)
                    
            
#             if not self.getData():
#                 self.__isBufferEmpty = False
#                 return None
    
        if self.dataOut.flagNoData:
            return None
        
        myMetadataSerial = obj2Serial(self.dataOut,
                                      serializer = self.__serializer)
        
        return myMetadataSerial
    
    def getSerialData(self):
        
        if self.__isBufferEmpty:
            ini = time.time()
            
            while True:
                
                if not self.__isBufferEmpty:
                    break
                
                if time.time() - ini > 20:
                    break
                
                sleep(1e-12)
                    
            
#             if not self.getData():
#                 self.__isBufferEmpty = False
#                 return None
    
        if self.dataOut.flagNoData:
            return None
        
        self.__isBufferEmpty = True
        
        return self.__mySerial
    
    def run(self):
         
        '''
        This method will be called once when start() is called
        '''
         
        if not self.isConfig:
            raise RuntimeError('setup() method has to be called before start()')
        
        print("Running ...")
        
        while True:
             
            if not self.__isBufferEmpty:
                sleep(1e-12)
                continue
             
            if not self.getData():
                break
            
            print(".", end=' ')
            
            self.__mySerial = obj2Serial(self.dataOut,
                                         keyList = self.__DATAKEYLIST,
                                         serializer = self.__serializer)
            self.__isBufferEmpty = False
             
#             print self.profileIndex
#             print 'wait 1 second'
            
#             sleep(0.1)

        print("Closing thread")
        
        return