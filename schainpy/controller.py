'''
Updated on January , 2018, for multiprocessing purposes
Author: Sergio Cortez
Created on September , 2012
'''
from platform import python_version
import sys
import ast
import datetime
import traceback
import math
import time
import zmq
from multiprocessing import Process, cpu_count
from threading import Thread
from xml.etree.ElementTree import ElementTree, Element, SubElement, tostring
from xml.dom import minidom


from schainpy.admin import Alarm, SchainWarning
from schainpy.model import *
from schainpy.utils import log


DTYPES = {
    'Voltage': '.r',
    'Spectra': '.pdata'
}


def MPProject(project, n=cpu_count()):
    '''
    Project wrapper to run schain in n processes
    '''

    rconf = project.getReadUnitObj()
    op = rconf.getOperationObj('run')
    dt1 = op.getParameterValue('startDate')
    dt2 = op.getParameterValue('endDate')
    tm1 = op.getParameterValue('startTime')
    tm2 = op.getParameterValue('endTime')
    days = (dt2 - dt1).days

    for day in range(days + 1):
        skip = 0
        cursor = 0
        processes = []
        dt = dt1 + datetime.timedelta(day)
        dt_str = dt.strftime('%Y/%m/%d')
        reader = JRODataReader()
        paths, files = reader.searchFilesOffLine(path=rconf.path,
                                                 startDate=dt,
                                                 endDate=dt,
                                                 startTime=tm1,
                                                 endTime=tm2,
                                                 ext=DTYPES[rconf.datatype])
        nFiles = len(files)
        if nFiles == 0:
            continue
        skip = int(math.ceil(nFiles / n))        
        while nFiles > cursor * skip:
            rconf.update(startDate=dt_str, endDate=dt_str, cursor=cursor,
                         skip=skip)
            p = project.clone()
            p.start()
            processes.append(p)
            cursor += 1

        def beforeExit(exctype, value, trace):
            for process in processes:
                process.terminate()
                process.join()
            print(traceback.print_tb(trace))

        sys.excepthook = beforeExit

        for process in processes:
            process.join()
            process.terminate()

        time.sleep(3)

def wait(context):
    
    time.sleep(1)
    c = zmq.Context()
    receiver = c.socket(zmq.SUB)
    receiver.connect('ipc:///tmp/schain_{}_pub'.format(self.id))    
    receiver.setsockopt(zmq.SUBSCRIBE, self.id.encode())
    msg = receiver.recv_multipart()[1]
    context.terminate()

