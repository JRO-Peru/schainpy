import os, sys
#import timeit
import datetime

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "HF_EXAMPLE"
filename = "hf_test.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)


path='/media/APOLLO/HF_rawdata/d2015026/0/cspec'
#path='/home/alex/Downloads/ICA_LAST_TEST'

readUnitConfObj = controllerObj.addReadUnit(datatype='HFReader',
                                            path=path,
                                            startDate='2013/01/1',
                                            endDate='2015/12/30',
                                            startTime='00:00:00',
                                            endTime='23:59:59',
                                            online=0,
                                            delay=10,
                                            walk=1)


procUnitConfObj0 = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())

opObj12 = procUnitConfObj0.addOperation(name='CohInt', optype='other')
opObj12.addParameter(name='n', value='10', format='int')
    
# opObj11 = procUnitConfObj0.addOperation(name='Scope', optype='other')
# opObj11.addParameter(name='id', value='10', format='int')
# opObj11.addParameter(name='wintitle', value='Voltage', format='str')
# opObj11.addParameter(name='ymin', value='-1e-8', format='float')
# opObj11.addParameter(name='ymax', value='1e-8', format='float')

procUnitConfObj1 = controllerObj.addProcUnit(datatype='SpectraProc', inputId=procUnitConfObj0.getId())
procUnitConfObj1.addParameter(name='nFFTPoints', value='10', format='int')
procUnitConfObj1.addParameter(name='nProfiles', value='10', format='int')


opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='id', value='2001', format='int')
opObj11.addParameter(name='wintitle', value='HF_Jicamarca', format='str')
opObj11.addParameter(name='zmin', value='-120', format='float')
opObj11.addParameter(name='zmax', value='-70', format='float')
 
opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
opObj11.addParameter(name='id', value='3002', format='int')
opObj11.addParameter(name='wintitle', value='HF_Jicamarca', format='str')
opObj11.addParameter(name='zmin', value='-120', format='float')
opObj11.addParameter(name='zmax', value='70', format='float')

print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()

#timeit.timeit('controllerObj.run()', number=2)

controllerObj.run()