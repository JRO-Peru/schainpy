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

#opObj10 = procUnitConfObjA.addOperation(name='selectChannels')
#opObj10.addParameter(name='channelList', value=[0,1])
#opObj10.addParameter(name='channelList', value='0',format='intlist')

opObj11 = procUnitConfObjA.addOperation(name='PulsePairVoltage', optype='other')
opObj11.addParameter(name='n', value='16', format='int')
opObj11.addParameter(name='removeDC', value=1, format='int')

controllerObj.start()
