import numpy
import time
import os
import h5py
import re

from model.data.jrodata import *
from model.proc.jroproc_base import ProcessingUnit, Operation
from model.io.jroIO_base import *


class HDF5Reader(ProcessingUnit):
    
    ext = ".hdf5"
        
    optchar = "D"
    
    timezone = None
    
    fileIndex = None
    
    blockIndex = None
    
    path = None
    
    #Hdf5 File
    
    fpMetadata = None
    
    listMetaname = None
    
    listMetadata = None
    
    fp = None
    
    #dataOut reconstruction
    
    
    dataOut = None
    
    nChannels = None    #Dimension 0
    
    nPoints = None      #Dimension 1, number of Points or Parameters
    
    nSamples = None     #Dimension 2, number of samples or ranges
    
    
    def __init__(self):
        
        return
        
    def setup(self,path=None,
                    startDate=None, 
                    endDate=None, 
                    startTime=datetime.time(0,0,0), 
                    endTime=datetime.time(23,59,59),
                    walk=True,
                    timezone='ut',
                    all=0,
                    online=False,
                    ext=None):
        
        if ext==None:
            ext = self.ext
        self.timezone = timezone
#         self.all = all
#         self.online = online
        self.path = path
                
                
        if not(online):
            #Busqueda de archivos offline
            self.__searchFilesOffline(path, startDate, endDate, ext, startTime, endTime, walk)
        else:
            self.__searchFilesOnline(path, walk)
        
        if not(self.filenameList):
            print "There is no files into the folder: %s"%(path)
            sys.exit(-1)

#         self.__getExpParameters()

        self.fileIndex = -1
        
        self.__setNextFileOffline()
        
        self.__readMetadata()
        
        self.blockIndex = 0
        
        return
    
    def __searchFilesOffline(self,
                            path,
                            startDate,
                            endDate,
                            ext,
                            startTime=datetime.time(0,0,0),
                            endTime=datetime.time(23,59,59),
                            walk=True):
        
