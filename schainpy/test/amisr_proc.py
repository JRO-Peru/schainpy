import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "AMISR Experiment"

filename = "amisr_reader.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)

path = '$HOME/Documents/amisr'

figpath = '$HOME/Pictures/amisr'

readUnitConfObj = controllerObj.addReadUnit(datatype='AMISR',
                                            path=path,
                                            startDate='2014/08/18',
                                            endDate='2014/08/18',
                                            startTime='00:00:00',
                                            endTime='23:59:59',
                                            walk=1)

#AMISR Processing Unit
procUnitAMISRBeam0 = controllerObj.addProcUnit(datatype='AMISR', inputId=readUnitConfObj.getId())

#Beam Selector
opObj11 = procUnitAMISRBeam0.addOperation(name='BeamSelector', optype='other')
opObj11.addParameter(name='beam', value='0', format='int')

#Voltage Processing Unit
procUnitConfObjBeam0 = controllerObj.addProcUnit(datatype='Voltage', inputId=procUnitAMISRBeam0.getId())
#Coherent Integration
opObj11 = procUnitConfObjBeam0.addOperation(name='CohInt', optype='other')
opObj11.addParameter(name='n', value='128', format='int')
#Spectra Unit Processing, getting spectras with nProfiles y nFFTPoints
procUnitConfObjSpectraBeam0 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObjBeam0.getId())
procUnitConfObjSpectraBeam0.addParameter(name='nFFTPoints', value=32, format='int')
procUnitConfObjSpectraBeam0.addParameter(name='nProfiles', value=32, format='int')
#Noise Estimation    
opObj11 = procUnitConfObjSpectraBeam0.addOperation(name='getNoise')
opObj11.addParameter(name='minHei', value='100', format='float')
opObj11.addParameter(name='maxHei', value='450', format='float')
#SpectraPlot    
opObj11 = procUnitConfObjSpectraBeam0.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='id', value='100', format='int')
opObj11.addParameter(name='wintitle', value='AMISR Beam 0', format='str')
#RTIPlot
opObj11 = procUnitConfObjSpectraBeam0.addOperation(name='RTIPlot', optype='other')
opObj11.addParameter(name='id', value='200', format='int')
opObj11.addParameter(name='wintitle', value=title1, format='str')
#Setting RTI time using xmin,xmax
opObj11.addParameter(name='xmin', value='0', format='int')
opObj11.addParameter(name='xmax', value='18', format='int')
#Setting dB range with zmin, zmax
opObj11.addParameter(name='zmin', value='45', format='int')
opObj11.addParameter(name='zmax', value='70', format='int')
opObj11.addParameter(name='showprofile', value='0', format='int')
opObj11.addParameter(name='figpath', value=figpath, format='str')
opObj11.addParameter(name='figfile', value=figfile1, format='str')


print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()
