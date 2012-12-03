# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/roj-idl71/SignalChain/signal/configuraproyect.ui'
#
# Created: Wed Sep  5 11:53:34 2012
#      by: PyQt4 UI code generator 4.8.6
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
        MainWindow.resize(728, 272)
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.centralWidget = QtGui.QWidget(MainWindow)
        self.centralWidget.setObjectName(_fromUtf8("centralWidget"))
        self.line = QtGui.QFrame(self.centralWidget)
        self.line.setGeometry(QtCore.QRect(0, 60, 731, 20))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.dirLabel = QtGui.QTextEdit(self.centralWidget)
        self.dirLabel.setGeometry(QtCore.QRect(0, 0, 731, 81))
        self.dirLabel.setReadOnly(True)
        self.dirLabel.setHtml(QtGui.QApplication.translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Cantarell\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; font-weight:600;\">Select a workspace</span></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">SignalChain stores your projects in a folder called a workspace.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Choose a workspace folder to use for this session.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.dirLabel.setObjectName(_fromUtf8("dirLabel"))
        self.dirWork = QtGui.QLabel(self.centralWidget)
        self.dirWork.setGeometry(QtCore.QRect(10, 90, 87, 22))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.dirWork.setFont(font)
        self.dirWork.setText(QtGui.QApplication.translate("MainWindow", "Workspace :", None, QtGui.QApplication.UnicodeUTF8))
        self.dirWork.setObjectName(_fromUtf8("dirWork"))
        self.dirButton = QtGui.QRadioButton(self.centralWidget)
        self.dirButton.setGeometry(QtCore.QRect(10, 200, 310, 26))
        self.dirButton.setText(QtGui.QApplication.translate("MainWindow", "Use this as the default and do not ask again", None, QtGui.QApplication.UnicodeUTF8))
        self.dirButton.setObjectName(_fromUtf8("dirButton"))
        self.layoutWidget = QtGui.QWidget(self.centralWidget)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 230, 701, 33))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.dirCancelbtn = QtGui.QPushButton(self.layoutWidget)
        self.dirCancelbtn.setText(QtGui.QApplication.translate("MainWindow", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.dirCancelbtn.setObjectName(_fromUtf8("dirCancelbtn"))
        self.horizontalLayout_2.addWidget(self.dirCancelbtn)
        self.dirOkbtn = QtGui.QPushButton(self.layoutWidget)
        self.dirOkbtn.setText(QtGui.QApplication.translate("MainWindow", "OK", None, QtGui.QApplication.UnicodeUTF8))
        self.dirOkbtn.setObjectName(_fromUtf8("dirOkbtn"))
        self.horizontalLayout_2.addWidget(self.dirOkbtn)
        self.dirCmbBox = QtGui.QComboBox(self.centralWidget)
        self.dirCmbBox.setGeometry(QtCore.QRect(10, 120, 621, 21))
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
        self.dirBrowsebtn.setGeometry(QtCore.QRect(640, 120, 76, 21))
        self.dirBrowsebtn.setText(QtGui.QApplication.translate("MainWindow", "Browse...", None, QtGui.QApplication.UnicodeUTF8))
        self.dirBrowsebtn.setObjectName(_fromUtf8("dirBrowsebtn"))
        MainWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        pass


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_Workspace()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())