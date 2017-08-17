'''
Created on September , 2012
@author:
'''

import sys
import ast
import datetime
import traceback
import math
import time
from multiprocessing import Process, Queue, cpu_count
from profilehooks import profile, coverage

import schainpy
import schainpy.admin

from xml.etree.ElementTree import ElementTree, Element, SubElement, tostring
from xml.dom import minidom

from schainpy.model import *
from time import sleep



def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def multiSchain(child, nProcess=cpu_count(), startDate=None, endDate=None, by_day=False):
    skip = 0
    cursor = 0
    nFiles = None
    processes = []
    dt1 = datetime.datetime.strptime(startDate, '%Y/%m/%d')
    dt2 = datetime.datetime.strptime(endDate, '%Y/%m/%d')
    days = (dt2 - dt1).days

    for day in range(days+1):
        skip = 0
        cursor = 0
        q = Queue()
        processes = []
        dt = (dt1 + datetime.timedelta(day)).strftime('%Y/%m/%d')
        firstProcess = Process(target=child, args=(cursor, skip, q, dt))
        firstProcess.start()
        if by_day:
            continue
        nFiles = q.get()
        firstProcess.terminate()
        skip = int(math.ceil(nFiles/nProcess))
        while True:
            processes.append(Process(target=child, args=(cursor, skip, q, dt)))
            processes[cursor].start()
            if nFiles < cursor*skip:
                break
            cursor += 1

        def beforeExit(exctype, value, trace):
            for process in processes:
                process.terminate()
                process.join()
            print traceback.print_tb(trace)

        sys.excepthook = beforeExit

        for process in processes:
            process.join()
            process.terminate()
        time.sleep(3)

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
            raise ValueError, "%s: This parameter value is empty" %self.name

        if format == 'list':
            strList = value.split(',')

            self.__formated_value = strList

            return self.__formated_value

        if format == 'intlist':
            """
            Example:
                value = (0,1,2)
            """

            new_value = ast.literal_eval(value)

            if type(new_value) not in (tuple, list):
                new_value = [int(new_value)]

            self.__formated_value = new_value

            return self.__formated_value

        if format == 'floatlist':
            """
            Example:
                value = (0.5, 1.4, 2.7)
            """

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
            """
            Example:
                value = (0,1),(1,2)
            """

            new_value = ast.literal_eval(value)

            if type(new_value) not in (tuple, list):
                raise ValueError, "%s has to be a tuple or list of pairs" %value

            if type(new_value[0]) not in (tuple, list):
                if len(new_value) != 2:
                    raise ValueError, "%s has to be a tuple or list of pairs" %value
                new_value = [new_value]

            for thisPair in new_value:
                if len(thisPair) != 2:
                    raise ValueError, "%s has to be a tuple or list of pairs" %value

            self.__formated_value = new_value

            return self.__formated_value

        if format == 'multilist':
            """
            Example:
                value = (0,1,2),(3,4,5)
            """
            multiList = ast.literal_eval(value)

            if type(multiList[0]) == int:
                multiList = ast.literal_eval("(" + value + ")")

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

        #Compatible with old signal chain version
        if self.format == 'int' and self.name == 'idfigure':
            self.name = 'id'

    def printattr(self):

        print "Parameter[%s]: name = %s, value = %s, format = %s" %(self.id, self.name, self.value, self.format)

