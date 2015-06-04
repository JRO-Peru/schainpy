import os, sys
#import timeit
import datetime

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "150 km Jicamarca January 2015"
filename = "150km_jicamarca.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)

path = '/home/operaciones/150km_jicamarca_january/RAW_EXP/2015_ISR'
#path = '/media/New Volume2/DATA/RAW_EXP/2015_ISR'

figpath = '/home/operaciones/Pictures/150km_jicamarca_january'

readUnitConfObj = controllerObj.addReadUnit(datatype='VoltageReader',
                                            path=path,
                                            startDate='2015/01/14',
                                            endDate='2015/01/30',
                                            startTime='07:40:00',
                                            endTime='23:59:59',
                                            online=1,
                                            delay=10,
                                            walk=1,
                                            nTxs=4)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')

procUnitConfObj0 = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())

opObj11 = procUnitConfObj0.addOperation(name='ProfileSelector', optype='other')
opObj11.addParameter(name='rangeList', value='(1,80),(341,420),(681,760),(1021,1100)', format='multiList')

# opObj11 = procUnitConfObj0.addOperation(name='filterByHeights')
# opObj11.addParameter(name='window', value='1', format='int')
# opObj11.addParameter(name='axis', value='2', format='int')
     
cod7barker="1,1,1,-1,-1,1,-1,1,1,1,-1,-1,1,-1,-1,-1,-1,1,1,-1,1,-1,-1,-1,1,1,-1,1"
# 1,1,1,-1,-1,1,-1
#-1,-1,-1,1,1,-1,1
opObj11 = procUnitConfObj0.addOperation(name='Decoder', optype='other')
opObj11.addParameter(name='code', value=cod7barker, format='floatlist')
opObj11.addParameter(name='nCode', value='4', format='int')
opObj11.addParameter(name='nBaud', value='7', format='int')

opObj11 = procUnitConfObj0.addOperation(name='deFlip')
opObj11.addParameter(name='channelList', value='1,3,5,7', format='intlist')

# cod7barker="1,1,1,-1,-1,1,-1"
# opObj11 = procUnitConfObj0.addOperation(name='Decoder', optype='other')
# opObj11.addParameter(name='code', value=cod7barker, format='intlist')
# opObj11.addParameter(name='nCode', value='1', format='int')
# opObj11.addParameter(name='nBaud', value='7', format='int')

# opObj11 = procUnitConfObj0.addOperation(name='Scope', optype='other')
# opObj11.addParameter(name='id', value='10', format='int')
# opObj11.addParameter(name='wintitle', value='Voltage', format='str')
# opObj11.addParameter(name='zmin', value='40', format='int')
# opObj11.addParameter(name='zmax', value='90', format='int')

#opObj11 = procUnitConfObj0.addOperation(name='Decoder', optype='other')

procUnitConfObj1 = controllerObj.addProcUnit(datatype='SpectraProc', inputId=procUnitConfObj0.getId())
procUnitConfObj1.addParameter(name='nFFTPoints', value='80', format='int')
procUnitConfObj1.addParameter(name='nProfiles', value='80', format='int')
#procUnitConfObj1.addParameter(name='pairsList', value='(3,7),(2,6)', format='pairsList')
procUnitConfObj1.addParameter(name='pairsList', value='(1,0),(3,2),(5,4),(7,6)', format='pairsList')

# 
opObj11 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
opObj11.addParameter(name='timeInterval', value='60', format='float')
# 
# opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
# opObj11.addParameter(name='id', value='2004', format='int')
# opObj11.addParameter(name='wintitle', value='150km_Jicamarca_ShortPulse', format='str')
# #opObj11.addParameter(name='channelList', value='0,1,2,3,45', format='intlist')
# opObj11.addParameter(name='zmin', value='15', format='int')
# opObj11.addParameter(name='zmax', value='45', format='int')
# opObj11.addParameter(name='figpath', value=figpath, format='str')
# opObj11.addParameter(name='exp_code', value='13', format='int')

opObj11 = procUnitConfObj1.addOperation(name='CrossSpectraPlot', optype='other')
opObj11.addParameter(name='id', value='2006', format='int')
opObj11.addParameter(name='wintitle', value='CrossSpectraPlot_ShortPulse', format='str')
opObj11.addParameter(name='coherence_cmap', value='jet', format='str')
opObj11.addParameter(name='phase_cmap', value='jet', format='str')
# opObj11.addParameter(name='ymin', value='0', format='int')
# opObj11.addParameter(name='ymax', value='105', format='int')
opObj11.addParameter(name='zmin', value='15', format='int')
opObj11.addParameter(name='zmax', value='45', format='int')
opObj11.addParameter(name='figpath', value=figpath, format='str')
opObj11.addParameter(name='exp_code', value='13', format='int')

# 
opObj11 = procUnitConfObj1.addOperation(name='CoherenceMap', optype='other')
opObj11.addParameter(name='id', value='102', format='int')
opObj11.addParameter(name='wintitle', value='Coherence', format='str')
opObj11.addParameter(name='phase_cmap', value='jet', format='str')
 
# 
opObj11.addParameter(name='xmin', value='0', format='int')
opObj11.addParameter(name='xmax', value='24', format='int')
opObj11.addParameter(name='figpath', value=figpath, format='str')
# opObj11.addParameter(name='wr_period', value='2', format='int')

  
# opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
# opObj11.addParameter(name='id', value='3005', format='int')
# opObj11.addParameter(name='wintitle', value='150km_Jicamarca_ShortPulse', format='str')
# # opObj11.addParameter(name='xmin', value='20.5', format='float')
# # opObj11.addParameter(name='xmax', value='24', format='float')
# opObj11.addParameter(name='zmin', value='15', format='int')
# opObj11.addParameter(name='zmax', value='45', format='int')
# #opObj11.addParameter(name='channelList', value='0,1,2,3', format='intlist')
# #opObj11.addParameter(name='channelList', value='0,1,2,3,4,5,6,7', format='intlist')
# opObj11.addParameter(name='showprofile', value='0', format='int')
# opObj11.addParameter(name='figpath', value=figpath, format='str')
# opObj11.addParameter(name='exp_code', value='13', format='int')

print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()

#timeit.timeit('controllerObj.run()', number=2)

controllerObj.run()