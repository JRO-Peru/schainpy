#    DIAS 19 Y 20 FEB 2014
#    Comprobacion de Resultados DBS con SA

import os, sys

path = os.path.split(os.getcwd())[0]
path = os.path.split(path)[0]

sys.path.insert(0, path)

from schainpy.controller import Project

desc = "SA Experiment Test"
filename = "SA2014050.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)


#Experimentos

#2014050    19 Feb 2014
path = '/media/joscanoa/84A65E64A65E5730/soporte/Data/MST/SA/d2014050'
pathFigure = '/media/joscanoa/84A65E64A65E5730/soporte/workspace/Graficos/SA/prueba1/'
xmin = '15.5'
xmax = '24'
startTime = '15:30:00'
filehdf5 = "SA_2014050.hdf5"

#2014051    20 Feb 2014
path = '/media/erick/6F60F7113095A154/CLAIRE/CLAIRE_WINDS_2MHZ/DATA/' #'/home/soporte/Data/MST/SA/d2014051'
# pathFigure = '/home/soporte/workspace/Graficos/SA/new/'
# xmin = '0.0'
# xmax = '8.0'
# startTime = '00:00:00'
# filehdf5 = "SA_2014051.hdf5"

readUnitConfObj = controllerObj.addReadUnit(datatype='VoltageReader',
                                            path=path,
                                            startDate='2017/08/22',
                                            endDate='2018/08/22',
                                            startTime='00:00:00',
                                            endTime='6:00:59',
                                            online=0,
                                            delay=5,
                                            walk=1)
                                            #getblock=1,
                                            #blocksize=32768)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')


#--------------------------------------------------------------------------------------------------

procUnitConfObj0 = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())

opObj11 = procUnitConfObj0.addOperation(name='Decoder', optype='other')

opObj11 = procUnitConfObj0.addOperation(name='CohInt', optype='other')
# opObj11.addParameter(name='n', value='600', format='int')
opObj11.addParameter(name='n', value='4', format='int')

opObj11 = procUnitConfObj0.addOperation(name='selectHeightsByIndex')
opObj11.addParameter(name='minIndex', value='10', format='float')
opObj11.addParameter(name='maxIndex', value='60', format='float')
#---------------------------------------------------------------------------------------------------
procUnitConfObj1 = controllerObj.addProcUnit(datatype='CorrelationProc', inputId=procUnitConfObj0.getId())
procUnitConfObj1.addParameter(name='pairsList', value='(0,0),(1,1),(2,2),(3,3),(1,0),(2,3)', format='pairsList')

#procUnitConfObj1.addParameter(name='removeDC', value='1', format='bool')
# #procUnitConfObj1.addParameter(name='lagT', value='0,1,2,3', format='intlist')
# 
# opObj12 = procUnitConfObj1.addOperation(name='CorrelationPlot', optype='other')
# opObj12.addParameter(name='id', value='1', format='int')
# opObj12.addParameter(name='wintitle', value='CrossCorrelation Plot', format='str')
# opObj12.addParameter(name='save', value='1', format='bool')
# opObj12.addParameter(name='zmin', value='0', format='int')
# opObj12.addParameter(name='zmax', value='1', format='int')
# opObj12.addParameter(name='figpath', value = pathFigure, format='str')
# 
# opObj12 = procUnitConfObj1.addOperation(name='removeNoise')
# opObj12.addParameter(name='mode', value='2', format='int')
# opObj12 = procUnitConfObj1.addOperation(name='calculateNormFactor')
#  
# opObj12 = procUnitConfObj1.addOperation(name='CorrelationPlot', optype='other')
# opObj12.addParameter(name='id', value='2', format='int')
# opObj12.addParameter(name='wintitle', value='CrossCorrelation Plot', format='str')
# opObj12.addParameter(name='save', value='1', format='bool')
# opObj12.addParameter(name='zmin', value='0', format='int')
# opObj12.addParameter(name='zmax', value='1', format='int')
# opObj12.addParameter(name='figpath', value = pathFigure, format='str')
# 
# #---------------------------------------------------------------------------------------------------
procUnitConfObj2 = controllerObj.addProcUnit(datatype='ParametersProc', inputId=procUnitConfObj1.getId())

opObj20 = procUnitConfObj2.addOperation(name='SALags', optype='other')
# 
opObj21 = procUnitConfObj2.addOperation(name='WindProfiler', optype='other')
opObj21.addParameter(name='technique', value='SA', format='str')
# # opObj21.addParameter(name='correctFactor', value='-1', format='float') 
opObj21.addParameter(name='positionX', value='1.5,0,1.5', format='floatlist')
opObj21.addParameter(name='positionY', value='0.875,0,-0.875', format='floatlist')
opObj21.addParameter(name='azimuth', value='0.0', format='float')

opObj22 = procUnitConfObj2.addOperation(name='WindProfilerPlot', optype='other')
opObj22.addParameter(name='id', value='4', format='int')
opObj22.addParameter(name='wintitle', value='Wind Profiler', format='str')
#opObj22.addParameter(name='save', value='1', format='bool')
#opObj22.addParameter(name='figpath', value = pathFigure, format='str')
opObj22.addParameter(name='zmin', value='-15', format='int')
opObj22.addParameter(name='zmax', value='15', format='int')
opObj22.addParameter(name='zmin_ver', value='-80', format='float')
opObj22.addParameter(name='zmax_ver', value='80', format='float')
opObj22.addParameter(name='SNRmin', value='-20', format='int')
opObj22.addParameter(name='SNRmax', value='40', format='int')
opObj22.addParameter(name='SNRthresh', value='-3.5', format='float')
opObj22.addParameter(name='xmin', value=xmin, format='float')
opObj22.addParameter(name='xmax', value=xmax, format='float')

#-----------------------------------------------------------------------------------

print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()
