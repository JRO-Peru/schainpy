import os,sys
import datetime
import time
from schainpy.controller import Project
path    = '/home/alex/Downloads/NEW_WR2'
pathfile    = '/home/alex/Downloads/test_rawdata'
figpath = path
desc            = "Simulator Test"

controllerObj   = Project()

controllerObj.setup(id='10',name='Test Simulator',description=desc)

readUnitConfObj = controllerObj.addReadUnit(datatype='SimulatorReader',
                                            frequency=9.345e9,
                                            FixRCP_IPP= 60,
                                            Tau_0 = 30.0,
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
                                            nTotalReadFiles=3)
#opObj11         = readUnitConfObj.addOperation(name='printInfo')
procUnitConfObjA = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())
#opObj10 = procUnitConfObjA.addOperation(name='selectChannels')
#opObj10.addParameter(name='channelList', value=[0,1])
#opObj10.addParameter(name='channelList', value='0',format='intlist')
opObj12 = procUnitConfObjA.addOperation(name='VoltageWriter', optype='other')
opObj12.addParameter(name='path', value=pathfile)
opObj12.addParameter(name='blocksPerFile', value='120', format='int')
opObj12.addParameter(name='profilesPerBlock', value='300', format='int')
controllerObj.start()
