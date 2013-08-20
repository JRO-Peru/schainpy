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

path = '/media/datos/JASMET'

readUnitConfObj = controllerObj.addReadUnit(datatype='Spectra',
                                            path=path,
                                            startDate='2013/08/01',
                                            endDate='2013/08/30',
                                            startTime='00:00:00',
                                            endTime='23:59:59',
                                            online=0,
                                            delay=1,
                                            walk=1)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')

procUnitConfObj1 = controllerObj.addProcUnit(datatype='Spectra', inputId=readUnitConfObj.getId())

opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
opObj11.addParameter(name='id', value='1000', format='int')
opObj11.addParameter(name='wintitle', value='JASMET', format='str')
# opObj11.addParameter(name='timerange', value='60', format='int')
# # opObj11.addParameter(name='zmin', value='15', format='float')
# # opObj11.addParameter(name='zmax', value='40', format='float')
# # opObj11.addParameter(name='xmin', value='0', format='float')
# # opObj11.addParameter(name='xmax', value='24', format='float')
# opObj11.addParameter(name='save', value='1', format='int')
# opObj11.addParameter(name='figpath', value='/home/dsuarez/Pictures/meteor_jasmet', format='str')
# opObj11.addParameter(name='ftp', value='1', format='int')
# opObj11.addParameter(name='wr_period', value='1', format='int')
# opObj11.addParameter(name='exp_code', value='15', format='int')


# opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
# opObj11.addParameter(name='id', value='1001', format='int')
# opObj11.addParameter(name='wintitle', value='JASMET', format='str')
# opObj11.addParameter(name='zmin', value='15', format='float')
# opObj11.addParameter(name='zmax', value='40', format='float')

# opObj11.addParameter(name='save', value='1', format='int')
# opObj11.addParameter(name='figpath', value='/home/dsuarez/Pictures/meteor_jasmet', format='str')
# # opObj11.addParameter(name='ftp', value='1', format='int')
# opObj11.addParameter(name='wr_period', value='5', format='int')
# opObj11.addParameter(name='exp_code', value='15', format='int')



print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()