class ParameterConf():

    id = None
    name = None
    value = None
    format = None

    __formated_value = None

    ELEMENTNAME = 'Parameter'

    def __init__(self):

        self.format = 'str'

    def getElementName(self):

        return self.ELEMENTNAME

    def getValue(self):

        value = self.value
        format = self.format

        if self.__formated_value != None:

            return self.__formated_value

        if format == 'obj':
            return value

        if format == 'str':
            self.__formated_value = str(value)
            return self.__formated_value

        if value == '':
            raise ValueError('%s: This parameter value is empty' % self.name)

        if format == 'list':
            strList = value.split(',')

            self.__formated_value = strList

            return self.__formated_value

        if format == 'intlist':
            '''
            Example:
                value = (0,1,2)
            '''

            new_value = ast.literal_eval(value)

            if type(new_value) not in (tuple, list):
                new_value = [int(new_value)]

            self.__formated_value = new_value

            return self.__formated_value

        if format == 'floatlist':
            '''
            Example:
                value = (0.5, 1.4, 2.7)
            '''

            new_value = ast.literal_eval(value)

            if type(new_value) not in (tuple, list):
                new_value = [float(new_value)]

            self.__formated_value = new_value

            return self.__formated_value

        if format == 'date':
            strList = value.split('/')
            intList = [int(x) for x in strList]
            date = datetime.date(intList[0], intList[1], intList[2])

            self.__formated_value = date

            return self.__formated_value

        if format == 'time':
            strList = value.split(':')
            intList = [int(x) for x in strList]
            time = datetime.time(intList[0], intList[1], intList[2])

            self.__formated_value = time

            return self.__formated_value

        if format == 'pairslist':
            '''
            Example:
                value = (0,1),(1,2)
            '''

            new_value = ast.literal_eval(value)

            if type(new_value) not in (tuple, list):
                raise ValueError('%s has to be a tuple or list of pairs' % value)

            if type(new_value[0]) not in (tuple, list):
                if len(new_value) != 2:
                    raise ValueError('%s has to be a tuple or list of pairs' % value)
                new_value = [new_value]

            for thisPair in new_value:
                if len(thisPair) != 2:
                    raise ValueError('%s has to be a tuple or list of pairs' % value)

            self.__formated_value = new_value

            return self.__formated_value

        if format == 'multilist':
            '''
            Example:
                value = (0,1,2),(3,4,5)
            '''
            multiList = ast.literal_eval(value)

            if type(multiList[0]) == int:
                multiList = ast.literal_eval('(' + value + ')')

            self.__formated_value = multiList

            return self.__formated_value

        if format == 'bool':
            value = int(value)

        if format == 'int':
            value = float(value)

        format_func = eval(format)

        self.__formated_value = format_func(value)

        return self.__formated_value

    def updateId(self, new_id):

        self.id = str(new_id)

    def setup(self, id, name, value, format='str'):
        self.id = str(id)
        self.name = name
        if format == 'obj':
            self.value = value
        else:
            self.value = str(value)
        self.format = str.lower(format)

        self.getValue()

        return 1

    def update(self, name, value, format='str'):

        self.name = name
        self.value = str(value)
        self.format = format

    def makeXml(self, opElement):
        if self.name not in ('queue',):
            parmElement = SubElement(opElement, self.ELEMENTNAME)
            parmElement.set('id', str(self.id))
            parmElement.set('name', self.name)
            parmElement.set('value', self.value)
            parmElement.set('format', self.format)
            
    def readXml(self, parmElement):

        self.id = parmElement.get('id')
        self.name = parmElement.get('name')
        self.value = parmElement.get('value')
        self.format = str.lower(parmElement.get('format'))

        # Compatible with old signal chain version
        if self.format == 'int' and self.name == 'idfigure':
            self.name = 'id'

    def printattr(self):

        print('Parameter[%s]: name = %s, value = %s, format = %s, project_id = %s' % (self.id, self.name, self.value, self.format, self.project_id))

