import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "AMISR Experiment"

filename = "amisr_reader.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)


path = os.path.join(os.environ['HOME'],'amisr')
path = '/media/signalchain/HD-PXU2/AMISR_JULIA_MODE'
figpath = os.path.join(os.environ['HOME'],'Pictures/amisr/eej')

xmin = '7'
xmax = '15'

readUnitConfObj = controllerObj.addReadUnit(datatype='AMISRReader',
                                            path=path,
                                            startDate='2014/10/07',
                                            endDate='2014/10/07',
                                            startTime='07:00:00',
                                            endTime='15:00:00',
                                            walk=0,
                                            timezone='lt',
                                            all=0,
                                            online=0)

#AMISR Processing Unit
procUnitAMISRBeam0 = controllerObj.addProcUnit(datatype='AMISRProc', inputId=readUnitConfObj.getId())

opObj11 = procUnitAMISRBeam0.addOperation(name='PrintInfo', optype='other')

#Reshaper
opObj11 = procUnitAMISRBeam0.addOperation(name='ProfileToChannels', optype='other')

#Voltage Processing Unit
procUnitConfObjBeam0 = controllerObj.addProcUnit(datatype='VoltageProc', inputId=procUnitAMISRBeam0.getId())
opObj10 = procUnitConfObjBeam0.addOperation(name='setRadarFrequency')
opObj10.addParameter(name='frequency', value='445e6', format='float')

# opObj12 = procUnitConfObjBeam0.addOperation(name='selectHeights')
# opObj12.addParameter(name='minHei', value='0', format='float')

# code = '1,1,-1,1,1,-1,1,-1,-1,1,-1,-1,-1,1,-1,-1,-1,1,-1,-1,-1,1,1,1,1,-1,-1,-1'
# code = '1,1,0,1,1,0,1,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,1,1,1,0,0,0'
code = '1,-1,-1,-1,1,1,1,1,-1,-1,-1,1,-1,-1,-1,1,-1,-1,-1,1,-1,-1,1,-1,1,1,-1,1'
opObj11 = procUnitConfObjBeam0.addOperation(name='Decoder', optype='other')
opObj11.addParameter(name='code', value=code, format='floatlist')
opObj11.addParameter(name='nCode', value='1', format='int')
opObj11.addParameter(name='nBaud', value='28', format='int')

# opObj12 = procUnitConfObjBeam0.addOperation(name='selectHeights')
# opObj12.addParameter(name='minHei', value='50', format='float')
# opObj12.addParameter(name='maxHei', value='150', format='float')
#Coherent Integration
#opObj11 = procUnitConfObjBeam0.addOperation(name='CohInt', optype='other')
#opObj11.addParameter(name='timeInterval', value='10', format='int')

#Spectra Unit Processing, getting spectras with nProfiles and nFFTPoints
procUnitConfObjSpectraBeam0 = controllerObj.addProcUnit(datatype='SpectraProc', inputId=procUnitConfObjBeam0.getId())
procUnitConfObjSpectraBeam0.addParameter(name='nFFTPoints', value=64, format='int')
procUnitConfObjSpectraBeam0.addParameter(name='nProfiles', value=64, format='int')

opObj11 =  procUnitConfObjSpectraBeam0.addOperation(name='IncohInt', optype='other')
# opObj11.addParameter(name='n', value='90', format='int')
opObj11.addParameter(name='timeInterval', value='30', format='float')

#RemoveDc
opObj11 = procUnitConfObjSpectraBeam0.addOperation(name='removeDC')

#Noise Estimation    
opObj11 = procUnitConfObjSpectraBeam0.addOperation(name='getNoise')
opObj11.addParameter(name='minHei', value='100', format='float')
opObj11.addParameter(name='maxHei', value='280', format='float')

#SpectraPlot    
opObj11 = procUnitConfObjSpectraBeam0.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='id', value='1', format='int')
opObj11.addParameter(name='wintitle', value='AMISR Beam 0', format='str')
opObj11.addParameter(name='zmin', value='38', format='int')
opObj11.addParameter(name='zmax', value='68', format='int')
opObj11.addParameter(name='save', value='1', format='bool')
opObj11.addParameter(name='figpath', value = figpath, format='str')
opObj11.addParameter(name='save', value='1', format='bool')
opObj11.addParameter(name='figpath', value = figpath, format='str')

#RTIPlot
#title0 = 'RTI AMISR Beam 0'
opObj11 = procUnitConfObjSpectraBeam0.addOperation(name='RTIPlot', optype='other')
opObj11.addParameter(name='id', value='2', format='int')
# opObj11.addParameter(name='wintitle', value=title0, format='str')
opObj11.addParameter(name='showprofile', value='0', format='int')
opObj11.addParameter(name='xmin', value=xmin, format='float')
opObj11.addParameter(name='xmax', value=xmax, format='float')
opObj11.addParameter(name='zmin', value='38', format='int')
opObj11.addParameter(name='zmax', value='68', format='int')
opObj11.addParameter(name='save', value='1', format='bool')
opObj11.addParameter(name='figpath', value = figpath, format='str')



#-----------------------------------------------------------------------------------------------


print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()

#21 3 pm


