'''
Created on Jul 15, 2014

@author: Miguel Urco
'''
from serializer import DynamicSerializer
 
DEFAULT_SERIALIZER = None #'cPickle', 'msgpack', "yaml"

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

def dict2Serial(myDict, serializer=DEFAULT_SERIALIZER):
     
    SERIALIZER = DynamicSerializer(serializer)
 
    mySerial = SERIALIZER.dumps(myDict)
     
    return mySerial
 
def serial2Dict(mySerial, serializer=DEFAULT_SERIALIZER):
     
    SERIALIZER = DynamicSerializer(serializer)
     
    myDict = SERIALIZER.loads(mySerial)
     
    return myDict
 
def obj2Serial(myObj, serializer=DEFAULT_SERIALIZER, **kwargs):
     
    SERIALIZER = DynamicSerializer(serializer)
         
    myDict = obj2Dict(myObj, **kwargs)
    mySerial = dict2Serial(myDict, serializer)
     
    return mySerial
 
def serial2Obj(mySerial, metadataDict = {}, serializer=DEFAULT_SERIALIZER):
     
    SERIALIZER = DynamicSerializer(serializer)
         
    myDataDict = serial2Dict(mySerial, serializer)
     
    if not metadataDict:
        myObj = dict2Obj(myDataDict)
        return myObj
 
    metadataDict.update(myDataDict)
    myObj = dict2Obj(metadataDict)
     
    return myObj
