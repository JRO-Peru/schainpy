import os, sys
#import timeit
import datetime

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *
dt1 = datetime.datetime.now()
desc = "MST-ISR-EEJ Experiment Test"
filename = "isr_blocks.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)

path = '/media/signalchain/HD-PXU2/mst_isr_eej'
path = '/media/data/DATA/MST_ISR_EEJ'

figpath = '/home/signalchain/Pictures/mst_isr_eej/isr'
figpath = '/media/DATA/mst_isr_eej/isr'


readUnitConfObj = controllerObj.addReadUnit(datatype='VoltageReader',
                                            path=path,
                                            startDate='2015/01/01',
                                            endDate='2015/12/30',
                                            startTime='00:00:00',
                                            endTime='23:59:59',
                                            online=1,
                                            delay=10,
                                            walk=1,
                                            getblock=1)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')

procUnitConfObjISR = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())
      
opObj11 = procUnitConfObjISR.addOperation(name='ProfileSelector', optype='other')
# profileIndex =  '20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99'
# opObj11.addParameter(name='profileList', value=profileIndex, format='intlist')
opObj11.addParameter(name='profileRangeList', value='20,99', format='intlist')
opObj11.addParameter(name='byblock', value='1', format='bool')
      
# opObj11 = procUnitConfObjISR.addOperation(name='ProfileConcat', optype='other')
# opObj11.addParameter(name='m', value='5', format='int')
   
opObj11 = procUnitConfObjISR.addOperation(name='Reshaper', optype='other') #Esta Operacion opera sobre bloques y reemplaza el ProfileConcat que opera sobre perfiles
opObj11.addParameter(name='shape', value='4,16,6750', format='intlist') # shape = (nchannels, nprofiles, nhieghts)
     
opObj11 = procUnitConfObjISR.addOperation(name='filterByHeights')
opObj11.addParameter(name='window', value='20', format='int')
#opObj11.addParameter(name='axis', value='2', format='int')
    
barker3x1 = '1,1,-1,-1,-1,1'
#barker3x5 = '1,1,1,1,1, 1,1,1,1,1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,1,1,1,1,1'
     
opObj11 = procUnitConfObjISR.addOperation(name='Decoder', optype='other')
opObj11.addParameter(name='code', value=barker3x1, format='floatlist')
opObj11.addParameter(name='nCode', value='2', format='int')
#opObj11.addParameter(name='nBaud', value='15', format='int')
opObj11.addParameter(name='nBaud', value='3', format='int')
opObj11.addParameter(name='mode', value='3', format='int')
opObj11.addParameter(name='times', value='8', format='int') 
opObj11.addParameter(name='osamp', value='5', format='int')
  
    
procUnitConfObjISRSpectra = controllerObj.addProcUnit(datatype='SpectraProc', inputId=procUnitConfObjISR.getId())
procUnitConfObjISRSpectra.addParameter(name='nFFTPoints', value='16', format='int')
procUnitConfObjISRSpectra.addParameter(name='nProfiles', value='16', format='int')
   
opObj11 = procUnitConfObjISRSpectra.addOperation(name='IncohInt', optype='other')
opObj11.addParameter(name='n', value='36', format='float')
   
opObj11 = procUnitConfObjISRSpectra.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='id', value='300', format='int')
opObj11.addParameter(name='zmin', value='23', format='int')
opObj11.addParameter(name='zmax', value='40', format='int')
opObj11.addParameter(name='wintitle', value='ISR', format='str')
opObj11.addParameter(name='figpath', value=figpath, format='str')
opObj11.addParameter(name='wr_period', value='5', format='int')
opObj11.addParameter(name='exp_code', value='20', format='int')

opObj11 = procUnitConfObjISRSpectra.addOperation(name='RTIPlot', optype='other')
opObj11.addParameter(name='id', value='301', format='int')
opObj11.addParameter(name='xmin', value='00', format='int')
opObj11.addParameter(name='xmax', value='24', format='int')
opObj11.addParameter(name='zmin', value='23', format='int')
opObj11.addParameter(name='zmax', value='40', format='int')
opObj11.addParameter(name='wintitle', value='ISR', format='str')
opObj11.addParameter(name='showprofile', value='0', format='int')
opObj11.addParameter(name='figpath', value=figpath, format='str')
opObj11.addParameter(name='wr_period', value='2', format='int')
opObj11.addParameter(name='exp_code', value='20', format='int')


opObj11 = procUnitConfObjISRSpectra.addOperation(name='SendByFTP', optype='other')
opObj11.addParameter(name='ext', value='*.png', format='str')
opObj11.addParameter(name='localfolder', value=figpath, format='str')
opObj11.addParameter(name='remotefolder', value='/home/wmaster/graficos', format='str')
opObj11.addParameter(name='server', value='jro-app.igp.gob.pe', format='str')
opObj11.addParameter(name='username', value='wmaster', format='str')
opObj11.addParameter(name='password', value='mst2010vhf', format='str')
opObj11.addParameter(name='period', value='5', format='int')



print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()

#timeit.timeit('controllerObj.run()', number=2)

controllerObj.run()
#print fib(5)

dt2 = datetime.datetime.now()
print "======================="
print dt2-dt1
print "======================="
