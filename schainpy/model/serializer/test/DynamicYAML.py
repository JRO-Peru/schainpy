'''
Module containing YAML Loader and Dumper for DynamicObjects
as well as built-in data types (numpy, PrecisionTime, datetime, Binary, ...)

$Id$
'''

import yaml
import OrderedYAML
import DynamicObject
import binascii
import numpy as np
import PrecisionTime
import Lookup
import pysvn

def load_defn(source, rev='head', repo=""):
    """ Import YAML definition(s) from given 'source' SVN location
    with specific revision number 'rev'. Returns a dict of the object
    names -> class object instances.
    
    NOTE: Object defns with same name & revision number will conflict /
    cause issues (regardless of svn location). """
    client = pysvn.Client()
    
    if rev == 'head':
        #yaml = client.cat(source)
        rev = client.info(repo).revision.number
    
    if source.startswith('http'):
        yaml = client.cat("%s?p=%d"%(source, rev))
    else:
        pysvn_rev = pysvn.Revision(pysvn.opt_revision_kind.number, rev)
        yaml = client.cat(source, pysvn_rev)
    
    revision_dict = {\
              "__revision_number": rev,
              "__revision_id": 'unknown',
              "__revision_source": source,
              "__revision_tag": 'unknown'}
    
    return DynamicObject.Factory(yaml=yaml, revision_dict=revision_dict).classes

class Loader(OrderedYAML.Loader):

    def __init__(self, stream):
        OrderedYAML.Loader.__init__(self, stream)
    
    def construct_object(self, node, deep=False):
        """ Unresolved tags on mapping nodes come from un-imported YAML definitions - import it """
        resolved = node.tag in self.yaml_constructors
        resolved = resolved or any([node.tag.startswith(x) for x in self.yaml_multi_constructors])
        if isinstance(node, yaml.nodes.MappingNode) and not resolved:
            data = self.construct_mapping(self, node)
            self.constructed_objects[node] = data
            del self.recursive_objects[node]
            if data.has_key('__revision_source'):
                # TODO: Handle password authentication
                client = pysvn.Client()
                source = data['__revision_source']
                if source.startswith('http'):
                    rev = data['__revision_number']
                    defn = client.cat("%s?p=%d"%(source, rev))
                else:
                    rev = pysvn.Revision(pysvn.opt_revision_kind.number, data['__revision_number'])
                    defn = client.cat(source, revision=rev)
                DynamicObject.Factory(yaml=defn) # Register the object
                
                constructor = self.yaml_constructors["%s.%s"%(data['__revision_name'], data['__revision_number'])]
                return constructor(node)
            else:
                raise Exception("Cannot load object with tag '%s' - cannot find YAML object definition (no __revision_source included)")
        else:
            return yaml.Loader.construct_object(self, node, deep=deep)

class Dumper(OrderedYAML.Dumper):
    
    def __init__(self, stream, *args, **kwargs):
        OrderedYAML.Dumper.__init__(self, stream, *args, **kwargs)
        
    def represent_dynamic_object(self, obj):
        """
        Override the !!python/object:__main__.xxx syntax with
        !ObjectName.zzz where zzz is the revision number of the Object obj
        """
        
        state = {}
        state.update(obj.__dict__.items())
        state.update(obj.__class__.meta_attributes.items())
        name = obj.getObjectName() # obj.__class__.__name__
        revision = obj.getRevisionNumber()
        return self.represent_mapping(u'!%s.%s' % (name, revision), state)

# Dtypes to be stored as hex in YAML streams / strings
hex_dtypes = ['float', 'complex', 'half', 'single', 'double']

# Register hex constructors for the numpy / built-in dtypes:
dtypes = Lookup.numpy_dtypes

# Inverse lookup for accessing tags given a class instance:
cls_dtypes = dict([(v,k) for (k,v) in dtypes.items()])

# Representer for numpy arrays:
def ndarray_representer(dumper, obj):
    #if isinstance(obj, np.ndarray):
    tag = 'dtype.'+obj.dtype.type.__name__
    hexlify = any([x in tag for x in hex_dtypes])
    np_ary = obj
    #hex_ary = np.empty(np_ary.shape, dtype=yaml.nodes.ScalarNode)
    np_flat, hex_flat = np_ary.flat, [] #hex_ary.flat
    hex_flat.append(dumper.represent_sequence(u'tag:yaml.org,2002:seq', list(np_ary.shape), flow_style=True))
    if hexlify:
        lst = []
        for i in range(len(np_flat)):
            value = u'%s'%(np_flat[i],)
            node = dumper.represent_scalar(u'tag:yaml.org,2002:str', value, style='')
            lst.append(node)
        hex_flat.append(yaml.nodes.SequenceNode(u'tag:yaml.org,2002:seq', lst, flow_style=True))
        lst = []
    for i in range(len(np_flat)):
        if hexlify: value = u'%s'%(binascii.hexlify(np_flat[i]),)
        else: value = u'%s'%(np_flat[i],)
        node = dumper.represent_scalar(u'tag:yaml.org,2002:str', value, style='')
        if hexlify: lst.append(node)
        else: hex_flat.append(node)
    if hexlify: hex_flat.append(yaml.nodes.SequenceNode(u'tag:yaml.org,2002:seq', lst, flow_style=True))
    return yaml.nodes.SequenceNode(u'!%s'%(tag,), hex_flat, flow_style=True)
