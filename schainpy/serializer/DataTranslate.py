'''
Created on Jul 15, 2014

@author: Miguel Urco
'''
from JROSerializer import DynamicSerializer

PICKLE_SERIALIZER = DynamicSerializer('cPickle')
MSGPACK_SERIALIZER = DynamicSerializer('msgpack')

from schainpy.model.data.jrodata import *

CLASSNAME_KEY = 'classname__'

def isNotClassVar(myObj):
    
    return not hasattr(myObj,'__dict__')

def isDictFormat(thisValue):
    
    if type(thisValue) != type({}):
        return False
    
    if CLASSNAME_KEY not in thisValue.keys():
        return False
    
    return True

def obj2Dict(myObj, keyList=[]):
    
    if not keyList:
        keyList = myObj.__dict__.keys()
        
    myDict = {}
    
    myDict[CLASSNAME_KEY] = myObj.__class__.__name__
    
    for thisKey, thisValue in myObj.__dict__.items():
        
        if thisKey not in keyList:
            continue
        
        if isNotClassVar(thisValue):
            myDict[thisKey] = thisValue
            continue
        
        ## If this value is another class instance
        myNewDict = obj2Dict(thisValue)
        myDict[thisKey] = myNewDict
        
    return myDict

def dict2Obj(myDict):
    '''
    '''
    
    if CLASSNAME_KEY not in myDict.keys():
        return None
    
    className = eval(myDict[CLASSNAME_KEY])
    
    myObj = className()
    
    for thisKey, thisValue in myDict.items():
        
        if thisKey == CLASSNAME_KEY:
            continue
        
        if not isDictFormat(thisValue):
            setattr(myObj, thisKey, thisValue)
            continue
        
        myNewObj = dict2Obj(thisValue)
        setattr(myObj, thisKey, myNewObj)
    
    return myObj

def obj2Serial(myObj, serializer='msgpack', **kwargs):
    
    if serializer == 'cPickle':
        SERIALIZER = PICKLE_SERIALIZER
    else:
        SERIALIZER = MSGPACK_SERIALIZER
        
    myDict = obj2Dict(myObj, **kwargs)
    mySerial = SERIALIZER.dumps(myDict)
    
    return mySerial

def serial2Dict(mySerial, serializer='msgpack'):
    
    if serializer == 'cPickle':
        SERIALIZER = PICKLE_SERIALIZER
    else:
        SERIALIZER = MSGPACK_SERIALIZER
        
    return SERIALIZER.loads(mySerial)

def serial2Obj(mySerial, metadataDict = {}, serializer='msgpack'):
    
    if serializer == 'cPickle':
        SERIALIZER = PICKLE_SERIALIZER
    else:
        SERIALIZER = MSGPACK_SERIALIZER
        
    myDataDict = SERIALIZER.loads(mySerial)
    
    if not metadataDict:
        myObj = dict2Obj(myDataDict)
        return myObj

    metadataDict.update(myDataDict)
    myObj = dict2Obj(metadataDict)
    
    return myObj