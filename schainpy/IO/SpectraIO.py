''' 
File: SpectraIO.py
Created on 20/02/2012

@author $Author$
@version $Id$
'''

import os, sys
import numpy
import glob
import fnmatch
import time, datetime

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from HeaderIO import *
from DataIO import DataReader
from DataIO import DataWriter

from Model.Spectra import Spectra

def isThisFileinRange(filename, startUTSeconds, endUTSeconds):
    """
    Esta funcion determina si un archivo de datos  en formato Jicamarca(.r) se encuentra
    o no dentro del rango de fecha especificado.
    
    Inputs:
        filename            :    nombre completo del archivo de datos en formato Jicamarca (.r)
        
        startUTSeconds      :    fecha inicial del rango seleccionado. La fecha esta dada en
                                 segundos contados desde 01/01/1970.
        endUTSeconds        :    fecha final del rango seleccionado. La fecha esta dada en
                                 segundos contados desde 01/01/1970.
    
    Return:
        Boolean    :    Retorna True si el archivo de datos contiene datos en el rango de
                        fecha especificado, de lo contrario retorna False.
    
    Excepciones:
        Si el archivo no existe o no puede ser abierto
        Si la cabecera no puede ser leida.
        
    """
    m_BasicHeader = BasicHeader()
    
    try:
        fp = open(filename,'rb')
    except:
        raise IOError, "The file %s can't be opened" %(filename)
    
    if not(m_BasicHeader.read(fp)):
        raise IOError, "The file %s has not a valid header" %(filename)
    
    fp.close()
    
    if not ((startUTSeconds <= m_BasicHeader.utc) and (endUTSeconds >= m_BasicHeader.utc)):
        return 0
    
    return 1


