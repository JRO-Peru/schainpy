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
from platform import python_version
import inspect
import zmq
import time
import pickle
import os
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
    # objeto de datos de entrada (Voltage, Spectra o Correlation)
    dataIn = None
    dataInList = []

    # objeto de datos de entrada (Voltage, Spectra o Correlation)

    id = None
    inputId = None

    dataOut = None

    dictProcs = None
    
    operations2RunDict = None

    isConfig = False

    def __init__(self):

        self.dataIn = None
        self.dataOut = None

        self.isConfig = False

    def getAllowedArgs(self):
        if hasattr(self, '__attrs__'):
            return self.__attrs__
        else:
            return inspect.getargspec(self.run).args

    def addOperationKwargs(self, objId, **kwargs):
        '''
        '''

        self.operationKwargs[objId] = kwargs
 
    def addOperation(self, opObj, objId):

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

        self.operations2RunDict[objId] = opObj

        return objId


    def getOperationObj(self, objId):

        if objId not in list(self.operations2RunDict.keys()):
            return None

        return self.operations2RunDict[objId]

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
        #Close every thread, queue or any other object here is it is neccesary.
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
    id = None
    __buffer = None
    dest = None
    isConfig = False
    readyFlag = None

    def __init__(self):

        self.buffer = None
        self.dest = None
        self.isConfig = False
        self.readyFlag = False

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

        pass


######### Decorator #########


