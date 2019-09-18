'''
Updated for multiprocessing
Author : Sergio Cortez
Jan 2018
Abstract:
    Base class for processing units and operations. A decorator provides multiprocessing features and interconnect the processes created.
    The argument (kwargs) sent from the controller is parsed and filtered via the decorator for each processing unit or operation instantiated. 
    The decorator handle also the methods inside the processing unit to be called from the main script (not as operations) (OPERATION -> type ='self'). 

Based on:
    $Author: murco $
    $Id: jroproc_base.py 1 2012-11-12 18:56:07Z murco $
'''

import os
import inspect
import zmq
import time
import pickle
import traceback
from queue import Queue
from threading import Thread
from multiprocessing import Process

from schainpy.utils import log


class ProcessingUnit(object):

    """
    Update - Jan 2018 - MULTIPROCESSING
    All the "call" methods present in the previous base were removed. 
    The majority of operations are independant processes, thus
    the decorator is in charge of communicate the operation processes 
    with the proccessing unit via IPC.

    The constructor does not receive any argument. The remaining methods
    are related with the operations to execute.
   

    """

    def __init__(self):

        self.dataIn = None
        self.dataOut = None
        self.isConfig = False
        self.operations = []
        self.plots = []

    def getAllowedArgs(self):
        if hasattr(self, '__attrs__'):
            return self.__attrs__
        else:
            return inspect.getargspec(self.run).args

    def addOperation(self, conf, operation):
        """
        This method is used in the controller, and update the dictionary containing the operations to execute. The dict 
        posses the id of the operation process (IPC purposes)

            Agrega un objeto del tipo "Operation" (opObj) a la lista de objetos "self.objectList" y retorna el
            identificador asociado a este objeto.

            Input:

                object    :    objeto de la clase "Operation"

            Return:

                objId    :    identificador del objeto, necesario para comunicar con master(procUnit)
        """

        self.operations.append(
            (operation, conf.type, conf.id, conf.getKwargs()))
        
        if 'plot' in self.name.lower():
            self.plots.append(operation.CODE)

    def getOperationObj(self, objId):

        if objId not in list(self.operations.keys()):
            return None

        return self.operations[objId]

    def operation(self, **kwargs):
        """
        Operacion directa sobre la data (dataOut.data). Es necesario actualizar los valores de los
        atributos del objeto dataOut

        Input:

            **kwargs    :    Diccionario de argumentos de la funcion a ejecutar
        """

        raise NotImplementedError

    def setup(self):

        raise NotImplementedError

    def run(self):

        raise NotImplementedError

    def close(self):

        return


class Operation(object):

    """
    Update - Jan 2018 - MULTIPROCESSING

    Most of the methods remained the same. The decorator parse the arguments and executed the run() method for each process.
    The constructor doe snot receive any argument, neither the baseclass.


        Clase base para definir las operaciones adicionales que se pueden agregar a la clase ProcessingUnit
        y necesiten acumular informacion previa de los datos a procesar. De preferencia usar un buffer de
        acumulacion dentro de esta clase

        Ejemplo: Integraciones coherentes, necesita la informacion previa de los n perfiles anteriores (bufffer)

    """

    def __init__(self):

        self.id = None
        self.isConfig = False

        if not hasattr(self, 'name'):
            self.name = self.__class__.__name__

    def getAllowedArgs(self):
        if hasattr(self, '__attrs__'):
            return self.__attrs__
        else:
            return inspect.getargspec(self.run).args

    def setup(self):

        self.isConfig = True

        raise NotImplementedError

    def run(self, dataIn, **kwargs):
        """
        Realiza las operaciones necesarias sobre la dataIn.data y actualiza los
        atributos del objeto dataIn.

        Input:

            dataIn    :    objeto del tipo JROData

        Return:

            None

        Affected:
            __buffer    :    buffer de recepcion de datos.

        """
        if not self.isConfig:
            self.setup(**kwargs)

        raise NotImplementedError

    def close(self):

        return


