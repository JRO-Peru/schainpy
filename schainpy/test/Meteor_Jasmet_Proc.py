import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "Meteor Experiment Test"
filename = "meteor20130812.xml"

controllerObj = Project()
controllerObj.setup(id = '191', name='meteor_test01', description=desc)

# path = '/home/dsuarez/.gvfs/datos on 10.10.20.2/High_Power_Meteor'
# 
# path = '/Volumes/FREE_DISK/meteor_data'
# 
# path = '/Users/dsuarez/Movies/meteor'

path = '/home/dsuarez/.gvfs/data on 10.10.20.6/RAW_EXP'

readUnitConfObj = controllerObj.addReadUnit(datatype='Voltage',
                                            path=path,
                                            startDate='2013/08/01',
                                            endDate='2013/08/30',
                                            startTime='00:00:00',
                                            endTime='23:59:59',
                                            online=0,
                                            delay=1,
                                            walk=0)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')

procUnitConfObj0 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())

opObj11 = procUnitConfObj0.addOperation(name='Decoder', optype='other')
# opObj11.addParameter(name='code', value='1,1,1,0,1,1,0,1,1,1,1,0,0,0,1,0,1,1,1,0,1,1,0,1,0,0,0,1,1,1,0,1', format='floatlist')
# opObj11.addParameter(name='nCode', value='2', format='int')
# opObj11.addParameter(name='nBaud', value='16', format='int')

opObj11 = procUnitConfObj0.addOperation(name='CohInt', optype='other')
opObj11.addParameter(name='n', value='2', format='int')


procUnitConfObj1 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObj0.getId())
procUnitConfObj1.addParameter(name='nFFTPoints', value='200', format='int')

# opObj11 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
# opObj11.addParameter(name='n', value='1', format='int')


opObj11 = procUnitConfObj1.addOperation(name='SpectraWriter', optype='other')
opObj11.addParameter(name='path', value='/media/datos/JASMET')
opObj11.addParameter(name='blocksPerFile', value='30', format='int')


print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()
