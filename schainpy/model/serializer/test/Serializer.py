'''
Module containing classes with serialization and de-serialization services.

$Id$
'''

import Lookup
import numpy as np
import zlib
import binascii
import yaml
import DynamicObject
import DynamicYAML
import PrecisionTime
import datetime
import re
import os
#import json
import jsonpickle
import jpickle
import h5py
import msgpack

class CompressionException(Exception): pass

class Serializer:
    """ Base class for pickle-like serialization
    of DynamicObjects (with compression available) """
    
    def __init__(self):
        pass
    
    def dump(self, obj, file_name, compression=None):
        """ Dumps obj to file_name, serializing the obj with toSerial() """
        string = self.dumps(obj, compression)
        open(file_name, 'w').write(string)
    
    def dumps(self, obj, compression=None):
        """ Returns serialized string representing obj, using toSerial() to serialize """
        if compression == 'gzip':
            return zlib.compress(self.toSerial(obj))
        elif compression in [None, '']:
            return self.toSerial(obj)
        else:
            raise CompressionException("Invalid decompression type '%r'"%(compression,))
    
    def load(self, file_name, compression=None):
        """ Returns the Object located in file_name, using fromSerial() to deserialize """
        string = open(file_name, 'r').read()
        return self.loads(string, compression)
    
    def loads(self, string, compression=None):
        """ Returns the Object serialized as the given string """
        if compression == 'gzip':
            return self.fromSerial(zlib.decompress(string))
        elif compression in [None, '']:
            return self.fromSerial(string)
        else:
            raise CompressionException("Invalid compression type '%r'"%(compression,))
    
    def fromSerial(self, string):
        """ Deserializes the given string """
        return string
    
    def toSerial(self, obj):
        """ Serializes the given object """
        return repr(obj)

class YAMLSerializer(Serializer):
    """ Serializes a Object to/from YAML format """
    
    def __init__(self):
        Serializer.__init__(self)
    
    def fromSerial(self, string):
        loader = DynamicYAML.Loader
        return yaml.load(string, Loader=loader)
    
    def toSerial(self, obj):
        dumper = DynamicYAML.Dumper
        return yaml.dump(obj, Dumper=dumper)

# Regular expression taken from yaml.constructor.py
timestamp_regexp_str = str(\
	ur'^(?P<year>[0-9][0-9][0-9][0-9])'
	ur'-(?P<month>[0-9][0-9]?)'
	ur'-(?P<day>[0-9][0-9]?)'
	ur'(?:(?:[Tt]|[ \t]+)'
	ur'(?P<hour>[0-9][0-9]?)'
	ur':(?P<minute>[0-9][0-9])'
	ur':(?P<second>[0-9][0-9])'
	ur'(?:\.(?P<fraction>[0-9]*))?'
	ur'(?:[ \t]*(?P<tz>Z|(?P<tz_sign>[-+])(?P<tz_hour>[0-9][0-9]?)'
	ur'(?::(?P<tz_minute>[0-9][0-9]))?))?)?$')
timestamp_regexp = re.compile(timestamp_regexp_str, re.X)

def construct_timestamp(value):
    """ Taken & modified from yaml.constructor.py """
    
    match = timestamp_regexp.match(value)
    #print "&%s&"%(value,)
    #print timestamp_regexp_str
    values = match.groupdict()
    year = int(values['year'])
    month = int(values['month'])
    day = int(values['day'])
    if not values['hour']:
        return datetime.date(year, month, day)
    hour = int(values['hour'])
    minute = int(values['minute'])
    second = int(values['second'])
    fraction = 0
    if values['fraction']:
        fraction = values['fraction'][:6]
        while len(fraction) < 6:
            fraction += '0'
        fraction = int(fraction)
    delta = None
    if values['tz_sign']:
        tz_hour = int(values['tz_hour'])
        tz_minute = int(values['tz_minute'] or 0)
        delta = datetime.timedelta(hours=tz_hour, minutes=tz_minute)
        if values['tz_sign'] == '-':
            delta = -delta
    data = datetime.datetime(year, month, day, hour, minute, second, fraction)
    if delta:
        data -= delta
    return data

