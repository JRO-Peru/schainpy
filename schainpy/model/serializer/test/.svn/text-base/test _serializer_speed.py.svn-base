'''
Created on Jul 16, 2014

@author: roj-idl71
'''
"""
Dependencies:
 
    pip install tabulate simplejson python-cjson ujson yajl msgpack-python
 
"""
 
from timeit import timeit 
from tabulate import tabulate
 
setup = '''d = {
        'words': """
            Lorem ipsum dolor sit amet, consectetur adipiscing 
            elit. Mauris adipiscing adipiscing placerat. 
            Vestibulum augue augue, 
            pellentesque quis sollicitudin id, adipiscing.
            """,
        'boolean' : False,
        'list': range(10),
        'dict': dict((str(i),'a') for i in xrange(10)),
        'int': 100,
        'float': 100.123456,
}'''

setup = '''import numpy;
import datetime;
d = {
        'words': """
            Lorem ipsum dolor sit amet, consectetur adipiscing 
            elit. Mauris adipiscing adipiscing placerat. 
            Vestibulum augue augue, 
            pellentesque quis sollicitudin id, adipiscing.
            """,
        'boolean' : False,
        'list': range(10),
        'dict': dict((str(i),'a') for i in xrange(10)),
        'int': 100,
        'float': 100.123456,
        'datetime' : datetime.datetime(2001,1,1,10,10,10)
}'''


setup_pickle    = '%s ; import pickle ; src = pickle.dumps(d)' % setup
setup_pickle2   = '%s ; import pickle ; src = pickle.dumps(d, 2)' % setup
setup_cpickle    = '%s ; import cPickle ; src = cPickle.dumps(d)' % setup
setup_cpickle2   = '%s ; import cPickle ; src = cPickle.dumps(d, 2)' % setup
setup_json      = '%s ; import json; src = json.dumps(d)' % setup
setup_ujson      = '%s ; import ujson; src = ujson.encode(d)' % setup
setup_cjson      = '%s ; import cjson; src = cjson.encode(d)' % setup
setup_simplejson      = '%s ; import simplejson; src = simplejson.dump(d)' % setup
setup_jsonpickle = '%s ; import jsonpickle; src = jsonpickle.encode(d)' % setup
setup_yaml      = '%s ; import yaml; src = yaml.dump(d)' % setup
setup_msgpack   = '%s ; import msgpack; src = msgpack.dumps(d)' % setup
setup_msgpack_np  = '%s; import msgpack_numpy as msgpack; src = msgpack.dumps(d)' % setup
 
tests = [
    # (title, setup, enc_test, dec_test, result)
    ('cPickle (binary)', 'import cPickle; %s' % setup_cpickle2, 'cPickle.dumps(d, 2)', 'r = cPickle.loads(src)', 'print r'),
    ('cPickle (ascii)', 'import cPickle; %s' % setup_cpickle, 'cPickle.dumps(d, 0)', 'r = cPickle.loads(src)', 'print r'),
    ('pickle (binary)', 'import pickle; %s' % setup_pickle2, 'pickle.dumps(d, 2)', 'r = pickle.loads(src)', 'print r'),
    ('pickle (ascii)', 'import pickle; %s' % setup_pickle, 'pickle.dumps(d, 0)', 'r = pickle.loads(src)', 'print r'),
    ('jsonpickle', 'import jsonpickle; %s' % setup_jsonpickle, 'jsonpickle.encode(d)', 'r = jsonpickle.decode(src)', 'print r'),
#     ('msgpack-numpy-python', '%s' % setup_msgpack_np, 'msgpack.dumps(d)', 'r = msgpack.loads(src)', 'print r'),
    ('ujson', 'import ujson; %s' % setup_ujson, 'ujson.encode(d)', 'r = ujson.decode(src)', 'print r'),
#     ('msgpack-python', 'import msgpack; %s' % setup_msgpack, 'msgpack.dumps(d)', 'r = msgpack.loads(src)', 'print r'),
#     ('json', 'import json; %s' % setup_json, 'json.dumps(d)', 'r = json.loads(src)', 'print r'),
#     ('python-cjson-1.0.5', 'import cjson; %s' % setup_cjson, 'cjson.encode(d)', 'r = cjson.decode(src)', 'print r'),
#     ('simplejson-3.3.1', 'import simplejson; %s' % setup_json, 'simplejson.dumps(d)', 'r = simplejson.loads(src)', 'print r'),
    ('yaml', 'import yaml; %s' % setup_yaml, 'yaml.dump(d)', 'r = yaml.load(src)', 'print r'),
]
 
loops = 1
enc_table = []
dec_table = []
 
print "Running tests (%d loops each)" % loops
 
for title, mod, enc, dec, msg in tests:
    print title
    
    ### Getting the package size
    exec mod
    size = len("".join(src))
    
    print "  [Encode]", enc 
    result = timeit(enc, mod, number=loops)
    enc_table.append([title, result, size])
    
    print "  [Decode]", dec 
    result = timeit(dec, mod, number=loops)
    dec_table.append([title, result])
    
    print "  Result" 
    result = timeit(msg, mod+';'+dec, number=1)
 
enc_table.sort(key=lambda x: x[1])
enc_table.insert(0, ['Package', 'Seconds', 'Size'])
 
dec_table.sort(key=lambda x: x[1])
dec_table.insert(0, ['Package', 'Seconds'])
 
print "\nEncoding Test (%d loops)" % loops
print tabulate(enc_table, headers="firstrow")
 
print "\nDecoding Test (%d loops)" % loops
print tabulate(dec_table, headers="firstrow")
 
"""
OUTPUT:
 
Running tests (15000 loops each)
pickle (ascii)
  [Encode] pickle.dumps(d, 0)
  [Decode] pickle.loads(src)
pickle (binary)
  [Encode] pickle.dumps(d, 2)
  [Decode] pickle.loads(src)
cPickle (ascii)
  [Encode] cPickle.dumps(d, 0)
  [Decode] cPickle.loads(src)
cPickle (binary)
  [Encode] cPickle.dumps(d, 2)
  [Decode] cPickle.loads(src)
json
  [Encode] json.dumps(d)
  [Decode] json.loads(src)
simplejson-3.3.1
  [Encode] simplejson.dumps(d)
  [Decode] simplejson.loads(src)
python-cjson-1.0.5
  [Encode] cjson.encode(d)
  [Decode] cjson.decode(src)
ujson-1.33
  [Encode] ujson.dumps(d)
  [Decode] ujson.loads(src)
yajl 0.3.5
  [Encode] yajl.dumps(d)
  [Decode] yajl.loads(src)
msgpack-python-0.3.0
  [Encode] msgpack.dumps(d)
  [Decode] msgpack.loads(src)
 
Encoding Test (15000 loops)
Package                 Seconds
--------------------  ---------
ujson-1.33             0.232215
msgpack-python-0.3.0   0.241945
cPickle (binary)       0.305273
yajl 0.3.5             0.634148
python-cjson-1.0.5     0.680604
json                   0.780438
simplejson-3.3.1       1.04763
cPickle (ascii)        1.62062
pickle (ascii)        14.0497
pickle (binary)       15.4712
 
Decoding Test (15000 loops)
Package                 Seconds
--------------------  ---------
msgpack-python-0.3.0   0.240885
cPickle (binary)       0.393152
ujson-1.33             0.396875
python-cjson-1.0.5     0.694321
yajl 0.3.5             0.748369
simplejson-3.3.1       0.780531
cPickle (ascii)        1.38561
json                   1.65921
pickle (binary)        5.20554
pickle (ascii)        17.8767
"""