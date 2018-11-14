'''
@author: Juan C. Espinoza
'''

import os
import glob
import time
import json
import numpy
import zmq
import datetime
import ftplib
from functools import wraps
from threading import Thread
from multiprocessing import Process

from schainpy.model.proc.jroproc_base import Operation, ProcessingUnit, MPDecorator
from schainpy.model.data.jrodata import JROData
from schainpy.utils import log

MAXNUMX = 500
MAXNUMY = 500

PLOT_CODES = {
    'rti': 0,            # Range time intensity (RTI).
    'spc': 1,            # Spectra (and Cross-spectra) information.
    'cspc': 2,           # Cross-Correlation information.
    'coh': 3,            # Coherence map.
    'base': 4,           # Base lines graphic.
    'row': 5,            # Row Spectra.
    'total': 6,          # Total Power.
    'drift': 7,          # Drifts graphics.
    'height': 8,         # Height profile.
    'phase': 9,          # Signal Phase.
    'power': 16,
    'noise': 17,
    'beacon': 18,
    'wind': 22,
    'skymap': 23,
    'Unknown': 24,
    'V-E': 25,          # PIP Velocity.
    'Z-E': 26,          # PIP Reflectivity.
    'V-A': 27,          # RHI Velocity.
    'Z-A': 28,          # RHI Reflectivity.
}

def get_plot_code(s):
    label = s.split('_')[0]
    codes = [key for key in PLOT_CODES if key in label]
    if codes:        
        return PLOT_CODES[codes[0]]
    else:
        return 24

def decimate(z, MAXNUMY):
    dy = int(len(z[0])/MAXNUMY) + 1

    return z[::, ::dy]


class PublishData(Operation):
    '''
    Operation to send data over zmq.
    '''

    __attrs__ = ['host', 'port', 'delay', 'verbose']

    def setup(self, server='zmq.pipe', delay=0, verbose=True, **kwargs):
        self.counter = 0
        self.delay = kwargs.get('delay', 0)
        self.cnt = 0
        self.verbose = verbose        
        context = zmq.Context()
        self.zmq_socket = context.socket(zmq.PUSH)
        server = kwargs.get('server', 'zmq.pipe')

        if 'tcp://' in server:
            address = server
        else:
            address = 'ipc:///tmp/%s' % server

        self.zmq_socket.connect(address)
        time.sleep(1)


    def publish_data(self):
        self.dataOut.finished = False
        
        if self.verbose:
            log.log(
                'Sending {} - {}'.format(self.dataOut.type, self.dataOut.datatime),
                self.name
            )
        self.zmq_socket.send_pyobj(self.dataOut)

    def run(self, dataOut, **kwargs):
        self.dataOut = dataOut
        if not self.isConfig:
            self.setup(**kwargs)
            self.isConfig = True

        self.publish_data()
        time.sleep(self.delay)

    def close(self):
        
        self.dataOut.finished = True
        self.zmq_socket.send_pyobj(self.dataOut)
        time.sleep(0.1)
        self.zmq_socket.close()
        

class ReceiverData(ProcessingUnit):

    __attrs__ = ['server']

    def __init__(self, **kwargs):

        ProcessingUnit.__init__(self, **kwargs)

        self.isConfig = False
        server = kwargs.get('server', 'zmq.pipe')
        if 'tcp://' in server:
            address = server
        else:
            address = 'ipc:///tmp/%s' % server

        self.address = address
        self.dataOut = JROData()

    def setup(self):

        self.context = zmq.Context()
        self.receiver = self.context.socket(zmq.PULL)
        self.receiver.bind(self.address)
        time.sleep(0.5)
        log.success('ReceiverData from {}'.format(self.address))


    def run(self):

        if not self.isConfig:
            self.setup()
            self.isConfig = True

        self.dataOut = self.receiver.recv_pyobj()
        log.log('{} - {}'.format(self.dataOut.type,
                                 self.dataOut.datatime.ctime(),),
                'Receiving')

