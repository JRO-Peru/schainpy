from controller import *

if __name__ == '__main__':
    
    desc = "Segundo Test"
    filename = "schain.xml"
    
    controllerObj = Project()
    
    controllerObj.setup(id = '191', name='test01', description=desc)
    
    readUnitConfObj = controllerObj.addReadUnit(datatype='Voltage',
                                                path='/remote/puma/2012_06/Meteors',
                                                startDate='2012/06/21',
                                                endDate='2012/06/21',
                                                startTime='04:00:00',
                                                endTime='05:59:59',
                                                online=0,
                                                walk=1)
    
#    opObj00 = readUnitConfObj.addOperation(name='printInfo')
    
    procUnitConfObj0 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())
    
    opObj10 = procUnitConfObj0.addOperation(name='selectChannels')
    opObj10.addParameter(name='channelList', value='0,1,2', format='intlist')
#
    opObj10 = procUnitConfObj0.addOperation(name='selectHeights')
    opObj10.addParameter(name='minHei', value='140', format='float')
    opObj10.addParameter(name='maxHei', value='180', format='float')

    opObj12 = procUnitConfObj0.addOperation(name='Decoder', optype='other')
    
    opObj12 = procUnitConfObj0.addOperation(name='CohInt', optype='other')
    opObj12.addParameter(name='n', value='4', format='int')

#    opObj11 = procUnitConfObj0.addOperation(name='Scope', optype='other')
#    opObj11.addParameter(name='idfigure', value='10', format='int')
#    opObj11.addParameter(name='wintitle', value='Voltage', format='str')
#    opObj11.addParameter(name='zmin', value='40', format='int')
#    opObj11.addParameter(name='zmax', value='90', format='int')
    
    procUnitConfObj1 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObj0.getId())
    procUnitConfObj1.addParameter(name='nFFTPoints', value='16', format='int')
    procUnitConfObj1.addParameter(name='pairsList', value='(0,1),(0,2),(1,2)', format='pairslist')
    

    opObj12 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
    opObj12.addParameter(name='n', value='10', format='int')
    
    opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
    opObj11.addParameter(name='idfigure', value='1', format='int')
    opObj11.addParameter(name='wintitle', value='SpectraPlot0', format='str')
    opObj11.addParameter(name='zmin', value='35', format='int')
    opObj11.addParameter(name='zmax', value='90', format='int')
    opObj11.addParameter(name='showprofile', value='1', format='int')
    opObj11.addParameter(name='figpath', value='/home/roj-idl71/Data/RAWDATA/BIESTATIC/RAWDATA_8CH/graphs')
    opObj11.addParameter(name='save', value='1', format='int')

    opObj11 = procUnitConfObj1.addOperation(name='CrossSpectraPlot', optype='other')
    opObj11.addParameter(name='idfigure', value='2', format='int')
    opObj11.addParameter(name='wintitle', value='CrossSpectraPlot', format='str')
    opObj11.addParameter(name='zmin', value='35', format='int')
    opObj11.addParameter(name='zmax', value='90', format='int')
    opObj11.addParameter(name='figpath', value='/home/roj-idl71/Data/RAWDATA/BIESTATIC/RAWDATA_8CH/graphs')
    opObj11.addParameter(name='save', value='1', format='int')
            

    opObj11 = procUnitConfObj1.addOperation(name='CoherenceMap', optype='other')
    opObj11.addParameter(name='idfigure', value='3', format='int')
    opObj11.addParameter(name='wintitle', value='CoherenciaMap', format='str')
#    opObj11.addParameter(name='timerange', value=str(60), format='int')
    opObj11.addParameter(name='figpath', value='/home/roj-idl71/Data/RAWDATA/BIESTATIC/RAWDATA_8CH/graphs')
    opObj11.addParameter(name='save', value='1', format='int')
    
    opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
    opObj11.addParameter(name='idfigure', value='4', format='int')
    opObj11.addParameter(name='wintitle', value='RTI', format='str')
#    opObj11.addParameter(name='timerange', value=str(60*60), format='int')
    opObj11.addParameter(name='zmin', value='35', format='int')
    opObj11.addParameter(name='zmax', value='90', format='int')
    opObj11.addParameter(name='figpath', value='/home/roj-idl71/Data/RAWDATA/BIESTATIC/RAWDATA_8CH/graphs')
    opObj11.addParameter(name='save', value='1', format='int')
    
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