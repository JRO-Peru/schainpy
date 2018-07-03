'''
Created on Jul 15, 2014

@author: roj-idl71
'''

import sys
import pickle

from schainpy.model.data.jrodata import Voltage
# from schainpy.model.io.jrodataIO import USRPReaderMP
from schainpy.serializer.DynamicSerializer import  DynamicSerializer
from schainpy.serializer.DataTranslate import obj2Dict, dict2Obj


if __name__ == "__main__":
    
    serializerObj = DynamicSerializer('yaml')
    
    myTestObj = Voltage()
    
    myDict = obj2Dict(myTestObj)
    
    myNewObj = dict2Obj(myDict)
    
#     print myDict
#     print myTestObj.__dict__
#     print myNewObj.__dict__
#     
#     print
#     print '#############################'
#     print
#     newValue = serializerObj.dumps(myDict)
#     print newValue
#     
#     newValue = serializerObj.loads(newValue)
#     print newValue
    
    
    print('###########CPICKLE##################')
    print(myDict)
    newSerialized = pickle.dumps(myDict, 2)
#     print newValue
    
    newDict = pickle.loads(newSerialized)
    print(newDict)