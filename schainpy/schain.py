'''
Created on September , 2012
@author: 
'''
from xml.etree.ElementTree import Element, SubElement, ElementTree
from xml.etree import ElementTree as ET
from xml.dom import minidom

import sys
import datetime
from model.jrodataIO import *
from model.jroprocessing import *

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
    type = None
    
    ELEMENTNAME = 'Parameter'
    
    def __init__(self):
        
        self.type = 'str'
    
    def getElementName(self):
        
        return self.ELEMENTNAME
    
    def getValue(self):
        
        if self.type == 'list':
            strList = self.value.split(',')
            return strList
        
        if self.type == 'intlist':
            strList = self.value.split(',')
            intList = [int(x) for x in strList]
            return intList
        
        if self.type == 'floatlist':
            strList = self.value.split(',')
            floatList = [float(x) for x in strList]
            return floatList
        
        if self.type == 'date':
            strList = self.value.split('/')
            intList = [int(x) for x in strList]
            date = datetime.date(intList[0], intList[1], intList[2])
            return date
        
        if self.type == 'time':
            strList = self.value.split(':')
            intList = [int(x) for x in strList]
            time = datetime.time(intList[0], intList[1], intList[2])
            return time
                
        func = eval(self.type)
            
        return func(self.value)
        
    def setup(self, id, name, value, type='str'):
        
        self.id = id
        self.name = name
        self.value = str(value)
        self.type = type
    
    def makeXml(self, opElement):
        
        parmElement = SubElement(opElement, self.ELEMENTNAME)
        parmElement.set('id', str(self.id))
        parmElement.set('name', self.name)
        parmElement.set('value', self.value)
        parmElement.set('type', self.type)
    
    def readXml(self, parmElement):
        
        self.id = parmElement.get('id')
        self.name = parmElement.get('name')
        self.value = parmElement.get('value')
        self.type = parmElement.get('type')
    
    def printattr(self):
        
        print "Parameter[%s]: name = %s, value = %s, type = %s" %(self.id, self.name, self.value, self.type)

class OperationConf():
    
    id = None
    name = None
    priority = None
    type = None
    
    parmConfObjList = []
    
    ELEMENTNAME = 'Operation'
    
    def __init__(self):
        
        id = 0
        name = None
        priority = None
        type = 'self'
    
    
    def __getNewId(self):
        
        return int(self.id)*10 + len(self.parmConfObjList) + 1
    
    def getElementName(self):
        
        return self.ELEMENTNAME
    
    def getParameterObjList(self):
        
        return self.parmConfObjList
    
    def setup(self, id, name, priority, type):
        
        self.id = id
        self.name = name
        self.type = type
        self.priority = priority
        
        self.parmConfObjList = []
        
    def addParameter(self, name, value, type='str'):
        
        id = self.__getNewId()
        
        parmConfObj = ParameterConf()
        parmConfObj.setup(id, name, value, type)
        
        self.parmConfObjList.append(parmConfObj)
        
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
        
        self.parmConfObjList = []
        
        parmElementList = opElement.getiterator(ParameterConf().getElementName())
        
        for parmElement in parmElementList:
            parmConfObj = ParameterConf()
            parmConfObj.readXml(parmElement)
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
        
        if self.type == 'other':
            className = eval(self.name)
            opObj = className()
        
        return opObj
            
