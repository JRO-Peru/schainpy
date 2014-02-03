import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "EWDrifts Experiment Test"
filename = "mstisr3.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)

path='/remote/ewdrifts/RAW_EXP/EW_DRIFT_FARADAY/EW_Drift'

path = '/home/operaciones/.gvfs/data on 10.10.20.13/MST_ISR/d2014007'

path = '/home/cluster/remote/MST_ISR/d2014009'
readUnitConfObj = controllerObj.addReadUnit(datatype='Voltage',
                                            path=path,
                                            startDate='2014/01/09',
                                            endDate='2014/01/09',
                                            startTime='00:00:00',
                                            endTime='23:59:59',
                                            set=0,
                                            online=0,
                                            delay=10,
                                            walk=0)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')

################ EEJ ####################################
procUnitConfObjEEJ = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())
 
opObj11 = procUnitConfObjEEJ.addOperation(name='ProfileSelector', optype='other')
opObj11.addParameter(name='profileRangeList', value='120,183', format='intlist')
 
opObj11 = procUnitConfObjEEJ.addOperation(name='Decoder', optype='other')
opObj11.addParameter(name='code', value='1,-1', format='floatlist')
opObj11.addParameter(name='nCode', value='2', format='int')
opObj11.addParameter(name='nBaud', value='1', format='int')
 
# opObj11 = procUnitConfObjEEJ.addOperation(name='CohInt', optype='other')
# opObj11.addParameter(name='n', value='2', format='int')
 
procUnitConfObjEEJSpecta = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObjEEJ.getId())
procUnitConfObjEEJSpecta.addParameter(name='nFFTPoints', value='64', format='int')
procUnitConfObjEEJSpecta.addParameter(name='nProfiles', value='64', format='int')
 
opObj11 = procUnitConfObjEEJSpecta.addOperation(name='IncohInt', optype='other')
opObj11.addParameter(name='timeInterval', value='10', format='float')
 
opObj11 = procUnitConfObjEEJSpecta.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='id', value='100', format='int')
opObj11.addParameter(name='wintitle', value='EEJ', format='str')
opObj11.addParameter(name='zmin', value='15', format='int')
opObj11.addParameter(name='zmax', value='40', format='int')# opObj11.addParameter(name='ftp', value='1', format='int')
opObj11.addParameter(name='save', value='1', format='int')
opObj11.addParameter(name='figpath', value='/home/cluster/Pictures/mst_isr_day3', format='str')
opObj11.addParameter(name='wr_period', value='1', format='int')
# opObj11.addParameter(name='ftp', value='1', format='int')
# opObj11.addParameter(name='server', value='jro-app.igp.gob.pe', format='str')
# opObj11.addParameter(name='folder', value='/home/wmaster/graficos', format='str')
# opObj11.addParameter(name='username', value='wmaster', format='str')
# opObj11.addParameter(name='password', value='mst2010vhf', format='str')
# opObj11.addParameter(name='ftp_wei', value='0', format='int')
# opObj11.addParameter(name='exp_code', value='22', format='int')
# opObj11.addParameter(name='sub_exp_code', value='0', format='int')
# opObj11.addParameter(name='plot_pos', value='0', format='int') 
 
 
opObj11 = procUnitConfObjEEJSpecta.addOperation(name='RTIPlot', optype='other')
opObj11.addParameter(name='id', value='101', format='int')
opObj11.addParameter(name='wintitle', value='EEJ', format='str')
opObj11.addParameter(name='showprofile', value='0', format='int')
opObj11.addParameter(name='xmin', value='0', format='int')
opObj11.addParameter(name='xmax', value='24', format='int')
opObj11.addParameter(name='zmin', value='15', format='int')
opObj11.addParameter(name='zmax', value='40', format='int')# opObj11.addParameter(name='ftp', value='1', format='int')
opObj11.addParameter(name='save', value='1', format='int')
opObj11.addParameter(name='figpath', value='/home/cluster/Pictures/mst_isr_day3', format='str')
opObj11.addParameter(name='wr_period', value='1', format='int')

# opObj11.addParameter(name='ftp', value='1', format='int')
# opObj11.addParameter(name='server', value='jro-app.igp.gob.pe', format='str')
# opObj11.addParameter(name='folder', value='/home/wmaster/graficos', format='str')
# opObj11.addParameter(name='username', value='wmaster', format='str')
# opObj11.addParameter(name='password', value='mst2010vhf', format='str')
# opObj11.addParameter(name='ftp_wei', value='0', format='int')
# opObj11.addParameter(name='exp_code', value='22', format='int')
# opObj11.addParameter(name='sub_exp_code', value='0', format='int')
# opObj11.addParameter(name='plot_pos', value='0', format='int')

################ MST ####################################
procUnitConfObjMST = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())
 
opObj11 = procUnitConfObjMST.addOperation(name='ProfileSelector', optype='other')
profileIndex =  '0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119'
opObj11.addParameter(name='profileList', value=profileIndex, format='intlist')
 
 
opObj11 = procUnitConfObjMST.addOperation(name='Decoder', optype='other')
 
