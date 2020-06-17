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
opObj10.addParameter(name='channelList', value=[0])

opObj11 = procUnitConfObjA.addOperation(name='PulsePairVoltage', optype='other')
opObj11.addParameter(name='n', value='32', format='int')#10
#opObj11.addParameter(name='removeDC', value=1, format='int')

controllerObj.start()
