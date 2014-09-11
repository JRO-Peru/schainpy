import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "AMISR Experiment Test"
filename = "amisr.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)

path = '/home/administrator/Documents/amisr_bug'
path = '/media/administrator/New Volume/amisr'
#path = '/media/administrator/Toshiba/data'
figpath = '/home/administrator/Pictures/amisr'

figfile0 = 'amisr_rti_beam0.png'
figfile1 = 'amisr_rti_beam1.png'
figfile2 = 'amisr_rti_beam2.png'
figfile3 = 'amisr_rti_beam3.png'
figfile4 = 'amisr_rti_beam4.png'
figfile5 = 'amisr_rti_beam5.png'
figfile6 = 'amisr_rti_beam6.png'

title0 = 'RTI AMISR Beam 0'
title1 = 'RTI AMISR Beam 1'
title2 = 'RTI AMISR Beam 2'
title3 = 'RTI AMISR Beam 3'
title4 = 'RTI AMISR Beam 4'
title5 = 'RTI AMISR Beam 5'
title6 = 'RTI AMISR Beam 6'

profileStrSelBeam0 = '0,101'
profileStrSelBeam1 = '614,741'
profileStrSelBeam2 = '358,485'
profileStrSelBeam3 = '742,869'
profileStrSelBeam4 = '230,357'
profileStrSelBeam5 = '486,613'
profileStrSelBeam6 = '102,229'

nProfiles = '32'
nFFTPoints = '32'


readUnitConfObj = controllerObj.addReadUnit(datatype='AMISR',
                                            path=path,
                                            startDate='2014/08/18',
                                            endDate='2014/08/18',
                                            startTime='00:00:00',
                                            endTime='23:59:59',
                                            walk=1)



# procUnitConfObjBeam0 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())
# opObj11 = procUnitConfObjBeam0.addOperation(name='ProfileSelector', optype='other')
# opObj11.addParameter(name='profileRangeList', value=profileStrSelBeam0, format='intlist')

# procUnitConfObjBeam1 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())
# procUnitConfObjBeam2 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())
# procUnitConfObjBeam3 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())
# procUnitConfObjBeam4 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())
# procUnitConfObjBeam5 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())
# procUnitConfObjBeam6 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())

# procUnitAMISR = controllerObj.addProcUnit(datatype='AMISR', inputId=readUnitConfObj.getId())
# opObj11 = procUnitAMISR.addOperation(name='BeamSelector', optype='other')
# opObj11.addParameter(name='beam', value='1', format='int')
# 
# procUnitConfObjBeam1 = controllerObj.addProcUnit(datatype='Voltage', inputId=procUnitAMISRBeam0.getId())
# 
# opObj11 = procUnitConfObjBeam1.addOperation(name='CohInt', optype='other')
# opObj11.addParameter(name='n', value='128', format='int')
# 
# 
# procUnitConfObjSpectraBeam1 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObjBeam1.getId())
# procUnitConfObjSpectraBeam1.addParameter(name='nFFTPoints', value='32', format='int')
# procUnitConfObjSpectraBeam1.addParameter(name='nProfiles', value='32', format='int')
#     
# opObj11 = procUnitConfObjSpectraBeam1.addOperation(name='getNoise')
# opObj11.addParameter(name='minHei', value='100', format='float')
# opObj11.addParameter(name='maxHei', value='450', format='float')
#     
# opObj11 = procUnitConfObjSpectraBeam1.addOperation(name='SpectraPlot', optype='other')
# opObj11.addParameter(name='id', value='100', format='int')
# opObj11.addParameter(name='wintitle', value='SpectraPlot', format='str')







# ############################# Beam0 #############################
procUnitAMISRBeam0 = controllerObj.addProcUnit(datatype='AMISR', inputId=readUnitConfObj.getId())

#opObj11 = procUnitAMISRBeam0.addOperation(name='PrintInfo', optype='other')


opObj11 = procUnitAMISRBeam0.addOperation(name='BeamSelector', optype='other')
opObj11.addParameter(name='beam', value='0', format='int')

