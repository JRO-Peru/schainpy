import os, sys
#import timeit
import datetime

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *
dt1 = datetime.datetime.now()
desc = "MST-ISR-EEJ Experiment Test"
filename = "mst_blocks.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)

path = '/media/signalchain/HD-PXU2/mst_isr_eej'

figpath = '/home/signalchain/Pictures/mst_isr_eej/mst'

readUnitConfObj = controllerObj.addReadUnit(datatype='VoltageReader',
                                            path=path,
                                            startDate='2014/05/01',
                                            endDate='2014/05/30',
                                            startTime='00:00:00',
                                            endTime='23:59:59',
                                            online=0,
                                            delay=10,
                                            walk=0,
                                            getblock=1)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')

procUnitConfObjMST = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())
      
opObj11 = procUnitConfObjMST.addOperation(name='ProfileSelector', optype='other')
profileIndex =  '0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119'
#profileIndex =  '0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19'
opObj11.addParameter(name='profileList', value=profileIndex, format='intlist')
opObj11.addParameter(name='byblock', value='1', format='bool')
      
opObj11 = procUnitConfObjMST.addOperation(name='Decoder', optype='other')
opObj11.addParameter(name='mode',value='3',format='int')
opObj11.addParameter(name='times',value='10',format='int')
     
opObj11 = procUnitConfObjMST.addOperation(name='CohInt', optype='other')
opObj11.addParameter(name='n', value='20', format='int')
opObj11.addParameter(name='byblock', value='1', format='bool')
       
procUnitConfObjMSTSpectra = controllerObj.addProcUnit(datatype='SpectraProc', inputId=procUnitConfObjMST.getId())
procUnitConfObjMSTSpectra.addParameter(name='nFFTPoints', value='64', format='int')
procUnitConfObjMSTSpectra.addParameter(name='nProfiles', value='64', format='int')
      
opObj11 = procUnitConfObjMSTSpectra.addOperation(name='IncohInt', optype='other')
opObj11.addParameter(name='n', value='2', format='float')
     
opObj11 = procUnitConfObjMSTSpectra.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='id', value='200', format='int')
opObj11.addParameter(name='wintitle', value='MST', format='str')
# # opObj11.addParameter(name='zmin', value='35', format='int')
# # opObj11.addParameter(name='zmax', value='60', format='int')
# # opObj11.addParameter(name='save', value='1', format='int')
opObj11.addParameter(name='figpath', value=figpath, format='str')
opObj11.addParameter(name='wr_period', value='5', format='int')
# # opObj11.addParameter(name='ftp', value='1', format='int')
# # opObj11.addParameter(name='server', value='jro-app.igp.gob.pe', format='str')
# # opObj11.addParameter(name='folder', value='/home/wmaster/graficos', format='str')
# # opObj11.addParameter(name='username', value='wmaster', format='str')
# # opObj11.addParameter(name='password', value='mst2010vhf', format='str')
# # opObj11.addParameter(name='ftp_wei', value='0', format='int')
opObj11.addParameter(name='exp_code', value='19', format='int')
# # opObj11.addParameter(name='sub_exp_code', value='0', format='int')
# # opObj11.addParameter(name='plot_pos', value='0', format='int') 
# #  
opObj11 = procUnitConfObjMSTSpectra.addOperation(name='RTIPlot', optype='other')
opObj11.addParameter(name='id', value='201', format='int')
opObj11.addParameter(name='wintitle', value='MST', format='str')
opObj11.addParameter(name='showprofile', value='0', format='int')
# # opObj11.addParameter(name='xmin', value='0', format='int')
# # opObj11.addParameter(name='xmax', value='24', format='int')
# # opObj11.addParameter(name='zmin', value='35', format='int')
# # opObj11.addParameter(name='zmax', value='60', format='int')
# # opObj11.addParameter(name='save', value='1', format='int')
opObj11.addParameter(name='figpath', value=figpath, format='str')
opObj11.addParameter(name='wr_period', value='5', format='int')
# # opObj11.addParameter(name='ftp', value='1', format='int')
# # opObj11.addParameter(name='server', value='jro-app.igp.gob.pe', format='str')
# # opObj11.addParameter(name='folder', value='/home/wmaster/graficos', format='str')
# # opObj11.addParameter(name='username', value='wmaster', format='str')
# # opObj11.addParameter(name='password', value='mst2010vhf', format='str')
# # opObj11.addParameter(name='ftp_wei', value='0', format='int')
opObj11.addParameter(name='exp_code', value='19', format='int')
# # opObj11.addParameter(name='sub_exp_code', value='0', format='int')
# # opObj11.addParameter(name='plot_pos', value='0', format='int')

opObj11 = procUnitConfObjMSTSpectra.addOperation(name='SendByFTP', optype='other')
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