def MPDecorator(BaseClass):
    """
    Multiprocessing class decorator

    This function add multiprocessing features to a BaseClass. Also, it handle
    the communication beetween processes (readers, procUnits and operations). 
    """

    class MPClass(BaseClass, Process):

        def __init__(self, *args, **kwargs):
            super(MPClass, self).__init__()
            Process.__init__(self)
            self.operationKwargs = {}
            self.args = args
            self.kwargs = kwargs
            self.sender = None
            self.receiver = None
            self.i = 0
            self.t = time.time()
            self.name = BaseClass.__name__
            
            if 'plot' in self.name.lower() and not self.name.endswith('_'):
                self.name = '{}{}'.format(self.CODE.upper(), 'Plot')
            
            self.start_time = time.time()            
            self.id = args[0]
            self.inputId = args[1]
            self.project_id = args[2]
            self.err_queue = args[3]
            self.typeProc = args[4]            
            self.err_queue.put('#_start_#')

        def subscribe(self):
            '''
            Start the zmq socket receiver and subcribe to input ID.
            '''
                        
            c = zmq.Context()
            self.receiver = c.socket(zmq.SUB)
            self.receiver.connect(
                'ipc:///tmp/schain/{}_pub'.format(self.project_id))
            self.receiver.setsockopt(zmq.SUBSCRIBE, self.inputId.encode())
            
            
        def listen(self):
            '''
            This function waits for objects
            '''
            
            data = pickle.loads(self.receiver.recv_multipart()[1])
           
            return data            

        def set_publisher(self):
            '''
            This function create a zmq socket for publishing objects. 
            '''

            time.sleep(0.5)
            
            c = zmq.Context()
            self.sender = c.socket(zmq.PUB)
            self.sender.connect(
                'ipc:///tmp/schain/{}_sub'.format(self.project_id))

        def publish(self, data, id):
            '''
            This function publish an object, to an specific topic.
            For Read Units (inputId == None) adds a little delay
            to avoid data loss
            '''

            if self.inputId is None:
                self.i += 1
                if self.i % 40 == 0 and time.time()-self.t > 0.1:                    
                    self.i = 0
                    self.t = time.time()
                    time.sleep(0.05)
                elif self.i % 40 == 0:
                    self.i = 0
                    self.t = time.time()
                    time.sleep(0.01)
            
            self.sender.send_multipart([str(id).encode(), pickle.dumps(data)])

        def runReader(self):
            '''
            Run fuction for read units
            '''
            while True:

                try:
                    BaseClass.run(self, **self.kwargs)
                except:
                    err = traceback.format_exc()                    
                    if 'No more files' in err:
                        log.warning('No more files to read', self.name)
                    else:
                        self.err_queue.put('{}|{}'.format(self.name, err))
                    self.dataOut.error = True                 
                
                for op, optype, opId, kwargs in self.operations:
                    if optype == 'self' and not self.dataOut.flagNoData:
                        op(**kwargs)
                    elif optype == 'other' and not self.dataOut.flagNoData:
                        self.dataOut = op.run(self.dataOut, **self.kwargs)
                    elif optype == 'external':
                        self.publish(self.dataOut, opId)

                if self.dataOut.flagNoData and not self.dataOut.error:
                    continue

                self.publish(self.dataOut, self.id)

                if self.dataOut.error:   
                    break

            time.sleep(0.5)

        def runProc(self):
            '''
            Run function for proccessing units
            '''

            while True:
                self.dataIn = self.listen()                

                if self.dataIn.flagNoData and self.dataIn.error is None:
                    continue
                elif not self.dataIn.error:
                    try:
                        BaseClass.run(self, **self.kwargs)
                    except:
                        self.err_queue.put('{}|{}'.format(self.name, traceback.format_exc()))
                        self.dataOut.error = True
                elif self.dataIn.error:
                    self.dataOut.error = self.dataIn.error
                    self.dataOut.flagNoData = True
                     
                for op, optype, opId, kwargs in self.operations:
                    if optype == 'self' and not self.dataOut.flagNoData:
                        op(**kwargs)
                    elif optype == 'other' and not self.dataOut.flagNoData:
                        self.dataOut = op.run(self.dataOut, **kwargs)
                    elif optype == 'external' and not self.dataOut.flagNoData:                        
                        self.publish(self.dataOut, opId)
                
                self.publish(self.dataOut, self.id)
                for op, optype, opId, kwargs in self.operations:
                    if optype == 'external' and self.dataOut.error:                        
                        self.publish(self.dataOut, opId)
                
                if self.dataOut.error:
                    break
            
            time.sleep(0.5)

        def runOp(self):
            '''
            Run function for external operations (this operations just receive data
            ex: plots, writers, publishers)
            '''
            
            while True:

                dataOut = self.listen()

                if not dataOut.error:
                    BaseClass.run(self, dataOut, **self.kwargs)
                else:
                    break            

        def run(self):
            if self.typeProc is "ProcUnit":

                if self.inputId is not None:
                    self.subscribe()
                    
                self.set_publisher()

                if 'Reader' not in BaseClass.__name__:
                    self.runProc()
                else:
                    self.runReader()

            elif self.typeProc is "Operation":

                self.subscribe()
                self.runOp()

            else:
                raise ValueError("Unknown type")

            self.close()

        def close(self):

            BaseClass.close(self)
            self.err_queue.put('#_end_#')

            if self.sender:
                self.sender.close()

            if self.receiver:
                self.receiver.close()

            log.success('Done...(Time:{:4.2f} secs)'.format(time.time()-self.start_time), self.name)

    return MPClass
