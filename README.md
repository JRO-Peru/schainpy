# Signal Chain

## Introduction

Signal Chain (SCh) is a radar data processing library developed using [Python](www.python.org) at JRO. SCh provides modules to read, write, process and plot data.

## Installation

Install system dependencies, clone the latest version from [here](http://jro-dev.igp.gob.pe/rhodecode/schain/) and install it as a normal python package, we strongly recommend to use Anaconda or a virtual environment for the installation.

### Dependencies
- GCC (gcc or gfortran)
- Python.h (python-dev or python-devel)
- Python-TK (python-tk)
- HDF5 libraries (libhdf5-dev)

### Linux based system (e.g. ubuntu)
```
$ git clone http://jro-dev.igp.gob.pe/rhodecode/schain/
$ cd schain
$ git checkout `schain-branch` (optional)
$ sudo pip install ./
```

### MAC Os 
```
$ brew install python
$ git clone http://jro-dev.igp.gob.pe/rhodecode/schain/
$ cd schain
$ git checkout `schain-branch` (optional)
$ sudo pip install ./
```

### Docker

Download Dockerfile from the repository, and create a docker image

```
$ docker build -t schain .
```

You can run a container using an xml file or a schain script also you need to mount a volume for the data input and for the output files/plots
```
$ docker run -it --rm --volume /path/to/host/data:/data schain xml /data/test.xml
$ docker run -it --rm --volume /path/to/host/data:/data --entrypoint /urs/local/bin/python schain /data/test.py
```

## CLI (command line interface)

Signal Chain provides the following commands:

- schainGUI: Open the GUI
- schain: Signal chain command line


## First Script

Here you can find an script to read Spectra data (.pdata), remove dc and plot spectra & RTI

First import SCh and creating a project

```python
#!/usr/bin/python

from schainpy.controller import Project

prj = Project()
prj.setup(
    id = '100',
    name='test',
    description='Basic experiment'
    )
```

Add read unit and operations

```python
read_unit = prj.addReadUnit(
    datatype='Spectra',
    path='/path/to/pdata/',
    startDate='2014/01/31',
    endDate='2014/03/31',
    startTime='00:00:00',
    endTime='23:59:59',
    online=0,
    walk=0
    )

proc_unit = prj.addProcUnit(datatype='Spectra', inputId=read_unit.getId())

op = proc_unit.addOperation(name='selectChannels')
op.addParameter(name='channelList', value='0,1')

op = proc_unit.addOperation(name='selectHeights')
op.addParameter(name='minHei', value='80')
op.addParameter(name='maxHei', value='200')

op = proc_unit.addOperation(name='removeDC')

```

Plot data & start project

```python
op = proc_unit.addOperation(name='SpectraPlot')
op.addParameter(name='id', value='1')
op.addParameter(name='wintitle', value='Spectra')

op = procUnitConfObj1.addOperation(name='RTIPlot')
op.addParameter(name='id', value='2')
op.addParameter(name='wintitle', value='RTI')

prj.start()

```

Full script


```python
#!/usr/bin/python

from schainpy.prj import Project

prj = Project()
prj.setup(id = '100',
                 name='test',
                 description='Basic experiment')
read_unit = prj.addReadUnit(datatype='Spectra',
                                   path='/path/to/pdata/',
                                   startDate='2014/01/31',
                                   endDate='2014/03/31',
                                   startTime='00:00:00',
                                   endTime='23:59:59',
                                   online=0,
                                   walk=0)

proc_unit = prj.addProcUnit(datatype='Spectra',
                                   inputId=read_unit.getId())

op = proc_unit.addOperation(name='selectChannels')
op.addParameter(name='channelList', value='0,1')

op = proc_unit.addOperation(name='selectHeights')
op.addParameter(name='minHei', value='80')
op.addParameter(name='maxHei', value='200')

op = proc_unit.addOperation(name='removeDC')

op = proc_unit.addOperation(name='SpectraPlot')
op.addParameter(name='wintitle', value='Spectra', format='str')

op = procUnitConfObj1.addOperation(name='RTIPlot')
op.addParameter(name='wintitle', value='RTI', format='str')

prj.start()

```