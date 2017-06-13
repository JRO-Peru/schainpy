import os, sys

path = os.path.split(os.getcwd())[0]
path = os.path.split(path)[0]

sys.path.insert(0, path)

from schainpy.controller import Project

desc = "DBS Experiment Test"
filename = "DBStest.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)

#Experimentos

#2014051    20 Feb 2014
path = '/home/joscanoa/Pictures/NonSpecular/CEDAR/SA/notmedian/meteor'

pathfig = '/home/joscanoa/Pictures/NonSpecular/CEDAR/SA/notmedian/graphic'

pathfile2 = '/home/joscanoa/Pictures/NonSpecular/CEDAR/test1/wind'


tmin = '00:00:00'
tmax = '23:59:59'
xmin = '20'
xmax = '32'



#------------------------------------------------------------------------------------------------
readUnitConfObj = controllerObj.addReadUnit(datatype='HDF5Reader',
                                            path=path,
                                            startDate='2016/06/02',
                                            endDate='2016/06/03',
                                            startTime=tmin,
                                            endTime=tmax,
                                            online=0,
                                            delay=20,
                                            walk=1)
#--------------------------------------------------------------------------------------------------
  
procUnitConfObj2 = controllerObj.addProcUnit(datatype='ParametersProc', inputId=readUnitConfObj.getId())
#  
opObj21 = procUnitConfObj2.addOperation(name='WindProfiler', optype='other')
opObj21.addParameter(name='technique', value='Meteors1', format='str')
 
opObj23 = procUnitConfObj2.addOperation(name='WindProfilerPlot', optype='other')
opObj23.addParameter(name='id', value='2', format='int')
opObj23.addParameter(name='wintitle', value='Wind Profiler', format='str')
opObj23.addParameter(name='save', value='1', format='bool')
opObj23.addParameter(name='figpath', value = pathfig, format='str')
opObj23.addParameter(name='zmin', value='-140', format='int')
opObj23.addParameter(name='zmax', value='140', format='int')
opObj23.addParameter(name='xmin', value=xmin, format='float')
opObj23.addParameter(name='xmax', value=xmax, format='float')
opObj23.addParameter(name='ymin', value='84', format='float')
opObj23.addParameter(name='ymax', value='102', format='float')
# 
# opObj21 = procUnitConfObj2.addOperation(name='NonSpecularMeteorsPlot',optype='other')
# opObj21.addParameter(name='id', value='2', format='int')
# opObj21.addParameter(name='wintitle', value='Non specular', format='str')
# opObj21.addParameter(name='save', value='1', format='bool')
# opObj21.addParameter(name='figpath', value = pathFigure, format='str')
# opObj21.addParameter(name='SNRmin', value='-10', format='float')
# opObj21.addParameter(name='SNRmax', value='20', format='float')
# opObj21.addParameter(name='cmin', value='0.5', format='float')
# opObj21.addParameter(name='vmax', value='100', format='float')
# opObj21.addParameter(name='vmin', value='-100', format='float')
  
# opObj24 = procUnitConfObj2.addOperation(name='HDF5Writer', optype='other')
# opObj24.addParameter(name='path', value=pathfile2)
# opObj24.addParameter(name='blocksPerFile', value='60', format='int')
# opObj24.addParameter(name='metadataList',value='type,heightList,outputInterval,timeZone',format='list')
# opObj24.addParameter(name='dataList',value='data_output,utctime,utctimeInit',format='list')
# # # opObj12.addParameter(name='mode',value='2',format='int')
#--------------------------------------------------------------------------------------------------

print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()