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
#path='/media/4B514E8903EBC487/CIRI Data/processed'
#path='/home/ciri/ciri_online'
#offline program
#path='/home/ciri/.gvfs/SFTP for radar on 192.168.1.161/media/dataswap/huancayo/20150701/processed'
#online program
path='/home/ciri/.gvfs/SFTP for radar on 192.168.1.161/media/dataswap/huancayo/processed' 
#pathFigure = 'C:\Users\jdk5273\Documents\LiClipseWorkspace'
pathFigure='/home/ciri/Pictures/ciri'
xmin = '0'
xmax = '24'
startTime = '00:00:00'
remotefolder = "/home/wmaster/graficos"

readUnitConfObj = controllerObj.addReadUnit(datatype='matoffReader',
                                            path=path,
                                            startDate='2015/05/30',
                                            endDate='2015/05/30',
                                            startTime=startTime,
                                            endTime='23:59:59',
                                            online=1,
                                            delay=5,
                                            walk=0)

procUnitConfObj1 = controllerObj.addProcUnit(datatype='SpectraProc', inputId=readUnitConfObj.getId())

# opObj14 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
# opObj14.addParameter(name='id', value='1', format='int')
# opObj14.addParameter(name='wintitle', value='Con interf', format='str')
# opObj14.addParameter(name='save', value='0', format='bool')
# opObj14.addParameter(name='figpath', value=pathFigure, format='str')

opObj11 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
opObj11.addParameter(name='n', value='60', format='int')

opObj14 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
opObj14.addParameter(name='id', value='2', format='int')
opObj14.addParameter(name='wintitle', value='Con interf', format='str')
opObj14.addParameter(name='save', value='1', format='bool')
opObj14.addParameter(name='figpath', value=pathFigure, format='str')
opObj14.addParameter(name='zmin', value='-30', format='int')
opObj14.addParameter(name='zmax', value='0', format='int')
opObj14.addParameter(name='exp_code', value='29', format='int')
opObj14.addParameter(name='wr_period', value='1', format='int')
opObj14.addParameter(name='save', value='1', format='int')

opObj14.addParameter(name='ftp', value='1', format='int')

opObj14 = procUnitConfObj1.addOperation(name='CrossSpectraPlot', optype='other')
opObj14.addParameter(name='id', value='4', format='int')
opObj14.addParameter(name='wintitle', value='Con interf', format='str')
opObj14.addParameter(name='phase_cmap', value='jet', format='str')
opObj14.addParameter(name='save', value='1', format='bool')
opObj14.addParameter(name='figpath', value=pathFigure, format='str')
opObj14.addParameter(name='zmin', value='-30', format='int')
opObj14.addParameter(name='zmax', value='0', format='int')
opObj14.addParameter(name='exp_code', value='29', format='int')
opObj14.addParameter(name='wr_period', value='1', format='int')
opObj14.addParameter(name='save', value='1', format='int')

opObj14.addParameter(name='ftp', value='1', format='int')

opObj12 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
opObj12.addParameter(name='id', value='3', format='int')
opObj12.addParameter(name='wintitle', value='RTI Plot', format='str')
opObj12.addParameter(name='save', value='1', format='bool')
opObj12.addParameter(name='figpath', value = pathFigure, format='str')
opObj12.addParameter(name='xmin', value=xmin, format='float')
opObj12.addParameter(name='xmax', value=xmax, format='float')
opObj12.addParameter(name='zmin', value='-30', format='int')
opObj12.addParameter(name='zmax', value='0', format='int')
opObj12.addParameter(name='exp_code', value='29', format='int')
opObj12.addParameter(name='wr_period', value='1', format='int')
opObj12.addParameter(name='save', value='1', format='int')

opObj12.addParameter(name='ftp', value='1', format='int')

# 
procUnitConfObj2 = controllerObj.addProcUnit(name='SendToServer')
procUnitConfObj2.addParameter(name='server', value='jro-app.igp.gob.pe', format='str')
procUnitConfObj2.addParameter(name='username', value='wmaster', format='str')
procUnitConfObj2.addParameter(name='password', value='mst2010vhf', format='str')
procUnitConfObj2.addParameter(name='localfolder', value=pathFigure, format='str')
procUnitConfObj2.addParameter(name='remotefolder', value=remotefolder, format='str')
procUnitConfObj2.addParameter(name='ext', value='.png', format='str')
procUnitConfObj2.addParameter(name='period', value=5, format='int')
procUnitConfObj2.addParameter(name='protocol', value='ftp', format='str')




#--------------------------------------------------------------------------------------------------
print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()


