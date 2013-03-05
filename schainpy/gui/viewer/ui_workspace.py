# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\alex\ericworkspace\GUIV1\workspacev3.ui'
#
# Created: Tue Mar 05 16:29:15 2013
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Workspace(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(678, 304)
        self.centralWidget = QtGui.QWidget(MainWindow)
        self.centralWidget.setObjectName(_fromUtf8("centralWidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.dirWork = QtGui.QLabel(self.centralWidget)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.dirWork.setFont(font)
        self.dirWork.setObjectName(_fromUtf8("dirWork"))
        self.gridLayout.addWidget(self.dirWork, 3, 0, 1, 1)
        self.dirLabel = QtGui.QTextEdit(self.centralWidget)
        self.dirLabel.setMaximumSize(QtCore.QSize(16777215, 75))
        self.dirLabel.setReadOnly(True)
        self.dirLabel.setObjectName(_fromUtf8("dirLabel"))
        self.gridLayout.addWidget(self.dirLabel, 0, 0, 1, 2)
        self.line = QtGui.QFrame(self.centralWidget)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.gridLayout.addWidget(self.line, 1, 0, 1, 2)
        self.dirComBox = QtGui.QComboBox(self.centralWidget)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        self.dirComBox.setPalette(palette)
        self.dirComBox.setObjectName(_fromUtf8("dirComBox"))
        self.gridLayout.addWidget(self.dirComBox, 5, 0, 1, 1)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.horizontalLayout_3.addItem(spacerItem)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.horizontalLayout_3.addItem(spacerItem1)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.horizontalLayout_3.addItem(spacerItem2)
        spacerItem3 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.horizontalLayout_3.addItem(spacerItem3)
        spacerItem4 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.horizontalLayout_3.addItem(spacerItem4)
        self.gridLayout.addLayout(self.horizontalLayout_3, 8, 0, 1, 1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.dirButton = QtGui.QRadioButton(self.centralWidget)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.dirButton.setFont(font)
        self.dirButton.setObjectName(_fromUtf8("dirButton"))
        self.horizontalLayout_2.addWidget(self.dirButton)
        spacerItem5 = QtGui.QSpacerItem(428, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem5)
        self.gridLayout.addLayout(self.horizontalLayout_2, 9, 0, 1, 2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem6 = QtGui.QSpacerItem(438, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem6)
        self.dirOkBtn = QtGui.QPushButton(self.centralWidget)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.dirOkBtn.setFont(font)
        self.dirOkBtn.setObjectName(_fromUtf8("dirOkBtn"))
        self.horizontalLayout.addWidget(self.dirOkBtn)
        self.dirCancelBtn = QtGui.QPushButton(self.centralWidget)
        self.dirCancelBtn.setObjectName(_fromUtf8("dirCancelBtn"))
        self.horizontalLayout.addWidget(self.dirCancelBtn)
        self.gridLayout.addLayout(self.horizontalLayout, 10, 0, 1, 2)
        self.dirToolPath = QtGui.QToolButton(self.centralWidget)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.dirToolPath.setFont(font)
        self.dirToolPath.setObjectName(_fromUtf8("dirToolPath"))
        self.gridLayout.addWidget(self.dirToolPath, 5, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.dirWork.setText(QtGui.QApplication.translate("MainWindow", "Workspace :", None, QtGui.QApplication.UnicodeUTF8))
        self.dirLabel.setHtml(QtGui.QApplication.translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Cantarell\'; font-size:8pt; font-weight:600;\"> Select a workspace</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Cantarell\'; font-size:8pt; font-weight:600;\"><br /></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Cantarell\'; font-size:8pt;\">  Signal Chain stores your projects in a folder called a workspace.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Cantarell\'; font-size:8pt;\">  Choose a workspace folder to use for this session.</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.dirButton.setText(QtGui.QApplication.translate("MainWindow", "Use this as the default and do not ask again", None, QtGui.QApplication.UnicodeUTF8))
        self.dirOkBtn.setText(QtGui.QApplication.translate("MainWindow", "OK", None, QtGui.QApplication.UnicodeUTF8))
        self.dirCancelBtn.setText(QtGui.QApplication.translate("MainWindow", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.dirToolPath.setText(QtGui.QApplication.translate("MainWindow", "...", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_Workspace()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())



