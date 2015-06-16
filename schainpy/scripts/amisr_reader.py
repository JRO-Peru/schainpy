import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "AMISR Experiment"

filename = "amisr_reader.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)

path = os.path.join(os.environ['HOME'],'Documents/amisr') #'/home/signalchain/Documents/amisr'

figpath = os.path.join(os.environ['HOME'],'Pictures/amisr')

readUnitConfObj = controllerObj.addReadUnit(datatype='AMISRReader',
                                            path=path,
                                            startDate='2014/08/18',
                                            endDate='2014/08/18',
                                            startTime='00:00:00',
                                            endTime='23:59:59',
                                            walk=1)

procUnitAMISR = controllerObj.addProcUnit(datatype='AMISRProc', inputId=readUnitConfObj.getId())

opObj11 = procUnitAMISR.addOperation(name='PrintInfo', optype='other')

print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()
