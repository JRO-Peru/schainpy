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
from model.jroplot import *

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
    
    ELEMENTNAME = 'Parameter'
    
    def __init__(self):
        
        self.format = 'str'
    
    def getElementName(self):
        
        return self.ELEMENTNAME
    
    def getValue(self):
        
        value = self.value
        
        if self.format == 'list':
            strList = value.split(',')
            return strList
        
        if self.format == 'intlist':
            strList = value.split(',')
            intList = [int(x) for x in strList]
            return intList
        
        if self.format == 'floatlist':
            strList = value.split(',')
            floatList = [float(x) for x in strList]
            return floatList
        
        if self.format == 'date':
            strList = value.split('/')
            intList = [int(x) for x in strList]
            date = datetime.date(intList[0], intList[1], intList[2])
            return date
        
        if self.format == 'time':
            strList = value.split(':')
            intList = [int(x) for x in strList]
            time = datetime.time(intList[0], intList[1], intList[2])
            return time
        
        if self.format == 'bool':
            value = int(value)
        
        func = eval(self.format)
        
        return func(value)
        
    def setup(self, id, name, value, format='str'):
        
        self.id = id
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
        self.format = parmElement.get('format')
    
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
        
    def addParameter(self, name, value, format='str'):
        
        id = self.__getNewId()
        
        parmConfObj = ParameterConf()
        parmConfObj.setup(id, name, value, format)
        
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
    datatype = None
    inputId = None
    
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
        
        return str(self.id)
    
    def getInputId(self):
        
        return str(self.inputId)
    
    def getOperationObjList(self):
        
        return self.opConfObjList
    
    def getProcUnitObj(self):
        
        return self.procUnitObj
    
    def setup(self, id, name, datatype, inputId):
        
        self.id = id
        self.name = name
        self.datatype = datatype
        self.inputId = inputId
        
        self.opConfObjList = []
        
        self.addOperation(name='init', optype='self')
    
    def addParameter(self, **kwargs):
        
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
                kwargs[parmConfObj.name] = parmConfObj.getValue()
            
            #print "\tRunning the '%s' operation with %s" %(opConfObj.name, opConfObj.id)
            sts = self.procUnitObj.call(opConfObj, **kwargs)
            finalSts = finalSts or sts
        
        return finalSts
            
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
        self.inputId = 0
        
        self.opConfObjList = []
        self.opObjList = []
    
    def getElementName(self):
        
        return self.ELEMENTNAME
        
    def setup(self, id, name, datatype, path, startDate, endDate, startTime, endTime, **kwargs):
        
        self.id = id
        self.name = name
        self.datatype = datatype
        
        self.path = path
        self.startDate = startDate
        self.endDate = endDate
        self.startTime = startTime
        self.endTime = endTime
        
        self.addRunOperation(**kwargs)
    
    def addRunOperation(self, **kwargs):
        
        opObj = self.addOperation(name = 'run', optype = 'self')
        
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
    
    def addReadUnit(self, datatype, path, startDate='', endDate='', startTime='', endTime='', **kwargs):
        
        id = self.__getNewId()
        name = '%sReader' %(datatype)
        
        readUnitConfObj = ReadUnitConf()
        readUnitConfObj.setup(id, name, datatype, path, startDate, endDate, startTime, endTime, **kwargs)
        
        self.procUnitConfObjDict[readUnitConfObj.getId()] = readUnitConfObj
        
        return readUnitConfObj
    
    def addProcUnit(self, datatype, inputId):
        
        id = self.__getNewId()
        name = '%sProc' %(datatype)
        
        procUnitConfObj = ProcUnitConf()
        procUnitConfObj.setup(id, name, datatype, inputId)
        
        self.procUnitConfObjDict[procUnitConfObj.getId()] = procUnitConfObj
        
        return procUnitConfObj
    
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
            
            finalSts = False
            
            for procUnitConfObj in self.procUnitConfObjDict.values():
                #print "Running the '%s' process with %s" %(procUnitConfObj.name, procUnitConfObj.id)
                sts = procUnitConfObj.run()
                finalSts = finalSts or sts
            
            #If every process unit finished so end process
            if not(finalSts):
                print "Every process units have finished"
                break
            
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
    
    opObj12 = procUnitConfObj0.addOperation(name='CohInt', optype='other')
    opObj12.addParameter(name='n', value='10', format='int')
    
    procUnitConfObj1 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObj0.getId())
    procUnitConfObj1.addParameter(name='nFFTPoints', value='32', format='int')
#    procUnitConfObj1.addParameter(name='pairList', value='(0,1),(0,2),(1,2)', format='')
    
    
    opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
    opObj11.addParameter(name='idfigure', value='1', format='int')
    opObj11.addParameter(name='wintitle', value='SpectraPlot0', format='str')
    opObj11.addParameter(name='zmin', value='40', format='int')
    opObj11.addParameter(name='zmax', value='90', format='int')
    opObj11.addParameter(name='showprofile', value='1', format='int')  

#    opObj11 = procUnitConfObj1.addOperation(name='CrossSpectraPlot', optype='other')
#    opObj11.addParameter(name='idfigure', value='2', format='int')
#    opObj11.addParameter(name='wintitle', value='CrossSpectraPlot', format='str')
#    opObj11.addParameter(name='zmin', value='40', format='int')
#    opObj11.addParameter(name='zmax', value='90', format='int') 
            
            
#    procUnitConfObj2 = controllerObj.addProcUnit(datatype='Voltage', inputId=procUnitConfObj0.getId())
#  
#    opObj12 = procUnitConfObj2.addOperation(name='CohInt', optype='other')
#    opObj12.addParameter(name='n', value='2', format='int')
#    opObj12.addParameter(name='overlapping', value='1', format='int')
#
#    procUnitConfObj3 = controllerObj.addProcUnit(datatype='Spectra', inputId=procUnitConfObj2.getId())
#    procUnitConfObj3.addParameter(name='nFFTPoints', value='32', format='int')
#    
#    opObj11 = procUnitConfObj3.addOperation(name='SpectraPlot', optype='other')
#    opObj11.addParameter(name='idfigure', value='2', format='int')
#    opObj11.addParameter(name='wintitle', value='SpectraPlot1', format='str')
#    opObj11.addParameter(name='zmin', value='40', format='int')
#    opObj11.addParameter(name='zmax', value='90', format='int')
#    opObj11.addParameter(name='showprofile', value='1', format='int') 

#    opObj11 = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
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
#    opObj12 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
#    opObj12.addParameter(name='n', value='2', format='int')
#
#    opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
#    opObj11.addParameter(name='idfigure', value='2', format='int')
#    opObj11.addParameter(name='wintitle', value='SpectraPlot10', format='str')
#    opObj11.addParameter(name='zmin', value='70', format='int')
#    opObj11.addParameter(name='zmax', value='90', format='int')
#
#    opObj10 = procUnitConfObj1.addOperation(name='selectChannels')
#    opObj10.addParameter(name='channelList', value='2,6', format='intlist')
#    
#    opObj12 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
#    opObj12.addParameter(name='n', value='2', format='int')
#
#    opObj11 = procUnitConfObj1.addOperation(name='SpectraPlot', optype='other')
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
#    opObj21 = procUnitConfObj2.addOperation(name='IncohInt', optype='other')
#    opObj21.addParameter(name='n', value='2', format='int')
#    
#    opObj11 = procUnitConfObj2.addOperation(name='SpectraPlot', optype='other')
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
    
    