'''
Created on Jul 11, 2014

@author: roj-idl71
'''

import zerorpc

if __name__ == '__main__':
    c = zerorpc.Client()
    c.connect("tcp://127.0.0.1:4242")
    c.load("file2") # AAAHH! The previously loaded model gets overwritten here! 
    print c.getModelName()