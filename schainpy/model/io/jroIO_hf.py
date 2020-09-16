'''
Created on Jul 3, 2014

@author: roj-com0419
'''

import os,sys
import time,datetime
import h5py
import numpy
import fnmatch
import re

from schainpy.model.data.jroheaderIO import RadarControllerHeader, SystemHeader
from schainpy.model.data.jrodata import Voltage
from schainpy.model.proc.jroproc_base import ProcessingUnit, Operation


def isNumber(str):
    """
    Chequea si el conjunto de caracteres que componen un string puede ser convertidos a un numero.

    Excepciones:
        Si un determinado string no puede ser convertido a numero
    Input:
        str, string al cual se le analiza para determinar si convertible a un numero o no

    Return:
        True    :    si el string es uno numerico
        False   :    no es un string numerico
    """
    try:
        float( str )
        return True
    except:
        return False

def getFileFromSet(path, ext, set=None):
    validFilelist = []
    fileList = os.listdir(path)


    if len(fileList) < 1:
        return None

    # 0 1234 567 89A BCDE
    # H YYYY DDD SSS .ext

    for thisFile in fileList:
        try:
            number= int(thisFile[6:16])

     #       year = int(thisFile[1:5])
     #       doy  = int(thisFile[5:8])
        except:
            continue

        if (os.path.splitext(thisFile)[-1].lower() != ext.lower()):
            continue

        validFilelist.append(thisFile)

    if len(validFilelist) < 1:
        return None

    validFilelist = sorted( validFilelist, key=str.lower )

    if set == None:
        return validFilelist[-1]

    print("set =" ,set)
    for thisFile in validFilelist:
        if set <= int(thisFile[6:16]):
            print(thisFile,int(thisFile[6:16]))
            return thisFile

    return validFilelist[-1]

    myfile = fnmatch.filter(validFilelist,'*%10d*'%(set))
    #myfile = fnmatch.filter(validFilelist,'*%4.4d%3.3d%3.3d*'%(year,doy,set))

    if len(myfile)!= 0:
        return myfile[0]
    else:
        filename = '*%10.10d%s'%(set,ext.lower())
        print('the filename %s does not exist'%filename)
        print('...going to the last file: ')

    if validFilelist:
        validFilelist = sorted( validFilelist, key=str.lower )
        return validFilelist[-1]

    return None

def getlastFileFromPath(path, ext):
    """
Depura el fileList dejando solo los que cumplan el formato de "res-xxxxxx.ext"
    al final de la depuracion devuelve el ultimo file de la lista que quedo.

    Input:
        fileList    :    lista conteniendo todos los files (sin path) que componen una determinada carpeta
        ext         :    extension de los files contenidos en una carpeta

    Return:
        El ultimo file de una determinada carpeta, no se considera el path.
    """
    validFilelist = []
    fileList = os.listdir(path)

    # 0 1234 567 89A BCDE
    # H YYYY DDD SSS .ext

    for thisFile in fileList:

        try:
            number= int(thisFile[6:16])
        except:
            print("There is a file or folder with different format")
        if not isNumber(number):
            continue

#        year = thisFile[1:5]
#        if not isNumber(year):
#            continue

#       doy = thisFile[5:8]
#        if not isNumber(doy):
#            continue

        number= int(number)
#        year = int(year)
#        doy = int(doy)

        if (os.path.splitext(thisFile)[-1].lower() != ext.lower()):
            continue


        validFilelist.append(thisFile)


    if validFilelist:
        validFilelist = sorted( validFilelist, key=str.lower )
        return validFilelist[-1]

    return None



