import os, sys

path = os.path.split(os.getcwd())[0]
path = os.path.split(path)[0]

sys.path.insert(0, path)

from schainpy.controller import Project

controllerObj = Project()
controllerObj.setup(id = '004', name='script04', description="JASMET Phase Calibration")

#--------------------------------------    Setup    -----------------------------------------
#Verificar estas variables

#Path donde estan los archivos HDF5 de meteoros
path = os.path.join(os.environ['HOME'],'Pictures/JASMET30_mp/201608/meteor')

#Path para los graficos
pathfig = os.path.join(os.environ['HOME'],'Pictures/JASMET30_mp/201608/graphics')

#Path donde se almacenaran las fases calculadas
pathfile = os.path.join(os.environ['HOME'],'Pictures/JASMET30_mp/201608/phase')

#Fechas para busqueda de archivos
startDate = '2016/08/29'
endDate = '2016/09/11'
#Horas para busqueda de archivos
startTime = '00:00:00'
endTime = '23:59:59'
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
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
# #      
opObj31 = procUnitConfObj1.addOperation(name='SMPhaseCalibration', optype='other')
opObj31.addParameter(name='nHours', value='1', format='float')
opObj31.addParameter(name='hmin', value='60', format='float') 
opObj31.addParameter(name='hmax', value='120', format='float')
# opObj31.addParameter(name='channelPositions', value='(2.5,0),(0,2.5),(0,0),(0,4.5),(-2,0)', format='pairslist')
     
opObj32 = procUnitConfObj1.addOperation(name='PhasePlot', optype='other')
opObj32.addParameter(name='id', value='201', format='int')
opObj32.addParameter(name='wintitle', value='PhaseCalibration', format='str')
opObj32.addParameter(name='save', value='1', format='bool')
opObj32.addParameter(name='xmin', value='0', format='float')
opObj32.addParameter(name='xmax', value='24', format='float')
opObj32.addParameter(name='ymin', value='-180', format='float')
opObj32.addParameter(name='ymax', value='180', format='float')
opObj32.addParameter(name='figpath', value=pathfig, format='str')
# # 
opObj33 = procUnitConfObj1.addOperation(name='ParamWriter', optype='other')
opObj33.addParameter(name='path', value=pathfile)
opObj33.addParameter(name='blocksPerFile', value='1000', format='int')
opObj33.addParameter(name='metadataList',value='type,outputInterval,timeZone',format='list')
opObj33.addParameter(name='dataList',value='data_output,utctime',format='list')
# # opObj25.addParameter(name='mode',value='1,0,0',format='intlist')

controllerObj.start()