class MessagePackSerializer(Serializer):
    """ Serializes a Object to/from MessagePack format """
    
    def __fromSerial(self, msg_dict):
        if not isinstance(msg_dict, (dict, list, tuple)):
            return msg_dict # msg_dict is a value - return it
        if isinstance(msg_dict, dict) and msg_dict.has_key('__meta_attributes'):
            meta_attr = msg_dict['__meta_attributes']
            msg_dict.pop('__meta_attributes')
            if meta_attr.has_key('type'):
                if meta_attr['type'] == 'datetime':
                    return construct_timestamp(str(msg_dict['ts']))
                elif meta_attr['type'] == 'nsTime':
                    msg_dict.pop('totalNS')
                elif meta_attr['type'] == 'psTime':
                    msg_dict.pop('totalPS')
                try: dtype = Lookup.cls_dtypes[meta_attr['type']]
                except KeyError: dtype = Lookup.builtin_objects[meta_attr['type']]
                return dtype(**msg_dict)
            else:
                for key in msg_dict.keys():
                    msg_dict[key] = self.__fromSerial(msg_dict[key])
                cls = Lookup.dynamicClasses['%s.%s'%(meta_attr['__object_name'],meta_attr['__revision_number'])]
                return cls(**msg_dict)
        elif msg_dict == ():
            return []
        elif isinstance(msg_dict[0], str) and msg_dict[1] in Lookup.numpy_dtypes and\
        isinstance(msg_dict, tuple) and len(msg_dict) == 2:
            value = binascii.unhexlify(msg_dict[0])
            return np.frombuffer(value, dtype=Lookup.numpy_dtypes[msg_dict[1]])[0]
        
        tup = isinstance(msg_dict, tuple)
        if tup and len(msg_dict) > 1 and msg_dict[0] in Lookup.numpy_dtypes.keys():
            msg_flat = list(msg_dict)
            dtypeName = msg_flat.pop(0)
            dtype = Lookup.numpy_dtypes[dtypeName]
            shape = msg_flat.pop(0)
            obj = np.empty(shape, dtype=dtype)
            np_flat = obj.flat
            for i in range(len(np_flat)):
                if isinstance(msg_flat[i], float):
                    value = msg_flat[i]
                else:
                    value = self.__fromSerial((msg_flat[i], dtypeName))
                np_flat[i] = value
            return obj
        else:
            return msg_dict
    
    def fromSerial(self, string):
        msg_dict = msgpack.unpackb(string)
        return self.__fromSerial(msg_dict)
    
    def __toSerial(self, obj):
        
        if isinstance(obj, (PrecisionTime.nsTime, PrecisionTime.psTime, DynamicObject.Binary, datetime.datetime)):
            msg_dict = {}
            if isinstance(obj, datetime.datetime):
                msg_dict['ts'] = obj.isoformat(' ')
            else:
                msg_dict.update(obj.__dict__)
            msg_dict['__meta_attributes'] = {'type': obj.__class__.__name__}
            return msg_dict
        elif isinstance(obj, DynamicObject.Object):
            msg_dict = {}
            for key, value in obj.__dict__.items():
                msg_dict[key] = self.__toSerial(value)
            
            msg_dict['__meta_attributes'] = obj.__class__.meta_attributes
            return msg_dict
        elif isinstance(obj, np.ndarray):
            np_flat = obj.flat
            msg_flat = []
            msg_flat.append(Lookup.cls_dtypes[obj.dtype.type]) # dtype is first element
            msg_flat.append(obj.shape) # shape of array is second element
            for i in range(len(np_flat)):
                toSer = self.__toSerial(np_flat[i])
                if isinstance(toSer, tuple): 
                    msg_flat.append(toSer[0])
                else:
                    msg_flat.append(toSer)
            return list(msg_flat)
        
        is_builtin = obj.__class__ in Lookup.numpy_dtypes.values()
        #is_python = isinstance(obj, Lookup.python_dtypes)
        if is_builtin: # and not is_python:
            try:
                #print obj.__class__
                msg_dict = (binascii.hexlify(obj), Lookup.cls_dtypes[obj.__class__])
                return msg_dict
            except TypeError: # numpy dtype is a built-in python type... force the hexlify:
                if not Lookup.bit32:
                    if obj.__class__ == int: return (binascii.hexlify(np.int64(obj)), 'dtype.int64')
                    elif obj.__class__ == float: return (binascii.hexlify(np.float64(obj)), 'dtype.float64')
                else:
                    #print np.int32(obj).__class__, obj.__class__
                    if obj.__class__ == int: return (binascii.hexlify(np.int32(obj)), 'dtype.int32')
                    elif obj.__class__ == float: return (binascii.hexlify(np.float32(obj)), 'dtype.float32')
                raise
        else:
            return obj
    
    def toSerial(self, obj):
        #if Lookup.bit32 and np.int32 != np.int: np.int32 = np.int
        toSer = self.__toSerial(obj)
        #print toSer
        value = msgpack.packb(toSer)
        return value

