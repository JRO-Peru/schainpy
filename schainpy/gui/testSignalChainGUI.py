#!/usr/bin/python
# -*- coding: utf-8 -*-

#from PyQt4 import QtCore, QtGuis
from PyQt4.QtGui import QApplication
#from PyQt4.QtCore import pyqtSignature
#from Controller.workspace import Workspace
#from Controller.mainwindow import InitWindow
#from Controller.initwindow import InitWindow
#from Controller.window import window
from viewcontroller.mainwindow import MainWindow
#from viewcontroller.mainwindow2 import UnitProcess

def main():
    import sys
    app = QApplication(sys.argv)
    #wnd=InitWindow()
   # wnd=UnitProcess()
    wnd=MainWindow()
    #wnd=Workspace()
    wnd.show()
    sys.exit(app.exec_())
    

if __name__ == "__main__":
    main()