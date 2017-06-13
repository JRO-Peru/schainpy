# -*- coding: utf-8 -*-

"""
Module implementing InitWindow.
"""
import os

from PyQt4.QtGui import QDialog
from PyQt4.QtCore import pyqtSignature
from PyQt4                 import QtCore
from PyQt4                 import QtGui

from schainpy.gui.viewer.ui_initwindow import Ui_InitWindow
from schainpy.gui.figures import tools

FIGURES_PATH = tools.get_path()

class InitWindow(QDialog, Ui_InitWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle("ROJ-Signal Chain")
        self.setWindowIcon(QtGui.QIcon( os.path.join(FIGURES_PATH,"logo.png") ))
    
    @pyqtSignature("")
    def on_ExitBtn_clicked(self):
        """
        Exit cierra la ventana de Bienvenida
        """
        self.close()
        
    @pyqtSignature("")
    def on_ContinueBtn_clicked(self):
        """
       Continue cierra la ventana de Bienvenida, a este evento se le complementa con la accion
       conectar con la ventana de configuracion de Workspace
        """
        # TODO: not implemented yet
        #raise NotImplementedError
        self.accept()
