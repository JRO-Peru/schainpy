basic = '''from schainpy.controller import Project

desc = "{desc}"
project = Project()
project.setup(id='200', name="{name}", description=desc)

voltage_reader = project.addReadUnit(datatype='VoltageReader',
                                      path="{path}",
                                      startDate="{startDate}",
                                      endDate="{endDate}",
                                      startTime="{startHour}",
                                      endTime="{endHour}",
                                      online=0,
                                      verbose=1,
                                      walk=1,
                                      )

voltage_proc = project.addProcUnit(datatype='VoltageProc', inputId=voltage_reader.getId())

profile = voltage_proc.addOperation(name='ProfileSelector', optype='other')
profile.addParameter(name='profileRangeList', value='120,183', format='intlist')

rti = voltage_proc.addOperation(name='RTIPlot', optype='other')
rti.addParameter(name='wintitle', value='Jicamarca Radio Observatory', format='str')
rti.addParameter(name='showprofile', value='0', format='int')
rti.addParameter(name='xmin', value='0', format='int')
rti.addParameter(name='xmax', value='24', format='int')
rti.addParameter(name='figpath', value="{figpath}", format='str')
rti.addParameter(name='wr_period', value='5', format='int')
rti.addParameter(name='exp_code', value='22', format='int')


controller.start()
'''

multiprocess = '''from schainpy.controller import Project, MPProject
from time import sleep
desc = "{desc}"

####################
# PLOTTER RECEIVER #
####################
plotter = Project()
plotter.setup(id='100', name='receiver', description=desc)

receiver_proc = plotter.addProcUnit(name='PlotterReceiver')
receiver_proc.addParameter(name='throttle', value=20, format='int')

rti = receiver_proc.addOperation(name='PlotRTIData', optype='other')
rti.addParameter(name='zmin', value='-40.0', format='float') 
rti.addParameter(name='zmax', value='100.0', format='float') 
rti.addParameter(name='xmin', value='0.0', format='int') 
rti.addParameter(name='colormap', value='jet', format='str') 

plotter.start()

sleep(2)

################
# DATA EMITTER #
################
project = Project()
project.setup(id='200', name="{name}", description=desc)

spectra_reader = project.addReadUnit(datatype='SpectraReader',
                                        path="{path}",
                                        startDate={startDate},
                                        endDate={endDate},
                                        startTime="{startHour}",
                                        endTime="{endHour}",
                                        online=0,
                                        verbose=1,
                                        walk=1,
                                        )

spectra_proc = project.addProcUnit(datatype='Spectra', inputId=spectra_reader.getId())

parameters_proc = project.addProcUnit(datatype='ParametersProc', inputId=spectra_proc.getId())
moments = parameters_proc.addOperation(name='SpectralMoments', optype='other')

publish = parameters_proc.addOperation(name='PublishData', optype='other')
publish.addParameter(name='zeromq', value=1, format='int')
publish.addParameter(name='verbose', value=0, format='bool')

MPProject(project, 16)


'''
