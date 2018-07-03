'''
Created on Jul 11, 2014

@author: roj-idl71
'''
# import sys
import datetime
import zerorpc

from schainpy.model.io.jrodataIO import USRPReaderAPI
# from schainpy.serializer.DataTranslate import serial2Obj

if __name__ == '__main__':
    
    replayerObj = USRPReaderAPI(serializer='msgpack')
    
    replayerObj.setup(path='/Volumes/DATA/haystack/passive_radar/',
                    startDate=datetime.date(2000,1,1),
                    endDate=datetime.date(2015,1,1),
                    startTime=datetime.time(0,0,0),
                    endTime=datetime.time(23,59,59),
                    online=1,
                    nSamples=500,
                    channelList = [0,1,2,3,4,5,6,7])
    
    replayerObj.start()
    
    print("Initializing 'zerorpc' server")
    s = zerorpc.Server(replayerObj)
    s.bind("tcp://0.0.0.0:4242")
    s.run()
    
    print("End")