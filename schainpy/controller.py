'''
Created on September , 2012
@author: 
'''
from xml.etree.ElementTree import Element, SubElement
from xml.etree import ElementTree as ET
from xml.dom import minidom

#import datetime
from model import *

try:
    from gevent import sleep
except:
    from time import sleep
    
import ast

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

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
        
        if format == 'str':
            self.__formated_value = str(value)
            return self.__formated_value
        
        if value == '':
            raise ValueError, "%s: This parameter value is empty" %self.name
        
        if format == 'bool':
            value = int(value)
            
        if format == 'list':
            strList = value.split(',')
            
            self.__formated_value = strList
            
            return self.__formated_value
        
        if format == 'intlist':
            """
            Example:
                value = (0,1,2)
            """
            value = value.replace('(', '')
            value = value.replace(')', '')
            
            value = value.replace('[', '')
            value = value.replace(']', '')
            
            strList = value.split(',')
            intList = [int(x) for x in strList]
            
            self.__formated_value = intList
            
            return self.__formated_value
        
        if format == 'floatlist':
            """
            Example:
                value = (0.5, 1.4, 2.7)
            """
            
            value = value.replace('(', '')
            value = value.replace(')', '')
            
            value = value.replace('[', '')
            value = value.replace(']', '')
            
            strList = value.split(',')
            floatList = [float(x) for x in strList]
            
            self.__formated_value = floatList
            
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

            value = value.replace('(', '')
            value = value.replace(')', '')
            
            value = value.replace('[', '')
            value = value.replace(']', '')
            
            strList = value.split(',')
            intList = [int(item) for item in strList]
            pairList = []
            for i in range(len(intList)/2):
                pairList.append((intList[i*2], intList[i*2 + 1]))
            
            self.__formated_value = pairList
            
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
        
        format_func = eval(format)
        
        self.__formated_value = format_func(value)
        
        return self.__formated_value

    def updateId(self, new_id):
        
        self.id = str(new_id)
             
    def setup(self, id, name, value, format='str'):
        
        self.id = str(id)
        self.name = name
        self.value = str(value)
        self.format = str.lower(format)
        
    def update(self, name, value, format='str'):
        
        self.name = name
        self.value = str(value)
        self.format = format
    
    def makeXml(self, opElement):
        
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

    def getParameterObjfromValue(self,parameterValue):
        for parmConfObj in self.parmConfObjList:
             
            if parmConfObj.getValue() != parameterValue:
                continue
             
            return parmConfObj.getValue()
         
        return None
    
    def getParameterValue(self, parameterName):
        
        parameterObj = self.getParameterObj(parameterName)
        value = parameterObj.getValue()
        
        return value
        
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
        parmConfObj.setup(id, name, value, format)
        
        self.parmConfObjList.append(parmConfObj)
        
        return parmConfObj
    
    def changeParameter(self, name, value, format='str'):
        
        parmConfObj = self.getParameterObj(name)
        parmConfObj.update(name, value, format)
        
        return parmConfObj
    
    def makeXml(self, upElement):
        
        opElement = SubElement(upElement, self.ELEMENTNAME)
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
        
        parmElementList = opElement.getiterator(ParameterConf().getElementName())
        
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
    
    def createObject(self):
        
        if self.type == 'self':
            raise ValueError, "This operation type cannot be created"
        
        if self.type == 'external' or self.type == 'other':
            className = eval(self.name)
            opObj = className()
        
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
    
    def getOpObjfromParamValue(self,value=None):
        
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
    
    def makeXml(self, procUnitElement):
        
        upElement = SubElement(procUnitElement, self.ELEMENTNAME)
        upElement.set('id', str(self.id))
        upElement.set('name', self.name)
        upElement.set('datatype', self.datatype)
        upElement.set('inputId', str(self.inputId))
        
        for opConfObj in self.opConfObjList:
            opConfObj.makeXml(upElement)
    
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
        
        opElementList = upElement.getiterator(OperationConf().getElementName())
        
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
    
    def createObjects(self):
        
        className = eval(self.name)
        procUnitObj = className()
        
        for opConfObj in self.opConfObjList:
            
            if opConfObj.type == 'self':
                continue
            
            opObj = opConfObj.createObject()
            
            self.opObjDict[opConfObj.id] = opObj
            procUnitObj.addOperation(opObj, opConfObj.id)
            
        self.procUnitObj = procUnitObj
        
        return procUnitObj
    
    def run(self):
        
        finalSts = False
        
        for opConfObj in self.opConfObjList:
            
            kwargs = {}
            for parmConfObj in opConfObj.getParameterObjList():
                if opConfObj.name == 'run' and parmConfObj.name == 'datatype':
                    continue
                    
                kwargs[parmConfObj.name] = parmConfObj.getValue()
            
            #print "\tRunning the '%s' operation with %s" %(opConfObj.name, opConfObj.id)
            sts = self.procUnitObj.call(opType = opConfObj.type,
                                        opName = opConfObj.name,
                                        opId = opConfObj.id,
                                         **kwargs)
            finalSts = finalSts or sts
        
        return finalSts

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
        
    def setup(self, id, name, datatype, path, startDate="", endDate="", startTime="", endTime="", parentId=None, **kwargs):

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
        
        self.path = path
        self.startDate = startDate
        self.endDate = endDate
        self.startTime = startTime
        self.endTime = endTime
        
        self.inputId = '0'
        self.parentId = parentId
        
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
        
    def addRunOperation(self, **kwargs):
        
        opObj = self.addOperation(name = 'run', optype = 'self')
        
        opObj.addParameter(name='datatype' , value=self.datatype, format='str')
        opObj.addParameter(name='path'     , value=self.path, format='str')
        opObj.addParameter(name='startDate' , value=self.startDate, format='date')
        opObj.addParameter(name='endDate'   , value=self.endDate, format='date')
        opObj.addParameter(name='startTime' , value=self.startTime, format='time')
        opObj.addParameter(name='endTime'   , value=self.endTime, format='time')
        
        for key, value in kwargs.items():
            opObj.addParameter(name=key, value=value, format=type(value).__name__)
            
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
    
