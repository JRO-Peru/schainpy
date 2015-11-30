# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/alex/ui/MainWindow_21_02_13_v49.ui'
#
# Created: Mon Mar 24 13:28:36 2014
#      by: PyQt4 UI code generator 4.10
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from windows import *

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

import os
from schainpy.gui.figures import tools
from schainpy import __version__

FIGURES_PATH = tools.get_path()

class Ui_EnvWindow(object):
    paused = False
    
    def restorePauseIcon(self):
        
        icon_name = "pause.png"
        iconPause = QtGui.QIcon()
        iconPause.addPixmap(QtGui.QPixmap(_fromUtf8( os.path.join(FIGURES_PATH, icon_name) )), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPauseToolbar.setIcon(iconPause)
    
    def restoreStartIcon(self):
        
        icon_name = "start.png"
        iconStart = QtGui.QIcon()
        iconStart.addPixmap(QtGui.QPixmap(_fromUtf8( os.path.join(FIGURES_PATH, icon_name) )), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionStarToolbar.setIcon(iconStart)
              
    def changePauseIcon(self, paused=False):
        
        if paused == True:
            icon_name = "pausered.png"
        else:
            icon_name = "pause.png"
            
        iconPause = QtGui.QIcon()
        iconPause.addPixmap(QtGui.QPixmap(_fromUtf8( os.path.join(FIGURES_PATH, icon_name) )), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPauseToolbar.setIcon(iconPause)
    
        return
    
    def changeStartIcon(self, started=False):
        
        if started == True:
            icon_name = "startred.png"
        else:
            icon_name = "start.png"
            
        iconStart = QtGui.QIcon()
        iconStart.addPixmap(QtGui.QPixmap(_fromUtf8( os.path.join(FIGURES_PATH, icon_name) )), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionStarToolbar.setIcon(iconStart)
    
        return
    
    def setupUi(self, MainWindow):
        
        self.paused=False
        
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1200, 800)
        
        self.centralWidget = QtGui.QWidget(MainWindow)
        self.centralWidget.setObjectName(_fromUtf8("centralWidget"))
        self.gridLayout_16 = QtGui.QGridLayout(self.centralWidget)
        self.gridLayout_16.setObjectName(_fromUtf8("gridLayout_16"))
        self.splitter_2 = QtGui.QSplitter(self.centralWidget)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName(_fromUtf8("splitter_2"))
        self.projectExplorerTree = QtGui.QTreeView(self.splitter_2)
        self.projectExplorerTree.setObjectName(_fromUtf8("projectExplorerTree"))
        self.splitter = QtGui.QSplitter(self.splitter_2)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.tabWidgetProject = QtGui.QTabWidget(self.splitter)
        self.tabWidgetProject.setMinimumSize(QtCore.QSize(0, 278))
        self.tabWidgetProject.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.tabWidgetProject.setObjectName(_fromUtf8("tabWidgetProject"))
        
        self.tabConsole = QtGui.QTabWidget(self.splitter)
        self.tabConsole.setMinimumSize(QtCore.QSize(0, 0))
        self.tabConsole.setObjectName(_fromUtf8("tabConsole"))
        self.tab_5 = QtGui.QWidget()
        self.tab_5.setObjectName(_fromUtf8("tab_5"))
        self.gridLayout_4 = QtGui.QGridLayout(self.tab_5)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.console = QtGui.QTextEdit(self.tab_5)
        self.console.setObjectName(_fromUtf8("console"))
        self.gridLayout_4.addWidget(self.console, 0, 0, 1, 1)
        self.tabConsole.addTab(self.tab_5, _fromUtf8(""))
        self.tabWidget = QtGui.QTabWidget(self.splitter_2)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tabProjectProperty = QtGui.QWidget()
        self.tabProjectProperty.setObjectName(_fromUtf8("tabProjectProperty"))
        self.gridLayout_8 = QtGui.QGridLayout(self.tabProjectProperty)
        self.gridLayout_8.setObjectName(_fromUtf8("gridLayout_8"))
        self.treeProjectProperties = QtGui.QTreeView(self.tabProjectProperty)
        self.treeProjectProperties.setObjectName(_fromUtf8("treeProjectProperties"))
        self.gridLayout_8.addWidget(self.treeProjectProperties, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tabProjectProperty, _fromUtf8(""))
        self.gridLayout_16.addWidget(self.splitter_2, 1, 0, 1, 1)
        
        MainWindow.setCentralWidget(self.centralWidget)
        self.toolBar = QtGui.QToolBar(MainWindow)
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        
        self.menuBar = QtGui.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1065, 25))
        self.menuBar.setObjectName(_fromUtf8("menuBar"))
        self.menuProject = QtGui.QMenu(self.menuBar)
        self.menuProject.setObjectName(_fromUtf8("menuProject"))
        self.menuRun = QtGui.QMenu(self.menuBar)
        self.menuRun.setObjectName(_fromUtf8("menuRun"))
        self.menuOptions = QtGui.QMenu(self.menuBar)
        self.menuOptions.setObjectName(_fromUtf8("menuOptions"))
        self.menuHelp = QtGui.QMenu(self.menuBar)
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))
        MainWindow.setMenuBar(self.menuBar)

        iconOpen = QtGui.QIcon()
        iconOpen.addPixmap(QtGui.QPixmap(_fromUtf8( os.path.join(FIGURES_PATH,"open.png") )), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        iconCreate = QtGui.QIcon()
        iconCreate.addPixmap(QtGui.QPixmap(_fromUtf8( os.path.join(FIGURES_PATH,"new.png") )), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        iconSave = QtGui.QIcon()
        iconSave.addPixmap(QtGui.QPixmap(_fromUtf8( os.path.join(FIGURES_PATH,"save.png") )), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        iconStart = QtGui.QIcon()
        iconStart.addPixmap(QtGui.QPixmap(_fromUtf8( os.path.join(FIGURES_PATH,"start.png") )), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        iconStop = QtGui.QIcon()
        iconStop.addPixmap(QtGui.QPixmap(_fromUtf8( os.path.join(FIGURES_PATH,"stop.png") )), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        iconPause = QtGui.QIcon()
        iconPause.addPixmap(QtGui.QPixmap(_fromUtf8( os.path.join(FIGURES_PATH,"pause.png") )), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        iconAddPU = QtGui.QIcon()
        iconAddPU.addPixmap(QtGui.QPixmap(_fromUtf8( os.path.join(FIGURES_PATH,"branch.png") )), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        iconClose = QtGui.QIcon()
        iconClose.addPixmap(QtGui.QPixmap(_fromUtf8( os.path.join(FIGURES_PATH,"close.png") )), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        
        self.actionOpen = QtGui.QAction(MainWindow)
        self.actionOpen.setIcon(iconOpen)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        self.actionCreate = QtGui.QAction(MainWindow)
        self.actionCreate.setIcon(iconCreate)
        self.actionCreate.setObjectName(_fromUtf8("actionCreate"))
        self.actionSave = QtGui.QAction(MainWindow)
        self.actionSave.setIcon(iconSave)
        self.actionSave.setObjectName(_fromUtf8("actionSave"))
        self.actionClose = QtGui.QAction(MainWindow)
        self.actionClose.setIcon(iconClose)
        self.actionClose.setObjectName(_fromUtf8("actionClose"))
        self.actionStart = QtGui.QAction(MainWindow)
        self.actionStart.setIcon(iconStart)
        self.actionStart.setObjectName(_fromUtf8("actionStart"))
        self.actionPause = QtGui.QAction(MainWindow)
        self.actionPause.setIcon(iconPause)
        self.actionPause.setObjectName(_fromUtf8("actionPause"))
        self.actionStop = QtGui.QAction(MainWindow)
        self.actionStop.setIcon(iconStop)
        self.actionStop.setObjectName(_fromUtf8("actionStop"))
        self.actionAbout = QtGui.QAction(MainWindow)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        
        self.actionOpenToolbar = QtGui.QAction(MainWindow)
        self.actionOpenToolbar.setIcon(iconOpen)
        self.actionOpenToolbar.setObjectName(_fromUtf8("actionOpenToolbar"))
        self.actionCreateToolbar = QtGui.QAction(MainWindow)
        self.actionCreateToolbar.setIcon(iconCreate)
        self.actionCreateToolbar.setObjectName(_fromUtf8("actionCreateToolbar"))
        self.actionSaveToolbar = QtGui.QAction(MainWindow)
        self.actionSaveToolbar.setIcon(iconSave)
        self.actionSaveToolbar.setObjectName(_fromUtf8("actionSaveToolbar"))
        self.actionStarToolbar = QtGui.QAction(MainWindow)
        self.actionStarToolbar.setIcon(iconStart)
        self.actionStarToolbar.setObjectName(_fromUtf8("actionStarToolbar"))
        self.actionStopToolbar = QtGui.QAction(MainWindow)
        self.actionStopToolbar.setIcon(iconStop)
        self.actionStopToolbar.setObjectName(_fromUtf8("actionStopToolbar"))
        self.actionPauseToolbar = QtGui.QAction(MainWindow)
        self.actionPauseToolbar.setIcon(iconPause)
        self.actionPauseToolbar.setObjectName(_fromUtf8("actionPauseToolbar"))
        self.actionAddPU = QtGui.QAction(MainWindow)
        self.actionAddPU.setIcon(iconAddPU)  
        self.actionAddPU.setObjectName(_fromUtf8("actionAddPU"))
        self.actionFTP = QtGui.QAction(MainWindow)
        self.actionFTP.setObjectName(_fromUtf8("actionFTP"))
        self.toolBar.addAction(self.actionOpenToolbar)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionCreateToolbar)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionAddPU)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionSaveToolbar)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionStarToolbar)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionPauseToolbar)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionStopToolbar)
        self.toolBar.addSeparator()
        
#         self.actionPause.triggered.connect(self.changePauseIcon)
#         self.actionPauseToolbar.triggered.connect(self.changePauseIcon)
        
        self.menuProject.addAction(self.actionOpen)
        self.menuProject.addAction(self.actionCreate)
        self.menuProject.addAction(self.actionSave)
        self.menuProject.addAction(self.actionClose)
        self.menuRun.addAction(self.actionStart)
        self.menuRun.addAction(self.actionPause)
        self.menuRun.addAction(self.actionStop)
        self.menuOptions.addAction(self.actionFTP)
        self.menuHelp.addAction(self.actionAbout)
        self.menuBar.addAction(self.menuProject.menuAction())
        self.menuBar.addAction(self.menuRun.menuAction())
        self.menuBar.addAction(self.menuOptions.menuAction())
        self.menuBar.addAction(self.menuHelp.menuAction())
        
        self.tabConsole.setCurrentIndex(0)
        self.tabWidget.setCurrentIndex(0)
        
    def retranslateUi(self, MainWindow):
        
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        
        self.tabConsole.setTabText(self.tabConsole.indexOf(self.tab_5), _translate("MainWindow", "Console", None))
        
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabProjectProperty), _translate("MainWindow", "Project Property", None))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar", None))
        self.menuProject.setTitle(_translate("MainWindow", "Project", None))
        self.menuRun.setTitle(_translate("MainWindow", "Run", None))
        self.menuOptions.setTitle(_translate("MainWindow", "Options", None))
        self.menuHelp.setTitle(_translate("MainWindow", "Help", None))
        self.actionOpen.setText(_translate("MainWindow", "Open", None))
        self.actionCreate.setText(_translate("MainWindow", "Create", None))
        self.actionSave.setText(_translate("MainWindow", "Save", None))
        self.actionClose.setText(_translate("MainWindow", "Close", None))
        self.actionStart.setText(_translate("MainWindow", "Start", None))
        self.actionPause.setText(_translate("MainWindow", "Pause", None))
        self.actionStop.setText(_translate("MainWindow", "Stop", None))
        self.actionAbout.setText(_translate("MainWindow", "About SChain", None))
        self.actionOpenToolbar.setText(_translate("MainWindow", "openToolbar", None))
        self.actionOpenToolbar.setToolTip(_translate("MainWindow", "Open a project", None))
        self.actionCreateToolbar.setText(_translate("MainWindow", "createToolbar", None))
        self.actionCreateToolbar.setToolTip(_translate("MainWindow", "Create a new project", None))
        self.actionSaveToolbar.setText(_translate("MainWindow", "saveToolbar", None))
        self.actionSaveToolbar.setToolTip(_translate("MainWindow", "Save a project", None))
        self.actionStarToolbar.setText(_translate("MainWindow", "starToolbar", None))
        self.actionStarToolbar.setToolTip(_translate("MainWindow", "Start process", None))
        self.actionStopToolbar.setText(_translate("MainWindow", "stopToolbar", None))
        self.actionStopToolbar.setToolTip(_translate("MainWindow", "Stop process", None))
        self.actionPauseToolbar.setText(_translate("MainWindow", "pauseToolbar", None))
        self.actionPauseToolbar.setToolTip(_translate("MainWindow", "Pause process", None))
        self.actionAddPU.setText(_translate("MainWindow", "Add Processing Unit", None))
        self.actionFTP.setText(_translate("MainWindow", "FTP", None))
        
    def closeEvent(self, event):
        
        reply = QtGui.QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QtGui.QMessageBox.Yes | 
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
    
    def aboutEvent(self):
        title = "Signal Chain Processing Software v%s" %__version__
        message = """
Developed by Jicamarca Radio Observatory
Any comment to miguel.urco@jro.igp.gob.pe
"""
        QtGui.QMessageBox.about(self, title, message)
            
            
