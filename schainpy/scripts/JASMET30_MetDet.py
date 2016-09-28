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

pathfile1 = os.path.join(os.environ['HOME'],'Pictures/last_campaign/meteor')
pathfig = os.path.join(os.environ['HOME'],'Pictures/last_campaign/graphics')

path = '/mnt/jars/2016_08/NOCHE'
startTime = '00:00:00'
endTime = '08:59:59'
# 
# path = '/mnt/jars/2016_08/DIA'
# startTime = '12:13:00'
# endTime = '23:59:59'

# path = '/mnt/jars/2016_08/NOCHE'
# startTime = '15:00:00'
# endTime = '23:59:59'
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
#------------------------------------------------------------------------------------------------
readUnitConfObj = controllerObj.addReadUnit(datatype='VoltageReader',
                                            path=path,
                                            startDate='2016/08/26',
                                            endDate='2016/08/26',
                                            startTime=startTime,
                                            endTime=endTime,
                                            online=0,
                                            delay=30,
                                            walk=1,
                                            getblock=1,
                                            blocktime=100)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')

#--------------------------------------------------------------------------------------------------

procUnitConfObj0 = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())

opObj00 = procUnitConfObj0.addOperation(name='selectChannels')
opObj00.addParameter(name='channelList', value='0,1,2,3,4', format='intlist')

opObj01 = procUnitConfObj0.addOperation(name='setRadarFrequency')
opObj01.addParameter(name='frequency', value='30.e6', format='float')

opObj00 = procUnitConfObj0.addOperation(name='interpolateHeights')
opObj00.addParameter(name='topLim', value='73', format='int')
opObj00.addParameter(name='botLim', value='69', format='int')

opObj11 = procUnitConfObj0.addOperation(name='Decoder', optype='other')

opObj12 = procUnitConfObj0.addOperation(name='CohInt', optype='other')
opObj12.addParameter(name='n', value='2', format='int')

#--------------------------------------------------------------------------------------------------

procUnitConfObj1 = controllerObj.addProcUnit(datatype='ParametersProc', inputId=procUnitConfObj0.getId())
#     
opObj10 = procUnitConfObj1.addOperation(name='MeteorDetection')
opObj10.addParameter(name='azimuth', value='45', format='float') 
opObj10.addParameter(name='hmin', value='60', format='float') 
opObj10.addParameter(name='hmax', value='120', format='float')

opObj12 = procUnitConfObj1.addOperation(name='ParamWriter', optype='other')
opObj12.addParameter(name='path', value=pathfile1)
opObj12.addParameter(name='blocksPerFile', value='1000', format='int')
opObj12.addParameter(name='metadataList',value='type,heightList,paramInterval,timeZone',format='list')
opObj12.addParameter(name='dataList',value='data_param,utctime',format='list')
opObj12.addParameter(name='mode',value='2',format='int')
# # Tiene que ser de 3 dimensiones, append en lugar de aumentar una dimension
#      
#--------------------------------------------------------------------------------------------------

print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()