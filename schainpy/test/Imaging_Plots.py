import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "EWDrifts+Imaging+Faraday Experiments"
filename = "imaging_plots.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)

path = '/media/signalchain/datos/IMAGING/IMAGING/setiembre2014'

readUnitConfObj = controllerObj.addReadUnit(datatype='SpectraReader',
                                            path=path,
                                            startDate='2014/09/22',
                                            endDate='2014/09/22',
                                            startTime='00:30:00',
                                            endTime='23:59:59',
                                            delay=5,
                                            online=0,
                                            walk=1)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')

######################## IMAGING #############################################

procUnitConfObj1 = controllerObj.addProcUnit(datatype='SpectraProc', inputId=readUnitConfObj.getId())

opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='id', value='2000', format='int')
opObj11.addParameter(name='wintitle', value='Imaging', format='str')
opObj11.addParameter(name='zmin', value='15', format='int')
opObj11.addParameter(name='zmax', value='45', format='int')
opObj11.addParameter(name='figpath', value='/home/signalchain/Pictures/imaging', format='str')
opObj11.addParameter(name='exp_code', value='13', format='int')
 
opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
opObj11.addParameter(name='id', value='3001', format='int')
opObj11.addParameter(name='wintitle', value='Imaging', format='str')
opObj11.addParameter(name='xmin', value='20.5', format='float')
opObj11.addParameter(name='xmax', value='24', format='float')
opObj11.addParameter(name='zmin', value='15', format='int')
opObj11.addParameter(name='zmax', value='45', format='int')
opObj11.addParameter(name='channelList', value='0,1,2,3', format='intlist')
opObj11.addParameter(name='showprofile', value='0', format='int')
opObj11.addParameter(name='figpath', value='/home/signalchain/Pictures/imaging', format='str')
opObj11.addParameter(name='exp_code', value='13', format='int')
 
opObj11 = procUnitConfObj1.addOperation(name='CoherenceMap', optype='other')
opObj11.addParameter(name='id', value='2001', format='int')
opObj11.addParameter(name='wintitle', value='Imaging', format='str')
opObj11.addParameter(name='xmin', value='20.5', format='float')
opObj11.addParameter(name='xmax', value='24', format='float')
opObj11.addParameter(name='figpath', value='/home/signalchain/Pictures/imaging', format='str')
opObj11.addParameter(name='exp_code', value='13', format='int')
 
opObj11 = procUnitConfObj1.addOperation(name='SendByFTP', optype='other')
opObj11.addParameter(name='ext', value='*.png', format='str')
opObj11.addParameter(name='localfolder', value='/home/signalchain/Pictures/imaging', format='str')
opObj11.addParameter(name='remotefolder', value='/home/wmaster/graficos', format='str')
opObj11.addParameter(name='server', value='jro-app.igp.gob.pe', format='str')
opObj11.addParameter(name='username', value='wmaster', format='str')
opObj11.addParameter(name='password', value='mst2010vhf', format='str')


print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()
  
  
