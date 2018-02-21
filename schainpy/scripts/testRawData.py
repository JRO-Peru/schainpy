import os, sys

from schainpy.controller import Project

if __name__ == '__main__':
    
    desc = "Segundo Test"
    filename = "schain.xml"
    
    pathW='/media/erick/6F60F7113095A154/CLAIRE/CLAIRE_WINDS_2MHZ/DATA/pdatatest/test1024'
    figpath = '/media/erick/6F60F7113095A154/CLAIRE/CLAIRE_WINDS_2MHZ/Images/test1024'
    
    controllerObj = Project()
    
    controllerObj.setup(id='191', name='test01', description=desc)
    
    readUnitConfObj = controllerObj.addReadUnit(datatype='VoltageReader',
                                                path='/media/erick/6F60F7113095A154/CLAIRE/CLAIRE_WINDS_2MHZ/DATA/',
                                                #path='/home/erick/Documents/Data/Claire_Data/raw',
                                                startDate='2017/08/22',
                                                endDate='2017/08/22',
                                                startTime='01:00:00',
                                                endTime='06:00:00',
                                                online=0,
                                                walk=1)
    
    opObj00 = readUnitConfObj.addOperation(name='printInfo') 
#     
#     procUnitConfObj0 = controllerObj.addProcUnit(datatype='VoltageProc',
#                                                  inputId=readUnitConfObj.getId())
#     
#     opObj10 = procUnitConfObj0.addOperation(name='selectHeights')
#     opObj10.addParameter(name='minHei', value='0', format='float')
#     opObj10.addParameter(name='maxHei', value='8', format='float')
# 
#     opObj10 = procUnitConfObj0.addOperation(name='filterByHeights')
#     opObj10.addParameter(name='window', value='2', format='float')
#     
#     opObj10 = procUnitConfObj0.addOperation(name='Decoder', optype='external')
#     opObj10.addParameter(name='code', value='1,-1', format='intlist')
#     opObj10.addParameter(name='nCode', value='2', format='float')
#     opObj10.addParameter(name='nBaud', value='1', format='float')
#  
# 
#     opObj10 = procUnitConfObj0.addOperation(name='CohInt', optype='external')
#     opObj10.addParameter(name='n', value='1296', format='float')

    opObj00 = readUnitConfObj.addOperation(name='printNumberOfBlock')
    
    procUnitConfObj0 = controllerObj.addProcUnit(datatype='VoltageProc',
                                                 inputId=readUnitConfObj.getId())
    

    opObj10 = procUnitConfObj0.addOperation(name='setRadarFrequency')
    opObj10.addParameter(name='frequency', value='445.09e6', format='float')
    
    #opObj10 = procUnitConfObj0.addOperation(name='CohInt', optype='external')
    #opObj10.addParameter(name='n', value='1', format='float')
    
    #opObj10 = procUnitConfObj0.addOperation(name='selectHeights')
    #opObj10.addParameter(name='minHei', value='1', format='float')
    #opObj10.addParameter(name='maxHei', value='15', format='float')
    
    #opObj10 = procUnitConfObj0.addOperation(name='selectFFTs')
    #opObj10.addParameter(name='minHei', value='', format='float')
    #opObj10.addParameter(name='maxHei', value='', format='float')
    
    procUnitConfObj1 = controllerObj.addProcUnit(datatype='SpectraProc',
                                                 inputId=procUnitConfObj0.getId())
    
    # Creating a processing object with its parameters
    # schainpy.model.proc.jroproc_spectra.SpectraProc.run()    
    # If you need to add more parameters can use the "addParameter method"
    procUnitConfObj1.addParameter(name='nFFTPoints', value='1024', format='int')
    
    
    opObj10 = procUnitConfObj1.addOperation(name='removeDC')
    #opObj10 = procUnitConfObj1.addOperation(name='removeInterference')
    #opObj10 = procUnitConfObj1.addOperation(name='IncohInt', optype='external')
    #opObj10.addParameter(name='n', value='30', format='float')
    
    
    
    #opObj10 = procUnitConfObj1.addOperation(name='selectFFTs')
    #opObj10.addParameter(name='minFFT', value='-15', format='float')
    #opObj10.addParameter(name='maxFFT', value='15', format='float')
    
    
    
    opObj10 = procUnitConfObj1.addOperation(name='SpectraWriter', optype='other')
    opObj10.addParameter(name='blocksPerFile', value='64', format = 'int')
    opObj10.addParameter(name='path', value=pathW)
    # Using internal methods
    # schainpy.model.proc.jroproc_spectra.SpectraProc.selectChannels()