class Project():
    
    id = None
    name = None
    description = None
#    readUnitConfObjList = None
    procUnitConfObjDict = None
    
    ELEMENTNAME = 'Project'
    
    def __init__(self, control=None, dataq=None):
        
        self.id = None
        self.name = None
        self.description = None

        self.procUnitConfObjDict = {}
        
        #global data_q
        #data_q = dataq
        
        if control==None:
            control = {'stop':False,'pause':False}
        
        self.control = control
        
    def __getNewId(self):
        
        id = int(self.id)*10 + len(self.procUnitConfObjDict) + 1
        
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
        
    def addReadUnit(self, datatype=None, name=None, **kwargs):
            
        idReadUnit = self.__getNewId()
        
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
    
    def getProcUnitObj(self, id):
        
        return self.procUnitConfObjDict[id]

    def getProcUnitObjByName(self, name):
        
        for obj in self.procUnitConfObjDict.values():
            if obj.name == name:
                return obj
               
        return None
     
    def makeXml(self):    
        
        projectElement = Element('Project')
        projectElement.set('id', str(self.id))
        projectElement.set('name', self.name)
        projectElement.set('description', self.description)
        
#        for readUnitConfObj in self.readUnitConfObjList:
#            readUnitConfObj.makeXml(projectElement)
            
        for procUnitConfObj in self.procUnitConfObjDict.values():
            procUnitConfObj.makeXml(projectElement)
            
        self.projectElement = projectElement
    
    def writeXml(self, filename):
        
        self.makeXml()
        
        #print prettify(self.projectElement)
        
        ElementTree(self.projectElement).write(filename, method='xml')

    def readXml(self, filename):
        
        #tree = ET.parse(filename)
        self.projectElement = None
#        self.readUnitConfObjList = []
        self.procUnitConfObjDict = {}
        
        self.projectElement = ElementTree().parse(filename)
        
        self.project = self.projectElement.tag
        
        self.id = self.projectElement.get('id')
        self.name = self.projectElement.get('name')
        self.description = self.projectElement.get('description')       
        
        readUnitElementList = self.projectElement.getiterator(ReadUnitConf().getElementName())
        
        for readUnitElement in readUnitElementList:
            readUnitConfObj = ReadUnitConf()
            readUnitConfObj.readXml(readUnitElement)
            
            if readUnitConfObj.parentId == None:
                readUnitConfObj.parentId = self.id
            
            self.procUnitConfObjDict[readUnitConfObj.getId()] = readUnitConfObj
        
        procUnitElementList = self.projectElement.getiterator(ProcUnitConf().getElementName())
        
        for procUnitElement in procUnitElementList:
            procUnitConfObj = ProcUnitConf()
            procUnitConfObj.readXml(procUnitElement)
            
            if procUnitConfObj.parentId == None:
                procUnitConfObj.parentId = self.id
                
            self.procUnitConfObjDict[procUnitConfObj.getId()] = procUnitConfObj
               
    def printattr(self):
        
        print "Project[%s]: name = %s, description = %s" %(self.id,
                                                              self.name,
                                                              self.description)
        
