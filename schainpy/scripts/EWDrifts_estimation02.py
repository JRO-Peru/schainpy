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

path = "/home/soporte/Data/drifts/HDF5"
pathFigure = '/home/soporte/workspace/Graficos/drifts/prueba'
pathFile = '/home/soporte/Data/drifts/HDF5'

xmin = 0
xmax = 24
#------------------------------------------------------------------------------------------------
readUnitConfObj = controllerObj.addReadUnit(datatype='HDF5Reader',
                                            path=path,
                                            startDate='2012/09/06',
                                            endDate='2012/09/06',
                                            startTime='00:00:00',
                                            endTime='23:59:59',
                                            timezone='lt',
                                            walk=1)

procUnitConfObj0 = controllerObj.addProcUnit(datatype='ParametersProc', inputId=readUnitConfObj.getId())
#--------------------------------------------------------------------------------------------------

opObj11 = procUnitConfObj0.addOperation(name='EWDriftsEstimation', optype='other')
opObj11.addParameter(name='zenith', value='-3.80208,3.10658', format='floatlist')
opObj11.addParameter(name='zenithCorrection', value='0.183201', format='float')

opObj23 = procUnitConfObj0.addOperation(name='EWDriftsPlot', optype='other')
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