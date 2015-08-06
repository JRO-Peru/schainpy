#    DIAS 19 Y 20 FEB 2014
#    Comprobacion de Resultados DBS con SA

import os, sys

path = os.path.split(os.getcwd())[0]
path = os.path.split(path)[0]

sys.path.insert(0, path)

from schainpy.controller import Project

desc = "JASMET Experiment Test"
filename = "JASMETtest.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)

#Experimentos

#2014051    20 Feb 2014
# path = '/home/soporte/Data/JASMET/JASMET_30/2014106'
# pathFigure = '/home/soporte/workspace/Graficos/JASMET/prueba1'

remotefolder = "/home/wmaster/graficos"
path = '/media/joscanoa/84A65E64A65E5730/soporte/Data/JASMET/JASMET_30/'

pathfile1 = os.path.join(os.environ['HOME'],'Pictures/JASMET30/meteor')
pathfile2 = os.path.join(os.environ['HOME'],'Pictures/JASMET30/wind')
pathfile3 = os.path.join(os.environ['HOME'],'Pictures/JASMET30/phase')

pathfig = os.path.join(os.environ['HOME'],'Pictures/JASMET30/graph')

startTime = '00:00:00'
endTime = '23:59:59'
xmin ='17.0'
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
                                            walk=1)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')


#--------------------------------------------------------------------------------------------------

procUnitConfObj0 = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())

opObj00 = procUnitConfObj0.addOperation(name='selectChannels')
opObj00.addParameter(name='channelList', value='0, 1, 2, 3, 4', format='intlist')

opObj01 = procUnitConfObj0.addOperation(name='setRadarFrequency')
# opObj01.addParameter(name='frequency', value='30.e6', format='float')
opObj01.addParameter(name='frequency', value='50.e6', format='float')

#opObj11 = procUnitConfObj0.addOperation(name='Decoder', optype='other')
#--------------------------------------------------------------------------------------------------

procUnitConfObj1 = controllerObj.addProcUnit(datatype='ParametersProc', inputId=procUnitConfObj0.getId())
procUnitConfObj1.addParameter(name='nSeconds', value='100', format='int')

opObj10 = procUnitConfObj1.addOperation(name='MeteorDetection')
# opObj10.addParameter(name='predefinedPhaseShifts', value='-89.5, 41.5, 0.0, -138.0, -85.5', format='floatlist')
opObj10.addParameter(name='predefinedPhaseShifts', value='0, 0, 0, 0, 0', format='floatlist')
opObj10.addParameter(name='cohDetection', value='0', format='bool') 
opObj10.addParameter(name='noise_multiple', value='4', format='int') 
opObj10.addParameter(name='SNRThresh', value='5', format='float') 
opObj10.addParameter(name='phaseThresh', value='20', format='float') 
opObj10.addParameter(name='azimuth', value='45', format='float') 
opObj10.addParameter(name='hmin', value='68', format='float') 
opObj10.addParameter(name='hmax', value='112', format='float') 
opObj10.addParameter(name='saveAll', value='1', format='bool') 

opObj12 = procUnitConfObj1.addOperation(name='HDF5Writer', optype='other')
opObj12.addParameter(name='path', value=pathfile1)
opObj12.addParameter(name='blocksPerFile', value='1000', format='int')
opObj12.addParameter(name='metadataList',value='type,inputUnit,heightList,paramInterval',format='list')
opObj12.addParameter(name='dataList',value='data_param',format='list')
opObj12.addParameter(name='mode',value='0',format='int')
#Tiene que ser de 3 dimensiones, append en lugar de aumentar una dimension

opObj13 = procUnitConfObj1.addOperation(name='SkyMapPlot', optype='other')
opObj13.addParameter(name='id', value='1', format='int')
opObj13.addParameter(name='wintitle', value='Sky Map', format='str')
opObj13.addParameter(name='save', value='1', format='bool')
opObj13.addParameter(name='figpath', value=pathfig, format='str')
opObj13.addParameter(name='ftp', value='1', format='int')
opObj13.addParameter(name='exp_code', value='15', format='int')
opObj13.addParameter(name='sub_exp_code', value='1', format='int')


#--------------------------------------------------------------------------------------------------
procUnitConfObj2 = controllerObj.addProcUnit(datatype='ParametersProc', inputId=procUnitConfObj1.getId())
  
opObj22 = procUnitConfObj2.addOperation(name='WindProfiler', optype='other')
opObj22.addParameter(name='technique', value='Meteors', format='str')
opObj22.addParameter(name='nHours', value='0.25', format='float')
opObj22.addParameter(name='SNRThresh', value='12.0', format='float')
  
