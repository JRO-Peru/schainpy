# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\alex\ericworkspace\GUIV1\workspacev2.ui'
#
# Created: Thu Dec 13 09:23:36 2012
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
        MainWindow.resize(728, 344)
        self.centralWidget = QtGui.QWidget(MainWindow)
        self.centralWidget.setObjectName(_fromUtf8("centralWidget"))
        self.line = QtGui.QFrame(self.centralWidget)
        self.line.setGeometry(QtCore.QRect(0, 60, 731, 20))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.dirLabel = QtGui.QTextEdit(self.centralWidget)
        self.dirLabel.setGeometry(QtCore.QRect(0, 0, 731, 91))
        self.dirLabel.setReadOnly(True)
        self.dirLabel.setObjectName(_fromUtf8("dirLabel"))
        self.dirWork = QtGui.QLabel(self.centralWidget)
        self.dirWork.setGeometry(QtCore.QRect(10, 110, 87, 22))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.dirWork.setFont(font)
        self.dirWork.setObjectName(_fromUtf8("dirWork"))
        self.dirButton = QtGui.QRadioButton(self.centralWidget)
        self.dirButton.setGeometry(QtCore.QRect(10, 250, 401, 26))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.dirButton.setFont(font)
        self.dirButton.setObjectName(_fromUtf8("dirButton"))
        self.dirCmbBox = QtGui.QComboBox(self.centralWidget)
        self.dirCmbBox.setGeometry(QtCore.QRect(100, 110, 481, 31))
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
        self.dirCmbBox.setPalette(palette)
        self.dirCmbBox.setObjectName(_fromUtf8("dirCmbBox"))
        self.dirBrowsebtn = QtGui.QToolButton(self.centralWidget)
        self.dirBrowsebtn.setGeometry(QtCore.QRect(600, 110, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.dirBrowsebtn.setFont(font)
        self.dirBrowsebtn.setObjectName(_fromUtf8("dirBrowsebtn"))
        self.dirOkbtn = QtGui.QPushButton(self.centralWidget)
        self.dirOkbtn.setGeometry(QtCore.QRect(590, 300, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.dirOkbtn.setFont(font)
        self.dirOkbtn.setObjectName(_fromUtf8("dirOkbtn"))
        self.dirCancelbtn = QtGui.QPushButton(self.centralWidget)
        self.dirCancelbtn.setGeometry(QtCore.QRect(470, 300, 111, 31))
        self.dirCancelbtn.setObjectName(_fromUtf8("dirCancelbtn"))
        MainWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.dirLabel.setHtml(QtGui.QApplication.translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Cantarell\'; font-size:11pt; font-weight:600;\"> Select a workspace</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Cantarell\'; font-size:11pt; font-weight:600;\"><br /></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Cantarell\'; font-size:11pt;\">  Signal Chain stores your projects in a folder called a workspace.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Cantarell\'; font-size:11pt;\">  Choose a workspace folder to use for this session.</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.dirWork.setText(QtGui.QApplication.translate("MainWindow", "Workspace :", None, QtGui.QApplication.UnicodeUTF8))
        self.dirButton.setText(QtGui.QApplication.translate("MainWindow", "Use this as the default and do not ask again", None, QtGui.QApplication.UnicodeUTF8))
        self.dirBrowsebtn.setText(QtGui.QApplication.translate("MainWindow", "Browse...", None, QtGui.QApplication.UnicodeUTF8))
        self.dirOkbtn.setText(QtGui.QApplication.translate("MainWindow", "OK", None, QtGui.QApplication.UnicodeUTF8))
        self.dirCancelbtn.setText(QtGui.QApplication.translate("MainWindow", "Cancel", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_Workspace()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

