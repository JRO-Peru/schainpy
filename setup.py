'''
Created on Jul 16, 2014

@author: Miguel Urco
@author: Juan C. Espinoza
'''

import os
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as _build_ext
from schainpy import __version__

class build_ext(_build_ext):
    def finalize_options(self):
        _build_ext.finalize_options(self)
        # Prevent numpy from thinking it is still in its setup process:
        __builtins__.__NUMPY_SETUP__ = False
        import numpy
        self.include_dirs.append(numpy.get_include())

setup(
    name = "schainpy",
    version = __version__,
    description = "Python tools to read, write and process Jicamarca data",
    author = "Miguel Urco, Juan C. Espinoza",
    author_email = "juan.espinoza@jro.igp.gob.pe",
    url = "http://jro-dev.igp.gob.pe/rhodecode/schain",
    packages = {
        'schainpy',
        'schainpy.model',
        'schainpy.model.data',
        'schainpy.model.graphics',
        'schainpy.model.io',
        'schainpy.model.proc',
        'schainpy.model.utils',
        'schainpy.utils',
        'schainpy.gui',
        'schainpy.cli',
        },
    package_data = {'': ['schain.conf.template'],
                    'schainpy.files': ['*.oga']
                    },
    include_package_data = False,
    scripts = ['schainpy/gui/schainGUI'],
    entry_points = {
        'console_scripts': [
            'schain = schainpy.cli.cli:main',
            ],
        },
    cmdclass = {'build_ext': build_ext},
    ext_modules=[
        Extension("schainpy.model.data._noise", ["schainc/_noise.c"]),
        ],
    setup_requires = ["numpy"],
    install_requires = [
        "scipy",
        "h5py",
        "matplotlib",
        "pyzmq",
        "fuzzywuzzy",
        "click",
        ],
)