class HFReader(ProcessingUnit):
    '''
    classdocs
    '''
    path     = None
    startDate= None
    endDate  = None
    startTime= None
    endTime  = None
    walk     = None
    isConfig = False
    dataOut=None
    nTries = 3
    ext      = ".hdf5"

    def __init__(self, **kwargs):
        '''
        Constructor
        '''
        ProcessingUnit.__init__(self, **kwargs)

        self.isConfig =False

        self.datablock = None

        self.filename_current=None

        self.utc = 0

        self.ext='.hdf5'

        self.flagIsNewFile = 1

        #-------------------------------------------------
        self.fileIndex=None

        self.profileIndex_offset=None

        self.filenameList=[]

        self.hfFilePointer= None

        self.filename_online = None

        self.status=True

        self.flagNoMoreFiles= False

        self.__waitForNewFile = 20


        #--------------------------------------------------

        self.dataOut = self.createObjByDefault()


    def createObjByDefault(self):

        dataObj = Voltage()

        return dataObj

    def setObjProperties(self):

        pass

    def getBlockDimension(self):
        """
        Obtiene la cantidad de puntos a leer por cada bloque de datos

        Affected:
            self.blocksize

        Return:
            None
        """
        pts2read =self.nChannels*self.nHeights*self.nProfiles
        self.blocksize = pts2read

    def __readHeader(self):

        self.nProfiles = 100
        self.nHeights = 1000
        self.nChannels = 2
        self.__firstHeigth=0
        self.__nSamples=1000
        self.__deltaHeigth=1.5
        self.__sample_rate=1e5
        #self.__frequency=2.72e6
        #self.__frequency=3.64e6
        self.__frequency=None
        self.__online = False
        self.filename_next_set=None

        #print "Frequency of Operation:", self.__frequency


    def __setParameters(self,path='', startDate='',endDate='',startTime='', endTime='', walk=''):
        self.path = path
        self.startDate = startDate
        self.endDate = endDate
        self.startTime = startTime
        self.endTime = endTime
        self.walk = walk

    def __checkPath(self):
        if os.path.exists(self.path):
            self.status=1
        else:
            self.status=0
            print('Path %s does not exits'%self.path)
            return
        return

    def __selDates(self, hf_dirname_format):
        try:
            dir_hf_filename= self.path+"/"+hf_dirname_format
            fp= h5py.File(dir_hf_filename,'r')
            hipoc=fp['t'].value
            fp.close()
            date_time=datetime.datetime.utcfromtimestamp(hipoc)
            year =int(date_time[0:4])
            month=int(date_time[5:7])
            dom  =int(date_time[8:10])
            thisDate= datetime.date(year,month,dom)
            if (thisDate>=self.startDate and thisDate <= self.endDate):
                return hf_dirname_format
        except:
            return None

    def __findDataForDates(self,online=False):
        if not(self.status):
            return None

        pat = '\d+.\d+'
        dirnameList = [re.search(pat,x) for x in os.listdir(self.path)]
        dirnameList = [x for x in dirnameList if x!=None]
        dirnameList = [x.string for x in dirnameList]
        if not(online):

            dirnameList = [self.__selDates(x) for x in dirnameList]
            dirnameList = [x for x in dirnameList if x!=None]

        if len(dirnameList)>0:
                self.status = 1
                self.dirnameList = dirnameList
                self.dirnameList.sort()

        else:
            self.status = 0
            return None

    def __getTimeFromData(self):
        startDateTime_Reader = datetime.datetime.combine(self.startDate,self.startTime)
        endDateTime_Reader = datetime.datetime.combine(self.endDate,self.endTime)
        print('Filtering Files from %s to %s'%(startDateTime_Reader, endDateTime_Reader))
        print('........................................')
        filter_filenameList=[]
        self.filenameList.sort()
        for i in range(len(self.filenameList)-1):
            filename=self.filenameList[i]
            dir_hf_filename= filename
            fp= h5py.File(dir_hf_filename,'r')
            hipoc=fp['t'].value
            hipoc=hipoc+self.timezone
            date_time=datetime.datetime.utcfromtimestamp(hipoc)
            fp.close()
            year =int(date_time[0:4])
            month=int(date_time[5:7])
            dom  =int(date_time[8:10])
            hour =int(date_time[11:13])
            min  =int(date_time[14:16])
            sec  =int(date_time[17:19])
            this_time=datetime.datetime(year,month,dom,hour,min,sec)
            if (this_time>=startDateTime_Reader and this_time <= endDateTime_Reader):
                filter_filenameList.append(filename)
        filter_filenameList.sort()
        self.filenameList = filter_filenameList
        return 1

    def __getFilenameList(self):
        #print "hola"
        #print self.dirnameList
        dirList = [os.path.join(self.path,x) for x in self.dirnameList]
        self.filenameList= dirList
        #print self.filenameList
        #print "pase",len(self.filenameList)

    def __selectDataForTimes(self, online=False):

        if not(self.status):
            return None
        #----------------
        self.__getFilenameList()
        #----------------
        if not(online):
            if not(self.all):
                self.__getTimeFromData()
            if len(self.filenameList)>0:
                self.status=1
                self.filenameList.sort()
            else:
                self.status=0
                return None
        else:
            if self.set != None:

                filename=getFileFromSet(self.path,self.ext,self.set)

                if self.flag_nextfile==True:
                    self.dirnameList=[filename]
                    fullfilename=self.path+"/"+filename
                    self.filenameList=[fullfilename]
                    self.filename_next_set=int(filename[6:16])+10

                    self.flag_nextfile=False
                else:
                    print(filename)
                    print("PRIMERA CONDICION")
                    #if self.filename_next_set== int(filename[6:16]):
                    print("TODO BIEN")

                    if filename == None:
                        raise ValueError("corregir")

                    self.dirnameList=[filename]
                    fullfilename=self.path+"/"+filename
                    self.filenameList=[fullfilename]
                    self.filename_next_set=int(filename[6:16])+10
                    print("Setting next file",self.filename_next_set)
                    self.set=int(filename[6:16])
                    if True:
                        pass
                    else:
                        print("ESTOY AQUI PORQUE NO EXISTE EL SIGUIENTE ARCHIVO")

            else:
                filename =getlastFileFromPath(self.path,self.ext)

                if self.flag_nextfile==True:
                    self.dirnameList=[filename]
                    fullfilename=self.path+"/"+filename
                    self.filenameList=[self.filenameList[-1]]
                    self.filename_next_set=int(filename[6:16])+10

                    self.flag_nextfile=False
                else:
                   filename=getFileFromSet(self.path,self.ext,self.set)
                   print(filename)
                   print("PRIMERA CONDICION")
                    #if self.filename_next_set== int(filename[6:16]):
                   print("TODO BIEN")

                   if filename == None:
                       raise ValueError("corregir")

                   self.dirnameList=[filename]
                   fullfilename=self.path+"/"+filename
                   self.filenameList=[fullfilename]
                   self.filename_next_set=int(filename[6:16])+10
                   print("Setting next file",self.filename_next_set)
                   self.set=int(filename[6:16])
                   if True:
                       pass
                   else:
                       print("ESTOY AQUI PORQUE NO EXISTE EL SIGUIENTE ARCHIVO")



    def searchFilesOffLine(self,
                            path,
                            startDate,
                            endDate,
                            ext,
                            startTime=datetime.time(0,0,0),
                            endTime=datetime.time(23,59,59),
                            walk=True):

        self.__setParameters(path, startDate, endDate, startTime, endTime, walk)

        self.__checkPath()

        self.__findDataForDates()
        #print self.dirnameList

        self.__selectDataForTimes()

        for i in range(len(self.filenameList)):
            print("%s"% (self.filenameList[i]))

        return

    def searchFilesOnLine(self,
                            path,
                            expLabel= "",
                            ext=None,
                            startDate=None,
                            endDate=None,
                            walk=True,
                            set=None):


        startDate = datetime.datetime.utcnow().date()
        endDate = datetime.datetime.utcnow().date()

        self.__setParameters(path=path,startDate=startDate,endDate=endDate,walk=walk)

        self.__checkPath()

        fullpath=path
        print("%s folder was found: " %(fullpath ))

        if set == None:
            self.set=None
            filename =getlastFileFromPath(fullpath,ext)
            startDate= datetime.datetime.utcnow().date
            endDate= datetime.datetime.utcnow().date()
