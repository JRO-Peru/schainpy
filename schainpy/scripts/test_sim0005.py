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
################# RANGO DE PLOTEO######################################
dBmin = '30'
dBmax = '60'
xmin = '0'
xmax ='24'
ymin = '0'
ymax = '600'
########################FECHA##########################################
str = datetime.date.today()
today = str.strftime("%Y/%m/%d")
str2 = str - datetime.timedelta(days=1)
yesterday = str2.strftime("%Y/%m/%d")
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
#opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')
#######################################################################
################ OPERACIONES DOMINIO DEL TIEMPO########################
#######################################################################

procUnitConfObjA = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())
'''
opObj11 = procUnitConfObjA.addOperation(name='PulsePairVoltage', optype='other')
opObj11.addParameter(name='n', value='256', format='int')
opObj11.addParameter(name='removeDC', value=1, format='int')
'''
'''
type="power"
opObj10 = procUnitConfObjA.addOperation(name='ScopePlot', optype='external')
#opObj10.addParameter(name='id', value='12')
opObj10.addParameter(name='wintitle', value=type )
opObj10.addParameter(name='type', value=type)
106 32
102 64
99 128
99 256s
'''
'''
type="WeatherPower"
opObj10 = procUnitConfObjA.addOperation(name='PulsepairPowerPlot', optype='external')
#opObj10.addParameter(name='id', value='12')
opObj10.addParameter(name='wintitle', value=type )

opObj11 = procUnitConfObjA.addOperation(name='PulsepairVelocityPlot', optype='other')
opObj11.addParameter(name='xmax', value=8)
'''

controllerObj.start()