class OperationConf():

    ELEMENTNAME = 'Operation'

    def __init__(self):

        self.id = '0'
        self.name = None
        self.priority = None
        self.topic = None

    def __getNewId(self):

        return int(self.id) * 10 + len(self.parmConfObjList) + 1

    def getId(self):
        return self.id

    def updateId(self, new_id):

        self.id = str(new_id)

        n = 1
        for parmObj in self.parmConfObjList:

            idParm = str(int(new_id) * 10 + n)
            parmObj.updateId(idParm)

            n += 1

    def getElementName(self):

        return self.ELEMENTNAME

    def getParameterObjList(self):

        return self.parmConfObjList

    def getParameterObj(self, parameterName):

        for parmConfObj in self.parmConfObjList:

            if parmConfObj.name != parameterName:
                continue

            return parmConfObj

        return None

    def getParameterObjfromValue(self, parameterValue):

        for parmConfObj in self.parmConfObjList:

            if parmConfObj.getValue() != parameterValue:
                continue

            return parmConfObj.getValue()

        return None

    def getParameterValue(self, parameterName):

        parameterObj = self.getParameterObj(parameterName)

    #         if not parameterObj:
    #             return None

        value = parameterObj.getValue()

        return value

    def getKwargs(self):

        kwargs = {}

        for parmConfObj in self.parmConfObjList:
            if self.name == 'run' and parmConfObj.name == 'datatype':
                continue

            kwargs[parmConfObj.name] = parmConfObj.getValue()

        return kwargs

    def setup(self, id, name, priority, type, project_id):

        self.id = str(id)
        self.project_id = project_id
        self.name = name
        self.type = type
        self.priority = priority
        self.parmConfObjList = []

    def removeParameters(self):

        for obj in self.parmConfObjList:
            del obj

        self.parmConfObjList = []

    def addParameter(self, name, value, format='str'):

        if value is None:
            return None
        id = self.__getNewId()

        parmConfObj = ParameterConf()
        if not parmConfObj.setup(id, name, value, format):
            return None

        self.parmConfObjList.append(parmConfObj)

        return parmConfObj

    def changeParameter(self, name, value, format='str'):

        parmConfObj = self.getParameterObj(name)
        parmConfObj.update(name, value, format)

        return parmConfObj

    def makeXml(self, procUnitElement):

        opElement = SubElement(procUnitElement, self.ELEMENTNAME)
        opElement.set('id', str(self.id))
        opElement.set('name', self.name)
        opElement.set('type', self.type)
        opElement.set('priority', str(self.priority))

        for parmConfObj in self.parmConfObjList:
            parmConfObj.makeXml(opElement)

    def readXml(self, opElement, project_id):

        self.id = opElement.get('id')
        self.name = opElement.get('name')
        self.type = opElement.get('type')
        self.priority = opElement.get('priority')
        self.project_id = str(project_id)  

        # Compatible with old signal chain version
        # Use of 'run' method instead 'init'
        if self.type == 'self' and self.name == 'init':
            self.name = 'run'

        self.parmConfObjList = []

        parmElementList = opElement.iter(ParameterConf().getElementName())

        for parmElement in parmElementList:
            parmConfObj = ParameterConf()
            parmConfObj.readXml(parmElement)

            # Compatible with old signal chain version
            # If an 'plot' OPERATION is found, changes name operation by the value of its type PARAMETER
            if self.type != 'self' and self.name == 'Plot':
                if parmConfObj.format == 'str' and parmConfObj.name == 'type':
                    self.name = parmConfObj.value
                    continue

            self.parmConfObjList.append(parmConfObj)

    def printattr(self):

        print('%s[%s]: name = %s, type = %s, priority = %s, project_id = %s' % (self.ELEMENTNAME,
                                                               self.id,
                                                               self.name,
                                                               self.type,
                                                               self.priority,
                                                               self.project_id))

        for parmConfObj in self.parmConfObjList:
            parmConfObj.printattr()

    def createObject(self):

        className = eval(self.name)

        if self.type == 'other':
            opObj = className()
        elif self.type == 'external':
            kwargs = self.getKwargs()
            opObj = className(self.id, self.project_id, **kwargs)
            opObj.start()

        return opObj

