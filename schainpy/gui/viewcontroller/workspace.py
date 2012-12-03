# -*- coding: utf-8 -*-

from PyQt4.QtGui import QMainWindow
from PyQt4.QtCore import pyqtSignature
from PyQt4.QtCore import pyqtSignal
from PyQt4 import QtGui
from mainwindow import MainWindow
from GUI.ui_workspace import Ui_Workspace

class Workspace(QMainWindow, Ui_Workspace):
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
        #*#######   DIRECTORIO DE TRABAJO  #########*#
        self.dirCmbBox.setItemText(0, QtGui.QApplication.translate("MainWindow", "C:\WorkSpaceGui", None, QtGui.QApplication.UnicodeUTF8))
        self.dir=str("C:\WorkSpaceGui")
        self.dirCmbBox.addItem(self.dir)
                  
    @pyqtSignature("")
    def on_dirBrowsebtn_clicked(self):
        """
        Slot documentation goes here.
        """
        self.dirBrowse = str(QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', './',  QtGui.QFileDialog.ShowDirsOnly))
        self.dirCmbBox.addItem(self.dirBrowse)
        
    @pyqtSignature("")
    def on_dirButton_clicked(self):
        """
        Slot documentation goes here.
        """

    @pyqtSignature("")
    def on_dirOkbtn_clicked(self):
        """
        VISTA DE INTERFAZ GRÃFICA
        """
        self.showmemainwindow()
    
               
    @pyqtSignature("")
    def on_dirCancelbtn_clicked(self):
        """
        Cerrar
        """
        self.close()
        
    def showmemainwindow(self):
        self.Dialog= MainWindow(self)
        self.Dialog.show()
        self.hide()

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()
    

    
    