import os, sys
from pytz import timezone
path = os.path.dirname(os.getcwd())
path = os.path.dirname(path)

print path
sys.path.insert(0, path) # Para usar las librerias del eclipse.

from schainpy.controller import Project

# from __main__ import time
#path = os.path.split(os.getcwd())[0]
#sys.path.append(path)
# import scipy.io as sio 
# import pprint
# import numpy
# import time
# import os
# import h5py
# import re
# import tables
# 
# from model.data.jrodata import *
# from model.proc.jroproc_base import ProcessingUnit, Operation
# from model.io.jroIO_base import *


# controllerObj = Project()

# controllerObj.setup(id = '191', name='test01', description=desc)


#from controller import *

desc = "DBS Experiment Test"
filename = "DBStest.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)

#path = 'F:\CIRI Data\processed'
path='/media/4B514E8903EBC487/CIRI Data/processed'
#pathFigure = 'C:\Users\jdk5273\Documents\LiClipseWorkspace'
pathFigure='/home/alex/Pictures/ciri'
xmin = '16'
xmax = '17'
startTime = '15:59:00'

readUnitConfObj = controllerObj.addReadUnit(datatype='matoffReader',
                                            path=path,
                                            startDate='2015/05/20',
                                            endDate='2015/05/20',
                                            startTime=startTime,
                                            endTime='17:59:59',
                                            online=0,
                                            delay=5,
                                            walk=0)

procUnitConfObj1 = controllerObj.addProcUnit(datatype='SpectraProc', inputId=readUnitConfObj.getId())

# opObj14 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
# opObj14.addParameter(name='id', value='1', format='int')
# opObj14.addParameter(name='wintitle', value='Con interf', format='str')
# opObj14.addParameter(name='save', value='0', format='bool')
# opObj14.addParameter(name='figpath', value=pathFigure, format='str')

opObj11 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
opObj11.addParameter(name='n', value='10', format='int')

opObj14 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
opObj14.addParameter(name='id', value='2', format='int')
opObj14.addParameter(name='wintitle', value='Con interf', format='str')
opObj14.addParameter(name='save', value='0', format='bool')
opObj14.addParameter(name='figpath', value=pathFigure, format='str')
# opObj14.addParameter(name='zmin', value='5', format='int')
# opObj14.addParameter(name='zmax', value='90', format='int')

opObj14 = procUnitConfObj1.addOperation(name='CrossSpectraPlot', optype='other')
opObj14.addParameter(name='id', value='4', format='int')
opObj14.addParameter(name='wintitle', value='Con interf', format='str')
opObj14.addParameter(name='phase_cmap', value='jet', format='str')
opObj14.addParameter(name='save', value='0', format='bool')
opObj14.addParameter(name='figpath', value=pathFigure, format='str')
# opObj14.addParameter(name='zmin', value='5', format='int')
# opObj14.addParameter(name='zmax', value='90', format='int')

opObj12 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
opObj12.addParameter(name='id', value='3', format='int')
opObj12.addParameter(name='wintitle', value='RTI Plot', format='str')
opObj12.addParameter(name='save', value='1', format='bool')
opObj12.addParameter(name='figpath', value = pathFigure, format='str')
opObj12.addParameter(name='xmin', value=xmin, format='float')
opObj12.addParameter(name='xmax', value=xmax, format='float')
# opObj12.addParameter(name='zmin', value='5', format='int')
# opObj12.addParameter(name='zmax', value='90', format='int')

#--------------------------------------------------------------------------------------------------
print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()


