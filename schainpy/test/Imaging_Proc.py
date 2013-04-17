import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "EWDrifts+Imaging+Faraday Experiment"
filename = "imaging_proc.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)

path = '/remote'
path = '/home/dsuarez/.gvfs/data on 10.10.20.13/EW_Faraday_imaging'
path = '/home/dsuarez/imaging_data'

readUnitConfObj = controllerObj.addReadUnit(datatype='Voltage',
                                            path=path,
                                            startDate='2013/04/09',
                                            endDate='2013/04/09',
                                            startTime='17:00:00',
                                            endTime='23:59:59',
                                            delay=20,
                                            online=1,
                                            walk=1)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')

######################## IMAGING #############################################
procUnitConfObj0 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())
#
opObj11 = procUnitConfObj0.addOperation(name='ProfileSelector', optype='other')
opObj11.addParameter(name='profileRangeList', value='0,39', format='intlist')

#opObj11 = procUnitConfObj0.addOperation(name='filterByHeights')
#opObj11.addParameter(name='window', value='4', format='int')

opObj11 = procUnitConfObj0.addOperation(name='Decoder', optype='other')


#opObj11 = procUnitConfObj0.addOperation(name='selectHeights')
#opObj11.addParameter(name='maxHei', value='300', format='float')

#opObj11 = procUnitConfObj0.addOperation(name='selectHeights')
#opObj11.addParameter(name='minHei', value='300', format='float')
#opObj11.addParameter(name='maxHei', value='600', format='float')

procUnitConfObj1 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObj0.getId())
procUnitConfObj1.addParameter(name='nFFTPoints', value='8', format='int')
procUnitConfObj1.addParameter(name='pairsList', value='(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(0,7), \
							(1,2),(1,3),(1,4),(1,5),(1,6),(1,7), \
							(2,3),(2,4),(2,5),(2,6),(2,7), \
							(3,4),(3,5),(3,6),(3,7), \
							(4,5),(4,6),(4,7), \
							(5,6),(5,7), \
							(6,7)', \
							format='pairslist')

opObj11 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
opObj11.addParameter(name='n', value='50', format='float')


opObj11 = procUnitConfObj1.addOperation(name='SpectraWriter', optype='other')
opObj11.addParameter(name='path', value='/media/datos/IMAGING/IMAGING')
opObj11.addParameter(name='blocksPerFile', value='10', format='int')


print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()
  
  
