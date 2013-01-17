from controller import *

def meteors():
    
    desc = "Segundo Test"
    filename = "schain.xml"
    
    controllerObj = Project()
    
    controllerObj.setup(id = '191', name='test01', description=desc)
    
    readUnitConfObj = controllerObj.addReadUnit(datatype='Voltage',
                                                path='/Data/Data/RAWDATA/Meteors',
                                                startDate='2012/06/20',
                                                endDate='2012/06/20',
                                                startTime='04:00:00',
                                                endTime='06:00:00',
                                                online=0,
                                                walk=1)
    
    ##  if you want to look at the coded data, process only channels 0, 1, 2 
    ##  and ranges between 80 and 130 km. Then you need to input the code we are using for proper decoding.
    
#    procUnitConfObj0 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())
#    
#    opObj10 = procUnitConfObj0.addOperation(name='selectChannels')
#    opObj10.addParameter(name='channelList', value='0,1,2', format='intlist')
#
#    opObj10 = procUnitConfObj0.addOperation(name='selectHeights')
#    opObj10.addParameter(name='minHei', value='80', format='float')
#    opObj10.addParameter(name='maxHei', value='130', format='float')
#
#    opObj12 = procUnitConfObj0.addOperation(name='Decoder', optype='other')
#    
#    opObj12 = procUnitConfObj0.addOperation(name='CohInt', optype='other')
#    opObj12.addParameter(name='n', value='4', format='int')
#    
#    procUnitConfObj1 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObj0.getId())
#    procUnitConfObj1.addParameter(name='nFFTPoints', value='16', format='int')
#    procUnitConfObj1.addParameter(name='pairsList', value='(0,1),(0,2),(1,2)', format='pairslist')
#
#    opObj12 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
#    opObj12.addParameter(name='n', value='10', format='int')
    
#    opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
#    opObj11.addParameter(name='idfigure', value='1', format='int')
#    opObj11.addParameter(name='wintitle', value='LongPulse', format='str')
#    opObj11.addParameter(name='zmin', value='35', format='int')
#    opObj11.addParameter(name='zmax', value='90', format='int')
#    opObj11.addParameter(name='showprofile', value='1', format='int')
#    opObj11.addParameter(name='figpath', value='/home/roj-idl71/Data/RAWDATA/Meteors/graphs')
#    opObj11.addParameter(name='save', value='1', format='int')
#
#    opObj11 = procUnitConfObj1.addOperation(name='CrossSpectraPlot', optype='other')
#    opObj11.addParameter(name='idfigure', value='2', format='int')
#    opObj11.addParameter(name='wintitle', value='LongPulse', format='str')
#    opObj11.addParameter(name='zmin', value='35', format='int')
#    opObj11.addParameter(name='zmax', value='90', format='int')
#    opObj11.addParameter(name='figpath', value='/home/roj-idl71/Data/RAWDATA/Meteors/graphs')
#    opObj11.addParameter(name='save', value='1', format='int')
    
#    opObj11 = procUnitConfObj1.addOperation(name='CoherenceMap', optype='other')
#    opObj11.addParameter(name='idfigure', value='3', format='int')
#    opObj11.addParameter(name='wintitle', value='LongPulse', format='str')
#    opObj11.addParameter(name='zmin', value='10', format='int')
#    opObj11.addParameter(name='zmax', value='90', format='int')    
#    opObj11.addParameter(name='figpath', value='/home/roj-idl71/Data/RAWDATA/Meteors/graphs')
#    opObj11.addParameter(name='save', value='1', format='int')
#    opObj11.addParameter(name='timerange', value=2*60*60, format='int')
#    
#    opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
#    opObj11.addParameter(name='idfigure', value='4', format='int')
#    opObj11.addParameter(name='wintitle', value='LongPulse', format='str')
#    opObj11.addParameter(name='zmin', value='10', format='int')
#    opObj11.addParameter(name='zmax', value='90', format='int')
#    opObj11.addParameter(name='figpath', value='/home/roj-idl71/Data/RAWDATA/Meteors/graphs')
#    opObj11.addParameter(name='save', value='1', format='int')
#    opObj11.addParameter(name='timerange', value=2*60*60, format='int')
    
    ##
    ## For the narrow pulse data, process channels 3,4 and 5 and ranges 140 km and above (remember
    ## this pulse was shifted 60 km). In this processing you don't need to add a code.
    ##
    
    procUnitConfObj0 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())
    
