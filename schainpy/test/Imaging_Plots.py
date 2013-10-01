import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

desc = "EWDrifts+Imaging+Faraday Experiments"
filename = "imaging_plots.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)

path = '/home/dsuarez/EW_Faraday_imaging'
path = '/media/datos/IMAGING/IMAGING/setiembre2013'

readUnitConfObj = controllerObj.addReadUnit(datatype='Spectra',
                                            path=path,
                                            startDate='2013/09/27',
                                            endDate='2013/09/27',
                                            startTime='19:00:00',
                                            endTime='23:59:59',
                                            delay=20,
                                            online=1,
                                            walk=1)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')

######################## IMAGING #############################################

procUnitConfObj1 = controllerObj.addProcUnit(datatype='Spectra', inputId=readUnitConfObj.getId())


# opObj11 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
# opObj11.addParameter(name='n', value='2', format='float')

opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
opObj11.addParameter(name='id', value='2000', format='int')
opObj11.addParameter(name='wintitle', value='Imaging', format='str')
opObj11.addParameter(name='zmin', value='35', format='int')
opObj11.addParameter(name='zmax', value='45', format='int')
# opObj11.addParameter(name='ymin', value='0', format='int')
# opObj11.addParameter(name='ymax', value='300', format='int')
opObj11.addParameter(name='save', value='1', format='int')
opObj11.addParameter(name='figpath', value='/media/datos/IMAGING/IMAGING/graphs/imaging_201309', format='str')
opObj11.addParameter(name='wr_period', value='5', format='int')
opObj11.addParameter(name='ftp', value='1', format='int')
opObj11.addParameter(name='server', value='jro-app.igp.gob.pe', format='str')
opObj11.addParameter(name='folder', value='/home/wmaster/graficos', format='str')
opObj11.addParameter(name='username', value='wmaster', format='str')
opObj11.addParameter(name='password', value='mst2010vhf', format='str')
opObj11.addParameter(name='ftp_wei', value='0', format='int')
opObj11.addParameter(name='exp_code', value='13', format='int')
opObj11.addParameter(name='sub_exp_code', value='0', format='int')
opObj11.addParameter(name='plot_pos', value='0', format='int')





# opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
# opObj11.addParameter(name='id', value='101', format='int')
# opObj11.addParameter(name='wintitle', value='Imaging', format='str')
# opObj11.addParameter(name='xmin', value='19', format='float')
# opObj11.addParameter(name='xmax', value='24', format='float')
# opObj11.addParameter(name='save', value='1', format='int')
# # opObj11.addParameter(name='figfile', value='rti-imaging.png', format='str')
# opObj11.addParameter(name='figpath', value='/home/dsuarez/Pictures/imaging_last_night', format='str')
# opObj11.addParameter(name='ftp', value='1', format='int')
# opObj11.addParameter(name='ftpratio', value='3', format='int')
# 
# 
# 
opObj11 = procUnitConfObj1.addOperation(name='CoherenceMap', optype='other')
opObj11.addParameter(name='id', value='2001', format='int')
opObj11.addParameter(name='wintitle', value='Imaging', format='str')
opObj11.addParameter(name='xmin', value='17', format='float')
opObj11.addParameter(name='xmax', value='24', format='float')
opObj11.addParameter(name='save', value='1', format='int')
opObj11.addParameter(name='figpath', value='/media/datos/IMAGING/IMAGING/graphs/imaging_201309', format='str')
opObj11.addParameter(name='wr_period', value='5', format='int')
opObj11.addParameter(name='ftp', value='1', format='int')
opObj11.addParameter(name='server', value='jro-app.igp.gob.pe', format='str')
opObj11.addParameter(name='folder', value='/home/wmaster/graficos', format='str')
opObj11.addParameter(name='username', value='wmaster', format='str')
opObj11.addParameter(name='password', value='mst2010vhf', format='str')
opObj11.addParameter(name='ftp_wei', value='0', format='int')
opObj11.addParameter(name='exp_code', value='13', format='int')
opObj11.addParameter(name='sub_exp_code', value='0', format='int')
opObj11.addParameter(name='plot_pos', value='0', format='int')





print "Escribiendo el archivo XML"
controllerObj.writeXml(filename)
print "Leyendo el archivo XML"
controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()
  
  
