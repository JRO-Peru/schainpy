import os
import time
import datetime

import numpy
import h5py

import schainpy.admin
from schainpy.model.data.jrodata import *
from schainpy.model.proc.jroproc_base import ProcessingUnit, Operation, MPDecorator
from schainpy.model.io.jroIO_base import *
from schainpy.utils import log


class HDFReader(Reader, ProcessingUnit):
    """Processing unit to read HDF5 format files

    This unit reads HDF5 files created with `HDFWriter` operation contains
    by default two groups Data and Metadata all variables would be saved as `dataOut`
    attributes. 
    It is possible to read any HDF5 file by given the structure in the `description`
    parameter, also you can add extra values to metadata with the parameter `extras`.

    Parameters:
    -----------
    path : str
        Path where files are located.
    startDate : date
        Start date of the files
    endDate : list
        End date of the files
    startTime : time
        Start time of the files
    endTime : time
        End time of the files
    description : dict, optional
        Dictionary with the description of the HDF5 file
    extras : dict, optional
        Dictionary with extra metadata to be be added to `dataOut`
    
    Examples
    --------
    
    desc = {
        'Data': {
            'data_output': ['u', 'v', 'w'],
            'utctime': 'timestamps',
        }  ,
        'Metadata': {
            'heightList': 'heights'
        }
    }

    desc = {
        'Data': {
            'data_output': 'winds',
            'utctime': 'timestamps'
        },
        'Metadata': {
            'heightList': 'heights'
        }
    }

    extras = {
        'timeZone': 300
    }
    
    reader = project.addReadUnit(
        name='HDFReader',
        path='/path/to/files',
        startDate='2019/01/01',
        endDate='2019/01/31',
        startTime='00:00:00',
        endTime='23:59:59',
        # description=json.dumps(desc),
        # extras=json.dumps(extras),
        )

    """

    __attrs__ = ['path', 'startDate', 'endDate', 'startTime', 'endTime', 'description', 'extras']

    def __init__(self):
        ProcessingUnit.__init__(self)
        self.dataOut = Parameters()
        self.ext = ".hdf5"
        self.optchar = "D"
        self.meta = {}
        self.data = {}
        self.open_file = h5py.File
        self.open_mode = 'r'
        self.description = {}
        self.extras = {}
        self.filefmt = "*%Y%j***"
        self.folderfmt = "*%Y%j"

    def setup(self, **kwargs):

        self.set_kwargs(**kwargs)
        if not self.ext.startswith('.'):
            self.ext = '.{}'.format(self.ext)            

        if self.online:
            log.log("Searching files in online mode...", self.name)

            for nTries in range(self.nTries):
                fullpath = self.searchFilesOnLine(self.path, self.startDate,
                    self.endDate, self.expLabel, self.ext, self.walk, 
                    self.filefmt, self.folderfmt)
                try:
                    fullpath = next(fullpath)
                except:
                    fullpath = None
                
                if fullpath:
                    break

                log.warning(
                    'Waiting {} sec for a valid file in {}: try {} ...'.format(
                        self.delay, self.path, nTries + 1), 
                    self.name)
                time.sleep(self.delay)

            if not(fullpath):
                raise schainpy.admin.SchainError(
                    'There isn\'t any valid file in {}'.format(self.path))                    

            pathname, filename = os.path.split(fullpath)
            self.year = int(filename[1:5])
            self.doy = int(filename[5:8])
            self.set = int(filename[8:11]) - 1                
        else:
            log.log("Searching files in {}".format(self.path), self.name)
            self.filenameList = self.searchFilesOffLine(self.path, self.startDate, 
                self.endDate, self.expLabel, self.ext, self.walk, self.filefmt, self.folderfmt)
        
        self.setNextFile()

        return

    def readFirstHeader(self):
        '''Read metadata and data'''

        self.__readMetadata()        
        self.__readData()
        self.__setBlockList()
        
        if 'type' in self.meta:
            self.dataOut = eval(self.meta['type'])()
        
        for attr in self.meta:
            setattr(self.dataOut, attr, self.meta[attr])
        
        self.blockIndex = 0
        
        return

    def __setBlockList(self):
        '''
        Selects the data within the times defined

        self.fp
        self.startTime
        self.endTime
        self.blockList
        self.blocksPerFile

        '''

        startTime = self.startTime
        endTime = self.endTime

        thisUtcTime = self.data['utctime']
        self.interval = numpy.min(thisUtcTime[1:] - thisUtcTime[:-1])

        thisDatetime = datetime.datetime.utcfromtimestamp(thisUtcTime[0])

        thisDate = thisDatetime.date()
        thisTime = thisDatetime.time()

        startUtcTime = (datetime.datetime.combine(thisDate, startTime) - datetime.datetime(1970, 1, 1)).total_seconds()
        endUtcTime = (datetime.datetime.combine(thisDate, endTime) - datetime.datetime(1970, 1, 1)).total_seconds()

        ind = numpy.where(numpy.logical_and(thisUtcTime >= startUtcTime, thisUtcTime < endUtcTime))[0]

        self.blockList = ind
        self.blocksPerFile = len(ind)
        return

    def __readMetadata(self):
        '''
        Reads Metadata
        '''

        meta = {}

        if self.description:
            for key, value in self.description['Metadata'].items():
                meta[key] = self.fp[value].value
        else:
            grp = self.fp['Metadata']
            for name in grp:
                meta[name] = grp[name].value            

        if self.extras:
            for key, value in self.extras.items():
                meta[key] = value
        self.meta = meta

        return

    def __readData(self):

        data = {}
        
        if self.description:
            for key, value in self.description['Data'].items():
                if isinstance(value, str):
                    if isinstance(self.fp[value], h5py.Dataset):
                        data[key] = self.fp[value].value
                    elif isinstance(self.fp[value], h5py.Group):
                        array = []
                        for ch in self.fp[value]:
                            array.append(self.fp[value][ch].value)
                        data[key] = numpy.array(array)
                elif isinstance(value, list):
                    array = []
                    for ch in value:
                        array.append(self.fp[ch].value)
                    data[key] = numpy.array(array)
        else:
            grp = self.fp['Data']
            for name in grp:
                if isinstance(grp[name], h5py.Dataset):
                    array = grp[name].value
                elif isinstance(grp[name], h5py.Group):
                    array = []
                    for ch in grp[name]:
                        array.append(grp[name][ch].value)
                    array = numpy.array(array)
                else:
                    log.warning('Unknown type: {}'.format(name))
                
                if name in self.description:
                    key = self.description[name]
                else:
                    key = name
                data[key] = array

        self.data = data
        return
    
    def getData(self):

        for attr in self.data:
            if self.data[attr].ndim == 1:
                setattr(self.dataOut, attr, self.data[attr][self.blockIndex])
            else:
                setattr(self.dataOut, attr, self.data[attr][:, self.blockIndex])

        self.dataOut.flagNoData = False
        self.blockIndex += 1

        log.log("Block No. {}/{} -> {}".format(
            self.blockIndex,
            self.blocksPerFile,
            self.dataOut.datatime.ctime()), self.name)

        return

    def run(self, **kwargs):

        if not(self.isConfig):
            self.setup(**kwargs)
            self.isConfig = True

        if self.blockIndex == self.blocksPerFile:
            self.setNextFile()

        self.getData()

        return

