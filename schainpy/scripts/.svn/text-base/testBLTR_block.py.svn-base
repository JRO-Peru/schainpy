'''
Created on Nov 09, 2016

@author: roj- LouVD
'''
import os, sys


path = os.path.split(os.getcwd())[0]
path = os.path.split(path)[0]

sys.path.insert(0, path)

from schainpy.controller import Project

filename = 'test1.xml'
# path = '/home/jespinoza/workspace/data/bltr/'
path = '/home/erick/Documents/Data/BLTR_Data/sswma/'    
desc = "read bltr data sswma file"
figpath = '/home/erick/workspace' 
pathhdf5 = '/tmp/'

controllerObj = Project()

controllerObj.setup(id = '191', name='test1', description=desc)
readUnitConfObj = controllerObj.addReadUnit(datatype='testBLTRReader',
                                            path=path,
                                            startDate='2015/01/17',
                                            endDate='2017/01/01',
                                            startTime='00:00:00',
                                            endTime='23:59:59',
                                            ext='sswma')                    

procUnitConfObj1 = controllerObj.addProcUnit(datatype='BLTRProcess', 
                                             inputId=readUnitConfObj.getId())
 
'''-------------------------------------------Processing--------------------------------------------'''
 
'''MODE 1: LOW ATMOSPHERE: 0- 3 km'''
# opObj10 = procUnitConfObj1.addOperation(name='SnrFilter')
# opObj10.addParameter(name='snr_val', value='-10', format='float')
# opObj10.addParameter(name='modetofilter', value='1', format='int')
#    
# opObj10 = procUnitConfObj1.addOperation(name='OutliersFilter')
# opObj10.addParameter(name='svalue', value='meridional', format='str')
# opObj10.addParameter(name='svalue2', value='inTime', format='str')
# opObj10.addParameter(name='method', value='0', format='float')
# opObj10.addParameter(name='factor', value='1', format='float')
# opObj10.addParameter(name='filter', value='0', format='float')
# opObj10.addParameter(name='npoints', value='5', format='float')
# opObj10.addParameter(name='modetofilter', value='1', format='int')
# # 
# opObj10 = procUnitConfObj1.addOperation(name='OutliersFilter')
# opObj10.addParameter(name='svalue', value='zonal', format='str')
# opObj10.addParameter(name='svalue2', value='inTime', format='str')
# opObj10.addParameter(name='method', value='0', format='float')
# opObj10.addParameter(name='factor', value='1', format='float')
# opObj10.addParameter(name='filter', value='0', format='float')
# opObj10.addParameter(name='npoints', value='5', format='float')
# opObj10.addParameter(name='modetofilter', value='1', format='int')
# #     
# opObj10 = procUnitConfObj1.addOperation(name='OutliersFilter')
# opObj10.addParameter(name='svalue', value='vertical', format='str')
# opObj10.addParameter(name='svalue2', value='inHeight', format='str')
# opObj10.addParameter(name='method', value='0', format='float')
# opObj10.addParameter(name='factor', value='2', format='float')
# opObj10.addParameter(name='filter', value='0', format='float')
# opObj10.addParameter(name='npoints', value='9', format='float')
# opObj10.addParameter(name='modetofilter', value='1', format='int')
#  
  
''' MODE 2: 0 - 10 km '''
 
opObj10 = procUnitConfObj1.addOperation(name='SnrFilter')
opObj10.addParameter(name='snr_val', value='-20', format='float')
opObj10.addParameter(name='modetofilter', value='2', format='int')
   
opObj10 = procUnitConfObj1.addOperation(name='OutliersFilter')
opObj10.addParameter(name='svalue', value='meridional', format='str')
opObj10.addParameter(name='svalue2', value='inTime', format='str')
opObj10.addParameter(name='method', value='0', format='float')
opObj10.addParameter(name='factor', value='2', format='float')
opObj10.addParameter(name='filter', value='0', format='float')
opObj10.addParameter(name='npoints', value='9', format='float')
opObj10.addParameter(name='modetofilter', value='2', format='int')
# # 
opObj10 = procUnitConfObj1.addOperation(name='OutliersFilter')
opObj10.addParameter(name='svalue', value='zonal', format='str')
opObj10.addParameter(name='svalue2', value='inTime', format='str')
opObj10.addParameter(name='method', value='0', format='float')
opObj10.addParameter(name='factor', value='2', format='float')
opObj10.addParameter(name='filter', value='0', format='float')
opObj10.addParameter(name='npoints', value='9', format='float')
opObj10.addParameter(name='modetofilter', value='2', format='int')
# #     
opObj10 = procUnitConfObj1.addOperation(name='OutliersFilter')
opObj10.addParameter(name='svalue', value='vertical', format='str')
opObj10.addParameter(name='svalue2', value='inHeight', format='str')
opObj10.addParameter(name='method', value='0', format='float')
opObj10.addParameter(name='factor', value='2', format='float')
opObj10.addParameter(name='filter', value='0', format='float')
opObj10.addParameter(name='npoints', value='9', format='float')
opObj10.addParameter(name='modetofilter', value='2', format='int')
 
