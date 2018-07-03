'''
The DynamicObject module supports dynamic loading of YAML
defined objects into Python class objects. Object can
be sub-classed to allow direct binding of methods having
matching signatures.

$Id$
'''

import urllib.request, urllib.parse, urllib.error
import os
import re
import yaml # YAML Ain't Markup Language
import numpy as np
import copy
import inspect
import PrecisionTime
import time
import sys
import datetime
import collections

# Replacement Loader for PyYAML to keep dictionaries in-order:
import OrderedYAML
#OrderedYAML.collections

class Object(object):
    """ Loads a YAML defined python class dynamically using the supplied URI,
    which may be a file, directory, web hyper-link, or hyper-linked directory. """
    
    # Dictionary containing all known Object class names and corresponding class objects
    dynamicClasses = collections.OrderedDict()
    
    def __init__(self, object_uri=None, revision=None, recursive=False):
        if isinstance(object_uri, file):
            # URI is a yaml file - read it.
            self.yaml = file.read()
        elif object_uri == None:
            self.yaml = None
        elif isinstance(object_uri, str):
            if object_uri.endswith('.yml'):
                # URI is a web hyper-linked yaml file - read it.
                self.yaml = urllib.request.urlopen(object_uri).read()
            else:
                # URI is a (hyper-linked?) directory - try reading it.
                #print "URI is a directory."
                try:
                    self.files = self.__parseLink(object_uri, recursive)
                except IOError:
                    # URI is a local directory - get a list of YAML files in it
                    self.files = self.__getYamlFiles(object_uri, recursive)
                
                # For each YAML file found, create a new DynamicObject of it:
                self.yaml = []
                for fn in self.files:
                    self.yaml.append(Object(fn))
        else:
            print("Invalid URI supplied: %s"%(object_uri,))
        
    def __parseLink(self, object_uri, recursive):
        """ Returns a listing of all YAML files located in the
        hyper-link directory given by page. """
        page = urllib.request.urlopen(object_uri).read()
        #print "URI is a URL directory: %s"%(object_uri,)
        pattern = re.compile(r'<a href="[^"]*">')
        
        # List of files contained in the directory at the given URL, ignoring
        # any "?" / GET query-string locations given:
        files = [x[9:-2] for x in pattern.findall(page) if not x[9:-2].startswith('?')]
        #print files
        
        yamlFiles = []
        dirs = []
        for fn in files:
            if not fn.startswith('/'): # Ignore absolute paths...
                path = os.path.join(object_uri, fn)
                #print path
                
                # Keep list of YAML files found...
                if fn.endswith('.yml'):
                    yamlFiles.append(path)
                
                # Keep list of directories found...
                elif recursive and fn.endswith('/'):
                    dirs.append(path)
            
        if recursive:
            #print dirs
            for path in dirs:
                yamlFiles += self.__parseLink(path,recursive)
        
        return yamlFiles
    
    def __getYamlFiles(self, local_dir, recursive):
        """ Returns a listing of all YAML files located in the given
        directory, recursing if requested. """
        yamlFiles = []
        dirs = []
        for fn in os.listdir(local_dir):
            path = os.path.join(local_dir, fn)
            
            # List of YAML files found...
            if fn.endswith('.yml'):
                yamlFiles.append(path)
            
            # List of directories found...
            elif recursive and os.path.isdir(path):
                dirs.append(path)
        
        # Recurse if desired:
        if recursive:
            for path in dirs:
                yamlFiles += self.__getYamlFiles(path,recursive)
        
        return yamlFiles
    
    def equals(self, obj, compare_time_created=True):
        """ Returns True iff self has identical attributes
        (numerically) to obj (no extras) """
        
        if not isinstance(obj, Object): return False
        
        self_keys = list(self.__dict__.keys())
        obj_keys = list(obj.__dict__.keys())
        if not self_keys == obj_keys:
            return False
        for key in self_keys:
            obj_keys.remove(key)
            
            self_value, obj_value = self.__dict__[key], obj.__dict__[key]
            if isinstance(self_value, Object):
                if not self_value.equals(obj_value, compare_time_created):
                    return False
            elif isinstance(self_value, np.ndarray):
                m1 = list(map(repr,self_value.flat))
                m2 = list(map(repr,obj_value.flat))
                ret = m1 == m2
                if not ret:
                    return False
            else:
                if not self_value == obj_value:
                    # Return False iff the different times are important
                    return key == '__time_created' and not compare_time_created
        
        return obj_keys == [] # no more keys --> the objects are identical
    
    def sizeof(self):
        """ Recursively computes the size in bytes of the given Dynamic Object """
        sz = 0
        values = list(self.__dict__.values())
        for val in values:
            if isinstance(val, Object): sz += val.sizeof()
            elif isinstance(val, np.ndarray): sz += val.nbytes
            elif hasattr(val, 'dtype') and hasattr(val.dtype, 'itemsize'): sz += val.dtype.itemsize
            else: sz += sys.getsizeof(val)
        return sz
    
    # Automatic methods for accessing meta-data
    getters = ['__object_name', '__revision_number', '__revision_id', '__revision_source', '__revision_tag', '__time_created']
    def getObjectName(self): return self.__class__.meta_attributes['__object_name']
    def getRevisionNumber(self): return self.__class__.meta_attributes['__revision_number']
    def getRevisionId(self): return self.__class__.meta_attributes['__revision_id']
    def getRevisionSource(self): return self.__class__.meta_attributes['__revision_source']
    def getRevisionTag(self): return self.__class__.meta_attributes['__revision_tag']
    def getTimeCreated(self): return getattr(self, "__time_created")
    
    """
    __getters = [('ObjectName', getObjectName), ('RevisionNumber', getRevisionNumber),
                 ('RevisionId', getRevisionId), ('RevisionSource', getRevisionSource),
                 ('RevisionTag', getRevisionTag)]
    def __repr__(self):
        meta_atts = repr([(x[0], x[1](self)) for x in Object.__getters])
        atts = repr(self.__dict__)
        return "Object(%s, %s)"%(atts, meta_atts)
    """


