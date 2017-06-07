from schainpy.controller import Project

desc = "asdasddsad"

controller = Project()
controller.setup(id='191', name="asdasd", description=desc)

readUnitConf = controller.addReadUnit(datatype='VoltageReader',
                                      path="/home/nanosat/schain/schain-cli",
                                      startDate="1970/01/01",
                                      endDate="2017/12/31",
                                      startTime="00:00:00",
                                      endTime="23:59:59",
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
opObj11.addParameter(name='figpath', value="/home/nanosat/schain/schain-cli/figs", format='str')
opObj11.addParameter(name='wr_period', value='5', format='int')
opObj11.addParameter(name='exp_code', value='22', format='int')


controller.start()