# '''-----------------------------------------Writing-------------------------------------------'''
# 
# # opObj10 =  procUnitConfObj1.addOperation(name='testBLTRWriter',optype='other')
# # opObj10.addParameter(name='path', value = pathhdf5) 
# # opObj10.addParameter(name='modetowrite', value = '2',format='int') 
# #    
# # opObj10 =  procUnitConfObj1.addOperation(name='testBLTRWriter',optype='other')
# # opObj10.addParameter(name='path', value = pathhdf5) 
# # opObj10.addParameter(name='modetowrite', value = '1',format='int') 
# 
# '''----------------------------------------Plotting--------------------------------------------'''
# 
opObj10 = procUnitConfObj1.addOperation(name='prePlot')
opObj10.addParameter(name='modeselect',value='1',format='int')
# #  
opObj10 = procUnitConfObj1.addOperation(name='WindProfilerPlot', optype='other')
opObj10.addParameter(name='id', value='1', format='int')
opObj10.addParameter(name='wintitle', value='', format='str')
opObj10.addParameter(name='channelList', value='0', format='intlist') 
#opObj10.addParameter(name='save', value='1', format='bool')
#opObj10.addParameter(name='figpath', value=figpath, format='str')
opObj10.addParameter(name='SNRmin', value='-10', format='int')
opObj10.addParameter(name='SNRmax', value='50', format='int')
opObj10.addParameter(name='SNRthresh', value='0', format='float')
opObj10.addParameter(name='xmin', value='0', format='float')
opObj10.addParameter(name='xmax', value='24', format='float')
opObj10.addParameter(name='ymax', value='3', format='float')
opObj10.addParameter(name='zmin', value='-20', format='float')
opObj10.addParameter(name='zmax', value='20', format='float')
opObj10.addParameter(name='zmin_ver', value='-200', format='float')
opObj10.addParameter(name='zmax_ver', value='200', format='float')
#opObj10.addParameter(name='showprofile', value='1', format='bool')
#opObj10.addParameter(name='show', value='1', format='bool')
 
opObj10 = procUnitConfObj1.addOperation(name='prePlot')
opObj10.addParameter(name='modeselect',value='2',format='int')
#  
opObj10 = procUnitConfObj1.addOperation(name='WindProfilerPlot', optype='other')
opObj10.addParameter(name='id', value='2', format='int')
opObj10.addParameter(name='wintitle', value='', format='str')
#opObj10.addParameter(name='channelList', value='0', format='intlist') 
#opObj10.addParameter(name='save', value='1', format='bool')
#opObj10.addParameter(name='figpath', value=figpath, format='str')
opObj10.addParameter(name='SNRmin', value='-20', format='int')
opObj10.addParameter(name='SNRmax', value='40', format='int')
opObj10.addParameter(name='SNRthresh', value='0', format='float')
opObj10.addParameter(name='xmin', value='0', format='float')
opObj10.addParameter(name='xmax', value='24', format='float')
#opObj10.addParameter(name='ymax', value='8', format='float')
opObj10.addParameter(name='zmin', value='-4', format='float')
opObj10.addParameter(name='zmax', value='4', format='float')
opObj10.addParameter(name='zmin_ver', value='-200', format='float')
opObj10.addParameter(name='zmax_ver', value='200', format='float')
#opObj10.addParameter(name='showprofile', value='1', format='bool')
#opObj10.addParameter(name='show', value='1', format='bool')

# # print "Escribiendo el archivo XML"
# controllerObj.writeXml(filename)
# # print "Leyendo el archivo XML"
# controllerObj.readXml(filename)

# controllerObj.createObjects()
# controllerObj.connectObjects()
# controllerObj.run()
controllerObj.start()