#        for readUnitConfObj in self.readUnitConfObjList:
#            readUnitConfObj.printattr()
        
        for procUnitConfObj in self.procUnitConfObjDict.values():
            procUnitConfObj.printattr()
    
    def createObjects(self):
        
#        for readUnitConfObj in self.readUnitConfObjList:
#            readUnitConfObj.createObjects()
        
        for procUnitConfObj in self.procUnitConfObjDict.values():
            procUnitConfObj.createObjects()
    
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
    
    def run(self):
        
#        for readUnitConfObj in self.readUnitConfObjList:
#            readUnitConfObj.run()
        print
        print "*"*40
        print "   Starting SIGNAL CHAIN PROCESSING  "
        print "*"*40
        print
        
        keyList = self.procUnitConfObjDict.keys()
        keyList.sort()
            
        while(True):
            
            finalSts = False
            
            for procKey in keyList:
#                 print "Running the '%s' process with %s" %(procUnitConfObj.name, procUnitConfObj.id)
                
                procUnitConfObj = self.procUnitConfObjDict[procKey]
                sts = procUnitConfObj.run()
                finalSts = finalSts or sts
            
            #If every process unit finished so end process
            if not(finalSts):
                print "Every process unit have finished"
                break

            if self.control['pause']:
                print "Process suspended"
                
                while True:    
                    sleep(0.1)
                    
                    if not self.control['pause']:
                        break
                    
                    if self.control['stop']:
                        break
                print "Process reinitialized"
            
            if self.control['stop']:
                print "Process stopped"
                break
                
        #Closing every process
        for procKey in keyList:
            procUnitConfObj = self.procUnitConfObjDict[procKey]
            procUnitConfObj.close()
            
        print "Process finished"
                
    def start(self, filename):
        
        self.writeXml(filename)
        self.readXml(filename)
    
        self.createObjects()
        self.connectObjects()
        self.run()

class ControllerThread(threading.Thread, Project):
    
    def __init__(self, filename):
        
        threading.Thread.__init__(self)
        Project.__init__(self)
        
        self.setDaemon(True)
        
        self.filename = filename
        self.control = {'stop':False, 'pause':False}
    
    def stop(self):
        self.control['stop'] = True
        
    def pause(self):
        self.control['pause'] = not(self.control['pause'])

    def run(self):
        self.control['stop'] = False
        self.control['pause'] = False
        
        self.readXml(self.filename)
        self.createObjects()
        self.connectObjects()
        Project.run(self)
        
if __name__ == '__main__':
    
    desc = "Segundo Test"
    filename = "schain.xml"
    
    controllerObj = Project()
    
    controllerObj.setup(id = '191', name='test01', description=desc)
    
    readUnitConfObj = controllerObj.addReadUnit(datatype='Voltage',
                                                path='data/rawdata/',
                                                startDate='2011/01/01',
                                                endDate='2012/12/31',
                                                startTime='00:00:00',
                                                endTime='23:59:59',
                                                online=1,
                                                walk=1)
    
#    opObj00 = readUnitConfObj.addOperation(name='printInfo')
    
    procUnitConfObj0 = controllerObj.addProcUnit(datatype='Voltage', inputId=readUnitConfObj.getId())
    
    opObj10 = procUnitConfObj0.addOperation(name='selectChannels')
    opObj10.addParameter(name='channelList', value='3,4,5', format='intlist')

    opObj10 = procUnitConfObj0.addOperation(name='selectHeights')
    opObj10.addParameter(name='minHei', value='90', format='float')
    opObj10.addParameter(name='maxHei', value='180', format='float')
    
    opObj12 = procUnitConfObj0.addOperation(name='CohInt', optype='external')
    opObj12.addParameter(name='n', value='10', format='int')
    
    procUnitConfObj1 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObj0.getId())
    procUnitConfObj1.addParameter(name='nFFTPoints', value='32', format='int')
#    procUnitConfObj1.addParameter(name='pairList', value='(0,1),(0,2),(1,2)', format='')
    
    
    opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='external')
    opObj11.addParameter(name='idfigure', value='1', format='int')
    opObj11.addParameter(name='wintitle', value='SpectraPlot0', format='str')
    opObj11.addParameter(name='zmin', value='40', format='int')
    opObj11.addParameter(name='zmax', value='90', format='int')
    opObj11.addParameter(name='showprofile', value='1', format='int')  