class SpectraReader(DataReader):
    """
    Esta clase permite leer datos de espectros desde archivos procesados (.pdata). La lectura
    de los datos siempre se realiza por bloques. Los datos leidos (array de 3 dimensiones: 
    perfiless*alturas*canales) son almacenados en la variable "buffer".
     
    Esta clase contiene instancias (objetos) de las clases BasicHeader, SystemHeader, 
    RadarControllerHeader y Spectra. Los tres primeros se usan para almacenar informacion de la
    cabecera de datos (metadata), y el cuarto (Spectra) para obtener y almacenar un bloque de
    datos desde el "buffer" cada vez que se ejecute el metodo "getData".
    
    Example:
    
        dpath = "/home/myuser/data"
        
        startTime = datetime.datetime(2010,1,20,0,0,0,0,0,0)
        
        endTime = datetime.datetime(2010,1,21,23,59,59,0,0,0)
        
        readerObj = SpectraReader()
        
        readerObj.setup(dpath, startTime, endTime)
        
        while(True):
            
            readerObj.getData()
            
            print readerObj.m_Spectra.data
            
            if readerObj.noMoreFiles:
                break
            
    """
    
    #speed of light
    __c = 3E8
    
    def __init__( self, m_Spectra = None ):
        """
        Inicializador de la clase SpectraReader para la lectura de datos de espectros.
        
        Input:
            m_Spectra    :    Objeto de la clase Spectra. Este objeto sera utilizado para
                              almacenar un perfil de datos cada vez que se haga un requerimiento
                              (getData). El perfil sera obtenido a partir del buffer de datos,
                              si el buffer esta vacio se hara un nuevo proceso de lectura de un
                              bloque de datos.
                              Si este parametro no es pasado se creara uno internamente.
        
        Variables afectadas:
            self.m_Spectra
            self.m_BasicHeader
            self.m_SystemHeader
            self.m_RadarControllerHeader
            self.m_ProcessingHeader
            
        
        Return:
            Void
        
        """
        if m_Spectra == None:
            m_Spectra = Spectra()
        
        if not( isinstance(m_Spectra, Spectra) ):
            raise ValueError, "in SpectraReader, m_Spectra must be an Spectra class object"
        
        self.m_Spectra = m_Spectra
        
        self.m_BasicHeader = BasicHeader()
        
        self.m_SystemHeader = SystemHeader()
        
        self.m_RadarControllerHeader = RadarControllerHeader()
        
        self.m_ProcessingHeader = ProcessingHeader()
    
        self.__fp = None
        
        self.__idFile = None
        
        self.__startDateTime = None
        
        self.__endDateTime = None
        
        self.__dataType = None
        
        self.__fileSizeByHeader = 0
        
        self.__pathList = []
        
        self.filenameList = []
        
        self.__lastUTTime = 0
        
        self.__maxTimeStep = 30
        
        self.__flagIsNewFile = 0
        
        self.flagResetProcessing = 0    
        
        self.flagIsNewBlock = 0
        
        self.noMoreFiles = 0
        
        self.nReadBlocks = 0
        
        self.online = 0
        
        self.firstHeaderSize = 0
        
        self.basicHeaderSize = 24
        
        self.filename = None
        
        self.fileSize = None
        
        self.__buffer_spc = None
        self.__buffer_cspc = None
        self.__buffer_dc  = None
        
        self.__buffer_id = 0
        
        self.__ippSeconds = 0
        
        self.nSelfChannels = 0
        
        self.nCrossPairs = 0
        
        self.nChannels = 0
        
        self.__path = None
        self.__startDateTime = None
        self.__endDateTime = None
        self.__expLabel = None
        self.__set = None
        self.__ext = None
        
    def __rdSystemHeader( self, fp=None ):
        if fp == None:
            fp = self.__fp
            
        self.m_SystemHeader.read( fp )
    
    def __rdRadarControllerHeader( self, fp=None ):
        if fp == None:
            fp = self.__fp
            
        self.m_RadarControllerHeader.read(fp)
        
    def __rdProcessingHeader( self,fp=None ):
        if fp == None:
            fp = self.__fp
            
        self.m_ProcessingHeader.read(fp)

    def __rdBasicHeader( self, fp=None ):
        if fp == None:
            fp = self.__fp
            
        self.m_BasicHeader.read(fp)
    
    def __readFirstHeader( self ):
        self.__rdBasicHeader()
        self.__rdSystemHeader()
        self.__rdRadarControllerHeader()
        self.__rdProcessingHeader()
        self.firstHeaderSize = self.m_BasicHeader.size
        
        data_type = int( numpy.log2((self.m_ProcessingHeader.processFlags & PROCFLAG.DATATYPE_MASK))-numpy.log2(PROCFLAG.DATATYPE_CHAR) )
        if data_type == 0:
            tmp = numpy.dtype([('real','<i1'),('imag','<i1')])
            
        elif data_type == 1:
            tmp = numpy.dtype([('real','<i2'),('imag','<i2')])
            
        elif data_type == 2:
            tmp = numpy.dtype([('real','<i4'),('imag','<i4')])
            
        elif data_type == 3:
            tmp = numpy.dtype([('real','<i8'),('imag','<i8')])
            
        elif data_type == 4:
            tmp = numpy.dtype([('real','<f4'),('imag','<f4')])
            
        elif data_type == 5:
            tmp = numpy.dtype([('real','<f8'),('imag','<f8')])
            
        else:
            raise ValueError, 'Data type was not defined'
        
        xi   = self.m_ProcessingHeader.firstHeight
        step = self.m_ProcessingHeader.deltaHeight
        xf   = xi + self.m_ProcessingHeader.numHeights*step
        
        self.__heights          = numpy.arange(xi, xf, step)
        self.__dataType         = tmp
        self.__fileSizeByHeader = self.m_ProcessingHeader.dataBlocksPerFile * self.m_ProcessingHeader.blockSize + self.firstHeaderSize + self.basicHeaderSize*(self.m_ProcessingHeader.dataBlocksPerFile - 1)
        self.__ippSeconds       = 2 * 1000 * self.m_RadarControllerHeader.ipp/self.__c
        
    def __setNextFileOnline(self, delay = 60 ):
        """
        
        
        return:
            bool
        
        """
        nFiles = 3
        nTries = 3
        
        countFiles = 0
        countTries = 0
        
        fileStatus = False
        
        while(True):
            countFiles += 1
            
            if countFiles > nFiles+1:
                break
            
            self.set += 1
                
            if countFiles > nFiles:
                self.doy += 1
                self.set = 0
            
            doypath = "D%04d%04d" %(self.year, self.doy)
            filename = "D%04d%04d%03d%s" %(self.year, self.doy, self.set, self.__ext)
            file = os.path.join(self.filepath, doypath, filename)
            fileSize = os.path.getsize(file)
            
            try:
                fp = open(file)
            except:
                raise IOError, "The file %s can't be opened" %file
            
            while(True):
                countTries += 1
                if countTries > nTries:
                    break
            
                currentSize = fileSize - fp.tell()
                neededSize = self.m_ProcessingHeader.blockSize + self.firstHeaderSize
                
                if (currentSize < neededSize):
                    #waiting for this block
                    time.sleep(delay)
                else:
                    fileStatus = True
                    break
            
            if fileStatus:
                break
            
            print "Skipping the file %s due to it hasn't enough data" %filename
            fp.close()
        
        return fileStatus

    def __setNextFileOffline( self ):
        idFile = self.__idFile

        while(True):
            idFile += 1
            
            if not( idFile < len(self.filenameList) ):
                self.noMoreFiles = 1
                return 0
            
            filename = self.filenameList[idFile]
            fileSize = os.path.getsize(filename)
            
            try:
                fp = open( filename, 'rb' )
            except:
                raise IOError, "The file %s can't be opened" %filename
            
            currentSize = fileSize - fp.tell()
            neededSize = self.m_ProcessingHeader.blockSize + self.firstHeaderSize
            
            if (currentSize < neededSize):
                print "Skipping the file %s due to it hasn't enough data" %filename
                fp.close()
                continue
            
            break
        
        self.__flagIsNewFile = 1
        self.__idFile = idFile
        self.filename = filename
        self.fileSize = fileSize
        self.__fp = fp
        
        print 'Setting the file: %s'%self.filename
        
        return 1

    def __setNextFile(self):
        
        if self.__fp != None:
            self.__fp.close()
        
        if self.online:
            newFile = self.__setNextFileOnline()
        else:
            newFile = self.__setNextFileOffline()
        
        if not(newFile):
            return 0
        
        self.__readFirstHeader()
        
        return 1
    
    def __setNewBlock( self ):
        if self.__fp == None:
            return 0
        
        if self.__flagIsNewFile:
            return 1
        
        currentSize = self.fileSize - self.__fp.tell()
        neededSize = self.m_ProcessingHeader.blockSize + self.basicHeaderSize
        
        #If there is enough data setting new data block
        if ( currentSize >= neededSize ):
            self.__rdBasicHeader()
            return 1
        
        #Setting new file 
        if not( self.__setNextFile() ):
            return 0
        
        deltaTime = self.m_BasicHeader.utc - self.__lastUTTime # check this
        
        self.flagResetProcessing = 0
        
        if deltaTime > self.__maxTimeStep:
            self.flagResetProcessing = 1
            self.ns = 0
            
        return 1
    


    def __readBlock(self):
        """
        __readBlock lee el bloque de datos desde la posicion actual del puntero del archivo
        (self.__fp) y actualiza todos los parametros relacionados al bloque de datos
        (metadata + data). La data leida es almacenada en el buffer y el contador del buffer
        es seteado a 0
        
        Inputs:
            None
            
        Return:
            None
        
        Variables afectadas:
        
            self.__buffer_id
            
            self.__buffer_sspc
            
            self.__flagIsNewFile
            
            self.flagIsNewBlock
            
            self.nReadBlocks
            
        """
        Npair_SelfSpectra = 0
        Npair_CrossSpectra = 0
        
        for i in range( 0,self.m_ProcessingHeader.totalSpectra*2,2 ):
            if self.m_ProcessingHeader.spectraComb[i] == self.m_ProcessingHeader.spectraComb[i+1]:
                Npair_SelfSpectra = Npair_SelfSpectra + 1 
            else:
                Npair_CrossSpectra = Npair_CrossSpectra + 1
                
