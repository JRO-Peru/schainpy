'''
Created on Jul 16, 2014

@author: Miguel Urco
'''

from schainpy import __version__
from setuptools import setup, Extension

setup(name="schainpy",
        version=__version__,
        description="Python tools to read, write and process Jicamarca data",
        author="Miguel Urco",
        author_email="miguel.urco@jro.igp.gob.pe",
        url="http://jro.igp.gob.pe",
        packages = {'schainpy',
                    'schainpy.model',
                    'schainpy.model.data',
                    'schainpy.model.graphics',
                    'schainpy.model.io',
                    'schainpy.model.proc',
                    'schainpy.model.serializer',
                    'schainpy.model.utils',
                    'schainpy.gui',
                    'schainpy.gui.figures',
                    'schainpy.gui.viewcontroller',
                    'schainpy.gui.viewer',
                    'schainpy.gui.viewer.windows'},
        ext_package='schainpy',
        py_modules=[''],
        package_data={'': ['schain.conf.template'],
                      'schainpy.gui.figures': ['*.png','*.jpg'],
                      },
        include_package_data=False,
        scripts =['schainpy/gui/schainGUI',
                  'schainpy/scripts/schain'],
        ext_modules=[Extension("cSchain", ["schainpy/model/proc/extensions.c"])],
        install_requires=[
                          "scipy >= 0.14.0",
                          "h5py >= 2.2.1",
                          "matplotlib >= 1.4.2",
                          "pyfits >= 3.4",
                          "numpy >= 1.11.2",
                          "paramiko >= 2.1.2",
                          "paho-mqtt >= 1.2",
                          "zmq",
                          "fuzzywuzzy"
                          ],
      )
