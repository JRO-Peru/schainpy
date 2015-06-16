import threading
import Queue
from time import sleep

from schainpy.controller  import Project
from command import *

class ControllerThread(threading.Thread):
    def __init__(self, filename, data_q=None):
        super(ControllerThread, self).__init__()
        self.filename = filename
        self.data_q = data_q
        self.control = {'stop':False,'pause':False}
    
    def stop(self):
        self.control['stop'] = True
        
    def pause(self):
        self.control['pause'] = not(self.control['pause'])

    def run(self):
        self.control['stop'] = False
        self.control['pause'] = False
        self.controllerObj = Project(self.control, self.data_q)
        self.controllerObj.readXml(self.filename)
        self.controllerObj.createObjects()
        self.controllerObj.connectObjects()
        self.controllerObj.run()
    
class CommCtrlProcessThread(threading.Thread):
    """ Implements the threading.Thread interface (start, join, etc.) and
        can be controlled via the cmd_q Queue attribute. Replies are placed in
        the reply_q Queue attribute.
    """
    def __init__(self, cmd_q=Queue.Queue(), reply_q=Queue.Queue()):
        super(CommCtrlProcessThread, self).__init__()
        self.cmd_q = cmd_q
#         self.reply_q = reply_q
        
#         self.print_q = Queue.Queue()
#         self.data_q = Queue.Queue()
        
        
        self.alive = threading.Event()
        self.setDaemon(True)
        self.alive.set()
        self.socket = None

        self.socketIO = None
        self.mySocket = None

        
        self.handlers = {
            ProcessCommand.PROCESS: self._handle_ioPROCESSTHREAD,
            ProcessCommand.MESSAGE: self._handle_ioMESSAGE,
            ProcessCommand.DATA: self._handle_ioDATA,
            ProcessCommand.STOP: self._handle_ioSTOP,
            ProcessCommand.PAUSE: self._handle_ioPAUSE
        }
    
    def run(self):
        
        while self.alive.isSet():
            try:
                cmd = self.cmd_q.get(True, 0.1)                
                self.handlers[cmd.type](cmd)
            except Queue.Empty as e:
                sleep(0.1)
                continue
    
    
    def _handle_ioPROCESSTHREAD(self, cmd):
        filename = cmd.data
        self.controllerObj = ControllerThread(filename=filename)
        self.controllerObj.start()
    
    def _handle_ioPAUSE(self, cmd):
        self.controllerObj.pause()
    
    def _handle_ioSTOP(self, cmd):
        self.controllerObj.stop()

    def _handle_ioDATA(self, cmd):
        self.reply_q.put(self._success_reply_data(data=cmd.data))

    def _handle_ioMESSAGE(self, cmd):
        self.reply_q.put(self._success_reply_message(data=cmd.data))

    def _success_reply_data(self, data=None):
        return ClientReply(ClientReply.DATA, data)

    def _success_reply_message(self, data=None):
        return ClientReply(ClientReply.MESSAGE, data)

    def join(self, timeout=None):
        self.alive.clear()
        threading.Thread.join(self, timeout)

    
    