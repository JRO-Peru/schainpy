import os, sys

path = os.path.split(os.getcwd())[0]
path = os.path.split(path)[0]

sys.path.insert(0, path)

filename = "bltr_reader.xml"
path = os.path.join(os.environ['HOME'],'Documents/Data/')
pathfile = os.path.join(os.environ['HOME'],'Documents/BLTR') #'/home/signalchain/Documents/amisr'
desc = "BLTR Experiment"

from schainpy.controller import Project
controllerObj = Project()
controllerObj.setup(id = '196', name='test01', description='Reader/Writer experiment')

readUnitConfObj = controllerObj.addReadUnit(datatype='BLTRReader',
                                            path=path,
                                            startDate='2016/10/19',
                                            endDate='2016/10/19',
                                            startTime='00:00:00',
                                            endTime='23:59:59',
                                            walk=1)

procUnitBLTR = controllerObj.addProcUnit(datatype='BLTRProc', inputId=readUnitConfObj.getId())

opObj11 = procUnitBLTR.addOperation(name='PrintInfo', optype='other')


print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()
