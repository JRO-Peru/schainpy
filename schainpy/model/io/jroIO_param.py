import numpy
import time
import os
import h5py
import re
import datetime

from schainpy.model.data.jrodata import *
from schainpy.model.proc.jroproc_base import ProcessingUnit, Operation
# from .jroIO_base import *
from schainpy.model.io.jroIO_base import *
import schainpy


class ParamReader(ProcessingUnit):
    '''
    Reads HDF5 format files

    path

    startDate

    endDate

    startTime

    endTime
    '''

    ext = ".hdf5"

    optchar = "D"

    timezone = None

    startTime = None

    endTime = None

    fileIndex = None

    utcList = None      #To select data in the utctime list

    blockList = None    #List to blocks to be read from the file

    blocksPerFile = None    #Number of blocks to be read

    blockIndex = None

    path = None

    #List of Files

    filenameList = None

    datetimeList = None

    #Hdf5 File

    listMetaname = None

    listMeta = None

    listDataname = None

    listData = None

    listShapes = None

    fp = None

    #dataOut reconstruction

    dataOut = None


    def __init__(self, **kwargs):
        ProcessingUnit.__init__(self, **kwargs)
        self.dataOut = Parameters()
        return

    def setup(self, **kwargs):

        path = kwargs['path']
        startDate = kwargs['startDate']
        endDate = kwargs['endDate']
        startTime = kwargs['startTime']
        endTime = kwargs['endTime']
        walk = kwargs['walk']
        if 'ext' in kwargs:
            ext = kwargs['ext']
        else:
            ext = '.hdf5'
        if 'timezone' in kwargs:
            self.timezone = kwargs['timezone']
        else:
            self.timezone = 'lt'

        print("[Reading] Searching files in offline mode ...")
        pathList, filenameList = self.searchFilesOffLine(path, startDate=startDate, endDate=endDate,
                                                               startTime=startTime, endTime=endTime,
                                                               ext=ext, walk=walk)

        if not(filenameList):
            print("There is no files into the folder: %s"%(path))
            sys.exit(-1)

        self.fileIndex = -1
        self.startTime = startTime
        self.endTime = endTime

        self.__readMetadata()

        self.__setNextFileOffline()

        return

    def searchFilesOffLine(self,
                            path,
                            startDate=None,
                            endDate=None,
                            startTime=datetime.time(0,0,0),
                            endTime=datetime.time(23,59,59),
                            ext='.hdf5',
                            walk=True):

        expLabel = ''
        self.filenameList = []
        self.datetimeList = []

        pathList = []

        JRODataObj = JRODataReader()
        dateList, pathList = JRODataObj.findDatafiles(path, startDate, endDate, expLabel, ext, walk, include_path=True)

        if dateList == []:
            print("[Reading] No *%s files in %s from %s to %s)"%(ext, path,
                                                        datetime.datetime.combine(startDate,startTime).ctime(),
                                                        datetime.datetime.combine(endDate,endTime).ctime()))

            return None, None

        if len(dateList) > 1:
            print("[Reading] %d days were found in date range: %s - %s" %(len(dateList), startDate, endDate))
        else:
            print("[Reading] data was found for the date %s" %(dateList[0]))

        filenameList = []
        datetimeList = []

        #----------------------------------------------------------------------------------

        for thisPath in pathList:
#             thisPath = pathList[pathDict[file]]

            fileList = glob.glob1(thisPath, "*%s" %ext)
            fileList.sort()

            for file in fileList:

                filename = os.path.join(thisPath,file)

                if not isFileInDateRange(filename, startDate, endDate):
                    continue

                thisDatetime = self.__isFileInTimeRange(filename, startDate, endDate, startTime, endTime)

                if not(thisDatetime):
                    continue

                filenameList.append(filename)
                datetimeList.append(thisDatetime)

        if not(filenameList):
            print("[Reading] Any file was found int time range %s - %s" %(datetime.datetime.combine(startDate,startTime).ctime(), datetime.datetime.combine(endDate,endTime).ctime()))
            return None, None

        print("[Reading] %d file(s) was(were) found in time range: %s - %s" %(len(filenameList), startTime, endTime))
        print()

