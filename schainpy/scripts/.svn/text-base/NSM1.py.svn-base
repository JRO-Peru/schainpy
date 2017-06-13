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

# pathfile = '/home/joscanoa/data/HP_Meteor/MST'
path = '/home/joscanoa/data/HP_Meteor/MST'
# path = '/media/joscanoa/DATA/DATA/RAW_EXP/MST_meteors_153-155'
pathfig = '/home/joscanoa/Pictures/NonSpecular/CEDAR/DBS/graphic'
pathfile1 = '/home/joscanoa/Pictures/NonSpecular/CEDAR/DBS/meteor'

xmax = '8'
xmin = '6'



#------------------------------------------------------------------------------------------------
readUnitConfObj = controllerObj.addReadUnit(datatype='VoltageReader',
                                            path=path,
                                            startDate='2016/06/02',
                                            endDate='2016/06/03',
                                            startTime='21:00:00',
                                            endTime='08:00:00',
                                            online=0,
                                            delay=20,
                                            walk=1,
                                            getblock=1,
                                            blocktime=120)
#                                             blocksize=4096)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')


#--------------------------------------------------------------------------------------------------

procUnitConfObj0 = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())

# opObj11 = procUnitConfObj0.addOperation(name='selectChannels')
# opObj11.addParameter(name='channelList', value='0,1,2,3', format='intlist')
#  
# opObj11 = procUnitConfObj0.addOperation(name='selectHeights')
# opObj11.addParameter(name='minHei', value='60', format='float')
# # opObj11.addParameter(name='minHei', value='272.5', format='float')
# opObj11.addParameter(name='maxHei', value='130', format='float')
#  
# opObj11 = procUnitConfObj0.addOperation(name='Decoder', optype='other')
#  
# opObj11 = procUnitConfObj0.addOperation(name='CohInt', optype='other')
# opObj11.addParameter(name='n', value='2', format='int')
# # opObj11.addParameter(name='n', value='16', format='int')
#  
# #---------------------------------------------------------------------------------------------------
# opObj11 = procUnitConfObj0.addOperation(name='VoltageWriter', optype='other')
# opObj11.addParameter(name='path', value=pathfile)
# opObj11.addParameter(name='blocksPerFile', value='120', format='int')
# opObj11.addParameter(name='profilesPerBlock', value='200', format='int')

#---------------------------------------------------------------------------------------------------

# procUnitConfObj1 = controllerObj.addProcUnit(datatype='SpectraProc', inputId=procUnitConfObj0.getId())
# procUnitConfObj1.addParameter(name='nFFTPoints', value='64', format='int')
# procUnitConfObj1.addParameter(name='nProfiles', value='64', format='int')
#  
# opObj11 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
# opObj11.addParameter(name='n', value='15', format='int')
# # 
# opObj14 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
# opObj14.addParameter(name='id', value='1', format='int')
# opObj14.addParameter(name='wintitle', value='spc', format='str')
# opObj14.addParameter(name='save', value='1', format='bool')
# opObj14.addParameter(name='figpath', value=pathFigure, format='str')
# # opObj14.addParameter(name='zmin', value='14', format='int')
# # opObj14.addParameter(name='zmax', value='60', format='int')
# opObj14.addParameter(name='xaxis', value='velocity', format='str')
#  
# opObj15 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
# opObj15.addParameter(name='id', value='2', format='int')
# opObj15.addParameter(name='wintitle', value='RTI Plot', format='str')
# opObj15.addParameter(name='save', value='1', format='bool')
# opObj15.addParameter(name='figpath', value = pathFigure, format='str')
# # opObj15.addParameter(name='timerange', value='600', format='float')
# opObj15.addParameter(name='xmin', value=xmin, format='float')
# opObj15.addParameter(name='xmax', value=xmax, format='float')
# # opObj15.addParameter(name='zmin', value='14', format='int')
# # opObj15.addParameter(name='zmax', value='60', format='int')

#--------------------------------------------------------------------------------------------------

procUnitConfObj1 = controllerObj.addProcUnit(datatype='CorrelationProc', inputId=procUnitConfObj0.getId())
procUnitConfObj1.addParameter(name='lags', value='0,1,2', format='intlist')
procUnitConfObj1.addParameter(name='fullBuffer', value='1', format='bool')
procUnitConfObj1.addParameter(name='nAvg', value='32', format='int')
 
procUnitConfObj2 = controllerObj.addProcUnit(datatype='ParametersProc', inputId=procUnitConfObj1.getId())
opObj20 = procUnitConfObj2.addOperation(name='NonSpecularMeteorDetection')
opObj20.addParameter(name='mode', value='DBS', format='str')
opObj20.addParameter(name='allData', value='0', format='bool')
# 
opObj21 = procUnitConfObj2.addOperation(name='NSMeteorDetection2Plot',optype='other')
opObj21.addParameter(name='id', value='2', format='int')
opObj21.addParameter(name='wintitle', value='Non specular', format='str')
opObj21.addParameter(name='save', value='1', format='bool')
opObj21.addParameter(name='figpath', value = pathfig, format='str')
opObj21.addParameter(name='SNRmin', value='-10', format='int')
opObj21.addParameter(name='SNRmax', value='30', format='int')
opObj21.addParameter(name='vmin', value='-50', format='int')
opObj21.addParameter(name='vmax', value='50', format='int')
opObj21.addParameter(name='mode', value='DBS', format='str')

opObj22 = procUnitConfObj2.addOperation(name='HDF5Writer', optype='other')
opObj22.addParameter(name='path', value=pathfile1)
opObj22.addParameter(name='blocksPerFile', value='80', format='int')
opObj22.addParameter(name='metadataList',value='type,heightList,abscissaList,paramInterval,timeZone,groupList',format='list')
opObj22.addParameter(name='dataList',value='data_param,utctime',format='list')
opObj22.addParameter(name='mode',value='2',format='int')
#--------------------------------------------------------------------------------------------------

print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()