class ProcUnitConf():
    
    id = None
    name = None
    type = None
    inputId = None
    
    opConfObjList = []
    
    procUnitObj = None
    opObjList = []
    
    ELEMENTNAME = 'ProcUnit'
    
    def __init__(self):
        
        self.id = None
        self.type = None
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
        
        return str(self.id)
    
    def getInputId(self):
        
        return str(self.inputId)
    
    def getOperationObjList(self):
        
        return self.opConfObjList
    
    def getProcUnitObj(self):
        
        return self.procUnitObj
    
    def setup(self, id, name, type, inputId):
        
        self.id = id
        self.name = name
        self.type = type
        self.inputId = inputId
        
        self.opConfObjList = []
        
        self.addOperation(name='init', optype='self')
        
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
        upElement.set('type', self.type)
        upElement.set('inputId', str(self.inputId))
        
        for opConfObj in self.opConfObjList:
            opConfObj.makeXml(upElement)
    
    def readXml(self, upElement):
        
        self.id = upElement.get('id')
        self.name = upElement.get('name')
        self.type = upElement.get('type')
        self.inputId = upElement.get('inputId')
        
        self.opConfObjList = []
        
        opElementList = upElement.getiterator(OperationConf().getElementName())
        
        for opElement in opElementList:
            opConfObj = OperationConf()
            opConfObj.readXml(opElement)
            self.opConfObjList.append(opConfObj)
    
    def printattr(self):
        
        print "%s[%s]: name = %s, type = %s, inputId = %s" %(self.ELEMENTNAME,
                                                             self.id,
                                                             self.name,
                                                             self.type,
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
        
        for opConfObj in self.opConfObjList:
            kwargs = {}
            for parmConfObj in opConfObj.getParameterObjList():
                kwargs[parmConfObj.name] = parmConfObj.getValue()
                    
            self.procUnitObj.call(opConfObj, **kwargs)
            

    
class ReadUnitConf(ProcUnitConf):
    
    
    path = None
    startDate = None
    endDate = None
    startTime = None
    endTime = None
    online = None
    expLabel = None
    delay = None
    
    ELEMENTNAME = 'ReadUnit'
    
    def __init__(self):
        
        self.id = None
        self.type = None
        self.name = None
        self.inputId = 0
        
        self.opConfObjList = []
        self.opObjList = []
    
    def getElementName(self):
        
        return self.ELEMENTNAME
        
    def setup(self, id, name, type, path, startDate, endDate, startTime, endTime, online=0, expLabel='', delay=60):
        
        self.id = id
        self.name = name
        self.type = type
        
        self.path = path
        self.startDate = startDate
        self.endDate = endDate
        self.startTime = startTime
        self.endTime = endTime
        self.online = online
        self.expLabel = expLabel
        self.delay = delay
        
        self.addRunOperation()
    
    def addRunOperation(self):
        
        opObj = self.addOperation(name = 'run', optype = 'self')
        
        opObj.addParameter(name='path'     , value=self.path, type='str')
        opObj.addParameter(name='startDate' , value=self.startDate, type='date')
        opObj.addParameter(name='endDate'   , value=self.endDate, type='date')
        opObj.addParameter(name='startTime' , value=self.startTime, type='time')
        opObj.addParameter(name='endTime'   , value=self.endTime, type='time')
        opObj.addParameter(name='expLabel'  , value=self.expLabel, type='str')
        opObj.addParameter(name='online'  , value=self.online, type='bool')
        opObj.addParameter(name='delay'  , value=self.delay, type='float')
                
        return opObj
    
    
class Controller():
    
    id = None
    name = None
    description = None
#    readUnitConfObjList = None
    procUnitConfObjDict = None
    
    ELEMENTNAME = 'Controller'
    
    def __init__(self):
        
        self.id = None
        self.name = None
        self.description = None
        
#        self.readUnitConfObjList = []
        self.procUnitConfObjDict = {}
        
    def __getNewId(self):
        
        id = int(self.id)*10 + len(self.procUnitConfObjDict) + 1
        
        return str(id)
    
    def getElementName(self):
        
        return self.ELEMENTNAME
    
    def setup(self, id, name, description):
        
        self.id = id
        self.name = name
        self.description = description
    
    def addReadUnit(self, type, path, startDate='', endDate='', startTime='', endTime='', online=0, expLabel='', delay=60):
        
        id = self.__getNewId()
        name = '%sReader' %(type)
        
        readUnitConfObj = ReadUnitConf()
        readUnitConfObj.setup(id, name, type, path, startDate, endDate, startTime, endTime, online, expLabel, delay)
        
        self.procUnitConfObjDict[readUnitConfObj.getId()] = readUnitConfObj
        
        return readUnitConfObj
    
    def addProcUnit(self, type, inputId):
        
        id = self.__getNewId()
        name = '%sProc' %(type)
        
        procUnitConfObj = ProcUnitConf()
        procUnitConfObj.setup(id, name, type, inputId)
        
        self.procUnitConfObjDict[procUnitConfObj.getId()] = procUnitConfObj
        
        return procUnitConfObj
    
    def makeXml(self):    
        
        projectElement = Element('Controller')
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
        
        print prettify(self.projectElement)
        
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
            
            self.procUnitConfObjDict[readUnitConfObj.getId()] = readUnitConfObj
        
        procUnitElementList = self.projectElement.getiterator(ProcUnitConf().getElementName())
        
        for procUnitElement in procUnitElementList:
            procUnitConfObj = ProcUnitConf()
            procUnitConfObj.readXml(procUnitElement)
            
            self.procUnitConfObjDict[procUnitConfObj.getId()] = procUnitConfObj
               
    def printattr(self):
        
        print "Controller[%s]: name = %s, description = %s" %(self.id,
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
    
    def __connect(self, objIN, obj):
        
        obj.setInput(objIN.getOutput())
    
    def connectObjects(self):
        
        for puConfObj in self.procUnitConfObjDict.values():
            
            inputId = puConfObj.getInputId()
            
            if int(inputId) == 0:
                continue
            
            puConfINObj = self.procUnitConfObjDict[inputId]
            
            puObj = puConfObj.getProcUnitObj()
            puINObj = puConfINObj.getProcUnitObj()
            
            self.__connect(puINObj, puObj)
    
    def run(self):
        
#        for readUnitConfObj in self.readUnitConfObjList:
#            readUnitConfObj.run()
        while(True):
            for procUnitConfObj in self.procUnitConfObjDict.values():
                procUnitConfObj.run()
            
if __name__ == '__main__':
    
    desc = "Segundo Test"
    filename = "schain.xml"
    
    controllerObj = Controller()
    
    controllerObj.setup(id = '191', name='test01', description=desc)
    
    readUnitConfObj = controllerObj.addReadUnit(type='Voltage',
                                                path='/home/roj-idl71/Data/RAWDATA/Meteors',
                                                startDate='2012/01/01',
                                                endDate='2012/12/31',
                                                startTime='00:00:00',
                                                endTime='23:59:59',
                                                online=0)
    
    procUnitConfObj1 = controllerObj.addProcUnit(type='Voltage', inputId=readUnitConfObj.getId())
    
    procUnitConfObj2 = controllerObj.addProcUnit(type='Voltage', inputId=procUnitConfObj1.getId())
    
    opObj11 = procUnitConfObj1.addOperation(name='selectChannels')
    opObj11.addParameter(name='channelList', value='1,2', type='intlist')
    
#    opObj12 = procUnitConfObj1.addOperation(name='decoder')
#    opObj12.addParameter(name='ncode', value='2', type='int')
#    opObj12.addParameter(name='nbauds', value='8', type='int')
#    opObj12.addParameter(name='code0', value='001110011', type='int')
#    opObj12.addParameter(name='code1', value='001110011', type='int')
    
    opObj21 = procUnitConfObj2.addOperation(name='CohInt', optype='other')
    opObj21.addParameter(name='nCohInt', value='10', type='int')
    
    
    print "Escribiendo el archivo XML"
    
    controllerObj.writeXml(filename)
    
    print "Leyendo el archivo XML"
    controllerObj.readXml(filename)
    #controllerObj.printattr()
    
    controllerObj.createObjects()
    controllerObj.connectObjects()
    controllerObj.run()
    
    