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

path= os.path.join(os.environ['HOME'],'Pictures/last_campaign/meteor')

pathfile2 = os.path.join(os.environ['HOME'],'Pictures/last_campaign/phase')
pathfig = os.path.join(os.environ['HOME'],'Pictures/last_campaign/graphics')


startTime = '00:00:00'
endTime = '23:59:59'
# endTime = '00:01:01'
xmin ='0'
xmax = '24'
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
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
# #      
opObj31 = procUnitConfObj1.addOperation(name='PhaseCalibration', optype='other')
opObj31.addParameter(name='nHours', value='1', format='float')
opObj31.addParameter(name='hmin', value='60', format='float') 
opObj31.addParameter(name='hmax', value='120', format='float')
# opObj31.addParameter(name='channelPositions', value='(2.5,0),(0,2.5),(0,0),(0,4.5),(-2,0)', format='pairslist')
     
opObj32 = procUnitConfObj1.addOperation(name='PhasePlot', optype='other')
opObj32.addParameter(name='id', value='201', format='int')
opObj32.addParameter(name='wintitle', value='PhaseCalibration', format='str')
opObj32.addParameter(name='save', value='1', format='bool')
opObj32.addParameter(name='xmin', value=xmin, format='float')
opObj32.addParameter(name='xmax', value=xmax, format='float')
opObj32.addParameter(name='ymin', value='-180', format='float')
opObj32.addParameter(name='ymax', value='180', format='float')
opObj32.addParameter(name='figpath', value=pathfig, format='str')
# # 
opObj33 = procUnitConfObj1.addOperation(name='ParamWriter', optype='other')
opObj33.addParameter(name='path', value=pathfile2)
opObj33.addParameter(name='blocksPerFile', value='1000', format='int')
opObj33.addParameter(name='metadataList',value='type,outputInterval,timeZone',format='list')
opObj33.addParameter(name='dataList',value='data_output,utctime',format='list')
# # opObj25.addParameter(name='mode',value='1,0,0',format='intlist')

#--------------------------------------------------------------------------------------------------

print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()