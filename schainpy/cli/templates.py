voltage = '''import os, sys, time 
from schainpy.controller import Project


def main():
    desc = "{desc}"
    controller = Project()
    controller.setup(id='200', name="{name}", description=desc)

    read_unit = controller.addReadUnit(datatype='Voltage',
                                        path="{path}",
                                        startDate="{startDate}",
                                        endDate="{endDate}",
                                        startTime="{startHour}",
                                        endTime="{endHour}",
                                        online=0,
                                        verbose=1,
                                        walk=0,
                                        delay=180,
                                        )

    code = '[[1, 1, -1], [-1, -1, 1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [-1, -1, 1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [-1, -1, 1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [-1, -1, 1], [-1, -1, 1], [-1, -1, 1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [-1, -1, 1], [-1, -1, 1], [1, 1, -1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [-1, -1, 1], [-1, -1, 1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [1, 1, -1], [-1, -1, 1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [-1, -1, 1], [-1, -1, 1], [-1, -1, 1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [-1, -1, 1], [-1, -1, 1], [1, 1, -1], [1, 1, -1], [-1, -1, 1], [-1, -1, 1], [-1, -1, 1], [-1, -1, 1], [-1, -1, 1], [-1, -1, 1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [-1, -1, 1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [-1, -1, 1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [-1, -1, 1], [-1, -1, 1], [1, 1, -1]]'
    nCode = '128'
    nBaud = '3'


    proc_voltage = controller.addProcUnit(name='VoltageProc', inputId=read_unit.getId())

    op1 = proc_voltage.addOperation(name='selectChannels', optype='self')
    op1.addParameter(name='channelList', value='0, 1, 2, 3', format='intlist')

    op2 = proc_voltage.addOperation(name='filterByHeights', optype='self')
    op2.addParameter(name='window', value='4', format='int')

    op3 = proc_voltage.addOperation(name='ProfileSelector', optype='other')
    op3.addParameter(name='profileRangeList', value='32, 159', format='intList')

    op4 = proc_voltage.addOperation(name='Decoder', optype='other')
    op4.addParameter(name='code', value=code, format='intlist')
    op4.addParameter(name='nCode', value=nCode, format='int')
    op4.addParameter(name='nBaud', value=nBaud, format='int')
    op4.addParameter(name='mode', value='0', format='int')
    
    op5 = proc_voltage.addOperation(name='Scope', optype='external')
    op5.addParameter(name='id', value='30', format='int')
    




    controller.start()

if __name__ == '__main__':
    import time
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))

'''


spectra = '''import os, sys, time 
from schainpy.controller import Project


def main():
    desc = "{desc}"
    controller = Project()
    controller.setup(id='300', name="{name}", description=desc)

    read_unit = controller.addReadUnit(datatype='Spectra',
                                        path="{path}",
                                        startDate="{startDate}",
                                        endDate="{endDate}",
                                        startTime="{startHour}",
                                        endTime="{endHour}",
                                        online=0,
                                        verbose=1,
                                        walk=0,
                                        delay=180,
                                        )

    proc_spectra = controller.addProcUnit(datatype='Spectra', inputId=read_unit.getId())
    proc_spectra.addParameter(name='nFFTPoints', value='128', format='int')  
    proc_spectra.addParameter(name='nProfiles', value='128', format='int')
    proc_spectra.addParameter(name='pairsList', value='(0, 1), (2, 3)', format='pairslist')

    op1 = proc_spectra.addOperation(name='IncohInt', optype='other')
    op1.addParameter(name='n', value='4', format='int')

    op2 = proc_spectra.addOperation(name='CrossSpectraPlot', optype='external')
    op2.addParameter(name='id', value='10', format='int')
    op2.addParameter(name='zmin', value='10.0', format='float')
    op2.addParameter(name='zmax', value='35.0', format='float')
        

    op3 = proc_spectra.addOperation(name='RTIPlot', optype='external')
    op3.addParameter(name='id', value='20', format='int')
    op3.addParameter(name='wintitle', value='RTI', format='str')
    op3.addParameter(name='xmin', value='0', format='float')
    op3.addParameter(name='xmax', value='24', format='float')
    op3.addParameter(name='zmin', value='12', format='int')
    op3.addParameter(name='zmax', value='32', format='int')
    op3.addParameter(name='showprofile', value='1', format='int')
    op3.addParameter(name='timerange', value=str(24*60*60), format='int')

    op4 = proc_spectra.addOperation(name='CoherenceMap', optype='external')
    op4.addParameter(name='id', value='30', format='int')
    op4.addParameter(name='xmin', value='0.0', format='float')
    op4.addParameter(name='xmax', value='24.0', format='float')


    controller.start()

if __name__ == '__main__':
    import time
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))

'''

