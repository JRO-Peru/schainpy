#!/usr/bin/env python
'''
Created on Jul 7, 2014

@author: roj-idl71
'''
import os, sys

from schainpy.controller import Project

if __name__ == '__main__':
    desc = "Segundo Test"

    controllerObj = Project()
    controllerObj.setup(id='191', name='test01', description=desc)

    proc1 = controllerObj.addProcUnit(name='ReceiverData')
    # proc1.addParameter(name='server', value='tcp://10.10.10.87:3000', format='str')
    proc1.addParameter(name='realtime', value='1', format='bool')
    proc1.addParameter(name='plottypes', value='spc', format='str')

    # op1 = proc1.addOperation(name='PlotRTIData', optype='other')
    # op1.addParameter(name='wintitle', value='Julia 150Km', format='str')
    #
    op2 = proc1.addOperation(name='PlotSpectraData', optype='other')
    op2.addParameter(name='wintitle', value='Julia 150Km', format='str')
    # op2.addParameter(name='xaxis', value='velocity', format='str')
    # op2.addParameter(name='showprofile', value='1', format='bool')
    #op2.addParameter(name='xmin', value='-0.1', format='float')
    #op2.addParameter(name='xmax', value='0.1', format='float')

    # op1 = proc1.addOperation(name='PlotPHASEData', optype='other')
    # op1.addParameter(name='wintitle', value='Julia 150Km', format='str')

#     proc1 = controllerObj.addProcUnit(name='ReceiverData')
#     proc1.addParameter(name='server', value='pipe2', format='str')
#     proc1.addParameter(name='mode', value='buffer', format='str')
#     proc1.addParameter(name='plottypes', value='snr', format='str')


    controllerObj.start()
