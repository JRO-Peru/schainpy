'''
Helper module for DynamicObject module - contains dictionaries
of data types built-in to our YAML IDL, converting backing and forth between
strings / YAML tags and python class instances.

$Id$
'''

import datetime
import numpy as np
import PrecisionTime
import DynamicObject
Binary = DynamicObject.Binary
import platform
import collections

# Implicit Types:
python_dtypes = tuple([bool,int,int,float,str,datetime.datetime,list,
                 set,dict,tuple,str])

# Numpy Data-types:
numpy_dtypes = {'dtype.bool': bool, 'dtype.int': np.int, 'dtype.int8': np.int8,
          'dtype.int16': np.int16, 'dtype.int32': np.int32, 'dtype.int64': np.int64,
          'dtype.uint8': np.uint8, 'dtype.uint16': np.uint16, 'dtype.uint32': np.uint32,
          'dtype.uint64': np.uint64, 'dtype.float': np.float, 'dtype.float16': np.float16,
          'dtype.float32': np.float32, 'dtype.float64': np.float64, 'dtype.complex': np.complex,
          'dtype.complex64': np.complex64, 'dtype.complex128': np.complex128,
          'dtype.byte': np.byte, 'dtype.short': np.short, 'dtype.intc': np.intc,
          'dtype.longlong': np.longlong, 'dtype.intp': np.intp, 'dtype.ubyte': np.ubyte,
          'dtype.ushort': np.ushort, 'dtype.uintc': np.uintc, 'dtype.uint': np.uint,
          'dtype.uintc': np.uintc, 'dtype.uint': np.uint, 'dtype.ulonglong': np.ulonglong,
          'dtype.uintp': np.uintp, 'dtype.half': np.half, 'dtype.single': np.single,
          'dtype.double': np.double, 'dtype.longfloat': np.longfloat,
          'dtype.csingle': np.csingle, 'dtype.clongfloat': np.clongfloat, 'dtype.long': np.long}

if platform.architecture()[0] != '32bit': # 64bit - certain numpy types exist
    numpy_dtypes.update({'dtype.float128': np.float128, 'dtype.complex256': np.complex256})
    bit32 = False
else:
    bit32 = True
#else: # 32 bit - fix 32 bit integer issue.
#    np.int32 = np.int
#    bit32 = True

# Built-in objects:
builtin_objects = {'binary': Binary, 'nsTime': PrecisionTime.nsTime, 'psTime': PrecisionTime.psTime,
          'timestamp_ns': PrecisionTime.nsTime, 'timestamp_ps': PrecisionTime.psTime,
          'timestamp_nanosecond': PrecisionTime.nsTime, 'timestamp_picosecond': PrecisionTime.psTime,
          'datetime': datetime.datetime, 'Binary': Binary}

builtin_objects_simple = {'nsTime': PrecisionTime.nsTime, 'psTime': PrecisionTime.psTime,
                          'binary': Binary, 'datetime': datetime.datetime,
                          'Binary': Binary}

# Inverse lookup for accessing tags given a class instance:
cls_dtypes = dict([(v,k) for (k,v) in list(numpy_dtypes.items())])
obj_dtypes = dict([(v,k) for (k,v) in list(builtin_objects_simple.items())])

# Pointer to the list of all Object classes created, as located in the Object module / class:
dynamicClasses = DynamicObject.Object.dynamicClasses