class SignatureException(Exception):
    """ Exception thrown when a data or method signature is unknown or invalid
    for a particular Object. """
    def __init__(self, value): self.value = value
    def __str__(self): return repr(self.value)

class _IDLTag(object):
    """ IDLTag (aka Interface Definition Language Tag) is an abstract helper class
    used by the Factory to define built-in tags used
    specifically for our IDL """
    def __init__(self, yamlString):
        self.yamlString = yamlString
    def __repr__(self):
        return self.yamlString

class _Reference(_IDLTag):
    """ Helper class for Factory: Objects can be composed
    of other objects, requiring a Reference to the other object. """
    def __repr__(self):
        return "Ref(%s)"%(self.yamlString,)

class _Method(_IDLTag):
    """ Helper class for Factory: Objects have methods
    associated with them - this tag tells the Factory that a method
    signature follows (in dict format) """
    def __repr__(self):
        return "Method(%r)"%(self.yamlString,)

class Binary(Object):
    def __init__(self, binary_type, value=None):
        self.binary_type = binary_type
        self.value = value

import Lookup

class BuiltinDtype(_IDLTag):
    """ Helper class for Factory: Object parameters each
    have a certain data type (either dtype.xxxx for numpy compatible data
    types, or one of the generic python data types (i.e. int, bool, str...)
    
    __addYamlConstructor in Factory registers all of the tags
    listed as keys in the dtypes dictionary."""
    
    def __init__(self, yamlString, tag=None):
        self.tag = tag[1:]
        super(BuiltinDtype, self).__init__(yamlString)
        #print self.tag
        try: self.dtype = Lookup.numpy_dtypes[self.tag]
        except KeyError: self.dtype = Lookup.builtin_objects[self.tag]
    
    def __repr__(self):
        return "_BuiltinType(%s,%s)"%(self.yamlString, self.tag)

# Register hexadecimal representation of numpy dtypes in YAML

class _Parameter:
    """ Helper class for Factory: Contains the name, default
    value, and length (if an array) of an object initialization parameter. """
    
    def __init__(self, name, hasDefault=False, default=None, length=None, classType=None):
        self.name = name
        self.hasDefault = hasDefault
        self.default = default
        self.length = length
        if isinstance(classType, None.__class__) and not isinstance(default, None.__class__):
            self.classType = default.__class__
        else:
            self.classType = classType

class _UnresolvedType:
    """ Used to indicate a data type which has not yet been parsed (i.e. for
    recursive data-types. """
    
    def __init__(self, yamlObject):
        # Either the name of the class we couldn't resolve, or a dictionary
        # containing the name and a default value
        self.yamlObject = yamlObject