procUnitConfObjBeam0 = controllerObj.addProcUnit(datatype='Voltage', inputId=procUnitAMISRBeam0.getId())

opObj11 = procUnitConfObjBeam0.addOperation(name='CohInt', optype='other')
opObj11.addParameter(name='n', value='128', format='int')

procUnitConfObjSpectraBeam0 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObjBeam0.getId())
procUnitConfObjSpectraBeam0.addParameter(name='nFFTPoints', value=nFFTPoints, format='int')
procUnitConfObjSpectraBeam0.addParameter(name='nProfiles', value=nProfiles, format='int')
    
opObj11 = procUnitConfObjSpectraBeam0.addOperation(name='getNoise')
opObj11.addParameter(name='minHei', value='100', format='float')
opObj11.addParameter(name='maxHei', value='450', format='float')
    
opObj11 = procUnitConfObjSpectraBeam0.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='id', value='100', format='int')
opObj11.addParameter(name='wintitle', value='AMISR Beam 0', format='str')




# procUnitConfObjBeam0 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())
# opObj11 = procUnitConfObjBeam0.addOperation(name='ProfileSelector', optype='other')
# opObj11.addParameter(name='profileRangeList', value=profileStrSelBeam0, format='intlist')
#     
# opObj11 = procUnitConfObjBeam0.addOperation(name='CohInt', optype='other')
# opObj11.addParameter(name='n', value='102', format='int')
#    
# procUnitConfObjSpectraBeam0 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObjBeam0.getId())
# procUnitConfObjSpectraBeam0.addParameter(name='nFFTPoints', value='32', format='int')
# procUnitConfObjSpectraBeam0.addParameter(name='nProfiles', value='32', format='int')
#    
# opObj11 = procUnitConfObjSpectraBeam0.addOperation(name='getNoise')
# opObj11.addParameter(name='minHei', value='100', format='float')
# opObj11.addParameter(name='maxHei', value='450', format='float')
#    
# opObj11 = procUnitConfObjSpectraBeam0.addOperation(name='RTIPlot', optype='other')
# opObj11.addParameter(name='id', value='100', format='int')
# opObj11.addParameter(name='wintitle', value=title0, format='str')
# opObj11.addParameter(name='xmin', value='0', format='int')
# opObj11.addParameter(name='xmax', value='18', format='int')
# opObj11.addParameter(name='zmin', value='45', format='int')
# opObj11.addParameter(name='zmax', value='70', format='int')
# #opObj11.addParameter(name='timerange', value='7200', format='int')
# opObj11.addParameter(name='showprofile', value='0', format='int')
# opObj11.addParameter(name='figpath', value=figpath, format='str')
# opObj11.addParameter(name='figfile', value=figfile0, format='str')
# 
# 
# 
# 
# 
# # 

# #############################  Beam1 #############################
procUnitAMISRBeam1 = controllerObj.addProcUnit(datatype='AMISR', inputId=readUnitConfObj.getId())

#opObj11 = procUnitAMISRBeam1.addOperation(name='PrintInfo', optype='other')


opObj11 = procUnitAMISRBeam1.addOperation(name='BeamSelector', optype='other')
opObj11.addParameter(name='beam', value='1', format='int')

procUnitConfObjBeam1 = controllerObj.addProcUnit(datatype='Voltage', inputId=procUnitAMISRBeam1.getId())

opObj11 = procUnitConfObjBeam1.addOperation(name='CohInt', optype='other')
opObj11.addParameter(name='n', value='128', format='int')

procUnitConfObjSpectraBeam1 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObjBeam1.getId())
procUnitConfObjSpectraBeam1.addParameter(name='nFFTPoints', value=nFFTPoints, format='int')
procUnitConfObjSpectraBeam1.addParameter(name='nProfiles', value=nProfiles, format='int')
    
opObj11 = procUnitConfObjSpectraBeam1.addOperation(name='getNoise')
opObj11.addParameter(name='minHei', value='100', format='float')
opObj11.addParameter(name='maxHei', value='450', format='float')
    
