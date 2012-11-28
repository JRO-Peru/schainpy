'''
Created on September , 2012
@author: 
'''
from xml.etree.ElementTree import Element, SubElement, ElementTree
from xml.etree import ElementTree as ET
from xml.dom import minidom

import sys

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

#def save(a, b):
#    
#    nameP = "Alexnder"
#    descripcion = self.projectWindow.Text()
#    id = 1
#    x = self.data.projectWindow.cmbbox.value()
#    
#    projectObj = Controller(id, name, description)
#    
#    projectObj.setup(id, name, description)

class Controller():
    
    id = None
    name = None
    description = None
    readBranchObjList = None
    procBranchObjList = None
    
    def __init__(self):
        
#        self.id = id
#        self.name = name
#        self.description = description
        
        self.readBranchObjList = []
        self.procBranchObjList = []
    
    def setParms(self, id, name, description):
        
        self.id = id
        self.name = name
        self.description = description
    
    def addReadBranch(self, dpath, dataformat, readMode, startDate='', endDate='', startTime='', endTime=''):
        
        id = len(self.readBranchObjList) + 1
        
        readBranchObj = ReadBranch()
        readBranchObj.setup(id, dpath, dataformat, readMode, startDate, endDate, startTime, endTime)
        
        self.readBranchObjList.append(readBranchObj)
        
        return readBranchObj
    
    def addProcBranch(self, name):
        
        id = len(self.procBranchObjList) + 1
        
        procBranchObj = ProcBranch()
        procBranchObj.setup(id, name)
        
        self.procBranchObjList.append(procBranchObj)
        
        return procBranchObj
    
    def makeXml(self):    
        
        projectElement = Element('Controller')
        projectElement.set('id', str(self.id))
        projectElement.set('name', self.name)
        #projectElement.set('description', self.description)
        
        se = SubElement(projectElement, 'description',description=self.description)#ESTO ES LO ULTIMO QUE SE TRABAJO
        #se.text = self.description                    #ULTIMA MODIFICACION PARA SACAR UN SUB ELEMENT  
        
        for readBranchObj in self.readBranchObjList:
            readBranchObj.makeXml(projectElement)
            
        for procBranchObj in self.procBranchObjList:
            procBranchObj.makeXml(projectElement)
            
        self.projectElement = projectElement
    
    def writeXml(self, filename):
        
        self.makeXml()
        ElementTree(self.projectElement).write(filename, method='xml')
        print prettify(self.projectElement)

    def readXml(self, filename):
        
        #tree = ET.parse(filename)
        self.projectElement = None
        self.readBranchObjList = None
        self.procBranchObjList = None
        
        self.projectElement = ElementTree().parse(filename)
        
        self.project = self.projectElement.tag
        
        self.id = self.projectElement.get('id')
        self.name = self.projectElement.get('name')      
        
        self.readBranchObjList = []
        
        readBranchElementList = self.projectElement.getiterator('readBranch')
        
        for readBranchElement in readBranchElementList:
            readBrachObj = ReadBranch()
            readBrachObj.readXml(readBranchElement)
            self.readBranchObjList.append(readBranchObj)
        
        self.procBranchObjList = []
        
        procBranchElementList = self.projectElement.getiterator('procBranch')
        
        for procBranchElement in procBranchElementList:
            procBranchObj = ProcBranch()
            procBranchObj.readXml(procBranchElement)
            self.procBranchObjList.append(procBranchObj)
#    
class ReadBranch():
    
    id = None
#    dpath = None
#    dataformat = None
#    readMode = None
#    startDate = None
#    endDate = None
#    startTime = None
#    endTime = None
    
    parmObjList = []
    
    def __init__(self):
        
        self.parmObjList = []
        
    def setup(self, id, dpath, dataformat, readMode, startDate, endDate, startTime, endTime):
        
        self.id = id
        self.dpath = dpath
        self.dataformat = dataformat
        self.readMode = readMode
        self.startDate = startDate
        self.endDate = endDate
        self.startTime = startTime
        self.endTime = endTime
    
    def addParameter(self, name, value):
        
        id = len(self.parmObjList) + 1
        
        parmObj = ParameterConf()
        parmObj.setup(id, name, value)
        
        self.parmObjList.append(parmObj)
        
        return parmObj
    
    def makeXml(self, projectElement):
        
        readBranchElement = SubElement(projectElement, 'readBranch')
        readBranchElement.set('id', str(self.id))
            
        self.addParameter(name='dpath'     , value=self.dpath)
        self.addParameter(name='dataformat', value=self.dataformat)
        self.addParameter(name='startDate' , value=self.startDate)
        self.addParameter(name='endDate'   , value=self.endDate)
        self.addParameter(name='startTime' , value=self.startTime)
        self.addParameter(name='endTime'   , value=self.endTime)
        self.addParameter(name='readMode'  , value=str(self.readMode))
        
        for parmObj in self.parmObjList:
            parmObj.makeXml(readBranchElement)
            
    def readXml(self, readBranchElement):
        
        self.id = readBranchElement.get('id')
        
        self.parmObjList = []
        
        parmElementList = readBranchElement.getiterator('Parameter')
        
        for parmElement in parmElementList:
            parmObj = Parameter()
            parmObj.readXml(parmElement)
            self.parmObjList.append(parmObj)
        
    
