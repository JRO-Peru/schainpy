# Copyright (c) 2012-2020 Jicamarca Radio Observatory
# All rights reserved.
#
# Distributed under the terms of the BSD 3-clause license.
"""API to create signal chain projects

The API is provide through class: Project
"""

import re
import sys
import ast
import datetime
import traceback
import time
from multiprocessing import Process, Queue
from threading import Thread
from xml.etree.ElementTree import ElementTree, Element, SubElement

from schainpy.admin import Alarm, SchainWarning
from schainpy.model import *
from schainpy.utils import log


class ConfBase():

    def __init__(self):

        self.id = '0'
        self.name = None
        self.priority = None
        self.parameters = {}
        self.object = None
        self.operations = []

    def getId(self):

        return self.id
    
    def getNewId(self):

        return int(self.id) * 10 + len(self.operations) + 1

    def updateId(self, new_id):

        self.id = str(new_id)

        n = 1
        for conf in self.operations:
            conf_id = str(int(new_id) * 10 + n)
            conf.updateId(conf_id)
            n += 1

    def getKwargs(self):

        params = {}

        for key, value in self.parameters.items():
            if value not in (None, '', ' '):
                params[key] = value
        
        return params

    def update(self, **kwargs):

        for key, value in kwargs.items():
            self.addParameter(name=key, value=value)

    def addParameter(self, name, value, format=None):
        '''
        '''

        if isinstance(value, str) and re.search(r'(\d+/\d+/\d+)', value):
            self.parameters[name] = datetime.date(*[int(x) for x in value.split('/')])
        elif isinstance(value, str) and re.search(r'(\d+:\d+:\d+)', value):
            self.parameters[name] = datetime.time(*[int(x) for x in value.split(':')])
        else:
            try:
                self.parameters[name] = ast.literal_eval(value)
            except:
                if isinstance(value, str) and ',' in value:
                    self.parameters[name] = value.split(',')
                else:
                    self.parameters[name] = value

    def getParameters(self):

        params = {}
        for key, value in self.parameters.items():
            s = type(value).__name__
            if s == 'date':
                params[key] = value.strftime('%Y/%m/%d')
            elif s == 'time':
                params[key] = value.strftime('%H:%M:%S')
            else:
                params[key] = str(value)

        return params
    
    def makeXml(self, element):

        xml = SubElement(element, self.ELEMENTNAME)
        for label in self.xml_labels:
            xml.set(label, str(getattr(self, label)))
        
        for key, value in self.getParameters().items():
            xml_param = SubElement(xml, 'Parameter')
            xml_param.set('name', key)
            xml_param.set('value', value)
        
        for conf in self.operations:
            conf.makeXml(xml)
            
    def __str__(self):

        if self.ELEMENTNAME == 'Operation':
            s = '  {}[id={}]\n'.format(self.name, self.id)
        else:
            s = '{}[id={}, inputId={}]\n'.format(self.name, self.id, self.inputId)

        for key, value in self.parameters.items():
            if self.ELEMENTNAME == 'Operation':
                s += '    {}: {}\n'.format(key, value)
            else:
                s += '  {}: {}\n'.format(key, value)
        
        for conf in self.operations:
            s += str(conf)

        return s

class OperationConf(ConfBase):

    ELEMENTNAME = 'Operation'
    xml_labels = ['id', 'name']

    def setup(self, id, name, priority, project_id, err_queue):

        self.id = str(id)
        self.project_id = project_id
        self.name = name
        self.type = 'other'
        self.err_queue = err_queue

    def readXml(self, element, project_id, err_queue):

        self.id = element.get('id')
        self.name = element.get('name')
        self.type = 'other'
        self.project_id = str(project_id)
        self.err_queue = err_queue

        for elm in element.iter('Parameter'):
            self.addParameter(elm.get('name'), elm.get('value'))

    def createObject(self):

        className = eval(self.name)

        if 'Plot' in self.name or 'Writer' in self.name or 'Send' in self.name or 'print' in self.name:
            kwargs = self.getKwargs()
            opObj = className(self.id, self.id, self.project_id, self.err_queue, **kwargs)
            opObj.start()
            self.type = 'external'
        else:
            opObj = className()

        self.object = opObj
        return opObj