Dumper.add_representer(np.ndarray, ndarray_representer)

# Constructor for ndarrays with arbitrary (specified) dtype:
def ndarray_constructor(loader, node, dtype, hexlify=False):
    shape = loader.construct_sequence(node.value.pop(0))
    np_ary = np.empty(shape, dtype=dtype)
    np_flat = np_ary.flat # Flat iterator
    if hexlify:
        node.value[1].tag = node.tag
        node = node.value[1] # only look at hexlified values
    for i in range(len(node.value)):
        # Over-ride the 'tag:yaml.org,2002:str' tag with correct data type
        node.value[i].tag = node.tag
        value = loader.construct_object(node.value[i])
        #if hexlify:
        #    value = binascii.unhexlify(value)
        #    value = np.frombuffer(value, dtype=dtype)
        np_flat[i] = value
    return np_ary

class __dtype_con:
    
    def __init__(self, tag):
        # Whether or not to convert to hex:
        hexlify = any([x in tag for x in hex_dtypes])
        dtype = dtypes[tag]
        
        # Mutable list containing constructor & representer info
        self.fncn_attributes = [tag, hexlify, dtype]
        
        def dtype_constructor(loader, node):
            tag, hexlify, dtype = self.fncn_attributes
            if isinstance(node, yaml.nodes.SequenceNode):
                return ndarray_constructor(loader, node, dtype, hexlify=hexlify)
            else: # isinstance(node, yaml.nodes.ScalarNode):
                value = loader.construct_scalar(node)
                dtype = dtypes[node.tag[1:]]
                if hexlify:
                    value = binascii.unhexlify(value)
                    value = np.frombuffer(value, dtype=dtype)[0]
                else:
                    value = dtype(value)
                return value
        
        def dtype_representer(dumper, obj):
            tag, hexlify, dtype = self.fncn_attributes
            if isinstance(obj, float): obj = np.float64(obj)
            if hexlify: value = u'%s'%(binascii.hexlify(obj),)
            else: value = u'%s'%(obj,)
            try: tag = u'!%s'%(cls_dtypes[obj.__class__]) # 'dtype.'+obj.__class__.__name__ # bullshit...
            except KeyError: tag = ''
            node = dumper.represent_scalar(tag, value, style='')
            return node
        
        self.dtype_constructor = dtype_constructor
        self.dtype_representer = dtype_representer

keys = [x for x in dtypes.keys() if x != 'dtype.int' and x != 'dtype.bool']
print keys

n = len(keys)
print n
i=0

for tag in keys:
    dtype = __dtype_con(tag)
    dtype_constructor = dtype.dtype_constructor
    dtype_representer = dtype.dtype_representer
    Loader.add_constructor(u'!%s'%(tag,), dtype_constructor)
    Dumper.add_representer(dtypes[tag], dtype_representer)

# Precision time constructors & representers:
def ns_rep(dumper, obj):
    state = {'second': obj.__dict__['second'], 'nanosecond': obj.__dict__['nanosecond']}
    return dumper.represent_mapping(u'!timestamp_ns', state)
def ps_rep(dumper, obj):
    state = {'second': obj.__dict__['second'], 'picosecond': obj.__dict__['picosecond']}
    return dumper.represent_mapping(u'!timestamp_ps', state)
def ns_con(loader, node): return PrecisionTime.nsTime(**loader.construct_mapping(node))
def ps_con(loader, node): return PrecisionTime.psTime(**loader.construct_mapping(node))

Dumper.add_representer(PrecisionTime.nsTime, ns_rep)
Dumper.add_representer(PrecisionTime.psTime, ps_rep)
Loader.add_constructor(u'!timestamp_ns', ns_con)
Loader.add_constructor(u'!timestamp_nanosecond', ns_con)
Loader.add_constructor(u'!timestamp_ps', ps_con)
Loader.add_constructor(u'!timestamp_picosecond', ps_con)

# Binary object constructor & representer:
def bin_rep(dumper, obj): return dumper.represent_mapping(u'!binary', obj.__dict__)
def bin_con(loader, node): return DynamicObject.Binary(**loader.construct_mapping(node))
Dumper.add_representer(DynamicObject.Binary, bin_rep)
Loader.add_constructor(u'!binary', bin_con)

