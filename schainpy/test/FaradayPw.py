import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "Faraday Experiment Test"
filename = "faraday.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)

path = '/Volumes/data_f/RAW_EXP/LP_FARADAY'

readUnitConfObj = controllerObj.addReadUnit(datatype='Voltage',
                                            path=path,
                                            startDate='2013/01/01',
                                            endDate='2013/12/31',
                                            startTime='00:00:00',
                                            endTime='23:59:59',
                                            online=0,
                                            delay=10,
                                            walk=0)
################ FARADAY LONG PULSE ####################################
procUnitConfObj0 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())

opObj11 = procUnitConfObj0.addOperation(name='ProfileSelector', optype='other')
opObj11.addParameter(name='profileRangeList', value='0,127', format='intlist')

opObj11 = procUnitConfObj0.addOperation(name='selectHeightsByIndex')
opObj11.addParameter(name='minIndex', value='0', format='float')
opObj11.addParameter(name='maxIndex', value='800', format='float')

opObj11 = procUnitConfObj0.addOperation(name='selectChannels')
opObj11.addParameter(name='channelList', value='0', format='intlist')

procUnitConfObj1 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObj0.getId())
procUnitConfObj1.addParameter(name='nFFTPoints', value='16', format='int')

opObj11 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
opObj11.addParameter(name='timeInterval', value='1', format='float')

opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
opObj11.addParameter(name='idfigure', value='1', format='int')
opObj11.addParameter(name='wintitle', value='RTIPLot', format='str')
opObj11.addParameter(name='zmin', value='0', format='int')
opObj11.addParameter(name='zmax', value='90', format='int')
opObj11.addParameter(name='xmin', value='9', format='float')
opObj11.addParameter(name='xmax', value='11', format='float')
#opObj11.addParameter(name='save', value='1', format='int')
#opObj11.addParameter(name='figfile', value='rti-imaging.png', format='str')
#opObj11.addParameter(name='figpath', value='/media/datos/IMAGING/IMAGING/graphs', format='str')
#opObj11.addParameter(name='ftp', value='1', format='int')
#opObj11.addParameter(name='ftpratio', value='3', format='int')

################ FARADAY DOUBLE PULSE PARTE 1####################################
procUnitConfObjDP1 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())

opObj11 = procUnitConfObjDP1.addOperation(name='ProfileSelector', optype='other')
opObj11.addParameter(name='profileRangeList', value='0,0', format='intlist')

opObj11 = procUnitConfObjDP1.addOperation(name='selectHeightsByIndex')
opObj11.addParameter(name='minIndex', value='801', format='float')
opObj11.addParameter(name='maxIndex', value='1065', format='float')

opObj11 = procUnitConfObjDP1.addOperation(name='selectChannels')
opObj11.addParameter(name='channelList', value='0', format='intlist')

procUnitConfObjSpDP1 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObjDP1.getId())
procUnitConfObjSpDP1.addParameter(name='nFFTPoints', value='16', format='int')

opObj11 = procUnitConfObjSpDP1.addOperation(name='IncohInt', optype='other')
opObj11.addParameter(name='timeInterval', value='2', format='float')

opObj11 = procUnitConfObjSpDP1.addOperation(name='RTIPlot', optype='other')
opObj11.addParameter(name='idfigure', value='2', format='int')
opObj11.addParameter(name='wintitle', value='RTIPLot', format='str')
opObj11.addParameter(name='zmin', value='0', format='int')
opObj11.addParameter(name='zmax', value='90', format='int')
opObj11.addParameter(name='xmin', value='9', format='float')
opObj11.addParameter(name='xmax', value='11', format='float')
#opObj11.addParameter(name='save', value='1', format='int')
#opObj11.addParameter(name='figfile', value='rti-imaging.png', format='str')
#opObj11.addParameter(name='figpath', value='/media/datos/IMAGING/IMAGING/graphs', format='str')
#opObj11.addParameter(name='ftp', value='1', format='int')
#opObj11.addParameter(name='ftpratio', value='3', format='int')


################ FARADAY DOUBLE PULSE PARTE 2####################################

procUnitConfObjDP2 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())

opObj11 = procUnitConfObjDP2.addOperation(name='ProfileSelector', optype='other')
opObj11.addParameter(name='profileRangeList', value='0,0', format='intlist')

opObj11 = procUnitConfObjDP2.addOperation(name='selectHeightsByIndex')
opObj11.addParameter(name='minIndex', value='1069', format='float')
opObj11.addParameter(name='maxIndex', value='1337', format='float')

opObj11 = procUnitConfObjDP2.addOperation(name='selectChannels')
opObj11.addParameter(name='channelList', value='0', format='intlist')

procUnitConfObjSpDP2 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObjDP2.getId())
procUnitConfObjSpDP2.addParameter(name='nFFTPoints', value='16', format='int')

opObj11 = procUnitConfObjSpDP2.addOperation(name='IncohInt', optype='other')
opObj11.addParameter(name='timeInterval', value='2', format='float')

opObj11 = procUnitConfObjSpDP2.addOperation(name='RTIPlot', optype='other')
opObj11.addParameter(name='idfigure', value='3', format='int')
opObj11.addParameter(name='wintitle', value='RTIPLot', format='str')
opObj11.addParameter(name='zmin', value='0', format='int')
opObj11.addParameter(name='zmax', value='90', format='int')
opObj11.addParameter(name='xmin', value='9', format='float')
opObj11.addParameter(name='xmax', value='11', format='float')
#opObj11.addParameter(name='save', value='1', format='int')
#opObj11.addParameter(name='figfile', value='rti-imaging.png', format='str')
#opObj11.addParameter(name='figpath', value='/media/datos/IMAGING/IMAGING/graphs', format='str')
#opObj11.addParameter(name='ftp', value='1', format='int')
#opObj11.addParameter(name='ftpratio', value='3', format='int')


print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()