class OperationConf():  

    id = None
    name = None
    priority = None
    type = None

    parmConfObjList = []

    ELEMENTNAME = 'Operation'

    def __init__(self):

        self.id = '0'
        self.name = None
        self.priority = None
        self.type = 'self'


    def __getNewId(self):

        return int(self.id)*10 + len(self.parmConfObjList) + 1

    def updateId(self, new_id):

        self.id = str(new_id)

        n = 1
        for parmObj in self.parmConfObjList:

            idParm = str(int(new_id)*10 + n)
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

    def setup(self, id, name, priority, type):

        self.id = str(id)
        self.name = name
        self.type = type
        self.priority = priority

        self.parmConfObjList = []

    def removeParameters(self):

        for obj in self.parmConfObjList:
            del obj

        self.parmConfObjList = []

    def addParameter(self, name, value, format='str'):

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

    def readXml(self, opElement):

        self.id = opElement.get('id')
        self.name = opElement.get('name')
        self.type = opElement.get('type')
        self.priority = opElement.get('priority')

        #Compatible with old signal chain version
        #Use of 'run' method instead 'init'
        if self.type == 'self' and self.name == 'init':
            self.name = 'run'

        self.parmConfObjList = []

        parmElementList = opElement.iter(ParameterConf().getElementName())

        for parmElement in parmElementList:
            parmConfObj = ParameterConf()
            parmConfObj.readXml(parmElement)

            #Compatible with old signal chain version
            #If an 'plot' OPERATION is found, changes name operation by the value of its type PARAMETER
            if self.type != 'self' and self.name == 'Plot':
                if parmConfObj.format == 'str' and parmConfObj.name == 'type':
                    self.name = parmConfObj.value
                    continue

            self.parmConfObjList.append(parmConfObj)

    def printattr(self):

        print "%s[%s]: name = %s, type = %s, priority = %s" %(self.ELEMENTNAME,
                                                              self.id,
                                                              self.name,
                                                              self.type,
                                                              self.priority)

        for parmConfObj in self.parmConfObjList:
            parmConfObj.printattr()

    def createObject(self, plotter_queue=None):


        if self.type == 'self':
            raise ValueError, "This operation type cannot be created"

        if self.type == 'plotter':
            #Plotter(plotter_name)
            if not plotter_queue:
                raise ValueError, "plotter_queue is not defined. Use:\nmyProject = Project()\nmyProject.setPlotterQueue(plotter_queue)"

            opObj = Plotter(self.name, plotter_queue)

        if self.type == 'external' or self.type == 'other':

            className = eval(self.name)
            kwargs = self.getKwargs()

            opObj = className(**kwargs)

        return opObj


class ProcUnitConf():

    id = None
    name = None
    datatype = None
    inputId = None
    parentId = None

    opConfObjList = []

    procUnitObj = None
    opObjList = []

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

        return len(self.opConfObjList)+1

    def __getNewId(self):

        return int(self.id)*10 + len(self.opConfObjList) + 1

    def getElementName(self):

        return self.ELEMENTNAME

    def getId(self):

        return self.id

    def updateId(self, new_id, parentId=parentId):


        new_id = int(parentId)*10 + (int(self.id) % 10)
        new_inputId = int(parentId)*10 + (int(self.inputId) % 10)

        #If this proc unit has not inputs
        if self.inputId == '0':
            new_inputId = 0

        n = 1
        for opConfObj in self.opConfObjList:

            idOp = str(int(new_id)*10 + n)
            opConfObj.updateId(idOp)

            n += 1

        self.parentId = str(parentId)
        self.id = str(new_id)
        self.inputId = str(new_inputId)


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

    def setup(self, id, name, datatype, inputId, parentId=None):

        #Compatible with old signal chain version
        if datatype==None and name==None:
            raise ValueError, "datatype or name should be defined"

        if name==None:
            if 'Proc' in datatype:
                name = datatype
            else:
                name = '%sProc' %(datatype)

        if datatype==None:
            datatype = name.replace('Proc','')

        self.id = str(id)
        self.name = name
        self.datatype = datatype
        self.inputId = inputId
        self.parentId = parentId

        self.opConfObjList = []

        self.addOperation(name='run', optype='self')

    def removeOperations(self):

        for obj in self.opConfObjList:
            del obj

        self.opConfObjList = []
        self.addOperation(name='run')

    def addParameter(self, **kwargs):
        '''
        Add parameters to "run" operation
        '''
        opObj = self.opConfObjList[0]

        opObj.addParameter(**kwargs)

        return opObj

    def addOperation(self, name, optype='self'):

        id = self.__getNewId()
        priority = self.__getPriority()

        opConfObj = OperationConf()
        opConfObj.setup(id, name=name, priority=priority, type=optype)

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

    def readXml(self, upElement):

        self.id = upElement.get('id')
        self.name = upElement.get('name')
        self.datatype = upElement.get('datatype')
        self.inputId = upElement.get('inputId')

        if self.ELEMENTNAME == "ReadUnit":
            self.datatype = self.datatype.replace("Reader", "")

        if self.ELEMENTNAME == "ProcUnit":
            self.datatype = self.datatype.replace("Proc", "")

        if self.inputId == 'None':
            self.inputId = '0'

        self.opConfObjList = []

        opElementList = upElement.iter(OperationConf().getElementName())

        for opElement in opElementList:
            opConfObj = OperationConf()
            opConfObj.readXml(opElement)
            self.opConfObjList.append(opConfObj)

    def printattr(self):

        print "%s[%s]: name = %s, datatype = %s, inputId = %s" %(self.ELEMENTNAME,
                                                             self.id,
                                                             self.name,
                                                             self.datatype,
                                                             self.inputId)

        for opConfObj in self.opConfObjList:
            opConfObj.printattr()


    def getKwargs(self):

        opObj = self.opConfObjList[0]
        kwargs = opObj.getKwargs()

        return kwargs

    def createObjects(self, plotter_queue=None):

        className = eval(self.name)
        kwargs = self.getKwargs()
        procUnitObj = className(**kwargs)

        for opConfObj in self.opConfObjList:

            if opConfObj.type=='self' and self.name=='run':
                continue
            elif opConfObj.type=='self':
                procUnitObj.addOperationKwargs(opConfObj.id, **opConfObj.getKwargs())
                continue

            opObj = opConfObj.createObject(plotter_queue)

            self.opObjDict[opConfObj.id] = opObj

            procUnitObj.addOperation(opObj, opConfObj.id)

        self.procUnitObj = procUnitObj

        return procUnitObj

    ## @profile
    def run(self):

        is_ok = False

        for opConfObj in self.opConfObjList:

            kwargs = {}
            for parmConfObj in opConfObj.getParameterObjList():
                if opConfObj.name == 'run' and parmConfObj.name == 'datatype':
                    continue

                kwargs[parmConfObj.name] = parmConfObj.getValue()

            #ini = time.time()

            #print "\tRunning the '%s' operation with %s" %(opConfObj.name, opConfObj.id)
            sts = self.procUnitObj.call(opType = opConfObj.type,
                                        opName = opConfObj.name,
                                        opId = opConfObj.id,
                                        )

        #             total_time = time.time() - ini
        #
        #             if total_time > 0.002:
        #                 print "%s::%s took %f seconds" %(self.name, opConfObj.name, total_time)

            is_ok = is_ok or sts

        return is_ok

    def close(self):

        for opConfObj in self.opConfObjList:
            if opConfObj.type == 'self':
                continue

            opObj = self.procUnitObj.getOperationObj(opConfObj.id)
            opObj.close()

        self.procUnitObj.close()

        return