#         self.__setParameters(path, startDate, endDate, startTime, endTime, walk)
#         
#         self.__checkPath()
#         
#         self.__findDataForDates()
#         
#         self.__selectDataForTimes()
#         
#         for i in range(len(self.filenameList)):
#             print "%s" %(self.filenameList[i])
        
        pathList = []
        
        if not walk:
            #pathList.append(path)
            multi_path = path.split(',')
            for single_path in multi_path:
                pathList.append(single_path)
        
        else:
            #dirList = []
            multi_path = path.split(',')
            for single_path in multi_path:
                dirList = []
                for thisPath in os.listdir(single_path):
                    if not os.path.isdir(os.path.join(single_path,thisPath)):
                        continue
                    if not isDoyFolder(thisPath):
                        continue
                
                    dirList.append(thisPath)
    
                if not(dirList):
                    return None, None
            
                thisDate = startDate
            
                while(thisDate <= endDate):
                    year = thisDate.timetuple().tm_year
                    doy = thisDate.timetuple().tm_yday
                    
                    matchlist = fnmatch.filter(dirList, '?' + '%4.4d%3.3d' % (year,doy) + '*')
                    if len(matchlist) == 0:
                        thisDate += datetime.timedelta(1)
                        continue
                    for match in matchlist:
                        pathList.append(os.path.join(single_path,match))
                    
                    thisDate += datetime.timedelta(1)
        
        if pathList == []:
            print "Any folder was found for the date range: %s-%s" %(startDate, endDate)
            return None, None
        
        print "%d folder(s) was(were) found for the date range: %s - %s" %(len(pathList), startDate, endDate)
            
        filenameList = []
        datetimeList = []
        pathDict = {}
        filenameList_to_sort = []
        
        for i in range(len(pathList)):
            
            thisPath = pathList[i]
            
            fileList = glob.glob1(thisPath, "*%s" %ext)
            fileList.sort()
            pathDict.setdefault(fileList[0])
            pathDict[fileList[0]] = i
            filenameList_to_sort.append(fileList[0])
        
        filenameList_to_sort.sort()
        
        for file in filenameList_to_sort:
            thisPath = pathList[pathDict[file]]
            
            fileList = glob.glob1(thisPath, "*%s" %ext)
            fileList.sort()
        
            for file in fileList:
                
                filename = os.path.join(thisPath,file)
                thisDatetime = self.__isFileinThisTime(filename, startTime, endTime)
                
                if not(thisDatetime):
                    continue
                
                filenameList.append(filename)
                datetimeList.append(thisDatetime)
                
        if not(filenameList):
            print "Any file was found for the time range %s - %s" %(startTime, endTime)
            return None, None
        
        print "%d file(s) was(were) found for the time range: %s - %s" %(len(filenameList), startTime, endTime)
        print
        
        for i in range(len(filenameList)):
            print "%s -> [%s]" %(filenameList[i], datetimeList[i].ctime())

        self.filenameList = filenameList
        self.datetimeList = datetimeList
        
        return pathList, filenameList

    def __isFileinThisTime(self, filename, startTime, endTime):
        """
        Retorna 1 si el archivo de datos se encuentra dentro del rango de horas especificado.
        
        Inputs:
            filename            :    nombre completo del archivo de datos en formato Jicamarca (.r)
            
            startTime          :    tiempo inicial del rango seleccionado en formato datetime.time
            
            endTime            :    tiempo final del rango seleccionado en formato datetime.time
        
        Return:
            Boolean    :    Retorna True si el archivo de datos contiene datos en el rango de
                            fecha especificado, de lo contrario retorna False.
        
        Excepciones:
            Si el archivo no existe o no puede ser abierto
            Si la cabecera no puede ser leida.
            
        """
        
        
        try:
            fp = fp = h5py.File(filename,'r')
        except IOError:
            traceback.print_exc()
            raise IOError, "The file %s can't be opened" %(filename)
        
        grp = fp['Data']
        time = grp['time']
        time0 = time[:][0]
        
        fp.close()
        
        thisDatetime = datetime.datetime.utcfromtimestamp(time0)
        
        if self.timezone == 'lt':
            thisDatetime = thisDatetime - datetime.timedelta(minutes = 300)
    
        thisTime = thisDatetime.time()
            
        if not ((startTime <= thisTime) and (endTime > thisTime)):
            return None
        
        return thisDatetime
     
    def __checkPath(self):
        if os.path.exists(self.path):
            self.status = 1
        else:
            self.status = 0
            print 'Path:%s does not exists'%self.path
            
        return
    
    def __setNextFileOffline(self):
        idFile = self.fileIndex
        idFile += 1
        
        if not(idFile < len(self.filenameList)):
            self.flagNoMoreFiles = 1
            print "No more Files"
            return 0

        filename = self.filenameList[idFile]

        filePointer = h5py.File(filename,'r')
            
        self.flagIsNewFile = 1
        self.fileIndex = idFile
        self.filename = filename

        self.fp = filePointer

        print "Setting the file: %s"%self.filename
        
        self.__readMetadata()
        
        return 1
    
    def __readMetadata(self):
        grp = self.fp['Data']
        self.pathMeta = os.path.join(self.path, grp.attrs['metadata'])
        filePointer = h5py.File(self.pathMeta,'r')
        groupPointer = filePointer['Metadata']
        
        listMetaname = []
        listMetadata = []
        for item in groupPointer.items():
            name = item[0]
            
            if name=='data shape':
                self.nSamples = 1
                self.nPoints = 1
                self.nChannels = 1
            else:
                data = groupPointer[name][:]
                listMetaname.append(name)
                listMetadata.append(data)
                
                if name=='type':
                    self.__initDataOut(name)
                    
        filePointer.close()
        
        self.listMetadata = listMetaname
        self.listMetadata = listMetadata
        
        return
    
    def __initDataOut(self, type):
        
        if 'type'=='Parameters':
            self.dataOut = Parameters()
        elif 'type'=='Spectra':
            self.dataOut = Spectra()
        elif 'type'=='Voltage':
            self.dataOut = Voltage()
        elif 'type'=='Correlation':
            self.dataOut = Correlation()
            
        return
    
    def __setDataOut(self):
        listMetadata = self.listMetadata
        listMetaname = self.listMetaname
        listDataname = self.listDataname
        listData = self.listData
        
        blockIndex = self.blockIndex
        
        for i in range(len(listMetadata)):
            setattr(self.dataOut,listMetaname[i],listMetadata[i])
        
        for j in range(len(listData)):
            setattr(self.dataOut,listDataname[j][blockIndex,:],listData[j][blockIndex,:])
        
        return
    
    def getData(self):
        
        if self.flagNoMoreFiles:
            self.dataOut.flagNoData = True
            print 'Process finished'
            return 0
        
        if self.__hasNotDataInBuffer():
            self.__setNextFile()

        
        if self.datablock == None: # setear esta condicion cuando no hayan datos por leers
            self.dataOut.flagNoData = True 
            return 0
        
        self.__setDataOut()
        self.dataOut.flagNoData = False
        
        self.blockIndex += 1
        
        return self.dataOut.data
    
    def run(self, **kwargs):
        
        if not(self.isConfig):
            self.setup(**kwargs)
            self.setObjProperties()
            self.isConfig = True
        
        self.getData()
    
        return