opObj11 = procUnitConfObjSpectraBeam1.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='id', value='101', format='int')
opObj11.addParameter(name='wintitle', value='AMISR Beam 1', format='str')

#   
# opObj11 = procUnitConfObjSpectraBeam1.addOperation(name='RTIPlot', optype='other')
# opObj11.addParameter(name='id', value='201', format='int')
# opObj11.addParameter(name='wintitle', value=title1, format='str')
# #opObj11.addParameter(name='timerange', value='36000', format='int')
# opObj11.addParameter(name='xmin', value='0', format='int')
# opObj11.addParameter(name='xmax', value='18', format='int')
# opObj11.addParameter(name='zmin', value='45', format='int')
# opObj11.addParameter(name='zmax', value='70', format='int')
# opObj11.addParameter(name='showprofile', value='0', format='int')
# opObj11.addParameter(name='figpath', value=figpath, format='str')
# opObj11.addParameter(name='figfile', value=figfile1, format='str')
# #  
# #  
# #  
# #  
# #  
# ############################## Beam2 #############################
procUnitAMISRBeam2 = controllerObj.addProcUnit(datatype='AMISR', inputId=readUnitConfObj.getId())
opObj11 = procUnitAMISRBeam2.addOperation(name='BeamSelector', optype='other')
opObj11.addParameter(name='beam', value='2', format='int')

procUnitConfObjBeam2 = controllerObj.addProcUnit(datatype='Voltage', inputId=procUnitAMISRBeam2.getId())

opObj11 = procUnitConfObjBeam2.addOperation(name='CohInt', optype='other')
opObj11.addParameter(name='n', value='128', format='int')


procUnitConfObjSpectraBeam2 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObjBeam2.getId())
procUnitConfObjSpectraBeam2.addParameter(name='nFFTPoints', value=nFFTPoints, format='int')
procUnitConfObjSpectraBeam2.addParameter(name='nProfiles', value=nProfiles, format='int')
    
opObj11 = procUnitConfObjSpectraBeam2.addOperation(name='getNoise')
opObj11.addParameter(name='minHei', value='100', format='float')
opObj11.addParameter(name='maxHei', value='450', format='float')
    
opObj11 = procUnitConfObjSpectraBeam2.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='id', value='102', format='int')
opObj11.addParameter(name='wintitle', value='AMISR Beam 2', format='str')

#     
# opObj11 = procUnitConfObjSpectraBeam2.addOperation(name='RTIPlot', optype='other')
# opObj11.addParameter(name='id', value='202', format='int')
# opObj11.addParameter(name='wintitle', value=title2, format='str')
# #opObj11.addParameter(name='timerange', value='18000', format='int')
# opObj11.addParameter(name='xmin', value='0', format='int')
# opObj11.addParameter(name='xmax', value='18', format='int')
# opObj11.addParameter(name='zmin', value='45', format='int')
# opObj11.addParameter(name='zmax', value='70', format='int')
# opObj11.addParameter(name='showprofile', value='0', format='int')
# opObj11.addParameter(name='figpath', value=figpath, format='str')
# opObj11.addParameter(name='figfile', value=figfile2, format='str')
#   
#   
#   
#   
#   
#    
# ############################## Beam3 #############################
procUnitAMISRBeam3 = controllerObj.addProcUnit(datatype='AMISR', inputId=readUnitConfObj.getId())
opObj11 = procUnitAMISRBeam3.addOperation(name='BeamSelector', optype='other')
opObj11.addParameter(name='beam', value='3', format='int')

procUnitConfObjBeam3 = controllerObj.addProcUnit(datatype='Voltage', inputId=procUnitAMISRBeam3.getId())

opObj11 = procUnitConfObjBeam3.addOperation(name='CohInt', optype='other')
opObj11.addParameter(name='n', value='128', format='int')


