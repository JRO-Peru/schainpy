import os, sys
#import timeit
import datetime

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "HF_EXAMPLE"
filename = "hf_test.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)


#path='/media/APOLLO/HF_rawdata/d2015026/0/cspec'
#path='/media/APOLLO/HF_rawdata/cspec'
path="/media/APOLLO/HF_rawdata/d2015059/sp01_f0" #f0=2.72e6
#path="/media/APOLLO/HF_rawdata/d2015059/sp01_f1" #f0=3.64e6
#path='/media/APOLLO/HF_rawdata/test'
figpath='/home/alex/Pictures/hf2_16/last_data'
pathFigure='/home/alex/Pictures/hf2_16/last_data'
#path='/home/alex/Downloads/ICA_LAST_TEST'

readUnitConfObj = controllerObj.addReadUnit(datatype='HFReader',
                                            path=path,
                                            startDate='2014/05/13',
                                            endDate='2015/05/13',
                                            startTime='00:00:00',
                                            endTime='23:59:59',
                                            online=0,
                                            #set=8000,
                                            delay=10,
                                            walk=1,
                                            timezone=-5*3600)


procUnitConfObj0 = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())

#opObj12 = procUnitConfObj0.addOperation(name='selectChannels',optype='self')
#opObj12.addParameter(name='channelList', value='0', format='intList')

# 
opObj12 = procUnitConfObj0.addOperation(name='CohInt', optype='other')
opObj12.addParameter(name='n', value='4', format='int')
#     
# opObj11 = procUnitConfObj0.addOperation(name='Scope', optype='other')
# opObj11.addParameter(name='id', value='10', format='int')
# opObj11.addParameter(name='wintitle', value='Voltage', format='str')
# opObj11.addParameter(name='ymin', value='-1e-8', format='float')
# opObj11.addParameter(name='ymax', value='1e-8', format='float')
# # 
procUnitConfObj1 = controllerObj.addProcUnit(datatype='SpectraProc', inputId=procUnitConfObj0.getId())
procUnitConfObj1.addParameter(name='nFFTPoints', value='25', format='int')
procUnitConfObj1.addParameter(name='nProfiles', value='25', format='int')
procUnitConfObj1.addParameter(name='pairsList', value='(0,1)', format='pairsList')


opObj11 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
opObj11.addParameter(name='n', value='15', format='float')

# opObj11 = procUnitConfObj1.addOperation(name='SpectraWriter', optype='other')
# opObj11.addParameter(name='path', value='/home/alex/Downloads/pdata_hf')
# opObj11.addParameter(name='blocksPerFile', value='1', format='int')

#  
# opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
# opObj11.addParameter(name='id', value='2001', format='int')
# opObj11.addParameter(name='wintitle', value='HF_Jicamarca', format='str')
# opObj11.addParameter(name='zmin', value='-120', format='float')
# opObj11.addParameter(name='zmax', value='-70', format='float')
# opObj11.addParameter(name='save', value='1', format='int')
# opObj11.addParameter(name='figpath', value=figpath, format='str')


#opObj11 = procUnitConfObj1.addOperation(name='PowerProfile', optype='other')
#opObj11.addParameter(name='id', value='2004', format='int')
#opObj11.addParameter(name='wintitle', value='HF_Jicamarca', format='str')

#opObj11.addParameter(name='channelList', value='0,1,2,3', format='intlist') 
#opObj11.addParameter(name='save', value='1', format='bool')
#opObj11.addParameter(name='figpath', value=figpath, format='str')
##opObj11.addParameter(name='xmin', value='10', format='int')
##opObj11.addParameter(name='xmax', value='40', format='int')

# opObj11 = procUnitConfObj1.addOperation(name='CoherenceMap', optype='other')
# opObj11.addParameter(name='id', value='4005', format='int')
# opObj11.addParameter(name='wintitle', value='HF_Jicamarca', format='str')
# opObj11.addParameter(name='xmin', value='0', format='float')
# opObj11.addParameter(name='xmax', value='24', format='float')
# #opObj11.addParameter(name='channelList', value='0,1,2,3', format='intlist') 
# opObj11.addParameter(name='save', value='1', format='bool')
# opObj11.addParameter(name='figpath', value=figpath, format='str')

# opObj11 = procUnitConfObj1.addOperation(name='CrossSpectraPlot', optype='other')
# opObj11.addParameter(name='id', value='6005', format='int')
# opObj11.addParameter(name='wintitle', value='HF_Jicamarca', format='str')
# opObj11.addParameter(name='zmin', value='-110', format='float')
# opObj11.addParameter(name='zmax', value='-50', format='float')
# #opObj11.addParameter(name='xmin', value='0', format='float')
# #opObj11.addParameter(name='xmax', value='24', format='float')
# #opObj11.addParameter(name='channelList', value='0,1,2,3', format='intlist') 
# opObj11.addParameter(name='save', value='1', format='bool')
# opObj11.addParameter(name='figpath', value=figpath, format='str')

# 
# #   
opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
opObj11.addParameter(name='id', value='3002', format='int')
opObj11.addParameter(name='wintitle', value='HF_Jicamarca', format='str')
#opObj11.addParameter(name='channelList', value='0', format='intlist') 
opObj11.addParameter(name='xmin', value='0', format='float')
opObj11.addParameter(name='xmax', value='24', format='float')
#opObj11.addParameter(name='zmin', value='-110', format='float')
#opObj11.addParameter(name='zmax', value='-50', format='float')
opObj11.addParameter(name='save', value='1', format='int')
opObj11.addParameter(name='figpath', value=figpath, format='str')


#------------------------------------------------------------------

# procUnitConfObj2 = controllerObj.addProcUnit(datatype='ParametersProc', inputId=procUnitConfObj1.getId())
# opObj20 = procUnitConfObj2.addOperation(name='GetMoments')
 
# opObj21 = procUnitConfObj2.addOperation(name='MomentsPlot', optype='other')
# opObj21.addParameter(name='id', value='3', format='int')
# opObj21.addParameter(name='wintitle', value='Moments Plot', format='str')
# opObj21.addParameter(name='save', value='1', format='bool')
# opObj21.addParameter(name='figpath', value=pathFigure, format='str')
# #opObj21.addParameter(name='zmin', value='5', format='int')
# #opObj21.addParameter(name='zmax', value='90', format='int')
# 
# opObj21 = procUnitConfObj2.addOperation(name='ParametersPlot', optype='other')
# opObj21.addParameter(name='id', value='5', format='int')
# opObj21.addParameter(name='wintitle', value='Radial Velocity Plot', format='str')
# opObj21.addParameter(name='save', value='1', format='bool')
# opObj21.addParameter(name='figpath', value=pathFigure, format='str')
# opObj21.addParameter(name='SNRmin', value='-50', format='int')
# opObj21.addParameter(name='SNRmax', value='-10', format='int')
# opObj21.addParameter(name='SNRthresh', value='0', format='float')
# opObj21.addParameter(name='xmin', value=0, format='float')
# opObj21.addParameter(name='xmax', value=24, format='float')



print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()

#timeit.timeit('controllerObj.run()', number=2)

controllerObj.run()