class ReadUnitConf(ProcUnitConf):

    path = None
    startDate = None
    endDate = None
    startTime = None
    endTime = None

    ELEMENTNAME = 'ReadUnit'

    def __init__(self):

        self.id = None
        self.datatype = None
        self.name = None
        self.inputId = None

        self.parentId = None

        self.opConfObjList = []
        self.opObjList = []

    def getElementName(self):

        return self.ELEMENTNAME

    def setup(self, id, name, datatype, path='', startDate="", endDate="", startTime="", 
              endTime="", parentId=None, queue=None, server=None, **kwargs):

        #Compatible with old signal chain version
        if datatype==None and name==None:
            raise ValueError, "datatype or name should be defined"
        
        if name==None:
            if 'Reader' in datatype:
                name = datatype
            else:
                name = '%sReader' %(datatype)
        if datatype==None:
            datatype = name.replace('Reader','')

        self.id = id
        self.name = name
        self.datatype = datatype
        if path != '':
            self.path = os.path.abspath(path)
        self.startDate = startDate
        self.endDate = endDate
        self.startTime = startTime
        self.endTime = endTime

        self.inputId = '0'
        self.parentId = parentId
        self.queue = queue
        self.server = server
        self.addRunOperation(**kwargs)

    def update(self, datatype, path, startDate, endDate, startTime, endTime, parentId=None, name=None, **kwargs):

        #Compatible with old signal chain version
        if datatype==None and name==None:
            raise ValueError, "datatype or name should be defined"

        if name==None:
            if 'Reader' in datatype:
                name = datatype
            else:
                name = '%sReader' %(datatype)

        if datatype==None:
            datatype = name.replace('Reader','')

        self.datatype = datatype
        self.name = name
        self.path = path
        self.startDate = startDate
        self.endDate = endDate
        self.startTime = startTime
        self.endTime = endTime

        self.inputId = '0'
        self.parentId = parentId

        self.updateRunOperation(**kwargs)

    def removeOperations(self):

        for obj in self.opConfObjList:
            del obj

        self.opConfObjList = []

    def addRunOperation(self, **kwargs):

        opObj = self.addOperation(name = 'run', optype = 'self')

        if self.server is None:
            opObj.addParameter(name='datatype' , value=self.datatype, format='str')
            opObj.addParameter(name='path'     , value=self.path, format='str')
            opObj.addParameter(name='startDate' , value=self.startDate, format='date')
            opObj.addParameter(name='endDate'   , value=self.endDate, format='date')
            opObj.addParameter(name='startTime' , value=self.startTime, format='time')
            opObj.addParameter(name='endTime'   , value=self.endTime, format='time')
            opObj.addParameter(name='queue'   , value=self.queue, format='obj')
            for key, value in kwargs.items():
                opObj.addParameter(name=key, value=value, format=type(value).__name__)
        else:
            opObj.addParameter(name='server' , value=self.server, format='str')
        

        return opObj

    def updateRunOperation(self, **kwargs):

        opObj = self.getOperationObj(name = 'run')
        opObj.removeParameters()

        opObj.addParameter(name='datatype' , value=self.datatype, format='str')
        opObj.addParameter(name='path'     , value=self.path, format='str')
        opObj.addParameter(name='startDate' , value=self.startDate, format='date')
        opObj.addParameter(name='endDate'   , value=self.endDate, format='date')
        opObj.addParameter(name='startTime' , value=self.startTime, format='time')
        opObj.addParameter(name='endTime'   , value=self.endTime, format='time')

        for key, value in kwargs.items():
            opObj.addParameter(name=key, value=value, format=type(value).__name__)

        return opObj

        #     def makeXml(self, projectElement):
        #
        #         procUnitElement = SubElement(projectElement, self.ELEMENTNAME)
        #         procUnitElement.set('id', str(self.id))
        #         procUnitElement.set('name', self.name)
        #         procUnitElement.set('datatype', self.datatype)
        #         procUnitElement.set('inputId', str(self.inputId))
        #
        #         for opConfObj in self.opConfObjList:
        #             opConfObj.makeXml(procUnitElement)

    def readXml(self, upElement):

        self.id = upElement.get('id')
        self.name = upElement.get('name')
        self.datatype = upElement.get('datatype')
        self.inputId = upElement.get('inputId')

        if self.ELEMENTNAME == "ReadUnit":
            self.datatype = self.datatype.replace("Reader", "")

        if self.inputId == 'None':
            self.inputId = '0'

        self.opConfObjList = []

        opElementList = upElement.iter(OperationConf().getElementName())

        for opElement in opElementList:
            opConfObj = OperationConf()
            opConfObj.readXml(opElement)
            self.opConfObjList.append(opConfObj)

            if opConfObj.name == 'run':
                self.path = opConfObj.getParameterValue('path')
                self.startDate = opConfObj.getParameterValue('startDate')
                self.endDate = opConfObj.getParameterValue('endDate')
                self.startTime = opConfObj.getParameterValue('startTime')
                self.endTime = opConfObj.getParameterValue('endTime')

