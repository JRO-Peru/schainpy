#!/usr/bin/env python
'''
Created on Jul 7, 2014

@author: roj-idl71
'''
import os, sys
from Queue import Queue
from time import sleep

from schainpy.controller_api import ControllerThread
from schainpy.model.graphics.jroplotter import PlotManager

def main():
    desc = "Segundo Test"
    filename = "schain.xml"
    
    controllerObj = ControllerThread()
    
    controllerObj.setup(id = '191', name='test01', description=desc)
    
    readUnitConfObj = controllerObj.addReadUnit(datatype='Spectra',
                                                path='../data/pdata/',
                                                startDate='2010/12/18',
                                                endDate='2015/12/22',
                                                startTime='00:00:00',
                                                endTime='23:59:59',
                                                online=0,
                                                walk=0,
                                                expLabel='')
    
    procUnitConfObj1 = controllerObj.addProcUnit(datatype='Spectra', inputId=readUnitConfObj.getId())
    
    opObj10 = procUnitConfObj1.addOperation(name='selectChannels')
    opObj10.addParameter(name='channelList', value='0,1', format='intlist')

    opObj10 = procUnitConfObj1.addOperation(name='selectHeights')
    opObj10.addParameter(name='minHei', value='90', format='float')
    opObj10.addParameter(name='maxHei', value='180', format='float')
    
    opObj10 = procUnitConfObj1.addOperation(name='removeDC')
    
    opObj12 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
    opObj12.addParameter(name='n', value='1', format='int')
    
    opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
    opObj11.addParameter(name='id', value='1', format='int')
    opObj11.addParameter(name='wintitle', value='SpectraPlot0', format='str')
    opObj11.addParameter(name='showprofile', value='1', format='int')  
    opObj11.addParameter(name='save', value='0', format='int')
    opObj11.addParameter(name='figpath', value='/Users/miguel/Data/JULIA/pdata/graphs')
 
    opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
    opObj11.addParameter(name='id', value='10', format='int')
    opObj11.addParameter(name='wintitle', value='RTI', format='str')
    opObj11.addParameter(name='xmin', value='21', format='float')
    opObj11.addParameter(name='xmax', value='22', format='float')
    opObj11.addParameter(name='zmin', value='12', format='int')
    opObj11.addParameter(name='zmax', value='32', format='int')
    opObj11.addParameter(name='showprofile', value='1', format='int')
    opObj11.addParameter(name='timerange', value=str(2*60*60), format='int')
    
    ########################################
    #Configure use of external plotter before start
    plotterObj = controllerObj.useExternalPlotter()
    ########################################
    
    controllerObj.start()
    
    plotterObj.start()
    
if __name__ == '__main__':
    import time
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
