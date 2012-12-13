# -*- coding: utf-8 -*-

"""
Module implementing InitWindow.
"""

from PyQt4.QtGui import QMainWindow
from PyQt4.QtCore import pyqtSignature

from viewer.ui_initwindow import Ui_InitWindow

class InitWindow(QMainWindow, Ui_InitWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
    
    @pyqtSignature("")
    def on_ExitBtn_clicked(self):
        """
        Exit cierra la ventana de Bienvenida
        """
        # TODO: not implemented yet
        #raise NotImplementedError
        self.close()
        
    @pyqtSignature("")
    def on_ContinueBtn_clicked(self):
        """
       Continue cierra la ventana de Bienvenida, a este evento se le complementa con la accion
       conectar con la ventana de configuracion de Workspace
        """
        # TODO: not implemented yet
        #raise NotImplementedError
        self.close()