#        self.__buffer_sspc = numpy.concatenate( (data_sspc,data_cspc,data_dcc), axis=0 )
        
        self.__buffer_id = 0
        self.__flagIsNewFile = 0
        self.flagIsNewBlock = 1

        pts2read = self.m_ProcessingHeader.profilesPerBlock*self.m_ProcessingHeader.numHeights
        
        spc  = numpy.fromfile(self.__fp, self.__dataType[0], int(pts2read*Npair_SelfSpectra))
        cspc  = numpy.fromfile(self.__fp, self.__dataType, int(pts2read*Npair_CrossSpectra))
        dc  = numpy.fromfile(self.__fp, self.__dataType, int(self.m_ProcessingHeader.numHeights*self.m_SystemHeader.numChannels) )
                
        spc = spc.reshape((Npair_SelfSpectra, self.m_ProcessingHeader.numHeights, self.m_ProcessingHeader.profilesPerBlock))
        cspc = cspc.reshape((Npair_CrossSpectra, self.m_ProcessingHeader.numHeights, self.m_ProcessingHeader.profilesPerBlock))
        dc = dc.reshape((self.m_SystemHeader.numChannels, self.m_ProcessingHeader.numHeights))
        
        if not(self.m_ProcessingHeader.shif_fft):
            spc = numpy.roll(spc, self.m_ProcessingHeader.profilesPerBlock/2, axis=2)
            cspc = numpy.roll(cspc, self.m_ProcessingHeader.profilesPerBlock/2, axis=2)
        
        spc = numpy.transpose(spc, (0,2,1))
        cspc = numpy.transpose(cspc, (0,2,1))
        #dc = numpy.transpose(dc, (0,2,1))
        
        data_spc = spc
        data_cspc = cspc['real'] + cspc['imag']*1j
        data_dc = dc['real'] + dc['imag']*1j
        
        self.__buffer_spc = data_spc
        self.__buffer_cspc = data_cspc
        self.__buffer_dc  = data_dc
        
        self.__flagIsNewFile = 0
        
        self.flagIsNewBlock = 1
        
        self.nReadBlocks += 1
        
 
    def __hasNotDataInBuffer(self):
        return 1

    def __searchFilesOnline(self, path, startDateTime, expLabel = "", ext = ".pdata"):
        """
        
        
        Return:
        
            filepath
            
            filename
            
            year
            
            doy
            
            set
        
        """
        
        pass
    
    def __searchFilesOffline(self, path, startDateTime, endDateTime, set=None, expLabel = "", ext = ".pdata"):
        """
        __searchFiles realiza una busqueda de los archivos que coincidan con los parametros
        especificados y se encuentren ubicados en el path indicado. Para realizar una busqueda
        correcta la estructura de directorios debe ser la siguiente:
        
        ...path/D[yyyy][ddd]/expLabel/D[yyyy][ddd][sss].ext
        
        [yyyy]: anio
        [ddd] : dia del anio
        [sss] : set del archivo        
        
        Inputs:
            path           :    Directorio de datos donde se realizara la busqueda. Todos los
                                ficheros que concidan con el criterio de busqueda seran
                                almacenados en una lista y luego retornados.
            startDateTime  :    Fecha inicial. Rechaza todos los archivos donde 
                                file end time < startDateTime (objeto datetime.datetime)
                                                         
            endDateTime    :    Fecha final. Rechaza todos los archivos donde 
                                file start time > endDateTime (obejto datetime.datetime)
            
            set            :    Set del primer archivo a leer. Por defecto None
            
            expLabel       :    Nombre del subdirectorio de datos.  Por defecto ""
            
            ext            :    Extension de los archivos a leer. Por defecto .r
            
        Return:
            
            (pathList, filenameList)
            
            pathList        :    Lista de directorios donde se encontraron archivos dentro 
                                 de los parametros especificados
            filenameList    :    Lista de archivos (ruta completa) que coincidieron con los
                                 parametros especificados.
        
        Variables afectadas:
        
            self.filenameList:    Lista de archivos (ruta completa) que la clase utiliza
                                  como fuente para leer los bloque de datos, si se termina
                                  de leer todos los bloques de datos de un determinado 
                                  archivo se pasa al siguiente archivo de la lista.
             
        Excepciones:
        
        """
        
        print "Searching files ..."
        
        dirList = []
        for thisPath in os.listdir(path):
            if os.path.isdir(os.path.join(path,thisPath)):
                dirList.append(thisPath)

        pathList = []
        
        thisDateTime = startDateTime
        
        while(thisDateTime <= endDateTime):
            year = thisDateTime.timetuple().tm_year
            doy = thisDateTime.timetuple().tm_yday
            
            match = fnmatch.filter(dirList, '?' + '%4.4d%3.3d' % (year,doy))
            if len(match) == 0:
                thisDateTime += datetime.timedelta(1)
                continue
            
            pathList.append(os.path.join(path,match[0],expLabel))
            thisDateTime += datetime.timedelta(1)
        
        startUtSeconds = time.mktime(startDateTime.timetuple())
        endUtSeconds = time.mktime(endDateTime.timetuple())
        
        filenameList = []
        for thisPath in pathList:
            fileList = glob.glob1(thisPath, "*%s" %ext)
            fileList.sort()
            for file in fileList:
                filename = os.path.join(thisPath,file)
                if isThisFileinRange(filename, startUtSeconds, endUtSeconds):
                    filenameList.append(filename)
                    
        self.filenameList = filenameList
        
        return pathList, filenameList

    
    def __searchFiles(self, path, startDateTime, endDateTime, set, expLabel, ext, online):
        
        if online:
            pathList, filenameList = self.__searchFilesOnline(path, startDateTime, endDateTime, set, expLabel, ext)
        else:
            pathList, filenameList = self.__searchFilesOffline(path, startDateTime, endDateTime, set, expLabel, ext)
        
        return 1
    
    def setup( self, path, startDateTime, endDateTime=None, set=None, expLabel = "", ext = ".pdata", online = 0 ):
        """
        setup configura los parametros de lectura de la clase SpectraReader.
        
        Si el modo de lectura es offline, primero se realiza una busqueda de todos los archivos
        que coincidan con los parametros especificados; esta lista de archivos son almacenados en
        self.filenameList.
        
        Input:
            path                :    Directorios donde se ubican los datos a leer. Dentro de este
                                     directorio deberia de estar subdirectorios de la forma:
                                     
                                     path/D[yyyy][ddd]/expLabel/P[yyyy][ddd][sss][ext]
            
            startDateTime       :    Fecha inicial. Rechaza todos los archivos donde
                                     file end time < startDatetime (objeto datetime.datetime)
            
            endDateTime         :    Fecha final. Si no es None, rechaza todos los archivos donde
                                     file end time < startDatetime (objeto datetime.datetime)
            
            set                 :    Set del primer archivo a leer. Por defecto None
            
            expLabel            :    Nombre del subdirectorio de datos.  Por defecto ""
            
            ext                 :    Extension de los archivos a leer. Por defecto .r
            
            online              :    
            
        Return:
        
        Affected:
        
        Excepciones:
        
        Example:       
        
        """
        if online == 0:
            pathList, filenameList = self.__searchFilesOffline(path, startDateTime, endDateTime, set, expLabel, ext)
            self.__idFile = -1

        else:
            filepath, filename, year, doy, set = self.__searchFilesOnline()
            set -= 1
            
        if not(self.__setNextFile()):
            print "No files in range: %s - %s" %(startDateTime.ctime(), endDateTime.ctime())
            return 0            
        
        self.startUTCSeconds = time.mktime(startDateTime.timetuple())
        self.endUTCSeconds = time.mktime(endDateTime.timetuple())
        
        self.startYear = startDateTime.timetuple().tm_year 
        self.endYear = endDateTime.timetuple().tm_year
        
        self.startDoy = startDateTime.timetuple().tm_yday
        self.endDoy = endDateTime.timetuple().tm_yday
        #call fillHeaderValues() - to Data Object
            
        self.__pathList = pathList
        self.filenameList = filenameList 
        self.online = online
        
        self.__startDateTime = startDateTime
        
        return 1
        
    def readNextBlock(self):
        """
        readNextBlock establece un nuevo bloque de datos a leer y los lee, si es que no existiese
        mas bloques disponibles en el archivo actual salta al siguiente.
        
        """

        if not( self.__setNewBlock() ):
            return 0
             
        self.__readBlock()
        
        self.__lastUTTime = self.m_BasicHeader.utc
        
        return 1

   
    def getData(self):
        """
        getData copia el buffer de lectura a la clase "Spectra",
        con todos los parametros asociados a este (metadata). cuando no hay datos en el buffer de
        lectura es necesario hacer una nueva lectura de los bloques de datos usando "readNextBlock"
        
        Inputs:
            None
            
        Return:
            data    :    retorna un bloque de datos (nFFTs * alturas * canales) copiados desde el
                         buffer. Si no hay mas archivos a leer retorna None.
            
        Variables afectadas:
            self.m_Spectra
            self.__buffer_id
            
        Excepciones:
        
        """

        self.flagResetProcessing = 0
        self.flagIsNewBlock = 0
        
        if self.__hasNotDataInBuffer():            
            self.readNextBlock() 
            
            self.m_Spectra.m_BasicHeader = self.m_BasicHeader.copy()
            self.m_Spectra.m_ProcessingHeader = self.m_ProcessingHeader.copy()
            self.m_Spectra.m_RadarControllerHeader = self.m_RadarControllerHeader.copy()
            self.m_Spectra.m_SystemHeader = self.m_SystemHeader.copy()
            self.m_Spectra.heights = self.__heights
            self.m_Spectra.dataType = self.__dataType
        
        if self.noMoreFiles == 1:
            print 'Process finished'
            return 0
        
        #data es un numpy array de 3 dmensiones (perfiles, alturas y canales)
        #print type(self.__buffer_sspc)
                
        time = self.m_BasicHeader.utc + self.__buffer_id*self.__ippSeconds
        
        self.m_Spectra.m_BasicHeader.utc = time
        self.m_Spectra.data_spc = self.__buffer_spc
        self.m_Spectra.data_cspc = self.__buffer_cspc
        self.m_Spectra.data_dc = self.__buffer_dc
        
        #call setData - to Data Object
    
        return 1


