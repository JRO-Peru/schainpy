import argparse

from schainpy.controller import Project, multiSchain

desc = "HF_EXAMPLE"

def fiber(cursor, skip, q, dt):

    controllerObj = Project()

    controllerObj.setup(id='191', name='test01', description=desc)

    readUnitConfObj = controllerObj.addReadUnit(datatype='SpectraReader',
                                                 path='/data/workspace/data/julia/',
                                                 startDate=dt,
                                                 endDate=dt,
                                                 startTime="00:00:00",
                                                 endTime="23:59:59",
                                                 online=0,
                                                 #set=1426485881,
                                                 delay=10,
                                                 walk=1,
                                                 queue=q,
                                                 cursor=cursor,
                                                 skip=skip,
                                                 #timezone=-5*3600
                                                 )

    #     #opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')
    #
    procUnitConfObj2 = controllerObj.addProcUnit(datatype='Spectra', inputId=readUnitConfObj.getId())
    # opObj11 = procUnitConfObj2.addParameter(name='pairsList', value='(0,1)', format='pairslist')
    #
    # procUnitConfObj2 = controllerObj.addProcUnit(datatype='ParametersProc', inputId=readUnitConfObj.getId())

    # opObj11 = procUnitConfObj2.addOperation(name='SpectralMoments', optype='other')

    #
    #     opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
    #     opObj11.addParameter(name='id', value='1000', format='int')
    #     opObj11.addParameter(name='wintitle', value='HF_Jicamarca_Spc', format='str')
    #     opObj11.addParameter(name='channelList', value='0', format='intlist')
    #     opObj11.addParameter(name='zmin', value='-120', format='float')
    #     opObj11.addParameter(name='zmax', value='-70', format='float')
    #     opObj11.addParameter(name='save', value='1', format='int')
    #     opObj11.addParameter(name='figpath', value=figpath, format='str')

    # opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
    # opObj11.addParameter(name='id', value='2000', format='int')
    # opObj11.addParameter(name='wintitle', value='HF_Jicamarca', format='str')
    # opObj11.addParameter(name='showprofile', value='0', format='int')
    # opObj11.addParameter(name='channelList', value='0', format='intlist')
    # #     opObj11.addParameter(name='xmin', value='0', format='float')
    # opObj11.addParameter(name='xmin', value='0', format='float')
    # opObj11.addParameter(name='xmax', value='24', format='float')
    #
    # opObj11.addParameter(name='zmin', value='-110', format='float')
    # opObj11.addParameter(name='zmax', value='-70', format='float')
    # opObj11.addParameter(name='save', value='0', format='int')
    # opObj11.addParameter(name='figpath', value='/tmp/', format='str')

    opObj12 = procUnitConfObj2.addOperation(name='PublishData', optype='other')
    opObj12.addParameter(name='zeromq', value=1, format='int')

    # print "Escribiendo el archivo XML"
    # controllerObj.writeXml(filename)
    # print "Leyendo el archivo XML"
    # controllerObj.readXml(filename)

    controllerObj.createObjects()
    controllerObj.connectObjects()

    # timeit.timeit('controllerObj.run()', number=2)

    controllerObj.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Set number of parallel processes')
    parser.add_argument('--nProcess', default=2, type=int)
    args = parser.parse_args()
    multiSchain(fiber, nProcess=args.nProcess, startDate='2016/08/19', endDate='2016/08/20')
