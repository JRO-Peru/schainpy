#    DIAS 19 Y 20 FEB 2014
#    Comprobacion de Resultados DBS con SA

import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "DBS Experiment Test"
filename = "DBStest.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)

#Experimentos

#2014050    19 Feb 2014
# path = '/home/soporte/Documents/MST_Data/DBS/d2014050'
# pathFigure = '/home/soporte/workspace/Graficos/DBS/d2014050p/'
# xmin = '15.5'
# xmax = '23.99999999'
# startTime = '17:25:00'
# filehdf5 = "DBS_2014050.hdf5"

#2014051    20 Feb 2014
path = '/home/soporte/Data/MST/DBS/d2014051'
pathFigure = '/home/soporte/workspace/Graficos/DBS/prueba1/'
xmin = '0'
xmax = '7.5'
startTime = '00:00:00'
filehdf5 = "DBS_2014051.hdf5"



#------------------------------------------------------------------------------------------------
readUnitConfObj = controllerObj.addReadUnit(datatype='VoltageReader',
                                            path=path,
                                            startDate='2014/01/31',
                                            endDate='2014/03/31',
                                            startTime=startTime,
                                            endTime='23:59:59',
                                            online=0,
                                            delay=5,
                                            walk=0)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')


#--------------------------------------------------------------------------------------------------

procUnitConfObj0 = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())

opObj11 = procUnitConfObj0.addOperation(name='Decoder', optype='other')

opObj11 = procUnitConfObj0.addOperation(name='CohInt', optype='other')
opObj11.addParameter(name='n', value='256', format='int')
# opObj11.addParameter(name='n', value='16', format='int')

opObj11 = procUnitConfObj0.addOperation(name='selectHeightsByIndex')
opObj11.addParameter(name='minIndex', value='10', format='float')
opObj11.addParameter(name='maxIndex', value='60', format='float')

#---------------------------------------------------------------------------------------------------

procUnitConfObj1 = controllerObj.addProcUnit(datatype='SpectraProc', inputId=procUnitConfObj0.getId())
procUnitConfObj1.addParameter(name='nFFTPoints', value='64', format='int')
procUnitConfObj1.addParameter(name='nProfiles', value='64', format='int')
# procUnitConfObj1.addParameter(name='ippFactor', value='2', format='int')
procUnitConfObj1.addParameter(name='pairsList', value='(0,0),(0,1),(2,1)', format='pairsList')

opObj11 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
opObj11.addParameter(name='n', value='5', format='int')

opObj14 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
opObj14.addParameter(name='id', value='1', format='int')
opObj14.addParameter(name='wintitle', value='Con interf', format='str')
opObj14.addParameter(name='save', value='1', format='bool')
opObj14.addParameter(name='figpath', value=pathFigure, format='str')
opObj14.addParameter(name='zmin', value='5', format='int')
opObj14.addParameter(name='zmax', value='90', format='int')

opObj12 = procUnitConfObj1.addOperation(name='removeInterference')
opObj13 = procUnitConfObj1.addOperation(name='removeDC')
opObj13.addParameter(name='mode', value='1', format='int')

opObj12 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
opObj12.addParameter(name='id', value='2', format='int')
opObj12.addParameter(name='wintitle', value='RTI Plot', format='str')
opObj12.addParameter(name='save', value='1', format='bool')
opObj12.addParameter(name='figpath', value = pathFigure, format='str')
opObj12.addParameter(name='xmin', value=xmin, format='float')
opObj12.addParameter(name='xmax', value=xmax, format='float')
opObj12.addParameter(name='zmin', value='5', format='int')
opObj12.addParameter(name='zmax', value='90', format='int')

#--------------------------------------------------------------------------------------------------

procUnitConfObj2 = controllerObj.addProcUnit(datatype='ParametersProc', inputId=procUnitConfObj1.getId())
opObj20 = procUnitConfObj2.addOperation(name='GetMoments')
 
