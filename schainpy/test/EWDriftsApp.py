import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "EWDrifts Experiment Test"
filename = "ewdrifts.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)

readUnitConfObj = controllerObj.addReadUnit(datatype='Voltage',
                                            path='/Users/dsuarez/Remote/EW_DRIFTS_Sep2012',
                                            startDate='2011/01/01',
                                            endDate='2012/12/31',
                                            startTime='00:00:00',
                                            endTime='23:59:59',
                                            online=0,
                                            walk=0)

procUnitConfObj0 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())

opObj11 = procUnitConfObj0.addOperation(name='ProfileSelector', optype='other')
opObj11.addParameter(name='profileRangeList', value='0,127', format='intlist')

opObj11 = procUnitConfObj0.addOperation(name='filterByHeights')
opObj11.addParameter(name='window', value='3', format='int')

opObj11 = procUnitConfObj0.addOperation(name='Decoder', optype='other')

procUnitConfObj1 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObj0.getId())
procUnitConfObj1.addParameter(name='nFFTPoints', value='128', format='int')
procUnitConfObj1.addParameter(name='pairsList', value='(0,1),(2,3)', format='pairslist')

opObj11 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
opObj11.addParameter(name='n', value='10', format='float')
#opObj11.addParameter(name='timeInterval', value='0.33', format='float')

opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='idfigure', value='1', format='int')
opObj11.addParameter(name='wintitle', value='SpectraPlot', format='str')
#opObj11.addParameter(name='channelList', value='0,6', format='intlist')
opObj11.addParameter(name='zmin', value='30', format='int')
opObj11.addParameter(name='zmax', value='120', format='int')
opObj11.addParameter(name='showprofile', value='1', format='int') 


#opObj11 = procUnitConfObj1.addOperation(name='RTIfromNoise', optype='other')
#opObj11.addParameter(name='idfigure', value='2', format='int')
#opObj11.addParameter(name='timerange', value='10', format='int')
#opObj11.addParameter(name='ymin', value='20', format='int')
#opObj11.addParameter(name='ymax', value='120', format='int')

opObj11 = procUnitConfObj1.addOperation(name='ProfilePlot', optype='other')
opObj11.addParameter(name='idfigure', value='2', format='int')
#opObj11.addParameter(name='wintitle', value='Prof', format='str')
opObj11.addParameter(name='xmin', value='30', format='int')
opObj11.addParameter(name='xmax', value='120', format='int')
 
opObj11 = procUnitConfObj1.addOperation(name='CrossSpectraPlot', optype='other')
opObj11.addParameter(name='idfigure', value='3', format='int')
opObj11.addParameter(name='wintitle', value='CrossSpectraPlot', format='str')
opObj11.addParameter(name='zmin', value='30', format='int')
opObj11.addParameter(name='zmax', value='120', format='int') 
#opObj11.addParameter(name='pairsList', value='(0,2)', format='pairslist')

opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
opObj11.addParameter(name='idfigure', value='4', format='int')
opObj11.addParameter(name='wintitle', value='RTIPLot', format='str')
opObj11.addParameter(name='zmin', value='30', format='int')
opObj11.addParameter(name='zmax', value='120', format='int')
opObj11.addParameter(name='timerange', value='3600', format='int') 
opObj11.addParameter(name='showprofile', value='1', format='int')
opObj11.addParameter(name='save', value='1', format='bool')
opObj11.addParameter(name='figpath', value='/Users/dsuarez/Pictures', format='str')

opObj11 = procUnitConfObj1.addOperation(name='CoherenceMap', optype='other')
opObj11.addParameter(name='idfigure', value='5', format='int')
#opObj11.addParameter(name='pairsList', value='(0,2)', format='pairslist')
opObj11.addParameter(name='timerange', value='300', format='int') 
opObj11.addParameter(name='showprofile', value='1', format='int')

print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()
  
  