procUnitConfObjSpectraBeam3 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObjBeam3.getId())
procUnitConfObjSpectraBeam3.addParameter(name='nFFTPoints', value=nFFTPoints, format='int')
procUnitConfObjSpectraBeam3.addParameter(name='nProfiles', value=nProfiles, format='int')
    
opObj11 = procUnitConfObjSpectraBeam3.addOperation(name='getNoise')
opObj11.addParameter(name='minHei', value='100', format='float')
opObj11.addParameter(name='maxHei', value='450', format='float')
    
opObj11 = procUnitConfObjSpectraBeam3.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='id', value='103', format='int')
opObj11.addParameter(name='wintitle', value='AMISR Beam 3', format='str')

#     
# opObj11 = procUnitConfObjSpectraBeam3.addOperation(name='RTIPlot', optype='other')
# opObj11.addParameter(name='id', value='203', format='int')
# opObj11.addParameter(name='wintitle', value=title3, format='str')
# #opObj11.addParameter(name='timerange', value='18000', format='int')
# opObj11.addParameter(name='xmin', value='0', format='int')
# opObj11.addParameter(name='xmax', value='18', format='int')
# opObj11.addParameter(name='zmin', value='45', format='int')
# opObj11.addParameter(name='zmax', value='70', format='int')
# opObj11.addParameter(name='showprofile', value='0', format='int')
# opObj11.addParameter(name='figpath', value=figpath, format='str')
# opObj11.addParameter(name='figfile', value=figfile3, format='str')
# # #  
# # #  
# # #  
# # #  
# # #  
# # #    
# ############################## Beam4 #############################
procUnitAMISRBeam4 = controllerObj.addProcUnit(datatype='AMISR', inputId=readUnitConfObj.getId())
opObj11 = procUnitAMISRBeam4.addOperation(name='BeamSelector', optype='other')
opObj11.addParameter(name='beam', value='4', format='int')

procUnitConfObjBeam4 = controllerObj.addProcUnit(datatype='Voltage', inputId=procUnitAMISRBeam4.getId())

opObj11 = procUnitConfObjBeam4.addOperation(name='CohInt', optype='other')
opObj11.addParameter(name='n', value='128', format='int')


procUnitConfObjSpectraBeam4 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObjBeam4.getId())
procUnitConfObjSpectraBeam4.addParameter(name='nFFTPoints', value=nFFTPoints, format='int')
procUnitConfObjSpectraBeam4.addParameter(name='nProfiles', value=nProfiles, format='int')
    
opObj11 = procUnitConfObjSpectraBeam4.addOperation(name='getNoise')
opObj11.addParameter(name='minHei', value='100', format='float')
opObj11.addParameter(name='maxHei', value='450', format='float')
    
opObj11 = procUnitConfObjSpectraBeam4.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='id', value='104', format='int')
opObj11.addParameter(name='wintitle', value='AMISR Beam 4', format='str')

# opObj11 = procUnitConfObjSpectraBeam4.addOperation(name='RTIPlot', optype='other')
# opObj11.addParameter(name='id', value='204', format='int')
# opObj11.addParameter(name='wintitle', value=title4, format='str')
# #opObj11.addParameter(name='timerange', value='18000', format='int')
# opObj11.addParameter(name='xmin', value='0', format='int')
# opObj11.addParameter(name='xmax', value='18', format='int')
# opObj11.addParameter(name='zmin', value='45', format='int')
# opObj11.addParameter(name='zmax', value='70', format='int')
# opObj11.addParameter(name='showprofile', value='0', format='int')
# opObj11.addParameter(name='figpath', value=figpath, format='str')
# opObj11.addParameter(name='figfile', value=figfile4, format='str')
# # # #  
# # # #  
# # # #  
# # # #  
# # # #   
# ############################## Beam5 #############################
procUnitAMISRBeam5 = controllerObj.addProcUnit(datatype='AMISR', inputId=readUnitConfObj.getId())
opObj11 = procUnitAMISRBeam5.addOperation(name='BeamSelector', optype='other')
opObj11.addParameter(name='beam', value='5', format='int')

