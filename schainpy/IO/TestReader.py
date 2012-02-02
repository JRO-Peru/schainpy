'''
Created on 23/01/2012

@author: danielangelsuarezmunoz
'''

import VoltageReader
import datetime
import time

objReader = VoltageReader.VoltageReader()

path = '/Users/danielangelsuarezmunoz/Documents/Projects'
startDateTime = datetime.datetime(2007,1,1,16,0,0)
endDateTime = datetime.datetime(2007,12,1,17,1,0)
set = None
expLabel = ''
ext = '*.r'

t0 = time.time()
objReader.setup(path, startDateTime, endDateTime, set, expLabel, ext)
print time.time() - t0


while(not(objReader.noMoreFiles)):
    
    objReader.getData()
    #print objReader.objStructShortHeader.dataBlock
    #print time.localtime(objReader.objStructShortHeader.universalTime)
    
    