class UnresolvedTypeException(Exception):
    """ Raised when a !ref tag is used, but the reference cannot be resolved """
    pass

def get_class(kls):
    """ Returns a pointer to the class instance with the name kls
    Function acquired from http://stackoverflow.com/questions/452969/ """
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__( module )
    for comp in parts[1:]:
        m = getattr(m, comp)            
    return m

# Aliased constructor & representer adders for easily swapping between Ordered and non-Ordered:
def add_constructor(tag, constructor):
    #yaml.add_constructor(tag, constructor)
    OrderedYAML.Loader.add_constructor(tag, constructor)
def add_representer(cls, representer):
    #yaml.add_representer(cls, representer)
    OrderedYAML.Dumper.add_representer(cls, representer)

# Implicit constructor for _Reference objects using the !ref tag:
def __ref_constructor(loader, node):
    if isinstance(node, yaml.nodes.MappingNode):
        return _Reference(loader.construct_mapping(node))
    else:
        return _Reference(loader.construct_scalar(node))
add_constructor('!ref', __ref_constructor)

# Method constructor using !method tag:
def __method_constructor(loader, node):
    if isinstance(node, yaml.nodes.MappingNode):
        return _Method(loader.construct_mapping(node))
    else:
        return _Method(loader.construct_scalar(node))
add_constructor('!method', __method_constructor)

# Generic constructor for any _BuiltinDtype
def __dtype_constructor(loader, node):
    if isinstance(node, yaml.nodes.SequenceNode):
        ret = BuiltinDtype(loader.construct_sequence(node), tag=node.tag)
    elif isinstance(node, yaml.nodes.MappingNode):
        ret = BuiltinDtype(loader.construct_mapping(node), tag=node.tag)
    else:
        ret = BuiltinDtype(loader.construct_scalar(node), tag=node.tag)
    return ret

# Register YAML constructors for each builtin type:
for dtype in list(Lookup.numpy_dtypes.keys()) + list(Lookup.builtin_objects.keys()):
    add_constructor('!%s'%(dtype,), __dtype_constructor)

class FactoryLoader(OrderedYAML.Loader):
    """ A YAML Loader specifically designed to load YAML object definitions
    (as opposed to actual instances of the objects) """
    
    def construct_yaml_timestamp(self, node):
        """ Make empty timestamps (None/null) acceptable, otherwise parse the timestamp """
        if node.value == '':
            name = 'YAML_DEFN_LOADED_INCORRECTLY' # in case we forget to fix the name...
            return _Parameter(name, hasDefault=False, classType=datetime.datetime)
        else:
            return yaml.constructor.SafeConstructor.construct_yaml_timestamp(self, node)

# Override default timestamp constructor:
FactoryLoader.add_constructor(
        'tag:yaml.org,2002:timestamp',
        FactoryLoader.construct_yaml_timestamp
)

