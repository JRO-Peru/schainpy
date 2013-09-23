import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "EWDrifts+Imaging+Faraday Experiments"
filename = "imaging_plots.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)

path = '/media/datos/IMAGING/IMAGING'

readUnitConfObj = controllerObj.addReadUnit(datatype='Spectra',
                                            path=path,
                                            startDate='2013/04/09',
                                            endDate='2013/04/09',
                                            startTime='17:00:00',
                                            endTime='23:59:59',
                                            set=0,
                                            delay=20,
                                            online=1,
                                            walk=1)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')

######################## IMAGING #############################################

procUnitConfObj1 = controllerObj.addProcUnit(datatype='Spectra', inputId=readUnitConfObj.getId())


# opObj11 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
# opObj11.addParameter(name='n', value='2', format='float')

opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='id', value='100', format='int')
opObj11.addParameter(name='wintitle', value='Imaging', format='str')
opObj11.addParameter(name='zmin', value='10', format='int')
opObj11.addParameter(name='zmax', value='50', format='int')
# opObj11.addParameter(name='ymin', value='0', format='int')
# opObj11.addParameter(name='ymax', value='300', format='int')



# opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
# opObj11.addParameter(name='id', value='101', format='int')
# opObj11.addParameter(name='wintitle', value='Imaging', format='str')
# opObj11.addParameter(name='xmin', value='0', format='float')
# opObj11.addParameter(name='xmax', value='24', format='float')
# opObj11.addParameter(name='save', value='1', format='int')
# opObj11.addParameter(name='figfile', value='rti-imaging.png', format='str')
# opObj11.addParameter(name='figpath', value='/media/datos/IMAGING/IMAGING/graphs', format='str')
# opObj11.addParameter(name='ftp', value='1', format='int')
# opObj11.addParameter(name='ftpratio', value='3', format='int')
# 
# 
# 
# opObj11 = procUnitConfObj1.addOperation(name='CoherenceMap', optype='other')
# opObj11.addParameter(name='id', value='102', format='int')
# opObj11.addParameter(name='wintitle', value='Imaging', format='str')
# opObj11.addParameter(name='xmin', value='0', format='float')
# opObj11.addParameter(name='xmax', value='24', format='float')
# #opObj11.addParameter(name='zmin', value='30', format='int')
# #opObj11.addParameter(name='zmax', value='50', format='int')
# #opObj11.addParameter(name='xmin', value='18.5', format='float')
# #opObj11.addParameter(name='xmax', value='22', format='float')
# opObj11.addParameter(name='save', value='1', format='int')
# opObj11.addParameter(name='figfile', value='coherence-imaging.png', format='str')
# opObj11.addParameter(name='figpath', value='/media/datos/IMAGING/IMAGING/graphs', format='str')
# opObj11.addParameter(name='ftp', value='1', format='int')
# opObj11.addParameter(name='ftpratio', value='3', format='int')






print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()
  
  
