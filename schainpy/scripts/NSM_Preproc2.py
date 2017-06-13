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
path = '/media/joscanoa/DATA/DATA/RAW_EXP/MST_meteors_153-155'
pathFigure = '/home/joscanoa/Pictures/NonSpecular'
pathfile = '/home/joscanoa/data/HP_Meteor/Met'

tmin = '00:00:00'
tmax = '23:59:59'
xmax = '0'
xmin = '24'



#------------------------------------------------------------------------------------------------
readUnitConfObj = controllerObj.addReadUnit(datatype='VoltageReader',
                                            path=path,
                                            startDate='2016/06/03',
                                            endDate='2016/06/03',
                                            startTime=tmin,
                                            endTime=tmax,
                                            online=0,
                                            delay=20,
                                            walk=1,
                                            getblock=0,
                                            blocktime=60)
#                                             blocksize=12800)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')


#--------------------------------------------------------------------------------------------------

procUnitConfObj0 = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())
# 
opObj11 = procUnitConfObj0.addOperation(name='selectChannels')
opObj11.addParameter(name='channelList', value='4,5,6', format='intlist')
 
opObj11 = procUnitConfObj0.addOperation(name='selectHeights')
opObj11.addParameter(name='minHei', value='257.5', format='float')
# opObj11.addParameter(name='minHei', value='272.5', format='float')
opObj11.addParameter(name='maxHei', value='307.5', format='float')
 
opObj11 = procUnitConfObj0.addOperation(name='Decoder', optype='other')
opObj11.addParameter(name='code', value='1,1,1,1,1,-1,-1,1,1,-1,1,-1,1', format='intlist')
opObj11.addParameter(name='nCode', value='1', format='int')
opObj11.addParameter(name='nBaud', value='13', format='int')
 
opObj11 = procUnitConfObj0.addOperation(name='CohInt', optype='other')
opObj11.addParameter(name='n', value='2', format='int')
# #---------------------------------------------------------------------------------------------------
opObj11 = procUnitConfObj0.addOperation(name='VoltageWriter', optype='other')
opObj11.addParameter(name='path', value=pathfile)
opObj11.addParameter(name='blocksPerFile', value='120', format='int')
opObj11.addParameter(name='profilesPerBlock', value='200', format='int')
#---------------------------------------------------------------------------------------------------

print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()