'''
Created on Jun 5, 2015

@author: Miguel Urco
'''

from distutils.core import setup, Extension

setup(name="schainpy",
        version="2.0",
        description="Signal Chain Graphical Interface",
        author="Miguel Urco",
        author_email="miguel.urco@jro.igp.gob.pe",
        url="http://jro.igp.gob.pe",
        packages = {'schainpy',
                    'schainpy.gui',
                    'schainpy.gui.figure',
                    'schainpy.gui.viewcontroller',
                    'schainpy.gui.viewer',},
        py_modules=['schainpy.controller'],
        package_data={'schainpy.gui.figure': ['*.jpg', '*.png', '*.gif']},
        include_package_data=True,
        scripts =['schainpy/gui/schaingui.py'])