@MPDecorator
class SendToFTP(Operation):

    '''
    Operation to send data over FTP.
    patternX = 'local, remote, ext, period, exp_code, sub_exp_code'
    '''

    __attrs__ = ['server', 'username', 'password', 'timeout', 'patternX']

    def __init__(self):
        '''
        '''
        Operation.__init__(self)
        self.ftp = None
        self.ready = False

    def setup(self, server, username, password, timeout, **kwargs):
        '''
        '''

        self.server = server
        self.username = username
        self.password = password
        self.timeout = timeout
        self.patterns = []
        self.times = []
        self.latest = []
        for arg, value in kwargs.items():
            if 'pattern' in arg:
                self.patterns.append(value)
                self.times.append(time.time())
                self.latest.append('')

    def connect(self):
        '''
        '''

        log.log('Connecting to ftp://{}'.format(self.server), self.name)
        try:
            self.ftp = ftplib.FTP(self.server, timeout=self.timeout)
        except ftplib.all_errors:
            log.error('Server connection fail: {}'.format(self.server), self.name)
            if self.ftp is not None:
                self.ftp.close()
            self.ftp = None
            self.ready = False
            return 

        try:
            self.ftp.login(self.username, self.password)
        except ftplib.all_errors:
            log.error('The given username y/o password are incorrect', self.name)
            if self.ftp is not None:
                self.ftp.close()
            self.ftp = None
            self.ready = False
            return

        log.success('Connection success', self.name)
        self.ready = True
        return

    def check(self):

        try:
            self.ftp.voidcmd("NOOP")
        except:
            log.warning('Connection lost... trying to reconnect', self.name)
            if self.ftp is not None:
                self.ftp.close()
            self.ftp = None
            self.connect()

    def find_files(self, path, ext):

        files = glob.glob1(path, '*{}'.format(ext))
        files.sort()
        if files:
            return files[-1]
        return None

    def getftpname(self, filename, exp_code, sub_exp_code):

        thisDatetime = datetime.datetime.strptime(filename.split('_')[1], '%Y%m%d')
        YEAR_STR = '%4.4d' % thisDatetime.timetuple().tm_year
        DOY_STR = '%3.3d' % thisDatetime.timetuple().tm_yday
        exp_code = '%3.3d' % exp_code
        sub_exp_code = '%2.2d' % sub_exp_code
        plot_code = '%2.2d' % get_plot_code(filename)
        name = YEAR_STR + DOY_STR + '00' + exp_code + sub_exp_code + plot_code + '00.png'
        return name

    def upload(self, src, dst):

        log.log('Uploading {} -> {} '.format(
            src.split('/')[-1], dst.split('/')[-1]), 
            self.name, 
            nl=False
            )

        fp = open(src, 'rb')
        command = 'STOR {}'.format(dst)

        try:
            self.ftp.storbinary(command, fp, blocksize=1024)
        except Exception as e:
            log.error('{}'.format(e), self.name)
            if self.ftp is not None:
                self.ftp.close()
            self.ftp = None
            return 0

        try:
            self.ftp.sendcmd('SITE CHMOD 755 {}'.format(dst))
        except Exception as e:
            log.error('{}'.format(e), self.name)
            if self.ftp is not None:
                self.ftp.close()
            self.ftp = None
            return 0

        fp.close()
        log.success('OK', tag='')
        return 1
    
    def send_files(self):

        for x, pattern in enumerate(self.patterns):
            local, remote, ext, period, exp_code, sub_exp_code = pattern
            if time.time()-self.times[x] >= int(period):
                srcname = self.find_files(local, ext)
                src = os.path.join(local, srcname)
                if os.path.getmtime(src) < time.time() - 30*60:
                    log.warning('Skipping old file {}'.format(srcname))                  
                    continue

                if srcname is None or srcname == self.latest[x]:
                    log.warning('File alreday uploaded {}'.format(srcname))                  
                    continue
                
                if 'png' in ext:
                    dstname = self.getftpname(srcname, int(exp_code), int(sub_exp_code))
                else:
                    dstname = srcname                
                
                dst = os.path.join(remote, dstname)

                if self.upload(src, dst):
                    self.times[x] = time.time()
                    self.latest[x] = srcname
                else:                    
                    self.ready = False
                    break            

    def run(self, dataOut, server, username, password, timeout=10, **kwargs):

        if not self.isConfig:
            self.setup(
                server=server, 
                username=username, 
                password=password, 
                timeout=timeout, 
                **kwargs
                )
            self.isConfig = True
        if not self.ready:
            self.connect()
        if self.ftp is not None:
            self.check()
            self.send_files()

    def close(self):

        if self.ftp is not None:
            self.ftp.close()
