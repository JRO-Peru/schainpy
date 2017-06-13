#!/usr/bin/env python
import os, sys

path = os.path.dirname(os.getcwd())
path = os.path.join(path, 'source')
sys.path.insert(0, path)

from schainpy.controller import Project
    

desc = "ProcBLTR Test"
filename = "ProcBLTR.xml"
    
controllerObj = Project()
    
controllerObj.setup(id = '191', name='test01', description=desc)
    
readUnitConfObj = controllerObj.addReadUnit(datatype='BLTRReader',
                                                path='/home/erick/Documents/Data/', 
                                                startDate='2016/10/19',
                                                endDate='2016/10/19',
                                                startTime='21:00:00',
                                                endTime='23:59:59',
                                                online=0,
                                                walk=0)
                                                #expLabel='')
    
opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')
    
procUnitConfObj1 = controllerObj.addProcUnit(datatype='SpectraProc', inputId=readUnitConfObj.getId())
    
opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='id', value='21', format='int')
opObj11.addParameter(name='wintitle', value='SpectraPlot', format='str')
            
print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)            
                                                
controllerObj.printattr()
controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()
