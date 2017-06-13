"""
Se debe verficar que el disco de datos se encuentra montado en el sistema
"""
import os, sys

path = os.path.split(os.getcwd())[0]
path = os.path.split(path)[0]

sys.path.insert(0, path)

from schainpy.controller import Project

desc = "Meteor Experiment Test"
filename = "meteor20130812.xml"

controllerObj = Project()
controllerObj.setup(id = '191', name='meteor_test01', description=desc)

path='/mnt/jars/2016_08/NOCHE/'
path='/mnt/jars/2016_08/DIA/'
path1 = '/media/soporte/Data/JASMET'

readUnitConfObj = controllerObj.addReadUnit(datatype='Voltage',
                                            path=path,
                                            startDate='2016/09/28',
                                            endDate='2016/09/28',
                                            startTime='00:00:00',
                                            endTime='10:50:00',
                                            online=0,
                                            walk=1)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')
    
procUnitConfObj0 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())
    
opObj11 = procUnitConfObj0.addOperation(name='Decoder', optype='other')
    
opObj11 = procUnitConfObj0.addOperation(name='CohInt', optype='other')
opObj11.addParameter(name='n', value='2', format='int')
    
opObj11 = procUnitConfObj0.addOperation(name='VoltageWriter', optype='other')
opObj11.addParameter(name='path', value=path1)
opObj11.addParameter(name='blocksPerFile', value='100', format='int')
opObj11.addParameter(name='profilesPerBlock', value='200', format='int')

print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()
