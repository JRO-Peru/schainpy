"""

Este script se ha configurado para procesar datos de JASMET 30.15MHz

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

# path = '/home/dsuarez/.gvfs/datos on 10.10.20.2/High_Power_Meteor'
# 
# path = '/Volumes/FREE_DISK/meteor_data'
# 
# path = '/Users/dsuarez/Movies/meteor'

# path = '/home/dsuarez/.gvfs/data on 10.10.20.6/RAW_EXP'

# DEFINE EL PATH PARA DIA o NOCHE
path = ''


readUnitConfObj = controllerObj.addReadUnit(datatype='Voltage',
                                            path=path,
                                            startDate='2013/08/21',
                                            endDate='2013/08/21',
                                            startTime='00:00:00',
                                            endTime='23:59:59',
                                            online=1,
                                            delay=2,
                                            walk=1)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')

procUnitConfObj0 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())


opObj11 = procUnitConfObj0.addOperation(name='Decoder', optype='other')


opObj11 = procUnitConfObj0.addOperation(name='CohInt', optype='other')
opObj11.addParameter(name='n', value='2', format='int')

opObj11 = procUnitConfObj0.addOperation(name='VoltageWriter', optype='other')
opObj11.addParameter(name='path', value='/')
opObj11.addParameter(name='blocksPerFile', value='100', format='int')
opObj11.addParameter(name='profilesPerBlock', value='200', format='int')



# procUnitConfObj1 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObj0.getId())
# procUnitConfObj1.addParameter(name='nProfiles', value='200', format='int')
# procUnitConfObj1.addParameter(name='nFFTPoints', value='200', format='int')
# 
# 
# opObj11 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
# opObj11.addParameter(name='n', value='4', format='int')



# opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
# opObj11.addParameter(name='id', value='100', format='int')
# opObj11.addParameter(name='wintitle', value='JASMET30MHZ', format='str')
# opObj11.addParameter(name='timerange', value='300', format='int')
# opObj11.addParameter(name='zmin', value='20', format='float')
# opObj11.addParameter(name='zmax', value='60', format='float')
# # opObj11.addParameter(name='xmin', value='18', format='float')
# # opObj11.addParameter(name='xmax', value='', format='float')
# opObj11.addParameter(name='save', value='1', format='int')
# opObj11.addParameter(name='figpath', value='/home/operaciones/Pictures', format='str')
# opObj11.addParameter(name='ftp', value='1', format='int')
# opObj11.addParameter(name='wr_period', value='10', format='int')
# opObj11.addParameter(name='ftp_wei', value='1', format='int')
# opObj11.addParameter(name='exp_code', value='15', format='int')


# opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
# opObj11.addParameter(name='id', value='101', format='int')
# opObj11.addParameter(name='wintitle', value='JASMET30MHZ', format='str')
# opObj11.addParameter(name='zmin', value='20', format='float')
# opObj11.addParameter(name='zmax', value='60', format='float')
# # opObj11.addParameter(name='realtime', value='1', format='bool')
# # opObj11.addParameter(name='show', value='0', format='bool')
# opObj11.addParameter(name='save', value='1', format='int')
# opObj11.addParameter(name='figpath', value='/home/operaciones/Pictures', format='str')
# opObj11.addParameter(name='ftp', value='1', format='int')
# opObj11.addParameter(name='wr_period', value='10', format='int')
# opObj11.addParameter(name='ftp_wei', value='1', format='int')
# opObj11.addParameter(name='exp_code', value='15', format='int')


print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()