opObj11 = procUnitConfObjMST.addOperation(name='CohInt', optype='other')
opObj11.addParameter(name='n', value='20', format='int')
 
 
procUnitConfObjMSTSpectra = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObjMST.getId())
procUnitConfObjMSTSpectra.addParameter(name='nFFTPoints', value='64', format='int')
procUnitConfObjMSTSpectra.addParameter(name='nProfiles', value='64', format='int')
 
opObj11 = procUnitConfObjMSTSpectra.addOperation(name='IncohInt', optype='other')
opObj11.addParameter(name='n', value='5', format='float')
 
opObj11 = procUnitConfObjMSTSpectra.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='id', value='200', format='int')
opObj11.addParameter(name='wintitle', value='MST', format='str')
opObj11.addParameter(name='zmin', value='35', format='int')
opObj11.addParameter(name='zmax', value='55', format='int')
opObj11.addParameter(name='save', value='1', format='int')
opObj11.addParameter(name='figpath', value='/home/cluster/Pictures/mst_isr_day3', format='str')
opObj11.addParameter(name='wr_period', value='1', format='int')
# opObj11.addParameter(name='ftp', value='1', format='int')
# opObj11.addParameter(name='server', value='jro-app.igp.gob.pe', format='str')
# opObj11.addParameter(name='folder', value='/home/wmaster/graficos', format='str')
# opObj11.addParameter(name='username', value='wmaster', format='str')
# opObj11.addParameter(name='password', value='mst2010vhf', format='str')
# opObj11.addParameter(name='ftp_wei', value='0', format='int')
# opObj11.addParameter(name='exp_code', value='19', format='int')
# opObj11.addParameter(name='sub_exp_code', value='0', format='int')
# opObj11.addParameter(name='plot_pos', value='0', format='int') 
 
opObj11 = procUnitConfObjMSTSpectra.addOperation(name='RTIPlot', optype='other')
opObj11.addParameter(name='id', value='201', format='int')
opObj11.addParameter(name='wintitle', value='MST', format='str')
opObj11.addParameter(name='showprofile', value='0', format='int')
opObj11.addParameter(name='xmin', value='0', format='int')
opObj11.addParameter(name='xmax', value='24', format='int')
opObj11.addParameter(name='zmin', value='35', format='int')
opObj11.addParameter(name='zmax', value='55', format='int')
opObj11.addParameter(name='save', value='1', format='int')
opObj11.addParameter(name='figpath', value='/home/cluster/Pictures/mst_isr_day3', format='str')
opObj11.addParameter(name='wr_period', value='1', format='int')

################ ISR ####################################

procUnitConfObjISR = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())
  
opObj11 = procUnitConfObjISR.addOperation(name='ProfileSelector', optype='other')
profileIndex =  '20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99'
opObj11.addParameter(name='profileList', value=profileIndex, format='intlist')
  
opObj11 = procUnitConfObjISR.addOperation(name='ProfileConcat', optype='other')
opObj11.addParameter(name='m', value='5', format='int')
 
opObj11 = procUnitConfObjISR.addOperation(name='filterByHeights')
opObj11.addParameter(name='window', value='20', format='int')

barker3x1 = '1,1,-1,-1,-1,1'
barker3x5 = '1,1,1,1,1, 1,1,1,1,1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,1,1,1,1,1'
 
opObj11 = procUnitConfObjISR.addOperation(name='Decoder', optype='other')
opObj11.addParameter(name='code', value=barker3x5, format='floatlist')
opObj11.addParameter(name='nCode', value='2', format='int')
opObj11.addParameter(name='nBaud', value='15', format='int')

procUnitConfObjISRSpectra = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObjISR.getId())
procUnitConfObjISRSpectra.addParameter(name='nFFTPoints', value='16', format='int')
procUnitConfObjISRSpectra.addParameter(name='nProfiles', value='16', format='int')

opObj11 = procUnitConfObjISRSpectra.addOperation(name='IncohInt', optype='other')
opObj11.addParameter(name='timeInterval', value='60', format='float')

opObj11 = procUnitConfObjISRSpectra.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='id', value='300', format='int')
opObj11.addParameter(name='wintitle', value='ISR', format='str')
opObj11.addParameter(name='zmin', value='45', format='int')
opObj11.addParameter(name='zmax', value='55', format='int')
opObj11.addParameter(name='save', value='1', format='int')
opObj11.addParameter(name='figpath', value='/home/cluster/Pictures/mst_isr_day3', format='str')
opObj11.addParameter(name='wr_period', value='1', format='int')


opObj11 = procUnitConfObjISRSpectra.addOperation(name='RTIPlot', optype='other')
opObj11.addParameter(name='id', value='301', format='int')
opObj11.addParameter(name='wintitle', value='ISR', format='str')
opObj11.addParameter(name='showprofile', value='0', format='int')
opObj11.addParameter(name='xmin', value='0', format='int')
opObj11.addParameter(name='xmax', value='24', format='int')
opObj11.addParameter(name='zmin', value='45', format='int')
opObj11.addParameter(name='zmax', value='55', format='int')
opObj11.addParameter(name='save', value='1', format='int')
opObj11.addParameter(name='figpath', value='/home/cluster/Pictures/mst_isr_day3', format='str')
opObj11.addParameter(name='wr_period', value='1', format='int')


print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()