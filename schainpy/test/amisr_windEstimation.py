import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "AMISR Experiment"

filename = "amisr_reader.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)


path = os.path.join(os.environ['HOME'],'Development/amisr/data')
path = '/home/soporte/Data/AMISR'
figpath = os.path.join(os.environ['HOME'],'Pictures/amisr')

pathFigure = '/home/soporte/workspace/Graficos/DBS/amisr/'
xmin = '12.0'
xmax = '14.0'

readUnitConfObj = controllerObj.addReadUnit(datatype='AMISRReader',
                                            path=path,
                                            startDate='2014/10/21',
                                            endDate='2014/10/21',
                                            startTime='00:00:00',
                                            endTime='23:59:59',
                                            walk=1,
                                            timezone='lt')

#AMISR Processing Unit
procUnitAMISRBeam0 = controllerObj.addProcUnit(datatype='AMISRProc', inputId=readUnitConfObj.getId())

opObj11 = procUnitAMISRBeam0.addOperation(name='PrintInfo', optype='other')

#Reshaper
opObj11 = procUnitAMISRBeam0.addOperation(name='ProfileToChannels', optype='other')


#Beam Selector
#opObj11 = procUnitAMISRBeam0.addOperation(name='BeamSelector', optype='other')
#opObj11.addParameter(name='beam', value='0', format='int')

#Voltage Processing Unit
procUnitConfObjBeam0 = controllerObj.addProcUnit(datatype='VoltageProc', inputId=procUnitAMISRBeam0.getId())
#Coherent Integration
opObj11 = procUnitConfObjBeam0.addOperation(name='CohInt', optype='other')
opObj11.addParameter(name='n', value='8', format='int')
#Spectra Unit Processing, getting spectras with nProfiles and nFFTPoints
procUnitConfObjSpectraBeam0 = controllerObj.addProcUnit(datatype='SpectraProc', inputId=procUnitConfObjBeam0.getId())
procUnitConfObjSpectraBeam0.addParameter(name='nFFTPoints', value=32, format='int')
procUnitConfObjSpectraBeam0.addParameter(name='nProfiles', value=32, format='int')
#RemoveDc
opObj11 = procUnitConfObjSpectraBeam0.addOperation(name='removeDC')

#Noise Estimation    
opObj11 = procUnitConfObjSpectraBeam0.addOperation(name='getNoise')
opObj11.addParameter(name='minHei', value='5', format='float')
opObj11.addParameter(name='maxHei', value='20', format='float')

#SpectraPlot    
opObj11 = procUnitConfObjSpectraBeam0.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='id', value='100', format='int')
opObj11.addParameter(name='wintitle', value='AMISR Beam 0', format='str')
opObj11.addParameter(name='zmin', value='30', format='int')
opObj11.addParameter(name='zmax', value='80', format='int')

#RTIPlot
#title0 = 'RTI AMISR Beam 0'
#opObj11 = procUnitConfObjSpectraBeam0.addOperation(name='RTIPlot', optype='other')
#opObj11.addParameter(name='id', value='200', format='int')
#opObj11.addParameter(name='wintitle', value=title0, format='str')
#opObj11.addParameter(name='showprofile', value='0', format='int')
##Setting RTI time using xmin,xmax
#opObj11.addParameter(name='xmin', value='15', format='int')
#opObj11.addParameter(name='xmax', value='23', format='int')
#Setting dB range with zmin, zmax
#opObj11.addParameter(name='zmin', value='45', format='int')
#opObj11.addParameter(name='zmax', value='70', format='int')
#Save RTI
#figfile0 = 'amisr_rti_beam0.png'
#opObj11.addParameter(name='figpath', value=figpath, format='str')
#opObj11.addParameter(name='figfile', value=figfile0, format='str')

#-----------------------------------------------------------------------------------------------
procUnitConfObj2 = controllerObj.addProcUnit(datatype='ParametersProc', inputId=procUnitConfObjSpectraBeam0 .getId())
opObj20 = procUnitConfObj2.addOperation(name='GetMoments')
 
# opObj21 = procUnitConfObj2.addOperation(name='MomentsPlot', optype='other')
# opObj21.addParameter(name='id', value='3', format='int')
# opObj21.addParameter(name='wintitle', value='Moments Plot', format='str')
# opObj21.addParameter(name='save', value='1', format='bool')
# opObj21.addParameter(name='figpath', value=pathFigure, format='str')
# opObj21.addParameter(name='zmin', value='5', format='int')
# opObj21.addParameter(name='zmax', value='90', format='int')
     
opObj22 = procUnitConfObj2.addOperation(name='WindProfiler', optype='other')
opObj22.addParameter(name='technique', value='DBS', format='str')
opObj22.addParameter(name='azimuth', value='51.06', format='float')
opObj22.addParameter(name='correctFactor', value='-1', format='float') 
opObj22.addParameter(name='dirCosx', value='9.63770247e-01, 5.93066547e-17, 1, 5.93066547e-17,-9.68583161e-01', format='floatlist') 
opObj22.addParameter(name='dirCosy', value=' 0,-0.96858316,0,0.96858316,0', format='floatlist')
# opObj22.addParameter(name='horizontalOnly', value='1', format='bool')
# opObj22.addParameter(name='channelList', value='1,2', format='intlist')

opObj23 = procUnitConfObj2.addOperation(name='WindProfilerPlot', optype='other')
opObj23.addParameter(name='id', value='4', format='int')
opObj23.addParameter(name='wintitle', value='Wind Profiler', format='str')
opObj23.addParameter(name='save', value='1', format='bool')
opObj23.addParameter(name='figpath', value = pathFigure, format='str')
opObj23.addParameter(name='zmin', value='-10', format='int')
opObj23.addParameter(name='zmax', value='10', format='int')
opObj23.addParameter(name='zmin_ver', value='-80', format='float')
opObj23.addParameter(name='zmax_ver', value='80', format='float')
opObj23.addParameter(name='SNRmin', value='-10', format='int')
opObj23.addParameter(name='SNRmax', value='60', format='int')
opObj23.addParameter(name='SNRthresh', value='0', format='float')
opObj23.addParameter(name='xmin', value=xmin, format='float')
opObj23.addParameter(name='xmax', value=xmax, format='float')

print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()
