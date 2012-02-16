'''
Created on 23/01/2012

@author $Author$
@version $Id$
'''

from Header import *
from DataIO import DataReader
from DataIO import DataWriter


class SpectraReader(DataReader):
    """
    Esta clase permite leer datos de espectros desde archivos procesados (.pdata). La lectura
    de los datos siempre se realiza por bloques. Los datos leidos (array de 3 dimensiones: 
    nFFTs*alturas*canales) son almacenados en la variable "buffer".
     
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
    
    def __init__(self, m_Spectra = None):
        """
        Inicializador de la clase SpectraReader para la lectura de datos de espectros.
        
        Input:
            m_Spectra    :    Objeto de la clase Voltage. Este objeto sera utilizado para
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
            m_Spectra = Voltage()
        
        if not(isinstance(m_Spectra, Voltage)):
            raise ValueError, "in VoltageReader, m_Spectra must be an Voltage class object"
        
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
        
        self.__ippSeconds = 0
        
        self.flagResetProcessing = 0    
        
        self.flagIsNewBlock = 0
        
        self.noMoreFiles = 0
        
        self.nReadBlocks = 0
        
        self.online = 0
        
        self.filename = None
        
        self.fileSize = None
        
        self.firstHeaderSize = 0
        
        self.basicHeaderSize = 24
        
        self.idProfile = 0
        
        self.__buffer = 0
        
        self.__buffer_id = 9999
    
    def __rdSystemHeader(self,fp=None):
        if fp == None:
            fp = self.__fp
            
        self.m_SystemHeader.read(fp)
    
    def __rdRadarControllerHeader(self,fp=None):
        if fp == None:
            fp = self.__fp
            
        self.m_RadarControllerHeader.read(fp)
        
    def __rdProcessingHeader(self,fp=None):
        if fp == None:
            fp = self.__fp
            
        self.m_ProcessingHeader.read(fp)

    def __rdBasicHeader(self, fp=None):
        
        if fp == None:
            fp = self.__fp
            
        self.m_BasicHeader.read(fp)
    
    def __readFirstHeader(self):
        
        self.__rdBasicHeader()
        self.__rdSystemHeader()
        self.__rdRadarControllerHeader()
        self.__rdProcessingHeader()
        self.firstHeaderSize = self.m_BasicHeader.size
        
    def __setNextFileOnline(self):
        return 1

    def __setNextFileOffline(self):
        
        return 1

    def __setNextFile(self):
        
        
        
        return 1
    
    def __setNewBlock(self):
        
            
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
            
            self.__buffer
            
            self.__flagIsNewFile
            
            self.idProfile
            
            self.flagIsNewBlock
            
            self.nReadBlocks
            
        """
    
 
    def __hasNotDataInBuffer(self):

        
        return 0

    def __searchFiles(self, path, startDateTime, endDateTime, set=None, expLabel = "", ext = ".pdata"):
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
                                file end time < startDateTime (obejto datetime.datetime)
                                                         
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
        

    
    def setup(self, path, startDateTime, endDateTime=None, set=None, expLabel = "", ext = ".pdata", online = 0):
        """
        setup configura los parametros de lectura de la clase VoltageReader.
        
        Si el modo de lectura es offline, primero se realiza una busqueda de todos los archivos
        que coincidan con los parametros especificados; esta lista de archivos son almacenados en
        self.filenameList.
        
        Input:
            path                :    Directorios donde se ubican los datos a leer. Dentro de este
                                     directorio deberia de estar subdirectorios de la forma:
                                     
                                     path/D[yyyy][ddd]/expLabel/P[yyyy][ddd][sss][ext]
            
            startDateTime       :    Fecha inicial. Rechaza todos los archivos donde
                                     file end time < startDatetime (obejto datetime.datetime)
            
            endDateTime         :    Fecha final. Si no es None, rechaza todos los archivos donde
                                     file end time < startDatetime (obejto datetime.datetime)
            
            set                 :    Set del primer archivo a leer. Por defecto None
            
            expLabel            :    Nombre del subdirectorio de datos.  Por defecto ""
            
            ext                 :    Extension de los archivos a leer. Por defecto .r
            
            online              :    
            
        Return:
        
        Affected:
        
        Excepciones:
        
        Example:       
        
        """

        
    def readNextBlock(self):
        """
        readNextBlock establece un nuevo bloque de datos a leer y los lee, si es que no existiese
        mas bloques disponibles en el archivo actual salta al siguiente.
        
        """

        
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
            self.idProfile
            
        Excepciones:
        
        """

    
        return data

class SpectraWriter(DataWriter):
    def __init__(self):
        pass

