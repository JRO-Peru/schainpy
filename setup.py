'''
Created on Jul 16, 2014

@author: roj-idl71
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
                    'schainpy.model.utils',
                    'schainpy.gui',
                    'schainpy.gui.figures',
                    'schainpy.gui.viewcontroller',
                    'schainpy.gui.viewer',
                    'schainpy.gui.viewer.windows'},
        py_modules=['schainpy.serializer.DataTranslate',
                    'schainpy.serializer.JROSerializer'],
        package_data={'schainpy': ['*.cfg'],
                      'schainpy.gui.figures': ['*.png','*.jpg']
                      },
        include_package_data=True,
        scripts =['schainpy/gui/schainGUI'],
        install_requires=["numpy >= 1.6.0",
                          "scipy >= 0.9.0",
                          "h5py >= 2.0.1",
                          "wxpython >= 2.8",
                          "matplotlib >= 1.0.0"
                          ],
      )