class ProcUnitConf(ConfBase):

    ELEMENTNAME = 'ProcUnit'
    xml_labels = ['id', 'inputId', 'name']

    def setup(self, project_id, id, name, datatype, inputId, err_queue):
        '''
        '''
        
        if datatype == None and name == None:
            raise ValueError('datatype or name should be defined')

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
        self.err_queue = err_queue
        self.operations = []
        self.parameters = {}

    def removeOperation(self, id):

        i = [1 if x.id==id else 0 for x in self.operations]
        self.operations.pop(i.index(1))
        
    def getOperation(self, id):

        for conf in self.operations:
            if conf.id == id:
                return conf

    def addOperation(self, name, optype='self'):
        '''
        '''

        id = self.getNewId()
        conf = OperationConf()
        conf.setup(id, name=name, priority='0', project_id=self.project_id, err_queue=self.err_queue)
        self.operations.append(conf)

        return conf

    def readXml(self, element, project_id, err_queue):

        self.id = element.get('id')
        self.name = element.get('name')
        self.inputId = None if element.get('inputId') == 'None' else element.get('inputId')
        self.datatype = element.get('datatype', self.name.replace(self.ELEMENTNAME.replace('Unit', ''), ''))
        self.project_id = str(project_id)
        self.err_queue = err_queue
        self.operations = []
        self.parameters = {}
        
        for elm in element:
            if elm.tag == 'Parameter':
                self.addParameter(elm.get('name'), elm.get('value'))
            elif elm.tag == 'Operation':
                conf = OperationConf()
                conf.readXml(elm, project_id, err_queue)
                self.operations.append(conf)

    def createObjects(self):
        '''
        Instancia de unidades de procesamiento.
        '''

        className = eval(self.name)
        kwargs = self.getKwargs()
        procUnitObj = className()
        procUnitObj.name = self.name
        log.success('creating process...', self.name)

        for conf in self.operations:
            
            opObj = conf.createObject()
            
            log.success('adding operation: {}, type:{}'.format(
                conf.name,
                conf.type), self.name)
            
            procUnitObj.addOperation(conf, opObj)
     
        self.object = procUnitObj

    def run(self):
        '''
        '''
        
        return self.object.call(**self.getKwargs())


class ReadUnitConf(ProcUnitConf):

    ELEMENTNAME = 'ReadUnit'

    def __init__(self):

        self.id = None
        self.datatype = None
        self.name = None
        self.inputId = None
        self.operations = []
        self.parameters = {}
    
    def setup(self, project_id, id, name, datatype, err_queue, path='', startDate='', endDate='',
              startTime='', endTime='', server=None, **kwargs):
        
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
        self.err_queue = err_queue        
        
        self.addParameter(name='path', value=path)
        self.addParameter(name='startDate', value=startDate)
        self.addParameter(name='endDate', value=endDate)
        self.addParameter(name='startTime', value=startTime)
        self.addParameter(name='endTime', value=endTime)

        for key, value in kwargs.items():
            self.addParameter(name=key, value=value)