class ProcBranch():
    
    id = None
    name = None
    
    upObjList = None
    
    def __init__(self):
        pass
    
    def setup(self, id, name):
        
        self.id = id
        self.name = name
        
        self.upObjList = []
        
    def addUP(self, name, type):
        
        id = len(self.upObjList) + 1
        
        upObj = UPConf()
        upObj.setup(id, name, type)
        
        self.upObjList.append(upObj)
        
        return upObj
          
    def makeXml(self, projectElement):
        
        procBranchElement = SubElement(projectElement, 'procBranch')
        procBranchElement.set('id', str(self.id))
        procBranchElement.set('name', self.name)
        
        for upObj in self.upObjList:
            upObj.makeXml(procBranchElement)
    
    def readXml(self, procBranchElement):
        
        self.id = procBranchElement.get('id')
        self.name = procBranchElement.get('name')
        
        self.upObjList = []
        
        upElementList = procBranchElement.getiterator('UP')
        
        for upElement in upElementList:
            upObj = UPConf()
            #upObj.readXml(upElement)
            self.upObjList.append(upObj)
    
class UPConf():
    
    id = None
    name = None
    type = None
    
    opObjList = []
    
    def __init__(self):
        pass
    
    def setup(self, id, name, type):
        
        self.id = id
        self.name = name
        self.type = type
        
        self.opObjList = []
        
    def addOperation(self, name, priority, type='self'):
        
        id = len(self.opObjList) + 1
        
        opObj = OperationConf()
        opObj.setup(id, name, priority, type)
        
        self.opObjList.append(opObj)
        
        return opObj
    
    def makeXml(self, procBranchElement):
        
        upElement = SubElement(procBranchElement, 'UP')
        upElement.set('id', str(self.id))
        upElement.set('name', self.name)
        upElement.set('type', self.type)
        
        for opObj in self.opObjList:
            opObj.makeXml(upElement)
    
    def readXml(self, upElement):
        
        self.id = upElement.get('id')
        self.name = upElement.get('name')
        self.type = upElement.get('type')
        
        opElementList = upElement.getiterator('Operation')
        
        for opElement in opElementList:
            pass
        
    def getOperationObjList(self):
        
        return self.opObjList
    
class OperationConf():
    
    id = 0
    name = None
    priority = None
    type = 'self'
    
    parmObjList = []
    
    def __init__(self):
        pass
    
    def setup(self, id, name, priority, type):
        
        self.id = id
        self.name = name
        self.priority = priority
        self.type = type
        
        self.parmObjList = []
        
    def addParameter(self, name, value):
        
        id = len(self.parmObjList) + 1
        
        parmObj = ParameterConf()
        parmObj.setup(id, name, value)
        
        self.parmObjList.append(parmObj)
        
        return parmObj
    
    def makeXml(self, upElement):
        
        opElement = SubElement(upElement, 'Operation')
        opElement.set('id', str(self.id))
        opElement.set('name', self.name)
        opElement.set('priority', str(self.priority))
        
        for parmObj in self.parmObjList:
            parmObj.makeXml(opElement)
            
    def readXml(self, opElement):
        
        self.id = opElement.get('id')
        self.name = opElement.get('name')
        self.type = opElement.get('type')
        
        parmElementList = opElement.getiterator('Parameter')
        
        for parmElement in parmElementList:
            pass
        
    def getParameterObjList(self):
        
        return self.parmObjList
    
class ParameterConf():
    
    id = None
    name = None
    value = None
    
    def __init__(self):
        pass
    
    def setup(self, id, name, value):
        
        self.id = id
        self.name = name
        self.value = value
    
    def makeXml(self, opElement):
        
        parmElement = SubElement(opElement, 'Parameter')
        parmElement.set('name', self.name)
        parmElement.set('value', self.value)
    
    def readXml(self, parmElement):
        
        self.id = parmElement.get('id')
        self.name = parmElement.get('name')
        self.value = parmElement.get('value')
        
if __name__ == '__main__':
    
    desc = "Este es un test"
    filename = "test.xml"
    
    projectObj = Controller()
    
    projectObj.setParms(id = '11', name='test01', description=desc)
    
    readBranchObj = projectObj.addReadBranch(dpath='mydata', dataformat='rawdata', readMode=0, startDate='1', endDate='3', startTime='4', endTime='5')
    
    procBranchObj = projectObj.addProcBranch(name='Branch1')
    
    procBranchObj1 = projectObj.addProcBranch(name='Branch2')
    upObj1 = procBranchObj.addUP(name='UP1', type='Voltage')
    upObj2 = procBranchObj.addUP(name='UP2', type='Voltage')
    
    opObj11 = upObj1.addOperation(name='removeDC', priority=1)
    opObj11.addParameter(name='type', value='1')
    
    
    opObj12 = upObj1.addOperation(name='decodification', priority=2)
    opObj12.addParameter(name='ncode', value='2')
    opObj12.addParameter(name='nbauds', value='8')
    opObj12.addParameter(name='code1', value='001110011')
    opObj12.addParameter(name='code2', value='001110011')
    
    print "Escribiendo el XML"
    
    projectObj.writeXml(filename)
    
    print "Leyendo el XML"
    projectObj.readXml(filename)
    