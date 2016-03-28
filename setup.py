'''
Created on Jul 16, 2014

@author: @author: Miguel Urco
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
        py_modules=[''],
        package_data={'': ['schain.conf.template'],
                      'schainpy.gui.figures': ['*.png','*.jpg'],
                      },
        include_package_data=False,
        scripts =['schainpy/gui/schainGUI'],
        install_requires=["numpy >= 1.6.0",
                          "scipy >= 0.9.0",
                          "h5py >= 2.0.1",
                          "matplotlib >= 1.0.0",
                          "pyfits >= 2.0.0",
                          ],
      )