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


readUnitConfObj = controllerObj.addReadUnit(datatype='Voltage',
                                            path=path,
                                            startDate='2013/08/01',
                                            endDate='2013/08/30',
                                            startTime='00:00:00',
                                            endTime='23:59:59',
                                            online=1,
                                            delay=2,
                                            walk=1)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')

procUnitConfObj0 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())

# opObj11 = procUnitConfObj0.addOperation(name='ProfileSelector', optype='other')
# opObj11.addParameter(name='profileList', 
#                      value='1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23,  \
#                      25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49, \
#                      51, 53, 55, 57, 59, 61, 63, 65, 67, 69, 71, 73, 75, \
#                      77, 79, 81, 83, 85, 87, 89, 91, 93, 95, 97, 99, 101, \
#                      103, 105, 107, 109, 111, 113, 115, 117, 119, 121, 123, \
#                      125, 127, 129, 131, 133, 135, 137, 139, 141, 143, 145, \
#                      147, 149, 151, 153, 155, 157, 159, 161, 163, 165, 167, \
#                      169, 171, 173, 175, 177, 179, 181, 183, 185, 187, 189, \
#                      191, 193, 195, 197, 199', format='intlist')

# opObj11 = procUnitConfObj0.addOperation(name='filterByHeights')
# opObj11.addParameter(name='window', value='3', format='int')

opObj11 = procUnitConfObj0.addOperation(name='Decoder', optype='other')
# opObj11.addParameter(name='code', value='1,1,1,0,1,1,0,1,1,1,1,0,0,0,1,0,1,1,1,0,1,1,0,1,0,0,0,1,1,1,0,1', format='floatlist')
# opObj11.addParameter(name='nCode', value='2', format='int')
# opObj11.addParameter(name='nBaud', value='16', format='int')

opObj11 = procUnitConfObj0.addOperation(name='CohInt', optype='other')
opObj11.addParameter(name='n', value='2', format='int')




procUnitConfObj1 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObj0.getId())
procUnitConfObj1.addParameter(name='nProfiles', value='400', format='int')
procUnitConfObj1.addParameter(name='nFFTPoints', value='50', format='int')


opObj11 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
opObj11.addParameter(name='n', value='4', format='int')



opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
opObj11.addParameter(name='id', value='1000', format='int')
opObj11.addParameter(name='wintitle', value='JASMET-JARS', format='str')
opObj11.addParameter(name='timerange', value='300', format='int')
# opObj11.addParameter(name='zmin', value='15', format='float')
# opObj11.addParameter(name='zmax', value='40', format='float')
# opObj11.addParameter(name='xmin', value='18', format='float')
# opObj11.addParameter(name='xmax', value='', format='float')

opObj11.addParameter(name='save', value='1', format='int')
opObj11.addParameter(name='figpath', value='/home/dsuarez/Pictures/meteor_jasmet_offline', format='str')
# opObj11.addParameter(name='ftp', value='1', format='int')
# opObj11.addParameter(name='wr_period', value='60', format='int')
# opObj11.addParameter(name='exp_code', value='10', format='int')


opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='id', value='1001', format='int')
opObj11.addParameter(name='wintitle', value='JASMET-JARS', format='str')
# opObj11.addParameter(name='zmin', value='5', format='float')
# opObj11.addParameter(name='zmax', value='10', format='float')

opObj11.addParameter(name='save', value='1', format='int')
opObj11.addParameter(name='figpath', value='/home/dsuarez/Pictures/meteor_jasmet_offline', format='str')
#opObj11.addParameter(name='ftp', value='1', format='int')
#opObj11.addParameter(name='wr_period', value='60', format='int')
#opObj11.addParameter(name='exp_code', value='10', format='int')


print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()