class HDF5Serializer(Serializer):
    """ Serializes a Object to/from HDF5 format """
    
    tmp_num = 0
    
    def __fromSerial(self, grp):
        
        if isinstance(grp, h5py.Dataset):
            return grp.value
        
        elif isinstance(grp, h5py.Group) and '__type' in grp.keys():
            typ = grp['__type'].value
            if typ == 'datetime':
                return construct_timestamp(str(grp['ts'].value))
            elif typ == '_null':
                return None
            elif typ == 'tuple':
                return tuple(grp['tuple'])
            elif typ == 'empty_list':
                return []
            try: cls = Lookup.builtin_objects_simple[typ]
            except KeyError: cls = Lookup.dynamicClasses[typ]
            args = []
            for key in grp.keys():
                fromSer = self.__fromSerial(grp[key])
                args.append((key, fromSer))
            kwargs = dict(args)
            kwargs.pop('__type')
            return cls(**kwargs)
        #else:
        #    return grp.value
        
    
    def fromSerial(self, string):
        HDF5Serializer.tmp_num += 1
        fn = 'tmp%d.hdf5'%(HDF5Serializer.tmp_num-1,)
        fp = open(fn, 'wb')
        fp.write(string)
        fp.flush(), fp.close()
        
        root = h5py.File(fn, driver='core')
        try:
            fromSer = self.__fromSerial(root['dataset'])
        except:
            root.flush(), root.close()
            os.remove(fn)
            raise
            
        root.flush(), root.close()
        os.remove(fn)
        
        return fromSer
    
    def __toSerial(self, obj, grp, name):
        
        if isinstance(obj, datetime.datetime):
            sub_grp = grp.create_group(name)
            sub_grp['__type'] = 'datetime'
            sub_grp['ts'] = obj.isoformat(' ')
        
        elif isinstance(obj, tuple(Lookup.builtin_objects_simple.values())):
            sub_grp = grp.create_group(name)
            sub_grp['__type'] = Lookup.obj_dtypes[obj.__class__]
            for key, value in obj.__dict__.items():
                if value != None and key not in ['totalNS', 'totalPS']:
                    sub_grp[key] = value
        
        elif obj == None:
            sub_grp = grp.create_group(name)
            sub_grp['__type'] = '_null'
        
        elif isinstance(obj, DynamicObject.Object):
            # Create the new group and assign unique identifier for this type of DynamicObject
            sub_grp = grp.create_group(name)
            tag = '%s.%s'%(obj.getObjectName(), obj.getRevisionNumber())
            sub_grp['__type'] = tag
            # Put all of the DynamicObject's attributes into the new h5py group
            for key, value in obj.__dict__.items():
                self.__toSerial(value, sub_grp, key)
        
        elif isinstance(obj, tuple):
            sub_grp = grp.create_group(name)
            sub_grp['__type'] = 'tuple'
            sub_grp['tuple'] = obj
        
        elif isinstance(obj, list) and len(obj) == 0:
            sub_grp = grp.create_group(name)
            sub_grp['__type'] = 'empty_list'
        
        else:
            grp[name] = obj
    
    def toSerial(self, obj):
        HDF5Serializer.tmp_num += 1
        fn = 'tmp%d.hdf5'%(HDF5Serializer.tmp_num,)
        root = h5py.File(fn, driver='core')
        try:
            self.__toSerial(obj, root, 'dataset')
        except:
            root.flush(), root.close()
            os.remove(fn)
            raise
        root.flush(), root.close()
        
        fp = open(fn, 'rb')
        msg = fp.read()
        fp.close()
        os.remove(fn)
        
        return msg

# Alias for the standard json serializer:
class jsonSerializer(Serializer):
    def fromSerial(self, string):
        #return json.loads(string)
        return jsonpickle.decode(string)
    def toSerial(self, string):
        #return json.dumps(string)
        return jsonpickle.encode(string, max_depth=500)

# Dict mapping from serializer type to corresponding class object:
serializers = {'yaml': YAMLSerializer,
               'msgpack': MessagePackSerializer,
               'hdf5': HDF5Serializer,
               'json': jsonSerializer}

instances = {'yaml': YAMLSerializer(),
             'msgpack': MessagePackSerializer(),
             'hdf5': HDF5Serializer(),
             'json': jsonSerializer()}

serial_types = dict([(v,u) for u,v in serializers.items()])

compression_types = ['gzip', '']

