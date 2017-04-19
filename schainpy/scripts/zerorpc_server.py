#!/usr/bin/env python
'''
Created on Jul 11, 2014

@author: roj-idl71
'''
# import sys
import datetime
import zerorpc

import os, sys

path = os.path.dirname(os.getcwd())
path = os.path.join(path, 'source')
sys.path.insert(0, path)

# from gevent import sleep

from schainpy.model.io.jroIO_usrp_api import USRPReaderAPI
# from schainpy.serializer.DataTranslate import serial2Obj

if __name__ == '__main__':
    
    replayerObj = USRPReaderAPI(serializer='msgpack')
    
    replayerObj.setup(path='../data/haystack/',
                    startDate=datetime.date(2000,1,1),
                    endDate=datetime.date(2016,1,1),
                    startTime=datetime.time(0,0,0),
                    endTime=datetime.time(23,59,59),
                    online=0,
                    nSamples=50,
                    buffer_size = 8,
                    channelList = [0])
    
    replayerObj.start()
    
    print "\nInitializing 'zerorpc' server"
    s = zerorpc.Server(replayerObj)
    s.bind("tcp://0.0.0.0:4242")
    s.run()
    
    print "End"