class ProcUnitConf():

    ELEMENTNAME = 'ProcUnit'

    def __init__(self):

        self.id = None
        self.datatype = None
        self.name = None
        self.inputId = None 
        self.opConfObjList = []
        self.procUnitObj = None
        self.opObjDict = {}

    def __getPriority(self):

        return len(self.opConfObjList) + 1

    def __getNewId(self):

        return int(self.id) * 10 + len(self.opConfObjList) + 1

    def getElementName(self):

        return self.ELEMENTNAME

    def getId(self):

        return self.id

    def updateId(self, new_id): 
        '''
        new_id = int(parentId) * 10 + (int(self.id) % 10)
        new_inputId = int(parentId) * 10 + (int(self.inputId) % 10)

        # If this proc unit has not inputs
        #if self.inputId == '0':
            #new_inputId = 0

        n = 1
        for opConfObj in self.opConfObjList:

            idOp = str(int(new_id) * 10 + n)
            opConfObj.updateId(idOp)

            n += 1

        self.parentId = str(parentId)
        self.id = str(new_id)
        #self.inputId = str(new_inputId)
        '''
        n = 1

    def getInputId(self):

        return self.inputId

    def getOperationObjList(self):

        return self.opConfObjList

    def getOperationObj(self, name=None):

        for opConfObj in self.opConfObjList:

            if opConfObj.name != name:
                continue

            return opConfObj

        return None

    def getOpObjfromParamValue(self, value=None):

        for opConfObj in self.opConfObjList:
            if opConfObj.getParameterObjfromValue(parameterValue=value) != value:
                continue
            return opConfObj
        return None

    def getProcUnitObj(self):

        return self.procUnitObj

    def setup(self, project_id, id, name, datatype, inputId):
        '''
            id sera el topico a publicar
            inputId sera el topico a subscribirse
        '''
        
        # Compatible with old signal chain version
        if datatype == None and name == None:
            raise ValueError('datatype or name should be defined')

        #Definir una condicion para inputId cuando sea 0

        if name == None:
            if 'Proc' in datatype:
                name = datatype
            else:
                name = '%sProc' % (datatype)

        if datatype == None:
            datatype = name.replace('Proc', '')

        self.id = str(id)
        self.project_id = project_id
        self.name = name
        self.datatype = datatype
        self.inputId = inputId 
        self.opConfObjList = []

        self.addOperation(name='run', optype='self') 

    def removeOperations(self):

        for obj in self.opConfObjList:
            del obj

        self.opConfObjList = []
        self.addOperation(name='run')

    def addParameter(self, **kwargs):
        '''
        Add parameters to 'run' operation
        '''
        opObj = self.opConfObjList[0]

        opObj.addParameter(**kwargs)

        return opObj

    def addOperation(self, name, optype='self'):
        '''
            Actualizacion - > proceso comunicacion
            En el caso de optype='self', elminar. DEfinir comuncacion IPC -> Topic
            definir el tipoc de socket o comunicacion ipc++

        '''

        id = self.__getNewId()
        priority = self.__getPriority() # Sin mucho sentido, pero puede usarse
        opConfObj = OperationConf()
        opConfObj.setup(id, name=name, priority=priority, type=optype, project_id=self.project_id)
        self.opConfObjList.append(opConfObj)

        return opConfObj

    def makeXml(self, projectElement):

        procUnitElement = SubElement(projectElement, self.ELEMENTNAME)
        procUnitElement.set('id', str(self.id))
        procUnitElement.set('name', self.name)
        procUnitElement.set('datatype', self.datatype)
        procUnitElement.set('inputId', str(self.inputId))

        for opConfObj in self.opConfObjList:
            opConfObj.makeXml(procUnitElement)

    def readXml(self, upElement, project_id):

        self.id = upElement.get('id')
        self.name = upElement.get('name')
        self.datatype = upElement.get('datatype')
        self.inputId = upElement.get('inputId')
        self.project_id = str(project_id)

        if self.ELEMENTNAME == 'ReadUnit':
            self.datatype = self.datatype.replace('Reader', '')

        if self.ELEMENTNAME == 'ProcUnit':
            self.datatype = self.datatype.replace('Proc', '')

        if self.inputId == 'None':
            self.inputId = '0'

        self.opConfObjList = []

        opElementList = upElement.iter(OperationConf().getElementName())

        for opElement in opElementList:
            opConfObj = OperationConf()
            opConfObj.readXml(opElement, project_id)
            self.opConfObjList.append(opConfObj)

    def printattr(self):

        print('%s[%s]: name = %s, datatype = %s, inputId = %s, project_id = %s' % (self.ELEMENTNAME,
                                                                  self.id,
                                                                  self.name,
                                                                  self.datatype,
                                                                  self.inputId,
                                                                  self.project_id))

        for opConfObj in self.opConfObjList:
            opConfObj.printattr()

    def getKwargs(self):

        opObj = self.opConfObjList[0]
        kwargs = opObj.getKwargs()

        return kwargs

    def createObjects(self):
        '''
        Instancia de unidades de procesamiento.
        '''

        className = eval(self.name)
        kwargs = self.getKwargs()
        procUnitObj = className(self.id, self.inputId, self.project_id, **kwargs) # necesitan saber su id y su entrada por fines de ipc
        log.success('creating process...', self.name)

        for opConfObj in self.opConfObjList:
            
            if opConfObj.type == 'self' and opConfObj.name == 'run':
                continue
            elif opConfObj.type == 'self':
                opObj = getattr(procUnitObj, opConfObj.name)
            else:
                opObj = opConfObj.createObject()
            
            log.success('creating operation: {}, type:{}'.format(
                opConfObj.name,
                opConfObj.type), self.name)
            
            procUnitObj.addOperation(opConfObj, opObj)
     
        procUnitObj.start()
        self.procUnitObj = procUnitObj
        
    def close(self):

        for opConfObj in self.opConfObjList:
            if opConfObj.type == 'self':
                continue

            opObj = self.procUnitObj.getOperationObj(opConfObj.id)
            opObj.close()

        self.procUnitObj.close()

        return


