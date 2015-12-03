'''
Created on Jul 17, 2014

@author: roj-idl71
'''

DEFAULT_SERIALIZER = None

try:
    import cPickle
    DEFAULT_SERIALIZER = 'cPickle'
except:
    pass
 
try:
    import msgpack_numpy
    DEFAULT_SERIALIZER = 'msgpack'
except:
    pass

# import jsonpickle
# import yaml

class Serializer(object):
    
    def __init__(self):
        
        self.serializer = None
    
    def dumps(self, obj, **kwargs):
        
        return self.serializer.dumps(obj, **kwargs)
        
    def loads(self, obj, **kwargs):
        return self.serializer.loads(obj, **kwargs)
        
class cPickleSerializer(Serializer):
    
    def __init__(self):
        self.serializer = cPickle
        
    def dumps(self, obj, **kwargs):
        return self.serializer.dumps(obj, 2)
          
    def loads(self, obj, **kwargs):
        return self.serializer.loads(obj)

class msgpackSerializer(Serializer):
    
    def __init__(self):
        
        self.serializer = msgpack_numpy
    
    def dumps(self, obj, **kwargs):
        return self.serializer.packb(obj)
          
    def loads(self, obj, **kwargs):
        return self.serializer.unpackb(obj)
    
# class jsonpickleSerializer(Serializer):
#     
#     def __init__(self):
#         
#         self.serializer = jsonpickle
#         
#     def dumps(self, obj, **kwargs):
#         return self.serializer.encode(obj, **kwargs)
#          
#     def loads(self, obj, **kwargs):
#         return self.serializer.decode(obj, **kwargs)
# 
# class yamlSerializer(Serializer):
#     
#     def __init__(self):
#         
#         self.serializer = yaml
#         
#     def dumps(self, obj, **kwargs):
#         return self.serializer.dump(obj, **kwargs)
#          
#     def loads(self, obj, **kwargs):
#         return self.serializer.load(obj, **kwargs)

class DynamicSerializer(Serializer):
    
    def __init__(self, module = None):
        
        if not DEFAULT_SERIALIZER:
            raise ImportError, "Install a python serializer like cPickle or msgpack"
            
        if not mode:
            mode == DEFAULT_SERIALIZER
            
        if mode == 'cPickle':
            self.serializer = cPickleSerializer()
#         
#         if mode == 'jsonpickle':
#             self.serializer = jsonpickleSerializer()
#         
#         if mode == 'yaml':
#             self.serializer = yamlSerializer()
        
        if mode == 'msgpack':
            self.serializer = msgpackSerializer()
        
    
if __name__ == '__main__':
    pass