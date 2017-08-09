""".

Created on Jul 16, 2014

@author: Miguel Urco
"""

import numpy
from setuptools import setup, Extension
from schainpy import __version__

setup(name="schainpy",
      version=__version__,
      description="Python tools to read, write and process Jicamarca data",
      author="Miguel Urco",
      author_email="miguel.urco@jro.igp.gob.pe",
      url="http://jro.igp.gob.pe",
      packages={'schainpy',
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
                    'schainpy.gui.figures': ['*.png', '*.jpg'],
                    },
      include_package_data=False,
      entry_points={
        'console_scripts': [
            'schain = schaincli.cli:main',
        ],
      },
      scripts=['schainpy/gui/schainGUI'],
      ext_modules=[Extension("cSchain", ["schainpy/model/proc/extensions.c"], include_dirs=[numpy.get_include()])],
      install_requires=[
                      "scipy >= 0.14.0",
                      "h5py >= 2.2.1",
                      "matplotlib >= 1.4.2",
                      "pyfits >= 3.4",                      
                      "paramiko >= 2.1.2",
                      "paho-mqtt >= 1.2",
                      "zmq",
                      "fuzzywuzzy",
                      "click",
                      "colorama",
                      "python-Levenshtein"
                      ],
      )

