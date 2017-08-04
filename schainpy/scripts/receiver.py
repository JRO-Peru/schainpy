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

    proc1 = controllerObj.addProcUnit(name='PlotterReceiver')
    proc1.addParameter(name='plottypes', value='rti,dop,snr,phase,coh', format='str')
    proc1.addParameter(name='interactive', value='0', format='bool') # ? PREGUNTAR
    # proc1.addParameter(name='server', value='tcp://10.10.10.82:7000', format='str')
    ## TODO Agregar direccion de server de publicacion a graficos como variable

    op2 = proc1.addOperation(name='PlotCOHData', optype='other')
    op2.addParameter(name='wintitle', value='HF System Coh', format='str')
    op2.addParameter(name='zmin', value='0.001', format='float')
    op2.addParameter(name='zmax', value='1', format='float')
    op2.addParameter(name='save', value='/home/ci-81/Pictures', format='str')
    op2.addParameter(name='colormap', value='jet', format='str')
    op2.addParameter(name='show', value='1', format='bool')

    op3 = proc1.addOperation(name='PlotSNRData', optype='other')
    op3.addParameter(name='wintitle', value='HF System SNR0', format='str')
    op3.addParameter(name='save', value='/home/ci-81/Pictures', format='str')
    op3.addParameter(name='show', value='1', format='bool')
    op3.addParameter(name='zmin', value='-10', format='int')
    op3.addParameter(name='zmax', value='30', format='int')
    op3.addParameter(name='SNRthresh', value='0', format='float')
    op3.addParameter(name='ind_plt_ch',value='1',format = 'bool')


    op5 = proc1.addOperation(name='PlotDOPData', optype='other')
    op5.addParameter(name='wintitle', value='HF System DOP', format='str')
    op5.addParameter(name='save', value='/home/ci-81/Pictures', format='str')
    op5.addParameter(name='show', value='1', format='bool')
    op5.addParameter(name='zmin', value='-140', format='float')
    op5.addParameter(name='zmax', value='140', format='float')
    op5.addParameter(name='colormap', value='RdBu_r', format='str')
    op5.addParameter(name='ind_plt_ch',value='1',format = 'bool')
    '''
    *** WARNING ***
    tanto Phase como Coherencia usan los 2 canales de data, por ende la variable ind_plt_ch siempre
    deberia ser 0, para que no trate de separarlas, << esta hardcodeado >>
    '''
    op6 = proc1.addOperation(name='PlotPHASEData', optype='other')
    op6.addParameter(name='wintitle', value='HF System', format='str')
    op6.addParameter(name='colormap', value='RdBu_r', format='str')
    op6.addParameter(name='zmin', value='-180', format='float')
    op6.addParameter(name='zmax', value='180', format='float')
    op6.addParameter(name='save', value='/home/ci-81/Pictures', format='str')
    op6.addParameter(name='show', value='1', format='bool')
    op6.addParameter(name='ind_plt_ch',value='0',format = 'bool')
    """ """
    controllerObj.start()