#     opObj10 = procUnitConfObj1.addOperation(name='selectChannels')
#     opObj10.addParameter(name='channelList', value='0,1', format='intlist')
    
    # Using internal methods
    # schainpy.model.proc.jroproc_spectra.SpectraProc.selectHeights()
#     opObj10 = procUnitConfObj1.addOperation(name='selectHeights')
#     opObj10.addParameter(name='minHei', value='90', format='float')
#     opObj10.addParameter(name='maxHei', value='180', format='float')
    
    # Using external methods (new modules)
#     #schainpy.model.proc.jroproc_spectra.IncohInt.setup()
#     opObj12 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
#     opObj12.addParameter(name='n', value='1', format='int')
    
    # Using external methods (new modules)
    # schainpy.model.graphics.jroplot_spectra.SpectraPlot.setup()
    opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='external')
    opObj11.addParameter(name='id', value='11', format='int')
    opObj11.addParameter(name='wintitle', value='SpectraPlot', format='str')
    opObj11.addParameter(name='xaxis', value='velocity', format='str')
    # opObj11.addParameter(name='xmin', value='-10', format='int')
    # opObj11.addParameter(name='xmax', value='10', format='int')
    
#     opObj11.addParameter(name='ymin', value='1', format='float')
#     opObj11.addParameter(name='ymax', value='3', format='int')
    #opObj11.addParameter(name='zmin', value='10', format='int')
    #opObj11.addParameter(name='zmax', value='35', format='int')
#     opObj11.addParameter(name='save', value='2', format='int')
#     opObj11.addParameter(name='save', value='5', format='int')
    # opObj11.addParameter(name='figpath', value=figpath, format='str')
    
    
    opObj11 = procUnitConfObj1.addOperation(name='CrossSpectraPlot', optype='other')
    procUnitConfObj1.addParameter(name='pairsList', value='(0,1),(0,2),(1,2)', format='pairsList')
    opObj11.addParameter(name='id', value='2005', format='int')
    #opObj11.addParameter(name='wintitle', value='CrossSpectraPlot_ShortPulse', format='str')
    #opObj11.addParameter(name='exp_code', value='13', format='int')
    opObj11.addParameter(name='xaxis', value='Velocity', format='str')
    #opObj11.addParameter(name='xmin', value='-6', format='float')
    #opObj11.addParameter(name='xmax', value='6', format='float')
    opObj11.addParameter(name='zmin', value='15', format='float')
    opObj11.addParameter(name='zmax', value='50', format='float')
    opObj11.addParameter(name='ymin', value='0', format='float')
    opObj11.addParameter(name='ymax', value='7', format='float')
    #opObj11.addParameter(name='phase_min', value='-4', format='int')
    #opObj11.addParameter(name='phase_max', value='4', format='int')
#    
    
    # Using external methods (new modules)
    # schainpy.model.graphics.jroplot_spectra.RTIPlot.setup()
    opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
    opObj11.addParameter(name='id', value='30', format='int')
    opObj11.addParameter(name='wintitle', value='RTI', format='str')
    opObj11.addParameter(name='zmin', value='15', format='int')
    opObj11.addParameter(name='zmax', value='40', format='int')
    opObj11.addParameter(name='ymin', value='1', format='int')
    opObj11.addParameter(name='ymax', value='7', format='int')
    opObj11.addParameter(name='showprofile', value='1', format='int')
#     opObj11.addParameter(name='timerange', value=str(5*60*60*60), format='int')
    opObj11.addParameter(name='xmin', value='1', format='float')
    opObj11.addParameter(name='xmax', value='6', format='float')    
    opObj11.addParameter(name='save', value='1', format='int')
    
 
