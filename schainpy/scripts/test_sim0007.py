import os, sys
import datetime
import time
from schainpy.controller import Project

desc = "USRP_test"
filename = "USRP_processing.xml"
controllerObj = Project()
controllerObj.setup(id = '191', name='Test_USRP', description=desc)

############## USED TO PLOT IQ VOLTAGE, POWER AND SPECTRA #############
######PATH DE LECTURA, ESCRITURA, GRAFICOS Y ENVIO WEB#################
path    = '/home/alex/Downloads/test_rawdata'
figpath = '/home/alex/Downloads'
######################## UNIDAD DE LECTURA#############################
readUnitConfObj = controllerObj.addReadUnit(datatype='VoltageReader',
                                            path=path,
                                            startDate="2020/01/01",   #"2020/01/01",#today,
                                            endDate= "2020/12/01",  #"2020/12/30",#today,
                                            startTime='00:00:00',
                                            endTime='23:59:59',
                                            delay=0,
                                            #set=0,
                                            online=0,
                                            walk=1)

opObj11 = readUnitConfObj.addOperation(name='printInfo')

procUnitConfObjA = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())

procUnitConfObjB = controllerObj.addProcUnit(datatype='SpectraProc', inputId=procUnitConfObjA.getId())
procUnitConfObjB.addParameter(name='nFFTPoints', value=64, format='int')
procUnitConfObjB.addParameter(name='nProfiles', value=64, format='int')
'''
32 99.96  113.11  529.94s
64  97.3  122.96  326.26
128 96.29 100.23  230     894
256 98.65 102.83  182     640
'''
opObj11 = procUnitConfObjB.addOperation(name='removeDC')
opObj11.addParameter(name='mode', value=2)

#opObj11 = procUnitConfObjB.addOperation(name='IncohInt', optype='other')
#opObj11.addParameter(name='n', value='20', format='int')

procUnitConfObjC = controllerObj.addProcUnit(datatype='ParametersProc', inputId=procUnitConfObjB.getId())
procUnitConfObjC.addOperation(name='SpectralMoments')
opObj11 = procUnitConfObjC.addOperation(name='SpectralMomentsPlot')
#opObj11.addParameter(name='xmin', value=14)
opObj11.addParameter(name='xmax', value=6)
#opObj11.addParameter(name='save', value=figpath)
opObj11.addParameter(name='showprofile', value=1)
controllerObj.start()