#
        else:
            filename= getFileFromSet(fullpath,ext,set)
            startDate=None
            endDate=None
#
        if not (filename):
            return None,None,None,None,None
        #print "%s file was found" %(filename)

#
#         dir_hf_filename= self.path+"/"+filename
#         fp= h5py.File(dir_hf_filename,'r')
#         hipoc=fp['t'].value
#         fp.close()
#         date_time=datetime.datetime.utcfromtimestamp(hipoc)
#
#         year =int(date_time[0:4])
#         month=int(date_time[5:7])
#         dom  =int(date_time[8:10])
#         set= int(filename[4:10])
#         self.set=set-1
        #self.dirnameList=[filename]
        filenameList= fullpath+"/"+filename
        self.dirnameList=[filename]
        self.filenameList=[filenameList]
        self.flag_nextfile=True

        #self.__findDataForDates(online=True)
        #self.dirnameList=[self.dirnameList[-1]]
        #print self.dirnameList
        #self.__selectDataForTimes(online=True)
        #return fullpath,filename,year,month,dom,set
        return

    def __setNextFile(self,online=False):
        """
        """
        if not(online):
            newFile = self.__setNextFileOffline()
        else:
            newFile = self.__setNextFileOnline()

        if not(newFile):
            return 0
        return 1

    def __setNextFileOffline(self):
        """
        """
        idFile= self.fileIndex
        while(True):
            idFile += 1
            if not (idFile < len(self.filenameList)):
                self.flagNoMoreFiles = 1
                print("No more Files")
                return 0
            filename = self.filenameList[idFile]
            hfFilePointer =h5py.File(filename,'r')

            epoc=hfFilePointer['t'].value
            #this_time=datetime.datetime(year,month,dom,hour,min,sec)
            break

        self.flagIsNewFile = 1
        self.fileIndex = idFile
        self.filename = filename

        self.hfFilePointer = hfFilePointer
        hfFilePointer.close()
        self.__t0=epoc
        print("Setting the file: %s"%self.filename)

        return 1

    def __setNextFileOnline(self):
        """
        """
        print("SOY NONE",self.set)
        if self.set==None:
            pass
        else:
            self.set +=10

        filename = self.filenameList[0]#fullfilename
        if self.filename_online != None:
            self.__selectDataForTimes(online=True)
            filename = self.filenameList[0]
            while self.filename_online == filename:
                print('waiting %d seconds to get a new file...'%(self.__waitForNewFile))
                time.sleep(self.__waitForNewFile)
                #self.__findDataForDates(online=True)
                self.set=self.filename_next_set
                self.__selectDataForTimes(online=True)
                filename = self.filenameList[0]
                sizeoffile=os.path.getsize(filename)

        #print filename
        sizeoffile=os.path.getsize(filename)
        if sizeoffile<1670240:
            print("%s is not the rigth  size"%filename)
            delay=50
            print('waiting %d seconds for delay...'%(delay))
            time.sleep(delay)
        sizeoffile=os.path.getsize(filename)
        if sizeoffile<1670240:
            delay=50
            print('waiting %d  more seconds for delay...'%(delay))
            time.sleep(delay)

        sizeoffile=os.path.getsize(filename)
        if sizeoffile<1670240:
            delay=50
            print('waiting %d  more seconds for delay...'%(delay))
            time.sleep(delay)

        try:
            hfFilePointer=h5py.File(filename,'r')

        except:
            print("Error reading file %s"%filename)

        self.filename_online=filename
        epoc=hfFilePointer['t'].value

        self.hfFilePointer=hfFilePointer
        hfFilePointer.close()
        self.__t0=epoc


        self.flagIsNewFile = 1
        self.filename = filename

        print("Setting the file: %s"%self.filename)
        return 1

    def __getExpParameters(self):
        if not(self.status):
            return None

    def setup(self,
               path = None,
               startDate = None,
               endDate = None,
               startTime = datetime.time(0,0,0),
               endTime = datetime.time(23,59,59),
               set = None,
               expLabel = "",
               ext = None,
               all=0,
               timezone=0,
               online = False,
               delay = 60,
               walk = True):
        '''
        In this method we should set all initial parameters.

        '''
        if path==None:
            raise ValueError("The path is not valid")

        if ext==None:
            ext = self.ext

        self.timezone= timezone
        self.online= online
        self.all=all
        #if set==None:

        #print set
        if not(online):
            print("Searching files in offline mode...")

            self.searchFilesOffLine(path, startDate, endDate, ext, startTime, endTime, walk)
        else:
            print("Searching files in online mode...")
            self.searchFilesOnLine(path, walk,ext,set=set)
            if set==None:
                pass
            else:
                self.set=set-10

