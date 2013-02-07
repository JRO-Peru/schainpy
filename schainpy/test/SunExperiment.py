import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "EWDrifts Experiment Test"
filename = "ewdrifts.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)

readUnitConfObj = controllerObj.addReadUnit(datatype='Voltage',
                                            path='/Volumes/data_e/PaseDelSol/Raw/100KHZ',
                                            startDate='2013/02/06',
                                            endDate='2013/12/31',
                                            startTime='17:30:00',
                                            endTime='17:40:59',
                                            online=0,
                                            walk=1)

procUnitConfObj0 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())

procUnitConfObj1 = controllerObj.addProcUnit(datatype='SpectraHeis', inputId=procUnitConfObj0.getId())

opObj11 = procUnitConfObj1.addOperation(name='IncohInt4SpectraHeis', optype='other')
opObj11.addParameter(name='timeInterval', value='5', format='float')

opObj11 = procUnitConfObj1.addOperation(name='SpectraHeisScope', optype='other')
opObj11.addParameter(name='idfigure', value='10', format='int')
opObj11.addParameter(name='wintitle', value='SpectraHeisPlot', format='str')
opObj11.addParameter(name='ymin', value='125', format='int')
opObj11.addParameter(name='ymax', value='140', format='int')
#opObj11.addParameter(name='channelList', value='0,1,2', format='intlist')
#opObj11.addParameter(name='showprofile', value='1', format='int') 
opObj11.addParameter(name='save', value='1', format='bool')
opObj11.addParameter(name='figpath', value='/Users/dsuarez/Pictures/sun_pics', format='str')


#opObj11 = procUnitConfObj1.addOperation(name='RTIfromSpectraHeis', optype='other')
#opObj11.addParameter(name='idfigure', value='6', format='int')
#opObj11.addParameter(name='wintitle', value='RTIPLot', format='str')
##opObj11.addParameter(name='zmin', value='10', format='int')
##opObj11.addParameter(name='zmax', value='40', format='int')
#opObj11.addParameter(name='ymin', value='60', format='int')
#opObj11.addParameter(name='ymax', value='130', format='int')
##opObj11.addParameter(name='channelList', value='0,1,2,3', format='intlist') 
#opObj11.addParameter(name='timerange', value='600', format='int') 
##opObj11.addParameter(name='showprofile', value='0', format='int')
#opObj11.addParameter(name='save', value='1', format='bool')
#opObj11.addParameter(name='figpath', value='/Users/dsuarez/Pictures/sun_pics', format='str')



print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()
  
  