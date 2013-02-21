import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "FITS Test"
filename = "fitsexp.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)

readUnitConfObj = controllerObj.addReadUnit(datatype='Fits',
                                            path='/Users/dsuarez/Remote/d2013043',
                                            startDate='2013/02/06',
                                            endDate='2013/12/31',
                                            startTime='00:30:00',
                                            endTime='17:40:59',
                                            online=0,
                                            delay=3,
                                            walk=0)

#procUnitConfObj0 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())

#procUnitConfObj1 = controllerObj.addProcUnit(datatype='SpectraHeis', inputId=procUnitConfObj0.getId())
#procUnitConfObj1.addParameter(name='timeInterval', value='5', format='int')

#opObj11 = procUnitConfObj1.addOperation(name='IncohInt4SpectraHeis', optype='other')
#opObj11.addParameter(name='timeInterval', value='1', format='float')




print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()
  
  