class ReadUnitConf(ProcUnitConf):

    ELEMENTNAME = 'ReadUnit'

    def __init__(self):

        self.id = None
        self.datatype = None
        self.name = None
        self.inputId = None
        self.opConfObjList = []

    def getElementName(self):

        return self.ELEMENTNAME 
    
    def setup(self, project_id, id, name, datatype, path='', startDate='', endDate='',
              startTime='', endTime='', server=None, **kwargs):


        '''
        *****el id del proceso sera el Topico

        Adicion de {topic}, si no esta presente -> error
        kwargs deben ser trasmitidos en la instanciacion

        '''
        
        # Compatible with old signal chain version
        if datatype == None and name == None:
            raise ValueError('datatype or name should be defined')
        if name == None:
            if 'Reader' in datatype:
                name = datatype
                datatype = name.replace('Reader','')
            else:
                name = '{}Reader'.format(datatype)
        if datatype == None:
            if 'Reader' in name:
                datatype = name.replace('Reader','')
            else:
                datatype = name
                name = '{}Reader'.format(name)

        self.id = id
        self.project_id = project_id
        self.name = name
        self.datatype = datatype
        if path != '':
            self.path = os.path.abspath(path)
        self.startDate = startDate
        self.endDate = endDate
        self.startTime = startTime
        self.endTime = endTime
        self.server = server
        self.addRunOperation(**kwargs)

    def update(self, **kwargs):

        if 'datatype' in kwargs:
            datatype = kwargs.pop('datatype')
            if 'Reader' in datatype:
                self.name = datatype
            else:
                self.name = '%sReader' % (datatype)
            self.datatype = self.name.replace('Reader', '')

        attrs = ('path', 'startDate', 'endDate',
                 'startTime', 'endTime')

        for attr in attrs:
            if attr in kwargs:
                setattr(self, attr, kwargs.pop(attr))

        self.updateRunOperation(**kwargs)

    def removeOperations(self):

        for obj in self.opConfObjList:
            del obj

        self.opConfObjList = []

    def addRunOperation(self, **kwargs): 

        opObj = self.addOperation(name='run', optype='self') 

        if self.server is None:
            opObj.addParameter(
                name='datatype', value=self.datatype, format='str')
            opObj.addParameter(name='path', value=self.path, format='str')
            opObj.addParameter(
                name='startDate', value=self.startDate, format='date')
            opObj.addParameter(
                name='endDate', value=self.endDate, format='date')
            opObj.addParameter(
                name='startTime', value=self.startTime, format='time')
            opObj.addParameter(
                name='endTime', value=self.endTime, format='time')

            for key, value in list(kwargs.items()):
                opObj.addParameter(name=key, value=value,
                                   format=type(value).__name__)
        else:
            opObj.addParameter(name='server', value=self.server, format='str')

        return opObj

    def updateRunOperation(self, **kwargs):

        opObj = self.getOperationObj(name='run')
        opObj.removeParameters()

        opObj.addParameter(name='datatype', value=self.datatype, format='str')
        opObj.addParameter(name='path', value=self.path, format='str')
        opObj.addParameter(
            name='startDate', value=self.startDate, format='date')
        opObj.addParameter(name='endDate', value=self.endDate, format='date')
        opObj.addParameter(
            name='startTime', value=self.startTime, format='time')
        opObj.addParameter(name='endTime', value=self.endTime, format='time')

        for key, value in list(kwargs.items()):
            opObj.addParameter(name=key, value=value,
                               format=type(value).__name__)

        return opObj

    def readXml(self, upElement, project_id):

        self.id = upElement.get('id')
        self.name = upElement.get('name')
        self.datatype = upElement.get('datatype')
        self.project_id = str(project_id)  #yong

        if self.ELEMENTNAME == 'ReadUnit':
            self.datatype = self.datatype.replace('Reader', '')

        self.opConfObjList = []

        opElementList = upElement.iter(OperationConf().getElementName())

        for opElement in opElementList:
            opConfObj = OperationConf()
            opConfObj.readXml(opElement, project_id)
            self.opConfObjList.append(opConfObj)

            if opConfObj.name == 'run':
                self.path = opConfObj.getParameterValue('path')
                self.startDate = opConfObj.getParameterValue('startDate')
                self.endDate = opConfObj.getParameterValue('endDate')
                self.startTime = opConfObj.getParameterValue('startTime')
                self.endTime = opConfObj.getParameterValue('endTime')


