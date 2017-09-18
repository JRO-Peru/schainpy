
import os, sys

from schainpy.controller import Project

controllerObj = Project()
controllerObj.setup(id = '002', name='script02', description="JASMET Meteor Detection")

#--------------------------------------    Setup    -----------------------------------------
#Verificar estas variables

#Path para los archivos
# path = '/mnt/jars/2016_08/NOCHE'
# path = '/media/joscanoa/DATA_JASMET/JASMET/2016_08/DIA' 
# path = '/media/joscanoa/DATA_JASMET/JASMET/2016_08/NOCHE' 
path = '/home/nanosat/data/jasmet' 

#Path para los graficos
pathfig = os.path.join(os.environ['HOME'],'Pictures/JASMET30/201608/graphics')

#Path para los archivos HDF5 de meteoros
pathfile = os.path.join(os.environ['HOME'],'Pictures/JASMET30/201608/meteor')

#Fechas para busqueda de archivos
startDate = '2010/08/29'
endDate = '2017/09/11'
#Horas para busqueda de archivos
startTime = '00:00:00'
endTime = '23:59:59'
                            
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
#------------------------------    Voltage Reading Unit    ----------------------------------

readUnitConfObj = controllerObj.addReadUnit(datatype='VoltageReader',
                                            path=path,
                                            startDate=startDate,
                                            endDate=endDate,
                                            startTime=startTime,
                                            endTime=endTime,
                                            online=0,
                                            delay=30,
                                            walk=1,
                                            getblock=1,
                                            blocktime=100)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')

#--------------------------    Voltage Processing Unit    ------------------------------------

procUnitConfObj0 = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())

opObj00 = procUnitConfObj0.addOperation(name='selectChannels')
opObj00.addParameter(name='channelList', value='0,1,2,3,4', format='intlist')

opObj01 = procUnitConfObj0.addOperation(name='setRadarFrequency')
opObj01.addParameter(name='frequency', value='30.e6', format='float')

# opObj01 = procUnitConfObj0.addOperation(name='interpolateHeights')
# opObj01.addParameter(name='topLim', value='73', format='int')
# opObj01.addParameter(name='botLim', value='71', format='int')

opObj02 = procUnitConfObj0.addOperation(name='Decoder', optype='other')

opObj03 = procUnitConfObj0.addOperation(name='CohInt', optype='other')
opObj03.addParameter(name='n', value='2', format='int')

procUnitConfObj1 = controllerObj.addProcUnit(datatype='SpectraProc', inputId=procUnitConfObj0.getId())
opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
opObj11.addParameter(name='id', value='237', format='int')
opObj11.addParameter(name='xmin', value='9.0', format='float') 
opObj11.addParameter(name='xmax', value='16.0', format='float') 
opObj11.addParameter(name='zmin', value='15.0', format='float') 
opObj11.addParameter(name='zmax', value='50.0', format='float') 

#---------------------------    Parameters Processing Unit    ------------------------------------

procUnitConfObj1 = controllerObj.addProcUnit(datatype='ParametersProc', inputId=procUnitConfObj0.getId())
#     
opObj10 = procUnitConfObj1.addOperation(name='SMDetection', optype='other')
opObj10.addParameter(name='azimuth', value='45', format='float') 
opObj10.addParameter(name='hmin', value='60', format='float') 
opObj10.addParameter(name='hmax', value='120', format='float')

opObj12 = procUnitConfObj1.addOperation(name='ParamWriter', optype='other')
opObj12.addParameter(name='path', value=pathfile)
opObj12.addParameter(name='blocksPerFile', value='1000', format='int')
opObj12.addParameter(name='metadataList',value='type,heightList,paramInterval,timeZone',format='list')
opObj12.addParameter(name='dataList',value='data_param,utctime',format='list')
opObj12.addParameter(name='mode',value='2',format='int')

#--------------------------------------------------------------------------------------------------

controllerObj.start()


