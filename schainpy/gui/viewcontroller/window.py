# -*- coding: utf-8 -*-

"""
Module implementing Window.
"""
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QMainWindow
from PyQt4.QtCore import pyqtSignature
from GUI.ui_window import Ui_window

#closed=pyqtSignal()

class Window(QMainWindow, Ui_window):
    """
    Class documentation goes here.
    """
    closed=pyqtSignal()
    def __init__(self, parent = None):
        """
        Constructor
        """
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.name=0

    
    @pyqtSignature("")
    def on_cancelButton_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        #raise NotImplementedError
        self.close()
        
    @pyqtSignature("")
    def on_okButton_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        #raise NotImplementedError
        # self.almacena()
        self.close()
        
    
    def almacena(self):
        #print str(self.proyectNameLine.text())
        return str(self.proyectNameLine.text())
     
    def closeEvent(self, event):
        self.closed.emit()
        event.accept()
    