voltagespectra = '''import os, sys, time 
from schainpy.controller import Project


def main():
    desc = "{desc}"
    controller = Project()
    controller.setup(id='400', name="{name}", description=desc)

    read_unit = controller.addReadUnit(datatype='Voltage',
                                        path="{path}",
                                        startDate="{startDate}",
                                        endDate="{endDate}",
                                        startTime="{startHour}",
                                        endTime="{endHour}",
                                        online=0,
                                        verbose=1,
                                        walk=0,
                                        delay=180,
                                        )

    code = '[[1, 1, -1], [-1, -1, 1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [-1, -1, 1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [-1, -1, 1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [-1, -1, 1], [-1, -1, 1], [-1, -1, 1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [-1, -1, 1], [-1, -1, 1], [1, 1, -1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [-1, -1, 1], [-1, -1, 1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [1, 1, -1], [-1, -1, 1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [-1, -1, 1], [-1, -1, 1], [-1, -1, 1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [-1, -1, 1], [-1, -1, 1], [1, 1, -1], [1, 1, -1], [-1, -1, 1], [-1, -1, 1], [-1, -1, 1], [-1, -1, 1], [-1, -1, 1], [-1, -1, 1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [1, 1, -1], [-1, -1, 1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [-1, -1, 1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [1, 1, -1], [-1, -1, 1], [-1, -1, 1], [-1, -1, 1], [1, 1, -1]]'
    nCode = '128'
    nBaud = '3'


    proc_voltage = controller.addProcUnit(name='VoltageProc', inputId=read_unit.getId())

    op1 = proc_voltage.addOperation(name='selectChannels', optype='self')
    op1.addParameter(name='channelList', value='0, 1, 2, 3', format='intlist')

    op2 = proc_voltage.addOperation(name='filterByHeights', optype='self')
    op2.addParameter(name='window', value='4', format='int')

    op3 = proc_voltage.addOperation(name='ProfileSelector', optype='other')
    op3.addParameter(name='profileRangeList', value='32, 159', format='intList')

    op4 = proc_voltage.addOperation(name='Decoder', optype='other')
    op4.addParameter(name='code', value=code, format='intlist')
    op4.addParameter(name='nCode', value=nCode, format='int')
    op4.addParameter(name='nBaud', value=nBaud, format='int')
    op4.addParameter(name='mode', value='0', format='int')



    proc_spectra = controller.addProcUnit(datatype='Spectra', inputId=proc_voltage.getId())
    proc_spectra.addParameter(name='nFFTPoints', value='128', format='int')  
    proc_spectra.addParameter(name='nProfiles', value='128', format='int')
    proc_spectra.addParameter(name='pairsList', value='(0, 1), (2, 3)', format='pairslist')

    op5 = proc_spectra.addOperation(name='IncohInt', optype='other')
    op5.addParameter(name='n', value='4', format='int')

    op6 = proc_spectra.addOperation(name='CrossSpectraPlot', optype='external')
    op6.addParameter(name='id', value='10', format='int')
    op6.addParameter(name='zmin', value='10.0', format='float')
    op6.addParameter(name='zmax', value='35.0', format='float')
        

    op7 = proc_spectra.addOperation(name='RTIPlot', optype='external')
    op7.addParameter(name='id', value='20', format='int')
    op7.addParameter(name='wintitle', value='RTI', format='str')
    op7.addParameter(name='xmin', value='0', format='float')
    op7.addParameter(name='xmax', value='24', format='float')
    op7.addParameter(name='zmin', value='12', format='int')
    op7.addParameter(name='zmax', value='32', format='int')
    op7.addParameter(name='showprofile', value='1', format='int')
    op7.addParameter(name='timerange', value=str(24*60*60), format='int')

    op8 = proc_spectra.addOperation(name='CoherenceMap', optype='external')
    op8.addParameter(name='id', value='30', format='int')
    op8.addParameter(name='xmin', value='0.0', format='float')
    op8.addParameter(name='xmax', value='24.0', format='float')


    controller.start()

if __name__ == '__main__':
    import time
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))

'''








multiprocess = '''from schainpy.controller import Project, MPProject
from time import sleep
desc = "{desc}"

####################
# PLOTTER RECEIVER #
####################
plotter = Project()
plotter.setup(id='100', name='receiver', description=desc)

receiver_plot = plotter.addProcUnit(name='PlotterReceiver')
receiver_plot.addParameter(name='throttle', value=20, format='int')
receiver_plot.addParameter(name='plottypes', value='rti', format='str')

rti = receiver_plot.addOperation(name='PlotRTIData', optype='other')
rti.addParameter(name='zmin', value='-40.0', format='float') 
rti.addParameter(name='zmax', value='100.0', format='float') 
rti.addParameter(name='decimation', value='200', format='int') 
rti.addParameter(name='xmin', value='0.0', format='int') 
rti.addParameter(name='colormap', value='jet', format='str') 

plotter.start()

sleep(2)

################
# DATA EMITTER #
################
controller = Project()
controller.setup(id='200', name="{name}", description=desc)

spectra_reader = controller.addReadUnit(datatype='SpectraReader',
                                        path="{path}",
                                        startDate={startDate},
                                        endDate={endDate},
                                        startTime="{startHour}",
                                        endTime="{endHour}",
                                        online=0,
                                        verbose=1,
                                        walk=1,
                                        )

spectra_proc = controller.addProcUnit(datatype='Spectra', inputId=spectra_reader.getId())

parameters_proc = controller.addProcUnit(datatype='ParametersProc', inputId=spectra_proc.getId())
moments = parameters_proc.addOperation(name='SpectralMoments', optype='other')

publish = parameters_proc.addOperation(name='PublishData', optype='other')
publish.addParameter(name='zeromq', value=1, format='int')
publish.addParameter(name='verbose', value=0, format='bool')

MPProject(controller, 16)


'''
