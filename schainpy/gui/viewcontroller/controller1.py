'''
Created on September , 2012
@author: 
'''
from xml.etree.ElementTree import Element, SubElement, ElementTree
from xmlprint import  prettify 
from xml.etree import ElementTree as ET
import sys

class Project():
    
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
    
    def addReadBranch(self,id, dpath, dataformat, opMode,readMode, startDate='', endDate='', startTime='', endTime=''):
        
        #id = len(self.readBranchObjList) + 1
        
        readBranchObj = ReadBranch(id, dpath, dataformat, opMode , readMode, startDate, endDate, startTime, endTime)
        
        self.readBranchObjList.append(readBranchObj)
        
        return readBranchObj
    
    def addProcBranch(self, id,name):
        
       # id = len(self.procBranchObjList) + 1
        
        procBranchObj = ProcBranch(id, name)
        
        self.procBranchObjList.append(procBranchObj)
        
        return procBranchObj
    
    def makeXml(self):    
        
        projectElement = Element('Project')
        projectElement.set('id', str(self.id))
        projectElement.set('name', self.name)
        #projectElement.set('description', self.description)
        
        se = SubElement(projectElement, 'description',description=self.description)#ESTO ES LO ULTIMO QUE SE TRABAJO
        #se.text = self.description                    #ULTIMA MODIFICACION PARA SACAR UN SUB ELEMENT  
        
        for readBranchObj in self.readBranchObjList:
            readBranchObj.makeXml(projectElement)
            
        for branchObj in self.procBranchObjList:
            branchObj.makeXml(projectElement)
            
        self.projectElement = projectElement
    
    def writeXml(self, filename):
        
        self.makeXml()
        ElementTree(self.projectElement).write(filename, method='xml')
        #print prettify(self.projectElement)

class ReadBranch():
    
    id = None
    dpath = None
    dataformat = None
    opMode =None
    readMode = None
    startDate = None
    endDate = None
    startTime = None
    endTime = None
    
    def __init__(self, id, dpath, dataformat,opMode, readMode, startDate, endDate, startTime, endTime):
        
        self.id = id
        self.dpath = dpath
        self.dataformat = dataformat
        self.opMode = opMode
        self.readMode = readMode
        self.startDate = startDate
        self.endDate = endDate
        self.startTime = startTime
        self.endTime = endTime
    
    def makeXml(self, projectElement):
        
        readBranchElement = SubElement(projectElement, 'readBranch')
        readBranchElement.set('id', str(self.id))
            
        ##########################################################################
        se = SubElement(readBranchElement, 'parameter', name='dpath'     , value=self.dpath)
        se = SubElement(readBranchElement, 'parameter', name='dataformat', value=self.dataformat)
        se = SubElement(readBranchElement, 'parameter', name='opMode'    , value=self.opMode)
        se = SubElement(readBranchElement, 'parameter', name='startDate' , value=self.startDate)
        se = SubElement(readBranchElement, 'parameter', name='endDate'   , value=self.endDate)
        se = SubElement(readBranchElement, 'parameter', name='startTime' , value=self.startTime)
        se = SubElement(readBranchElement, 'parameter', name='endTime'   , value=self.endTime)
        se = SubElement(readBranchElement, 'parameter', name='readMode'  , value=str(self.readMode))
            
class ProcBranch():
    
    id = None
    name = None
    
    upObjList = None
    upsubObjList=None
    
    def __init__(self, id, name):
        
        self.id = id
        self.name = name
        
        self.upObjList = []
        self.upsubObjList = []
        
    def addUP(self,id, name, type):
        
        #id = len(self.upObjList) + 1
        
        upObj = UP(id, name, type)
        
        self.upObjList.append(upObj)
        
        return upObj
     
    def addUPSUB(self,id, name, type):
        
        # id = len(self.upsubObjList) + 1
        
        upsubObj = UPSUB(id, name, type)
        
        self.upsubObjList.append(upsubObj)
        
        return upsubObj
          
    def makeXml(self, projectElement):
        
        procBranchElement = SubElement(projectElement, 'procBranch')
        procBranchElement.set('id', str(self.id))
        procBranchElement.set('name', self.name)
        
        for upObj in self.upObjList:
            upObj.makeXml(procBranchElement)
            
        for upsubObj in self.upsubObjList:
            upsubObj.makeXml(procBranchElement)
    