opObj21 = procUnitConfObj2.addOperation(name='MomentsPlot', optype='other')
opObj21.addParameter(name='id', value='3', format='int')
opObj21.addParameter(name='wintitle', value='Moments Plot', format='str')
opObj21.addParameter(name='save', value='1', format='bool')
opObj21.addParameter(name='figpath', value=pathFigure, format='str')
opObj21.addParameter(name='zmin', value='5', format='int')
opObj21.addParameter(name='zmax', value='90', format='int')

opObj21 = procUnitConfObj2.addOperation(name='ParametersPlot', optype='other')
opObj21.addParameter(name='id', value='5', format='int')
opObj21.addParameter(name='wintitle', value='Radial Velocity Plot', format='str')
opObj21.addParameter(name='save', value='1', format='bool')
opObj21.addParameter(name='figpath', value=pathFigure, format='str')
opObj21.addParameter(name='SNRmin', value='-10', format='int')
opObj21.addParameter(name='SNRmax', value='60', format='int')
opObj21.addParameter(name='SNRthresh', value='0', format='float')
opObj21.addParameter(name='xmin', value=xmin, format='float')
opObj21.addParameter(name='xmax', value=xmax, format='float')

opObj21 = procUnitConfObj2.addOperation(name='ParametersPlot', optype='other')
opObj21.addParameter(name='id', value='6', format='int')
opObj21.addParameter(name='wintitle', value='Spectral width Plot', format='str')
opObj21.addParameter(name='save', value='1', format='bool')
opObj21.addParameter(name='figpath', value=pathFigure, format='str')
opObj21.addParameter(name='SNRmin', value='-10', format='int')
opObj21.addParameter(name='SNRmax', value='60', format='int')
opObj21.addParameter(name='SNRthresh', value='0', format='float')
opObj21.addParameter(name='xmin', value=xmin, format='float')
opObj21.addParameter(name='xmax', value=xmax, format='float')
opObj21.addParameter(name='zmin', value=0, format='float')
opObj21.addParameter(name='paramIndex', value=2, format='int')
opObj21.addParameter(name='onlyPositive', value=1, format='bool')
     
opObj22 = procUnitConfObj2.addOperation(name='WindProfiler', optype='other')
opObj22.addParameter(name='technique', value='DBS', format='str')
opObj22.addParameter(name='correctAzimuth', value='51.06', format='float')
opObj22.addParameter(name='correctFactor', value='-1', format='float') 
opObj22.addParameter(name='dirCosx', value='0.041016, 0, -0.054688', format='floatlist') 
opObj22.addParameter(name='dirCosy', value='-0.041016, 0.025391, -0.023438', format='floatlist')
# opObj22.addParameter(name='horizontalOnly', value='1', format='bool')
# opObj22.addParameter(name='channelList', value='1,2', format='intlist')

opObj23 = procUnitConfObj2.addOperation(name='WindProfilerPlot', optype='other')
opObj23.addParameter(name='id', value='4', format='int')
opObj23.addParameter(name='wintitle', value='Wind Profiler', format='str')
opObj23.addParameter(name='save', value='1', format='bool')
opObj23.addParameter(name='figpath', value = pathFigure, format='str')
opObj23.addParameter(name='zmin', value='-10', format='int')
opObj23.addParameter(name='zmax', value='10', format='int')
opObj23.addParameter(name='zmin_ver', value='-80', format='float')
opObj23.addParameter(name='zmax_ver', value='80', format='float')
opObj23.addParameter(name='SNRmin', value='-10', format='int')
opObj23.addParameter(name='SNRmax', value='60', format='int')
opObj23.addParameter(name='SNRthresh', value='0', format='float')
opObj23.addParameter(name='xmin', value=xmin, format='float')
opObj23.addParameter(name='xmax', value=xmax, format='float')

#--------------------------------------------------------------------------------------------------
print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()