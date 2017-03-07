'''
@author: Juan C. Espinoza
'''

import time
import json
import numpy
import paho.mqtt.client as mqtt
from pymongo import MongoClient

from schainpy.model.proc.jroproc_base import Operation

class PrettyFloat(float):
    def __repr__(self):
        return '%.2f' % self

def roundFloats(obj):
    if isinstance(obj, list):
        return map(roundFloats, obj)
    elif isinstance(obj, float):
        return round(obj, 2)

def pretty_floats(obj):
    if isinstance(obj, float):
        return PrettyFloat(obj)
    elif isinstance(obj, dict):
        return dict((k, pretty_floats(v)) for k, v in obj.items())
    elif isinstance(obj, (list, tuple)):
        return map(pretty_floats, obj)
    return obj


class PublishData(Operation):
    """Clase publish."""

    __MAXNUMX = 80
    __MAXNUMY = 80

    def __init__(self):
        """Inicio."""
        Operation.__init__(self)
        self.isConfig = False
        self.client = None

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print("Unexpected disconnection.")
        self.connect()

    def connect(self):
        print 'trying to connect'
        try:
            self.client.connect(
                host=self.host,
                port=self.port,
                keepalive=60*10,
                bind_address='')
            print "connected"
            self.client.loop_start()
            # self.client.publish(
            #     self.topic + 'SETUP',
            #     json.dumps(setup),
            #     retain=True
            #     )
        except:
            print "MQTT Conection error."
            self.client = False

    def setup(self, host, port=1883, username=None, password=None, mongo=0, clientId="user", **kwargs):

        self.mongo = mongo
        self.topic = kwargs.get('topic', 'schain')
        self.delay = kwargs.get('delay', 0)
        self.plottype = kwargs.get('plottype', 'spectra')
        self.host = host
        self.port = port
        self.clientId = clientId
        self.cnt = 0
        setup = []
        if (self.mongo):
            self.MongoClient = MongoClient("mongodb://127.0.0.1:3003")
            self.MongoDB = self.MongoClient['meteor']
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
        self.client = mqtt.Client(
            client_id=self.clientId + self.topic + 'SCHAIN',
            clean_session=True)
        self.client.on_disconnect = self.on_disconnect
        self.connect()

    def publish_data(self, plottype):
        data = getattr(self.dataOut, 'data_spc')
        yData = self.dataOut.heightList[:2].tolist()
        if plottype == 'spectra':
            z = data/self.dataOut.normFactor
            zdB = 10*numpy.log10(z)
            xlen, ylen = zdB[0].shape
            dx = numpy.floor(xlen/self.__MAXNUMX) + 1
            dy = numpy.floor(ylen/self.__MAXNUMY) + 1
            Z = [0 for i in self.dataOut.channelList]
            for i in self.dataOut.channelList:
                Z[i] = zdB[i][::dx, ::dy].tolist()
            payload = {
                'timestamp': self.dataOut.utctime,
                'data': roundFloats(Z),
                'channels': ['Ch %s' % ch for ch in self.dataOut.channelList],
                'interval': self.dataOut.getTimeInterval(),
                'xRange': [0, 80],
                'type': plottype,
                'yData': yData
            }
            # print payload

        elif plottype in ('rti', 'power'):
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
                'xRange': [0, 80],
                'type': plottype,
                'yData': yData
            }
        elif plottype == 'noise':
            noise = self.dataOut.getNoise()/self.dataOut.normFactor
            noisedB = 10*numpy.log10(noise)
            payload = {
                'timestamp': self.dataOut.utctime,
                'data': roundFloats(noisedB.reshape(-1, 1).tolist()),
                'channels': ['Ch %s' % ch for ch in self.dataOut.channelList],
                'interval': self.dataOut.getTimeInterval(),
                'xRange': [0, 80],
                'type': plottype,
                'yData': yData
            }
        else:
            print "Tipo de grafico invalido"
            payload = {
                'data': 'None',
                'timestamp': 'None',
                'type': None
            }
        print 'Publishing data to {}'.format(self.host)
        print '*************************'
        print self.client
        self.client.publish(self.topic + plottype, json.dumps(payload), qos=0)
        if (self.mongo):
            print 'Publishing data to Mongo'
            result = self.MongoDB.realtime.insert_one(payload)
            print result.inserted_id


    def run(self, dataOut, host, **kwargs):
        self.dataOut = dataOut
        if not self.isConfig:
            self.setup(host, **kwargs)
            self.isConfig = True

        map(self.publish_data, self.plottype)
        time.sleep(self.delay)

    def close(self):
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
