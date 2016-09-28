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

#Verificar
path= os.path.join(os.environ['HOME'],'Pictures/last_campaign/meteor')
pathfile2 = os.path.join(os.environ['HOME'],'Pictures/last_campaign/winds')    
pathfig = os.path.join(os.environ['HOME'],'Pictures/last_campaign/graphics')

startTime = '00:00:00'
endTime = '23:59:59'
xmin ='0.0'
xmax = '24.0'
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
#------------------------------------------------------------------------------------------------
readUnitConfObj = controllerObj.addReadUnit(datatype='ParamReader',
                                            path=path,
                                            startDate='2016/06/02',
                                            endDate='2017/06/03',
                                            startTime=startTime,
                                            endTime=endTime,
                                            walk=1)
#--------------------------------------------------------------------------------------------------

procUnitConfObj1 = controllerObj.addProcUnit(datatype='ParametersProc', inputId=readUnitConfObj.getId())
opObj10 = procUnitConfObj1.addOperation(name='CorrectMeteorPhases')
opObj10.addParameter(name='phaseOffsets', value='3.4,-3.6,19.4,0.1', format='floatlist')

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
# opObj12.addParameter(name='zmin_ver', value='-0.8', format='float')
# opObj12.addParameter(name='zmax_ver', value='0.8', format='float')
# opObj23.addParameter(name='SNRmin', value='-10', format='int')
# opObj23.addParameter(name='SNRmax', value='60', format='int')
# opObj23.addParameter(name='SNRthresh', value='0', format='float')
opObj23.addParameter(name='xmin', value=xmin, format='float')
opObj23.addParameter(name='xmax', value=xmax, format='float')
opObj23.addParameter(name='ymin', value='70', format='float')
opObj23.addParameter(name='ymax', value='110', format='float')
# opObj23.addParameter(name='ftp', value='1', format='int')
# opObj23.addParameter(name='exp_code', value='15', format='int')
# opObj23.addParameter(name='sub_exp_code', value='1', format='int') 
 
# opObj24 = procUnitConfObj1.addOperation(name='HDF5Writer', optype='other')
# opObj24.addParameter(name='path', value=pathfile2)
# opObj24.addParameter(name='blocksPerFile', value='1000', format='int')
# opObj24.addParameter(name='metadataList',value='type,outputInterval,heightList,timeZone',format='list')
# opObj24.addParameter(name='dataList',value='data_output,utctime,utctimeInit',format='list')

#--------------------------------------------------------------------------------------------------

print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()