opObj23 = procUnitConfObj2.addOperation(name='WindProfilerPlot', optype='other')
opObj23.addParameter(name='id', value='2', format='int')
opObj23.addParameter(name='wintitle', value='Wind Profiler', format='str')
opObj23.addParameter(name='save', value='1', format='bool')
opObj23.addParameter(name='figpath', value = pathfig, format='str')
opObj23.addParameter(name='zmin', value='-120', format='int')
opObj23.addParameter(name='zmax', value='120', format='int')
# opObj12.addParameter(name='zmin_ver', value='-0.8', format='float')
# opObj12.addParameter(name='zmax_ver', value='0.8', format='float')
# opObj23.addParameter(name='SNRmin', value='-10', format='int')
# opObj23.addParameter(name='SNRmax', value='60', format='int')
# opObj23.addParameter(name='SNRthresh', value='0', format='float')
opObj23.addParameter(name='xmin', value=xmin, format='float')
opObj23.addParameter(name='xmax', value=xmax, format='float')
opObj23.addParameter(name='ftp', value='1', format='int')
opObj23.addParameter(name='exp_code', value='15', format='int')
opObj23.addParameter(name='sub_exp_code', value='1', format='int') 
 
opObj24 = procUnitConfObj2.addOperation(name='HDF5Writer', optype='other')
opObj24.addParameter(name='path', value=pathfile2)
opObj24.addParameter(name='blocksPerFile', value='1000', format='int')
opObj24.addParameter(name='metadataList',value='type,inputUnit,outputInterval',format='list')
opObj24.addParameter(name='dataList',value='data_output,utctime',format='list')
 
#--------------------------------------------------------------------------------------------------
procUnitConfObj3 = controllerObj.addProcUnit(datatype='ParametersProc', inputId=procUnitConfObj1.getId())
 
 
opObj31 = procUnitConfObj3.addOperation(name='PhaseCalibration', optype='other')
opObj31.addParameter(name='nHours', value='0.25', format='float')
opObj31.addParameter(name='distances', value='-15, -15, 12, 12', format='intlist')
# opObj31.addParameter(name='distances', value='-25, -25, 20, 20', format='intlist')
opObj31.addParameter(name='pairs', value='(0,3),(1,2)', format='pairslist')
opObj31.addParameter(name='hmin', value='68', format='float') 
opObj31.addParameter(name='hmax', value='112', format='float')
 
opObj32 = procUnitConfObj3.addOperation(name='PhasePlot', optype='other')
opObj32.addParameter(name='id', value='201', format='int')
opObj32.addParameter(name='wintitle', value='PhaseCalibration', format='str')
# opObj32.addParameter(name='timerange', value='300', format='int')
opObj32.addParameter(name='xmin', value=xmin, format='float')
opObj32.addParameter(name='xmax', value=xmax, format='float')
# opObj32.addParameter(name='xmin', value='19', format='float')
# opObj32.addParameter(name='xmax', value='20', format='float')
opObj32.addParameter(name='ymin', value='-180', format='float')
opObj32.addParameter(name='ymax', value='180', format='float')
opObj32.addParameter(name='figpath', value=pathfig, format='str')
opObj32.addParameter(name='ftp', value='1', format='int')
opObj32.addParameter(name='exp_code', value='15', format='int')
opObj32.addParameter(name='sub_exp_code', value='1', format='int')

opObj33 = procUnitConfObj3.addOperation(name='HDF5Writer', optype='other')
opObj33.addParameter(name='path', value=pathfile3)
opObj33.addParameter(name='blocksPerFile', value='1000', format='int')
opObj33.addParameter(name='metadataList',value='type,inputUnit,outputInterval',format='list')
opObj33.addParameter(name='dataList',value='data_output,utctime',format='list')
# opObj25.addParameter(name='mode',value='1,0,0',format='intlist')

#--------------------------------------------------------------------------------------------------

procUnitConfObj4 = controllerObj.addProcUnit(name='SendToServer')
procUnitConfObj4.addParameter(name='server', value='jro-app.igp.gob.pe', format='str')
procUnitConfObj4.addParameter(name='username', value='wmaster', format='str')
procUnitConfObj4.addParameter(name='password', value='mst2010vhf', format='str')
procUnitConfObj4.addParameter(name='localfolder', value=pathfig, format='str')
procUnitConfObj4.addParameter(name='remotefolder', value=remotefolder, format='str')
procUnitConfObj4.addParameter(name='ext', value='.png', format='str')
procUnitConfObj4.addParameter(name='period', value=20, format='int')
procUnitConfObj4.addParameter(name='protocol', value='ftp', format='str')

#--------------------------------------------------------------------------------------------------

print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()