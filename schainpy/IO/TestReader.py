'''
Created on 23/01/2012

@author: danielangelsuarezmunoz
'''

import Voltage
import datetime
import time

objReader = Voltage.VoltageReader()


path = '/home/roj-idl71/Data/RAWDATA/DP_Faraday/'
#path = '/remote/puma/2011_03/DP_Faraday'


startDateTime = datetime.datetime(2011,3,11,16,0,0)
endDateTime = datetime.datetime(2011,3,12,20,1,0)

t0 = time.time()
objReader.setup(path, startDateTime, endDateTime)
print time.time() - t0


while(not(objReader.noMoreFiles)):
    
    objReader.getData()
#    if objReader.flagIsNewFile:
#        print objReader.m_BasicHeader.dataBlock
    #print objReader.objStructShortHeader.dataBlock
    #print time.localtime(objReader.m_BasicHeader.utc)
    
    