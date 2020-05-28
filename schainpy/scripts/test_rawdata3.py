import os,sys
import datetime
import time
from schainpy.controller import Project
path    = '/home/alex/Downloads'
figpath = path   
desc            = "Simulator Test"
controllerObj   = Project()
controllerObj.setup(id='19',name='Test Simulator',description=desc)

readUnitConfObj = controllerObj.addReadUnit(datatype='SimulatorReader',
                                            #path=path,
                                            #startDate="2015/01/01",#today,
                                            #endDate="2015/12/30",#today,
                                            #startTime='00:00:00',
                                            #endTime='23:59:59',
                                            delay=0,
                                            server="simulate",
                                            online=0,
                                            walk=0)


opObj11         = readUnitConfObj.addOperation(name='printInfo')
opObj11         = readUnitConfObj.addOperation(name='printNumberOfBlock')


procUnitConfObjA = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())

opObj10 = procUnitConfObjA.addOperation(name='selectChannels')
opObj10.addParameter(name='channelList', value='0', format='intList')
'''
opObj10 = procUnitConfObjA.addOperation(name='Scope_', optype='external')
opObj10.addParameter(name='id', value='10', format='int')
#opObj10.addParameter(name='xmin', value='0', format='int')
#opObj10.addParameter(name='xmax', value='1000', format='int')
opObj10.addParameter(name='type', value='iq')
#opObj10.addParameter(name='ymin', value='-5000', format='int')
##opObj10.addParameter(name='ymax', value='8500', format='int')
'''
#######################################################################
########## OPERACIONES DOMINIO DE LA FRECUENCIA########################
#######################################################################
procUnitConfObjSousySpectra = controllerObj.addProcUnit(datatype='SpectraProc', inputId=procUnitConfObjA.getId())
procUnitConfObjSousySpectra.addParameter(name='nFFTPoints', value='64', format='int')
procUnitConfObjSousySpectra.addParameter(name='nProfiles', value='64', format='int')

#######################################################################
########## PLOTEO DOMINIO DE LA FRECUENCIA#############################
#######################################################################
'''
#SpectraPlot
opObj11 = procUnitConfObjSousySpectra.addOperation(name='SpectraPlot', optype='external')
opObj11.addParameter(name='id', value='1', format='int')
opObj11.addParameter(name='wintitle', value='Spectra', format='str')
#opObj11.addParameter(name='xmin', value=-0.01, format='float')
#opObj11.addParameter(name='xmax', value=0.01, format='float')
#opObj11.addParameter(name='zmin', value=dBmin, format='int')
#opObj11.addParameter(name='zmax', value=dBmax, format='int')
#opObj11.addParameter(name='ymin', value=ymin, format='int')
#opObj11.addParameter(name='ymax', value=ymax, format='int')
opObj11.addParameter(name='showprofile', value='1', format='int')
opObj11.addParameter(name='save', value=figpath, format='str')
opObj11.addParameter(name='save_period', value=10, format='int')
'''

#RTIPLOT
opObj11 = procUnitConfObjSousySpectra.addOperation(name='RTIPlot', optype='external')
opObj11.addParameter(name='id', value='2', format='int')
opObj11.addParameter(name='wintitle', value='RTIPlot', format='str')
#opObj11.addParameter(name='zmin', value=dBmin, format='int')
#opObj11.addParameter(name='zmax', value=dBmax, format='int')
#opObj11.addParameter(name='ymin', value=ymin, format='int')
#opObj11.addParameter(name='ymax', value=ymax, format='int')
opObj11.addParameter(name='xmin', value=17, format='int')
opObj11.addParameter(name='xmax', value=18, format='int')
#opObj11.addParameter(name='save', value=figpath, format='str')


controllerObj.start()