#             for nTries in range(self.nTries):
#
#                 fullpath,file,year,month,day,set = self.searchFilesOnLine(path=path,expLabel=expLabel,ext=ext, walk=walk,set=set)
#
#                 if fullpath:
#                     break
#                 print '\tWaiting %0.2f sec for an valid file in %s: try %02d ...' % (self.delay, path, nTries+1)
#                 time.sleep(self.delay)
#             if not(fullpath):
#                 print "There ins't valid files in %s" % path
#                 return None


        if not(self.filenameList):
            print("There  is no files into the folder: %s"%(path))
            sys.exit(-1)

        self.__getExpParameters()


        self.fileIndex = -1

        self.__setNextFile(online)

        self.__readMetadata()

        self.__setLocalVariables()

        self.__setHeaderDO()
        #self.profileIndex_offset= 0

        #self.profileIndex = self.profileIndex_offset

        self.isConfig = True

    def __readMetadata(self):
        self.__readHeader()


    def __setLocalVariables(self):

        self.datablock = numpy.zeros((self.nChannels, self.nHeights,self.nProfiles), dtype = numpy.complex)
        #



        self.profileIndex = 9999


    def __setHeaderDO(self):


        self.dataOut.radarControllerHeaderObj = RadarControllerHeader()

        self.dataOut.systemHeaderObj = SystemHeader()


        #---------------------------------------------------------
        self.dataOut.systemHeaderObj.nProfiles=100
        self.dataOut.systemHeaderObj.nSamples=1000


        SAMPLING_STRUCTURE=[('h0', '<f4'), ('dh', '<f4'), ('nsa', '<u4')]
        self.dataOut.radarControllerHeaderObj.samplingWindow=numpy.zeros((1,),SAMPLING_STRUCTURE)
        self.dataOut.radarControllerHeaderObj.samplingWindow['h0']=0
        self.dataOut.radarControllerHeaderObj.samplingWindow['dh']=1.5
        self.dataOut.radarControllerHeaderObj.samplingWindow['nsa']=1000
        self.dataOut.radarControllerHeaderObj.nHeights=int(self.dataOut.radarControllerHeaderObj.samplingWindow['nsa'])
        self.dataOut.radarControllerHeaderObj.firstHeight = self.dataOut.radarControllerHeaderObj.samplingWindow['h0']
        self.dataOut.radarControllerHeaderObj.deltaHeight = self.dataOut.radarControllerHeaderObj.samplingWindow['dh']
        self.dataOut.radarControllerHeaderObj.samplesWin = self.dataOut.radarControllerHeaderObj.samplingWindow['nsa']

        self.dataOut.radarControllerHeaderObj.nWindows=1
        self.dataOut.radarControllerHeaderObj.codetype=0
        self.dataOut.radarControllerHeaderObj.numTaus=0
        #self.dataOut.radarControllerHeaderObj.Taus = numpy.zeros((1,),'<f4')


        #self.dataOut.radarControllerHeaderObj.nCode=numpy.zeros((1,), '<u4')
        #self.dataOut.radarControllerHeaderObj.nBaud=numpy.zeros((1,), '<u4')
        #self.dataOut.radarControllerHeaderObj.code=numpy.zeros(0)

        self.dataOut.radarControllerHeaderObj.code_size=0
        self.dataOut.nBaud=0
        self.dataOut.nCode=0
        self.dataOut.nPairs=0


        #---------------------------------------------------------

        self.dataOut.type = "Voltage"

        self.dataOut.data = None

        self.dataOut.dtype = numpy.dtype([('real','<f4'),('imag','<f4')])

        self.dataOut.nProfiles = 1

        self.dataOut.heightList = self.__firstHeigth + numpy.arange(self.__nSamples, dtype = numpy.float)*self.__deltaHeigth

        self.dataOut.channelList = list(range(self.nChannels))

        #self.dataOut.channelIndexList = None

        self.dataOut.flagNoData = True

        #Set to TRUE if the data is discontinuous
        self.dataOut.flagDiscontinuousBlock = False

        self.dataOut.utctime = None

        self.dataOut.timeZone = self.timezone

        self.dataOut.dstFlag = 0

        self.dataOut.errorCount = 0

        self.dataOut.nCohInt = 1

        self.dataOut.blocksize = self.dataOut.nChannels * self.dataOut.nHeights

        self.dataOut.flagDecodeData = False #asumo que la data esta decodificada

        self.dataOut.flagDeflipData = False #asumo que la data esta sin flip

        self.dataOut.flagShiftFFT = False

        self.dataOut.ippSeconds = 1.0*self.__nSamples/self.__sample_rate

        #Time interval between profiles
        #self.dataOut.timeInterval =self.dataOut.ippSeconds * self.dataOut.nCohInt


        self.dataOut.frequency = self.__frequency

        self.dataOut.realtime = self.__online

    def __hasNotDataInBuffer(self):

        if self.profileIndex >= self.nProfiles:
            return 1

        return 0

    def readNextBlock(self):
        if not(self.__setNewBlock()):
            return 0

        if not(self.readBlock()):
            return 0

        return 1

    def __setNewBlock(self):

        if self.hfFilePointer==None:
            return 0

        if self.flagIsNewFile:
            return 1

        if self.profileIndex < self.nProfiles:
            return 1

        self.__setNextFile(self.online)

        return 1



    def readBlock(self):
        fp=h5py.File(self.filename,'r')
                      #Puntero que apunta al archivo hdf5
        ch0=(fp['ch0']).value    #Primer canal (100,1000)--(perfiles,alturas)
        ch1=(fp['ch1']).value    #Segundo canal (100,1000)--(perfiles,alturas)
        fp.close()
        ch0= ch0.swapaxes(0,1)   #Primer canal (100,1000)--(alturas,perfiles)
        ch1= ch1.swapaxes(0,1)   #Segundo canal (100,1000)--(alturas,perfiles)
        self.datablock = numpy.array([ch0,ch1])
        self.flagIsNewFile=0

        self.profileIndex=0

        return 1

    def getData(self):
        if self.flagNoMoreFiles:
            self.dataOut.flagNoData = True
            return 0

        if self.__hasNotDataInBuffer():
            if not(self.readNextBlock()):
                self.dataOut.flagNodata=True
                return 0

        ##############################
        ##############################
        self.dataOut.data = self.datablock[:,:,self.profileIndex]
        self.dataOut.utctime = self.__t0 + self.dataOut.ippSeconds*self.profileIndex
        self.dataOut.profileIndex= self.profileIndex
        self.dataOut.flagNoData=False
        self.profileIndex +=1

        return self.dataOut.data


    def run(self, **kwargs):
        '''
        This method will be called many times so here you should put all your code
        '''

        if not self.isConfig:
            self.setup(**kwargs)
            self.isConfig = True
        self.getData()