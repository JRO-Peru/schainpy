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
#
# codigo64='1,1,1,0,1,1,0,1,1,1,1,0,0,0,1,0,1,1,1,0,1,1,0,1,0,0,0,1,1,1,0,1,1,1,1,0,1,1,0,1,1,1,1,0,0,0,1,0,0,0,0,1,0,0,1,0,1,1,1,0,0,0,1,0,'+\
#              '1,1,1,0,1,1,0,1,1,1,1,0,0,0,1,0,1,1,1,0,1,1,0,1,0,0,0,1,1,1,0,1,0,0,0,1,0,0,1,0,0,0,0,1,1,1,0,1,1,1,1,0,1,1,0,1,0,0,0,1,1,1,0,1'

#opObj11 = procUnitConfObjA.addOperation(name='setRadarFrequency')
#opObj11.addParameter(name='frequency', value='30e6', format='float')

#opObj10 = procUnitConfObjA.addOperation(name='Scope', optype='external')
#opObj10.addParameter(name='id', value='10', format='int')
##opObj10.addParameter(name='xmin', value='0', format='int')
##opObj10.addParameter(name='xmax', value='50', format='int')
#opObj10.addParameter(name='type', value='iq')
#opObj10.addParameter(name='ymin', value='-5000', format='int')
##opObj10.addParameter(name='ymax', value='8500', format='int')

#opObj10 = procUnitConfObjA.addOperation(name='setH0')
#opObj10.addParameter(name='h0', value='-5000', format='float')

#opObj11 =  procUnitConfObjA.addOperation(name='filterByHeights')
#opObj11.addParameter(name='window', value='1', format='int')

#codigo='1,1,-1,1,1,-1,1,-1,-1,1,-1,-1,-1,1,-1,-1,-1,1,-1,-1,-1,1,1,1,1,-1,-1,-1'
#opObj11 = procUnitConfObjSousy.addOperation(name='Decoder', optype='other')
#opObj11.addParameter(name='code', value=codigo, format='floatlist')
#opObj11.addParameter(name='nCode', value='1', format='int')
#opObj11.addParameter(name='nBaud', value='28', format='int')

#opObj11 = procUnitConfObjA.addOperation(name='CohInt', optype='other')
#opObj11.addParameter(name='n', value='100', format='int')

#######################################################################
########## OPERACIONES DOMINIO DE LA FRECUENCIA########################
#######################################################################
procUnitConfObjB = controllerObj.addProcUnit(datatype='SpectraProc', inputId=procUnitConfObjA.getId())
procUnitConfObjB.addParameter(name='nFFTPoints', value='100', format='int')
procUnitConfObjB.addParameter(name='nProfiles', value='100', format='int')
#procUnitConfObjSousySpectra.addParameter(name='pairsList', value='(0,0),(1,1),(0,1)', format='pairsList')

#opObj13 = procUnitConfObjSousySpectra.addOperation(name='removeDC')
#opObj13.addParameter(name='mode', value='2', format='int')

#opObj11 = procUnitConfObjSousySpectra.addOperation(name='IncohInt', optype='other')
#opObj11.addParameter(name='n', value='60', format='float')
#######################################################################
########## PLOTEO DOMINIO DE LA FRECUENCIA#############################
#######################################################################
#SpectraPlot

##opObj11 = procUnitConfObjB.addOperation(name='SpectraPlot', optype='external')
##opObj11.addParameter(name='id', value='1', format='int')
##opObj11.addParameter(name='wintitle', value='Spectra', format='str')
#opObj11.addParameter(name='xmin', value=-0.01, format='float')
#opObj11.addParameter(name='xmax', value=0.01, format='float')
#opObj11.addParameter(name='zmin', value=dBmin, format='int')
#opObj11.addParameter(name='zmax', value=dBmax, format='int')
#opObj11.addParameter(name='ymin', value=ymin, format='int')
#opObj11.addParameter(name='ymax', value=ymax, format='int')
##opObj11.addParameter(name='showprofile', value='1', format='int')
##opObj11.addParameter(name='save', value=figpath, format='str')
##opObj11.addParameter(name='save_period', value=10, format='int')


#RTIPLOT

##opObj11 = procUnitConfObjB.addOperation(name='RTIPlot', optype='external')
##opObj11.addParameter(name='id', value='2', format='int')
##opObj11.addParameter(name='wintitle', value='RTIPlot', format='str')
#opObj11.addParameter(name='zmin', value=dBmin, format='int')
#opObj11.addParameter(name='zmax', value=dBmax, format='int')
#opObj11.addParameter(name='ymin', value=ymin, format='int')
#opObj11.addParameter(name='ymax', value=ymax, format='int')
##opObj11.addParameter(name='xmin', value=0, format='int')
##opObj11.addParameter(name='xmax', value=23, format='int')

##opObj11.addParameter(name='showprofile', value='1', format='int')
##opObj11.addParameter(name='save', value=figpath, format='str')
##opObj11.addParameter(name='save_period', value=10, format='int')


# opObj11 = procUnitConfObjSousySpectra.addOperation(name='CrossSpectraPlot', optype='other')
# opObj11.addParameter(name='id', value='3', format='int')
# opObj11.addParameter(name='wintitle', value='CrossSpectraPlot', format='str')
# opObj11.addParameter(name='ymin', value=ymin, format='int')
# opObj11.addParameter(name='ymax', value=ymax, format='int')
# opObj11.addParameter(name='phase_cmap', value='jet', format='str')
# opObj11.addParameter(name='zmin', value=dBmin, format='int')
# opObj11.addParameter(name='zmax', value=dBmax, format='int')
# opObj11.addParameter(name='figpath', value=figures_path, format='str')
# opObj11.addParameter(name='save', value=0, format='bool')
# opObj11.addParameter(name='pairsList', value='(0,1)', format='pairsList')
# #
# opObj11 = procUnitConfObjSousySpectra.addOperation(name='CoherenceMap', optype='other')
# opObj11.addParameter(name='id', value='4', format='int')
# opObj11.addParameter(name='wintitle', value='Coherence', format='str')
# opObj11.addParameter(name='phase_cmap', value='jet', format='str')
# opObj11.addParameter(name='xmin', value=xmin, format='float')
# opObj11.addParameter(name='xmax', value=xmax, format='float')
# opObj11.addParameter(name='figpath', value=figures_path, format='str')
# opObj11.addParameter(name='save', value=0, format='bool')
# opObj11.addParameter(name='pairsList', value='(0,1)', format='pairsList')
#
#######################################################################
############### UNIDAD DE ESCRITURA ###################################
#######################################################################
#opObj11 = procUnitConfObjSousySpectra.addOperation(name='SpectraWriter', optype='other')
#opObj11.addParameter(name='path', value=wr_path)
#opObj11.addParameter(name='blocksPerFile', value='50', format='int')

procUnitConfObjC = controllerObj.addProcUnit(datatype='ParametersProc', inputId=procUnitConfObjB.getId())
procUnitConfObjC.addOperation(name='SpectralMoments')

procUnitConfObjC.addOperation(name='SpectralMomentsPlot')


print ("Escribiendo el archivo XML")
print ("Leyendo el archivo XML")



controllerObj.start()
