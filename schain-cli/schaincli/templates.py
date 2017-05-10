basic = '''from schainpy.controller import Project

desc = "{desc}"

controller = Project()
controller.setup(id='191', name="{name}", description=desc)

readUnitConf = controller.addReadUnit(datatype='VoltageReader',
                                      path="{path}",
                                      startDate="{startDate}",
                                      endDate="{endDate}",
                                      startTime="{startHour}",
                                      endTime="{endHour}",
                                      online=0,
                                      verbose=1,
                                      walk=1,
                                      )

procUnitConf1 = controller.addProcUnit(datatype='VoltageProc', inputId=readUnitConf.getId())

opObj11 = procUnitConf1.addOperation(name='ProfileSelector', optype='other')
opObj11.addParameter(name='profileRangeList', value='120,183', format='intlist')

opObj11 = procUnitConf1.addOperation(name='RTIPlot', optype='other')
opObj11.addParameter(name='wintitle', value='Jicamarca Radio Observatory', format='str')
opObj11.addParameter(name='showprofile', value='0', format='int')
opObj11.addParameter(name='xmin', value='0', format='int')
opObj11.addParameter(name='xmax', value='24', format='int')
opObj11.addParameter(name='figpath', value="{figpath}", format='str')
opObj11.addParameter(name='wr_period', value='5', format='int')
opObj11.addParameter(name='exp_code', value='22', format='int')


controller.start()
'''

multiprocess = '''from schainpy.controller import Project, multiSchain

desc = "{desc}"

def fiber(cursor, skip, q, day):
    controller = Project()
    controller.setup(id='191', name="{name}", description=desc)

    readUnitConf = controller.addReadUnit(datatype='SpectraReader',
                                          path="{path}",
                                          startDate="day",
                                          endDate="day",
                                          startTime="{startHour}",
                                          endTime="{endHour}",
                                          online=0,
                                          queue=q,
                                          cursor=cursor,
                                          skip=skip,
                                          verbose=1,
                                          walk=1,
                                          )

    procUnitConf1 = controller.addProcUnit(datatype='Spectra', inputId=readUnitConf.getId())

    procUnitConf2 = controller.addProcUnit(datatype='ParametersProc', inputId=readUnitConf.getId())
    opObj11 = procUnitConf2.addOperation(name='SpectralMoments', optype='other')

    opObj12 = procUnitConf2.addOperation(name='PublishData', optype='other')
    opObj12.addParameter(name='zeromq', value=1, format='int')
    opObj12.addParameter(name='verbose', value=0, format='bool')

    controller.start()


if __name__ == '__main__':
    multiSchain(fiber, nProcess={nProcess}, startDate="{startDate}", endDate="{endDate}")


'''
