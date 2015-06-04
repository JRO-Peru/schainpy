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
                                            startDate='2015/01/13',
                                            endDate='2015/01/30',
                                            startTime='07:55:00',
                                            endTime='23:59:59',
                                            online=0,
                                            delay=10,
                                            walk=1)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')

procUnitConfObj0 = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())
a=[]
for i in range(85):
    if i>20:
        a.append(i)      
for i in range(170):
    if i>105:
        a.append(i)  
for i in range(255):   
    if i>190:
       a.append(i)
for i in range(340):   
    if 339>i>275:
       a.append(i) 
    if i==339:
        a.append(i)
        
b= str(a) 
profileIndex =   b[1:][:-1]

opObj11 = procUnitConfObj0.addOperation(name='ProfileSelector', optype='other')
#profileIndex =  '0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19'
opObj11.addParameter(name='profileList', value=profileIndex, format='intlist')


# opObj11 = procUnitConfObj0.addOperation(name='ProfileSelector', optype='other')
# opObj11.addParameter(name='profileRangeList', value='21,84', format='intlist')


binary28="1,1,-1,1,1,-1,1,-1,-1,1,-1,-1,-1,1,-1,-1,-1,1,-1,-1,-1,1,1,1,1,-1,-1,-1"


CODEB=numpy.array([1,1,-1,1,1,-1,1,-1,-1,1,-1,-1,-1,1,-1,-1,-1,1,-1,-1,-1,1,1,1,1,-1,-1,-1])
x= numpy.array([ CODEB,CODEB,-CODEB,-CODEB])
code= ",".join(map(str,x.flatten()))

opObj11 = procUnitConfObj0.addOperation(name='Decoder', optype='other')
opObj11.addParameter(name='code', value=code, format='intlist')
opObj11.addParameter(name='nCode', value='4', format='int')
opObj11.addParameter(name='nBaud', value='28', format='int')

opObj11 = procUnitConfObj0.addOperation(name='deFlip')
opObj11.addParameter(name='channelList', value='1,3,5,7', format='intlist')

# opObj10 = procUnitConfObj0.addOperation(name='selectHeights')
# opObj10.addParameter(name='minHei', value='50', format='float')
# opObj10.addParameter(name='maxHei', value='150', format='float')
    
# opObj11 = procUnitConfObj0.addOperation(name='CohInt', optype='other')
# opObj11.addParameter(name='n', value='4', format='float')


# opObj11 = procUnitConfObj0.addOperation(name='Scope', optype='other')
# opObj11.addParameter(name='id', value='10', format='int')
# opObj11.addParameter(name='wintitle', value='Voltage', format='str')
# opObj11.addParameter(name='zmin', value='40', format='int')
# opObj11.addParameter(name='zmax', value='90', format='int')

#opObj11 = procUnitConfObj0.addOperation(name='Decoder', optype='other')

procUnitConfObj1 = controllerObj.addProcUnit(datatype='SpectraProc', inputId=procUnitConfObj0.getId())
procUnitConfObj1.addParameter(name='nFFTPoints', value='64', format='int')
procUnitConfObj1.addParameter(name='nProfiles', value='64', format='int')

#procUnitConfObj1.addParameter(name='pairsList', value='(3,7),(2,6)', format='pairsList')
procUnitConfObj1.addParameter(name='pairsList', value='(1,0),(3,2),(5,4),(7,6)', format='pairsList')

opObj11 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
opObj11.addParameter(name='timeInterval', value='60', format='float')

# opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
# opObj11.addParameter(name='id', value='2001', format='int')
# opObj11.addParameter(name='wintitle', value='150km_Jicamarca', format='str')
# #opObj11.addParameter(name='channelList', value='0,1,2,3,45', format='intlist')
# # opObj11.addParameter(name='zmin', value='0', format='int')
# # opObj11.addParameter(name='zmax', value='60', format='int')
# opObj11.addParameter(name='figpath', value=figpath, format='str')
# opObj11.addParameter(name='exp_code', value='13', format='int')

opObj11 = procUnitConfObj1.addOperation(name='CrossSpectraPlot', optype='other')
opObj11.addParameter(name='id', value='2005', format='int')
opObj11.addParameter(name='wintitle', value='CrossSpectraPlot_LongPulse', format='str')
opObj11.addParameter(name='phase_cmap', value='jet', format='str')
opObj11.addParameter(name='zmin', value='20', format='int')
opObj11.addParameter(name='zmax', value='80', format='int')
opObj11.addParameter(name='figpath', value=figpath, format='str')
opObj11.addParameter(name='exp_code', value='13', format='int')
opObj11.addParameter(name='figpath', value=figpath, format='str')
opObj11.addParameter(name='wr_period', value='2', format='int')


opObj11 = procUnitConfObj1.addOperation(name='CoherenceMap', optype='other')
opObj11.addParameter(name='id', value='101', format='int')
opObj11.addParameter(name='wintitle', value='Coherence', format='str')
opObj11.addParameter(name='phase_cmap', value='jet', format='str')

opObj11.addParameter(name='xmin', value='0', format='int')
opObj11.addParameter(name='xmax', value='24', format='int')
opObj11.addParameter(name='figpath', value=figpath, format='str')
opObj11.addParameter(name='wr_period', value='2', format='int')

# opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
# opObj11.addParameter(name='id', value='3002', format='int')
# opObj11.addParameter(name='wintitle', value='150km_Jicamarca_LongPulse', format='str')
# # opObj11.addParameter(name='xmin', value='20.5', format='float')
# # opObj11.addParameter(name='xmax', value='24', format='float')
# opObj11.addParameter(name='zmin', value='20', format='int')
# opObj11.addParameter(name='zmax', value='80', format='int')
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