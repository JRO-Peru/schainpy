#    DIAS 19 Y 20 FEB 2014
#    Comprobacion de Resultados DBS con SA

import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "DBS Experiment Test"
filename = "DBStest.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)

#Experimentos

path = '/host/Jicamarca/EW_Drifts/d2012248'
pathFigure = '/home/propietario/workspace/Graficos/drifts'


path = "/home/soporte/Data/drifts"
pathFigure = '/home/soporte/workspace/Graficos/drifts/prueba'

xmin = 11.75
xmax = 14.75
#------------------------------------------------------------------------------------------------
readUnitConfObj = controllerObj.addReadUnit(datatype='VoltageReader',
                                            path=path,
                                            startDate='2012/01/01',
                                            endDate='2012/12/31',
                                            startTime='00:00:00',
                                            endTime='23:59:59',
                                            online=0,
                                            walk=1)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')

#--------------------------------------------------------------------------------------------------

procUnitConfObj0 = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())

opObj11 = procUnitConfObj0.addOperation(name='ProfileSelector', optype='other')
opObj11.addParameter(name='profileRangeList', value='0,127', format='intlist')
 
opObj11 = procUnitConfObj0.addOperation(name='filterByHeights')
opObj11.addParameter(name='window', value='3', format='int')
 
opObj11 = procUnitConfObj0.addOperation(name='Decoder', optype='other')
# opObj11.addParameter(name='code', value='1,-1', format='floatlist')
# opObj11.addParameter(name='nCode', value='2', format='int')
# opObj11.addParameter(name='nBaud', value='1', format='int')
 
procUnitConfObj1 = controllerObj.addProcUnit(datatype='SpectraProc', inputId=procUnitConfObj0.getId())
procUnitConfObj1.addParameter(name='nFFTPoints', value='128', format='int')
procUnitConfObj1.addParameter(name='nProfiles', value='128', format='int')
procUnitConfObj1.addParameter(name='pairsList', value='(0,1),(2,3)', format='pairsList')#,(2,3)

opObj11 = procUnitConfObj1.addOperation(name='selectHeights')
# # opObj11.addParameter(name='minHei', value='320.0', format='float') 
# # opObj11.addParameter(name='maxHei', value='350.0', format='float') 
opObj11.addParameter(name='minHei', value='200.0', format='float') 
opObj11.addParameter(name='maxHei', value='600.0', format='float')

opObj11 = procUnitConfObj1.addOperation(name='selectChannels')
opObj11.addParameter(name='channelList', value='0,1,2,3', format='intlist') 
   
opObj11 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
opObj11.addParameter(name='timeInterval', value='300.0', format='float')

opObj13 = procUnitConfObj1.addOperation(name='removeDC')

# opObj14 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
# opObj14.addParameter(name='id', value='1', format='int')
# # opObj14.addParameter(name='wintitle', value='Con interf', format='str')
# opObj14.addParameter(name='save', value='1', format='bool')
# opObj14.addParameter(name='figpath', value=pathFigure, format='str')
# # opObj14.addParameter(name='zmin', value='5', format='int')
# opObj14.addParameter(name='zmax', value='30', format='int')
#  
# opObj12 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
# opObj12.addParameter(name='id', value='2', format='int')
# opObj12.addParameter(name='wintitle', value='RTI Plot', format='str')
# opObj12.addParameter(name='save', value='1', format='bool')
# opObj12.addParameter(name='figpath', value = pathFigure, format='str')
# opObj12.addParameter(name='xmin', value=xmin, format='float')
# opObj12.addParameter(name='xmax', value=xmax, format='float')
# # opObj12.addParameter(name='zmin', value='5', format='int')
# opObj12.addParameter(name='zmax', value='30', format='int')

#--------------------------------------------------------------------------------------------------

procUnitConfObj2 = controllerObj.addProcUnit(datatype='ParametersProc', inputId=procUnitConfObj1.getId())
opObj20 = procUnitConfObj2.addOperation(name='SpectralFitting')
opObj20.addParameter(name='path', value='/home/soporte/workspace/RemoteSystemsTempFiles', format='str')
opObj20.addParameter(name='file', value='modelSpectralFitting', format='str')
opObj20.addParameter(name='groupList', value='(0,1),(2,3)',format='multiList')

opObj11 = procUnitConfObj2.addOperation(name='SpectralFittingPlot', optype='other')
opObj11.addParameter(name='id', value='3', format='int')
opObj11.addParameter(name='wintitle', value='DopplerPlot', format='str')
opObj11.addParameter(name='cutHeight', value='350', format='int')
opObj11.addParameter(name='fit', value='1', format='int')#1--True/include fit
opObj11.addParameter(name='save', value='1', format='bool')
opObj11.addParameter(name='figpath', value = pathFigure, format='str')

opObj11 = procUnitConfObj2.addOperation(name='EWDriftsEstimation', optype='other')
opObj11.addParameter(name='zenith', value='-3.80208,3.10658', format='floatlist')
opObj11.addParameter(name='zenithCorrection', value='0.183201', format='float')

opObj23 = procUnitConfObj2.addOperation(name='EWDriftsPlot', optype='other')
opObj23.addParameter(name='id', value='4', format='int')
opObj23.addParameter(name='wintitle', value='EW Drifts', format='str')
opObj23.addParameter(name='save', value='1', format='bool')
opObj23.addParameter(name='figpath', value = pathFigure, format='str')
opObj23.addParameter(name='zminZonal', value='-150', format='int')
opObj23.addParameter(name='zmaxZonal', value='150', format='int')
opObj23.addParameter(name='zminVertical', value='-30', format='float')
opObj23.addParameter(name='zmaxVertical', value='30', format='float')
opObj23.addParameter(name='SNR_1', value='1', format='bool')
opObj23.addParameter(name='SNRmax', value='5', format='int')
# opObj23.addParameter(name='SNRthresh', value='-50', format='float')
opObj23.addParameter(name='xmin', value=xmin, format='float')
opObj23.addParameter(name='xmax', value=xmax, format='float')
#--------------------------------------------------------------------------------------------------
print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()