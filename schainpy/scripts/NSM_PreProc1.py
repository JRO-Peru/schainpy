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
path = '/media/joscanoa/DATA/DATA/RAW_EXP/MST_meteors_153-155'
pathFigure = '/home/joscanoa/Pictures/NonSpecular'
pathfile = '/home/joscanoa/data/HP_Meteor/MST'

xmax = '24'
xmin = '0'



#------------------------------------------------------------------------------------------------
readUnitConfObj = controllerObj.addReadUnit(datatype='VoltageReader',
                                            path=path,
                                            startDate='2016/06/03',
                                            endDate='2016/06/03',
                                            startTime='00:00:00',
                                            endTime='23:59:59',
                                            online=0,
                                            delay=20,
                                            walk=1,
                                            getblock=0,
#                                             blocktime=10)
                                            blocksize=4096)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')


#--------------------------------------------------------------------------------------------------

procUnitConfObj0 = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())

opObj11 = procUnitConfObj0.addOperation(name='selectChannels')
opObj11.addParameter(name='channelList', value='1,2,3,4', format='intlist')

opObj11 = procUnitConfObj0.addOperation(name='selectHeights')
opObj11.addParameter(name='minHei', value='60', format='float')
# opObj11.addParameter(name='minHei', value='272.5', format='float')
opObj11.addParameter(name='maxHei', value='120', format='float')

opObj11 = procUnitConfObj0.addOperation(name='Decoder', optype='other')

opObj11 = procUnitConfObj0.addOperation(name='CohInt', optype='other')
opObj11.addParameter(name='n', value='2', format='int')
#---------------------------------------------------------------------------------------------------
opObj11 = procUnitConfObj0.addOperation(name='VoltageWriter', optype='other')
opObj11.addParameter(name='path', value=pathfile)
opObj11.addParameter(name='blocksPerFile', value='120', format='int')
opObj11.addParameter(name='profilesPerBlock', value='200', format='int')
#--------------------------------------------------------------------------------------------------

print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()