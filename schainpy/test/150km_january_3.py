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

figpath = '/home/operaciones/Pictures/150km_jicamarca_january'

readUnitConfObj = controllerObj.addReadUnit(datatype='VoltageReader',
                                            path=path,
                                            startDate='2015/01/13',
                                            endDate='2015/01/30',
                                            startTime='08:55:00',
                                            endTime='23:59:59',
                                            online=1,
                                            delay=10,
                                            walk=1,
                                            getblock=1)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')

procUnitConfObj0 = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())

# opObj11 = procUnitConfObj0.addOperation(name='ProfileSelector', optype='other')
# opObj11.addParameter(name='profileRangeList', value='0,20', format='intlist')


opObj11 = procUnitConfObj0.addOperation(name='ProfileSelector', optype='other')
# profileIndex =  '20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99'
# opObj11.addParameter(name='profileList', value=profileIndex, format='intlist')
opObj11.addParameter(name='profileRangeList', value='0,20', format='intlist')
opObj11.addParameter(name='byblock', value='1', format='bool')
      
# opObj11 = procUnitConfObjISR.addOperation(name='ProfileConcat', optype='other')
# opObj11.addParameter(name='m', value='5', format='int')
   
opObj11 = procUnitConfObj0.addOperation(name='Reshaper', optype='other') #Esta Operacion opera sobre bloques y reemplaza el ProfileConcat que opera sobre perfiles
opObj11.addParameter(name='shape', value='8,84,140', format='intlist') # shape = (nchannels, nprofiles, nhieghts)


opObj11 = procUnitConfObj0.addOperation(name='ProfileSelector', optype='other')
# profileIndex =  '20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99'
# opObj11.addParameter(name='profileList', value=profileIndex, format='intlist')
opObj11.addParameter(name='profileRangeList', value='1,80', format='intlist')
opObj11.addParameter(name='byblock', value='1', format='bool')

    
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
opObj11.addParameter(name='mode', value='3', format='int')
opObj11.addParameter(name='times', value='20', format='int') 
opObj11.addParameter(name='osamp', value='1', format='int')

 
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
# 
opObj11 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
opObj11.addParameter(name='timeInterval', value='10', format='float')
# 
opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='id', value='2004', format='int')
opObj11.addParameter(name='wintitle', value='150km_Jicamarca_ShortPulse', format='str')
#opObj11.addParameter(name='channelList', value='0,1,2,3,45', format='intlist')
#opObj11.addParameter(name='zmin', value='15', format='int')
#  opObj11.addParameter(name='zmax', value='45', format='int')
opObj11.addParameter(name='figpath', value=figpath, format='str')
opObj11.addParameter(name='exp_code', value='13', format='int')


opObj11 = procUnitConfObj1.addOperation(name='CrossSpectraPlot', optype='other')
opObj11.addParameter(name='id', value='2005', format='int')
opObj11.addParameter(name='wintitle', value='CrossSpectraPlot_ShortPulse', format='str')
opObj11.addParameter(name='figpath', value=figpath, format='str')
opObj11.addParameter(name='exp_code', value='13', format='int')


  
opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
opObj11.addParameter(name='id', value='3005', format='int')
opObj11.addParameter(name='wintitle', value='150km_Jicamarca_ShortPulse', format='str')
# opObj11.addParameter(name='xmin', value='20.5', format='float')
# opObj11.addParameter(name='xmax', value='24', format='float')
# opObj11.addParameter(name='zmin', value='15', format='int')
# opObj11.addParameter(name='zmax', value='45', format='int')
#opObj11.addParameter(name='channelList', value='0,1,2,3', format='intlist')
#opObj11.addParameter(name='channelList', value='0,1,2,3,4,5,6,7', format='intlist')
opObj11.addParameter(name='showprofile', value='0', format='int')
opObj11.addParameter(name='figpath', value=figpath, format='str')
opObj11.addParameter(name='exp_code', value='13', format='int')



print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()

#timeit.timeit('controllerObj.run()', number=2)

controllerObj.run()