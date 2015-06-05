# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/alex/ui/ftpConfig4.ui'
#
# Created: Tue Aug 20 08:24:35 2013
#      by: PyQt4 UI code generator 4.10
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

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

class Ui_Ftp(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(374, 399)
        MainWindow.setMinimumSize(QtCore.QSize(374, 399))
        MainWindow.setMaximumSize(QtCore.QSize(374, 399))
        self.centralWidget = QtGui.QWidget(MainWindow)
        self.centralWidget.setObjectName(_fromUtf8("centralWidget"))
        self.label = QtGui.QLabel(self.centralWidget)
        self.label.setGeometry(QtCore.QRect(9, 38, 47, 17))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(self.centralWidget)
        self.label_2.setGeometry(QtCore.QRect(9, 133, 77, 17))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(self.centralWidget)
        self.label_3.setGeometry(QtCore.QRect(9, 166, 68, 17))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label_4 = QtGui.QLabel(self.centralWidget)
        self.label_4.setGeometry(QtCore.QRect(9, 9, 101, 17))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.label_5 = QtGui.QLabel(self.centralWidget)
        self.label_5.setGeometry(QtCore.QRect(9, 104, 87, 17))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.label_6 = QtGui.QLabel(self.centralWidget)
        self.label_6.setGeometry(QtCore.QRect(9, 71, 47, 17))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.serverFTP = QtGui.QLineEdit(self.centralWidget)
        self.serverFTP.setGeometry(QtCore.QRect(130, 40, 231, 27))
        self.serverFTP.setObjectName(_fromUtf8("serverFTP"))
        self.folderFTP = QtGui.QLineEdit(self.centralWidget)
        self.folderFTP.setGeometry(QtCore.QRect(130, 70, 231, 27))
        self.folderFTP.setObjectName(_fromUtf8("folderFTP"))
        self.usernameFTP = QtGui.QLineEdit(self.centralWidget)
        self.usernameFTP.setGeometry(QtCore.QRect(130, 130, 231, 27))
        self.usernameFTP.setObjectName(_fromUtf8("usernameFTP"))
        self.passwordFTP = QtGui.QLineEdit(self.centralWidget)
        self.passwordFTP.setGeometry(QtCore.QRect(130, 160, 231, 27))
        self.passwordFTP.setObjectName(_fromUtf8("passwordFTP"))
        self.ftpCancelButton = QtGui.QPushButton(self.centralWidget)
        self.ftpCancelButton.setGeometry(QtCore.QRect(130, 360, 111, 27))
        self.ftpCancelButton.setObjectName(_fromUtf8("ftpCancelButton"))
        self.ftpOkButton = QtGui.QPushButton(self.centralWidget)
        self.ftpOkButton.setGeometry(QtCore.QRect(250, 360, 111, 27))
        self.ftpOkButton.setObjectName(_fromUtf8("ftpOkButton"))
        self.label_7 = QtGui.QLabel(self.centralWidget)
        self.label_7.setGeometry(QtCore.QRect(10, 200, 66, 17))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.label_8 = QtGui.QLabel(self.centralWidget)
        self.label_8.setGeometry(QtCore.QRect(10, 230, 81, 17))
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.label_9 = QtGui.QLabel(self.centralWidget)
        self.label_9.setGeometry(QtCore.QRect(10, 260, 81, 17))
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.label_10 = QtGui.QLabel(self.centralWidget)
        self.label_10.setGeometry(QtCore.QRect(10, 290, 81, 17))
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.label_11 = QtGui.QLabel(self.centralWidget)
        self.label_11.setGeometry(QtCore.QRect(10, 320, 81, 17))
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.weightFTP = QtGui.QLineEdit(self.centralWidget)
        self.weightFTP.setGeometry(QtCore.QRect(130, 230, 231, 27))
        self.weightFTP.setObjectName(_fromUtf8("weightFTP"))
        self.expcodeFTP = QtGui.QLineEdit(self.centralWidget)
        self.expcodeFTP.setGeometry(QtCore.QRect(130, 260, 231, 27))
        self.expcodeFTP.setObjectName(_fromUtf8("expcodeFTP"))
        self.subexpFTP = QtGui.QLineEdit(self.centralWidget)
        self.subexpFTP.setGeometry(QtCore.QRect(130, 290, 231, 27))
        self.subexpFTP.setObjectName(_fromUtf8("subexpFTP"))
        self.plotposFTP = QtGui.QLineEdit(self.centralWidget)
        self.plotposFTP.setGeometry(QtCore.QRect(130, 320, 231, 27))
        self.plotposFTP.setObjectName(_fromUtf8("plotposFTP"))
        MainWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.label.setText(_translate("MainWindow", "Server:", None))
        self.label_2.setText(_translate("MainWindow", "User Name:", None))
        self.label_3.setText(_translate("MainWindow", "Password:", None))
        self.label_4.setText(_translate("MainWindow", "Server Details", None))
        self.label_5.setText(_translate("MainWindow", "User Details", None))
        self.label_6.setText(_translate("MainWindow", "Folder:", None))
        self.ftpCancelButton.setText(_translate("MainWindow", "Cancel", None))
        self.ftpOkButton.setText(_translate("MainWindow", "Ok", None))
        self.label_7.setText(_translate("MainWindow", "Others", None))
        self.label_8.setText(_translate("MainWindow", "Ftp_wei:", None))
        self.label_9.setText(_translate("MainWindow", "Exp_code:", None))
        self.label_10.setText(_translate("MainWindow", "Sub_exp:", None))
        self.label_11.setText(_translate("MainWindow", "Plot_pos:", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_Ftp()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

