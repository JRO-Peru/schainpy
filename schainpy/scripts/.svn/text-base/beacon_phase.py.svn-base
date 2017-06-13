import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "Meteor Experiment Test"
filename = "jasmet20140415.xml"

controllerObj = Project()
controllerObj.setup(id = '191', name='meteor_test01', description=desc)

path = '/home/dsuarez/.gvfs/data on 10.10.20.13/Jasmet50/d2014104'


readUnitConfObj = controllerObj.addReadUnit(datatype='Voltage',
                                            path=path,
                                            startDate='2013/08/21',
                                            endDate='2013/08/21',
                                            startTime='00:00:00',
                                            endTime='23:59:59',
                                            online=0,
                                            walk=0)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')

procUnitConfObj0 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())

procUnitConfObjBeacon = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObj0.getId())
procUnitConfObjBeacon.addParameter(name='nProfiles', value='200', format='int')
procUnitConfObjBeacon.addParameter(name='nFFTPoints', value='200', format='int')
procUnitConfObjBeacon.addParameter(name='pairsList', value='(0,5),(1,5),(2,5),(3,5),(4,5)', format='pairsList')

opObj11 = procUnitConfObjBeacon.addOperation(name='IncohInt', optype='other')
opObj11.addParameter(name='n', value='4', format='int')

opObj11 = procUnitConfObjBeacon.addOperation(name='getBeaconSignal')

opObj11 = procUnitConfObjBeacon.addOperation(name='BeaconPhase', optype='other')
opObj11.addParameter(name='id', value='301', format='int')
opObj11.addParameter(name='wintitle', value='Beacon Phase', format='str')
opObj11.addParameter(name='timerange', value='300', format='int')
opObj11.addParameter(name='ymin', value='-180', format='float')
opObj11.addParameter(name='ymax', value='180', format='float')
opObj11.addParameter(name='save', value='1', format='int')
opObj11.addParameter(name='figpath', value='/home/dsuarez/Pictures/beacon_abril', format='str')

print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()