#! /usr/bin/python
#! /usr/bin/env python

import os, sys
import time

path = os.path.dirname(os.getcwd())
path = os.path.dirname(path)
sys.path.insert(0, path)

from schainpy.controller import Project

desc = "AMISR Experiment"

filename = "amisr_reader.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='eej_proc', description=desc)


# path = os.path.join(os.environ['HOME'],'amisr')
# path = '/media/signalchain/HD-PXU2/AMISR_JULIA_MODE'
# path = '/media/soporte/E9F4-F053/AMISR/Data/NoiseTest/EEJ'
# path = '/media/soporte/E9F4-F053/AMISR/Data/EEJ'
# path = '/mnt/data_amisr'
# path = '/media/soporte/E9F4-F053/AMISR/Data/winds'
path = '/mnt/data_amisr'
#path = '/media/soporte/AMISR_104'
#figpath = os.path.join(os.environ['HOME'],'Pictures/amisr/test/proc/eej')
figpath = '/home/soporte/Data/winds/plots'
remotefolder = "/home/wmaster/graficos"

xmin = '08'
xmax = '18'
dbmin = '50' #'60'#'55' #'40' #noise  esf  eej
dbmax = '80' #'70' #'55'

#to consider that each real IPP is actually original_IPP * nchannels
ippFactor = '5'

# code = '1,-1,-1,-1,1,1,1,1,-1,-1,-1,1,-1,-1,-1,1,-1,-1,-1,1,-1,-1,1,-1,1,1,-1,1'
# nCode = '1'
# nBaud = '28'


today = time.strftime("%Y/%m/%d")


readUnitConfObj = controllerObj.addReadUnit(datatype='AMISRReader',
                                            path=path,
                                            startDate='2016/10/28', #'2014/10/07',
                                            endDate='2014/10/28', #'2014/10/07',
                                            startTime='00:00:00',#'07:00:00',
                                            endTime='23:59:59',#'15:00:00',
                                            walk=0,
#                                             code = code,
#                                             nCode = nCode,
#                                             nBaud = nBaud,
                                            timezone='lt',
                                            online=1)

#AMISR Processing Unit

#Voltage Processing Unit
procUnitConfObjBeam0 = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())
opObj10 = procUnitConfObjBeam0.addOperation(name='setRadarFrequency')
opObj10.addParameter(name='frequency', value='445e6', format='float')



opObj12 = procUnitConfObjBeam0.addOperation(name='selectHeights')
opObj12.addParameter(name='minHei', value='0', format='float')
opObj12.addParameter(name='maxHei', value='10', format='float')



#Spectra Unit Processing, getting spectras with nProfiles and nFFTPoints
procUnitConfObjSpectraBeam0 = controllerObj.addProcUnit(datatype='SpectraProc', inputId=procUnitConfObjBeam0.getId())
procUnitConfObjSpectraBeam0.addParameter(name='nFFTPoints', value=32, format='int')
procUnitConfObjSpectraBeam0.addParameter(name='ippFactor', value=ippFactor, format='int')
# 
opObj11 =  procUnitConfObjSpectraBeam0.addOperation(name='IncohInt', optype='other')
opObj11.addParameter(name='n', value='16', format='int')
#opObj11.addParameter(name='timeInterval', value='30', format='float')


# # #RemoveDc
opObj11 = procUnitConfObjSpectraBeam0.addOperation(name='removeDC')
#  
#Noise Estimation    
opObj11 = procUnitConfObjSpectraBeam0.addOperation(name='getNoise')
opObj11.addParameter(name='minHei', value='5', format='float')
opObj11.addParameter(name='maxHei', value='9', format='float')

 
#SpectraPlot    
opObj11 = procUnitConfObjSpectraBeam0.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='id', value='1', format='int')
opObj11.addParameter(name='wintitle', value='Winds AMISR', format='str')
opObj11.addParameter(name='zmin', value=dbmin, format='int')
opObj11.addParameter(name='zmax', value=dbmax, format='int')
opObj11.addParameter(name='save', value='1', format='bool')
opObj11.addParameter(name='figpath', value = figpath, format='str')
opObj11.addParameter(name='ftp', value='1', format='int')
opObj11.addParameter(name='wr_period', value='2', format='int')
opObj11.addParameter(name='exp_code', value='21', format='int')
opObj11.addParameter(name='sub_exp_code', value='3', format='int')
opObj11.addParameter(name='ftp_wei', value='0', format='int')
opObj11.addParameter(name='plot_pos', value='0', format='int')