class HDF5Writer(Operation):
    
    ext = ".hdf5"
    
    optchar = "D"
    
    metaoptchar = "M"
    
    metaFile = None
    
    path = None
    
    setFile = None
    
    fp = None
    
    grp = None
    
    ds = None
    
    firsttime = True
    
    #Configurations
    
    blocksPerFile = None
    
    blockIndex = None
    
    dataOut = None
    
    #Data Arrays
    
    dataList = None
    
    metadataList = None
    
    dataDim = None
    
    tableDim = None
    
    dtype = [('arrayName', 'S10'),('nChannels', 'i'), ('nPoints', 'i'), ('nSamples', 'i')]
    
    def __init__(self):
        
        Operation.__init__(self)
        self.isConfig = False
        return
    
    
    def setup(self, dataOut, **kwargs):

        self.path = kwargs['path']
        
        if kwargs.has_key('ext'):    
            self.ext = kwargs['ext']
        else:                         
            self.blocksPerFile = 10
        
        if kwargs.has_key('blocksPerFile'):    
            self.blocksPerFile = kwargs['blocksPerFile']
        else:                         
            self.blocksPerFile = 10
        
        self.dataOut = dataOut
        
        self.metadataList = ['type','inputUnit','abscissaRange','heightRange']
         
        self.dataList = ['data_param', 'data_error', 'data_SNR']
        
        self.dataDim = numpy.zeros((len(self.dataList),3))
        
        #Data types
        
        dtype0 = self.dtype
        
        tableList = []
        
        for i in range(len(self.dataList)):
            
            dataDim = getattr(self.dataOut, self.dataList[i]).shape
            
            if len(dataDim) == 3:
                self.dataDim[i,:] = numpy.array(dataDim)
            else:
                self.dataDim[i,0] = numpy.array(dataDim)[0]
                self.dataDim[i,2] = numpy.array(dataDim)[1]
                self.dataDim[i,1] = 1
                
            table = numpy.array((self.dataList[i],) + tuple(self.dataDim[i,:]),dtype = dtype0)
            tableList.append(table)
            
        self.tableDim = numpy.array(tableList, dtype = dtype0)        
        self.blockIndex = 0
        
        return

    def putMetadata(self):
        
        fp = self.createMetadataFile()
        self.writeMetadata(fp)    
        fp.close()
        return
    
    def createMetadataFile(self):
        ext = self.ext
        path = self.path
        setFile = self.setFile
         
        timeTuple = time.localtime(self.dataOut.utctime)
        subfolder = ''

        fullpath = os.path.join( path, subfolder )
        if not( os.path.exists(fullpath) ):
            os.mkdir(fullpath)
            setFile = -1 #inicializo mi contador de seteo
        else:
            filesList = os.listdir( fullpath )
            if len( filesList ) > 0:
                filesList = sorted( filesList, key=str.lower )
                filen = filesList[-1]
                # el filename debera tener el siguiente formato
                # 0 1234 567 89A BCDE (hex)
                # x YYYY DDD SSS .ext
                if isNumber( filen[8:11] ):
                    setFile = int( filen[8:11] ) #inicializo mi contador de seteo al seteo del ultimo file
                else:    
                    setFile = -1
            else:
                setFile = -1 #inicializo mi contador de seteo

        setFile += 1
                
        file = '%s%4.4d%3.3d%3.3d%s' % (self.metaoptchar,
                                        timeTuple.tm_year,
                                        timeTuple.tm_yday,
                                        setFile,
                                        ext )

        filename = os.path.join( path, subfolder, file )
        self.metaFile = file
        #Setting HDF5 File
        fp = h5py.File(filename,'w')

        return fp
    
    def writeMetadata(self, fp): 
        
        grp = fp.create_group("Metadata")
        grp.create_dataset('array dimensions', data = self.tableDim, dtype = self.dtype)
        
        for i in range(len(self.metadataList)):
            grp.create_dataset(self.metadataList[i], data=getattr(self.dataOut, self.metadataList[i]))
        return
        
    def setNextFile(self):
        
        ext = self.ext
        path = self.path
        setFile = self.setFile
        
        if self.fp != None:
            self.fp.close()
        
        timeTuple = time.localtime(self.dataOut.utctime)
        subfolder = 'd%4.4d%3.3d' % (timeTuple.tm_year,timeTuple.tm_yday)

        fullpath = os.path.join( path, subfolder )
        if not( os.path.exists(fullpath) ):
            os.mkdir(fullpath)
            setFile = -1 #inicializo mi contador de seteo
        else:
            filesList = os.listdir( fullpath )
            if len( filesList ) > 0:
                filesList = sorted( filesList, key=str.lower )
                filen = filesList[-1]
                # el filename debera tener el siguiente formato
                # 0 1234 567 89A BCDE (hex)
                # x YYYY DDD SSS .ext
                if isNumber( filen[8:11] ):
                    setFile = int( filen[8:11] ) #inicializo mi contador de seteo al seteo del ultimo file
                else:    
                    setFile = -1
            else:
                setFile = -1 #inicializo mi contador de seteo

        setFile += 1
                
        file = '%s%4.4d%3.3d%3.3d%s' % (self.optchar,
                                        timeTuple.tm_year,
                                        timeTuple.tm_yday,
                                        setFile,
                                        ext )

        filename = os.path.join( path, subfolder, file )

        #Setting HDF5 File
        fp = h5py.File(filename,'w')
        grp = fp.create_group("Data")
        grp.attrs['metadata'] = self.metaFile
        
        grp['blocksPerFile'] = 0
        
        ds = []
        data = []
        
        for i in range(len(self.dataList)):
            
            grp0 = grp.create_group(self.dataList[i])
                
            for j in range(int(self.dataDim[i,0])):
                tableName = "channel" + str(j)
                
                if not(self.dataDim[i,1] == 1):
                    ds0 = grp0.create_dataset(tableName, (1,1,1) , chunks = True)
                else:
                    ds0 = grp0.create_dataset(tableName, (1,1) , chunks = True)
                
                ds.append(ds0)
                data.append([])
    
        ds0 = grp.create_dataset("time", (1,) , chunks = True)
        ds.append(ds0)
        data.append([])
        
        #Saving variables        
        print 'Writing the file: %s'%filename
        self.fp = fp
        self.grp = grp
        self.ds = ds
        self.data = data
        
        self.setFile = setFile
        self.firsttime = True
        self.blockIndex = 0
        return     
    
    def putData(self):
        self.setBlock()
        self.writeBlock()
        
        if self.blockIndex == self.blocksPerFile:
            self.setNextFile()     
        return
    
    def setBlock(self):
        '''
        data Array configured
        
        '''
        #Creating Arrays
        data = self.data
        ind = 0
        for i in range(len(self.dataList)):
            dataAux = getattr(self.dataOut,self.dataList[i])
            
            for j in range(int(self.dataDim[i,0])):
                data[ind] = dataAux[j,:]
                
                if not(self.dataDim[i,1] == 1):
                    data[ind] = data[ind].reshape((data[ind].shape[0],data[ind].shape[1],1))
                    if not self.firsttime:
                        data[ind] = numpy.dstack((self.ds[ind][:], data[ind]))
                else:
                    data[ind] = data[ind].reshape((1,data[ind].shape[0]))
                    if not self.firsttime:
                        data[ind] = numpy.vstack((self.ds[ind][:], data[ind]))                    
                ind += 1
            
        data[ind] = numpy.array([self.dataOut.utctime])
        if not self.firsttime:
            self.data[ind] = numpy.hstack((self.ds[ind][:], self.data[ind]))
        self.data = data
        
        return
    
    def writeBlock(self):
        '''
        Saves the block in the HDF5 file
        '''
        for i in range(len(self.ds)):
            self.ds[i].shape = self.data[i].shape 
            self.ds[i][:] = self.data[i]     
        
        self.blockIndex += 1
        
        self.grp.attrs.modify('blocksPerFile', self.blockIndex)
        
        self.firsttime = False
        return
    
    def run(self, dataOut, **kwargs):
        if not(self.isConfig):
            self.setup(dataOut, **kwargs)
            self.isConfig = True
            self.putMetadata()
            self.setNextFile()
            
        self.putData()
        return
        
