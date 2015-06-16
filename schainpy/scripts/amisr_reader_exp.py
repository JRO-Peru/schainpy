import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "AMISR Experiment Test"
filename = "amisr.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)

path = '/home/administrator/Documents/amisr'

readUnitConfObj = controllerObj.addReadUnit(datatype='AMISR',
                                            path=path,
                                            startDate='2014/08/18',
                                            endDate='2014/08/18',
                                            startTime='00:00:00',
                                            endTime='23:59:59',
                                            walk=1)

procUnitConfObj0 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())

opObj11 = procUnitConfObj0.addOperation(name='Scope', optype='other')
opObj11.addParameter(name='id', value='101', format='int')
opObj11.addParameter(name='wintitle', value='AMISR', format='str')
opObj11.addParameter(name='type', value='iq', format='str')

opObj11 = procUnitConfObjBeam1.addOperation(name='ProfileSelector', optype='other')
opObj11.addParameter(name='profileRangeList', value='0,81', format='intlist')

opObj11 = procUnitConfObj0.addOperation(name='PowerProfile', optype='other')
opObj11.addParameter(name='id', value='102', format='int')
opObj11.addParameter(name='wintitle', value='AMISR Power Profile', format='str')


print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()
