import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

if __name__ == '__main__':
    
    desc = "Segundo Test"
    filename = "schain.xml"
    
    controllerObj = Project()
    
    controllerObj.setup(id = '191', name='test01', description=desc)
    
    readUnitConfObj = controllerObj.addReadUnit(datatype='Spectra',
                                                path='/remote/datos/IMAGING/IMAGING2',
                                                startDate='2012/12/18',
                                                endDate='2012/12/22',
                                                startTime='00:00:00',
                                                endTime='23:59:59',
                                                online=0,
                                                walk=1,
                                                expLabel='')
    
#    opObj00 = readUnitConfObj.addOperation(name='printInfo')
    
#    procUnitConfObj1 = controllerObj.addProcUnit(datatype='Spectra', inputId=readUnitConfObj.getId())
    
#    opObj10 = procUnitConfObj0.addOperation(name='selectChannels')
#    opObj10.addParameter(name='channelList', value='3,4,5', format='intlist')

#    opObj10 = procUnitConfObj0.addOperation(name='selectHeights')
#    opObj10.addParameter(name='minHei', value='90', format='float')
#    opObj10.addParameter(name='maxHei', value='180', format='float')
    
#    opObj12 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
#    opObj12.addParameter(name='n', value='10', format='int')
    
#    procUnitConfObj1 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObj0.getId())
#    procUnitConfObj1.addParameter(name='nFFTPoints', value='32', format='int')
#    procUnitConfObj1.addParameter(name='pairList', value='(0,1),(0,2),(1,2)', format='')
    
    
#    opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
#    opObj11.addParameter(name='idfigure', value='1', format='int')
#    opObj11.addParameter(name='wintitle', value='SpectraPlot0', format='str')
##    opObj11.addParameter(name='zmin', value='30', format='int')
##    opObj11.addParameter(name='zmax', value='70', format='int')
#    opObj11.addParameter(name='showprofile', value='1', format='int')  
#    opObj11.addParameter(name='save', value='1', format='int')
#    opObj11.addParameter(name='figpath', value='/home/roj-idl71/tmp/graphs')
##
#    opObj11 = procUnitConfObj1.addOperation(name='CrossSpectraPlot', optype='other')
#    opObj11.addParameter(name='idfigure', value='2', format='int')
#    opObj11.addParameter(name='wintitle', value='CrossSpectraPlot', format='str')
##    opObj11.addParameter(name='zmin', value='30', format='int')
##    opObj11.addParameter(name='zmax', value='70', format='int') 
#    opObj11.addParameter(name='save', value='1', format='int')
#    opObj11.addParameter(name='figpath', value='/home/roj-idl71/tmp/graphs')
    
#            
#    opObj11 = procUnitConfObj1.addOperation(name='CoherenceMap', optype='other')
#    opObj11.addParameter(name='idfigure', value='3', format='int')
#    opObj11.addParameter(name='wintitle', value='CrossSpectraPlot', format='str')
#    opObj11.addParameter(name='zmin', value='40', format='int')
#    opObj11.addParameter(name='zmax', value='90', format='int') 
    
#    procUnitConfObj2 = controllerObj.addProcUnit(datatype='Voltage', inputId=procUnitConfObj0.getId())
#  
#    opObj12 = procUnitConfObj2.addOperation(name='CohInt', optype='other')
#    opObj12.addParameter(name='n', value='2', format='int')
#    opObj12.addParameter(name='overlapping', value='1', format='int')
#
#    procUnitConfObj3 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObj2.getId())
#    procUnitConfObj3.addParameter(name='nFFTPoints', value='32', format='int')
#    
#    opObj11 = procUnitConfObj3.addOperation(name='SpectraPlot', optype='other')
#    opObj11.addParameter(name='idfigure', value='2', format='int')
#    opObj11.addParameter(name='wintitle', value='SpectraPlot1', format='str')
#    opObj11.addParameter(name='zmin', value='40', format='int')
#    opObj11.addParameter(name='zmax', value='90', format='int')
#    opObj11.addParameter(name='showprofile', value='1', format='int') 

#    opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
#    opObj11.addParameter(name='idfigure', value='10', format='int')
#    opObj11.addParameter(name='wintitle', value='RTI', format='str')
##    opObj11.addParameter(name='xmin', value='21', format='float')
##    opObj11.addParameter(name='xmax', value='22', format='float')
#    opObj11.addParameter(name='zmin', value='40', format='int')
#    opObj11.addParameter(name='zmax', value='90', format='int')
#    opObj11.addParameter(name='showprofile', value='1', format='int')
#    opObj11.addParameter(name='timerange', value=str(60), format='int')
    
#    opObj10 = procUnitConfObj1.addOperation(name='selectChannels')
#    opObj10.addParameter(name='channelList', value='0,2,4,6', format='intlist')
#    
#    opObj12 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
#    opObj12.addParameter(name='n', value='2', format='int')
#
#    opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
#    opObj11.addParameter(name='idfigure', value='2', format='int')
#    opObj11.addParameter(name='wintitle', value='SpectraPlot10', format='str')
#    opObj11.addParameter(name='zmin', value='70', format='int')
#    opObj11.addParameter(name='zmax', value='90', format='int')
#
#    opObj10 = procUnitConfObj1.addOperation(name='selectChannels')
#    opObj10.addParameter(name='channelList', value='2,6', format='intlist')
#    
#    opObj12 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
#    opObj12.addParameter(name='n', value='2', format='int')
#
#    opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
#    opObj11.addParameter(name='idfigure', value='3', format='int')
#    opObj11.addParameter(name='wintitle', value='SpectraPlot10', format='str')
#    opObj11.addParameter(name='zmin', value='70', format='int')
#    opObj11.addParameter(name='zmax', value='90', format='int')
    
          
#    opObj12 = procUnitConfObj1.addOperation(name='decoder')
#    opObj12.addParameter(name='ncode', value='2', format='int')
#    opObj12.addParameter(name='nbauds', value='8', format='int')
#    opObj12.addParameter(name='code0', value='001110011', format='int')
#    opObj12.addParameter(name='code1', value='001110011', format='int')  
  


#    procUnitConfObj2 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObj1.getId())
#    
#    opObj21 = procUnitConfObj2.addOperation(name='IncohInt', optype='other')
#    opObj21.addParameter(name='n', value='2', format='int')
#    
#    opObj11 = procUnitConfObj2.addOperation(name='SpectraPlot', optype='other')
#    opObj11.addParameter(name='idfigure', value='4', format='int')
#    opObj11.addParameter(name='wintitle', value='SpectraPlot OBJ 2', format='str')
#    opObj11.addParameter(name='zmin', value='70', format='int')
#    opObj11.addParameter(name='zmax', value='90', format='int')
      
    print "Escribiendo el archivo XML"
    
    controllerObj.writeXml(filename)
    
    print "Leyendo el archivo XML"
    controllerObj.readXml(filename)
    #controllerObj.printattr()
    
    controllerObj.createObjects()
    controllerObj.connectObjects()
    controllerObj.run()