'''
Created on Jul 15, 2014

@author: roj-idl71
'''

import sys
import yaml
import numpy
import jsonpickle

# import schainpy.serializer.DynamicSerializer as DynamicSerializer



def isNotClassVar(myObj):
    
    return not hasattr(myObj,'__dict__')

def isDictFormat(thisValue):
    
    if type(thisValue) != type({}):
        return False
    
    if '__name__' not in thisValue.keys():
        return False
    
    return True

def obj2Dict(myObj):
    
    myDict = {}
    
    myDict['__name__'] = myObj.__class__.__name__
    
    for thisKey, thisValue in myObj.__dict__.items():
        
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
    
    if '__name__' not in myDict.keys():
        return None
    
    className = eval(myDict['__name__'])
    
    myObj = className()
    
    for thisKey, thisValue in myDict.items():
        
        if thisKey == '__name__':
            continue
        
        if not isDictFormat(thisValue):
            setattr(myObj, thisKey, thisValue)
            continue
        
        myNewObj = dict2Obj(thisValue)
        setattr(myObj, thisKey, myNewObj)
    
    return myObj
  
class myTestClass3(object):
    
    def __init__(self):
        '''
        '''
        self.y1 = 'y1'
        self.y2 = 'y2'
              
class myTestClass2(object):
    
    def __init__(self):
        '''
        '''
        self.x1 = 'x1'
        self.x2 = 'x2'
        self.otherObj = myTestClass3()
        
        
class myTestClass(object):
    
    flagNoData = True
    value1 = 1
    value2 = 2
    myObj = None
    
    def __init__(self):
        
        '''
        '''
        self.flagNoData = True
        self.value1 = 1
        self.value2 = 2
        self.myObj = myTestClass2()
    
    def get_dtype(self):
        
        '''
        '''
        return self.value1
    
    def set_dtype(self, value):
        
        '''
        '''
        
        self.value1 = value
        
    dtype = property(get_dtype, set_dtype)

def myMsgPackTest():
    
    import msgpack
    import msgpack_numpy as m
    import numpy as np
    
    x = np.random.rand(5)
    x_enc = m.encode(x)
    x_rec = m.decode(x_enc)
    
    print x_rec
#     
#     x_enc = msgpack.packb(x, default=m.encoder)
#     x_rec = msgpack.unpackb(x_enc, object_hook=m.decoder)
    
if __name__ == '__main__':
    
    myMsgPackTest()
    
    sys.exit()
    
    serializerObj = DynamicSerializer.DynamicSerializer('json')
    serializerObj = jsonpickle
    
    myTestObj = myTestClass()
    
    myTestObj.flagNoData = False
    myTestObj.value1 = [1+3.4j,4,'5',]
    myTestObj.value2 = {'x2': numpy.complex(1,2),'x1': 'x1'}
#     myTestObj.myObj.x2 = numpy.arange(15, dtype=numpy.complex)
    
    myDict = obj2Dict(myTestObj)
    
    myNewObj = dict2Obj(myDict)
    
#     print myDict
#     print myTestObj.__dict__
#     print myNewObj.__dict__
    
#     sys.exit()
    print myDict
    
    newSerial = serializerObj.encode(myDict)
#     print newSerial
    
    newDict = serializerObj.decode(newSerial)
    print newDict
    
    myNewObj = dict2Obj(newDict)
    
    print
    print
    print 50*'###'
    print myTestObj.__dict__
    print myNewObj.__dict__
    