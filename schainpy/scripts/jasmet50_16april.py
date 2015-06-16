"""
Se debe verficar que el disco de datos se encuentra montado en el sistema
"""
import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "Meteor Experiment Test"
filename = "meteor20130812.xml"

controllerObj = Project()
controllerObj.setup(id = '191', name='meteor_test01', description=desc)

path = '/home/dsuarez/.gvfs/data on 10.10.20.13/Jasmet50'


readUnitConfObj = controllerObj.addReadUnit(datatype='Voltage',
                                            path=path,
                                            startDate='2014/04/16',
                                            endDate='2014/04/16',
                                            startTime='00:00:00',
                                            endTime='23:59:59',
                                            online=0,
                                            walk=1)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')

procUnitConfObj0 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())

opObj11 = procUnitConfObj0.addOperation(name='setRadarFrequency')
opObj11.addParameter(name='frequency', value='30.15e6', format='float')

opObj11 = procUnitConfObj0.addOperation(name='Decoder', optype='other')


opObj11 = procUnitConfObj0.addOperation(name='CohInt', optype='other')
opObj11.addParameter(name='n', value='2', format='int')

opObj11 = procUnitConfObj0.addOperation(name='VoltageWriter', optype='other')
opObj11.addParameter(name='path', value='/media/datos/jasmet50_abril')
opObj11.addParameter(name='blocksPerFile', value='100', format='int')
opObj11.addParameter(name='profilesPerBlock', value='200', format='int')


"""
########################################### BEACON ########################################## 
"""

procUnitConfObjBeacon = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObj0.getId())
procUnitConfObjBeacon.addParameter(name='nProfiles', value='200', format='int')
procUnitConfObjBeacon.addParameter(name='nFFTPoints', value='200', format='int')
procUnitConfObjBeacon.addParameter(name='pairsList', value='(2,0),(2,1),(2,3),(2,4)', format='pairsList')

opObj11 = procUnitConfObjBeacon.addOperation(name='IncohInt', optype='other')
opObj11.addParameter(name='n', value='4', format='int')

opObj11 = procUnitConfObjBeacon.addOperation(name='getBeaconSignal')

opObj11 = procUnitConfObjBeacon.addOperation(name='BeaconPhase', optype='other')
opObj11.addParameter(name='id', value='301', format='int')
opObj11.addParameter(name='wintitle', value='Beacon Phase', format='str')
opObj11.addParameter(name='xmin', value='0', format='float')
opObj11.addParameter(name='xmax', value='24', format='float')
opObj11.addParameter(name='ymin', value='-180', format='float')
opObj11.addParameter(name='ymax', value='180', format='float')
opObj11.addParameter(name='figpath', value='/media/datos/jasmet50_phase', format='str')


print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()