def MPDecorator(BaseClass):
    
    """
    "Multiprocessing class decorator"

        This function add multiprocessing features to the base class. Also,
        it handle the communication beetween processes (readers, procUnits and operations). 
        Receive the arguments at the moment of instantiation. According to that, discriminates if it
        is a procUnit or an operation
    """
  
    class MPClass(BaseClass, Process):
      
        "This is the overwritten class"
        operations2RunDict = None
        socket_l = None
        socket_p = None
        socketOP = None
        socket_router = None
        dictProcs = None
        typeProc = None
        def __init__(self, *args, **kwargs):
            super(MPClass, self).__init__()
            Process.__init__(self)
            
     
            self.operationKwargs = {}
            self.args = args
            

            self.operations2RunDict = {}
            self.kwargs = kwargs

        # The number of arguments (args) determine the type of process

            if len(self.args) is 3:
                self.typeProc = "ProcUnit"
                self.id = args[0] #topico de publicacion
                self.inputId = args[1] #topico de  subcripcion           
                self.dictProcs = args[2] #diccionario de procesos globales
            else:
                self.id = args[0]
                self.typeProc = "Operation"
                         
        def addOperationKwargs(self, objId, **kwargs):
     
            self.operationKwargs[objId] = kwargs

        def getAllowedArgs(self):

            if hasattr(self, '__attrs__'):
                return self.__attrs__
            else:
                return inspect.getargspec(self.run).args


        def sockListening(self, topic):

            """
            This function create a socket to receive objects.
                The 'topic' argument is related to the publisher process from which the self process is
                listening (data).
                In the case were the self process is listening to a Reader (proc Unit), 
                special conditions are introduced to maximize parallelism.
            """

            cont = zmq.Context()
            zmq_socket = cont.socket(zmq.SUB)
            if not os.path.exists('/tmp/socketTmp'): 
                os.mkdir('/tmp/socketTmp')
            
            if 'Reader' in self.dictProcs[self.inputId].name:
                zmq_socket.connect('ipc:///tmp/socketTmp/b')
                
            else:
                zmq_socket.connect('ipc:///tmp/socketTmp/%s' % self.inputId)
                
            #log.error('RECEIVING FROM {} {}'.format(self.inputId, str(topic).encode()))
            zmq_socket.setsockopt(zmq.SUBSCRIBE, str(topic).encode())   #yong

            return zmq_socket


        def listenProc(self, sock):

            """
            This function listen to a ipc addres until a message is recovered. To serialize the 
            data (object), pickle has been use.
            The 'sock' argument is the socket previously connect to an ipc address and with a topic subscription.
            """
            
            a = sock.recv_multipart()
            a = pickle.loads(a[1])
            return a

        def sockPublishing(self):

            """
            This function create a socket for publishing purposes.
            Depending on the process type from where is created, it binds or connect
            to special IPC addresses. 
            """
            time.sleep(4)              #yong
            context = zmq.Context()
            zmq_socket = context.socket(zmq.PUB)      
            if not os.path.exists('/tmp/socketTmp'): os.mkdir('/tmp/socketTmp')
            if 'Reader' in self.dictProcs[self.id].name:
                zmq_socket.connect('ipc:///tmp/socketTmp/a')        
            else:           
                zmq_socket.bind('ipc:///tmp/socketTmp/%s' % self.id)

            return zmq_socket

        def publishProc(self, sock, data): 

            """
            This function publish a python object (data) under a specific topic in a socket (sock).
            Usually, the topic is the self id of the process.
            """

            sock.send_multipart([str(self.id).encode(), pickle.dumps(data)]) #yong
            
            return True

        def sockOp(self):

            """
            This function create a socket for communication purposes with operation processes.
            """

            cont = zmq.Context()
            zmq_socket = cont.socket(zmq.DEALER)
            
            if python_version()[0] == '2':
                zmq_socket.setsockopt(zmq.IDENTITY, self.id)
            if python_version()[0] == '3':
                zmq_socket.setsockopt_string(zmq.IDENTITY, self.id)


            return zmq_socket


        def execOp(self, socket, opId, dataObj): 

            """
            This function 'execute' an operation main routine by establishing a
            connection with it and sending a python object (dataOut).
            """
            if not os.path.exists('/tmp/socketTmp'): os.mkdir('/tmp/socketTmp')
            socket.connect('ipc:///tmp/socketTmp/%s' %opId)

            
            socket.send(pickle.dumps(dataObj))   #yong

            argument = socket.recv_multipart()[0]

            argument = pickle.loads(argument)

            return argument

        def sockIO(self):

            """
            Socket defined for an operation process. It is able to recover the object sent from another process as well as a
            identifier of who sent it.
            """

            cont = zmq.Context()
            if not os.path.exists('/tmp/socketTmp'): os.mkdir('/tmp/socketTmp')
            socket = cont.socket(zmq.ROUTER)
            socket.bind('ipc:///tmp/socketTmp/%s' % self.id)

            return socket

        def funIOrec(self, socket):

            """
            Operation method, recover the id of the process who sent a python object. 
            The 'socket' argument is the socket binded to a specific process ipc.
            """

            #id_proc = socket.recv()
  
            #dataObj = socket.recv_pyobj()
            
            dataObj = socket.recv_multipart()
            
            dataObj[1] = pickle.loads(dataObj[1])
            return dataObj[0], dataObj[1]

        def funIOsen(self, socket, data, dest):

            """
            Operation method, send a python object to a specific destination. 
            The 'dest' argument is the id of a proccesinf unit. 
            """
    
            socket.send_multipart([dest, pickle.dumps(data)])  #yong

            return True


        def runReader(self):

            # time.sleep(3)
            while True:
            
                BaseClass.run(self, **self.kwargs)


                keyList = list(self.operations2RunDict.keys())
                keyList.sort()
                    
                for key in keyList:
                    self.socketOP = self.sockOp()
                    self.dataOut = self.execOp(self.socketOP, key, self.dataOut)

                
                if self.flagNoMoreFiles: #Usar un objeto con flags para saber si termino el proc o hubo un error
                    self.publishProc(self.socket_p, "Finish")
                    break

                if self.dataOut.flagNoData:
                    continue
              
                #print("Publishing data...")
                self.publishProc(self.socket_p, self.dataOut)   
                # time.sleep(2)
                  
            
            print("%s done" %BaseClass.__name__)
            return 0
 
        def runProc(self):

            # All the procUnits with kwargs that require a setup initialization must be defined here.

            if self.setupReq:
                BaseClass.setup(self, **self.kwargs)

            while True:
                self.dataIn = self.listenProc(self.socket_l)
                #print("%s received data" %BaseClass.__name__)
                
                if self.dataIn == "Finish":
                    break

                m_arg = list(self.kwargs.keys())
                num_arg = list(range(1,int(BaseClass.run.__code__.co_argcount)))
               
                run_arg = {}
                
                for var in num_arg:
                    if BaseClass.run.__code__.co_varnames[var] in m_arg:
                        run_arg[BaseClass.run.__code__.co_varnames[var]] = self.kwargs[BaseClass.run.__code__.co_varnames[var]]

                #BaseClass.run(self, **self.kwargs)
                BaseClass.run(self, **run_arg)

                ## Iterar sobre una serie de data que podrias aplicarse

                for m_name in BaseClass.METHODS:

                    met_arg = {}

                    for arg in m_arg:
                        if arg in BaseClass.METHODS[m_name]:
                            for att in BaseClass.METHODS[m_name]:
                                met_arg[att] = self.kwargs[att]

                            method = getattr(BaseClass, m_name)
                            method(self, **met_arg)
                            break

                if self.dataOut.flagNoData:
                    continue

                keyList = list(self.operations2RunDict.keys())
                keyList.sort()
                    
                for key in keyList:
               
                    self.socketOP = self.sockOp()
                    self.dataOut = self.execOp(self.socketOP, key, self.dataOut)
     
                     
                self.publishProc(self.socket_p, self.dataOut)
                
                    
            print("%s done" %BaseClass.__name__)

            return 0

        def runOp(self):

            while True:

                [self.dest ,self.buffer] = self.funIOrec(self.socket_router)

                self.buffer = BaseClass.run(self, self.buffer, **self.kwargs)
                
                self.funIOsen(self.socket_router, self.buffer, self.dest)

            print("%s done" %BaseClass.__name__)
            return 0
        
 
        def run(self):

            if self.typeProc is "ProcUnit":
                    
                self.socket_p = self.sockPublishing()
            
                if 'Reader' not in self.dictProcs[self.id].name:
                    self.socket_l = self.sockListening(self.inputId)
                    self.runProc()               

                else:
     
                    self.runReader()

            elif self.typeProc is "Operation":
                
                self.socket_router = self.sockIO()

                self.runOp()

            else:
                raise ValueError("Unknown type")

            return 0
      
    return MPClass