#     '''#########################################################################################'''
#  
#     
#     procUnitConfObj2 = controllerObj.addProcUnit(datatype='Parameters', inputId=procUnitConfObj1.getId())
#     opObj11 = procUnitConfObj2.addOperation(name='SpectralMoments', optype='other')
#     
#     '''
#     # Discriminacion de ecos
#     opObj11 = procUnitConfObj2.addOperation(name='GaussianFit', optype='other')
#     opObj11.addParameter(name='SNRlimit', value='0', format='int')
#     '''
#     
#     '''
#     # Estimacion de Precipitacion
#     opObj11 = procUnitConfObj2.addOperation(name='PrecipitationProc', optype='other')
#     '''
#     
#     opObj22 = procUnitConfObj2.addOperation(name='FullSpectralAnalysis', optype='other')
#     
#     opObj22.addParameter(name='SNRlimit', value='-10', format='float')
#     opObj22.addParameter(name='E01', value='1.500', format='float')
#     opObj22.addParameter(name='E02', value='1.500', format='float')
#     opObj22.addParameter(name='E12', value='0', format='float')
#     opObj22.addParameter(name='N01', value='0.875', format='float')
#     opObj22.addParameter(name='N02', value='-0.875', format='float')
#     opObj22.addParameter(name='N12', value='-1.750', format='float')
#     
#     
#     opObj22 = procUnitConfObj2.addOperation(name='WindProfilerPlot', optype='other')
#     opObj22.addParameter(name='id', value='4', format='int')
#     opObj22.addParameter(name='wintitle', value='Wind Profiler', format='str')
#     opObj22.addParameter(name='save', value='1', format='bool')
#     opObj22.addParameter(name='xmin', value='0', format='float')
#     opObj22.addParameter(name='xmax', value='6', format='float')
#     opObj22.addParameter(name='ymin', value='1', format='float')
#     opObj22.addParameter(name='ymax', value='3.5', format='float')
#     opObj22.addParameter(name='zmin', value='-1', format='float')
#     opObj22.addParameter(name='zmax', value='1', format='float')
#     opObj22.addParameter(name='SNRmin', value='-15', format='float')
#     opObj22.addParameter(name='SNRmax', value='20', format='float')
#     opObj22.addParameter(name='zmin_ver', value='-200', format='float')
#     opObj22.addParameter(name='zmax_ver', value='200', format='float')
#     opObj22.addParameter(name='save', value='1', format='int')
#     opObj22.addParameter(name='figpath', value=figpath, format='str')
# 
# 
# 
#     #opObj11.addParameter(name='zmin', value='75', format='int')
#     
#     #opObj12 = procUnitConfObj2.addOperation(name='ParametersPlot', optype='other')
#     #opObj12.addParameter(name='id',value='4',format='int')
#     #opObj12.addParameter(name='wintitle',value='First_gg',format='str')
#     ''' 
#     #Ploteo de Discriminacion de Gaussianas
#     
#     opObj11 = procUnitConfObj2.addOperation(name='FitGauPlot', optype='other')
#     opObj11.addParameter(name='id', value='21', format='int')
#     opObj11.addParameter(name='wintitle', value='Rainfall Gaussian', format='str')
#     opObj11.addParameter(name='xaxis', value='velocity', format='str')
#     opObj11.addParameter(name='showprofile', value='1', format='int')  
#     opObj11.addParameter(name='zmin', value='75', format='int')
#     opObj11.addParameter(name='zmax', value='100', format='int')
#     opObj11.addParameter(name='GauSelector', value='1', format='int')
#     #opObj11.addParameter(name='save', value='1', format='int')
#     #opObj11.addParameter(name='figpath', value='/home/erick/Documents/Data/d2015106')
#     
#     opObj11 = procUnitConfObj2.addOperation(name='FitGauPlot', optype='other')
#     opObj11.addParameter(name='id', value='22', format='int')
#     opObj11.addParameter(name='wintitle', value='Wind Gaussian', format='str')
#     opObj11.addParameter(name='xaxis', value='velocity', format='str')
#     opObj11.addParameter(name='showprofile', value='1', format='int')  
#     opObj11.addParameter(name='zmin', value='75', format='int')
#     opObj11.addParameter(name='zmax', value='100', format='int')
#     opObj11.addParameter(name='GauSelector', value='0', format='int')
#     '''
#     
#     
    
      
    controllerObj.start()
