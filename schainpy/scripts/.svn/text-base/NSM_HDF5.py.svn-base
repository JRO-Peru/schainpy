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
path = '/home/joscanoa/Pictures/NonSpecular/test/data'
pathFigure = '/home/joscanoa/Pictures/NonSpecular'
pathfile = '/home/joscanoa/Pictures/NonSpecular'

tmin = '00:00:00'
tmax = '23:59:59'
xmax = '24'
xmin = '0'



#------------------------------------------------------------------------------------------------
readUnitConfObj = controllerObj.addReadUnit(datatype='HDF5Reader',
                                            path=path,
                                            startDate='2016/05/29',
                                            endDate='2016/06/29',
                                            startTime=tmin,
                                            endTime=tmax,
                                            online=0,
                                            delay=20,
                                            walk=1)
#                                             blocksize=12800)

# opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')


#--------------------------------------------------------------------------------------------------

procUnitConfObj2 = controllerObj.addProcUnit(datatype='ParametersProc', inputId=readUnitConfObj.getId())
# opObj20 = procUnitConfObj2.addOperation(name='NonSpecularMeteorDetection')
# opObj20.addParameter(name='mode', value='SA', format='str')
# 
opObj21 = procUnitConfObj2.addOperation(name='NonSpecularMeteorsPlot',optype='other')
opObj21.addParameter(name='id', value='2', format='int')
opObj21.addParameter(name='wintitle', value='Non specular', format='str')
opObj21.addParameter(name='save', value='1', format='bool')
opObj21.addParameter(name='figpath', value = pathFigure, format='str')
opObj21.addParameter(name='SNRmin', value='-10', format='float')
opObj21.addParameter(name='cmin', value='0.5', format='float')
opObj21.addParameter(name='vmax', value='100', format='float')
opObj21.addParameter(name='vmin', value='-100', format='float')

# opObj22 = procUnitConfObj2.addOperation(name='HDF5Writer', optype='other')
# opObj22.addParameter(name='path', value=pathfile)
# opObj22.addParameter(name='blocksPerFile', value='1', format='int')
# opObj22.addParameter(name='metadataList',value='type,heightList,paramInterval,timeZone',format='list')
# opObj22.addParameter(name='dataList',value='data_param,utctime',format='list')
# # opObj12.addParameter(name='mode',value='2',format='int')
#--------------------------------------------------------------------------------------------------

print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()