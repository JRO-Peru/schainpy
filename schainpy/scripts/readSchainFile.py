#!/usr/bin/env python
'''
Created on Jul 7, 2014

@author: roj-idl71
'''
import os, sys

schainpy_path = os.path.dirname(os.getcwd())
source_path = os.path.dirname(schainpy_path)
sys.path.insert(0, source_path)

from schainpy.controller_api import ControllerThread
    
def main():
    desc = "Segundo Test"
    filename = "/Users/miguel/Downloads/mst_blocks.xml"
    
    controllerObj = ControllerThread()
    controllerObj.readXml(filename)
    
    #Configure use of external plotter before start
    plotterObj = controllerObj.useExternalPlotter()
    ########################################
    
    controllerObj.start()
    plotterObj.start()
    
    
if __name__ == '__main__':
    import time
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))