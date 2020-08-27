'''
Base clases to create Processing units and operations, the MPDecorator
must be used in plotting and writing operations to allow to run as an
external process.
'''

import inspect
import zmq
import time
import pickle
import traceback
from threading import Thread
from multiprocessing import Process, Queue
from schainpy.utils import log


class ProcessingUnit(object):
    '''
    Base class to create Signal Chain Units
    '''

    proc_type = 'processing'

    def __init__(self):

        self.dataIn = None
        self.dataOut = None
        self.isConfig = False
        self.operations = []
    
    def setInput(self, unit):

        self.dataIn = unit.dataOut
    
    def getAllowedArgs(self):
        if hasattr(self, '__attrs__'):
            return self.__attrs__
        else:
            return inspect.getargspec(self.run).args

    def addOperation(self, conf, operation):
        '''
        '''
        
        self.operations.append((operation, conf.type, conf.getKwargs()))

    def getOperationObj(self, objId):

        if objId not in list(self.operations.keys()):
            return None

        return self.operations[objId]

    def call(self, **kwargs):
        '''
        '''

        try:
            if self.dataIn is not None and self.dataIn.flagNoData and not self.dataIn.error:
                return self.dataIn.isReady()
            elif self.dataIn is None or not self.dataIn.error:
                self.run(**kwargs)
            elif self.dataIn.error:
                self.dataOut.error = self.dataIn.error
                self.dataOut.flagNoData = True
        except:
            err = traceback.format_exc()                    
            if 'SchainWarning' in err:
                log.warning(err.split('SchainWarning:')[-1].split('\n')[0].strip(), self.name)
            elif 'SchainError' in err:
                log.error(err.split('SchainError:')[-1].split('\n')[0].strip(), self.name)
            else:
                log.error(err, self.name)
            self.dataOut.error = True
        
        for op, optype, opkwargs in self.operations:
            if optype == 'other' and not self.dataOut.flagNoData:
                self.dataOut = op.run(self.dataOut, **opkwargs)
            elif optype == 'external' and not self.dataOut.flagNoData:
                op.queue.put(self.dataOut)
            elif optype == 'external' and self.dataOut.error:                        
                op.queue.put(self.dataOut)

        return 'Error' if self.dataOut.error else self.dataOut.isReady()

    def setup(self):

        raise NotImplementedError

    def run(self):

        raise NotImplementedError

    def close(self):

        return


class Operation(object):

    '''
    '''
    
    proc_type = 'operation'

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

    This function add multiprocessing features to a BaseClass.  
    """

    class MPClass(BaseClass, Process):

        def __init__(self, *args, **kwargs):
            super(MPClass, self).__init__()
            Process.__init__(self)

            self.args = args
            self.kwargs = kwargs
            self.t = time.time()
            self.op_type = 'external'
            self.name = BaseClass.__name__
            self.__doc__ = BaseClass.__doc__
            
            if 'plot' in self.name.lower() and not self.name.endswith('_'):
                self.name = '{}{}'.format(self.CODE.upper(), 'Plot')
            
            self.start_time = time.time()
            self.err_queue = args[3]
            self.queue = Queue(maxsize=1)
            self.myrun = BaseClass.run

        def run(self):
            
            while True:

                dataOut = self.queue.get()

                if not dataOut.error:
                    try:
                        BaseClass.run(self, dataOut, **self.kwargs)
                    except:
                        err = traceback.format_exc()  
                        log.error(err, self.name)
                else:
                    break

            self.close()

        def close(self):

            BaseClass.close(self)
            log.success('Done...(Time:{:4.2f} secs)'.format(time.time()-self.start_time), self.name)

    return MPClass
