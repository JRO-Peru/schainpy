import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "EWDrifts Experiment Test"
filename = "ewdrifts.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)

readUnitConfObj = controllerObj.addReadUnit(datatype='Voltage',
                                            path='/remote/puma/2012_12/EW_Drifts+Faraday+Imaging/Imaging',
                                            startDate='2012/12/19',
                                            endDate='2012/12/21',
                                            startTime='17:00:00',
                                            endTime='23:59:59',
                                            online=0,
                                            walk=1)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')

######################## IMAGING #############################################
#procUnitConfObj0 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())
#
#opObj11 = procUnitConfObj0.addOperation(name='ProfileSelector', optype='other')
#opObj11.addParameter(name='profileRangeList', value='0,39', format='intlist')
#
#opObj11 = procUnitConfObj0.addOperation(name='Decoder', optype='other')

#opObj11 = procUnitConfObj0.addOperation(name='selectHeights')
#opObj11.addParameter(name='minHei', value='300', format='float')
#opObj11.addParameter(name='maxHei', value='600', format='float')

#procUnitConfObj1 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObj0.getId())
#procUnitConfObj1.addParameter(name='nFFTPoints', value='8', format='int')
#procUnitConfObj1.addParameter(name='pairsList', value='(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(0,7), \
#							(1,2),(1,3),(1,4),(1,5),(1,6),(1,7), \
#							(2,3),(2,4),(2,5),(2,6),(2,7), \
#							(3,4),(3,5),(3,6),(3,7), \
#							(4,5),(4,6),(4,7), \
#							(5,6),(5,7), \
#							(6,7)', \
#							format='pairslist')

#opObj11 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
#opObj11.addParameter(name='n', value='5', format='float')

#opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
#opObj11.addParameter(name='idfigure', value='10', format='int')
#opObj11.addParameter(name='wintitle', value='SpectraPlot', format='str')
#opObj11.addParameter(name='zmin', value='30', format='int')
#opObj11.addParameter(name='zmax', value='50', format='int')
#opObj11.addParameter(name='showprofile', value='1', format='int') 

#opObj11 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
#opObj11.addParameter(name='n', value='10', format='float')

#opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
#opObj11.addParameter(name='idfigure', value='11', format='int')
#opObj11.addParameter(name='wintitle', value='SpectraPlot', format='str')
#opObj11.addParameter(name='zmin', value='30', format='int')
#opObj11.addParameter(name='zmax', value='50', format='int')
#opObj11.addParameter(name='showprofile', value='1', format='int') 
#opObj11.addParameter(name='save', value='1', format='int')
#opObj11.addParameter(name='figpath', value='/media/datos/IMAGING/IMAGING/graphs', format='str')

#opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
#opObj11.addParameter(name='idfigure', value='100', format='int')
#opObj11.addParameter(name='wintitle', value='RTIPLot', format='str')
#opObj11.addParameter(name='zmin', value='30', format='int')
#opObj11.addParameter(name='zmax', value='50', format='int')
#opObj11.addParameter(name='xmin', value='17', format='float')
#opObj11.addParameter(name='xmax', value='22', format='float')
#opObj11.addParameter(name='save', value='1', format='int')
#opObj11.addParameter(name='figfile', value='rti-imaging.png', format='str')
#opObj11.addParameter(name='figpath', value='/media/datos/IMAGING/IMAGING/graphs', format='str')
#opObj11.addParameter(name='ftp', value='1', format='int')
#opObj11.addParameter(name='ftpratio', value='3', format='int')

#opObj11 = procUnitConfObj1.addOperation(name='CrossSpectraPlot', optype='other')
#opObj11.addParameter(name='idfigure', value='13', format='int')
#opObj11.addParameter(name='wintitle', value='CrossSpectraPlot', format='str')
#opObj11.addParameter(name='zmin', value='30', format='int')
#opObj11.addParameter(name='zmax', value='50', format='int') 
#opObj11.addParameter(name='save', value='1', format='bool')
#opObj11.addParameter(name='figpath', value='/media/datos/IMAGING/IMAGING/graphs', format='str')

#opObj11 = procUnitConfObj1.addOperation(name='CoherenceMap', optype='other')
#opObj11.addParameter(name='idfigure', value='101', format='int')
#opObj11.addParameter(name='wintitle', value='Coherence', format='str')
#opObj11.addParameter(name='zmin', value='30', format='int')
#opObj11.addParameter(name='zmax', value='50', format='int')
#opObj11.addParameter(name='xmin', value='17', format='float')
#opObj11.addParameter(name='xmax', value='22', format='float')
#opObj11.addParameter(name='save', value='1', format='int')
#opObj11.addParameter(name='figfile', value='coherence-imaging.png', format='str')
#opObj11.addParameter(name='figpath', value='/media/datos/IMAGING/IMAGING/graphs', format='str')
#opObj11.addParameter(name='ftp', value='1', format='int')
#opObj11.addParameter(name='ftpratio', value='3', format='int')

