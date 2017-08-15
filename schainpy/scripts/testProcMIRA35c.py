#!/usr/bin/env python
import os, sys

path = os.path.dirname(os.getcwd())
path = os.path.join(path, 'source')
sys.path.insert(0, '../')

from controller import Project

xmin = '15.5'
xmax = '24'

desc = "ProcBLTR Test"


filename = "ProcBLTR.xml"

controllerObj = Project()


controllerObj.setup(id = '191', name='test01', description=desc)

readUnitConfObj = controllerObj.addReadUnit(datatype='MIRA35CReader',
                                                path='/home/erick/Documents/MIRA35C/20160117', 
                                                startDate='2016/11/8',                
                                                endDate='2017/10/19',
                                                startTime='13:00:00',
                                                
                                                endTime='23:59:59',
                                                
                                                
                                                online=0,
                                                walk=0)
                                                

#opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')

procUnitConfObj1 = controllerObj.addProcUnit(datatype='Spectra', inputId=readUnitConfObj.getId())




opObj11 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
opObj11.addParameter(name='n', value='1', format='float')

opObj10 = procUnitConfObj1.addOperation(name='removeDC')

#opObj10 = procUnitConfObj1.addOperation(name='calcMag')

# #opObj10 = procUnitConfObj1.addOperation(name='selectChannels')
# #opObj10.addParameter(name='channelList', value='0,1', format='intlist')

opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='id', value='21', format='int')
opObj11.addParameter(name='wintitle', value='SpectraCutPlot', format='str')
opObj11.addParameter(name='xaxis', value='velocity', format='str')
opObj11.addParameter(name='colormap', value='nipy_spectral', format='str')
opObj11.addParameter(name='normFactor', value='1', format='float')
#opObj11.addParameter(name='xaxis', value='velocity', format='str')
#opObj11.addParameter(name='xmin', value='-1.', format='float')

#opObj11.addParameter(name='xmax', value='1.', format='float')

#opObj11.addParameter(name='ymin', value='0', format='float')
#opObj11.addParameter(name='ymax', value='5000', format='float')
opObj11.addParameter(name='zmin', value='-20', format='int')
opObj11.addParameter(name='zmax', value='20', format='int')    

opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
opObj11.addParameter(name='id', value='10', format='int')
opObj11.addParameter(name='wintitle', value='RTI', format='str')
opObj11.addParameter(name='colormap', value='nipy_spectral', format='str')
#opObj11.addParameter(name='ymin', value='0', format='float')
#opObj11.addParameter(name='ymax', value='5000', format='float')
opObj11.addParameter(name='normFactor', value='1', format='float')
#opObj11.addParameter(name='xmin', value='0', format='float')
#opObj11.addParameter(name='xmax', value='24', format='float')
opObj11.addParameter(name='zmin', value='-20', format='int')
opObj11.addParameter(name='zmax', value='20', format='int')
opObj11.addParameter(name='timerange', value='10800', format='int')
opObj11.addParameter(name='HEIGHT', value='400', format='int')
 # opObj11.addParameter(name='zmin', value='-90', format='int')
 # opObj11.addParameter(name='zmax', value='-40', format='int')
#opObj11.addParameter(name='showprofile', value='1', format='int')
#opObj11.addParameter(name='timerange', value=str(2*60*60), format='int')

procUnitConfObj2 = controllerObj.addProcUnit(datatype='Parameters', inputId=readUnitConfObj.getId())
#opObj11 = procUnitConfObj2.addOperation(name='SpectralMoments', optype='other')
opObj22 = procUnitConfObj2.addOperation(name='PrecipitationProc', optype='other')
opObj22.addParameter(name='radar', value='MIRA35C', format='str')

opObj22 = procUnitConfObj2.addOperation(name='ParametersPlot', optype='other')
opObj22.addParameter(name='id', value='4', format='int')
opObj22.addParameter(name='wintitle', value='PrecipitationProc', format='str')
opObj22.addParameter(name='save', value='1', format='bool')
opObj22.addParameter(name='colormap', value='nipy_spectral', format='str')
# opObj22.addParameter(name='figpath', value = '/home/erick/Pictures', format='str')
opObj22.addParameter(name='zmin', value='-60', format='int')
opObj22.addParameter(name='zmax', value='-20', format='int')  
opObj22.addParameter(name='timerange', value='10800', format='int')
#opObj22.addParameter(name='channelList', value='0', format='intlist')
#opObj22.addParameter(name='colormap', value='nipy_spectral', format='str')
opObj22.addParameter(name='HEIGHT', value='500', format='int')
#opObj22.addParameter(name='zmin_ver', value='-250', format='float')
#opObj22.addParameter(name='zmax_ver', value='250', format='float')
#opObj22.addParameter(name='SNRmin', value='-5', format='int')
#opObj22.addParameter(name='SNRmax', value='30', format='int')
# opObj22.addParameter(name='SNRthresh', value='-3.5', format='float')
#opObj22.addParameter(name='xmin', value=0, format='float')
#opObj22.addParameter(name='xmax', value=2, format='float')
#opObj22.addParameter(name='ymin', value='225', format='float')
#opObj22.addParameter(name='ymax', value='5000', format='float')

# opObj12 = procUnitConfObj1.addOperation(name='PublishData', optype='other')
# opObj12.addParameter(name='zeromq', value=1, format='int')
# opObj12.addParameter(name='verbose', value=0, format='bool')
# opObj12.addParameter(name='server', value='Jose', format='str')

#controllerObj.createObjects()
#controllerObj.connectObjects()
controllerObj.start()
