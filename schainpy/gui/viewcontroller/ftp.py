# -*- coding: utf-8 -*-

"""
Module implementing Ftp.
"""

from PyQt4.QtGui import QMainWindow
from PyQt4.QtCore import pyqtSignature

from schainpy.gui.viewer.ftp import Ui_Ftp

class Ftp(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
