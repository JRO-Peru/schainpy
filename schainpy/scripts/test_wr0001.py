import os,sys
import datetime
import time
from schainpy.controller import Project
path    = '/home/alex/Downloads/hdf5_wr'
figpath = path
desc            = "Simulator Test"

controllerObj   = Project()

controllerObj.setup(id='10',name='Test Simulator',description=desc)


readUnitConfObj = controllerObj.addReadUnit(datatype='ParamReader',
                                            path=path,
                                            startDate="2020/01/01",   #"2020/01/01",#today,
                                            endDate= "2020/12/01",  #"2020/12/30",#today,
                                            startTime='00:00:00',
                                            endTime='23:59:59',
                                            delay=0,
                                            #set=0,
                                            online=0,
                                            walk=1)

controllerObj.start()