#    opObj10 = procUnitConfObj0.addOperation(name='selectChannels')
#    opObj10.addParameter(name='channelList', value='3,4,5', format='intlist')

    opObj10 = procUnitConfObj0.addOperation(name='selectHeights')
    opObj10.addParameter(name='minHei', value='140', format='float')
    opObj10.addParameter(name='maxHei', value='180', format='float')
    
    opObj12 = procUnitConfObj0.addOperation(name='CohInt', optype='other')
    opObj12.addParameter(name='n', value='4', format='int')
    
    procUnitConfObj1 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObj0.getId())
    procUnitConfObj1.addParameter(name='nFFTPoints', value='16', format='int')
    procUnitConfObj1.addParameter(name='pairsList', value='(0,1),(0,2),(1,2)', format='pairslist')

    opObj12 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
    opObj12.addParameter(name='n', value='10', format='int')
    
#    opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
#    opObj11.addParameter(name='idfigure', value='11', format='int')
#    opObj11.addParameter(name='wintitle', value='NarrowPulse', format='str')
#    opObj11.addParameter(name='zmin', value='35', format='int')
#    opObj11.addParameter(name='zmax', value='90', format='int')
#    opObj11.addParameter(name='showprofile', value='1', format='int')
#    opObj11.addParameter(name='figpath', value='/home/roj-idl71/Data/RAWDATA/Meteors/graphs')
#    opObj11.addParameter(name='save', value='1', format='int')
#
    opObj11 = procUnitConfObj1.addOperation(name='CrossSpectraPlot', optype='other')
    opObj11.addParameter(name='idfigure', value='12', format='int')
    opObj11.addParameter(name='wintitle', value='NarrowPulse', format='str')
#    opObj11.addParameter(name='zmin', value='15', format='int')
#    opObj11.addParameter(name='zmax', value='60', format='int')
    opObj11.addParameter(name='figpath', value='/home/roj-idl71/Data/RAWDATA/Meteors/graphs')
    opObj11.addParameter(name='save', value='1', format='int')
#    
    opObj11 = procUnitConfObj1.addOperation(name='CoherenceMap', optype='other')
    opObj11.addParameter(name='idfigure', value='13', format='int')
    opObj11.addParameter(name='wintitle', value='NarrowPulse', format='str')
    opObj11.addParameter(name='figpath', value='/home/roj-idl71/Data/RAWDATA/Meteors/graphs')
    opObj11.addParameter(name='zmin', value='0', format='int')
    opObj11.addParameter(name='zmax', value='50', format='int')
    opObj11.addParameter(name='save', value='1', format='int')
    opObj11.addParameter(name='xmin', value='4', format='int')
    opObj11.addParameter(name='xmax', value='6', format='int')
#    opObj11.addParameter(name='timerange', value=60, format='int')
#    
#    
    opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
    opObj11.addParameter(name='idfigure', value='14', format='int')
    opObj11.addParameter(name='wintitle', value='NarrowPulse', format='str')
    opObj11.addParameter(name='zmin', value='0', format='int')
    opObj11.addParameter(name='zmax', value='50', format='int')
    opObj11.addParameter(name='figpath', value='/home/roj-idl71/Data/RAWDATA/Meteors/graphs')
    opObj11.addParameter(name='save', value='1', format='int')
    opObj11.addParameter(name='xmin', value='4', format='int')
    opObj11.addParameter(name='xmax', value='6', format='int')    
#    opObj11.addParameter(name='timerange', value=2*60*60, format='int')
      
    print "Escribiendo el archivo XML"
    
    controllerObj.writeXml(filename)
    
    print "Leyendo el archivo XML"
    controllerObj.readXml(filename)
    #controllerObj.printattr()
    
    controllerObj.createObjects()
    controllerObj.connectObjects()
    controllerObj.run()
        
if __name__=='__main__':
    
    meteors()
    
    """
    from timeit import Timer
    
    t = Timer("meteors()", "from __main__ import meteors")
    
    print t.timeit()
    """