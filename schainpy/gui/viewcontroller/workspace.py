# -*- coding: utf-8 -*-

from PyQt4.QtGui import QMainWindow
from PyQt4.QtCore import pyqtSignature
from PyQt4.QtCore import pyqtSignal
from PyQt4 import QtGui
from viewcontroller.mainwindow import MainWindow
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
        #*#######   DIRECTORIO DE TRABAJO  #########*#
        self.dirCmbBox.setItemText(0, QtGui.QApplication.translate("MainWindow", "C:\WorkSpaceGui", None, QtGui.QApplication.UnicodeUTF8))
        self.dir=str("C:\WorkSpaceGui")
        self.dirCmbBox.addItem(self.dir)
        self.dirList.append(self.dir)
                  
    @pyqtSignature("")
    def on_dirBrowsebtn_clicked(self):
        """
        Slot documentation goes here.
        """
        
        self.dirBrowse = str(QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', './',  QtGui.QFileDialog.ShowDirsOnly))
        self.dirCmbBox.setItemText(0, QtGui.QApplication.translate("MainWindow", self.dirBrowse, None, QtGui.QApplication.UnicodeUTF8))
        self.dirList.append(self.dirBrowse)
        self.dirCmbBox.clear()
        for i in self.dirList:
            self.dirCmbBox.addItem(i)
        

        
    @pyqtSignature("")
    def on_dirButton_clicked(self):
        """
        Slot documentation goes here.
        """
        pass

    @pyqtSignature("")
    def on_dirOkbtn_clicked(self):
        """
        VISTA DE INTERFAZ GRÃFICA
        """
        self.close()
               
    @pyqtSignature("")
    def on_dirCancelbtn_clicked(self):
        """
        Cerrar
        """
        self.close()

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()
    

    
    