# #RTIPlot
# #title0 = 'RTI AMISR Beam 0'
opObj11 = procUnitConfObjSpectraBeam0.addOperation(name='RTIPlot', optype='other')
opObj11.addParameter(name='id', value='2', format='int')
opObj11.addParameter(name='wintitle', value='Winds AMISR', format='str')
opObj11.addParameter(name='showprofile', value='0', format='int')
opObj11.addParameter(name='xmin', value=xmin, format='float')
opObj11.addParameter(name='xmax', value=xmax, format='float')
opObj11.addParameter(name='zmin', value=dbmin, format='int')
opObj11.addParameter(name='zmax', value=dbmax, format='int')
opObj11.addParameter(name='save', value='1', format='bool')
opObj11.addParameter(name='figpath', value = figpath, format='str')
opObj11.addParameter(name='ftp', value='1', format='int')
opObj11.addParameter(name='wr_period', value='2', format='int')
opObj11.addParameter(name='exp_code', value='21', format='int')
opObj11.addParameter(name='sub_exp_code', value='3', format='int')
opObj11.addParameter(name='ftp_wei', value='0', format='int')
opObj11.addParameter(name='plot_pos', value='0', format='int')
# 
# 
# #Noise
#title0 = 'RTI AMISR Beam 0'
opObj11 = procUnitConfObjSpectraBeam0.addOperation(name='Noise', optype='other')
opObj11.addParameter(name='id', value='3', format='int')
# opObj11.addParameter(name='wintitle', value=title0, format='str')
opObj11.addParameter(name='showprofile', value='0', format='int')
opObj11.addParameter(name='xmin', value=xmin, format='float')
opObj11.addParameter(name='xmax', value=xmax, format='float')
opObj11.addParameter(name='ymin', value=dbmin, format='int')
opObj11.addParameter(name='ymax', value=dbmax, format='int')
opObj11.addParameter(name='save', value='1', format='bool')
opObj11.addParameter(name='figpath', value = figpath, format='str')


#For saving Pdata (doesn't work with amisr data yet!)
# opObj11 = procUnitConfObjSpectraBeam0.addOperation(name='SpectraWriter', optype='other')
# opObj11.addParameter(name='path', value=figpath)
# opObj11.addParameter(name='blocksPerFile', value='100', format='int')
# opObj11.addParameter(name='datatype', value="4", format="int") #size of data to be saved


# procUnitConfObj2 = controllerObj.addProcUnit(name='SendToServer')
# procUnitConfObj2.addParameter(name='server', value='jro-app.igp.gob.pe', format='str')
# procUnitConfObj2.addParameter(name='username', value='wmaster', format='str')
# procUnitConfObj2.addParameter(name='password', value='mst2010vhf', format='str')
# procUnitConfObj2.addParameter(name='localfolder', value=pathFigure, format='str')
# procUnitConfObj2.addParameter(name='remotefolder', value=remotefolder, format='str')
# procUnitConfObj2.addParameter(name='ext', value='.png', format='str')
# procUnitConfObj2.addParameter(name='period', value=5, format='int')
# procUnitConfObj2.addParameter(name='protocol', value='ftp', format='str')
#-----------------------------------------------------------------------------------------------


# print "Escribiendo el archivo XML"
# controllerObj.writeXml(path +'/'+filename)
# print "Leyendo el archivo XML"
# controllerObj.readXml(path +'/'+filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()

#21 3 pm


