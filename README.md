# Signal Chain

## Introduction

Signal Chain (SCh) is a radar data processing library developed using [Python](www.python.org) at JRO. SCh provides modules to read, write, process and plot data.

## Installation

Install system dependencies, download the latest stable release from [svn](http://jro-dev.igp.gob.pe/svn/jro_soft/schain/Releases/) e.g. schainpy-2.2.5.tar.gz. and install it as a normal python package.

```
$ sudo apt-get install python-pip python-dev gfortran libpng-dev freetype* libblas-dev liblapack-dev libatlas-base-dev python-qt4 python-tk libssl-dev libhdf5-dev
$ tar xvzf schainpy-2.2.5.tar.gz
$ cd schainpy-2.2.5
$ sudo pip install ./
```

**Its recommended to install schain in a virtual environment**

```
$ sudo pip install virtualenv
$ virtualenv /path/to/virtual --system-site-packages
$ source /path/to/virtual/bin/activate
(virtual) $ cd schainpy-2.2.5
(virtual) $ pip install ./
```

## First Script

Read Spectra data (.pdata) - remove dc - plot spectra & RTI

Import SCh and creating a project

```python
#!/usr/bin/python

from schainpy.controller import Project

controller = Project()
controller.setup(id = '100',
                 name='test',
                 description='Basic experiment')


```

Adding read unit and operations

```python
read_unit = controller.addReadUnit(datatype='Spectra',
                                   path='/path/to/pdata/',
                                   startDate='2014/01/31',
                                   endDate='2014/03/31',
                                   startTime='00:00:00',
                                   endTime='23:59:59',
                                   online=0,
                                   walk=0)

proc_unit = controller.addProcUnit(datatype='Spectra',
                                   inputId=read_unit.getId())

op = proc_unit.addOperation(name='selectChannels')
op.addParameter(name='channelList', value='0,1', format='intlist')

op = proc_unit.addOperation(name='selectHeights')
op.addParameter(name='minHei', value='80', format='float')
op.addParameter(name='maxHei', value='200', format='float')

op = proc_unit.addOperation(name='removeDC')

```

Plotting data & start project

```python
op = proc_unit.addOperation(name='SpectraPlot', optype='other')
op.addParameter(name='id', value='1', format='int')
op.addParameter(name='wintitle', value='Spectra', format='str')

op = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
op.addParameter(name='id', value='2', format='int')
op.addParameter(name='wintitle', value='RTI', format='str')

controller.start()

```

Full script


```python
#!/usr/bin/python

from schainpy.controller import Project

controller = Project()
controller.setup(id = '100',
                 name='test',
                 description='Basic experiment')
read_unit = controller.addReadUnit(datatype='Spectra',
                                   path='/path/to/pdata/',
                                   startDate='2014/01/31',
                                   endDate='2014/03/31',
                                   startTime='00:00:00',
                                   endTime='23:59:59',
                                   online=0,
                                   walk=0)

proc_unit = controller.addProcUnit(datatype='Spectra',
                                   inputId=read_unit.getId())

op = proc_unit.addOperation(name='selectChannels')
op.addParameter(name='channelList', value='0,1', format='intlist')

op = proc_unit.addOperation(name='selectHeights')
op.addParameter(name='minHei', value='80', format='float')
op.addParameter(name='maxHei', value='200', format='float')

op = proc_unit.addOperation(name='removeDC')

op = proc_unit.addOperation(name='SpectraPlot', optype='other')
op.addParameter(name='id', value='6', format='int')
op.addParameter(name='wintitle', value='Spectra', format='str')

op = procUnitConfObj1.addOperation(name='RTIPlot', optype='other')
op.addParameter(name='id', value='2', format='int')
op.addParameter(name='wintitle', value='RTI', format='str')

controller.start()

```
