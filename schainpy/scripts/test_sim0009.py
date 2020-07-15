import os,sys
import datetime
import time
from schainpy.controller import Project
#path    = '/home/alex/Downloads/NEW_WR2/spc16removeDC'
#figpath = path

path    = '/home/alex/Downloads/test_rawdata'
figpath = '/home/alex/Downloads/hdf5_testPP'
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
                                            Fdoppler=600.0,
                                            Hdoppler=36,
                                            Adoppler=300,#300
                                            delay=0,
                                            online=0,
                                            walk=0,
                                            profilesPerBlock=625,
                                            dataBlocksPerFile=100)#,#nTotalReadFiles=2)

'''
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
'''
#opObj11         = readUnitConfObj.addOperation(name='printInfo')
procUnitConfObjA = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())
#opObj11 = procUnitConfObjA.addOperation(name='CohInt', optype='other')
#opObj11.addParameter(name='n', value='4', format='int')

#opObj10 = procUnitConfObjA.addOperation(name='selectChannels')
#opObj10.addParameter(name='channelList', value=[0])
opObj11 = procUnitConfObjA.addOperation(name='PulsePairVoltage', optype='other')
opObj11.addParameter(name='n', value='625', format='int')#10
opObj11.addParameter(name='removeDC', value=1, format='int')

#opObj11 = procUnitConfObjA.addOperation(name='PulsepairPowerPlot', optype='other')
#opObj11 = procUnitConfObjA.addOperation(name='PulsepairSignalPlot', optype='other')


#opObj11 = procUnitConfObjA.addOperation(name='PulsepairVelocityPlot', optype='other')
#opObj11.addParameter(name='xmax', value=8)

#opObj11 = procUnitConfObjA.addOperation(name='PulsepairSpecwidthPlot', optype='other')

procUnitConfObjB= controllerObj.addProcUnit(datatype='ParametersProc',inputId=procUnitConfObjA.getId())


opObj10 = procUnitConfObjB.addOperation(name='ParameterWriter')
opObj10.addParameter(name='path',value=figpath)
#opObj10.addParameter(name='mode',value=0)
opObj10.addParameter(name='blocksPerFile',value='100',format='int')
opObj10.addParameter(name='metadataList',value='utctimeInit,timeInterval',format='list')
opObj10.addParameter(name='dataList',value='dataPP_POW,dataPP_DOP,dataPP_SNR,dataPP_WIDTH')#,format='list'

controllerObj.start()
