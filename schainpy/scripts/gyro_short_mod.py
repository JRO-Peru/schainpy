#!/usr/bin/env python
'''
Created on Jul 7, 2014

@author: roj-idl71
'''
import os, sys

#path = os.path.dirname(os.getcwd())
#path = os.path.join(path, 'source')
#sys.path.insert(0, path)

from schainpy.controller import Project

if __name__ == '__main__':

    desc = "High altitude experiment SHORT "
    filename = "schain.xml"
    dpath = '/media/soporte/UUI/gyro20'
    figpath = "/media/soporte/UUI/pics_short"
    remotefolder = "/home/wmaster/graficos"
    t=['0','24']
    db_range=['15','35']
    db_range=['25','45']
    db_range=['0','35']
    period=60

    controllerObj = Project()

    controllerObj.setup(id = '191', name='test01', description=desc)

    readUnitConfObj = controllerObj.addReadUnit(datatype='Voltage',
                                                path=dpath,
                                                startDate='2019/06/04',
#                                                startDate='2018/06/18',
                                                endDate='2019/12/31',
#                                                endDate='2018/06/18',
                                                startTime='00:00:00',
                                                endTime='23:59:59',
                                                online=0,
                                                walk=0,
                                                expLabel='',
						                        delay=20)


    opObj00 = readUnitConfObj.addOperation(name='printInfo')
    opObj00 = readUnitConfObj.addOperation(name='printNumberOfBlock')

    procUnitConfObj1 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())

    opObj11 = procUnitConfObj1.addOperation(name='ProfileSelector', optype='other')
    opObj11.addParameter(name='profileList', value='(0, 1, 2, 3, 20, 21, 22, 23, 40, 41, 42, 43, 60, 61, 62, 63, 80, 81, 82, 83)', format='intlist')
#    opObj11.addParameter(name='rangeList', value='(0,63),(74,137)', format='intlist')

    #opObj11 = procUnitConfObj1.addOperation(name='filterByHeights')
    #opObj11.addParameter(name='window', value='10', format='int')
    opObj11 = procUnitConfObj1.addOperation(name='deFlip')
    opObj11.addParameter(name='channelList', value='1,3,5,7', format='intlist')

    opObj11 =  procUnitConfObj1.addOperation(name='SSheightProfiles', optype='other')
    opObj11.addParameter(name='step', value='5', format='int')
    opObj11.addParameter(name='nsamples', value='50', format='int')


    procUnitConfObj1SPC = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObj1.getId())
    procUnitConfObj1SPC.addParameter(name='nFFTPoints', value='100', format='int')
    procUnitConfObj1SPC.addParameter(name='nProfiles', value='50', format='int')
    procUnitConfObj1SPC.addParameter(name='pairsList', value='(1,0),(3,2),(5,4),(7,6)', format='pairsList')

    opObj11 = procUnitConfObj1SPC.addOperation(name='IncohInt', optype='other')
    opObj11.addParameter(name='timeInterval', value='600', format='int')

    procUnitConfObj2SPC = controllerObj.addProcUnit(datatype='SpectraAFCProc', inputId=procUnitConfObj1SPC.getId())


    '''
    opObj11 = procUnitConfObj1SPC.addOperation(name='SpectraPlot', optype='other')
    opObj11.addParameter(name='id', value='1', format='int')
    opObj11.addParameter(name='wintitle', value='Short Valley August 2019', format='str')
    opObj11.addParameter(name='xaxis', value='time', format='str')

    opObj11.addParameter(name='zmin', value=db_range[0], format='int')
    opObj11.addParameter(name='zmax', value=db_range[1], format='int')
    opObj11.addParameter(name='ymin', value='0', format='int')
    opObj11.addParameter(name='ymax', value='1500', format='int')
    #opObj11.addParameter(name='xmin', value='-5', format='int')
    #opObj11.addParameter(name='xmax', value='5', format='int')
    opObj11.addParameter(name='showprofile', value='1', format='int')
    opObj11.addParameter(name='save', value='1', format='int')
    opObj11.addParameter(name='figpath', value=figpath)
    '''
    '''
    opObj11 = procUnitConfObj1SPC.addOperation(name='RTIPlot', optype='other')
    opObj11.addParameter(name='id', value='2', format='int')
    opObj11.addParameter(name='wintitle', value='Short Valley August 2019', format='str')
    opObj11.addParameter(name='xmin', value=t[0], format='float')
    opObj11.addParameter(name='xmax', value=t[1], format='float')
    opObj11.addParameter(name='ymin', value='0', format='int')
    opObj11.addParameter(name='ymax', value='1500', format='int')
    opObj11.addParameter(name='zmin', value=db_range[0], format='int')
    opObj11.addParameter(name='zmax', value=db_range[1], format='int')
    opObj11.addParameter(name='showprofile', value='1', format='int')
    opObj11.addParameter(name='save', value='1', format='int')
    opObj11.addParameter(name='figpath', value=figpath)
    '''

    opObj11 = procUnitConfObj2SPC.addOperation(name='ACFPlot', optype='other')
    opObj11.addParameter(name='id', value='1', format='int')
    opObj11.addParameter(name='wintitle', value='Short Gyro August 2019', format='str')
    opObj11.addParameter(name='xaxis', value='time', format='str')
    opObj11.addParameter(name='channel', value='0', format='int')
    #opObj11.addParameter(name='nSampleList', value='(0,1,2,3,4,5)', format='intList')
    opObj11.addParameter(name='resolutionFactor', value='5', format='int')
    #opObj11.addParameter(name='zmin', value=0.5, format='int')
    #opObj11.addParameter(name='zmax', value=-0.5, format='int')
    #opObj11.addParameter(name='ymin', value='0', format='int')
    #opObj11.addParameter(name='ymax', value='0.5', format='int')
    #opObj11.addParameter(name='xmin', value='-1.2', format='int')
    #opObj11.addParameter(name='xmax', value='1.2', format='int')
    opObj11.addParameter(name='show', value='1', format='int')
    opObj11.addParameter(name='save', value='1', format='int')
    opObj11.addParameter(name='figpath', value=figpath)
    '''
    opObj11 = procUnitConfObj1SPC.addOperation(name='Noise', optype='other')
    opObj11.addParameter(name='id', value='3', format='int')
    opObj11.addParameter(name='wintitle', value='Short Valley August 2019', format='str')
    opObj11.addParameter(name='xmin', value=t[0], format='float')
    opObj11.addParameter(name='xmax', value=t[1], format='float')
    opObj11.addParameter(name='ymin', value=db_range[0], format='int')
    opObj11.addParameter(name='ymax', value=db_range[1], format='int')
    opObj11.addParameter(name='showprofile', value='1', format='int')
    opObj11.addParameter(name='save', value='1', format='int')
    opObj11.addParameter(name='figpath', value=figpath)


    '''


    controllerObj.start()