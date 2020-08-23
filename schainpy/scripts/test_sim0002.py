import os,sys
import datetime
import time
from schainpy.controller import Project
path    = '/home/alex/Downloads/NEW_WR2/spc16removeDC'
figpath = path
desc            = "Simulator Test"

controllerObj   = Project()

controllerObj.setup(id='10',name='Test Simulator',description=desc)

readUnitConfObj = controllerObj.addReadUnit(datatype='SimulatorReader',
                                            frequency=9.345e9,
                                            FixRCP_IPP= 60,
                                            Tau_0 = 30,
                                            AcqH0_0=0,
                                            samples=330,
                                            AcqDH_0=0.15,
                                            FixRCP_TXA=0.15,
                                            FixRCP_TXB=0.15,
                                            Fdoppler=200.0,
                                            Hdoppler=36,
                                            Adoppler=300,
                                            delay=0,
                                            online=0,
                                            walk=0,
                                            nTotalReadFiles=4)

opObj11         = readUnitConfObj.addOperation(name='printInfo')

procUnitConfObjA = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())

opObj10 = procUnitConfObjA.addOperation(name='selectChannels')
opObj10.addParameter(name='channelList', value=[0,1])

procUnitConfObjB = controllerObj.addProcUnit(datatype='SpectraProc', inputId=procUnitConfObjA.getId())
procUnitConfObjB.addParameter(name='nFFTPoints', value=200, format='int')
procUnitConfObjB.addParameter(name='nProfiles', value=200, format='int')

opObj11 = procUnitConfObjB.addOperation(name='removeDC')
opObj11.addParameter(name='mode', value=2)

#opObj11 = procUnitConfObjB.addOperation(name='IncohInt', optype='other')
#opObj11.addParameter(name='n', value='20', format='int')

procUnitConfObjC = controllerObj.addProcUnit(datatype='ParametersProc', inputId=procUnitConfObjB.getId())
procUnitConfObjC.addOperation(name='SpectralMoments')

opObj11 = procUnitConfObjC.addOperation(name='SpectralMomentsPlot')
opObj11.addParameter(name='xmax', value=6)
opObj11.addParameter(name='save', value=figpath)
opObj11.addParameter(name='showprofile', value=1)
opObj11.addParameter(name='save_period', value=10)

controllerObj.start()
