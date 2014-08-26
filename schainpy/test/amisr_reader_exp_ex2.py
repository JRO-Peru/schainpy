import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "AMISR Experiment Test"
filename = "amisr.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)

path = '/home/administrator/Documents/amisr'

readUnitConfObj = controllerObj.addReadUnit(datatype='AMISR',
                                            path=path,
                                            startDate='2014/08/18',
                                            endDate='2014/08/18',
                                            startTime='00:00:00',
                                            endTime='23:59:59',
                                            walk=1)

procUnitConfObjBeam0 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())
procUnitConfObjBeam1 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())
procUnitConfObjBeam2 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())
procUnitConfObjBeam3 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())
procUnitConfObjBeam4 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())
procUnitConfObjBeam5 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())
procUnitConfObjBeam6 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())

# Beam0
opObj11 = procUnitConfObjBeam0.addOperation(name='ProfileSelector', optype='other')
opObj11.addParameter(name='profileRangeList', value='0,81', format='intlist')

opObj11 = procUnitConfObjBeam0.addOperation(name='PowerProfile', optype='other')
opObj11.addParameter(name='id', value='10', format='int')
opObj11.addParameter(name='wintitle', value='AMISR Beam0 - Power Profile', format='str')

# Beam1
opObj11 = procUnitConfObjBeam1.addOperation(name='ProfileSelector', optype='other')
opObj11.addParameter(name='profileRangeList', value='82,209', format='intlist')
opObj11 = procUnitConfObjBeam1.addOperation(name='PowerProfile', optype='other')
opObj11.addParameter(name='id', value='11', format='int')
opObj11.addParameter(name='wintitle', value='AMISR Beam1 - Power Profile', format='str')
 
# # Beam2
opObj11 = procUnitConfObjBeam2.addOperation(name='ProfileSelector', optype='other')
opObj11.addParameter(name='profileRangeList', value='210,337', format='intlist')
opObj11 = procUnitConfObjBeam2.addOperation(name='PowerProfile', optype='other')
opObj11.addParameter(name='id', value='12', format='int')
opObj11.addParameter(name='wintitle', value='AMISR Beam2 - Power Profile', format='str')
# 
# # Beam3
opObj11 = procUnitConfObjBeam3.addOperation(name='ProfileSelector', optype='other')
opObj11.addParameter(name='profileRangeList', value='338,465', format='intlist')
opObj11 = procUnitConfObjBeam3.addOperation(name='PowerProfile', optype='other')
opObj11.addParameter(name='id', value='13', format='int')
opObj11.addParameter(name='wintitle', value='AMISR Beam3 - Power Profile', format='str')
 
# # Beam4
opObj11 = procUnitConfObjBeam4.addOperation(name='ProfileSelector', optype='other')
opObj11.addParameter(name='profileRangeList', value='466,593', format='intlist')
opObj11 = procUnitConfObjBeam4.addOperation(name='PowerProfile', optype='other')
opObj11.addParameter(name='id', value='14', format='int')
opObj11.addParameter(name='wintitle', value='AMISR Beam4 - Power Profile', format='str')
# 
# # Beam5
# opObj11 = procUnitConfObjBeam5.addOperation(name='ProfileSelector', optype='other')
# opObj11.addParameter(name='profileRangeList', value='594,721', format='intlist')
# opObj11 = procUnitConfObjBeam5.addOperation(name='PowerProfile', optype='other')
# opObj11.addParameter(name='id', value='15', format='int')
# opObj11.addParameter(name='wintitle', value='AMISR Beam5 - Power Profile', format='str')
# 
# # Beam6
# opObj11 = procUnitConfObjBeam6.addOperation(name='ProfileSelector', optype='other')
# opObj11.addParameter(name='profileRangeList', value='722,849', format='intlist')
# opObj11 = procUnitConfObjBeam6.addOperation(name='PowerProfile', optype='other')
# opObj11.addParameter(name='id', value='16', format='int')
# opObj11.addParameter(name='wintitle', value='AMISR Beam6 - Power Profile', format='str')




print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()
