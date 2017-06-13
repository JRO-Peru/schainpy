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


path = os.path.join(os.environ['HOME'],'amisr')
# path = '/media/signalchain/HD-PXU2/AMISR_JULIA_MODE'
# path = '/media/soporte/E9F4-F053/AMISR/Data/NoiseTest/EEJ'
# path = '/media/soporte/E9F4-F053/AMISR/Data/EEJ'
path = '/mnt/data_amisr'
#path = '/media/soporte/AMISR_104'
#figpath = os.path.join(os.environ['HOME'],'Pictures/amisr/test/proc/eej')
#figpath = '/media/soporte/E9F4-F053/AMISR/Data/JULIA/EEJ'
figpath = '/home/soporte/Data/EEJ'
remotefolder = "/home/wmaster/graficos"

xmin = '07'
xmax = '18'
ymin ='30'
ymax ='300' 
dbmin = '45' #'60'#'55' #'40' #noise  esf  eej
dbmax = '65' #'70' #'55'
show = '1'

code = '1,-1,-1,-1,1,1,1,1,-1,-1,-1,1,-1,-1,-1,1,-1,-1,-1,1,-1,-1,1,-1,1,1,-1,1'
nCode = '1'
nBaud = '28'


today = time.strftime("%Y/%m/%d")


readUnitConfObj = controllerObj.addReadUnit(datatype='AMISRReader',
                                            path=path,
                                            startDate=today, #'2014/10/07',
                                            endDate=today, #'2014/10/07',
                                            startTime='07:01:30',#'07:00:00',
                                            endTime='17:55:00',#'15:00:00',
                                            walk=0,
                                            code = code,
                                            nCode = nCode,
                                            nBaud = nBaud,
                                            timezone='lt',
                                            online=1)

#AMISR Processing Unit

#Voltage Processing Unit
procUnitConfObjBeam0 = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())
opObj10 = procUnitConfObjBeam0.addOperation(name='setRadarFrequency')
opObj10.addParameter(name='frequency', value='445e6', format='float') #changed on Dic 3, 15:40h
#opObj10.addParameter(name='frequency', value='440e6', format='float')

# opObj12 = procUnitConfObjBeam0.addOperation(name='selectHeights')
# opObj12.addParameter(name='minHei', value='0', format='float')


opObj11 = procUnitConfObjBeam0.addOperation(name='Decoder', optype='other')
opObj11.addParameter(name='code', value=code, format='floatlist')
opObj11.addParameter(name='nCode', value=nCode, format='int')
opObj11.addParameter(name='nBaud', value=nBaud, format='int')


#Spectra Unit Processing, getting spectras with nProfiles and nFFTPoints
procUnitConfObjSpectraBeam0 = controllerObj.addProcUnit(datatype='SpectraProc', inputId=procUnitConfObjBeam0.getId())
procUnitConfObjSpectraBeam0.addParameter(name='nFFTPoints', value=16, format='int')
# 
opObj11 =  procUnitConfObjSpectraBeam0.addOperation(name='IncohInt', optype='other')
opObj11.addParameter(name='n', value='150', format='int')
#opObj11.addParameter(name='timeInterval', value='30', format='float')

   

#Noise Estimation    
opObj11 = procUnitConfObjSpectraBeam0.addOperation(name='getNoise')
opObj11.addParameter(name='minHei', value='100', format='float')
opObj11.addParameter(name='maxHei', value='280', format='float')
#opObj11.addParameter(name='minHei', value='15', format='float')
#opObj11.addParameter(name='maxHei', value='20', format='float')

 
#SpectraPlot    
opObj11 = procUnitConfObjSpectraBeam0.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='id', value='1', format='int')
opObj11.addParameter(name='wintitle', value='EEJ AMISR', format='str')
opObj11.addParameter(name='ymin', value=ymin, format='int')
opObj11.addParameter(name='ymax', value=ymax, format='int')
opObj11.addParameter(name='zmin', value=dbmin, format='int')
opObj11.addParameter(name='zmax', value=dbmax, format='int')
opObj11.addParameter(name='save', value='0', format='bool')
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
opObj11.addParameter(name='wintitle', value='EEJ AMISR', format='str')
opObj11.addParameter(name='showprofile', value='0', format='int')
opObj11.addParameter(name='xmin', value=xmin, format='float')
opObj11.addParameter(name='xmax', value=xmax, format='float')
opObj11.addParameter(name='ymin', value=ymin, format='int')
opObj11.addParameter(name='ymax', value=ymax, format='int')
opObj11.addParameter(name='zmin', value=dbmin, format='int')
opObj11.addParameter(name='zmax', value=dbmax, format='int')
opObj11.addParameter(name='save', value='1', format='bool')
opObj11.addParameter(name='figpath', value = figpath, format='str')
opObj11.addParameter(name='show', value = show, format='bool')
opObj11.addParameter(name='ftp', value='1', format='int')
opObj11.addParameter(name='wr_period', value='2', format='int')
opObj11.addParameter(name='exp_code', value='21', format='int')
opObj11.addParameter(name='sub_exp_code', value='3', format='int')
opObj11.addParameter(name='ftp_wei', value='0', format='int')
opObj11.addParameter(name='plot_pos', value='0', format='int')
    
