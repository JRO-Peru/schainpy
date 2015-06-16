'''
Created on Jul 16, 2014

@author: roj-idl71
'''

from distutils.core import setup, Extension

setup(name="schainpy",
        version="2.0",
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
        package_data={'schainpy.gui.figures': ['*.jpg', '*.jpeg', '*.png', '*.gif']},
        include_package_data=True,
        scripts =['schainpy/gui/schainGUI'])