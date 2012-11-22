'''
Created on September , 2012
@author: 
'''
from xml.etree.ElementTree import Element, SubElement, ElementTree
from element import  prettify 
from xml.etree import ElementTree as ET
import sys


#def save(a, b):
#    
#    nameP = "Alexnder"
#    descripcion = self.projectWindow.Text()
#    id = 1
#    x = self.data.projectWindow.cmbbox.value()
#    
#    projectObj = Project(id, name, description)
#    
#    projectObj.setup(id, name, description)

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
    
    def addReadBranch(self, dpath, dataformat, readMode, startDate='', endDate='', startTime='', endTime=''):
        
        id = len(self.readBranchObjList) + 1
        
        readBranchObj = ReadBranch(id, dpath, dataformat, readMode, startDate, endDate, startTime, endTime)
        
        self.readBranchObjList.append(readBranchObj)
        
        return readBranchObj
    
    def addProcBranch(self, name):
        
        id = len(self.procBranchObjList) + 1
        
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
            
        for procBranchObj in self.procBranchObjList:
            procBranchObj.makeXml(projectElement)
            
        self.projectElement = projectElement
    
    def writeXml(self, filename):
        
        self.makeXml()
        ElementTree(self.projectElement).write(filename, method='xml')
        print prettify(self.projectElement)

    def readXml(self,workspace):
        print "Aqui estoy leyendo"
        tree=ET.parse(workspace)
        root=tree.getroot()
        self.project=root.tag
        self.idProyect= root.attrib.get('id')
        self.nameProyect= root.attrib.get('name') 
        for description in root.findall('description'):     
            description = description.get('description') 
        
        self.description= description
        
        for readBranch in root.findall('readBranch'):     
            id = readBranch.get('id') 
        self.idrb=id
        
        for procBranch in root.findall('procBranch'):     
            id = readBranch.get('id')     
            name = readBranch.get('name') 
        self.idpb=id
        self.nameBranch=name
#        
#        
        print self.project 
        print self.idProyect
        print self.nameProyect
        print  self.description
        print self.idrb
        print self.idpb
        print self.nameBranch
#        
####ESTO DEL MEDIO ESTABA COMENTADO
#        print root.tag , root.attrib
#        
#        print root.attrib.get('id')
#        print root.attrib.get('name')
            

#        for description in root.findall('description'):
#            description = root.find('description').text
#            name = root.get('name')
#            print name, description
        
#        description=root.find('description').text
#        print description
#   ESTO FUNCIONABA HACIA ABAJO     
        print "Otra forma "
        root=tree.getroot()
        print root.tag , root.attrib
        for child in root:
            print child.tag ,child.attrib 
            for child in child:
                print child.tag ,child.attrib
                for child in child:
                    print child.tag ,child.attrib
                    for child in child:
                        print child.tag ,child.attrib
#    
class ReadBranch():
    
    id = None
    dpath = None
    dataformat = None
    readMode = None
    startDate = None
    endDate = None
    startTime = None
    endTime = None
    
    def __init__(self, id, dpath, dataformat, readMode, startDate, endDate, startTime, endTime):
        
        self.id = id
        self.dpath = dpath
        self.dataformat = dataformat
        self.readMode = readMode
        self.startDate = startDate
        self.endDate = endDate
        self.startTime = startTime
        self.endTime = endTime
    
    def makeXml(self, projectElement):
        
        readBranchElement = SubElement(projectElement, 'readBranch')
        readBranchElement.set('id', str(self.id))
        
#        readBranchElement.set('dpath', self.dpath)
#        readBranchElement.set('dataformat', self.dataformat)
#        readBranchElement.set('startDate', self.startDate)
#        readBranchElement.set('endDate', self.endDate)
#        readBranchElement.set('startTime', self.startTime)
#        readBranchElement.set('endTime', self.endTime)
#        readBranchElement.set('readMode', str(self.readMode))
        
#        se = SubElement(readBranchElement, 'dpath')#ESTO ES LO ULTIMO QUE SE TRABAJO
#        se.text = self.dpath
#        
#        se = SubElement(readBranchElement, 'dataformat')#ESTO ES LO ULTIMO QUE SE TRABAJO
#        se.text = self.dataformat
#        
#        se = SubElement(readBranchElement, 'startDate')#ESTO ES LO ULTIMO QUE SE TRABAJO
#        se.text = self.startDate
#        
#        se = SubElement(readBranchElement, 'endDate')#ESTO ES LO ULTIMO QUE SE TRABAJO
#        se.text = self.endDate
#        
#        se = SubElement(readBranchElement, 'startTime')#ESTO ES LO ULTIMO QUE SE TRABAJO
#        se.text = self.startTime
#        
#        se = SubElement(readBranchElement, 'endTime')#ESTO ES LO ULTIMO QUE SE TRABAJO
#        se.text = self.endTime
#        
#        se = SubElement(readBranchElement, 'readMode')#ESTO ES LO ULTIMO QUE SE TRABAJO
#        se.text = str(self.readMode)
            
        ##########################################################################
        se = SubElement(readBranchElement, 'parameter', name='dpath'     , value=self.dpath)
        se = SubElement(readBranchElement, 'parameter', name='dataformat', value=self.dataformat)
        se = SubElement(readBranchElement, 'parameter', name='startDate' , value=self.startDate)
        se = SubElement(readBranchElement, 'parameter', name='endDate'   , value=self.endDate)
        se = SubElement(readBranchElement, 'parameter', name='startTime' , value=self.startTime)
        se = SubElement(readBranchElement, 'parameter', name='endTime'   , value=self.endTime)
        se = SubElement(readBranchElement, 'parameter', name='readMode'  , value=str(self.readMode))
         
    
class ProcBranch():
    
    id = None
    name = None
    
    upObjList = None
    
    def __init__(self, id, name):
        
        self.id = id
        self.name = name
        
        self.upObjList = []
        
    def addUP(self, name, type):
        
        id = len(self.upObjList) + 1
        
        upObj = UP(id, name, type)
        
        self.upObjList.append(upObj)
        
        return upObj
          
    def makeXml(self, projectElement):
        
        procBranchElement = SubElement(projectElement, 'procBranch')
        procBranchElement.set('id', str(self.id))
        procBranchElement.set('name', self.name)
        
        for upObj in self.upObjList:
            upObj.makeXml(procBranchElement)
    
class UP():
    
    id = None
    name = None
    type = None
    
    opObjList = []
    
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
    
    def makeXml(self, procBranchElement):
        
        upElement = SubElement(procBranchElement, 'UP')
        upElement.set('id', str(self.id))
        upElement.set('name', self.name)
        upElement.set('type', self.type)
        
        for opObj in self.opObjList:
            opObj.makeXml(upElement)
    
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
        
#        se = SubElement(parmElement, 'value')#ESTO ES LO ULTIMO QUE SE TRABAJO
#        se.text = self.value
        
if __name__ == '__main__':
    
    desc = "Este es un test"
    filename = "test.xml"
    
    workspace=str("C:\\Users\\alex\\workspace\\GUIV2.0\\test.xml")
    
    projectObj = Project()
    
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
    
    projectObj.writeXml(filename)
    
    projectObj.readXml(workspace)
    