# #send to server
procUnitConfObj2 = controllerObj.addProcUnit(name='SendToServer')
#procUnitConfObj2.addParameter(name='server', value='jro-app.igp.gob.pe', format='str')
procUnitConfObj2.addParameter(name='server', value='10.10.120.125', format='str')
procUnitConfObj2.addParameter(name='username', value='wmaster', format='str')
procUnitConfObj2.addParameter(name='password', value='mst2010vhf', format='str')
procUnitConfObj2.addParameter(name='localfolder', value=figpath, format='str')
procUnitConfObj2.addParameter(name='remotefolder', value=remotefolder, format='str')
procUnitConfObj2.addParameter(name='ext', value='.png', format='str')
procUnitConfObj2.addParameter(name='period', value='300', format='int')
procUnitConfObj2.addParameter(name='protocol', value='ssh', format='str')


# #Noise
#title0 = 'RTI AMISR Beam 0'
# opObj11 = procUnitConfObjSpectraBeam0.addOperation(name='Noise', optype='other')
# opObj11.addParameter(name='id', value='3', format='int')
# opObj11.addParameter(name='wintitle', value='EEJ AMISR', format='str')
# opObj11.addParameter(name='showprofile', value='0', format='int')
# opObj11.addParameter(name='xmin', value=xmin, format='float')
# opObj11.addParameter(name='xmax', value=xmax, format='float')
# opObj11.addParameter(name='ymin', value=dbmin, format='int')
# opObj11.addParameter(name='ymax', value=dbmax, format='int')
# opObj11.addParameter(name='save', value='0', format='bool')
# opObj11.addParameter(name='figpath', value = figpath, format='str')
# opObj11.addParameter(name='show', value = show, format='bool')


# #For saving Pdata (doesn't work with amisr data yet!)
# opObj11 = procUnitConfObjSpectraBeam0.addOperation(name='SpectraWriter', optype='other')
# opObj11.addParameter(name='path', value=figpath)
# opObj11.addParameter(name='blocksPerFile', value='10', format='int')
# opObj11.addParameter(name='datatype', value="4", format="int") #size of data to be saved
# 
# 
# # procUnitConfObj2 = controllerObj.addProcUnit(name='SendToServer')
# # procUnitConfObj2.addParameter(name='server', value='jro-app.igp.gob.pe', format='str')
# # procUnitConfObj2.addParameter(name='username', value='wmaster', format='str')
# # procUnitConfObj2.addParameter(name='password', value='mst2010vhf', format='str')
# # procUnitConfObj2.addParameter(name='localfolder', value=pathFigure, format='str')
# # procUnitConfObj2.addParameter(name='remotefolder', value=remotefolder, format='str')
# # procUnitConfObj2.addParameter(name='ext', value='.png', format='str')
# # procUnitConfObj2.addParameter(name='period', value=5, format='int')
# # procUnitConfObj2.addParameter(name='protocol', value='ftp', format='str')
# #-----------------------------------------------------------------------------------------------
# procUnitConfObj2 = controllerObj.addProcUnit(datatype='ParametersProc', inputId=procUnitConfObjSpectraBeam0.getId())
# opObj20 = procUnitConfObj2.addOperation(name='GetMoments')
# 
# opObj12 = procUnitConfObj2.addOperation(name='HDF5Writer', optype='other')
# opObj12.addParameter(name='path', value=figpath+'/plots')
# opObj12.addParameter(name='blocksPerFile', value='10', format='int')
# opObj12.addParameter(name='metadataList',value='type,inputUnit,heightList',format='list')
# opObj12.addParameter(name='dataList',value='data_param,data_SNR,utctime',format='list')
# opObj12.addParameter(name='mode',value='1',format='int')
 


# print "Escribiendo el archivo XML"
# controllerObj.writeXml(path +'/'+filename)
# print "Leyendo el archivo XML"
# controllerObj.readXml(path +'/'+filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()

#21 3 pm


