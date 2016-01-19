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

#Experimentos
remotefolder = "/home/wmaster/graficos"
path = '/mnt/jars/noche'
path = '/media/joscanoa/84A65E64A65E5730/soporte/Data/JASMET/JASMET_30'
pathfig = os.path.join(os.environ['HOME'],'Pictures/test')

startTime = '00:00:00'
endTime = '23:59:59'
# endTime = '00:01:01'
xmin ='0'
xmax = '7.0'
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
#------------------------------------------------------------------------------------------------
readUnitConfObj = controllerObj.addReadUnit(datatype='VoltageReader',
                                            path=path,
                                            startDate='2015/11/09',
                                            endDate='2015/11/09',
                                            startTime=startTime,
                                            endTime=endTime,
                                            online=0,
                                            delay=5,
                                            walk=1)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')


#--------------------------------------------------------------------------------------------------

procUnitConfObj0 = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())

opObj00 = procUnitConfObj0.addOperation(name='selectChannels')
opObj00.addParameter(name='channelList', value='0, 1, 2, 3, 4', format='intlist')

opObj01 = procUnitConfObj0.addOperation(name='setRadarFrequency')
opObj01.addParameter(name='frequency', value='30.e6', format='float')
# opObj01.addParameter(name='frequency', value='50.e6', format='float')

# opObj11 = procUnitConfObj0.addOperation(name='Decoder', optype='other')
# opObj11 = procUnitConfObj0.addOperation(name='CohInt', optype='other')
# opObj11.addParameter(name='n', value='2', format='int')
#--------------------------------------------------------------------------------------------------

procUnitConfObj2 = controllerObj.addProcUnit(datatype='SpectraProc', inputId=procUnitConfObj0.getId())
procUnitConfObj2.addParameter(name='nFFTPoints', value='100', format='int')
procUnitConfObj2.addParameter(name='nProfiles', value='100', format='int')
 
opObj21 = procUnitConfObj2.addOperation(name='IncohInt', optype='other')
opObj21.addParameter(name='n', value='40.0', format='float')
 
opObj23 = procUnitConfObj2.addOperation(name='SpectraPlot', optype='other')
opObj23.addParameter(name='id', value='4', format='int')
# opObj14.addParameter(name='wintitle', value='Con interf', format='str')
opObj23.addParameter(name='save', value='1', format='bool')
opObj23.addParameter(name='figpath', value=pathfig, format='str')
opObj23.addParameter(name='zmin', value='35', format='int')
opObj23.addParameter(name='zmax', value='60', format='int')
opObj23.addParameter(name='figpath', value=pathfig, format='str')
opObj23.addParameter(name='ftp', value='1', format='int')
opObj23.addParameter(name='exp_code', value='15', format='int')
opObj23.addParameter(name='sub_exp_code', value='1', format='int')
 
 
opObj22 = procUnitConfObj2.addOperation(name='RTIPlot', optype='other')
opObj22.addParameter(name='id', value='3', format='int')
opObj22.addParameter(name='wintitle', value='RTI Plot', format='str')
opObj22.addParameter(name='save', value='1', format='bool')
opObj22.addParameter(name='figpath', value = pathfig, format='str')
opObj22.addParameter(name='timerange', value = str(7*60*60), format='int')
# opObj22.addParameter(name='xmin', value=xmin, format='float')
# opObj22.addParameter(name='xmax', value=xmax, format='float')
opObj22.addParameter(name='zmin', value='35', format='int')
opObj22.addParameter(name='zmax', value='60', format='int')
opObj22.addParameter(name='figpath', value=pathfig, format='str')
opObj22.addParameter(name='ftp', value='1', format='int')
opObj22.addParameter(name='exp_code', value='15', format='int')
opObj22.addParameter(name='sub_exp_code', value='1', format='int')

#--------------------------------------------------------------------------------------------------
# procUnitConfObj4 = controllerObj.addProcUnit(name='SendToServer')
# procUnitConfObj4.addParameter(name='server', value='jro-app.igp.gob.pe', format='str')
# procUnitConfObj4.addParameter(name='username', value='wmaster', format='str')
# procUnitConfObj4.addParameter(name='password', value='mst2010vhf', format='str')
# procUnitConfObj4.addParameter(name='localfolder', value=pathfig, format='str')
# procUnitConfObj4.addParameter(name='remotefolder', value=remotefolder, format='str')
# procUnitConfObj4.addParameter(name='ext', value='.png', format='str')
# procUnitConfObj4.addParameter(name='period', value=20, format='int')
# procUnitConfObj4.addParameter(name='protocol', value='ftp', format='str')

#--------------------------------------------------------------------------------------------------
print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()