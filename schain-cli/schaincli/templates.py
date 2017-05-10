basic =
'''import argparse
from schainpy.controller import Project, multiSchain

desc = "{desc}"

controller = Project()
controller.setup(id='191', name="{name}", description=desc)

readUnitConf = controller.addReadUnit(datatype='SpectraReader',
                                             path="{path}",
                                             startDate="{startDate}",
                                             endDate="{endDate}",
                                             startTime="{startHour}",
                                             endTime="{endHour}",
                                             online=0,
                                             walk=1,
                                             )

procUnitConf2 = controllerObj.addProcUnit(datatype='Spectra', inputId=readUnitConfObj.getId())
'''
