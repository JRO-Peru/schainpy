import os, sys
#import timeit
import datetime

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *
dt1 = datetime.datetime.now()
desc = "MST-ISR-EEJ Experiment Test"
filename = "eej_blocks.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)

path = '/media/signalchain/HD-PXU2/mst_isr_eej'
path = '/media/data/DATA/MST_ISR_EEJ'

figpath = '/home/signalchain/Pictures/mst_isr_eej/eej'
figpath = '/media/DATA/mst_isr_eej/eej'

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
# ################ EEJ ####################################
procUnitConfObjEEJ = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())
    
opObj11 = procUnitConfObjEEJ.addOperation(name='ProfileSelector', optype='other')
opObj11.addParameter(name='profileRangeList', value='120,183', format='intlist')
opObj11.addParameter(name='byblock', value='1', format='bool')
    
opObj11 = procUnitConfObjEEJ.addOperation(name='Decoder', optype='other')
opObj11.addParameter(name='code', value='1,-1', format='floatlist')
opObj11.addParameter(name='nCode', value='2', format='int')
opObj11.addParameter(name='nBaud', value='1', format='int')
opObj11.addParameter(name='mode', value='3', format='int')
opObj11.addParameter(name='times', value='32', format='int') 
   
# opObj11 = procUnitConfObjEEJ.addOperation(name='CohInt', optype='other')
# opObj11.addParameter(name='n', value='2', format='int')
    
procUnitConfObjEEJSpecta = controllerObj.addProcUnit(datatype='SpectraProc', inputId=procUnitConfObjEEJ.getId())
procUnitConfObjEEJSpecta.addParameter(name='nFFTPoints', value='64', format='int')
procUnitConfObjEEJSpecta.addParameter(name='nProfiles', value='64', format='int')
    
opObj11 = procUnitConfObjEEJSpecta.addOperation(name='IncohInt', optype='other')
#opObj11.addParameter(name='timeInterval', value='10', format='float')
opObj11.addParameter(name='n', value='36', format='float')
   
opObj11 = procUnitConfObjEEJSpecta.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='id', value='100', format='int')
opObj11.addParameter(name='wintitle', value='EEJ', format='str')
opObj11.addParameter(name='zmin', value='20', format='int')
opObj11.addParameter(name='zmax', value='40', format='int')# opObj11.addParameter(name='ftp', value='1', format='int')
# opObj11.addParameter(name='zmin', value='20', format='int')
# opObj11.addParameter(name='zmax', value='60', format='int')# opObj11.addParameter(name='ftp', value='1', format='int')
opObj11.addParameter(name='save', value='1', format='int')
opObj11.addParameter(name='figpath', value=figpath, format='str')
opObj11.addParameter(name='wr_period', value='5', format='int')
# opObj11.addParameter(name='ftp_wei', value='0', format='int')
opObj11.addParameter(name='exp_code', value='22', format='int')
# opObj11.addParameter(name='sub_exp_code', value='0', format='int')
# opObj11.addParameter(name='plot_pos', value='0', format='int') 
 
 
opObj11 = procUnitConfObjEEJSpecta.addOperation(name='RTIPlot', optype='other')
opObj11.addParameter(name='id', value='101', format='int')
opObj11.addParameter(name='wintitle', value='EEJ', format='str')
opObj11.addParameter(name='showprofile', value='0', format='int')
#opObj11.addParameter(name='zmin', value='20', format='int')
#opObj11.addParameter(name='zmax', value='40', format='int')
opObj11.addParameter(name='xmin', value='0', format='int')
opObj11.addParameter(name='xmax', value='24', format='int')
# opObj11.addParameter(name='save', value='1', format='int')
opObj11.addParameter(name='figpath', value=figpath, format='str')
opObj11.addParameter(name='wr_period', value='5', format='int')
# opObj11.addParameter(name='ftp_wei', value='0', format='int')
opObj11.addParameter(name='exp_code', value='22', format='int')
# opObj11.addParameter(name='sub_exp_code', value='0', format='int')
# opObj11.addParameter(name='plot_pos', value='0', format='int')

opObj11 = procUnitConfObjEEJSpecta.addOperation(name='SendByFTP', optype='other')
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