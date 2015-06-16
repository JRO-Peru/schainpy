#    DIAS 19 Y 20 FEB 2014
#    Comprobacion de Resultados DBS con SA

import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "JASMET Experiment Test"
filename = "JASMETtest.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)

#Experimentos

#2014051    20 Feb 2014
path = '/home/soporte/Data/JASMET/JASMET_30/2014106'
pathFigure = '/home/soporte/workspace/Graficos/JASMET/prueba1'

startTime = '00:00:00'
endTime = '23:59:59'
xmin ='19.0'
xmax = '34.0'
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
#------------------------------------------------------------------------------------------------
readUnitConfObj = controllerObj.addReadUnit(datatype='VoltageReader',
                                            path=path,
                                            startDate='2014/04/15',
                                            endDate='2014/04/16',
                                            startTime=startTime,
                                            endTime=endTime,
                                            online=0,
                                            delay=5,
                                            walk=0)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')


#--------------------------------------------------------------------------------------------------

procUnitConfObj0 = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())

opObj00 = procUnitConfObj0.addOperation(name='selectChannels')
opObj00.addParameter(name='channelList', value='0, 1, 2, 3, 4', format='intlist')

opObj01 = procUnitConfObj0.addOperation(name='setRadarFrequency')
opObj01.addParameter(name='frequency', value='30.e6', format='float')

#opObj11 = procUnitConfObj0.addOperation(name='Decoder', optype='other')
#--------------------------------------------------------------------------------------------------

procUnitConfObj1 = controllerObj.addProcUnit(datatype='ParametersProc', inputId=procUnitConfObj0.getId())
procUnitConfObj1.addParameter(name='nSeconds', value='100', format='int')

opObj10 = procUnitConfObj1.addOperation(name='DetectMeteors')
opObj10.addParameter(name='predefinedPhaseShifts', value='-89.5, 41.5, 0.0, -138.0, -85.5', format='floatlist')
opObj10.addParameter(name='cohDetection', value='0', format='bool') 
opObj10.addParameter(name='noise_multiple', value='4', format='int') 
opObj10.addParameter(name='SNRThresh', value='5', format='float') 
opObj10.addParameter(name='phaseThresh', value='20', format='float') 
opObj10.addParameter(name='azimuth', value='45', format='float') 
opObj10.addParameter(name='hmin', value='68', format='float') 
opObj10.addParameter(name='hmax', value='112', format='float') 

opObj13 = procUnitConfObj1.addOperation(name='SkyMapPlot', optype='other')
opObj13.addParameter(name='id', value='1', format='int')
opObj13.addParameter(name='wintitle', value='Sky Map', format='str')
opObj13.addParameter(name='save', value='1', format='bool')
opObj13.addParameter(name='figpath', value=pathFigure, format='str')

opObj11 = procUnitConfObj1.addOperation(name='WindProfiler', optype='other')
opObj11.addParameter(name='technique', value='Meteors', format='str')
opObj11.addParameter(name='nHours', value='1.0', format='float')
opObj11.addParameter(name='SNRThresh', value='12.0', format='float')

opObj12 = procUnitConfObj1.addOperation(name='WindProfilerPlot', optype='other')
opObj12.addParameter(name='id', value='2', format='int')
opObj12.addParameter(name='wintitle', value='Wind Profiler', format='str')
opObj12.addParameter(name='save', value='1', format='bool')
opObj12.addParameter(name='figpath', value = pathFigure, format='str')
opObj12.addParameter(name='zmin', value='-120', format='int')
opObj12.addParameter(name='zmax', value='120', format='int')
# opObj12.addParameter(name='zmin_ver', value='-0.8', format='float')
# opObj12.addParameter(name='zmax_ver', value='0.8', format='float')
# opObj23.addParameter(name='SNRmin', value='-10', format='int')
# opObj23.addParameter(name='SNRmax', value='60', format='int')
# opObj23.addParameter(name='SNRthresh', value='0', format='float')
opObj12.addParameter(name='xmin', value=xmin, format='float')
opObj12.addParameter(name='xmax', value=xmax, format='float')

#--------------------------------------------------------------------------------------------------
print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()