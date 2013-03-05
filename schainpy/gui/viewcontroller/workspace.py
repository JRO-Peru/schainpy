# -*- coding: utf-8 -*-

from PyQt4.QtGui import QMainWindow
from PyQt4.QtCore import pyqtSignature
from PyQt4.QtCore import pyqtSignal
from PyQt4 import QtGui
from viewer.ui_workspace import Ui_Workspace

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
        self.dirList=[]
        self.setupUi(self)
        self.setWindowTitle("ROJ-Signal Chain")
        self.setWindowIcon(QtGui.QIcon("figure/adn.jpg"))
        #*#######   DIRECTORIO DE TRABAJO  #########*#
        #self.dirCmbBox.setItemText(0, QtGui.QApplication.translate("MainWindow", "C:\WorkSpaceGui", None, QtGui.QApplication.UnicodeUTF8))
        
        self.dir=str("C:\WorkSpaceGui")
        self.dirComBox.addItem(self.dir)
        self.i=0
        
                  
    @pyqtSignature("")
    def on_dirToolPath_clicked(self):
        """
        Slot documentation goes here.
        """
        self.i +=1
        self.dirBrowse = str(QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', './',  QtGui.QFileDialog.ShowDirsOnly))
        self.dirComBox.addItem(self.dirBrowse)
        self.dirComBox.setCurrentIndex(self.i)



    @pyqtSignature("")
    def on_dirOkBtn_clicked(self):
        """
        VISTA DE INTERFAZ GRÃFICA
        """
        self.close()
               
    @pyqtSignature("")
    def on_dirCancelBtn_clicked(self):
        """
        Cerrar
        """
        self.close()

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()
    

    
    