#
# rps 6/9/2014
# mit haystack obs
#
# wrapper for Karl's code

import DynamicObject     # used for serial/deserial of complex python objects
import Serializer        # used for serial/deserial of complex python

#
class DynamicSerializer:
    #
    #------------------------------------------------------
    #
    def __init__(self,which='yaml'):
        #
        # choices are: yaml, msgpack, hdf5, json
        #
        self.err_f = False
        self.whichList = ['yaml', 'msgpack', 'hdf5', 'json'] # from Serialzer.py
        self.err_f,self.serializer = self.initSerializer(which)
    #
    #------------------------------------------------------
    #
    def initSerializer(self,which):
        #
        # calls REU student code that works but hasn't been walked-through
        # it's a dynamic serializer not strictly a yaml serializer
        #
        err_f = False
        match_f = False
        serializer = None
        ii = 0
        while ii < len(self.whichList):
            if (self.whichList[ii] == which):
                match_f = True
                break
            ii = ii + 1
        # end while
        if not match_f:
            err_f = True
        else:
            serializer = which
            serializer = Serializer.serializers[serializer]()
    
        return err_f,serializer
        # end initSerializer
        #
        # --------------------------------------------------
        #
    def loads(self,element):   # borrows name from json module (json - to - python)
        retval = self.serializer.fromSerial(element)  # de-serialize
        return retval
    # end loads
    #
    # --------------------------------------------------
    #
    def dumps(self,element):  # borrows name from json module (python - to - json)
        retval = self.serializer.toSerial(element)  # serialize
        return retval
    # end dumps
    #
    # --------------------------------------------------
    #
# end class DynamicSerializer

if __name__ == "__main__":
    DynamicSerializer()
    print("DynamicSerializer ran")