#opObj11 = procUnitConfObj1.addOperation(name='SpectraWriter', optype='other')
#opObj11.addParameter(name='path', value='/media/datos/IMAGING/IMAGING2')
#opObj11.addParameter(name='blocksPerFile', value='10', format='int')

##################### EW - DRIFT ##############################################
procUnitConfObj0 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())

opObj11 = procUnitConfObj0.addOperation(name='ProfileSelector', optype='other')
opObj11.addParameter(name='profileRangeList', value='40,167', format='intlist')

opObj11 = procUnitConfObj0.addOperation(name='filterByHeights')
opObj11.addParameter(name='window', value='36', format='int')

#opObj11 = procUnitConfObj0.addOperation(name='selectHeights')
#opObj11.addParameter(name='minHei', value='200', format='float')
#opObj11.addParameter(name='maxHei', value='700', format='float')

opObj11 = procUnitConfObj0.addOperation(name='Decoder', optype='other')
opObj11.addParameter(name='code', value='1,1,-1,-1,-1,1', format='floatlist')
opObj11.addParameter(name='nCode', value='2', format='int')
opObj11.addParameter(name='nBaud', value='3', format='int')

#opObj11 = procUnitConfObj0.addOperation(name='CohInt', optype='other')
#opObj11.addParameter(name='n', value='1', format='float')

procUnitConfObj1 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObj0.getId())
procUnitConfObj1.addParameter(name='nFFTPoints', value='8', format='int')
procUnitConfObj1.addParameter(name='pairsList', value='(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(0,7), \
							(1,2),(1,3),(1,4),(1,5),(1,6),(1,7), \
							(2,3),(2,4),(2,5),(2,6),(2,7), \
							(3,4),(3,5),(3,6),(3,7), \
							(4,5),(4,6),(4,7), \
							(5,6),(5,7), \
							(6,7)', \
							format='pairslist')

opObj11 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
opObj11.addParameter(name='n', value='16', format='float')

#opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
#opObj11.addParameter(name='idfigure', value='30', format='int')
#opObj11.addParameter(name='wintitle', value='SpectraPlot', format='str')
#opObj11.addParameter(name='zmin', value='40', format='int')
#opObj11.addParameter(name='zmax', value='100', format='int')
#opObj11.addParameter(name='channelList', value='0,1,2', format='intlist') 
#opObj11.addParameter(name='showprofile', value='1', format='int') 
#opObj11.addParameter(name='save', value='1', format='bool')
#opObj11.addParameter(name='figpath', value='/mnt/Datos/PROCDATA/IMAGING/EW-DRIFT/graphs', format='str')

#opObj11 = procUnitConfObj1.addOperation(name='CrossSpectraPlot', optype='other')
#opObj11.addParameter(name='idfigure', value='3', format='int')
#opObj11.addParameter(name='wintitle', value='CrossSpectraPlot', format='str')
#opObj11.addParameter(name='zmin', value='45', format='int')
#opObj11.addParameter(name='zmax', value='100', format='int') 
#opObj11.addParameter(name='save', value='1', format='bool')
#opObj11.addParameter(name='figpath', value='/mnt/Datos/PROCDATA/IMAGING/EW-DRIFT/graphs', format='str')

#opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
#opObj11.addParameter(name='idfigure', value='20', format='int')
#opObj11.addParameter(name='wintitle', value='RTIPLot', format='str')
#opObj11.addParameter(name='zmin', value='40', format='int')
#opObj11.addParameter(name='zmax', value='100', format='int')
#opObj11.addParameter(name='xmin', value='17', format='int')
#opObj11.addParameter(name='xmax', value='22', format='int')
#opObj11.addParameter(name='channelList', value='0', format='intlist')  
#opObj11.addParameter(name='showprofile', value='0', format='int')
#opObj11.addParameter(name='save', value='1', format='int')
#opObj11.addParameter(name='figpath', value='/mnt/Datos/PROCDATA/IMAGING/EW-DRIFT/graphs', format='str')

opObj11 = procUnitConfObj1.addOperation(name='SpectraWriter', optype='other')
opObj11.addParameter(name='path', value='/mnt/Datos/PROCDATA/IMAGING/EW-DRIFT')
opObj11.addParameter(name='blocksPerFile', value='200', format='int')

print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()
  
  