import DynamicYAML
class Factory:
    """ Load a YAML defined python class and create a class with initialization
    provided by this factory. This is intended as an abstract class to be sub-classed
    to enable complex initialization on object instantiation.
    
    Factory subclasses should override __buildClass()."""
    
    def __init__(self, dynamic_object=None, yaml=None, typeCheck='strong', parse=True, revision_dict=None):
        if revision_dict != None: self.revision_dict = revision_dict # Remember for when we build each individual class
        else:
            self.revision_dict = {\
              "__revision_number": 0,
              "__revision_id": 'unknown',
              "__revision_source": 'unknown',
              "__revision_tag": 'unknown'}
        if parse:
            if dynamic_object:
                self.parse(dynamic_object, typeCheck=typeCheck)
            else:
                dyno = Object()
                dyno.yaml = yaml
                self.parse(dyno, typeCheck=typeCheck)
    
    def parse(self, dynamic_object, typeCheck='strong'):
        """
        Initializer for a Factory, converting the given dynamic_object
        containing a (text) YAML object definition into the corresponding class-type
        with initializer.
        
        typeCheck parameter can be one of 'strong' or 'cast':
            'strong': Class initializer should raise a TypeError when given
            anything but the correct type
            'cast': Class initializer should attempt to cast any input to the correct type
        """
        
        # Remember what kind of type-checking to do:
        if typeCheck not in ['strong', 'cast']:
            raise Exception('Incorrect input for typeCheck: %s\nExpected "strong" or "cast"'%(typeCheck))
        self.typeCheck = typeCheck
        
        # Get a list of the objects to build:
        if isinstance(dynamic_object.yaml, list):
            objects = dynamic_object.yaml
        else:
            objects = [dynamic_object]
        
        # Generate a dictionary of classes from the DynamicObjects given:
        self.classes = dict()
        for obj in objects:
            
            # This loader breaks nothing anymore #everything currently
            loader = FactoryLoader(obj.yaml)
            #loader = yaml.Loader(obj.yaml)
            
            # Dictionary with method and data signatures for the current object:
            objDefn = []
            while loader.check_data():
                objDefn.append(loader.get_data())
            loader.dispose()
            
            # Parse the dictionary into a class definition:
            objClass = self.__buildClass(objDefn)
            self.classes.update(objClass)
    
    def parseMethodSignature(self, sigName, methDict):
        """ Returns the python method corresponding to the given signature 
        (given signature should be in the loaded YAML dict format.
        
        Override this method for recognizing complex method signatures. """
        
        raise SignatureException("Object abstract base class doesn't support any method signatures.")
    
    def parseDataSignature(self, sigName, sig):
        """ Returns the Parameter object corresponding to the given signature.
        
        This method should be overridden for recognizing complex data signatures
        (don't forget to call super(sig) for built-in data types though!) """
        
        # Is the object an array with explicit default elements?:
        if isinstance(sig.yamlString, list):
            #length = len(sig.yamlString)
            if 'dtype' in sig.tag:
                default = np.array(sig.yamlString, dtype=sig.dtype)
            elif 'binary' == sig.tag:
                default = Binary(sig.yamlString["type"])
            else:
                default = sig.yamlString
            return _Parameter(sigName, True, default, length=None)
        
        # Is the object an array with length and default value given?:
        if isinstance(sig.yamlString, dict) and "len" in list(sig.yamlString.keys()):
            length = sig.yamlString["len"]
            
            # Shape is given as something like [[],[]], not [2,2] - convert
            if isinstance(length, list):
                
                def get_shape(lst):
                    """ Gets the shape of a list recursively filled with empty lists """
                    if lst == []: return [0]
                    return [len(lst)] + get_shape(lst[0])
                    
                if len(length) > 0:
                    if isinstance(length[0], list):
                        length = get_shape(length)
                    else:
                        pass
                else:
                    length = [0] # convert [] to [0] (numpy interprets [] as [1] for shapes)
                        
            
            if 'complex' in sig.tag:
                imag = sig.yamlString["default"]["imag"]
                real = sig.yamlString["default"]["real"]
                default = sig.dtype(real) + sig.dtype(imag*1j)
            elif 'binary' == sig.tag:
                default = Binary(sig.yamlString["type"])
            else:
                default = sig.dtype(sig.yamlString["default"])
            
            return _Parameter(sigName, True, default, length)
        
        # The object is singular, with a given value:
        if 'complex' in sig.tag:
            imag = sig.yamlString["imag"]
            real = sig.yamlString["real"]
            default = sig.dtype(real) + sig.dtype(imag*1j)
            return _Parameter(sigName, True, default)
        elif 'binary' == sig.tag:
            default = Binary(sig.yamlString["type"])
            return _Parameter(sigName, False, default, classType=Binary)
        elif 'timestamp' in sig.tag:
            if isinstance(sig.yamlString, dict):
                if sig.tag in ['timestamp_picosecond', 'timestamp_ps']:
                    try: s = sig.yamlString['second']
                    except KeyError: s = sig.yamlString['s']
                    try: ps = sig.yamlString['picosecond']
                    except KeyError: ps = sig.yamlString['ps']
                    return _Parameter(sigName, True, PrecisionTime.psTime(s, ps))
                elif sig.tag in ['timestamp_nanosecond', 'timestamp_ns']:
                    try: s = sig.yamlString['second']
                    except KeyError: s = sig.yamlString['s']
                    try: ns = sig.yamlString['nanosecond']
                    except KeyError: ns = sig.yamlString['ns']
                    return _Parameter(sigName, True, PrecisionTime.nsTime(s, ns))
            else:
                if sig.tag in ['timestamp_picosecond', 'timestamp_ps']:
                    return _Parameter(sigName, False, classType=PrecisionTime.psTime)
                elif sig.tag in ['timestamp_nanosecond', 'timestamp_ns']:
                    return _Parameter(sigName, False, classType=PrecisionTime.nsTime)
        else:
            default = sig.dtype(sig.yamlString)
            return _Parameter(sigName, True, default) # not binary
    
    
    
    def __parsePythonType(self, sigName, sig):
        """ Returns a _Parameter object, similar to parseDataSignature, but
        for a basic python type. """
        
        if isinstance(sig, collections.OrderedDict):
            default = dict(sig) # Type-check user-defined !!maps as dicts, not OrderedDicts.
        else:
            default = sig # The signature sig is the default value itself
        return _Parameter(sigName, True, default)
    
    def __parseReferenceSignature(self, sigName, ref_object, objClasses):
        """ Takes a reference object ref_object to be named sigName, and
        produces a _Parameter object with default value of None. """
        
        # List of names of classes we've created so far:
        #print [x for x in objClasses]
        names = list(objClasses.keys())
        
        if ref_object.yamlString in names:
            defaultType = objClasses[ref_object.yamlString]
            return _Parameter(sigName, classType=defaultType)
        else:
            try:
                # Try to find the class type in globals:
                className = objClasses[str(ref_object.yamlString)]
                defaultType = get_class(className)
            except (ValueError, KeyError):
                defaultType = _UnresolvedType(ref_object.yamlString)
                #raise NameError("Invalid reference to module %s"%(className,))
            
            return _Parameter(sigName, classType=defaultType)
    
    def __buildInitializer(self, className, classData):
        """ Constructs the initializer for an object which expects parameters
        listed in classData as input upon initialization. """
        
        # Type of type-checking to use:
        strong = (self.typeCheck == 'strong')
        #cast = (self.typeCheck == 'cast')
        
        def typeCheck(param, arg):
            """
            Checks to see if the type of arg matches that of the corresponding param,
            casting arg to the correct type if desired.
            """
            if isinstance(arg, param.classType): return arg
            if isinstance(arg, np.ndarray) and arg.dtype.type == param.classType:
                if not param.hasDefault: return arg
                if param.default.shape == (): return arg
                if param.default.shape[-1] == 0: return arg
                if arg.shape == param.default.shape: return arg
            if isinstance(arg, None.__class__): return arg
            if strong:
                raise TypeError("Incorrect input type on strong type-checking."+\
                " Expected %s - got %s"%(param.classType,arg.__class__))
            else:
                # If the parameter corresponding to the given argument has a non-NoneType default
                # value, then attempt to cast the argument into the correct parameter type
                if param.hasDefault and param.default != None:
                    if isinstance(param.default, np.ndarray):
                        return np.array(arg, dtype=param.default.dtype)
                    else:
                        return param.default.__class__(arg)
                else:
                    return param.classType(arg)
        
        """
        attributes = {"__object_name": className,
                      "__revision_number": self.svn_revision_number,
                      "__revision_id": 'unknown',
                      "__revision_source": 'unknown',
                      "__revision_tag": 'unknown'}
        """
        attributes = {} # Create new attributes dict for this particular class object
        attributes.update(self.revision_dict) # Revision info now passed into the factory
        attributes['__object_name'] = className
        
        def init(_self, *args, **kwargs):
            """ Dynamically generated initializer. """
            
            # meta-data goes in the class, not the objects (commented the following out):
            """
            # Initialize automatic class data
            for attr,value in attributes.items():
                try:
                    value = kwargs[attr] # Are we given a value to over-ride with?
                    del kwargs[attr] # Ignore the meta attribute later
                except KeyError:
                    pass
                setattr(_self, attr, value)
            """
            
            # Set default values first (assume no parameters):
            for param in classData:
                if param.length:
                    if isinstance(param.length, int): param.length = [param.length]
                    default = np.empty(param.length, dtype=param.classType)
                    if param.hasDefault:
                        # Initialize array with default array value given:
                        flatIter = default.flat
                        for i in range(len(flatIter)):
                            flatIter[i] = copy.deepcopy(param.default)
                    else:
                        # Initialize to None if no default given:
                        default.fill(None)
                else:
                    default = param.default
                setattr(_self, param.name, copy.deepcopy(default))
            
            # Set attributes given by standard args:
            for i in range(len(args)):
                arg = typeCheck(classData[i], args[i])
                setattr(_self, classData[i].name, arg)
            
            # Set named attributes (given by dictionary kwargs):
            for key,value in list(kwargs.items()):
                
                try: keyIndex = [param.name for param in classData].index(key)
                except ValueError:
                    raise TypeError("'%s' is an invalid keyword argument"%(key,))
                arg = typeCheck(classData[keyIndex],value)
                #setattr(_self, key, value)
                setattr(_self, key, arg)
            

            # Object instantiation / creation time (if not already present):
            if '__time_created' not in kwargs:
                setattr(_self, "__time_created", np.float64(time.time()))
        
        return init, attributes
    
    def __findClass(self, className, localClasses):
        """ Looks for the given className first in the given dictionary of localClasses
        then in the global definitions, returning the corresponding class object. Raises
        a KeyError if the class cannot be found. """
        
        # If class definition was in the YAML file, extend that one:
        if className in list(localClasses.keys()):
            return localClasses[className]
        
        # Else try finding the class definition in our global scope:
        try: classObj = get_class(className)
        except KeyError:
            raise KeyError("Class '%s' not found in given YAML scope or global scope."%(className,))
        return classObj
    
    def __buildClass(self, objDefn):
        """ Takes an object definition list / dictionary objDefn (loaded from a YAML
        object definition file) and creates a class, dynamically binding
        method and data signatures to the new class.
        
        This method only performs a basic binding of method and data signatures to
        the new class. Object(s) having more complex initialization requirements
        should be given their own Factory subclass, overriding this
        and other methods."""
        
        # objDefn is a list of dictionaries found in the YAML file - build each one...
        objClasses = dict()
        objClassesRev = dict()
        
        # A list of all _Parameter objects created, used to resolve recursive
        # or "tangled" data structures
        allClassData = []
        
        for document in objDefn:
            # Each document can contain multiple objects - build each one.
            # (NOTE: objects can cross reference each other in the same document
            # need to resolve Reference objects as last step)
            for objClassName in list(document.keys()):
                
                # The dictionary containing method & data signatures:
                objDict = document[objClassName]
                
                # Extract data / attribute definitions (signatures) from the YAML dictionary
                # as well as method signatures and which classes this class extends:
                classData = []
                classMethods = dict()
                classBases = [Object]
                
                # List structured documents result in a list of dicts each with one key:
                if isinstance(objDict, list): keys = [list(param.keys())[0] for param in objDict]
                # Otherwise the parameter names are just the  keys of the dict
                else: keys = list(objDict.keys())   # if key not found, raises AttributeError
                   
                for sigName in keys:
                    #print sigName
                    sig = objDict[sigName]
                    #for f in _BuiltinDtype.python_dtypes: print f.__class__
                    if sigName == '__extends':
                        if isinstance(sig, str):
                            sig = [sig]
                        if isinstance(sig, list):
                            for className in sig:
                                newBase = self.__findClass(className, objClasses)
                                
                                # Remove Object extension if newBase extends it already:
                                if Object in classBases and Object in inspect.getmro(newBase):
                                    classBases.remove(Object)
                                classBases += [newBase]
                        else:
                            raise TypeError("Incorrect format for extending classes - %s"%(sig,))
                    elif isinstance(sig, BuiltinDtype):
                        classData.append(self.parseDataSignature(sigName, sig))
                    elif isinstance(sig, Lookup.python_dtypes):
                        classData.append(self.__parsePythonType(sigName, sig))
                    elif isinstance(sig, _Reference):
                        classData.append(self.__parseReferenceSignature(sigName, sig, objClasses))
                    elif isinstance(sig, _Method):
                        classMethods[sigName] = self.parseMethodSignature(sigName, sig.yamlString)
                    elif isinstance(sig, (PrecisionTime.nsTime, PrecisionTime.psTime)):
                        classData.append(_Parameter(sigName, True, sig))
                    elif isinstance(sig, _Parameter): # sig is already a parameter (we skipped a step)
                        sig.name = sigName # we didn't know the name during load time - fill that in now
                        classData.append(sig)
                    else:
                        msg = "Factory abstract base class doesn't " +\
                        "support the following signature: %r \"%s\""%(sig.__class__,str(sig))
                        print(sig.__class__)
                        raise SignatureException(msg)
                
                # Built-in attribute for all Dynamic Objects:
                classData.append(_Parameter('__time_created', classType=np.float64))
                
                # Turn the object data / attributes into a usable __init__ method:
                classMethods["__init__"], meta_attributes = self.__buildInitializer(objClassName, classData)
                
                # Keep a record of the _Parameters created for later type resolution
                allClassData.extend(classData)
                
                """
                __automaticMethods = {
                        "getObjectName": lambda _self: getattr(_self, '__object_name'),
                        "getRevisionNumber": lambda _self: getattr(_self, '__revision_number'),
                        "getRevisionId": lambda _self: getattr(_self, '__revision_id'),
                        "getRevisionSource": lambda _self: getattr(_self, '__revision_source'),
                        "getRevisionTag": lambda _self: getattr(_self, '__revision_tag')
                }
                classMethods.update(__automaticMethods)
                """
                
                # Put the method signatures into a namespace for the new class,
                # then dynamically build the class from this namespace.
                classNamespace = classMethods
                classNamespace["meta_attributes"] = meta_attributes
                cls = type(str(objClassName), tuple(classBases), classNamespace)
                objClasses[objClassName] = cls
                objClassesRev['%s.%s'%(objClassName,cls.meta_attributes["__revision_number"])] = cls
                
                # Create and register a constructor (loading) and representer (dumping) for the new class cls
                def construct_dynamic_object(loader, node):
                    kwargs = loader.construct_mapping(node)
                    # Remove revision control from loaded objects (info is in the class object!)
                    for arg in list(kwargs.keys()):
                        if arg in getattr(Object, 'getters') and arg != '__time_created':
                            del kwargs[arg]
                    return cls(**kwargs)
                revision = cls.meta_attributes["__revision_number"]
                DynamicYAML.Loader.add_constructor('!%s.%s'%(str(objClassName),revision), construct_dynamic_object)
                
                represent_dynamic_object = DynamicYAML.Dumper.represent_dynamic_object
                DynamicYAML.Dumper.add_representer(cls, represent_dynamic_object)
        
        def findClass(className):
            """ Search for the most recently added class object with given className """
            try:
                return objClasses[className] # Look for reference to object in same YAML defn file:
            except KeyError:
                # Now look for reference to class object loaded from any YAML defn file, loading the
                # most recent version / revision (number) of the definition
                for dynClass in list(Object.dynamicClasses.keys())[::-1]:
                    if dynClass.startswith(className):
                        return Object.dynamicClasses[dynClass]
                    
                # Still unresolved - raise exception:
                allDynamicClasses = repr(list(objClasses.keys()) + list(Object.dynamicClasses.keys()))
                raise UnresolvedTypeException("Cannot resolve type '%s': Name not found in %s"%(className,allDynamicClasses))

        
        def resolve(param):
            
            # Reference is just a string - that's the class name:
            if isinstance(param.classType.yamlObject, str):
                className = str(param.classType.yamlObject)
                param.classType = findClass(className)
                return
            
            # Reference is a dict containing class name and / or default values:
            if not isinstance(param.classType.yamlObject, dict):
                raise UnresolvedTypeException("Cannot resolve reference of type '%s'"%(param.classType.yamlObject.__class__,))
            
            # Definitely a dict:
            refDict = param.classType.yamlObject
            
            # Determine the name of the class being referenced
            try:
                className = refDict["type"]
            except KeyError:
                raise KeyError("No 'type' key in reference dictionary for parameter '%s'"%(param.name,))
            
            # Determine the class object corresponding to the class name
            param.classType = findClass(className)
            
            try:
                defaultParams = refDict["default"]
            except KeyError:
                defaultParams = None
            
            if defaultParams != None:
                for sub_param in defaultParams:
                    if isinstance(sub_param.classType, _UnresolvedType):
                        resolve(sub_param)
                param.default = param.classType( **defaultParams ) # Create the default object
                param.hasDefault = True
            else:
                param.hasDefault = False # for good measure
            
            # Is it an object array?:
            if "len" in list(refDict.keys()):
                param.length = refDict["len"]
        
        # Resolve any unresolved data-types:
        for param in allClassData:
            if isinstance(param.classType, _UnresolvedType):
                resolve(param)
        
        Object.dynamicClasses.update(objClassesRev)
        return objClasses

def load_defn(yaml):
    """ Shortcut for producing a single DynamicObject class object from
    the provided yaml definition in string format """
    return list(Factory(yaml=yaml).classes.values())[0]


