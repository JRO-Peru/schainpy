#!/usr/bin/python
# -*- coding: utf-8 -*-

#from PyQt4 import QtCore, QtGuis
from PyQt4.QtGui import QApplication
#from PyQt4.QtCore import pyqtSignature

from viewcontroller.initwindow import InitWindow
from viewcontroller.mainwindow import MainWindow
from viewcontroller.workspace import Workspace

def main():
    import sys
    app = QApplication(sys.argv)
    
#    Welcome=InitWindow()
#    Welcome.show() 
    
#    WorkPathspace=Workspace()
#    WorkPathspace.show()
    #Welcome.ContinueBtn.clicked.connect(WorkPathspace.show)    
    
    MainGUI=MainWindow()
#    WorkPathspace.dirOkbtn.clicked.connect(MainGUI.show)
    MainGUI.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()
