import os, sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

def verifyCmdArguments():   
    import getopt
    arglist = ''
    path = None
    startDate = None    
    startTime = None
    endDate = None
    endTime = None
    xmin = None
    xmax = None
    zmin = None
    zmax = None
    gpath = None
    wpath = None
    save_figure = None
    save_pdata = None

    longarglist = ['path=',
                   'startDate=',
                   'startTime=',
                   'endDate=',
                   'endTime=',
                   'xmin=',
                   'xmax=',
                   'zmin=',                
                   'zmax=',
                   'gpath=',
                   'wpath=',
                   'save_figure=',
                   'save_pdata='
                   ]
    
    optlist, args = getopt.getopt(sys.argv[1:], arglist, longarglist)
            
    for opt in optlist:
        if opt[0] == '--path':
            path = opt[1]
        elif opt[0] == '--startDate':
            startDate = opt[1]
        elif opt[0] == '--startTime':
            startTime = opt[1]
        elif opt[0] == '--endDate':
            endDate = opt[1]
        elif opt[0] == '--endTime':
            endTime = opt[1]
        elif opt[0] == '--xmin':
            xmin = opt[1]
        elif opt[0] == '--xmax':
            xmax = opt[1]
        elif opt[0] == '--zmin':
            zmin = opt[1]
        elif opt[0] == '--zmax':
            zmax = opt[1]
        elif opt[0] == '--gpath':
            gpath = opt[1]
        elif opt[0] == '--wpath':
            wpath = opt[1]
        elif opt[0] == '--save_figure':
            save_figure = bool(int(opt[1]))
        elif opt[0] == '--save_pdata':
            save_pdata = bool(int(opt[1]))
                                
        else:
            print 'Illegal option %s\n%s%s' % (opt[0], usage, expId.keys())
            sys.exit(-1)
    
    #print path,startDate,startTime,endDate,endTime,xmin,xmax,zmin,zmax
    return path,startDate,startTime,endDate,endTime,xmin,xmax,zmin,zmax,gpath,save_figure,wpath,save_pdata


desc = "EWDrifts+Imaging+Faraday Experiment"
filename = "imaging_proc.xml"

controllerObj = Project()

controllerObj.setup(id = '191', name='test01', description=desc)

path = '/remote'
path = '/home/dsuarez/.gvfs/data on 10.10.20.13/EW_Faraday_imaging/d2013270'
path = '/home/dsuarez/.gvfs/data on 10.10.20.13/EW_Faraday_imaging/d2013267'
path = '/home/dsuarez/.gvfs/data on 10.10.20.13/Imaging_Driver4'

path,startDate,startTime,endDate,endTime,xmin,xmax,zmin,zmax,gpath,save_figure,wpath,save_pdata = verifyCmdArguments()


readUnitConfObj = controllerObj.addReadUnit(datatype='Voltage',
                                            path=path,
                                            startDate=startDate,
                                            endDate=endDate,
                                            startTime=startTime,
                                            endTime=endTime,
                                            delay=20,
                                            online=0,
                                            walk=1)

opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')

######################## IMAGING #############################################
procUnitConfObj0 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())


opObj11 = procUnitConfObj0.addOperation(name='Decoder', optype='other')


procUnitConfObj1 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObj0.getId())
procUnitConfObj1.addParameter(name='nProfiles', value='16', format='int')
procUnitConfObj1.addParameter(name='nFFTPoints', value='16', format='int')
 
procUnitConfObj1.addParameter(name='pairsList', value='(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(0,7), \
                            (1,2),(1,3),(1,4),(1,5),(1,6),(1,7), \
                            (2,3),(2,4),(2,5),(2,6),(2,7), \
                            (3,4),(3,5),(3,6),(3,7), \
                            (4,5),(4,6),(4,7), \
                            (5,6),(5,7), \
                            (6,7)', \
                            format='pairslist')
 
opObj11 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
opObj11.addParameter(name='timeInterval', value='5', format='float')


# opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
# opObj11.addParameter(name='id', value='2000', format='int')
# opObj11.addParameter(name='wintitle', value='Imaging', format='str')
# opObj11.addParameter(name='zmin', value='25', format='int')
# opObj11.addParameter(name='zmax', value='40', format='int')



opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
opObj11.addParameter(name='id', value='1', format='int')
opObj11.addParameter(name='wintitle', value='Imaging', format='str')
opObj11.addParameter(name='showprofile', value='0', format='int')
opObj11.addParameter(name='xmin', value=xmin, format='float')
opObj11.addParameter(name='xmax', value=xmax, format='float')
opObj11.addParameter(name='zmin', value=zmin, format='float')
opObj11.addParameter(name='zmax', value=zmax, format='float')

if save_figure:
    opObj11.addParameter(name='save', value='1', format='int')
    opObj11.addParameter(name='figpath', value=gpath, format='str')
    #opObj11.addParameter(name='figpath', value='/home/dsuarez/Pictures/Imaging_Driver4', format='str')
    opObj11.addParameter(name='wr_period', value='5', format='int')  

if save_pdata:
    opObj11 = procUnitConfObj1.addOperation(name='SpectraWriter', optype='other')
    opObj11.addParameter(name='path', value=wpath)
    #opObj11.addParameter(name='path', value='/media/datos/IMAGING/IMAGING/Driver4/')
    opObj11.addParameter(name='blocksPerFile', value='10', format='int')


# print "Escribiendo el archivo XML"
# controllerObj.writeXml(filename)
# print "Leyendo el archivo XML"
# controllerObj.readXml(filename)

controllerObj.createObjects()
controllerObj.connectObjects()
controllerObj.run()
