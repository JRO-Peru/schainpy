import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "Meteor Experiment Test"
filename = "meteor20130812.xml"

controllerObj = Project()
controllerObj.setup(id = '191', name='meteor_test01', description=desc)

# path = '/home/dsuarez/.gvfs/datos on 10.10.20.2/High_Power_Meteor'
# 
# path = '/Volumes/FREE_DISK/meteor_data'
# 
# path = '/Users/dsuarez/Movies/meteor'

path = '/home/dsuarez/.gvfs/data on 10.10.20.6/RAW_EXP'
path = '/home/dsuarez/.gvfs/data on 10.10.20.13/DataJasmet'
path = '/home/dsuarez/.gvfs/data on 10.10.20.13/hydra/d2013248'
path = '/media/New Volume/data/hydra/d2013248'
# path = '/home/dsuarez/Documents/jasmet30_rawdata_proc/d2013234'

readUnitConfObj = controllerObj.addReadUnit(datatype='Spectra',
                                            path=path,
                                            startDate='2013/08/01',
                                            endDate='2013/08/30',
                                            startTime='08:00:00',
                                            endTime='08:59:59',
                                            online=0,
                                            delay=2,
                                            walk=0)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')

procUnitConfObj0 = controllerObj.addProcUnit(datatype='Spectra', inputId=readUnitConfObj.getId())


opObj11 = procUnitConfObj0.addOperation(name='selectChannels')
opObj11.addParameter(name='channelList', value='0,7', format='intlist')
# 
# 
# opObj11 = procUnitConfObj0.addOperation(name='Decoder', optype='other')
#    
#    
# opObj11 = procUnitConfObj0.addOperation(name='CohInt', optype='other')
# opObj11.addParameter(name='n', value='2', format='int')
   
   
# # opObj11 = procUnitConfObj0.addOperation(name='VoltageWriter', optype='other')
# # opObj11.addParameter(name='path', value='/home/dsuarez/Documents/jasmet50_rawdata_proc_rev')
# # opObj11.addParameter(name='blocksPerFile', value='100', format='int')
# # opObj11.addParameter(name='profilesPerBlock', value='200', format='int')

# 
# procUnitConfObj1 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObj0.getId())
# procUnitConfObj1.addParameter(name='nProfiles', value='200', format='int')
# # procUnitConfObj1.addParameter(name='nFFTPoints', value='50', format='int')
# procUnitConfObj1.addParameter(name='nFFTPoints', value='100', format='int')
#   
#   
# opObj11 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
# opObj11.addParameter(name='n', value='4', format='int')
 
# 
# 
# opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
# opObj11.addParameter(name='id', value='3000', format='int')
# opObj11.addParameter(name='wintitle', value='JASMET-JARS', format='str')
# opObj11.addParameter(name='timerange', value='300', format='int')
# opObj11.addParameter(name='zmin', value='20', format='float')
# opObj11.addParameter(name='zmax', value='45', format='float')
# # opObj11.addParameter(name='xmin', value='18', format='float')
# # opObj11.addParameter(name='xmax', value='', format='float')
# 
# opObj11.addParameter(name='save', value='1', format='int')
# opObj11.addParameter(name='figpath', value='/home/dsuarez/Pictures/meteor_jasmet_online', format='str')
# opObj11.addParameter(name='ftp', value='1', format='int')
# opObj11.addParameter(name='wr_period', value='10', format='int')
# opObj11.addParameter(name='exp_code', value='15', format='int')
# 
# 


opObj11 = procUnitConfObj0.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='id', value='101', format='int')
opObj11.addParameter(name='zmin', value='35', format='float')
opObj11.addParameter(name='zmax', value='40', format='float')
# opObj11.addParameter(name='save', value='1', format='int')
# opObj11.addParameter(name='figpath', value='/home/dsuarez/Pictures/hydra/20130905', format='str')
# opObj11.addParameter(name='wr_period', value='1', format='int')


# opObj11 = procUnitConfObj0.addOperation(name='Noise', optype='other')
# opObj11.addParameter(name='id', value='100', format='int')
# opObj11.addParameter(name='wintitle', value='Hydra', format='str')
# opObj11.addParameter(name='xmin', value='8', format='float')
# opObj11.addParameter(name='xmax', value='9', format='float')
# opObj11.addParameter(name='ymin', value='35', format='float')
# opObj11.addParameter(name='ymax', value='43', format='float')
# # opObj11.addParameter(name='timerange', value='600', format='int')
# opObj11.addParameter(name='save', value='1', format='int')
# opObj11.addParameter(name='figpath', value='/home/dsuarez/Pictures/hydra/20130905', format='str')
# opObj11.addParameter(name='wr_period', value='1', format='int')

# opObj11 = procUnitConfObj0.addOperation(name='SpectraPlot', optype='other')
# opObj11.addParameter(name='id', value='3001', format='int')
# opObj11.addParameter(name='wintitle', value='JASMET-JARS', format='str')

#  
# opObj11.addParameter(name='save', value='1', format='int')
# opObj11.addParameter(name='figpath', value='/home/dsuarez/Pictures/meteor_jasmet_online', format='str')
# opObj11.addParameter(name='ftp', value='1', format='int')
# opObj11.addParameter(name='wr_period', value='10', format='int')
# opObj11.addParameter(name='exp_code', value='15', format='int')


print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()
