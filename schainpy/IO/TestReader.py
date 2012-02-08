'''
Created on 23/01/2012

@author: danielangelsuarezmunoz
'''

import Voltage
import datetime
import time, datetime

objReader = Voltage.VoltageReader()


path = '/home/roj-idl71/Data/RAWDATA/DP_Faraday/'
#path = '/remote/puma/2011_03/DP_Faraday'


startDateTime = datetime.datetime(2011,3,11,16,40,0)
endDateTime = datetime.datetime(2011,3,11,16,59,0)

t0 = time.time()
objReader.setup(path, startDateTime, endDateTime)
print time.time() - t0


while(not(objReader.noMoreFiles)):
    
    objReader.getData()
    if objReader.flagIsNewBlock:
        print "Block No %04d, Time: %s" %(objReader.nReadBlocks, datetime.datetime.fromtimestamp(objReader.m_BasicHeader.utc))
#        print objReader.m_BasicHeader.dataBlock
    #print objReader.objStructShortHeader.dataBlock
        
    
    