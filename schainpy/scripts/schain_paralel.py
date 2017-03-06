from mpi4py import MPI
import datetime
import os, sys
#import timeit

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

def conversion(x1,x2):
    a=[x1,x2]
    for x in a:
        m,s = divmod(x,60)
        h,m = divmod(m,60)
        if x==x1:
            startime= str("%02d:%02d:%02d" % (h, m, s))
        if x==x2:
            endtime =str("%02d:%02d:%02d" % (h, m, s))
    return startime,endtime



def loop(startime,endtime,rank):
    desc = "HF_EXAMPLE"+str(rank)
    path= "/home/alex/Documents/hysell_data/pdata/sp1_f0"
    figpath= "/home/alex/Pictures/pdata_plot"+str(rank)

    filename = "hf_test"+str(rank)+".xml"
    
    controllerObj = Project()
    
    controllerObj.setup(id = '191', name='test01'+str(rank), description=desc)   

    readUnitConfObj = controllerObj.addReadUnit(datatype='SpectraReader',
                                                 path=path,
                                                 startDate='2015/09/26',
                                                 endDate='2015/09/26',
                                                 startTime=startime,
                                                 endTime=endtime,
                                                 online=0,
                                                 #set=1426485881,
                                                 delay=10,
                                                 walk=1
                                                 #timezone=-5*3600
                                                 )

    #opObj11 = readUnitConfObj.addOperation(name='printNumberOfBlock')
     
    procUnitConfObj1 = controllerObj.addProcUnit(datatype='SpectraProc', inputId=readUnitConfObj.getId())
    
    opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
    opObj11.addParameter(name='id', value='1000', format='int')
    opObj11.addParameter(name='wintitle', value='HF_Jicamarca_Spc', format='str')
    #opObj11.addParameter(name='channelList', value='0', format='intlist') 
    opObj11.addParameter(name='zmin', value='-120', format='float')
    opObj11.addParameter(name='zmax', value='-70', format='float')
    opObj11.addParameter(name='save', value='1', format='int')
    opObj11.addParameter(name='figpath', value=figpath, format='str')
    

    print "Escribiendo el archivo XML"
    controllerObj.writeXml(filename)
    print "Leyendo el archivo XML"
    controllerObj.readXml(filename)
    
    controllerObj.createObjects()
    controllerObj.connectObjects()
    
    #timeit.timeit('controllerObj.run()', number=2)
    
    controllerObj.run()

    

def parallel():
    
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()  
    totalStartTime = time.time()
    print "Hello world from process %d/%d"%(rank,size)
    # First just for one day :D!
    num_hours = 4/size
    time1,time2 = rank*num_hours*3600,(rank+1)*num_hours*3600-60
    #print time1,time2
    startime,endtime =conversion(time1,time2)
    print startime,endtime
    loop(startime,endtime,rank)
    print "Total time %f seconds" %(time.time() -totalStartTime)

if __name__=='__main__':
    parallel()