#!/usr/bin/env python
'''
Created on Jul 7, 2014

@author: roj-idl71
'''
import os
import sys

from schainpy.controller import Project


def main():

    desc = "Testing USRP data reader"
    filename = "schain.xml"
    figpath = "./"
    remotefolder = "/home/wmaster/graficos"

    # this controller object save all user configuration and then execute each module
    # with their parameters.
    controllerObj = Project()

    controllerObj.setup(id='191', name='test01', description=desc)

    # Creating a reader object with its parameters
    # schainpy.model.io.jroIO_usrp.USRPReader.setup()
    readUnitConfObj = controllerObj.addReadUnit(datatype='DigitalRF',
                                                path='/home/nanosat/data',
                                                startDate='2000/07/03',
                                                endDate='2017/07/03',
                                                startTime='00:00:00',
                                                endTime='23:59:59',
                                                online=0)

    # procUnitConfObj0 = controllerObj.addProcUnit(datatype='Voltage',
    #                                              inputId=readUnitConfObj.getId())

#     opObj10 = procUnitConfObj0.addOperation(name='selectHeights')
#     opObj10.addParameter(name='minHei', value='0', format='float')
#     opObj10.addParameter(name='maxHei', value='8', format='float')

#     opObj10 = procUnitConfObj0.addOperation(name='setH0')
#     opObj10.addParameter(name='h0', value='5.4', format='float')

#     opObj10 = procUnitConfObj0.addOperation(name='Decoder', optype='external')
#     opObj10.addParameter(name='code', value='1,-1', format='intlist')
#     opObj10.addParameter(name='nCode', value='2', format='float')
#     opObj10.addParameter(name='nBaud', value='1', format='float')

    # opObj10 = procUnitConfObj0.addOperation(name='CohInt', optype='external')
    # opObj10.addParameter(name='n', value='128', format='float')

    # opObj11 = procUnitConfObj0.addOperation(name='Scope', optype='external')
    # opObj11.addParameter(name='id', value='121', format='int')
    # opObj11.addParameter(name='wintitle', value='Scope', format='str')

    # procUnitConfObj1 = controllerObj.addProcUnit(datatype='Spectra',
    #                                              inputId=procUnitConfObj0.getId())

    # #Creating a processing object with its parameters
    # #schainpy.model.proc.jroproc_spectra.SpectraProc.run()
    # #If you need to add more parameters can use the "addParameter method"
    # procUnitConfObj1.addParameter(name='nFFTPoints', value='8', format='int')
    # procUnitConfObj1.addParameter(name='pairsList', value='(0,1)', format='pairslist')

#     opObj10 = procUnitConfObj1.addOperation(name='IncohInt', optype='external')
#     opObj10.addParameter(name='n', value='2', format='float')
#
    # Using internal methods
    # schainpy.model.proc.jroproc_spectra.SpectraProc.selectChannels()
#     opObj10 = procUnitConfObj1.addOperation(name='selectChannels')
#     opObj10.addParameter(name='channelList', value='0,1', format='intlist')

    # Using internal methods
    # schainpy.model.proc.jroproc_spectra.SpectraProc.selectHeights()
#     opObj10 = procUnitConfObj1.addOperation(name='selectHeights')
#     opObj10.addParameter(name='minHei', value='90', format='float')
#     opObj10.addParameter(name='maxHei', value='180', format='float')

    # Using external methods (new modules)
#     #schainpy.model.proc.jroproc_spectra.IncohInt.setup()
#     opObj12 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
#     opObj12.addParameter(name='n', value='1', format='int')

    # Using external methods (new modules)
    # schainpy.model.graphics.jroplot_spectra.SpectraPlot.setup()
    # opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='external')
    # opObj11.addParameter(name='id', value='11', format='int')
    # opObj11.addParameter(name='wintitle', value='SpectraPlot', format='str')
#     opObj11.addParameter(name='zmin', value='0', format='int')
#     opObj11.addParameter(name='zmax', value='90', format='int')
#     opObj11.addParameter(name='save', value='1', format='int')
#     opObj11.addParameter(name='xmin', value='-20', format='float')
#     opObj11.addParameter(name='xmax', value='20', format='float')

    # Using external methods (new modules)
    # schainpy.model.graphics.jroplot_spectra.RTIPlot.setup()
#     opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
#     opObj11.addParameter(name='id', value='30', format='int')
#     opObj11.addParameter(name='wintitle', value='RTI', format='str')
# #     opObj11.addParameter(name='zmin', value='0', format='int')
# #     opObj11.addParameter(name='zmax', value='90', format='int')
#     opObj11.addParameter(name='showprofile', value='1', format='int')
#     opObj11.addParameter(name='timerange', value=str(2*60*60), format='int')
#     opObj11.addParameter(name='xmin', value='19.5', format='float')
#     opObj11.addParameter(name='xmax', value='20', format='float')

    # opObj11 = procUnitConfObj1.addOperation(name='CrossSpectraPlot', optype='other')
    # opObj11.addParameter(name='id', value='3', format='int')
    # opObj11.addParameter(name='wintitle', value='CrossSpectraPlot', format='str')
#     opObj11.addParameter(name='zmin', value='30', format='int')
#     opObj11.addParameter(name='zmax', value='120', format='int')
#     opObj11.addParameter(name='pairsList', value='(0,1)', format='pairslist')

    controllerObj.start()


if __name__ == '__main__':
    main()
