import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "EWDrifts Experiment Test"
filename = "ewdrifts2.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)

path='/remote/ewdrifts/RAW_EXP/EW_DRIFT_FARADAY/EW_Drift'


path = '/home/signalchain/Puma/2014_07/EW_Drift'

readUnitConfObj = controllerObj.addReadUnit(datatype='VoltageReader',
                                            path=path,
                                            startDate='2014/07/01',
                                            endDate='2014/07/30',
                                            startTime='00:00:00',
                                            endTime='23:59:59',
                                            online=0,
                                            delay=5,
                                            walk=0)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')

procUnitConfObj0 = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())

opObj11 = procUnitConfObj0.addOperation(name='ProfileSelector', optype='other')
opObj11.addParameter(name='profileRangeList', value='0,127', format='intlist')
 
opObj11 = procUnitConfObj0.addOperation(name='filterByHeights')
opObj11.addParameter(name='window', value='3', format='int')
  
opObj11 = procUnitConfObj0.addOperation(name='Decoder', optype='other')
 
procUnitConfObj1 = controllerObj.addProcUnit(datatype='SpectraProc', inputId=procUnitConfObj0.getId())
procUnitConfObj1.addParameter(name='nFFTPoints', value='128', format='int')
procUnitConfObj1.addParameter(name='nProfiles', value='128', format='int')
 
 
opObj11 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
opObj11.addParameter(name='timeInterval', value='60', format='float')

opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='id', value='100', format='int')
opObj11.addParameter(name='wintitle', value='SpectraPlot', format='str')
# #opObj11.addParameter(name='channelList', value='0,1,2,3', format='intlist') 
# # opObj11.addParameter(name='zmin', value='0', format='int')
# # opObj11.addParameter(name='zmax', value='100', format='int')
# opObj11.addParameter(name='showprofile', value='0', format='int') 
# opObj11.addParameter(name='save', value='1', format='bool')
# opObj11.addParameter(name='figpath', value='/Users/dsuarez/Pictures/tr', format='str')
# 
# 
# opObj11 = procUnitConfObj1.addOperation(name='Noise', optype='other')
# opObj11.addParameter(name='id', value='101', format='int')
# opObj11.addParameter(name='wintitle', value='TR800KW', format='str')
# opObj11.addParameter(name='xmin', value='10', format='float')
# opObj11.addParameter(name='xmax', value='11.5', format='float') 
# opObj11.addParameter(name='ymin', value='55', format='float')
# opObj11.addParameter(name='ymax', value='65', format='float') 
# opObj11.addParameter(name='save', value='1', format='bool')
# opObj11.addParameter(name='figpath', value='/Users/dsuarez/Pictures/tr', format='str')

#
#opObj11 = procUnitConfObj1.addOperation(name='PowerProfilePlot', optype='other')
#opObj11.addParameter(name='id', value='2', format='int')
#opObj11.addParameter(name='channelList', value='0,1,2,3', format='intlist') 
#opObj11.addParameter(name='save', value='1', format='bool')
#opObj11.addParameter(name='figpath', value='/home/dsuarez/Pictures/EW_DRIFTS_2012_DEC', format='str')
##opObj11.addParameter(name='xmin', value='10', format='int')
##opObj11.addParameter(name='xmax', value='40', format='int')
#
# opObj11 = procUnitConfObj1.addOperation(name='CrossSpectraPlot', optype='other')
# opObj11.addParameter(name='id', value='3', format='int')
# opObj11.addParameter(name='wintitle', value='CrossSpectraPlot', format='str')
# #opObj11.addParameter(name='save', value='1', format='bool')
# #opObj11.addParameter(name='figpath', value='/home/dsuarez/Pictures/EW_DRIFTS_2012_DEC', format='str')
# ##opObj11.addParameter(name='zmin', value='10', format='int')
# ##opObj11.addParameter(name='zmax', value='40', format='int') 
# ##opObj11.addParameter(name='save', value='1', format='bool')
# ##opObj11.addParameter(name='figpath', value='/home/dsuarez/Pictures/cross_spc', format='str')
# opObj11.addParameter(name='zmin', value='20', format='int')
# opObj11.addParameter(name='zmax', value='40', format='int')
# opObj11.addParameter(name='save', value='1', format='bool')
# opObj11.addParameter(name='figpath', value='/home/dsuarez/Pictures/ew_drifts_mz', format='str')
# 
# # 
# opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
# opObj11.addParameter(name='id', value='102', format='int')
# opObj11.addParameter(name='wintitle', value='RTIPLot', format='str')
# opObj11.addParameter(name='xmin', value='10', format='float')
# opObj11.addParameter(name='xmax', value='11.5', format='float') 
# # opObj11.addParameter(name='zmin', value='20', format='int')
# # opObj11.addParameter(name='zmax', value='40', format='int')
# # #opObj11.addParameter(name='channelList', value='0,1,2,3', format='intlist') 
# # #opObj11.addParameter(name='timerange', value='86400', format='int') 
# opObj11.addParameter(name='showprofile', value='0', format='int')
# opObj11.addParameter(name='save', value='1', format='bool')
# opObj11.addParameter(name='figpath', value='/Users/dsuarez/Pictures/tr', format='str')

print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()
  
  
