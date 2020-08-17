import os,sys
import datetime
import time
from schainpy.controller import Project
#path    = '/home/alex/Downloads/hdf5_testPP2'
path    = '/home/alex/Downloads/hdf5_test'

figpath = path
desc            = "Simulator Test"

controllerObj   = Project()

controllerObj.setup(id='10',name='Test Simulator',description=desc)

readUnitConfObj = controllerObj.addReadUnit(datatype='ParameterReader',
                                            path=path,
                                            startDate="2020/01/01",   #"2020/01/01",#today,
                                            endDate= "2020/12/01",  #"2020/12/30",#today,
                                            startTime='00:00:00',
                                            endTime='23:59:59',
                                            delay=0,
                                            #set=0,
                                            online=0,
                                            walk=1)

procUnitConfObjA = controllerObj.addProcUnit(datatype='ParametersProc',inputId=readUnitConfObj.getId())
opObj11 = procUnitConfObjA.addOperation(name='Block360')
opObj11.addParameter(name='n', value='100', format='int')
opObj11= procUnitConfObjA.addOperation(name='WeatherPlot',optype='other')
opObj11.addParameter(name='save', value=figpath)
opObj11.addParameter(name='save_period', value=1)
#opObj11 = procUnitConfObjA.addOperation(name='PowerPlot', optype='other')#PulsepairPowerPlot
#opObj11 = procUnitConfObjA.addOperation(name='PPSignalPlot', optype='other')
controllerObj.start()
