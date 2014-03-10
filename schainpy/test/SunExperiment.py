import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "Sun Experiment Test"
filename = "sunexp.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)
#/Users/dsuarez/Documents/RadarData/SunExperiment
#/Volumes/data_e/PaseDelSol/Raw/100KHZ

path = '/Volumes/New Volume/data/PaseDelSol/Raw/1MHz/d2014044'
path = '/Users/dsuarez/Documents/pasedelsol/100KHz'
readUnitConfObj = controllerObj.addReadUnit(datatype='Voltage',
                                            path=path,
                                            startDate='2014/02/01',
                                            endDate='2014/02/27',
                                            startTime='00:00:00',
                                            endTime='23:59:59',
                                            online=0,
                                            delay=3,
                                            walk=0)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')

procUnitConfObj0 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())

procUnitConfObj1 = controllerObj.addProcUnit(datatype='SpectraHeis', inputId=procUnitConfObj0.getId())

opObj11 = procUnitConfObj1.addOperation(name='IncohInt4SpectraHeis', optype='other')
opObj11.addParameter(name='timeInterval', value='5', format='float')

opObj11 = procUnitConfObj1.addOperation(name='SpectraHeisScope', optype='other')
opObj11.addParameter(name='id', value='10', format='int')
opObj11.addParameter(name='wintitle', value='SpectraHeisPlot', format='str')
#opObj11.addParameter(name='ymin', value='125', format='int')
#opObj11.addParameter(name='ymax', value='140', format='int')
#opObj11.addParameter(name='channelList', value='0,1,2', format='intlist')
#opObj11.addParameter(name='showprofile', value='1', format='int') 
#opObj11.addParameter(name='save', value='1', format='bool')
#opObj11.addParameter(name='figfile', value='spc-noise.png', format='str')
#opObj11.addParameter(name='figpath', value='/Users/dsuarez/Pictures/sun_pics', format='str')
#opObj11.addParameter(name='ftp', value='1', format='int')
#opObj11.addParameter(name='ftpratio', value='10', format='int')

opObj11 = procUnitConfObj1.addOperation(name='RTIfromSpectraHeis', optype='other')
opObj11.addParameter(name='id', value='6', format='int')
opObj11.addParameter(name='wintitle', value='RTIPLot', format='str')
# opObj11.addParameter(name='xmin', value='11.5', format='float')
# opObj11.addParameter(name='xmax', value='12.5', format='float')
# opObj11.addParameter(name='ymin', value='60', format='int')
# opObj11.addParameter(name='ymax', value='85', format='int')
# opObj11.addParameter(name='channelList', value='0,1,2,3', format='intlist') 
#opObj11.addParameter(name='timerange', value='600', format='int') 
#opObj11.addParameter(name='showprofile', value='0', format='int')
#opObj11.addParameter(name='save', value='1', format='bool')
#opObj11.addParameter(name='figfile', value='rti-noise.png', format='str')
#opObj11.addParameter(name='figpath', value='/Users/dsuarez/Pictures/sun_pics', format='str')
#opObj11.addParameter(name='ftp', value='1', format='int')
#opObj11.addParameter(name='ftpratio', value='10', format='int')
# opObj11.addParameter(name='useLocalTime', value='1', format='bool')
# opObj11.addParameter(name='timezone', value='300', format='int')

#opObj11 = procUnitConfObj1.addOperation(name='SpectraHeisWriter', optype='other')
#opObj11.addParameter(name='wrpath', value='/Users/dsuarez/Remote', format='str')
##opObj11.addParameter(name='blocksPerFile', value='200', format='int')

opObj11 = procUnitConfObj1.addOperation(name='FitsWriter', optype='other')
opObj11.addParameter(name='path', value='/Users/dsuarez/Documents/fits_rev', format='str')
opObj11.addParameter(name='dataBlocksPerFile', value='10', format='int')
opObj11.addParameter(name='metadatafile', value='/Users/dsuarez/Downloads/metadata_fits_201402.xml', format='str')

print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()
  
  