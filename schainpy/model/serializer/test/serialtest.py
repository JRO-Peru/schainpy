   
#
# when Serializer is imported alone, fault indicates this package is 
# dependent on lookup, but don't import Lookup, instead:
# 
import DynamicObject # dependent on pysvn
import Serializer    # dependent on Dynamic Object

import msgpack
import redis

import numpy as np

class NamedObject():

  #---------------------------------------------
  @staticmethod  
  def indexListMatch(list_of_lists, name, value, name2=None, value2=None, unique_f=False):
       #
       # for each list's <element> attribute compare with value
       # if match, return  True plus list
       # else return  False plus empty list
       # 
       # search needs to be named part of class for object else .<value> is unrecognized
       #
       # unique_f finds non-uniqueness
    
  
       index = []                       # return empty indices
       list_data = []                   # return empty list
       ii = 0
       for theList in list_of_lists:
      
         cmd0 = "theList.%s == value" % (name)
         cmd1 = "isInlist(theList.%s,value)" % name
                                   # if name is valid then 
                                   # match name against value
                                   # match name (as list) against value                          
         if (eval(cmd0) or eval(cmd1)):                            
           if (name2 != None):
              cmd2 = "theList.%s == value2" % name2
              cmd3 = "isInlist(theList.%s,value2)" % name2
              if (eval(cmd2) or eval(cmd3)):
                 if (unique_f):
                   index = index + [ii]
                   list_data = list_data + [theList]   # save list of lists if non-unique
                                                       # don't exit on match, may be non-unique
                 else:
                   list_data = theList                 # save the list
                   index = [ii]
                   break 
           else:
             if (unique_f): 
               index = index + [ii]
               list_data = list_data +  [theList]      # list of lists if non-unique
             else:
               list_data = theList 
               index = [ii]
               break                                   # exit on match   
         #endif  
         ii = ii + 1             
       #end for
      
       return index, list_data      # return indices of matches and list (or list of lists)
    
  #end indexListMatch

  #---------------------------------------------
  @staticmethod  
  def namedListMatch(list_of_lists, name, value, name2=None, value2=None, unique_f=None):
       #
       # for each list's <element> attribute compare with value
       # if match, return  True plus list
       # else return  False plus empty list
       # 
       # search needs to be named part of class for object else .<value> is unrecognized
       #
       # unique_f finds non-uniqueness ('None' is same as False)
 
       match_f = False
       list_data = []                   # initialize
    
       for theList in list_of_lists:
      
         cmd0 = "theList.%s == value" % (name)
         cmd1 = "isInlist(theList.%s,value)" % name
                                   # if name is valid then 
                                   # match name against value
                                   # match name (as list) against value                          
         if (eval(cmd0) or eval(cmd1)):                            
           if (name2 != None):
              cmd2 = "theList.%s == value2" % name2
              cmd3 = "isInlist(theList.%s,value2)" % name2
              if (eval(cmd2) or eval(cmd3)):
                 match_f = True
                 if (unique_f):
                   list_data = list_data + [theList]   # save list of lists if non-unique
                                                       # don't exit on match, may be non-unique
                 else:
                   list_data = theList                 # save the list
                   break 
           else:
             match_f = True 
             if (unique_f): 
               list_data = list_data +  [theList]      # list of lists if non-unique
             else:
               list_data = theList 
               break                                   # exit on match   
         #endif               
       #end for
      
       return match_f, list_data      # return match, and list (or list of lists)
    
  #end namedListMatch
  
  #---------------------------------------------
  @staticmethod  
  def combineLists(object):
       #
       # used for dumping elements in list of lists for debugging
       #
       ret_list =[]
       ii = 0
       while ii < len(object):
         ret_list = ret_list + [object[ii].list] # not a real list, so can't use built-in list iterator
         ii = ii + 1
       return ret_list
    
  # end combineLists 



class StateListObject(NamedObject):   
    def __init__(self, concurrent=None, hierarchical=None, history=None, state=None):
       self.concurrent    = concurrent        
       self.hierarchical = hierarchical     
       self.history      = history
       self.state        = state
       self.list = [self.concurrent, self.hierarchical, self.history, self.state  ] 
#end class StateListObject  

source_object = "my test string"

serializer = "yaml"
# 
# python versioning issue (ver 2.7 -> else path)
#
if isinstance(serializer,Serializer.Serializer):
  serial_type = Serializer.serial_types[serializer]
else:
  serial_type = serializer
  serializer = Serializer.serializers[serializer]()
  


datastr = serializer.toSerial(source_object)

dest_object = serializer.fromSerial(datastr)

print("dest_object=",dest_object)

myObject = StateListObject(hierarchical="yes",state=np.array([1,2,3.0]))

datastr = serializer.toSerial(myObject)

packed = msgpack.packb(datastr)

try:
  r= redis.StrictRedis(host='localhost',port=6379,db=0)
except Exception as eobj:
  print("is the redis server running?",eobj)
else:

  r.set('baz',packed)   # converts to string
  x  = r.get('baz')

unpacked = msgpack.unpackb(x)

dest_object = serializer.fromSerial(unpacked)

print("val1=",dest_object.hierarchical)
val2 = dest_object.state
print("val2=",val2)
# can numpy array be used as array?
print(val2.shape)

