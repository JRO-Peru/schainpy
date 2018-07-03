'''
@author: Juan C. Espinoza
'''

import os
import glob
import time
import json
import numpy
import paho.mqtt.client as mqtt
import zmq
import datetime
import ftplib
from zmq.utils.monitor import recv_monitor_message
from functools import wraps
from threading import Thread
from multiprocessing import Process

from schainpy.model.proc.jroproc_base import Operation, ProcessingUnit
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

def roundFloats(obj):
    if isinstance(obj, list):
        return list(map(roundFloats, obj))
    elif isinstance(obj, float):
        return round(obj, 2)

def decimate(z, MAXNUMY):
    dy = int(len(z[0])/MAXNUMY) + 1

    return z[::, ::dy]

class throttle(object):
    '''
    Decorator that prevents a function from being called more than once every
    time period.
    To create a function that cannot be called more than once a minute, but
    will sleep until it can be called:
    @throttle(minutes=1)
    def foo():
      pass

    for i in range(10):
      foo()
      print "This function has run %s times." % i
    '''

    def __init__(self, seconds=0, minutes=0, hours=0):
        self.throttle_period = datetime.timedelta(
            seconds=seconds, minutes=minutes, hours=hours
        )

        self.time_of_last_call = datetime.datetime.min

    def __call__(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            coerce = kwargs.pop('coerce', None)
            if coerce:
                self.time_of_last_call = datetime.datetime.now()
                return fn(*args, **kwargs)
            else:
                now = datetime.datetime.now()
                time_since_last_call = now - self.time_of_last_call
                time_left = self.throttle_period - time_since_last_call

                if time_left > datetime.timedelta(seconds=0):
                    return

            self.time_of_last_call = datetime.datetime.now()
            return fn(*args, **kwargs)

        return wrapper

class Data(object):
    '''
    Object to hold data to be plotted
    '''

    def __init__(self, plottypes, throttle_value, exp_code, buffering=True):
        self.plottypes = plottypes
        self.throttle = throttle_value
        self.exp_code = exp_code
        self.buffering = buffering
        self.ended = False
        self.localtime = False
        self.meta = {}
        self.__times = []
        self.__heights = []

    def __str__(self):
        dum = ['{}{}'.format(key, self.shape(key)) for key in self.data]
        return 'Data[{}][{}]'.format(';'.join(dum), len(self.__times))

    def __len__(self):
        return len(self.__times)

    def __getitem__(self, key):
        if key not in self.data:
            raise KeyError(log.error('Missing key: {}'.format(key)))

        if 'spc' in key or not self.buffering:
            ret = self.data[key]
        else:
            ret = numpy.array([self.data[key][x] for x in self.times])
            if ret.ndim > 1:
                ret = numpy.swapaxes(ret, 0, 1)
        return ret

    def __contains__(self, key):
        return key in self.data

    def setup(self):
        '''
        Configure object
        '''
        
        self.type = ''
        self.ended = False
        self.data = {}
        self.__times = []
        self.__heights = []
        self.__all_heights = set()
        for plot in self.plottypes:
            if 'snr' in plot:
                plot = 'snr'
            self.data[plot] = {}

    def shape(self, key):
        '''
        Get the shape of the one-element data for the given key
        '''
        
        if len(self.data[key]):
            if 'spc' in key or not self.buffering:
                return self.data[key].shape
            return self.data[key][self.__times[0]].shape
        return (0,)

    def update(self, dataOut, tm):
        '''
        Update data object with new dataOut
        '''
        
        if tm in self.__times:
            return

        self.type = dataOut.type
        self.parameters = getattr(dataOut, 'parameters', [])
        if hasattr(dataOut, 'pairsList'):
            self.pairs = dataOut.pairsList
        if hasattr(dataOut, 'meta'):
            self.meta = dataOut.meta
        self.channels = dataOut.channelList
        self.interval = dataOut.getTimeInterval()
        self.localtime = dataOut.useLocalTime
        if 'spc' in self.plottypes or 'cspc' in self.plottypes:
            self.xrange = (dataOut.getFreqRange(1)/1000., dataOut.getAcfRange(1), dataOut.getVelRange(1))
        self.__heights.append(dataOut.heightList)
        self.__all_heights.update(dataOut.heightList)
        self.__times.append(tm)

        for plot in self.plottypes:
            if plot == 'spc':
                z = dataOut.data_spc/dataOut.normFactor
                buffer = 10*numpy.log10(z)
            if plot == 'cspc':
                buffer = dataOut.data_cspc
            if plot == 'noise':
                buffer = 10*numpy.log10(dataOut.getNoise()/dataOut.normFactor)
            if plot == 'rti':
                buffer = dataOut.getPower()
            if plot == 'snr_db':
                buffer = dataOut.data_SNR
            if plot == 'snr':
                buffer = 10*numpy.log10(dataOut.data_SNR)
            if plot == 'dop':
                buffer = 10*numpy.log10(dataOut.data_DOP)
            if plot == 'mean':
                buffer = dataOut.data_MEAN
            if plot == 'std':
                buffer = dataOut.data_STD
            if plot == 'coh':
                buffer = dataOut.getCoherence()
            if plot == 'phase':
                buffer = dataOut.getCoherence(phase=True)
            if plot == 'output':
                buffer = dataOut.data_output
            if plot == 'param':
                buffer = dataOut.data_param

            if 'spc' in plot:
                self.data[plot] = buffer
            else:
                if self.buffering:
                    self.data[plot][tm] = buffer
                else:
                    self.data[plot] = buffer

    def normalize_heights(self):
        '''
        Ensure same-dimension of the data for different heighList
        '''

        H = numpy.array(list(self.__all_heights))
        H.sort()
        for key in self.data:            
            shape = self.shape(key)[:-1] + H.shape
            for tm, obj in list(self.data[key].items()):
                h = self.__heights[self.__times.index(tm)]
                if H.size == h.size:
                    continue
                index = numpy.where(numpy.in1d(H, h))[0]
                dummy = numpy.zeros(shape) + numpy.nan                
                if len(shape) == 2:
                    dummy[:, index] = obj
                else:
                    dummy[index] = obj
                self.data[key][tm] = dummy
        
        self.__heights = [H for tm in self.__times]

    def jsonify(self, decimate=False):
        '''
        Convert data to json
        '''

        data = {}
        tm = self.times[-1]
        dy = int(self.heights.size/MAXNUMY) + 1
        for key in self.data:
            if key in ('spc', 'cspc') or not self.buffering:
                dx = int(self.data[key].shape[1]/MAXNUMX) + 1
                data[key] = roundFloats(self.data[key][::, ::dx, ::dy].tolist())
            else:
                data[key] = roundFloats(self.data[key][tm].tolist())

        ret = {'data': data}
        ret['exp_code'] = self.exp_code
        ret['time'] = tm
        ret['interval'] = self.interval
        ret['localtime'] = self.localtime
        ret['yrange'] = roundFloats(self.heights[::dy].tolist())
        if 'spc' in self.data or 'cspc' in self.data:
            ret['xrange'] = roundFloats(self.xrange[2][::dx].tolist())
        else:
            ret['xrange'] = []
        if hasattr(self, 'pairs'):
            ret['pairs'] = self.pairs
        else:
            ret['pairs'] = []
        
        for key, value in list(self.meta.items()):
            ret[key] = value

        return json.dumps(ret)

    @property
    def times(self):
        '''
        Return the list of times of the current data
        '''

        ret = numpy.array(self.__times)
        ret.sort()
        return ret

    @property
    def heights(self):
        '''
        Return the list of heights of the current data
        '''

        return numpy.array(self.__heights[-1])

class PublishData(Operation):
    '''
    Operation to send data over zmq.
    '''

    __attrs__ = ['host', 'port', 'delay', 'zeromq', 'mqtt', 'verbose']

    def __init__(self, **kwargs):
        """Inicio."""
        Operation.__init__(self, **kwargs)
        self.isConfig = False
        self.client = None
        self.zeromq = None
        self.mqtt = None

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            log.warning('Unexpected disconnection.')
        self.connect()

    def connect(self):
        log.warning('trying to connect')
        try:
            self.client.connect(
                host=self.host,
                port=self.port,
                keepalive=60*10,
                bind_address='')
            self.client.loop_start()
            # self.client.publish(
            #     self.topic + 'SETUP',
            #     json.dumps(setup),
            #     retain=True
            #     )
        except:
            log.error('MQTT Conection error.')
            self.client = False

    def setup(self, port=1883, username=None, password=None, clientId="user", zeromq=1, verbose=True, **kwargs):
        self.counter = 0
        self.topic = kwargs.get('topic', 'schain')
        self.delay = kwargs.get('delay', 0)
        self.plottype = kwargs.get('plottype', 'spectra')
        self.host = kwargs.get('host', "10.10.10.82")
        self.port = kwargs.get('port', 3000)
        self.clientId = clientId
        self.cnt = 0
        self.zeromq = zeromq
        self.mqtt = kwargs.get('plottype', 0)
        self.client = None
        self.verbose = verbose        
        setup = []
        if mqtt is 1:
            self.client = mqtt.Client(
                client_id=self.clientId + self.topic + 'SCHAIN',
                clean_session=True)
            self.client.on_disconnect = self.on_disconnect
            self.connect()
            for plot in self.plottype:
                setup.append({
                    'plot': plot,
                    'topic': self.topic + plot,
                    'title': getattr(self, plot + '_' + 'title', False),
                    'xlabel': getattr(self, plot + '_' + 'xlabel', False),
                    'ylabel': getattr(self, plot + '_' + 'ylabel', False),
                    'xrange': getattr(self, plot + '_' + 'xrange', False),
                    'yrange': getattr(self, plot + '_' + 'yrange', False),
                    'zrange': getattr(self, plot + '_' + 'zrange', False),
                })
        if zeromq is 1:
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
        if self.mqtt is 1:
            yData = self.dataOut.heightList[:2].tolist()
            if self.plottype == 'spectra':
                data = getattr(self.dataOut, 'data_spc')
                z = data/self.dataOut.normFactor
                zdB = 10*numpy.log10(z)
                xlen, ylen = zdB[0].shape
                dx = int(xlen/MAXNUMX) + 1
                dy = int(ylen/MAXNUMY) + 1
                Z = [0 for i in self.dataOut.channelList]
                for i in self.dataOut.channelList:
                    Z[i] = zdB[i][::dx, ::dy].tolist()
                payload = {
                    'timestamp': self.dataOut.utctime,
                    'data': roundFloats(Z),
                    'channels': ['Ch %s' % ch for ch in self.dataOut.channelList],
                    'interval': self.dataOut.getTimeInterval(),
                    'type': self.plottype,
                    'yData': yData
                }

            elif self.plottype in ('rti', 'power'):
                data = getattr(self.dataOut, 'data_spc')
                z = data/self.dataOut.normFactor
                avg = numpy.average(z, axis=1)
                avgdB = 10*numpy.log10(avg)
                xlen, ylen = z[0].shape
                dy = numpy.floor(ylen/self.__MAXNUMY) + 1
                AVG = [0 for i in self.dataOut.channelList]
                for i in self.dataOut.channelList:
                    AVG[i] = avgdB[i][::dy].tolist()
                payload = {
                    'timestamp': self.dataOut.utctime,
                    'data': roundFloats(AVG),
                    'channels': ['Ch %s' % ch for ch in self.dataOut.channelList],
                    'interval': self.dataOut.getTimeInterval(),
                    'type': self.plottype,
                    'yData': yData
                }
            elif self.plottype == 'noise':
                noise = self.dataOut.getNoise()/self.dataOut.normFactor
                noisedB = 10*numpy.log10(noise)
                payload = {
                    'timestamp': self.dataOut.utctime,
                    'data': roundFloats(noisedB.reshape(-1, 1).tolist()),
                    'channels': ['Ch %s' % ch for ch in self.dataOut.channelList],
                    'interval': self.dataOut.getTimeInterval(),
                    'type': self.plottype,
                    'yData': yData
                }
            elif self.plottype == 'snr':
                data = getattr(self.dataOut, 'data_SNR')
                avgdB = 10*numpy.log10(data)

                ylen = data[0].size
                dy = numpy.floor(ylen/self.__MAXNUMY) + 1
                AVG = [0 for i in self.dataOut.channelList]
                for i in self.dataOut.channelList:
                    AVG[i] = avgdB[i][::dy].tolist()
                payload = {
                    'timestamp': self.dataOut.utctime,
                    'data': roundFloats(AVG),
                    'channels': ['Ch %s' % ch for ch in self.dataOut.channelList],
                    'type': self.plottype,
                    'yData': yData
                }
            else:
                print("Tipo de grafico invalido")
                payload = {
                    'data': 'None',
                    'timestamp': 'None',
                    'type': None
                }

            self.client.publish(self.topic + self.plottype, json.dumps(payload), qos=0)

        if self.zeromq is 1:
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
        if self.zeromq is 1:
            self.dataOut.finished = True
            self.zmq_socket.send_pyobj(self.dataOut)
            time.sleep(0.1)
            self.zmq_socket.close()
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()


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


class PlotterReceiver(ProcessingUnit, Process):

    throttle_value = 5
    __attrs__ = ['server', 'plottypes', 'realtime', 'localtime', 'throttle',
        'exp_code', 'web_server', 'buffering']

    def __init__(self, **kwargs):

        ProcessingUnit.__init__(self, **kwargs)
        Process.__init__(self)
        self.mp = False
        self.isConfig = False
        self.isWebConfig = False
        self.connections = 0
        server = kwargs.get('server', 'zmq.pipe')
        web_server = kwargs.get('web_server', None)
        if 'tcp://' in server:
            address = server
        else:
            address = 'ipc:///tmp/%s' % server
        self.address = address
        self.web_address = web_server        
        self.plottypes = [s.strip() for s in kwargs.get('plottypes', 'rti').split(',')]
        self.realtime = kwargs.get('realtime', False)
        self.localtime = kwargs.get('localtime', True)
        self.buffering = kwargs.get('buffering', True)
        self.throttle_value = kwargs.get('throttle', 5)
        self.exp_code = kwargs.get('exp_code', None)
        self.sendData = self.initThrottle(self.throttle_value)
        self.dates = []
        self.setup()

    def setup(self):

        self.data = Data(self.plottypes, self.throttle_value, self.exp_code, self.buffering)
        self.isConfig = True

    def event_monitor(self, monitor):

        events = {}

        for name in dir(zmq):
            if name.startswith('EVENT_'):
                value = getattr(zmq, name)
                events[value] = name

        while monitor.poll():
            evt = recv_monitor_message(monitor)
            if evt['event'] == 32:
                self.connections += 1
            if evt['event'] == 512:
                pass

            evt.update({'description': events[evt['event']]})

            if evt['event'] == zmq.EVENT_MONITOR_STOPPED:
                break
        monitor.close()
        print('event monitor thread done!')

    def initThrottle(self, throttle_value):

        @throttle(seconds=throttle_value)
        def sendDataThrottled(fn_sender, data):
            fn_sender(data)

        return sendDataThrottled

    def send(self, data):
        log.log('Sending {}'.format(data), self.name)
        self.sender.send_pyobj(data)

    def run(self):

        log.log(
            'Starting from {}'.format(self.address),
            self.name
        )

        self.context = zmq.Context()
        self.receiver = self.context.socket(zmq.PULL)
        self.receiver.bind(self.address)
        monitor = self.receiver.get_monitor_socket()
        self.sender = self.context.socket(zmq.PUB)
        if self.web_address:
            log.success(
                'Sending to web: {}'.format(self.web_address),
                self.name
            )
            self.sender_web = self.context.socket(zmq.REQ)
            self.sender_web.connect(self.web_address)
            self.poll = zmq.Poller()
            self.poll.register(self.sender_web, zmq.POLLIN)
            time.sleep(1)

        if 'server' in self.kwargs:
            self.sender.bind("ipc:///tmp/{}.plots".format(self.kwargs['server']))
        else:
            self.sender.bind("ipc:///tmp/zmq.plots")

        time.sleep(2)

        t = Thread(target=self.event_monitor, args=(monitor,))
        t.start()

        while True:
            dataOut = self.receiver.recv_pyobj()
            if not dataOut.flagNoData:                
                if dataOut.type == 'Parameters':
                    tm = dataOut.utctimeInit
                else:
                    tm = dataOut.utctime
                if dataOut.useLocalTime:
                    if not self.localtime:
                        tm += time.timezone
                    dt = datetime.datetime.fromtimestamp(tm).date()
                else:
                    if self.localtime:
                        tm -= time.timezone
                    dt = datetime.datetime.utcfromtimestamp(tm).date()
                coerce = False
                if dt not in self.dates:
                    if self.data:
                        self.data.ended = True
                        self.send(self.data)
                        coerce = True
                    self.data.setup()
                    self.dates.append(dt)

                self.data.update(dataOut, tm)
            
            if dataOut.finished is True:
                self.connections -= 1
                if self.connections == 0 and dt in self.dates:
                    self.data.ended = True                    
                    self.send(self.data)
                    # self.data.setup()
                    time.sleep(1)
                    break
            else:
                if self.realtime:
                    self.send(self.data)
                    if self.web_address:
                        retries = 5
                        while True:
                            self.sender_web.send(self.data.jsonify())
                            socks = dict(self.poll.poll(5000))
                            if socks.get(self.sender_web) == zmq.POLLIN:
                                reply = self.sender_web.recv_string()
                                if reply == 'ok':
                                    log.log("Response from server ok", self.name)
                                    break
                                else:
                                    log.warning("Malformed reply from server: {}".format(reply), self.name)

                            else:
                                log.warning("No response from server, retrying...", self.name)
                            self.sender_web.setsockopt(zmq.LINGER, 0)
                            self.sender_web.close()
                            self.poll.unregister(self.sender_web)
                            retries -= 1
                            if retries == 0:
                                log.error("Server seems to be offline, abandoning", self.name)
                                self.sender_web = self.context.socket(zmq.REQ)
                                self.sender_web.connect(self.web_address)
                                self.poll.register(self.sender_web, zmq.POLLIN)
                                time.sleep(1)
                                break
                            self.sender_web = self.context.socket(zmq.REQ)
                            self.sender_web.connect(self.web_address)
                            self.poll.register(self.sender_web, zmq.POLLIN)
                            time.sleep(1)
                else:                    
                    self.sendData(self.send, self.data, coerce=coerce)
                    coerce = False

        return


class SendToFTP(Operation, Process):

    '''
    Operation to send data over FTP.
    '''

    __attrs__ = ['server', 'username', 'password', 'patterns', 'timeout']

    def __init__(self, **kwargs):
        '''
        patterns = [(local1, remote1, ext, delay, exp_code, sub_exp_code), ...]
        '''
        Operation.__init__(self, **kwargs)
        Process.__init__(self)
        self.server = kwargs.get('server')
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.patterns = kwargs.get('patterns')
        self.timeout = kwargs.get('timeout', 30)
        self.times = [time.time() for p in self.patterns]
        self.latest = ['' for p in self.patterns]
        self.mp = False
        self.ftp = None

    def setup(self):

        log.log('Connecting to ftp://{}'.format(self.server), self.name)
        try:
            self.ftp = ftplib.FTP(self.server, timeout=self.timeout)
        except ftplib.all_errors:
            log.error('Server connection fail: {}'.format(self.server), self.name)
            if self.ftp is not None:
                self.ftp.close()
            self.ftp = None
            self.isConfig = False
            return 

        try:
            self.ftp.login(self.username, self.password)
        except ftplib.all_errors:
            log.error('The given username y/o password are incorrect', self.name)
            if self.ftp is not None:
                self.ftp.close()
            self.ftp = None
            self.isConfig = False
            return

        log.success('Connection success', self.name)
        self.isConfig = True
        return

    def check(self):

        try:
            self.ftp.voidcmd("NOOP")
        except:
            log.warning('Connection lost... trying to reconnect', self.name)
            if self.ftp is not None:
                self.ftp.close()
            self.ftp = None
            self.setup()

    def find_files(self, path, ext):

        files = glob.glob1(path, '*{}'.format(ext))
        files.sort()
        if files:
            return files[-1]
        return None

    def getftpname(self, filename, exp_code, sub_exp_code):

        thisDatetime = datetime.datetime.strptime(filename.split('_')[1], '%Y%m%d')
        YEAR_STR = '%4.4d'%thisDatetime.timetuple().tm_year
        DOY_STR = '%3.3d'%thisDatetime.timetuple().tm_yday
        exp_code = '%3.3d'%exp_code
        sub_exp_code = '%2.2d'%sub_exp_code
        plot_code = '%2.2d'% get_plot_code(filename)
        name = YEAR_STR + DOY_STR + '00' + exp_code + sub_exp_code + plot_code + '00.png'
        return name

    def upload(self, src, dst):

        log.log('Uploading {} '.format(src), self.name, nl=False)

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
            local, remote, ext, delay, exp_code, sub_exp_code = pattern
            if time.time()-self.times[x] >= delay:
                srcname = self.find_files(local, ext)                
                src = os.path.join(local, srcname)                
                if os.path.getmtime(src) < time.time() - 30*60:                    
                    continue

                if srcname is None or srcname == self.latest[x]:
                    continue
                
                if 'png' in ext:
                    dstname = self.getftpname(srcname, exp_code, sub_exp_code)
                else:
                    dstname = srcname                
                
                dst = os.path.join(remote, dstname)

                if self.upload(src, dst):
                    self.times[x] = time.time()
                    self.latest[x] = srcname
                else:                    
                    self.isConfig = False                    
                    break            

    def run(self):

        while True:
            if not self.isConfig:
                self.setup()
            if self.ftp is not None:
                self.check()
                self.send_files()            
            time.sleep(10)

    def close():

        if self.ftp is not None:
            self.ftp.close()
        self.terminate()