class SpectraWriter(DataWriter):
    
    def __init__(self):
        if m_Spectra == None:
            m_Spectra = Spectra()    
                                                                                                                    
        self.m_Spectra = m_Spectra
        
        self.__fp = None
    
        self.__blocksCounter = 0
        
        self.__setFile = None
        
        self.__flagIsNewFile = 0
        
        self.__buffer_sspc = 0
        
        self.__buffer_id = 0
        
        self.__dataType = None
        
        self.__ext = None
        
        self.nWriteBlocks = 0 
        
        self.flagIsNewBlock = 0
        
        self.noMoreFiles = 0
        
        self.filename = None
        
        self.m_BasicHeader= BasicHeader()
    
        self.m_SystemHeader = SystemHeader()
    
        self.m_RadarControllerHeader = RadarControllerHeader()
    
        self.m_ProcessingHeader = ProcessingHeader()
    
    def __setNextFile(self):
        setFile = self.__setFile
        ext = self.__ext
        path = self.__path
        
        setFile += 1
         
        if not(self.__blocksCounter >= self.m_ProcessingHeader.dataBlocksPerFile):
            self.__fp.close()
            return 0
        
        timeTuple = time.localtime(self.m_Spectra.m_BasicHeader.utc) # utc from m_Spectra
        file = 'D%4.4d%3.3d%3.3d%s' % (timeTuple.tm_year,timeTuple.tm_doy,setFile,ext)
        subfolder = 'D%4.4d%3.3d' % (timeTuple.tm_year,timeTuple.tm_doy) 
        tmp = os.path.join(path,subfolder)
        if not(os.path.exists(tmp)):
            os.mkdir(tmp)
   
        filename = os.path.join(path,subfolder,file)
        fp = open(filename,'wb')
        
        #guardando atributos 
        self.filename = filename
        self.__subfolder = subfolder
        self.__fp = fp
        self.__setFile = setFile
        self.__flagIsNewFile = 1
        
        print 'Writing the file: %s'%self.filename
        
        return 1
            

    
    def __setNewBlock(self):
        if self.__fp == None:
            return 0
        
        if self.__flagIsNewFile:
            return 1
        
        #Bloques completados?
        if self.__blocksCounter < self.m_ProcessingHeader.profilesPerBlock:
            self.__writeBasicHeader()
            return 1
        
        if not(self.__setNextFile()):
            return 0
        
        self.__writeFirstHeader()
        
        return 1
    
    def __writeBlock(self):
        
        numpy.save(self.__fp,self.__buffer_sspc)
        
        self.__buffer_sspc = numpy.array([],self.__dataType)
        
        self.__buffer_id = 0 
        
        self.__flagIsNewFile = 0
        
        self.flagIsNewBlock = 1
        
        self.nWriteBlocks += 1
        
        self.__blocksCounter += 1
    
    def writeNextBlock(self):
        if not(self.__setNewBlock()):
            return 0
        
        self.__writeBlock()
        
        return 1
    
    def __hasAllDataInBuffer(self):
        if self.__buffer_id >= self.m_ProcessingHeader.profilesPerBlock:
            return 1
        
        return 0
    
    def putData(self):
        self.flagIsNewBlock = 0
        
        if self.m_Spectra.noData:
            return None
        
        shape = self.m_Spectra.data.shape
        data = numpy.zeros(shape,self.__dataType)
        data['real'] = self.m_Spectra.data.real
        data['imag'] = self.m_Spectra.data.imag
        data = data.reshape((-1))
        
        self.__buffer_sspc = numpy.hstack((self.__buffer_sspc,data))
        
        self.__buffer_id += 1
        
        if __hasAllDataInBuffer():
            self.writeNextBlock()
        
        
        if self.noMoreFiles:
            print 'Process finished'
            return None
        
        return 1
    

    def setup(self,path,set=None,format=None):
        
        if set == None:
            set = -1
        else:
            set -= 1
        
        if format == 'hdf5':
            ext = '.hdf5'
            print 'call hdf5 library'
            return 0
        
        if format == 'rawdata':
            ext = '.r'
        
        #call to config_headers
        
        self.__setFile = set
        
        if not(self.__setNextFile()):
            print "zzzzzzzzzzzz"
            return 0
        
        self.__writeFirstHeader() # dentro de esta funcion se debe setear e __dataType
        
        self.__buffer_sspc = numpy.array([],self.__dataType)
        
    
    
    def __writeBasicHeader(self):
        pass
    
    def __writeFirstHeader(self):
        pass
