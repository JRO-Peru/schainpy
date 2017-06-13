'''
@author: Juan C. Espinoza
'''

import time
import json
import numpy
import paho.mqtt.client as mqtt

from schainpy.model.proc.jroproc_base import Operation


class PrettyFloat(float):
    def __repr__(self):
        return '%.2f' % self

def pretty_floats(obj):
    if isinstance(obj, float):
        return PrettyFloat(obj)
    elif isinstance(obj, dict):
        return dict((k, pretty_floats(v)) for k, v in obj.items())
    elif isinstance(obj, (list, tuple)):
        return map(pretty_floats, obj)             
    return obj

class PublishData(Operation):
    
    __MAXNUMX = 80
    __MAXNUMY = 80
    
    def __init__(self):
        
        Operation.__init__(self)
        
        self.isConfig = False
        self.client = None        
    
    @staticmethod
    def on_disconnect(client, userdata, rc):
        if rc != 0:
            print("Unexpected disconnection.") 
    
    def setup(self, host, port=1883, username=None, password=None, **kwargs):
        
        self.client = mqtt.Client()
        try:
            self.client.connect(host=host, port=port, keepalive=60*10, bind_address='')
        except:
            self.client = False
        self.topic = kwargs.get('topic', 'schain')
        self.delay = kwargs.get('delay', 0)
        self.host = host
        self.port = port
        self.cnt = 0
    
    def run(self, dataOut, host, datatype='data_spc', **kwargs):
        
        if not self.isConfig:            
            self.setup(host, **kwargs)
            self.isConfig = True
        
        data = getattr(dataOut, datatype)                        

        z = data/dataOut.normFactor        
        zdB = 10*numpy.log10(z)
        avg = numpy.average(z, axis=1)
        avgdB = 10*numpy.log10(avg)        
        
        xlen ,ylen = zdB[0].shape
        
        
        dx = numpy.floor(xlen/self.__MAXNUMX) + 1
        dy = numpy.floor(ylen/self.__MAXNUMY) + 1
        
        Z = [0 for i in dataOut.channelList]
        AVG = [0 for i in dataOut.channelList]
        
        for i in dataOut.channelList:
            Z[i] = zdB[i][::dx, ::dy].tolist()
            AVG[i] = avgdB[i][::dy].tolist()                
        
        payload = {'timestamp':dataOut.utctime,
                   'data':pretty_floats(Z),
                   'data_profile':pretty_floats(AVG),
                   'channels': ['Ch %s' % ch for ch in dataOut.channelList],
                   'interval': dataOut.getTimeInterval(),
                   }        
                
        
        #if self.cnt==self.interval and self.client:
        print 'Publishing data to {}'.format(self.host)               
        self.client.publish(self.topic, json.dumps(payload), qos=0)
        time.sleep(self.delay)            
        #self.cnt = 0
        #else:
        #    self.cnt += 1     
        
                    
    def close(self):
        
        if self.client:       
            self.client.disconnect()