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
path = '/home/erick/Documents/Data/BLTR_Data/sswma/'#'/media/erick/6F60F7113095A154/BLTR/'    
desc = "read bltr data sswma file"
figpath = '/media/erick/6F60F7113095A154/BLTR/' 
pathhdf5 = '/tmp/'

controllerObj = Project()

controllerObj.setup(id = '191', name='test1', description=desc)
readUnitConfObj = controllerObj.addReadUnit(datatype='BLTRParamReader',
                                            path=path,
                                            startDate='2017/01/17',
                                            endDate='2018/01/01',
                                            startTime='06:00:00',
                                            endTime='23:59:59',
                                            verbose=0,
                                            )                    

procUnitConfObj1 = controllerObj.addProcUnit(datatype='BLTRParametersProc', 
                                             inputId=readUnitConfObj.getId())

procUnitConfObj1.addParameter(name='mode', value='1', format='int')
# procUnitConfObj1.addParameter(name='snr_threshold', value='10', format='float')
 

opObj10 = procUnitConfObj1.addOperation(name='WindProfilerPlot', optype='other')
opObj10.addParameter(name='id', value='2', format='int')
opObj10.addParameter(name='wintitle', value='', format='str')
 
# opObj10.addParameter(name='save', value='1', format='bool')
# opObj10.addParameter(name='figpath', value=figpath, format='str')
opObj10.addParameter(name='SNRmin', value='-20', format='int')
opObj10.addParameter(name='SNRmax', value='40', format='int')
opObj10.addParameter(name='SNRthresh', value='0', format='float')
opObj10.addParameter(name='xmin', value='0', format='float')
opObj10.addParameter(name='xmax', value='24', format='float')
opObj10.addParameter(name='ymin', value='0', format='float')
opObj10.addParameter(name='ymax', value='7', format='float')
opObj10.addParameter(name='zmin', value='-4', format='float')
opObj10.addParameter(name='zmax', value='4', format='float')
opObj10.addParameter(name='zmin_ver', value='-200', format='float')
opObj10.addParameter(name='zmax_ver', value='200', format='float')
#opObj10.addParameter(name='showprofile', value='1', format='bool')
#opObj10.addParameter(name='show', value='1', format='bool')

controllerObj.start()

