
import os, sys

path = os.path.split(os.getcwd())[0]
path = os.path.split(path)[0]

sys.path.insert(0, path)

from schainpy.controller import Project

controllerObj = Project()
controllerObj.setup(id = '001', name='script01', description="JASMET Online monitoring")

#--------------------------------------    Setup    -----------------------------------------
#Verificar estas variables

#Path para los archivos
path = '/mnt/jars/2016_08/DIA' 
path = '/media/joscanoa/DATA_JASMET/JASMET/2016_08/NOCHE' 
path = '/media/joscanoa/DATA_JASMET/JASMET/2016_08/DIA' 
#Path para los graficos
pathfig = os.path.join(os.environ['HOME'],'Pictures/JASMET30/201608/graphics')
#Fechas para busqueda de archivos
startDate = '2016/08/25'
endDate = '2016/08/26'
#Horas para busqueda de archivos
startTime = '10:00:00'
endTime = '23:59:59'
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
#------------------------------    Voltage Reading Unit    ----------------------------------

readUnitConfObj = controllerObj.addReadUnit(datatype='VoltageReader',
                                            path=path,
                                            startDate=startDate,
                                            endDate=endDate,
                                            startTime=startTime,
                                            endTime=endTime,
                                            online=0,
                                            delay=5,
                                            walk=1)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')

#--------------------------    Voltage Processing Unit    ------------------------------------

procUnitConfObj0 = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())

opObj00 = procUnitConfObj0.addOperation(name='selectChannels')
opObj00.addParameter(name='channelList', value='0, 1, 2, 3, 4', format='intlist')

opObj01 = procUnitConfObj0.addOperation(name='setRadarFrequency')
opObj01.addParameter(name='frequency', value='30.e6', format='float')

opObj00 = procUnitConfObj0.addOperation(name='interpolateHeights')
opObj00.addParameter(name='topLim', value='73', format='int')
opObj00.addParameter(name='botLim', value='71', format='int')
# opObj00.addParameter(name='topLim', value='82', format='int')
# opObj00.addParameter(name='botLim', value='79', format='int')
 
opObj11 = procUnitConfObj0.addOperation(name='Decoder', optype='other')
opObj11 = procUnitConfObj0.addOperation(name='CohInt', optype='other')
opObj11.addParameter(name='n', value='2', format='int')

#---------------------------    Spectra Processing Unit    ------------------------------------

procUnitConfObj2 = controllerObj.addProcUnit(datatype='SpectraProc', inputId=procUnitConfObj0.getId())
procUnitConfObj2.addParameter(name='nFFTPoints', value='128', format='int')
procUnitConfObj2.addParameter(name='nProfiles', value='128', format='int')
 
opObj21 = procUnitConfObj2.addOperation(name='IncohInt', optype='other')
opObj21.addParameter(name='n', value='40.0', format='float')
 
opObj23 = procUnitConfObj2.addOperation(name='SpectraPlot', optype='other')
opObj23.addParameter(name='id', value='1', format='int')
opObj23.addParameter(name='save', value='1', format='bool')
opObj23.addParameter(name='figpath', value=pathfig, format='str')
opObj23.addParameter(name='zmin', value='23', format='int')
opObj23.addParameter(name='zmax', value='40', format='int')
opObj23.addParameter(name='figpath', value=pathfig, format='str')
opObj23.addParameter(name='ftp', value='1', format='int')
opObj23.addParameter(name='xaxis', value='Velocity', format='str')
opObj23.addParameter(name='exp_code', value='15', format='int')
opObj23.addParameter(name='sub_exp_code', value='1', format='int')
 
opObj22 = procUnitConfObj2.addOperation(name='RTIPlot', optype='other')
opObj22.addParameter(name='id', value='2', format='int')
opObj22.addParameter(name='save', value='1', format='bool')
opObj22.addParameter(name='figpath', value = pathfig, format='str')
# opObj22.addParameter(name='timerange', value = str(7*60*60), format='int')
opObj22.addParameter(name='xmin', value='18', format='float')
opObj22.addParameter(name='xmax', value='25', format='float')
opObj22.addParameter(name='zmin', value='23', format='int')
opObj22.addParameter(name='zmax', value='40', format='int')
opObj22.addParameter(name='figpath', value=pathfig, format='str')
opObj22.addParameter(name='ftp', value='1', format='int')
opObj22.addParameter(name='exp_code', value='15', format='int')
opObj22.addParameter(name='sub_exp_code', value='1', format='int')

#------------------------------------    Send images to server    -------------------------------
# procUnitConfObj4 = controllerObj.addProcUnit(name='SendToServer')
# procUnitConfObj4.addParameter(name='server', value='jro-app.igp.gob.pe', format='str')
# procUnitConfObj4.addParameter(name='username', value='wmaster', format='str')
# procUnitConfObj4.addParameter(name='password', value='mst2010vhf', format='str')
# procUnitConfObj4.addParameter(name='localfolder', value=pathfig, format='str')
# procUnitConfObj4.addParameter(name='remotefolder', value="/home/wmaster/graficos", format='str')
# procUnitConfObj4.addParameter(name='ext', value='.png', format='str')
# procUnitConfObj4.addParameter(name='period', value=120, format='int')
# procUnitConfObj4.addParameter(name='protocol', value='ftp', format='str')

#--------------------------------------------------------------------------------------------------
print "Escribiendo el archivo XML"
controllerObj.writeXml("JASMET01.xml")
print "Leyendo el archivo XML"
controllerObj.readXml("JASMET01.xml")

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()