procUnitConfObjBeam5 = controllerObj.addProcUnit(datatype='Voltage', inputId=procUnitAMISRBeam5.getId())

opObj11 = procUnitConfObjBeam5.addOperation(name='CohInt', optype='other')
opObj11.addParameter(name='n', value='128', format='int')

procUnitConfObjSpectraBeam5 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObjBeam5.getId())
procUnitConfObjSpectraBeam5.addParameter(name='nFFTPoints', value=nFFTPoints, format='int')
procUnitConfObjSpectraBeam5.addParameter(name='nProfiles', value=nProfiles, format='int')
    
opObj11 = procUnitConfObjSpectraBeam5.addOperation(name='getNoise')
opObj11.addParameter(name='minHei', value='100', format='float')
opObj11.addParameter(name='maxHei', value='450', format='float')
    
opObj11 = procUnitConfObjSpectraBeam5.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='id', value='105', format='int')
opObj11.addParameter(name='wintitle', value='AMISR Beam 5', format='str')

# opObj11 = procUnitConfObjSpectraBeam5.addOperation(name='RTIPlot', optype='other')
# opObj11.addParameter(name='id', value='205', format='int')
# opObj11.addParameter(name='wintitle', value=title5, format='str')
# #opObj11.addParameter(name='timerange', value='18000', format='int')
# opObj11.addParameter(name='xmin', value='0', format='int')
# opObj11.addParameter(name='xmax', value='18', format='int')
# opObj11.addParameter(name='zmin', value='45', format='int')
# opObj11.addParameter(name='zmax', value='70', format='int')
# opObj11.addParameter(name='showprofile', value='0', format='int')
# opObj11.addParameter(name='figpath', value=figpath, format='str')
# opObj11.addParameter(name='figfile', value=figfile5, format='str')
# # #  
# # # #  
# # # #  
# # # #  
# # # #   
# ############################## Beam6 #############################
procUnitAMISRBeam6 = controllerObj.addProcUnit(datatype='AMISR', inputId=readUnitConfObj.getId())
opObj11 = procUnitAMISRBeam6.addOperation(name='BeamSelector', optype='other')
opObj11.addParameter(name='beam', value='6', format='int')

procUnitConfObjBeam6 = controllerObj.addProcUnit(datatype='Voltage', inputId=procUnitAMISRBeam6.getId())

opObj11 = procUnitConfObjBeam6.addOperation(name='CohInt', optype='other')
opObj11.addParameter(name='n', value='128', format='int')


procUnitConfObjSpectraBeam6 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObjBeam6.getId())
procUnitConfObjSpectraBeam6.addParameter(name='nFFTPoints', value=nFFTPoints, format='int')
procUnitConfObjSpectraBeam6.addParameter(name='nProfiles', value=nProfiles, format='int')
    
opObj11 = procUnitConfObjSpectraBeam6.addOperation(name='getNoise')
opObj11.addParameter(name='minHei', value='100', format='float')
opObj11.addParameter(name='maxHei', value='450', format='float')
    
opObj11 = procUnitConfObjSpectraBeam6.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='id', value='106', format='int')
opObj11.addParameter(name='wintitle', value='AMISR Beam 6', format='str')
#     
# opObj11 = procUnitConfObjSpectraBeam6.addOperation(name='RTIPlot', optype='other')
# opObj11.addParameter(name='id', value='206', format='int')
# opObj11.addParameter(name='wintitle', value=title6, format='str')
# #opObj11.addParameter(name='timerange', value='18000', format='int')
# opObj11.addParameter(name='xmin', value='0', format='int')
# opObj11.addParameter(name='xmax', value='18', format='int')
# opObj11.addParameter(name='zmin', value='45', format='int')
# opObj11.addParameter(name='zmax', value='70', format='int')
# opObj11.addParameter(name='showprofile', value='0', format='int')
# opObj11.addParameter(name='figpath', value=figpath, format='str')
# opObj11.addParameter(name='figfile', value=figfile6, format='str')


print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()
