#!/usr/bin/env python
import os, sys

# path = os.path.dirname(os.getcwd())
# path = os.path.join(path, 'source')
# sys.path.insert(0, '../')

from schainpy.controller import Project

xmin = '15.5'
xmax = '24'


desc = "ProcBLTR Test"
filename = "ProcBLTR.xml"
figpath = '/media/erick/6F60F7113095A154/BLTR' 
    
controllerObj = Project()
    
    
controllerObj.setup(id='191', name='test01', description=desc)
    
readUnitConfObj = controllerObj.addReadUnit(datatype='BLTRReader',
                                                path='/media/erick/6F60F7113095A154/BLTR/',
                                                
                                                endDate='2017/10/19',
                                                startTime='13:00:00',
                                                startDate='2016/11/8',
                                                endTime='23:59:59',
               
            
                                                online=0,
                                                walk=0,
                                                ReadMode='1')
                                                # expLabel='')
    
# opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')
    
procUnitConfObj1 = controllerObj.addProcUnit(datatype='Spectra', inputId=readUnitConfObj.getId())



opObj11 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
opObj11.addParameter(name='n', value='3', format='float')

opObj10 = procUnitConfObj1.addOperation(name='removeDC')

# opObj10 = procUnitConfObj1.addOperation(name='calcMag')

# opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
# opObj11.addParameter(name='id', value='21', format='int')
# opObj11.addParameter(name='wintitle', value='SpectraCutPlot', format='str')
# opObj11.addParameter(name='xaxis', value='frequency', format='str')
# opObj11.addParameter(name='colormap', value='winter', format='str')
# opObj11.addParameter(name='xmin', value='-0.005', format='float')
# opObj11.addParameter(name='xmax', value='0.005', format='float')
# #opObj10 = procUnitConfObj1.addOperation(name='selectChannels')
# #opObj10.addParameter(name='channelList', value='0,1', format='intlist')    
# opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
# opObj11.addParameter(name='id', value='21', format='int')
# opObj11.addParameter(name='wintitle', value='SpectraPlot', format='str')
# #opObj11.addParameter(name='xaxis', value='Velocity', format='str')

# opObj11.addParameter(name='xaxis', value='velocity', format='str')
# opObj11.addParameter(name='xmin', value='-0.005', format='float')
# opObj11.addParameter(name='xmax', value='0.005', format='float')

# opObj11.addParameter(name='ymin', value='225', format='float')
# opObj11.addParameter(name='ymax', value='3000', format='float')
# opObj11.addParameter(name='zmin', value='-100', format='int')
# opObj11.addParameter(name='zmax', value='-65', format='int')    

# opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
# opObj11.addParameter(name='id', value='10', format='int')
# opObj11.addParameter(name='wintitle', value='RTI', format='str')
 # opObj11.addParameter(name='ymin', value='0', format='float')
 # opObj11.addParameter(name='ymax', value='4000', format='float')
# #opObj11.addParameter(name='zmin', value='-100', format='int')
# #opObj11.addParameter(name='zmax', value='-70', format='int')
 # opObj11.addParameter(name='zmin', value='-90', format='int')
 # opObj11.addParameter(name='zmax', value='-40', format='int')
# opObj11.addParameter(name='showprofile', value='1', format='int')
# opObj11.addParameter(name='timerange', value=str(2*60*60), format='int')

opObj11 = procUnitConfObj1.addOperation(name='CrossSpectraPlot', optype='other')
procUnitConfObj1.addParameter(name='pairsList', value='(0,1),(0,2),(1,2)', format='pairsList')
opObj11.addParameter(name='id', value='2005', format='int')
opObj11.addParameter(name='wintitle', value='CrossSpectraPlot_ShortPulse', format='str')
# opObj11.addParameter(name='exp_code', value='13', format='int')
opObj11.addParameter(name='xaxis', value='Velocity', format='str')
#opObj11.addParameter(name='xmin', value='-10', format='float')
#opObj11.addParameter(name='xmax', value='10', format='float')
#opObj11.addParameter(name='ymin', value='225', format='float')
#opObj11.addParameter(name='ymax', value='3000', format='float')
#opObj11.addParameter(name='phase_min', value='-4', format='int')
#opObj11.addParameter(name='phase_max', value='4', format='int')

# procUnitConfObj2 = controllerObj.addProcUnit(datatype='CorrelationProc', inputId=procUnitConfObj1.getId())
# procUnitConfObj2.addParameter(name='pairsList', value='(0,1),(0,2),(1,2)', format='pairsList')

procUnitConfObj2 = controllerObj.addProcUnit(datatype='Parameters', inputId=procUnitConfObj1.getId())
opObj11 = procUnitConfObj2.addOperation(name='SpectralMoments', optype='other')
opObj22 = procUnitConfObj2.addOperation(name='FullSpectralAnalysis', optype='other')
# 
opObj22 = procUnitConfObj2.addOperation(name='WindProfilerPlot', optype='other')
opObj22.addParameter(name='id', value='4', format='int')
opObj22.addParameter(name='wintitle', value='Wind Profiler', format='str')
opObj22.addParameter(name='save', value='1', format='bool')
# opObj22.addParameter(name='figpath', value = '/home/erick/Pictures', format='str')

opObj22.addParameter(name='zmin', value='-20', format='int')
opObj22.addParameter(name='zmax', value='20', format='int')
opObj22.addParameter(name='zmin_ver', value='-250', format='float')
opObj22.addParameter(name='zmax_ver', value='250', format='float')
opObj22.addParameter(name='SNRmin', value='-5', format='int')
opObj22.addParameter(name='SNRmax', value='30', format='int')
# opObj22.addParameter(name='SNRthresh', value='-3.5', format='float')
opObj22.addParameter(name='xmin', value=0, format='float')
opObj22.addParameter(name='xmax', value=24, format='float')
opObj22.addParameter(name='ymin', value='225', format='float')
#opObj22.addParameter(name='ymax', value='2000', format='float')
opObj22.addParameter(name='save', value='1', format='int')
opObj22.addParameter(name='figpath', value=figpath, format='str')


# opObj11.addParameter(name='pairlist', value='(1,0),(0,2),(1,2)', format='pairsList')
#opObj10 = procUnitConfObj1.addOperation(name='selectHeights')
#opObj10.addParameter(name='minHei', value='225', format='float')
#opObj10.addParameter(name='maxHei', value='1000', format='float')         

# opObj11 = procUnitConfObj1.addOperation(name='CoherenceMap', optype='other')
# opObj11.addParameter(name='id', value='102', format='int')
# opObj11.addParameter(name='wintitle', value='Coherence', format='str')
# opObj11.addParameter(name='ymin', value='225', format='float')
# opObj11.addParameter(name='ymax', value='4000', format='float')

# opObj11.addParameter(name='phase_cmap', value='jet', format='str')
# opObj11.addParameter(name='xmin', value='8.5', format='float')
# opObj11.addParameter(name='xmax', value='9.5', format='float')
# opObj11.addParameter(name='figpath', value=figpath, format='str')
# opObj11.addParameter(name='save', value=1, format='bool')
# opObj11.addParameter(name='pairsList', value='(1,0),(3,2)', format='pairsList')

# opObj12 = procUnitConfObj1.addOperation(name='PublishData', optype='other')
# opObj12.addParameter(name='zeromq', value=1, format='int')
# opObj12.addParameter(name='verbose', value=0, format='bool')
# opObj12.addParameter(name='server', value='erick2', format='str')
controllerObj.start()


