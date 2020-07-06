#!python
'''
'''

import os, sys
import datetime
import time

#path = os.path.dirname(os.getcwd())
#path = os.path.dirname(path)
#sys.path.insert(0, path)

from schainpy.controller import Project

desc = "USRP_test"
filename = "USRP_processing.xml"
controllerObj = Project()
controllerObj.setup(id = '191', name='Test_USRP', description=desc)

############## USED TO PLOT IQ VOLTAGE, POWER AND SPECTRA #############

#######################################################################
######PATH DE LECTURA, ESCRITURA, GRAFICOS Y ENVIO WEB#################
#######################################################################
#path = '/media/data/data/vientos/57.2063km/echoes/NCO_Woodman'


#path = '/home/soporte/data_hdf5' #### with clock   35.16 db noise
path    = '/home/alex/Downloads'
figpath = '/home/alex/Downloads'
pathfile    = '/home/alex/Downloads/test_rawdata2'

#figpath = '/home/soporte/data_hdf5_imag'
#remotefolder = "/home/wmaster/graficos"
#######################################################################
################# RANGO DE PLOTEO######################################
#######################################################################
dBmin = '30'
dBmax = '60'
xmin = '0'
xmax ='24'
ymin = '0'
ymax = '600'
#######################################################################
########################FECHA##########################################
#######################################################################
str = datetime.date.today()
today = str.strftime("%Y/%m/%d")
str2 = str - datetime.timedelta(days=1)
yesterday = str2.strftime("%Y/%m/%d")
#######################################################################
######################## UNIDAD DE LECTURA#############################
#######################################################################
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


opObj12 = procUnitConfObjA.addOperation(name='VoltageWriter', optype='other')
opObj12.addParameter(name='path', value=pathfile)
opObj12.addParameter(name='blocksPerFile', value='120', format='int')
opObj12.addParameter(name='profilesPerBlock', value='300', format='int')




print ("Escribiendo el archivo XML")
print ("Leyendo el archivo XML")



controllerObj.start()
