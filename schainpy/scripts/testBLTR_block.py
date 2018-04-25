'''
Created on Nov 09, 2016

@author: roj- LouVD
'''
import os, sys
from time import sleep


path = os.path.split(os.getcwd())[0]
path = os.path.split(path)[0]

sys.path.insert(0, path)

from schainpy.controller import Project

filename = 'test1.xml'
# path = '/home/jespinoza/workspace/data/bltr/'
path = '/data/BLTR/nuevos_datos/'#'/media/erick/6F60F7113095A154/BLTR/'    
desc = "read bltr data sswma file"
figpath = '/data/BLTR/nuevos_datos/' 
pathhdf5 = '/tmp/'


controller = Project()
controller.setup(id = '195', name='test1', description=desc)
receiver = controller.addProcUnit(name='PlotterReceiver')
receiver.addParameter(name='plottypes', value='output')
receiver.addParameter(name='localtime', value='0', format='int')

op = receiver.addOperation(name='PlotWindProfilerData', optype='other')
op.addParameter(name='save', value=figpath)
op.addParameter(name='bgcolor', value='white')
op.addParameter(name='localtime', value='0', format='int')
op.addParameter(name='zlimits', value='(-20,20),(-20,20),(-2,2)', format='pairslist')

controller.start()



