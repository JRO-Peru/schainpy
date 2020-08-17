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
figpath = '/home/alex/Downloads/hdf5_test'
######################## UNIDAD DE LECTURA#############################
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
                                            dataBlocksPerFile=100)
                                            #nTotalReadFiles=2)


#opObj11 = readUnitConfObj.addOperation(name='printInfo')

procUnitConfObjA = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())

procUnitConfObjB = controllerObj.addProcUnit(datatype='SpectraProc', inputId=procUnitConfObjA.getId())
procUnitConfObjB.addParameter(name='nFFTPoints', value=625, format='int')
procUnitConfObjB.addParameter(name='nProfiles', value=625, format='int')

opObj11 = procUnitConfObjB.addOperation(name='removeDC')
opObj11.addParameter(name='mode', value=2)
#opObj11 = procUnitConfObjB.addOperation(name='SpectraPlot')
#opObj11 = procUnitConfObjB.addOperation(name='PowerProfilePlot')

procUnitConfObjC= controllerObj.addProcUnit(datatype='ParametersProc',inputId=procUnitConfObjB.getId())
procUnitConfObjC.addOperation(name='SpectralMoments')
#opObj11 = procUnitConfObjC.addOperation(name='PowerPlot')

'''
opObj11 = procUnitConfObjC.addOperation(name='SpectralMomentsPlot')
#opObj11.addParameter(name='xmin', value=14)
#opObj11.addParameter(name='xmax', value=15)
#opObj11.addParameter(name='save', value=figpath)
opObj11.addParameter(name='showprofile', value=1)
#opObj11.addParameter(name='save_period', value=10)
'''

opObj10 = procUnitConfObjC.addOperation(name='ParameterWriter')
opObj10.addParameter(name='path',value=figpath)
#opObj10.addParameter(name='mode',value=0)
opObj10.addParameter(name='blocksPerFile',value='100',format='int')
opObj10.addParameter(name='metadataList',value='utctimeInit,paramInterval,heightList',format='list')
opObj10.addParameter(name='dataList',value='data_POW,data_DOP,utctime')#,format='list'

controllerObj.start()