class Ui_BasicWindow(Ui_EnvWindow, Ui_ProjectTab, Ui_VoltageTab, Ui_SpectraTab, Ui_SpectraHeisTab, Ui_CorrelationTab):
    
    def setupUi(self, MainWindow):
        
        Ui_EnvWindow.setupUi(self, MainWindow)
        
        Ui_ProjectTab.setupUi(self)
        Ui_VoltageTab.setupUi(self)
        Ui_SpectraTab.setupUi(self)
        Ui_SpectraHeisTab.setupUi(self)
        Ui_CorrelationTab.setupUi(self)
    
        self.retranslateUi(MainWindow)
        
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
    def retranslateUi(self, MainWindow):
        
        Ui_EnvWindow.retranslateUi(self, MainWindow)
        
        Ui_ProjectTab.retranslateUi(self)
        Ui_VoltageTab.retranslateUi(self)
        Ui_SpectraTab.retranslateUi(self)
        Ui_SpectraHeisTab.retranslateUi(self)
        Ui_CorrelationTab.retranslateUi(self)
        
        
class Ui_AdvancedWindow(Ui_EnvWindow):
    
    def setupUi(self, AdvancedWindow):
        
        Ui_MainWindow.setupUi(self, AdvancedWindow)
    
    def retranslateUi(self, AdvancedWindow):
        
        Ui_MainWindow.retranslateUi(self, AdvancedWindow)
        


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_BasicWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

