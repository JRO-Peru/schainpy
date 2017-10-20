import os, sys

from schainpy.controller import Project

if __name__ == '__main__':
    
    desc = "Segundo Test"
    filename = "schain.xml"
    
    controllerObj = Project()
    
    controllerObj.setup(id = '191', name='test01', description=desc)
    
    readUnitConfObj = controllerObj.addReadUnit(datatype='VoltageReader',
                                                path='/home/nanosat/data/John',
                                                startDate='2010/10/28',
                                                endDate='2017/10/28',
                                                startTime='00:00:00',
                                                endTime='23:59:59',
                                                online=0,
                                                walk=0)
    
    opObj00 = readUnitConfObj.addOperation(name='printNumberOfBlock')
    
    procUnitConfObj0 = controllerObj.addProcUnit(datatype='VoltageProc',
                                                 inputId=readUnitConfObj.getId())

    # opObj11 = procUnitConfObj0.addOperation(name='Scope', optype='external')
    # opObj11.addParameter(name='id', value='121', format='int')
    # opObj11.addParameter(name='wintitle', value='Scope', format='str')

    opObj10 = procUnitConfObj0.addOperation(name='DigitalRFWriter', optype='other')
    opObj10.addParameter(name='path', value='/home/nanosat/data/digitalrf', format='str')
    # opObj10.addParameter(name='minHei', value='0', format='float')
    # opObj10.addParameter(name='maxHei', value='8', format='float')

    # opObj10 = procUnitConfObj0.addOperation(name='filterByHeights')
    # opObj10.addParameter(name='window', value='2', format='float')
    
    # opObj10 = procUnitConfObj0.addOperation(name='Decoder', optype='external')
    # opObj10.addParameter(name='code', value='1,-1', format='intlist')
    # opObj10.addParameter(name='nCode', value='2', format='float')
    # opObj10.addParameter(name='nBaud', value='1', format='float')
 

    # opObj10 = procUnitConfObj0.addOperation(name='CohInt', optype='external')
    # opObj10.addParameter(name='n', value='1296', format='float')

    # procUnitConfObj1 = controllerObj.addProcUnit(datatype='SpectraProc',
    #                                              inputId=procUnitConfObj0.getId())
    
    #Creating a processing object with its parameters
    #schainpy.model.proc.jroproc_spectra.SpectraProc.run()    
    #If you need to add more parameters can use the "addParameter method"
    # procUnitConfObj1.addParameter(name='nFFTPoints', value='128', format='int')

    # opObj10 = procUnitConfObj1.addOperation(name='IncohInt', optype='external')
    # opObj10.addParameter(name='n', value='2', format='float')
    
    #Using internal methods
    #schainpy.model.proc.jroproc_spectra.SpectraProc.selectChannels()
#     opObj10 = procUnitConfObj1.addOperation(name='selectChannels')
#     opObj10.addParameter(name='channelList', value='0,1', format='intlist')
    
    #Using internal methods
    #schainpy.model.proc.jroproc_spectra.SpectraProc.selectHeights()
#     opObj10 = procUnitConfObj1.addOperation(name='selectHeights')
#     opObj10.addParameter(name='minHei', value='90', format='float')
#     opObj10.addParameter(name='maxHei', value='180', format='float')
    
    #Using external methods (new modules)
#     #schainpy.model.proc.jroproc_spectra.IncohInt.setup()
#     opObj12 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
#     opObj12.addParameter(name='n', value='1', format='int')
    
    #Using external methods (new modules)
    #schainpy.model.graphics.jroplot_spectra.SpectraPlot.setup()
#     opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='external')
#     opObj11.addParameter(name='id', value='11', format='int')
#     opObj11.addParameter(name='wintitle', value='SpectraPlot', format='str')
#     opObj11.addParameter(name='zmin', value='-60', format='int')
#     opObj11.addParameter(name='zmax', value='10', format='int')
#     opObj11.addParameter(name='save', value='1', format='int')
    
#     #Using external methods (new modules)
#     #schainpy.model.graphics.jroplot_spectra.RTIPlot.setup()
#     opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
#     opObj11.addParameter(name='id', value='30', format='int')
#     opObj11.addParameter(name='wintitle', value='RTI', format='str')
#     opObj11.addParameter(name='zmin', value='-60', format='int')
#     opObj11.addParameter(name='zmax', value='-10', format='int')
#     opObj11.addParameter(name='showprofile', value='1', format='int')
# #     opObj11.addParameter(name='timerange', value=str(5*60*60*60), format='int')
#     opObj11.addParameter(name='xmin', value='14', format='float')
#     opObj11.addParameter(name='xmax', value='23.9', format='float')    
#     opObj11.addParameter(name='save', value='1', format='int')
      
    controllerObj.start()
