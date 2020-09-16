# Signal Chain

Signal Chain is a radar data processing library wich includes modules to read,
and write different files formats, besides modules to process and visualize the
data.

## Dependencies

- GCC (gcc or gfortran)
- Python.h (python-dev or python-devel)
- Python-TK (python-tk)
- HDF5 libraries (libhdf5-dev)

## Installation

To get started the easiest way to install it is through
[PyPI](https://pypi.org/project/schainpy/) with pip. We strongly recommend to
use an virtual environment like virtualenv or anaconda.

```bash
pip install schainpy
```

### From source

First, ensure that you have the above-listed dependencies installed, then clone
the repository and install as normal python package:

```bash
git clone https://github.com/JRO-Peru/schainpy.git
cd schain
git checkout `branch-name` (optional)
sudo pip install ./
```

### Using Docker

Download Dockerfile from the repository, and create a docker image:

```bash
docker build -t schain .
```

You can run a container using an xml file or a schain script also you need to
mount a volume for the data input and for the output files/plots:

```bash
docker run -it --rm --volume /path/to/host/data:/data schain xml /data/test.xml
docker run -it --rm --volume /path/to/host/data:/data --entrypoint /urs/local/bin/python schain /data/test.py
```

## CLI (command line interface)

Signal Chain provides the following commands:

- schainGUI: Open the GUI
- schain: Signal chain command line

## Example

Here you can find an script to read Spectra data (.pdata), remove dc and plot
self-spectra & RTI:

```python
#!/usr/bin/python

from schainpy.controller import Project

prj = Project()

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

proc_unit = prj.addProcUnit(
    datatype='Spectra',
    inputId=read_unit.getId()
    )

op = proc_unit.addOperation(name='selectChannels')
op.addParameter(name='channelList', value='0,1')

op = proc_unit.addOperation(name='selectHeights')
op.addParameter(name='minHei', value='80')
op.addParameter(name='maxHei', value='200')

op = proc_unit.addOperation(name='removeDC')

op = proc_unit.addOperation(name='SpectraPlot')
op.addParameter(name='wintitle', value='Spectra', format='str')

op = proc_unit.addOperation(name='RTIPlot')
op.addParameter(name='wintitle', value='RTI', format='str')

prj.start()

```