class Project():

    id = None
    name = None
    description = None
    filename = None

    procUnitConfObjDict = None

    ELEMENTNAME = 'Project'

    plotterQueue = None

    def __init__(self, plotter_queue=None):

        self.id = None
        self.name = None
        self.description = None

        self.plotterQueue = plotter_queue

        self.procUnitConfObjDict = {}

    def __getNewId(self):

        idList = self.procUnitConfObjDict.keys()

        id = int(self.id)*10

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

        keyList = self.procUnitConfObjDict.keys()
        keyList.sort()

        n = 1
        newProcUnitConfObjDict = {}

        for procKey in keyList:

            procUnitConfObj = self.procUnitConfObjDict[procKey]
            idProcUnit = str(int(self.id)*10 + n)
            procUnitConfObj.updateId(idProcUnit, parentId = self.id)

            newProcUnitConfObjDict[idProcUnit] = procUnitConfObj
            n += 1

        self.procUnitConfObjDict = newProcUnitConfObjDict

    def setup(self, id, name, description):

        self.id = str(id)
        self.name = name
        self.description = description

    def update(self, name, description):

        self.name = name
        self.description = description

    def addReadUnit(self, id=None, datatype=None, name=None, **kwargs):

        if id is None:
            idReadUnit = self.__getNewId()
        else:
            idReadUnit = str(id)

        readUnitConfObj = ReadUnitConf()
        readUnitConfObj.setup(idReadUnit, name, datatype, parentId=self.id, **kwargs)

        self.procUnitConfObjDict[readUnitConfObj.getId()] = readUnitConfObj

        return readUnitConfObj

    def addProcUnit(self, inputId='0', datatype=None, name=None):

        idProcUnit = self.__getNewId()

        procUnitConfObj = ProcUnitConf()
        procUnitConfObj.setup(idProcUnit, name, datatype, inputId, parentId=self.id)

        self.procUnitConfObjDict[procUnitConfObj.getId()] = procUnitConfObj

        return procUnitConfObj

    def removeProcUnit(self, id):

        if id in self.procUnitConfObjDict.keys():
            self.procUnitConfObjDict.pop(id)

    def getReadUnitId(self):

        readUnitConfObj = self.getReadUnitObj()

        return readUnitConfObj.id

    def getReadUnitObj(self):

        for obj in self.procUnitConfObjDict.values():
            if obj.getElementName() == "ReadUnit":
                return obj

        return None

    def getProcUnitObj(self, id=None, name=None):

        if id != None:
            return self.procUnitConfObjDict[id]

        if name != None:
            return self.getProcUnitObjByName(name)

        return None

    def getProcUnitObjByName(self, name):

        for obj in self.procUnitConfObjDict.values():
            if obj.name == name:
                return obj

        return None

    def procUnitItems(self):

        return self.procUnitConfObjDict.items()

    def makeXml(self):

        projectElement = Element('Project')
        projectElement.set('id', str(self.id))
        projectElement.set('name', self.name)
        projectElement.set('description', self.description)

        for procUnitConfObj in self.procUnitConfObjDict.values():
            procUnitConfObj.makeXml(projectElement)

        self.projectElement = projectElement

    def writeXml(self, filename=None):

        if filename == None:
            if self.filename:
                filename = self.filename
            else:
                filename = "schain.xml"

        if not filename:
            print "filename has not been defined. Use setFilename(filename) for do it."
            return 0

        abs_file = os.path.abspath(filename)

        if not os.access(os.path.dirname(abs_file), os.W_OK):
            print "No write permission on %s" %os.path.dirname(abs_file)
            return 0

        if os.path.isfile(abs_file) and not(os.access(abs_file, os.W_OK)):
            print "File %s already exists and it could not be overwriten" %abs_file
            return 0

        self.makeXml()

        ElementTree(self.projectElement).write(abs_file, method='xml')

        self.filename = abs_file

        return 1

    def readXml(self, filename = None):

        if not filename:
            print "filename is not defined"
            return 0

        abs_file = os.path.abspath(filename)

        if not os.path.isfile(abs_file):
            print "%s file does not exist" %abs_file
            return 0

        self.projectElement = None
        self.procUnitConfObjDict = {}

        try:
            self.projectElement = ElementTree().parse(abs_file)
        except:
            print "Error reading %s, verify file format" %filename
            return 0

        self.project = self.projectElement.tag

        self.id = self.projectElement.get('id')
        self.name = self.projectElement.get('name')
        self.description = self.projectElement.get('description')

        readUnitElementList = self.projectElement.iter(ReadUnitConf().getElementName())

        for readUnitElement in readUnitElementList:
            readUnitConfObj = ReadUnitConf()
            readUnitConfObj.readXml(readUnitElement)

            if readUnitConfObj.parentId == None:
                readUnitConfObj.parentId = self.id

            self.procUnitConfObjDict[readUnitConfObj.getId()] = readUnitConfObj

        procUnitElementList = self.projectElement.iter(ProcUnitConf().getElementName())

        for procUnitElement in procUnitElementList:
            procUnitConfObj = ProcUnitConf()
            procUnitConfObj.readXml(procUnitElement)

            if procUnitConfObj.parentId == None:
                procUnitConfObj.parentId = self.id

            self.procUnitConfObjDict[procUnitConfObj.getId()] = procUnitConfObj

        self.filename = abs_file

        return 1

    def printattr(self):

        print "Project[%s]: name = %s, description = %s" %(self.id,
                                                              self.name,
                                                              self.description)

        for procUnitConfObj in self.procUnitConfObjDict.values():
            procUnitConfObj.printattr()

    def createObjects(self):

        for procUnitConfObj in self.procUnitConfObjDict.values():
            procUnitConfObj.createObjects(self.plotterQueue)

    def __connect(self, objIN, thisObj):

        thisObj.setInput(objIN.getOutputObj())

    def connectObjects(self):

        for thisPUConfObj in self.procUnitConfObjDict.values():

            inputId = thisPUConfObj.getInputId()

            if int(inputId) == 0:
                continue

            #Get input object
            puConfINObj = self.procUnitConfObjDict[inputId]
            puObjIN = puConfINObj.getProcUnitObj()

            #Get current object
            thisPUObj = thisPUConfObj.getProcUnitObj()

            self.__connect(puObjIN, thisPUObj)

    def __handleError(self, procUnitConfObj, send_email=True):

        import socket

        err = traceback.format_exception(sys.exc_info()[0],
                                         sys.exc_info()[1],
                                         sys.exc_info()[2])

        print "***** Error occurred in %s *****" %(procUnitConfObj.name)
        print "***** %s" %err[-1]

        message = "".join(err)

        sys.stderr.write(message)

        if not send_email:
            return

        subject =  "SChain v%s: Error running %s\n" %(schainpy.__version__, procUnitConfObj.name)

        subtitle = "%s: %s\n" %(procUnitConfObj.getElementName() ,procUnitConfObj.name)
        subtitle += "Hostname: %s\n" %socket.gethostbyname(socket.gethostname())
        subtitle += "Working directory: %s\n" %os.path.abspath("./")
        subtitle += "Configuration file: %s\n" %self.filename
        subtitle += "Time: %s\n" %str(datetime.datetime.now())

        readUnitConfObj = self.getReadUnitObj()
        if readUnitConfObj:
            subtitle += "\nInput parameters:\n"
            subtitle += "[Data path = %s]\n" %readUnitConfObj.path
            subtitle += "[Data type = %s]\n" %readUnitConfObj.datatype
            subtitle += "[Start date = %s]\n" %readUnitConfObj.startDate
            subtitle += "[End date = %s]\n" %readUnitConfObj.endDate
            subtitle += "[Start time = %s]\n" %readUnitConfObj.startTime
            subtitle += "[End time = %s]\n" %readUnitConfObj.endTime

        adminObj = schainpy.admin.SchainNotify()
        adminObj.sendAlert(message=message,
                           subject=subject,
                           subtitle=subtitle,
                           filename=self.filename)

    def isPaused(self):
        return 0

    def isStopped(self):
        return 0

    def runController(self):
        """
        returns 0 when this process has been stopped, 1 otherwise
        """

        if self.isPaused():
            print "Process suspended"

            while True:
                sleep(0.1)

                if not self.isPaused():
                    break

                if self.isStopped():
                    break

            print "Process reinitialized"

        if self.isStopped():
            print "Process stopped"
            return 0

        return 1

    def setFilename(self, filename):

        self.filename = filename

    def setPlotterQueue(self, plotter_queue):

        raise NotImplementedError, "Use schainpy.controller_api.ControllerThread instead Project class"

    def getPlotterQueue(self):

        raise NotImplementedError, "Use schainpy.controller_api.ControllerThread instead Project class"

    def useExternalPlotter(self):

        raise NotImplementedError, "Use schainpy.controller_api.ControllerThread instead Project class"


    def run(self):

        print
        print "*"*60
        print "   Starting SIGNAL CHAIN PROCESSING v%s " %schainpy.__version__
        print "*"*60
        print

        keyList = self.procUnitConfObjDict.keys()
        keyList.sort()

        while(True):

            is_ok = False

            for procKey in keyList:
#                 print "Running the '%s' process with %s" %(procUnitConfObj.name, procUnitConfObj.id)

                procUnitConfObj = self.procUnitConfObjDict[procKey]

                try:
                    sts = procUnitConfObj.run()
                    is_ok = is_ok or sts
                except KeyboardInterrupt:
                    is_ok = False
                    break
                except ValueError, e:
                    sleep(0.5)
                    self.__handleError(procUnitConfObj, send_email=True)
                    is_ok = False
                    break
                except:
                    sleep(0.5)
                    self.__handleError(procUnitConfObj)
                    is_ok = False
                    break

            #If every process unit finished so end process
            if not(is_ok):
#                 print "Every process unit have finished"
                break

            if not self.runController():
                break

        #Closing every process
        for procKey in keyList:
            procUnitConfObj = self.procUnitConfObjDict[procKey]
            procUnitConfObj.close()

        print "Process finished"

    def start(self, filename=None):

        self.writeXml(filename)
        self.createObjects()
        self.connectObjects()
        self.run()
