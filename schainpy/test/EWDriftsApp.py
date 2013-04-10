import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "EWDrifts Experiment Test"
filename = "ewdrifts2.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)

path='/remote/ewdrifts/RAW_EXP/EW_DRIFT_FARADAY/EW_Drift'

path = '/home/dsuarez/.gvfs/data_f on 10.10.20.2/RAW_EXP/DIFFERENTIAL_PHASE'

readUnitConfObj = controllerObj.addReadUnit(datatype='Voltage',
                                            path=path,
                                            startDate='2013/01/11',
                                            endDate='2013/12/12',
                                            startTime='00:00:00',
                                            endTime='23:59:59',
                                            set=29,
                                            online=1,
                                            delay=5,
                                            walk=0)

procUnitConfObj0 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())

opObj11 = procUnitConfObj0.addOperation(name='ProfileSelector', optype='other')
opObj11.addParameter(name='profileRangeList', value='0,127', format='intlist')

opObj11 = procUnitConfObj0.addOperation(name='filterByHeights')
opObj11.addParameter(name='window', value='15', format='int')

opObj11 = procUnitConfObj0.addOperation(name='Decoder', optype='other')
opObj11.addParameter(name='code', value='1,-1', format='floatlist')
opObj11.addParameter(name='nCode', value='2', format='int')
opObj11.addParameter(name='nBaud', value='1', format='int')

procUnitConfObj1 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObj0.getId())
procUnitConfObj1.addParameter(name='nFFTPoints', value='128', format='int')
procUnitConfObj1.addParameter(name='pairsList', value='(0,1)', format='pairslist')

opObj11 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
opObj11.addParameter(name='timeInterval', value='0.5', format='float')

opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='idfigure', value='100', format='int')
opObj11.addParameter(name='wintitle', value='SpectraPlot', format='str')
#opObj11.addParameter(name='channelList', value='0,1,2,3', format='intlist') 
opObj11.addParameter(name='zmin', value='20', format='int')
opObj11.addParameter(name='zmax', value='40', format='int')
#opObj11.addParameter(name='showprofile', value='1', format='int') 
#opObj11.addParameter(name='save', value='1', format='bool')
#opObj11.addParameter(name='figpath', value='/home/dsuarez/Pictures/EW_DRIFTS_2012_DEC', format='str')
opObj11.addParameter(name='save', value='1', format='bool')
opObj11.addParameter(name='figpath', value='/home/dsuarez/Pictures/ew_drifts_mz', format='str')



#
#opObj11 = procUnitConfObj1.addOperation(name='PowerProfilePlot', optype='other')
#opObj11.addParameter(name='idfigure', value='2', format='int')
#opObj11.addParameter(name='channelList', value='0,1,2,3', format='intlist') 
#opObj11.addParameter(name='save', value='1', format='bool')
#opObj11.addParameter(name='figpath', value='/home/dsuarez/Pictures/EW_DRIFTS_2012_DEC', format='str')
##opObj11.addParameter(name='xmin', value='10', format='int')
##opObj11.addParameter(name='xmax', value='40', format='int')
#
opObj11 = procUnitConfObj1.addOperation(name='CrossSpectraPlot', optype='other')
opObj11.addParameter(name='idfigure', value='3', format='int')
opObj11.addParameter(name='wintitle', value='CrossSpectraPlot', format='str')
#opObj11.addParameter(name='save', value='1', format='bool')
#opObj11.addParameter(name='figpath', value='/home/dsuarez/Pictures/EW_DRIFTS_2012_DEC', format='str')
##opObj11.addParameter(name='zmin', value='10', format='int')
##opObj11.addParameter(name='zmax', value='40', format='int') 
##opObj11.addParameter(name='save', value='1', format='bool')
##opObj11.addParameter(name='figpath', value='/home/dsuarez/Pictures/cross_spc', format='str')
opObj11.addParameter(name='zmin', value='20', format='int')
opObj11.addParameter(name='zmax', value='40', format='int')
opObj11.addParameter(name='save', value='1', format='bool')
opObj11.addParameter(name='figpath', value='/home/dsuarez/Pictures/ew_drifts_mz', format='str')


opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
opObj11.addParameter(name='idfigure', value='4', format='int')
opObj11.addParameter(name='wintitle', value='RTIPLot', format='str')
opObj11.addParameter(name='xmin', value='0', format='int')
opObj11.addParameter(name='xmax', value='24', format='int')
opObj11.addParameter(name='zmin', value='20', format='int')
opObj11.addParameter(name='zmax', value='40', format='int')
#opObj11.addParameter(name='channelList', value='0,1,2,3', format='intlist') 
#opObj11.addParameter(name='timerange', value='86400', format='int') 
#opObj11.addParameter(name='showprofile', value='0', format='int')
opObj11.addParameter(name='save', value='1', format='bool')
opObj11.addParameter(name='figpath', value='/home/dsuarez/Pictures/ew_drifts_mz', format='str')

print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()
  
  