@MPDecorator
class HDFWriter(Operation):
    """Operation to write HDF5 files.

    The HDF5 file contains by default two groups Data and Metadata where
    you can save any `dataOut` attribute specified by `dataList` and `metadataList`
    parameters, data attributes are normaly time dependent where the metadata
    are not. 
    It is possible to customize the structure of the HDF5 file with the 
    optional description parameter see the examples.

    Parameters:
    -----------
    path : str
        Path where files will be saved.
    blocksPerFile : int
        Number of blocks per file
    metadataList : list
        List of the dataOut attributes that will be saved as metadata
    dataList : int
        List of the dataOut attributes that will be saved as data
    setType : bool
        If True the name of the files corresponds to the timestamp of the data
    description : dict, optional
        Dictionary with the desired description of the HDF5 file
    
    Examples
    --------
    
    desc = {
        'data_output': {'winds': ['z', 'w', 'v']},
        'utctime': 'timestamps',
        'heightList': 'heights'
    }
    desc = {
        'data_output': ['z', 'w', 'v'],
        'utctime': 'timestamps',
        'heightList': 'heights'
    }
    desc = {
        'Data': {
            'data_output': 'winds',
            'utctime': 'timestamps'
        },
        'Metadata': {
            'heightList': 'heights'
        }
    }
    
    writer = proc_unit.addOperation(name='HDFWriter')
    writer.addParameter(name='path', value='/path/to/file')
    writer.addParameter(name='blocksPerFile', value='32')
    writer.addParameter(name='metadataList', value='heightList,timeZone')
    writer.addParameter(name='dataList',value='data_output,utctime')
    # writer.addParameter(name='description',value=json.dumps(desc))

    """

    ext = ".hdf5"
    optchar = "D"
    filename = None
    path = None
    setFile = None
    fp = None
    firsttime = True
    #Configurations
    blocksPerFile = None
    blockIndex = None
    dataOut = None
    #Data Arrays
    dataList = None
    metadataList = None
    currentDay = None
    lastTime = None

    def __init__(self):
        
        Operation.__init__(self)
        return

    def setup(self, path=None, blocksPerFile=10, metadataList=None, dataList=None, setType=None, description=None):
        self.path = path
        self.blocksPerFile = blocksPerFile
        self.metadataList = metadataList
        self.dataList = dataList
        self.setType = setType
        self.description = description

        for s in ['type', 'timeZone', 'useLocalTime']:
            if s not in self.metadataList:
                self.metadataList.append(s)

        tableList = []
        dsList = []

        for i in range(len(self.dataList)):
            dsDict = {}
            dataAux = getattr(self.dataOut, self.dataList[i])
            dsDict['variable'] = self.dataList[i]

            if dataAux is None:
                continue
            elif isinstance(dataAux, (int, float, numpy.integer, numpy.float)):
                dsDict['nDim'] = 0
            else:
                dsDict['nDim'] = len(dataAux.shape)
                dsDict['shape'] = dataAux.shape
                dsDict['dsNumber'] = dataAux.shape[0]
                dsDict['dtype'] = dataAux.dtype
            
            dsList.append(dsDict)

        self.dsList = dsList
        self.currentDay = self.dataOut.datatime.date()

    def timeFlag(self):
        currentTime = self.dataOut.utctime
        timeTuple = time.localtime(currentTime)
        dataDay = timeTuple.tm_yday

        if self.lastTime is None:
            self.lastTime = currentTime
            self.currentDay = dataDay
            return False
        
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

    def run(self, dataOut, path, blocksPerFile=10, metadataList=[],
            dataList=[], setType=None, description={}):

        self.dataOut = dataOut
        if not(self.isConfig):
            self.setup(path=path, blocksPerFile=blocksPerFile, 
                       metadataList=metadataList, dataList=dataList,
                       setType=setType, description=description)

            self.isConfig = True
            self.setNextFile()

        self.putData()
        return
        
    def setNextFile(self):
        
        ext = self.ext
        path = self.path
        setFile = self.setFile

        timeTuple = time.localtime(self.dataOut.utctime)
        subfolder = 'd%4.4d%3.3d' % (timeTuple.tm_year,timeTuple.tm_yday)
        fullpath = os.path.join(path, subfolder)

        if os.path.exists(fullpath):
            filesList = os.listdir(fullpath)
            filesList = [k for k in filesList if k.startswith(self.optchar)]
            if len( filesList ) > 0:
                filesList = sorted(filesList, key=str.lower)
                filen = filesList[-1]
                # el filename debera tener el siguiente formato
                # 0 1234 567 89A BCDE (hex)
                # x YYYY DDD SSS .ext
                if isNumber(filen[8:11]):
                    setFile = int(filen[8:11]) #inicializo mi contador de seteo al seteo del ultimo file
                else:
                    setFile = -1
            else:
                setFile = -1 #inicializo mi contador de seteo
        else:
            os.makedirs(fullpath)
            setFile = -1 #inicializo mi contador de seteo

        if self.setType is None:
            setFile += 1
            file = '%s%4.4d%3.3d%03d%s' % (self.optchar,
                                           timeTuple.tm_year,
                                           timeTuple.tm_yday,
                                           setFile,
                                           ext )
        else:
            setFile = timeTuple.tm_hour*60+timeTuple.tm_min
            file = '%s%4.4d%3.3d%04d%s' % (self.optchar,
                                           timeTuple.tm_year,
                                           timeTuple.tm_yday,
                                           setFile,
                                           ext )

        self.filename = os.path.join( path, subfolder, file )

        #Setting HDF5 File
        self.fp = h5py.File(self.filename, 'w')
        #write metadata
        self.writeMetadata(self.fp)
        #Write data
        self.writeData(self.fp)

    def getLabel(self, name, x=None):

        if x is None:
            if 'Data' in self.description:
                data = self.description['Data']
                if 'Metadata' in self.description:
                    data.update(self.description['Metadata'])
            else:
                data = self.description
            if name in data:
                if isinstance(data[name], str):
                    return data[name]
                elif isinstance(data[name], list):
                    return None
                elif isinstance(data[name], dict):
                    for key, value in data[name].items():
                        return key
            return name
        else:
            if 'Metadata' in self.description:
                meta = self.description['Metadata']
            else:
                meta = self.description
            if name in meta:
                if isinstance(meta[name], list):
                    return meta[name][x]
                elif isinstance(meta[name], dict):
                    for key, value in meta[name].items():
                        return value[x]
            return 'channel{:02d}'.format(x)
    
    def writeMetadata(self, fp):

        if self.description:
            if 'Metadata' in self.description:
                grp = fp.create_group('Metadata')
            else:
                grp = fp
        else:
            grp = fp.create_group('Metadata')

        for i in range(len(self.metadataList)):
            if not hasattr(self.dataOut, self.metadataList[i]):
                log.warning('Metadata: `{}` not found'.format(self.metadataList[i]), self.name)
                continue
            value = getattr(self.dataOut, self.metadataList[i])
            if isinstance(value, bool):
                if value is True:
                    value = 1
                else:
                    value = 0
            grp.create_dataset(self.getLabel(self.metadataList[i]), data=value)
        return

    def writeData(self, fp):
        
        if self.description:
            if 'Data' in self.description:
                grp = fp.create_group('Data')
            else:
                grp = fp
        else:
            grp = fp.create_group('Data')

        dtsets = []
        data = []
        
        for dsInfo in self.dsList:
            if dsInfo['nDim'] == 0:
                ds = grp.create_dataset(
                    self.getLabel(dsInfo['variable']), 
                    (self.blocksPerFile, ),
                    chunks=True, 
                    dtype=numpy.float64)
                dtsets.append(ds)
                data.append((dsInfo['variable'], -1))
            else:
                label = self.getLabel(dsInfo['variable'])
                if label is not None:
                    sgrp = grp.create_group(label)
                else:
                    sgrp = grp
                for i in range(dsInfo['dsNumber']):
                    ds = sgrp.create_dataset(
                        self.getLabel(dsInfo['variable'], i), 
                        (self.blocksPerFile, ) + dsInfo['shape'][1:],
                        chunks=True,
                        dtype=dsInfo['dtype'])
                    dtsets.append(ds)
                    data.append((dsInfo['variable'], i))
        fp.flush()

        log.log('Creating file: {}'.format(fp.filename), self.name)
        
        self.ds = dtsets
        self.data = data
        self.firsttime = True
        self.blockIndex = 0
        return

    def putData(self):

        if (self.blockIndex == self.blocksPerFile) or self.timeFlag():
            self.closeFile()
            self.setNextFile()

        for i, ds in enumerate(self.ds):
            attr, ch = self.data[i]
            if ch == -1:
                ds[self.blockIndex] = getattr(self.dataOut, attr)
            else:
                ds[self.blockIndex] = getattr(self.dataOut, attr)[ch]

        self.fp.flush()
        self.blockIndex += 1
        log.log('Block No. {}/{}'.format(self.blockIndex, self.blocksPerFile), self.name)

        return

    def closeFile(self):

        if self.blockIndex != self.blocksPerFile:
            for ds in self.ds:
                ds.resize(self.blockIndex, axis=0)

        self.fp.flush()
        self.fp.close()

    def close(self):

        self.closeFile()