#         for i in range(len(filenameList)):
#             print "[Reading] %s -> [%s]" %(filenameList[i], datetimeList[i].ctime())

        self.filenameList = filenameList
        self.datetimeList = datetimeList

        return pathList, filenameList

    def __isFileInTimeRange(self,filename, startDate, endDate, startTime, endTime):

        """
        Retorna 1 si el archivo de datos se encuentra dentro del rango de horas especificado.

        Inputs:
            filename            :    nombre completo del archivo de datos en formato Jicamarca (.r)

            startDate          :    fecha inicial del rango seleccionado en formato datetime.date

            endDate            :    fecha final del rango seleccionado en formato datetime.date

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
            fp = h5py.File(filename,'r')
            grp1 = fp['Data']

        except IOError:
            traceback.print_exc()
            raise IOError("The file %s can't be opened" %(filename))
        #chino rata
        #In case has utctime attribute
        grp2 = grp1['utctime']
#         thisUtcTime = grp2.value[0] - 5*3600 #To convert to local time
        thisUtcTime = grp2.value[0]

        fp.close()

        if self.timezone == 'lt':
            thisUtcTime -= 5*3600

        thisDatetime = datetime.datetime.fromtimestamp(thisUtcTime[0] + 5*3600)
#         thisDatetime = datetime.datetime.fromtimestamp(thisUtcTime[0])
        thisDate = thisDatetime.date()
        thisTime = thisDatetime.time()

        startUtcTime = (datetime.datetime.combine(thisDate,startTime)- datetime.datetime(1970, 1, 1)).total_seconds()
        endUtcTime = (datetime.datetime.combine(thisDate,endTime)- datetime.datetime(1970, 1, 1)).total_seconds()

        #General case
        #           o>>>>>>>>>>>>>><<<<<<<<<<<<<<o
        #-----------o----------------------------o-----------
        #       startTime                     endTime

        if endTime >= startTime:
            thisUtcLog = numpy.logical_and(thisUtcTime > startUtcTime, thisUtcTime < endUtcTime)
            if numpy.any(thisUtcLog):   #If there is one block between the hours mentioned
                return thisDatetime
            return None

        #If endTime < startTime then endTime belongs to the next day
        #<<<<<<<<<<<o                            o>>>>>>>>>>>
        #-----------o----------------------------o-----------
        #        endTime                    startTime

        if (thisDate == startDate) and numpy.all(thisUtcTime < startUtcTime):
            return None

        if (thisDate == endDate) and numpy.all(thisUtcTime > endUtcTime):
            return None

        if numpy.all(thisUtcTime < startUtcTime) and numpy.all(thisUtcTime > endUtcTime):
            return None

        return thisDatetime

    def __setNextFileOffline(self):

        self.fileIndex += 1
        idFile = self.fileIndex

        if not(idFile < len(self.filenameList)):
            print("No more Files")
            return 0

        filename = self.filenameList[idFile]

        filePointer = h5py.File(filename,'r')

        self.filename = filename

        self.fp = filePointer

        print("Setting the file: %s"%self.filename)

#         self.__readMetadata()
        self.__setBlockList()
        self.__readData()
#         self.nRecords = self.fp['Data'].attrs['blocksPerFile']
#         self.nRecords = self.fp['Data'].attrs['nRecords']
        self.blockIndex = 0
        return 1

    def __setBlockList(self):
        '''
        Selects the data within the times defined

        self.fp
        self.startTime
        self.endTime

        self.blockList
        self.blocksPerFile

        '''
        fp = self.fp
        startTime = self.startTime
        endTime = self.endTime

        grp = fp['Data']
        thisUtcTime = grp['utctime'].value.astype(numpy.float)[0]

        #ERROOOOR
        if self.timezone == 'lt':
            thisUtcTime -= 5*3600

        thisDatetime = datetime.datetime.fromtimestamp(thisUtcTime[0] + 5*3600)

        thisDate = thisDatetime.date()
        thisTime = thisDatetime.time()

        startUtcTime = (datetime.datetime.combine(thisDate,startTime) - datetime.datetime(1970, 1, 1)).total_seconds()
        endUtcTime = (datetime.datetime.combine(thisDate,endTime) - datetime.datetime(1970, 1, 1)).total_seconds()

        ind = numpy.where(numpy.logical_and(thisUtcTime >= startUtcTime, thisUtcTime < endUtcTime))[0]

        self.blockList = ind
        self.blocksPerFile = len(ind)

        return

    def __readMetadata(self):
        '''
        Reads Metadata

        self.pathMeta

        self.listShapes
        self.listMetaname
        self.listMeta

        '''

#         grp = self.fp['Data']
#         pathMeta = os.path.join(self.path, grp.attrs['metadata'])
#
#         if pathMeta == self.pathMeta:
#             return
#         else:
#             self.pathMeta = pathMeta
#
#         filePointer = h5py.File(self.pathMeta,'r')
#         groupPointer = filePointer['Metadata']

        filename = self.filenameList[0]

        fp = h5py.File(filename,'r')

        gp = fp['Metadata']

        listMetaname = []
        listMetadata = []
        for item in list(gp.items()):
            name = item[0]

            if name=='array dimensions':
                table = gp[name][:]
                listShapes = {}
                for shapes in table:
                    listShapes[shapes[0]] = numpy.array([shapes[1],shapes[2],shapes[3],shapes[4],shapes[5]])
            else:
                data = gp[name].value
                listMetaname.append(name)
                listMetadata.append(data)

#                 if name=='type':
#                     self.__initDataOut(data)

        self.listShapes = listShapes
        self.listMetaname = listMetaname
        self.listMeta = listMetadata

        fp.close()
        return

    def __readData(self):
        grp = self.fp['Data']
        listdataname = []
        listdata = []

        for item in list(grp.items()):
            name = item[0]
            listdataname.append(name)

            array = self.__setDataArray(grp[name],self.listShapes[name])
            listdata.append(array)

        self.listDataname = listdataname
        self.listData = listdata
        return

    def __setDataArray(self, dataset, shapes):

        nDims = shapes[0]

        nDim2 = shapes[1]      #Dimension 0

        nDim1 = shapes[2]      #Dimension 1, number of Points or Parameters

        nDim0 = shapes[3]      #Dimension 2, number of samples or ranges

        mode = shapes[4]        #Mode of storing

        blockList = self.blockList

        blocksPerFile = self.blocksPerFile

        #Depending on what mode the data was stored
        if mode == 0:       #Divided in channels
            arrayData = dataset.value.astype(numpy.float)[0][blockList]
        if mode == 1:     #Divided in parameter
            strds = 'table'
            nDatas = nDim1
            newShapes = (blocksPerFile,nDim2,nDim0)
        elif mode==2:       #Concatenated in a table
            strds = 'table0'
            arrayData = dataset[strds].value
            #Selecting part of the dataset
            utctime = arrayData[:,0]
            u, indices = numpy.unique(utctime, return_index=True)

            if blockList.size != indices.size:
                indMin = indices[blockList[0]]
                if blockList[1] + 1 >= indices.size:
                    arrayData = arrayData[indMin:,:]
                else:
                    indMax = indices[blockList[1] + 1]
                    arrayData = arrayData[indMin:indMax,:]
            return arrayData

        #    One dimension
        if nDims == 0:
            arrayData = dataset.value.astype(numpy.float)[0][blockList]

        #    Two dimensions
        elif nDims == 2:
            arrayData = numpy.zeros((blocksPerFile,nDim1,nDim0))
            newShapes = (blocksPerFile,nDim0)
            nDatas = nDim1

            for i in range(nDatas):
                data = dataset[strds + str(i)].value
                arrayData[:,i,:] = data[blockList,:]

        #    Three dimensions
        else:
            arrayData = numpy.zeros((blocksPerFile,nDim2,nDim1,nDim0))
            for i in range(nDatas):

                data = dataset[strds + str(i)].value

                for b in range(blockList.size):
                    arrayData[b,:,i,:] = data[:,:,blockList[b]]

        return arrayData

    def __setDataOut(self):
        listMeta = self.listMeta
        listMetaname = self.listMetaname
        listDataname = self.listDataname
        listData = self.listData
        listShapes = self.listShapes

        blockIndex = self.blockIndex
#         blockList = self.blockList

        for i in range(len(listMeta)):
            setattr(self.dataOut,listMetaname[i],listMeta[i])

        for j in range(len(listData)):
            nShapes = listShapes[listDataname[j]][0]
            mode = listShapes[listDataname[j]][4]
            if nShapes == 1:
                setattr(self.dataOut,listDataname[j],listData[j][blockIndex])
            elif nShapes > 1:
                setattr(self.dataOut,listDataname[j],listData[j][blockIndex,:])
            elif mode==0:
                setattr(self.dataOut,listDataname[j],listData[j][blockIndex])
            #Mode Meteors
            elif mode ==2:
                selectedData = self.__selectDataMode2(listData[j], blockIndex)
                setattr(self.dataOut, listDataname[j], selectedData)
        return

    def __selectDataMode2(self, data, blockIndex):
        utctime = data[:,0]
        aux, indices = numpy.unique(utctime, return_inverse=True)
        selInd = numpy.where(indices == blockIndex)[0]
        selData = data[selInd,:]

        return selData

    def getData(self):

#         if self.flagNoMoreFiles:
#             self.dataOut.flagNoData = True
#             print 'Process finished'
#             return 0
#
        if self.blockIndex==self.blocksPerFile:
             if not( self.__setNextFileOffline() ):
                self.dataOut.flagNoData = True
                return 0

#         if self.datablock == None: # setear esta condicion cuando no hayan datos por leers
#             self.dataOut.flagNoData = True
#             return 0
#         self.__readData()
        self.__setDataOut()
        self.dataOut.flagNoData = False

        self.blockIndex += 1

        return

    def run(self, **kwargs):

        if not(self.isConfig):
            self.setup(**kwargs)
#             self.setObjProperties()
            self.isConfig = True

        self.getData()

        return

class ParamWriter(Operation):
    '''
    HDF5 Writer, stores parameters data in HDF5 format files

    path:             path where the files will be stored

    blocksPerFile:    number of blocks that will be saved in per HDF5 format file

    mode:             selects the data stacking mode: '0' channels, '1' parameters, '3' table (for meteors)

    metadataList:     list of attributes that will be stored as metadata

    dataList:         list of attributes that will be stores as data

    '''


    ext = ".hdf5"

    optchar = "D"

    metaoptchar = "M"

    metaFile = None

    filename = None

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

#     arrayDim = None

    dsList = None   #List of dictionaries with dataset properties

    tableDim = None

#     dtype = [('arrayName', 'S20'),('nChannels', 'i'), ('nPoints', 'i'), ('nSamples', 'i'),('mode', 'b')]

    dtype = [('arrayName', 'S20'),('nDimensions', 'i'), ('dim2', 'i'), ('dim1', 'i'),('dim0', 'i'),('mode', 'b')]

    currentDay = None

    lastTime = None

    def __init__(self, **kwargs):
        Operation.__init__(self, **kwargs)
        self.isConfig = False
        return

    def setup(self, dataOut, path=None, blocksPerFile=10, metadataList=None, dataList=None, mode=None, **kwargs):
        self.path = path
        self.blocksPerFile = blocksPerFile
        self.metadataList = metadataList
        self.dataList = dataList
        self.dataOut = dataOut
        self.mode = mode
        
        if self.mode is not None:
            self.mode = numpy.zeros(len(self.dataList)) + mode
        else:
            self.mode = numpy.ones(len(self.dataList))

        arrayDim = numpy.zeros((len(self.dataList),5))

        #Table dimensions
        dtype0 = self.dtype
        tableList = []

        #Dictionary and list of tables
        dsList = []

        for i in range(len(self.dataList)):
            dsDict = {}
            dataAux = getattr(self.dataOut, self.dataList[i])
            dsDict['variable'] = self.dataList[i]
            #---------------------    Conditionals    ------------------------
            #There is no data
            if dataAux is None:
                return 0

            #Not array, just a number
            #Mode 0
            if type(dataAux)==float or type(dataAux)==int:
                dsDict['mode'] = 0
                dsDict['nDim'] = 0
                arrayDim[i,0] = 0
                dsList.append(dsDict)

            #Mode 2: meteors
            elif mode[i] == 2:
#                 dsDict['nDim'] = 0
                dsDict['dsName'] = 'table0'
                dsDict['mode'] = 2      # Mode meteors
                dsDict['shape'] = dataAux.shape[-1]
                dsDict['nDim'] = 0
                dsDict['dsNumber'] = 1

                arrayDim[i,3] = dataAux.shape[-1]
                arrayDim[i,4] = mode[i]         #Mode the data was stored

                dsList.append(dsDict)

            #Mode 1
            else:
                arrayDim0 = dataAux.shape       #Data dimensions
                arrayDim[i,0] = len(arrayDim0)  #Number of array dimensions
                arrayDim[i,4] = mode[i]         #Mode the data was stored

                strtable = 'table'
                dsDict['mode'] = 1      # Mode parameters

                # Three-dimension arrays
                if len(arrayDim0) == 3:
                    arrayDim[i,1:-1] = numpy.array(arrayDim0)
                    nTables = int(arrayDim[i,2])
                    dsDict['dsNumber'] = nTables
                    dsDict['shape'] = arrayDim[i,2:4]
                    dsDict['nDim'] = 3

                    for j in range(nTables):
                        dsDict = dsDict.copy()
                        dsDict['dsName'] = strtable + str(j)
                        dsList.append(dsDict)

                # Two-dimension arrays
                elif len(arrayDim0) == 2:
                    arrayDim[i,2:-1] = numpy.array(arrayDim0)
                    nTables = int(arrayDim[i,2])
                    dsDict['dsNumber'] = nTables
                    dsDict['shape'] = arrayDim[i,3]
                    dsDict['nDim'] = 2

                    for j in range(nTables):
                        dsDict = dsDict.copy()
                        dsDict['dsName'] = strtable + str(j)
                        dsList.append(dsDict)

                # One-dimension arrays
                elif len(arrayDim0) == 1:
                    arrayDim[i,3] = arrayDim0[0]
                    dsDict['shape'] = arrayDim0[0]
                    dsDict['dsNumber'] = 1
                    dsDict['dsName'] = strtable + str(0)
                    dsDict['nDim'] = 1
                    dsList.append(dsDict)

            table = numpy.array((self.dataList[i],) + tuple(arrayDim[i,:]),dtype = dtype0)
            tableList.append(table)

#         self.arrayDim = arrayDim
        self.dsList = dsList
        self.tableDim = numpy.array(tableList, dtype = dtype0)
        self.blockIndex = 0

        timeTuple = time.localtime(dataOut.utctime)
        self.currentDay = timeTuple.tm_yday
        return 1

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

        subfolder = 'd%4.4d%3.3d' % (timeTuple.tm_year,timeTuple.tm_yday)
        fullpath = os.path.join( path, subfolder )

        if not( os.path.exists(fullpath) ):
            os.mkdir(fullpath)
            setFile = -1 #inicializo mi contador de seteo

        else:
            filesList = os.listdir( fullpath )
            filesList = sorted( filesList, key=str.lower )
            if len( filesList ) > 0:
                filesList = [k for k in filesList if 'M' in k]
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

        if self.setType is None:
            setFile += 1
            file = '%s%4.4d%3.3d%03d%s' % (self.metaoptchar,
                                           timeTuple.tm_year,
                                           timeTuple.tm_yday,
                                           setFile,
                                           ext )
        else:
            setFile = timeTuple.tm_hour*60+timeTuple.tm_min
            file = '%s%4.4d%3.3d%04d%s' % (self.metaoptchar,
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

    def timeFlag(self):
        currentTime = self.dataOut.utctime

        if self.lastTime is None:
            self.lastTime = currentTime

        #Day
        timeTuple = time.localtime(currentTime)
        dataDay = timeTuple.tm_yday

        #Time
        timeDiff = currentTime - self.lastTime

        #Si el dia es diferente o si la diferencia entre un dato y otro supera la hora
        if dataDay != self.currentDay:
            self.currentDay = dataDay
            return True
        elif timeDiff > 3*60*60:
            self.lastTime = currentTime
            return True
        else:
            self.lastTime = currentTime
            return False

    def setNextFile(self):

        ext = self.ext
        path = self.path
        setFile = self.setFile
        mode = self.mode

        timeTuple = time.localtime(self.dataOut.utctime)
        subfolder = 'd%4.4d%3.3d' % (timeTuple.tm_year,timeTuple.tm_yday)

        fullpath = os.path.join( path, subfolder )

        if os.path.exists(fullpath):
            filesList = os.listdir( fullpath )
            filesList = [k for k in filesList if 'D' in k]
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
        else:
            os.makedirs(fullpath)
            setFile = -1 #inicializo mi contador de seteo

        if self.setType is None:
            setFile += 1
            file = '%s%4.4d%3.3d%03d%s' % (self.metaoptchar,
                                           timeTuple.tm_year,
                                           timeTuple.tm_yday,
                                           setFile,
                                           ext )
        else:
            setFile = timeTuple.tm_hour*60+timeTuple.tm_min
            file = '%s%4.4d%3.3d%04d%s' % (self.metaoptchar,
                                           timeTuple.tm_year,
                                           timeTuple.tm_yday,
                                           setFile,
                                           ext )

        filename = os.path.join( path, subfolder, file )

        #Setting HDF5 File
        fp = h5py.File(filename,'w')
        #write metadata
        self.writeMetadata(fp)
        #Write data
        grp = fp.create_group("Data")
#         grp.attrs['metadata'] = self.metaFile

#         grp.attrs['blocksPerFile'] = 0
        ds = []
        data = []
        dsList = self.dsList
        i = 0
        while i < len(dsList):
            dsInfo = dsList[i]
            #One-dimension data
            if dsInfo['mode'] == 0:
#                 ds0 = grp.create_dataset(self.dataList[i], (1,1), maxshape=(1,self.blocksPerFile) , chunks = True, dtype='S20')
                ds0 = grp.create_dataset(dsInfo['variable'], (1,1), maxshape=(1,self.blocksPerFile) , chunks = True, dtype=numpy.float64)
                ds.append(ds0)
                data.append([])
                i += 1
                continue
#                 nDimsForDs.append(nDims[i])

            elif dsInfo['mode'] == 2:
                grp0 = grp.create_group(dsInfo['variable'])
                ds0 = grp0.create_dataset(dsInfo['dsName'], (1,dsInfo['shape']), data = numpy.zeros((1,dsInfo['shape'])) , maxshape=(None,dsInfo['shape']), chunks=True)
                ds.append(ds0)
                data.append([])
                i += 1
                continue

            elif dsInfo['mode'] == 1:
                grp0 = grp.create_group(dsInfo['variable'])

                for j in range(dsInfo['dsNumber']):
                    dsInfo = dsList[i]
                    tableName = dsInfo['dsName']
                    shape = int(dsInfo['shape'])

                    if dsInfo['nDim'] == 3:
                        ds0 = grp0.create_dataset(tableName, (shape[0],shape[1],1) , data = numpy.zeros((shape[0],shape[1],1)), maxshape = (None,shape[1],None), chunks=True)
                    else:
                        ds0 = grp0.create_dataset(tableName, (1,shape), data = numpy.zeros((1,shape)) , maxshape=(None,shape), chunks=True)

                    ds.append(ds0)
                    data.append([])
                    i += 1
#                     nDimsForDs.append(nDims[i])

        fp.flush()
        fp.close()

#         self.nDatas = nDatas
#         self.nDims = nDims
#         self.nDimsForDs = nDimsForDs
        #Saving variables
        print('Writing the file: %s'%filename)
        self.filename = filename
#         self.fp = fp
#         self.grp = grp
#         self.grp.attrs.modify('nRecords', 1)
        self.ds = ds
        self.data = data
#         self.setFile = setFile
        self.firsttime = True
        self.blockIndex = 0
        return

    def putData(self):

        if self.blockIndex == self.blocksPerFile or self.timeFlag():
            self.setNextFile()

#         if not self.firsttime:
        self.readBlock()
        self.setBlock()     #Prepare data to be written
        self.writeBlock()   #Write data

        return

    def readBlock(self):

        '''
        data Array configured


        self.data
        '''
        dsList = self.dsList
        ds = self.ds
                #Setting HDF5 File
        fp = h5py.File(self.filename,'r+')
        grp = fp["Data"]
        ind = 0

#         grp.attrs['blocksPerFile'] = 0
        while ind < len(dsList):
            dsInfo = dsList[ind]

            if dsInfo['mode'] == 0:
                ds0 = grp[dsInfo['variable']]
                ds[ind] = ds0
                ind += 1
            else:

                grp0 = grp[dsInfo['variable']]

                for j in range(dsInfo['dsNumber']):
                    dsInfo = dsList[ind]
                    ds0 = grp0[dsInfo['dsName']]
                    ds[ind] = ds0
                    ind += 1

        self.fp = fp
        self.grp = grp
        self.ds = ds

        return

    def setBlock(self):
        '''
        data Array configured


        self.data
        '''
        #Creating Arrays
        dsList = self.dsList
        data = self.data
        ind = 0

        while ind < len(dsList):
            dsInfo = dsList[ind]
            dataAux = getattr(self.dataOut, dsInfo['variable'])

            mode = dsInfo['mode']
            nDim = dsInfo['nDim']

            if mode == 0 or mode == 2 or nDim == 1:
                data[ind] = dataAux
                ind += 1
#             elif nDim == 1:
#                 data[ind] = numpy.reshape(dataAux,(numpy.size(dataAux),1))
#                 ind += 1
            elif nDim == 2:
                for j in range(dsInfo['dsNumber']):
                    data[ind] = dataAux[j,:]
                    ind += 1
            elif nDim == 3:
                for j in range(dsInfo['dsNumber']):
                    data[ind] = dataAux[:,j,:]
                    ind += 1

        self.data = data
        return

    def writeBlock(self):
        '''
        Saves the block in the HDF5 file
        '''
        dsList = self.dsList

        for i in range(len(self.ds)):
            dsInfo = dsList[i]
            nDim = dsInfo['nDim']
            mode = dsInfo['mode']

            #    First time
            if self.firsttime:
#                 self.ds[i].resize(self.data[i].shape)
#                 self.ds[i][self.blockIndex,:] = self.data[i]
                if type(self.data[i]) == numpy.ndarray:

                    if nDim == 3:
                        self.data[i] = self.data[i].reshape((self.data[i].shape[0],self.data[i].shape[1],1))
                        self.ds[i].resize(self.data[i].shape)
                    if mode == 2:
                        self.ds[i].resize(self.data[i].shape)
                self.ds[i][:] = self.data[i]
            else:

            #    From second time
                #    Meteors!
                if mode == 2:
                    dataShape = self.data[i].shape
                    dsShape = self.ds[i].shape
                    self.ds[i].resize((self.ds[i].shape[0] + dataShape[0],self.ds[i].shape[1]))
                    self.ds[i][dsShape[0]:,:] = self.data[i]
                #    No dimension
                elif mode == 0:
                    self.ds[i].resize((self.ds[i].shape[0], self.ds[i].shape[1] + 1))
                    self.ds[i][0,-1] = self.data[i]
                #    One dimension
                elif nDim == 1:
                    self.ds[i].resize((self.ds[i].shape[0] + 1, self.ds[i].shape[1]))
                    self.ds[i][-1,:] = self.data[i]
                #    Two dimension
                elif nDim == 2:
                    self.ds[i].resize((self.ds[i].shape[0] + 1,self.ds[i].shape[1]))
                    self.ds[i][self.blockIndex,:] = self.data[i]
                #    Three dimensions
                elif nDim == 3:
                    self.ds[i].resize((self.ds[i].shape[0],self.ds[i].shape[1],self.ds[i].shape[2]+1))
                    self.ds[i][:,:,-1] = self.data[i]

        self.firsttime = False
        self.blockIndex += 1

        #Close to save changes
        self.fp.flush()
        self.fp.close()
        return

    def run(self, dataOut, path=None, blocksPerFile=10, metadataList=None, dataList=None, mode=None, **kwargs):

        if not(self.isConfig):
            flagdata = self.setup(dataOut, path=path, blocksPerFile=blocksPerFile, 
                                  metadataList=metadataList, dataList=dataList, mode=mode, **kwargs)

            if not(flagdata):
                return

            self.isConfig = True
#             self.putMetadata()
            self.setNextFile()

        self.putData()
        return