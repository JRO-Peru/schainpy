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
                                            server="simulate",
                                            delay=0,
                                            online=0,
                                            walk=0)

opObj11         = readUnitConfObj.addOperation(name='printInfo')
opObj11         = readUnitConfObj.addOperation(name='printNumberOfBlock')
procUnitConfObjA = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())

opObj10 = procUnitConfObjA.addOperation(name='selectChannels')
opObj10.addParameter(name='channelList', value='0', format='intList')

opObj10 = procUnitConfObjA.addOperation(name='Scope_', optype='external')
opObj10.addParameter(name='id', value='10', format='int')
opObj10.addParameter(name='type', value='iq')
opObj10.addParameter(name='save', value='1', format='int')
opObj10.addParameter(name='figpath', value=figpath, format='str')
opObj10.addParameter(name='wr_period', value=10, format='int')
########## OPERACIONES DOMINIO DE LA FRECUENCIA########################
procUnitConfObjSousySpectra = controllerObj.addProcUnit(datatype='SpectraProc', inputId=procUnitConfObjA.getId())
procUnitConfObjSousySpectra.addParameter(name='nFFTPoints', value='64', format='int')
procUnitConfObjSousySpectra.addParameter(name='nProfiles', value='64', format='int')
########## PLOTEO DOMINIO DE LA FRECUENCIA#############################
#SpectraPlot
opObj11 = procUnitConfObjSousySpectra.addOperation(name='SpectraPlot', optype='external')
opObj11.addParameter(name='id', value='1', format='int')
opObj11.addParameter(name='wintitle', value='Spectra', format='str')
opObj11.addParameter(name='showprofile', value='1', format='int')
opObj11.addParameter(name='save', value=figpath, format='str')
opObj11.addParameter(name='save_period', value=10, format='int')
controllerObj.start()