#    opObj11 = procUnitConfObj1.addOperation(name='CrossSpectraPlot', optype='external')
#    opObj11.addParameter(name='idfigure', value='2', format='int')
#    opObj11.addParameter(name='wintitle', value='CrossSpectraPlot', format='str')
#    opObj11.addParameter(name='zmin', value='40', format='int')
#    opObj11.addParameter(name='zmax', value='90', format='int') 
            
            
#    procUnitConfObj2 = controllerObj.addProcUnit(datatype='Voltage', inputId=procUnitConfObj0.getId())
#  
#    opObj12 = procUnitConfObj2.addOperation(name='CohInt', optype='external')
#    opObj12.addParameter(name='n', value='2', format='int')
#    opObj12.addParameter(name='overlapping', value='1', format='int')
#
#    procUnitConfObj3 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObj2.getId())
#    procUnitConfObj3.addParameter(name='nFFTPoints', value='32', format='int')
#    
#    opObj11 = procUnitConfObj3.addOperation(name='SpectraPlot', optype='external')
#    opObj11.addParameter(name='idfigure', value='2', format='int')
#    opObj11.addParameter(name='wintitle', value='SpectraPlot1', format='str')
#    opObj11.addParameter(name='zmin', value='40', format='int')
#    opObj11.addParameter(name='zmax', value='90', format='int')
#    opObj11.addParameter(name='showprofile', value='1', format='int') 

#    opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='external')
#    opObj11.addParameter(name='idfigure', value='10', format='int')
#    opObj11.addParameter(name='wintitle', value='RTI', format='str')
##    opObj11.addParameter(name='xmin', value='21', format='float')
##    opObj11.addParameter(name='xmax', value='22', format='float')
#    opObj11.addParameter(name='zmin', value='40', format='int')
#    opObj11.addParameter(name='zmax', value='90', format='int')
#    opObj11.addParameter(name='showprofile', value='1', format='int')
#    opObj11.addParameter(name='timerange', value=str(60), format='int')
    
#    opObj10 = procUnitConfObj1.addOperation(name='selectChannels')
#    opObj10.addParameter(name='channelList', value='0,2,4,6', format='intlist')
#    
#    opObj12 = procUnitConfObj1.addOperation(name='IncohInt', optype='external')
#    opObj12.addParameter(name='n', value='2', format='int')
#
#    opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='external')
#    opObj11.addParameter(name='idfigure', value='2', format='int')
#    opObj11.addParameter(name='wintitle', value='SpectraPlot10', format='str')
#    opObj11.addParameter(name='zmin', value='70', format='int')
#    opObj11.addParameter(name='zmax', value='90', format='int')
#
#    opObj10 = procUnitConfObj1.addOperation(name='selectChannels')
#    opObj10.addParameter(name='channelList', value='2,6', format='intlist')
#    
#    opObj12 = procUnitConfObj1.addOperation(name='IncohInt', optype='external')
#    opObj12.addParameter(name='n', value='2', format='int')
#
#    opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='external')
#    opObj11.addParameter(name='idfigure', value='3', format='int')
#    opObj11.addParameter(name='wintitle', value='SpectraPlot10', format='str')
#    opObj11.addParameter(name='zmin', value='70', format='int')
#    opObj11.addParameter(name='zmax', value='90', format='int')
    
          
#    opObj12 = procUnitConfObj1.addOperation(name='decoder')
#    opObj12.addParameter(name='ncode', value='2', format='int')
#    opObj12.addParameter(name='nbauds', value='8', format='int')
#    opObj12.addParameter(name='code0', value='001110011', format='int')
#    opObj12.addParameter(name='code1', value='001110011', format='int')  
  


#    procUnitConfObj2 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObj1.getId())
#    
#    opObj21 = procUnitConfObj2.addOperation(name='IncohInt', optype='external')
#    opObj21.addParameter(name='n', value='2', format='int')
#    
#    opObj11 = procUnitConfObj2.addOperation(name='SpectraPlot', optype='external')
#    opObj11.addParameter(name='idfigure', value='4', format='int')
#    opObj11.addParameter(name='wintitle', value='SpectraPlot OBJ 2', format='str')
#    opObj11.addParameter(name='zmin', value='70', format='int')
#    opObj11.addParameter(name='zmax', value='90', format='int')
      
    print "Escribiendo el archivo XML"
    
    controllerObj.writeXml(filename)
    
    print "Leyendo el archivo XML"
    controllerObj.readXml(filename)
    #controllerObj.printattr()
    
    controllerObj.createObjects()
    controllerObj.connectObjects()
    controllerObj.run()
    
    