class Project(Process):
    """API to create signal chain projects"""

    ELEMENTNAME = 'Project'

    def __init__(self, name=''):

        Process.__init__(self)
        self.id = '1'
        if name:
            self.name = '{} ({})'.format(Process.__name__, name)
        self.filename = None
        self.description = None
        self.email = None
        self.alarm = []
        self.configurations = {}
        # self.err_queue = Queue()
        self.err_queue = None
        self.started = False

    def getNewId(self):

        idList = list(self.configurations.keys())
        id = int(self.id) * 10

        while True:
            id += 1

            if str(id) in idList:
                continue

            break

        return str(id)

    def updateId(self, new_id):

        self.id = str(new_id)

        keyList = list(self.configurations.keys())
        keyList.sort()

        n = 1
        new_confs = {}

        for procKey in keyList:

            conf = self.configurations[procKey]
            idProcUnit = str(int(self.id) * 10 + n)
            conf.updateId(idProcUnit)
            new_confs[idProcUnit] = conf
            n += 1

        self.configurations = new_confs

    def setup(self, id=1, name='', description='', email=None, alarm=[]):

        self.id = str(id)
        self.description = description 
        self.email = email
        self.alarm = alarm
        if name:
            self.name = '{} ({})'.format(Process.__name__, name)

    def update(self, **kwargs):

        for key, value in kwargs.items():
            setattr(self, key, value)

    def clone(self):

        p = Project()
        p.id = self.id
        p.name = self.name
        p.description = self.description
        p.configurations = self.configurations.copy()

        return p

    def addReadUnit(self, id=None, datatype=None, name=None, **kwargs):

        '''
        '''

        if id is None:
            idReadUnit = self.getNewId()
        else:
            idReadUnit = str(id)

        conf = ReadUnitConf()
        conf.setup(self.id, idReadUnit, name, datatype, self.err_queue, **kwargs)
        self.configurations[conf.id] = conf
        
        return conf

    def addProcUnit(self, id=None, inputId='0', datatype=None, name=None):

        '''
        '''

        if id is None:
            idProcUnit = self.getNewId()
        else:
            idProcUnit = id
        
        conf = ProcUnitConf()
        conf.setup(self.id, idProcUnit, name, datatype, inputId, self.err_queue)
        self.configurations[conf.id] = conf

        return conf

    def removeProcUnit(self, id):

        if id in self.configurations:
            self.configurations.pop(id)

    def getReadUnit(self):

        for obj in list(self.configurations.values()):
            if obj.ELEMENTNAME == 'ReadUnit':
                return obj

        return None

    def getProcUnit(self, id):

        return self.configurations[id]

    def getUnits(self):

        keys = list(self.configurations)
        keys.sort()

        for key in keys:
            yield self.configurations[key]

    def updateUnit(self, id, **kwargs):

        conf = self.configurations[id].update(**kwargs)
    
    def makeXml(self):

        xml = Element('Project')
        xml.set('id', str(self.id))
        xml.set('name', self.name)
        xml.set('description', self.description)

        for conf in self.configurations.values():
            conf.makeXml(xml)

        self.xml = xml

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

        ElementTree(self.xml).write(abs_file, method='xml')

        self.filename = abs_file

        return 1

    def readXml(self, filename):

        abs_file = os.path.abspath(filename)

        self.configurations = {}

        try:
            self.xml = ElementTree().parse(abs_file)
        except:
            log.error('Error reading %s, verify file format' % filename)
            return 0

        self.id = self.xml.get('id')
        self.name = self.xml.get('name')
        self.description = self.xml.get('description')

        for element in self.xml:
            if element.tag == 'ReadUnit':
                conf = ReadUnitConf()
                conf.readXml(element, self.id, self.err_queue)
                self.configurations[conf.id] = conf
            elif element.tag == 'ProcUnit':
                conf = ProcUnitConf()
                input_proc = self.configurations[element.get('inputId')]
                conf.readXml(element, self.id, self.err_queue)
                self.configurations[conf.id] = conf

        self.filename = abs_file
        
        return 1

    def __str__(self):

        text = '\nProject[id=%s, name=%s, description=%s]\n\n' % (
            self.id,
            self.name,
            self.description,
            )

        for conf in self.configurations.values():
            text += '{}'.format(conf)

        return text

    def createObjects(self):

        keys = list(self.configurations.keys())
        keys.sort()
        for key in keys:
            conf = self.configurations[key]
            conf.createObjects()
            if conf.inputId is not None:
                conf.object.setInput(self.configurations[conf.inputId].object)

    def monitor(self):

        t = Thread(target=self._monitor, args=(self.err_queue, self.ctx))
        t.start()
    
    def _monitor(self, queue, ctx):

        import socket
        
        procs = 0
        err_msg = ''
        
        while True:
            msg = queue.get()
            if '#_start_#' in msg:
                procs += 1
            elif '#_end_#' in msg:
                procs -=1
            else:
                err_msg = msg
            
            if procs == 0 or 'Traceback' in err_msg:                
                break
            time.sleep(0.1)
        
        if '|' in err_msg:
            name, err = err_msg.split('|')
            if 'SchainWarning' in err:
                log.warning(err.split('SchainWarning:')[-1].split('\n')[0].strip(), name)
            elif 'SchainError' in err:
                log.error(err.split('SchainError:')[-1].split('\n')[0].strip(), name)
            else:
                log.error(err, name)
        else:            
            name, err = self.name, err_msg
        
        time.sleep(1)
            
        ctx.term()

        message = ''.join(err)

        if err_msg:
            subject = 'SChain v%s: Error running %s\n' % (
                schainpy.__version__, self.name)

            subtitle = 'Hostname: %s\n' % socket.gethostbyname(
                socket.gethostname())
            subtitle += 'Working directory: %s\n' % os.path.abspath('./')
            subtitle += 'Configuration file: %s\n' % self.filename
            subtitle += 'Time: %s\n' % str(datetime.datetime.now())

            readUnitConfObj = self.getReadUnit()
            if readUnitConfObj:
                subtitle += '\nInput parameters:\n'
                subtitle += '[Data path = %s]\n' % readUnitConfObj.parameters['path']
                subtitle += '[Start date = %s]\n' % readUnitConfObj.parameters['startDate']
                subtitle += '[End date = %s]\n' % readUnitConfObj.parameters['endDate']
                subtitle += '[Start time = %s]\n' % readUnitConfObj.parameters['startTime']
                subtitle += '[End time = %s]\n' % readUnitConfObj.parameters['endTime']

            a = Alarm(
                modes=self.alarm, 
                email=self.email,
                message=message,
                subject=subject,
                subtitle=subtitle,
                filename=self.filename
            )

            a.start()

    def setFilename(self, filename):

        self.filename = filename

    def runProcs(self):

        err = False
        n = len(self.configurations)
        
        while not err:
            for conf in self.getUnits():
                ok = conf.run()                
                if ok is 'Error':
                    n -= 1
                    continue
                elif not ok:
                    break
            if n == 0:
                err = True
        
    def run(self):

        log.success('\nStarting Project {} [id={}]'.format(self.name, self.id), tag='')
        self.started = True
        self.start_time = time.time()        
        self.createObjects()
        self.runProcs()
        log.success('{} Done (Time: {:4.2f}s)'.format(
            self.name,
            time.time()-self.start_time), '')
