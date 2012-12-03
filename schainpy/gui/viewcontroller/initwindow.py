# -*- coding: utf-8 -*-

"""
Module implementing Pantalla.
"""
from PyQt4.QtGui import QMainWindow
from PyQt4.QtCore import pyqtSignature
from workspace import Workspace
#from mainwindow import Workspace
from GUI.ui_initwindow import Ui_InitWindow

class InitWindow(QMainWindow, Ui_InitWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        QMainWindow.__init__(self, parent)
      
    
    @pyqtSignature("")
    def on_pushButton_2_clicked(self):
        """
        Close First Window 
        """
        self.close()  

    @pyqtSignature("")
    def on_pushButton_clicked(self):
        """
        Show Workspace Window
        """
        self.showmeconfig()
    
    def showmeconfig(self):
        '''
        Method to call Workspace
        '''
        self.config=Workspace()
        self.config.closed.connect(self.show)
        self.config.show()
        self.hide()
        
        

