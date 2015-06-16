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
pathFigure = '/home/jasmet/jasmet30_phase'
path = '/home/soporte/Data/JASMET/JASMET_30/2014106'
pathFigure = '/home/soporte/workspace/Graficos/JASMET/prueba1'


readUnitConfObj = controllerObj.addReadUnit(datatype='VoltageReader',
                                            path=path,
                                            startDate='2014/04/15',
                                            endDate='2014/04/15',
                                            startTime='20:00:00',
                                            endTime='23:59:59',
                                            online=0,
                                            walk=0)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')

procUnitConfObj0 = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())


# opObj11 = procUnitConfObj0.addOperation(name='Decoder', optype='other')
# 
# 
# opObj11 = procUnitConfObj0.addOperation(name='CohInt', optype='other')
# opObj11.addParameter(name='n', value='2', format='int')

# opObj11 = procUnitConfObj0.addOperation(name='VoltageWriter', optype='other')
# opObj11.addParameter(name='path', value='/home/jasmet/jasmet30_abril')
# opObj11.addParameter(name='blocksPerFile', value='100', format='int')
# opObj11.addParameter(name='profilesPerBlock', value='200', format='int')


"""
########################################### BEACON ########################################## 
"""

procUnitConfObjBeacon = controllerObj.addProcUnit(datatype='SpectraProc', inputId=procUnitConfObj0.getId())
procUnitConfObjBeacon.addParameter(name='nProfiles', value='200', format='int')
procUnitConfObjBeacon.addParameter(name='nFFTPoints', value='200', format='int')
procUnitConfObjBeacon.addParameter(name='pairsList', value='(2,0),(2,1),(2,3),(2,4)', format='pairsList')

opObj11 = procUnitConfObjBeacon.addOperation(name='IncohInt', optype='other')
opObj11.addParameter(name='n', value='4', format='int')

opObj11 = procUnitConfObjBeacon.addOperation(name='getBeaconSignal')

opObj11 = procUnitConfObjBeacon.addOperation(name='BeaconPhase', optype='other')
opObj11.addParameter(name='id', value='201', format='int')
opObj11.addParameter(name='wintitle', value='Beacon Phase', format='str')
opObj11.addParameter(name='timerange', value='300', format='int')
opObj11.addParameter(name='xmin', value='20', format='float')
opObj11.addParameter(name='xmax', value='22', format='float')
opObj11.addParameter(name='ymin', value='-180', format='float')
opObj11.addParameter(name='ymax', value='180', format='float')
opObj11.addParameter(name='figpath', value=pathFigure, format='str')


print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()
