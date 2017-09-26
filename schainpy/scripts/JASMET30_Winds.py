import os, sys

path = os.path.split(os.getcwd())[0]
path = os.path.split(path)[0]

sys.path.insert(0, path)

from schainpy.controller import Project

controllerObj = Project()
controllerObj.setup(id = '005', name='script05', description="JASMET Wind Estimation")

#--------------------------------------    Setup    -----------------------------------------
#Verificar estas variables

#Path donde estan los archivos HDF5 de meteoros
path = os.path.join(os.environ['HOME'],'Pictures/JASMET30_mp/201608/meteor')

#Path para los graficos
pathfig = os.path.join(os.environ['HOME'],'Pictures/JASMET30_mp/201608/graphics')

#Path donde se almacenaran las estimaciones de vientos
pathfile = os.path.join(os.environ['HOME'],'Pictures/JASMET30_mp/201608/phase')

#Fechas para busqueda de archivos
startDate = '2016/08/29'
endDate = '2016/09/11'
#Horas para busqueda de archivos
startTime = '00:00:00'
endTime = '23:59:59'

#Offsets optimos obtenidos con OptimumOffset.py
phaseOffsets = '-2.84, -1.77, 11.94, 9.71'     
phaseOffsets = '-5.86, -0.93, -7.29, 23.35'                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
#------------------------------------------------------------------------------------------------
readUnitConfObj = controllerObj.addReadUnit(datatype='ParamReader',
                                            path=path,
                                            startDate=startDate,
                                            endDate=endDate,
                                            startTime=startTime,
                                            endTime=endTime,
                                            walk=1)
#--------------------------------------------------------------------------------------------------

procUnitConfObj1 = controllerObj.addProcUnit(datatype='ParametersProc', inputId=readUnitConfObj.getId())
opObj10 = procUnitConfObj1.addOperation(name='CorrectSMPhases',optype='other')
opObj10.addParameter(name='phaseOffsets', value=phaseOffsets, format='floatlist')

opObj13 = procUnitConfObj1.addOperation(name='SkyMapPlot', optype='other')
opObj13.addParameter(name='id', value='1', format='int')
opObj13.addParameter(name='wintitle', value='Sky Map', format='str')
opObj13.addParameter(name='save', value='1', format='bool')
opObj13.addParameter(name='figpath', value=pathfig, format='str')
opObj13.addParameter(name='ftp', value='1', format='int')
opObj13.addParameter(name='exp_code', value='15', format='int')
opObj13.addParameter(name='sub_exp_code', value='1', format='int')
opObj13.addParameter(name='tmin', value='0', format='int')
opObj13.addParameter(name='tmax', value='24', format='int')
  
opObj22 = procUnitConfObj1.addOperation(name='WindProfiler', optype='other')
opObj22.addParameter(name='technique', value='Meteors', format='str')
opObj22.addParameter(name='nHours', value='1', format='float')
opObj22.addParameter(name='hmin', value='70', format='float') 
opObj22.addParameter(name='hmax', value='120', format='float') 

opObj23 = procUnitConfObj1.addOperation(name='WindProfilerPlot', optype='other')
opObj23.addParameter(name='id', value='2', format='int')
opObj23.addParameter(name='wintitle', value='Wind Profiler', format='str')
opObj23.addParameter(name='save', value='1', format='bool')
opObj23.addParameter(name='figpath', value = pathfig, format='str')
opObj23.addParameter(name='zmin', value='-140', format='int')
opObj23.addParameter(name='zmax', value='140', format='int')
opObj23.addParameter(name='xmin', value='0', format='float')
opObj23.addParameter(name='xmax', value='24', format='float')
opObj23.addParameter(name='ymin', value='70', format='float')
opObj23.addParameter(name='ymax', value='110', format='float')
 
opObj33 = procUnitConfObj1.addOperation(name='ParamWriter', optype='other')
opObj33.addParameter(name='path', value=pathfile)
opObj33.addParameter(name='blocksPerFile', value='1000', format='int')
opObj33.addParameter(name='metadataList',value='type,outputInterval,timeZone',format='list')
opObj33.addParameter(name='dataList',value='data_output,utctime',format='list')
#--------------------------------------------------------------------------------------------------

controllerObj.start()