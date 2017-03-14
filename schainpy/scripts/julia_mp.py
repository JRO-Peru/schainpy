#!/usr/bin/env python
'''
Created on Jul 7, 2014

@author: roj-idl71
'''
import os, sys
from datetime import datetime, timedelta
import multiprocessing
from schainpy.controller import Project

def main(date):

    controllerObj = Project()

    controllerObj.setup(id = '191', name='test01', description='')

    readUnitConfObj = controllerObj.addReadUnit(datatype='Spectra',
                                                path='/data/workspace/data/zeus/',
                                                startDate=date,
                                                endDate=date,
                                                startTime='00:00:00',
                                                endTime='23:59:59',
                                                online=0,
                                                walk=1,
                                                expLabel='')

    procUnitConfObj1 = controllerObj.addProcUnit(datatype='Spectra', inputId=readUnitConfObj.getId())
    #opObj11 = procUnitConfObj1.addOperation(name='removeDC')
    #opObj11.addParameter(name='mode', value='1', format='int')

    #opObj11 = procUnitConfObj1.addOperation(name='removeInterference')


#     opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
#     opObj11.addParameter(name='id', value='10', format='int')
#     opObj11.addParameter(name='wintitle', value='150Km', format='str')
#     opObj11.addParameter(name='colormap', value='jro', format='str')
#     opObj11.addParameter(name='xaxis', value='time', format='str')
#     opObj11.addParameter(name='xmin', value='0', format='int')
#     opObj11.addParameter(name='xmax', value='23', format='int')
#     #opObj11.addParameter(name='ymin', value='100', format='int')
#     #opObj11.addParameter(name='ymax', value='150', format='int')
#     opObj11.addParameter(name='zmin', value='10', format='int')
#     opObj11.addParameter(name='zmax', value='35', format='int')

    


    opObj11 = procUnitConfObj1.addOperation(name='PlotRTIData', optype='other')
    opObj11.addParameter(name='id', value='12', format='int')
    opObj11.addParameter(name='wintitle', value='150Km', format='str')
    opObj11.addParameter(name='colormap', value='jro', format='str')
    opObj11.addParameter(name='xaxis', value='time', format='str')
    opObj11.addParameter(name='xmin', value='0', format='int')
    opObj11.addParameter(name='xmax', value='23', format='int')
    #opObj11.addParameter(name='ymin', value='100', format='int')
    #opObj11.addParameter(name='ymax', value='150', format='int')
    opObj11.addParameter(name='zmin', value='10', format='int')
    opObj11.addParameter(name='zmax', value='35', format='int')
    #opObj11.addParameter(name='pause', value='1', format='bool')
    opObj11.addParameter(name='show', value='0', format='bool')
    opObj11.addParameter(name='save', value='/tmp', format='str')


    controllerObj.start()

if __name__=='__main__':
    
    dt = datetime(2017, 1, 12)
    
    dates = [(dt+timedelta(x)).strftime('%Y/%m/%d')  for x in range(20)]
    
    p = multiprocessing.Pool(4)
    p.map(main, dates)
    
    