class UP():
    
    id = None
    name = None
    type = None
    upsubObjList=None
    opObjList = None
    
    def __init__(self, id, name, type):
        
        self.id = id
        self.name = name
        self.type = type
        self.upsubObjList=[]
        self.up2subObjList=[]
        self.opObjList = []
        
    def addOperation(self,id, name, priority):
        
        #id = len(self.opObjList) + 1
        
        opObj = Operation(id, name, priority)
        
        self.opObjList.append(opObj)
        
        return opObj
    
    def addUPSUB(self,id, name, type):
        
#        id = len(self.upsubObjList) + 1
        
        upsubObj = UPSUB(id, name, type)
        
        self.upsubObjList.append(upsubObj)
        
        return upsubObj
    
    def addUP2SUB(self,id, name, type):
        
#        id = len(self.upsubObjList) + 1
        
        up2subObj = UP2SUB(id, name, type)
        
        self.up2subObjList.append(up2subObj)
        
        return up2subObj
        
    def makeXml(self, procBranchElement):
        
        upElement = SubElement(procBranchElement, 'UP')
        upElement.set('id', str(self.id))
        upElement.set('name', self.name)
        upElement.set('type', self.type)
        
        for opObj in self.opObjList:
            opObj.makeXml(upElement)
            
        for upsubObj in self.upsubObjList:
            upsubObj.makeXml(upElement)
            
class UPSUB():
    
    id = None
    name = None
    type = None
    opObjList = None
    up2subObjList=None
    
    
    def __init__(self, id, name, type):
        
        self.id = id
        self.name = name
        self.type = type
        self.up2subObjList = []
        self.opObjList = []
        
    def addOperation(self, name, priority):
        
        id = len(self.opObjList) + 1
        
        opObj = Operation(id, name, priority)
        
        self.opObjList.append(opObj)
        
        return opObj
        
        
    def addUP2SUB(self,id, name, type):
#        
#        id = len(self.opObjList) + 1
        up2subObj = UP2SUB(id, name, type)
        
        self.up2subObjList.append(up2subObj)
        
        return up2subObj
    
    def makeXml(self, upElement):
        
        upsubElement = SubElement(upElement, 'UPSUB')
        upsubElement.set('id', str(self.id))
        upsubElement.set('name', self.name)
        upsubElement.set('type', self.type)
        
        for opObj in self.opObjList:
            opObj.makeXml(upsubElement)
            
        for up2subObj in self.up2subObjList:
            up2subObj.makeXml(upsubElement)

class UP2SUB():
    
    id = None
    name = None
    type = None
    opObjList = None
    
    def __init__(self, id, name, type):
        
        self.id = id
        self.name = name
        self.type = type
        self.opObjList = []    
        
    def addOperation(self, name, priority):
        
        id = len(self.opObjList) + 1
        
        opObj = Operation(id, name, priority)
        
        self.opObjList.append(opObj)
        
        return opObj
    
    def makeXml(self,upsubElement):
        up2subElement = SubElement(upsubElement, 'UPD2SUB')
        up2subElement.set('id', str(self.id))
        up2subElement.set('name', self.name)
        up2subElement.set('type', self.type)
        
        for opObj in self.opObjList:
            opObj.makeXml(up2subElement)
            
class Operation():
    
    id = 0
    name = None
    priority = None
    parmObjList = []
    
    def __init__(self, id, name, priority):
        
        self.id = id
        self.name = name
        self.priority = priority
        
        self.parmObjList = []
        
    def addParameter(self, name, value):
        
        id = len(self.parmObjList) + 1
        
        parmObj = Parameter(id, name, value)
        
        self.parmObjList.append(parmObj)
        
        return parmObj
    
    def makeXml(self, upElement):
        
        opElement = SubElement(upElement, 'Operation')
        opElement.set('id', str(self.id))
        opElement.set('name', self.name)
        opElement.set('priority', str(self.priority))
        
        for parmObj in self.parmObjList:
            parmObj.makeXml(opElement)
    
class Parameter():
    
    id = None
    name = None
    value = None
    
    def __init__(self, id, name, value):
        
        self.id = id
        self.name = name
        self.value = value
    
    def makeXml(self, opElement):
        
        parmElement = SubElement(opElement, 'Parameter')
        parmElement.set('name', self.name)
        parmElement.set('value', self.value)