class Project(Process):

    ELEMENTNAME = 'Project'

    def __init__(self):

        Process.__init__(self)
        self.id = None
        self.filename = None
        self.description = None
        self.email = None
        self.alarm = None
        self.procUnitConfObjDict = {}

    def __getNewId(self):

        idList = list(self.procUnitConfObjDict.keys())
        id = int(self.id) * 10

        while True:
            id += 1

            if str(id) in idList:
                continue

            break

        return str(id)

    def getElementName(self):

        return self.ELEMENTNAME

    def getId(self):

        return self.id

    def updateId(self, new_id):

        self.id = str(new_id)

        keyList = list(self.procUnitConfObjDict.keys())
        keyList.sort()

        n = 1
        newProcUnitConfObjDict = {}

        for procKey in keyList:

            procUnitConfObj = self.procUnitConfObjDict[procKey]
            idProcUnit = str(int(self.id) * 10 + n)
            procUnitConfObj.updateId(idProcUnit)
            newProcUnitConfObjDict[idProcUnit] = procUnitConfObj
            n += 1

        self.procUnitConfObjDict = newProcUnitConfObjDict

    def setup(self, id=1, name='', description='', email=None, alarm=[]):

        print(' ')
        print('*' * 60)
        print('*  Starting SIGNAL CHAIN PROCESSING (Multiprocessing) v%s *' % schainpy.__version__)
        print('*' * 60)
        print("*  Python " + python_version() + "  *")
        print('*' * 19)
        print(' ')
        self.id = str(id)
        self.description = description 
        self.email = email
        self.alarm = alarm

    def update(self, **kwargs):

        for key, value in list(kwargs.items()):
            setattr(self, key, value)

    def clone(self):

        p = Project()
        p.procUnitConfObjDict = self.procUnitConfObjDict
        return p

    def addReadUnit(self, id=None, datatype=None, name=None, **kwargs):

        '''
        Actualizacion:
            Se agrego un nuevo argumento: topic -relativo a la forma de comunicar los procesos simultaneos

            * El id del proceso sera el topico al que se deben subscribir los procUnits para recibir la informacion(data)

        '''

        if id is None:
            idReadUnit = self.__getNewId()
        else:
            idReadUnit = str(id)

        readUnitConfObj = ReadUnitConf()
        readUnitConfObj.setup(self.id, idReadUnit, name, datatype, **kwargs)
        self.procUnitConfObjDict[readUnitConfObj.getId()] = readUnitConfObj
        
        return readUnitConfObj

    def addProcUnit(self, inputId='0', datatype=None, name=None):

        '''
        Actualizacion:
            Se agrego dos nuevos argumentos: topic_read (lee data de otro procUnit) y topic_write(escribe o envia data a otro procUnit)
            Deberia reemplazar a "inputId"

            ** A fin de mantener el inputID, este sera la representaacion del topicoal que deben subscribirse. El ID propio de la intancia
            (proceso) sera el topico de la publicacion, todo sera asignado de manera dinamica.

        '''

        idProcUnit = self.__getNewId() #Topico para subscripcion
        procUnitConfObj = ProcUnitConf()
        procUnitConfObj.setup(self.id, idProcUnit, name, datatype, inputId) #topic_read, topic_write, 
        self.procUnitConfObjDict[procUnitConfObj.getId()] = procUnitConfObj

        return procUnitConfObj

    def removeProcUnit(self, id):

        if id in list(self.procUnitConfObjDict.keys()):
            self.procUnitConfObjDict.pop(id)

    def getReadUnitId(self):

        readUnitConfObj = self.getReadUnitObj()

        return readUnitConfObj.id

    def getReadUnitObj(self):

        for obj in list(self.procUnitConfObjDict.values()):
            if obj.getElementName() == 'ReadUnit':
                return obj

        return None

    def getProcUnitObj(self, id=None, name=None):

        if id != None:
            return self.procUnitConfObjDict[id]

        if name != None:
            return self.getProcUnitObjByName(name)

        return None

    def getProcUnitObjByName(self, name):

        for obj in list(self.procUnitConfObjDict.values()):
            if obj.name == name:
                return obj

        return None

    def procUnitItems(self):

        return list(self.procUnitConfObjDict.items())

    def makeXml(self):

        projectElement = Element('Project')
        projectElement.set('id', str(self.id))
        projectElement.set('name', self.name)
        projectElement.set('description', self.description)

        for procUnitConfObj in list(self.procUnitConfObjDict.values()):
            procUnitConfObj.makeXml(projectElement)

        self.projectElement = projectElement

    def writeXml(self, filename=None):

        if filename == None:
            if self.filename:
                filename = self.filename
            else:
                filename = 'schain.xml'

        if not filename:
            print('filename has not been defined. Use setFilename(filename) for do it.')
            return 0

        abs_file = os.path.abspath(filename)

        if not os.access(os.path.dirname(abs_file), os.W_OK):
            print('No write permission on %s' % os.path.dirname(abs_file))
            return 0

        if os.path.isfile(abs_file) and not(os.access(abs_file, os.W_OK)):
            print('File %s already exists and it could not be overwriten' % abs_file)
            return 0

        self.makeXml()

        ElementTree(self.projectElement).write(abs_file, method='xml')

        self.filename = abs_file

        return 1

    def readXml(self, filename=None):

        if not filename:
            print('filename is not defined')
            return 0

        abs_file = os.path.abspath(filename)

        if not os.path.isfile(abs_file):
            print('%s file does not exist' % abs_file)
            return 0

        self.projectElement = None
        self.procUnitConfObjDict = {}

        try:
            self.projectElement = ElementTree().parse(abs_file)
        except:
            print('Error reading %s, verify file format' % filename)
            return 0

        self.project = self.projectElement.tag

        self.id = self.projectElement.get('id')
        self.name = self.projectElement.get('name')
        self.description = self.projectElement.get('description')

        readUnitElementList = self.projectElement.iter(
            ReadUnitConf().getElementName())

        for readUnitElement in readUnitElementList:
            readUnitConfObj = ReadUnitConf()
            readUnitConfObj.readXml(readUnitElement, self.id)
            self.procUnitConfObjDict[readUnitConfObj.getId()] = readUnitConfObj

        procUnitElementList = self.projectElement.iter(
            ProcUnitConf().getElementName())

        for procUnitElement in procUnitElementList:
            procUnitConfObj = ProcUnitConf()
            procUnitConfObj.readXml(procUnitElement, self.id)
            self.procUnitConfObjDict[procUnitConfObj.getId()] = procUnitConfObj

        self.filename = abs_file

        return 1

    def __str__(self):

        print('Project[%s]: name = %s, description = %s, project_id = %s' % (self.id,
                                                            self.name,
                                                            self.description,
                                                            self.project_id))

        for procUnitConfObj in self.procUnitConfObjDict.values():
            print(procUnitConfObj)

    def createObjects(self):


        keys = list(self.procUnitConfObjDict.keys())
        keys.sort()
        for key in keys:
            self.procUnitConfObjDict[key].createObjects()

    def __handleError(self, procUnitConfObj, modes=None, stdout=True):

        import socket

        if modes is None:
            modes = self.alarm
        
        if not self.alarm:
            modes = []

        err = traceback.format_exception(sys.exc_info()[0],
                                         sys.exc_info()[1],
                                         sys.exc_info()[2])

        log.error('{}'.format(err[-1]), procUnitConfObj.name)

        message = ''.join(err)

        if stdout:
            sys.stderr.write(message)

        subject = 'SChain v%s: Error running %s\n' % (
            schainpy.__version__, procUnitConfObj.name)

        subtitle = '%s: %s\n' % (
            procUnitConfObj.getElementName(), procUnitConfObj.name)
        subtitle += 'Hostname: %s\n' % socket.gethostbyname(
            socket.gethostname())
        subtitle += 'Working directory: %s\n' % os.path.abspath('./')
        subtitle += 'Configuration file: %s\n' % self.filename
        subtitle += 'Time: %s\n' % str(datetime.datetime.now())

        readUnitConfObj = self.getReadUnitObj()
        if readUnitConfObj:
            subtitle += '\nInput parameters:\n'
            subtitle += '[Data path = %s]\n' % readUnitConfObj.path
            subtitle += '[Data type = %s]\n' % readUnitConfObj.datatype
            subtitle += '[Start date = %s]\n' % readUnitConfObj.startDate
            subtitle += '[End date = %s]\n' % readUnitConfObj.endDate
            subtitle += '[Start time = %s]\n' % readUnitConfObj.startTime
            subtitle += '[End time = %s]\n' % readUnitConfObj.endTime

        a = Alarm(
            modes=modes, 
            email=self.email,
            message=message,
            subject=subject,
            subtitle=subtitle,
            filename=self.filename
        )

        return a

    def isPaused(self):
        return 0

    def isStopped(self):
        return 0

    def runController(self):
        '''
        returns 0 when this process has been stopped, 1 otherwise
        '''

        if self.isPaused():
            print('Process suspended')

            while True:
                time.sleep(0.1)

                if not self.isPaused():
                    break

                if self.isStopped():
                    break

            print('Process reinitialized')

        if self.isStopped():
            print('Process stopped')
            return 0

        return 1

    def setFilename(self, filename):

        self.filename = filename

    def setProxyCom(self):

        if not os.path.exists('/tmp/schain'):
            os.mkdir('/tmp/schain')
        
        self.ctx = zmq.Context()
        xpub = self.ctx.socket(zmq.XPUB)
        xpub.bind('ipc:///tmp/schain/{}_pub'.format(self.id))
        xsub = self.ctx.socket(zmq.XSUB)
        xsub.bind('ipc:///tmp/schain/{}_sub'.format(self.id))
        
        try:
            zmq.proxy(xpub, xsub)
        except: # zmq.ContextTerminated:
            xpub.close()
            xsub.close()

    def run(self):

        log.success('Starting {}: {}'.format(self.name, self.id), tag='')
        self.start_time = time.time()
        self.createObjects()
        # t = Thread(target=wait, args=(self.ctx, ))
        # t.start()
        self.setProxyCom()
        
        # Iniciar todos los procesos .start(), monitoreo de procesos. ELiminar lo de abajo

        log.success('{} Done (time: {}s)'.format(
            self.name,
            time.time()-self.start_time))
