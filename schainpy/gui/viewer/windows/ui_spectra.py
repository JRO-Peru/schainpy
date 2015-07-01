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
    
class Ui_SpectraTab(object):
    
    def setupUi(self):

        self.tabSpectra = QtGui.QWidget()
        self.tabSpectra.setObjectName(_fromUtf8("tabSpectra"))
        self.gridLayout_7 = QtGui.QGridLayout(self.tabSpectra)
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.frame_5 = QtGui.QFrame(self.tabSpectra)
        self.frame_5.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_5.setObjectName(_fromUtf8("frame_5"))
        self.gridLayout_18 = QtGui.QGridLayout(self.frame_5)
        self.gridLayout_18.setObjectName(_fromUtf8("gridLayout_18"))
        self.specOpOk = QtGui.QPushButton(self.frame_5)
        self.specOpOk.setObjectName(_fromUtf8("specOpOk"))
        self.gridLayout_18.addWidget(self.specOpOk, 0, 0, 1, 1)
        self.specGraphClear = QtGui.QPushButton(self.frame_5)
        self.specGraphClear.setObjectName(_fromUtf8("specGraphClear"))
        self.gridLayout_18.addWidget(self.specGraphClear, 0, 1, 1, 1)
        self.gridLayout_7.addWidget(self.frame_5, 1, 1, 1, 1)
        self.tabWidgetSpectra = QtGui.QTabWidget(self.tabSpectra)
        self.tabWidgetSpectra.setObjectName(_fromUtf8("tabWidgetSpectra"))
        self.tabopSpectra = QtGui.QWidget()
        self.tabopSpectra.setObjectName(_fromUtf8("tabopSpectra"))
        self.gridLayout_5 = QtGui.QGridLayout(self.tabopSpectra)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.specOpCebCrossSpectra = QtGui.QCheckBox(self.tabopSpectra)
        self.specOpCebCrossSpectra.setObjectName(_fromUtf8("specOpCebCrossSpectra"))
        self.gridLayout_5.addWidget(self.specOpCebCrossSpectra, 4, 0, 1, 2)
        self.specOpComChannel = QtGui.QComboBox(self.tabopSpectra)
        self.specOpComChannel.setObjectName(_fromUtf8("specOpComChannel"))
        self.specOpComChannel.addItem(_fromUtf8(""))
        self.specOpComChannel.addItem(_fromUtf8(""))
        self.gridLayout_5.addWidget(self.specOpComChannel, 8, 0, 1, 2)
        self.specOpChannel = QtGui.QLineEdit(self.tabopSpectra)
        self.specOpChannel.setObjectName(_fromUtf8("specOpChannel"))
        self.gridLayout_5.addWidget(self.specOpChannel, 8, 3, 1, 2)
        self.specOpComHeights = QtGui.QComboBox(self.tabopSpectra)
        self.specOpComHeights.setObjectName(_fromUtf8("specOpComHeights"))
        self.specOpComHeights.addItem(_fromUtf8(""))
        self.specOpComHeights.addItem(_fromUtf8(""))
        self.gridLayout_5.addWidget(self.specOpComHeights, 11, 0, 1, 2)
        self.specOpHeights = QtGui.QLineEdit(self.tabopSpectra)
        self.specOpHeights.setObjectName(_fromUtf8("specOpHeights"))
        self.gridLayout_5.addWidget(self.specOpHeights, 11, 3, 1, 2)
        self.specOpIncoherent = QtGui.QLineEdit(self.tabopSpectra)
        self.specOpIncoherent.setObjectName(_fromUtf8("specOpIncoherent"))
        self.gridLayout_5.addWidget(self.specOpIncoherent, 13, 3, 1, 2)
        self.specOpCebRemoveDC = QtGui.QCheckBox(self.tabopSpectra)
        self.specOpCebRemoveDC.setObjectName(_fromUtf8("specOpCebRemoveDC"))
        self.gridLayout_5.addWidget(self.specOpCebRemoveDC, 14, 0, 1, 2)
        self.specOpCebHeights = QtGui.QCheckBox(self.tabopSpectra)
        self.specOpCebHeights.setObjectName(_fromUtf8("specOpCebHeights"))
        self.gridLayout_5.addWidget(self.specOpCebHeights, 9, 0, 1, 1)
        self.specOpCebChannel = QtGui.QCheckBox(self.tabopSpectra)
        self.specOpCebChannel.setObjectName(_fromUtf8("specOpCebChannel"))
        self.gridLayout_5.addWidget(self.specOpCebChannel, 7, 0, 1, 1)
        self.specOppairsList = QtGui.QLineEdit(self.tabopSpectra)
        self.specOppairsList.setObjectName(_fromUtf8("specOppairsList"))
        self.gridLayout_5.addWidget(self.specOppairsList, 6, 3, 1, 2)
        self.specOpnFFTpoints = QtGui.QLineEdit(self.tabopSpectra)
        self.specOpnFFTpoints.setObjectName(_fromUtf8("specOpnFFTpoints"))
        self.gridLayout_5.addWidget(self.specOpnFFTpoints, 2, 3, 1, 2)
        self.label_31 = QtGui.QLabel(self.tabopSpectra)
        self.label_31.setObjectName(_fromUtf8("label_31"))
        self.gridLayout_5.addWidget(self.label_31, 6, 0, 1, 2)
        self.label_26 = QtGui.QLabel(self.tabopSpectra)
        self.label_26.setObjectName(_fromUtf8("label_26"))
        self.gridLayout_5.addWidget(self.label_26, 2, 0, 1, 2)
        self.specOpCebIncoherent = QtGui.QCheckBox(self.tabopSpectra)
        self.specOpCebIncoherent.setObjectName(_fromUtf8("specOpCebIncoherent"))
        self.gridLayout_5.addWidget(self.specOpCebIncoherent, 12, 0, 1, 1)
        self.specOpCobIncInt = QtGui.QComboBox(self.tabopSpectra)
        self.specOpCobIncInt.setObjectName(_fromUtf8("specOpCobIncInt"))
        self.specOpCobIncInt.addItem(_fromUtf8(""))
        self.specOpCobIncInt.addItem(_fromUtf8(""))
        self.gridLayout_5.addWidget(self.specOpCobIncInt, 13, 0, 1, 2)
        spacerItem9 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_5.addItem(spacerItem9, 12, 3, 1, 1)
        self.specOpCebRadarfrequency = QtGui.QCheckBox(self.tabopSpectra)
        self.specOpCebRadarfrequency.setObjectName(_fromUtf8("specOpCebRadarfrequency"))
        self.gridLayout_5.addWidget(self.specOpCebRadarfrequency, 0, 0, 1, 2)
        spacerItem10 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_5.addItem(spacerItem10, 9, 3, 1, 1)
        spacerItem11 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_5.addItem(spacerItem11, 7, 3, 1, 1)
        self.specOpRadarfrequency = QtGui.QLineEdit(self.tabopSpectra)
        self.specOpRadarfrequency.setObjectName(_fromUtf8("specOpRadarfrequency"))
        self.gridLayout_5.addWidget(self.specOpRadarfrequency, 0, 3, 1, 2)
        spacerItem12 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_5.addItem(spacerItem12, 4, 3, 1, 1)
        self.label_21 = QtGui.QLabel(self.tabopSpectra)
        self.label_21.setObjectName(_fromUtf8("label_21"))
        self.gridLayout_5.addWidget(self.label_21, 1, 0, 1, 1)
        self.specOpProfiles = QtGui.QLineEdit(self.tabopSpectra)
        self.specOpProfiles.setObjectName(_fromUtf8("specOpProfiles"))
        self.gridLayout_5.addWidget(self.specOpProfiles, 1, 3, 1, 2)
        self.specOpCebRemoveInt = QtGui.QCheckBox(self.tabopSpectra)
        self.specOpCebRemoveInt.setObjectName(_fromUtf8("specOpCebRemoveInt"))
        self.gridLayout_5.addWidget(self.specOpCebRemoveInt, 15, 0, 1, 1)
        spacerItem13 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_5.addItem(spacerItem13, 15, 3, 1, 1)
        self.label_70 = QtGui.QLabel(self.tabopSpectra)
        self.label_70.setObjectName(_fromUtf8("label_70"))
        self.gridLayout_5.addWidget(self.label_70, 3, 0, 1, 1)
        self.specOpCebgetNoise = QtGui.QCheckBox(self.tabopSpectra)
        self.specOpCebgetNoise.setObjectName(_fromUtf8("specOpCebgetNoise"))
        self.gridLayout_5.addWidget(self.specOpCebgetNoise, 16, 0, 1, 1)
        self.specOpippFactor = QtGui.QLineEdit(self.tabopSpectra)
        self.specOpippFactor.setObjectName(_fromUtf8("specOpippFactor"))
        self.gridLayout_5.addWidget(self.specOpippFactor, 3, 3, 1, 2)
        self.specOpComRemoveDC = QtGui.QComboBox(self.tabopSpectra)
        self.specOpComRemoveDC.setObjectName(_fromUtf8("specOpComRemoveDC"))
        self.specOpComRemoveDC.addItem(_fromUtf8(""))
        self.specOpComRemoveDC.addItem(_fromUtf8(""))
        self.gridLayout_5.addWidget(self.specOpComRemoveDC, 14, 3, 1, 2)
        self.specOpgetNoise = QtGui.QLineEdit(self.tabopSpectra)
        self.specOpgetNoise.setObjectName(_fromUtf8("specOpgetNoise"))
        self.gridLayout_5.addWidget(self.specOpgetNoise, 16, 3, 1, 2)
        self.tabWidgetSpectra.addTab(self.tabopSpectra, _fromUtf8(""))
        
        
        self.tabgraphSpectra = QtGui.QWidget()
        self.tabgraphSpectra.setObjectName(_fromUtf8("tabgraphSpectra"))
        self.gridLayout_9 = QtGui.QGridLayout(self.tabgraphSpectra)
        self.gridLayout_9.setObjectName(_fromUtf8("gridLayout_9"))
        
        spacerItem14 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_9.addItem(spacerItem14, 14, 2, 1, 1)  
        
        self.label_24 = QtGui.QLabel(self.tabgraphSpectra)
        self.label_24.setObjectName(_fromUtf8("label_24"))
        self.gridLayout_9.addWidget(self.label_24, 0, 0, 1, 1)
        
        self.specGraphPath = QtGui.QLineEdit(self.tabgraphSpectra)
        self.specGraphPath.setObjectName(_fromUtf8("specGraphPath"))
        self.gridLayout_9.addWidget(self.specGraphPath, 0, 1, 1, 6)

        self.specGraphToolPath = QtGui.QToolButton(self.tabgraphSpectra)
        self.specGraphToolPath.setObjectName(_fromUtf8("specGraphToolPath"))
        self.gridLayout_9.addWidget(self.specGraphToolPath, 0, 7, 1, 1)
        
        self.label_25 = QtGui.QLabel(self.tabgraphSpectra)
        self.label_25.setObjectName(_fromUtf8("label_25"))
        self.gridLayout_9.addWidget(self.label_25, 2, 0, 1, 1)
        self.specGraphPrefix = QtGui.QLineEdit(self.tabgraphSpectra)
        self.specGraphPrefix.setObjectName(_fromUtf8("specGraphPrefix"))
        self.gridLayout_9.addWidget(self.specGraphPrefix, 2, 1, 1, 7)
        
        
        self.label_40 = QtGui.QLabel(self.tabgraphSpectra)
        self.label_40.setObjectName(_fromUtf8("label_40"))
        self.gridLayout_9.addWidget(self.label_40, 6, 0, 1, 1)
        self.label_41 = QtGui.QLabel(self.tabgraphSpectra)
        self.label_41.setObjectName(_fromUtf8("label_41"))
        self.gridLayout_9.addWidget(self.label_41, 8, 0, 1, 1)
        self.label_42 = QtGui.QLabel(self.tabgraphSpectra)
        self.label_42.setObjectName(_fromUtf8("label_42"))
        self.gridLayout_9.addWidget(self.label_42, 9, 0, 1, 1)
        self.label_44 = QtGui.QLabel(self.tabgraphSpectra)
        self.label_44.setObjectName(_fromUtf8("label_44"))
        self.gridLayout_9.addWidget(self.label_44, 10, 0, 1, 1)
        self.label_46 = QtGui.QLabel(self.tabgraphSpectra)
        self.label_46.setObjectName(_fromUtf8("label_46"))
        self.gridLayout_9.addWidget(self.label_46, 11, 0, 1, 1) 
        self.label_45 = QtGui.QLabel(self.tabgraphSpectra)
        self.label_45.setObjectName(_fromUtf8("label_45"))
        self.gridLayout_9.addWidget(self.label_45, 13, 0, 1, 1)
        
        self.label_43 = QtGui.QLabel(self.tabgraphSpectra)
        self.label_43.setObjectName(_fromUtf8("label_43"))
        self.gridLayout_9.addWidget(self.label_43, 3, 3, 2, 1)
        self.specGraphCebSpectraplot = QtGui.QCheckBox(self.tabgraphSpectra)
        self.specGraphCebSpectraplot.setText(_fromUtf8(""))
        self.specGraphCebSpectraplot.setObjectName(_fromUtf8("specGraphCebSpectraplot"))
        self.gridLayout_9.addWidget(self.specGraphCebSpectraplot, 6, 3, 1, 1)
        self.specGraphCebCrossSpectraplot = QtGui.QCheckBox(self.tabgraphSpectra)
        self.specGraphCebCrossSpectraplot.setText(_fromUtf8(""))
        self.specGraphCebCrossSpectraplot.setObjectName(_fromUtf8("specGraphCebCrossSpectraplot"))
        self.gridLayout_9.addWidget(self.specGraphCebCrossSpectraplot, 8, 3, 1, 1)
        self.specGraphCebRTIplot = QtGui.QCheckBox(self.tabgraphSpectra)
        self.specGraphCebRTIplot.setText(_fromUtf8(""))
        self.specGraphCebRTIplot.setObjectName(_fromUtf8("specGraphCebRTIplot"))
        self.gridLayout_9.addWidget(self.specGraphCebRTIplot, 9, 3, 1, 1)
        self.specGraphCebCoherencmap = QtGui.QCheckBox(self.tabgraphSpectra)
        self.specGraphCebCoherencmap.setText(_fromUtf8(""))
        self.specGraphCebCoherencmap.setObjectName(_fromUtf8("specGraphCebCoherencmap"))
        self.gridLayout_9.addWidget(self.specGraphCebCoherencmap, 10, 3, 1, 1)
        self.specGraphPowerprofile = QtGui.QCheckBox(self.tabgraphSpectra)
        self.specGraphPowerprofile.setText(_fromUtf8(""))
        self.specGraphPowerprofile.setObjectName(_fromUtf8("specGraphPowerprofile"))
        self.gridLayout_9.addWidget(self.specGraphPowerprofile, 11, 3, 1, 1)
        self.specGraphCebRTInoise = QtGui.QCheckBox(self.tabgraphSpectra)
        self.specGraphCebRTInoise.setText(_fromUtf8(""))
        self.specGraphCebRTInoise.setObjectName(_fromUtf8("specGraphCebRTInoise"))
        self.gridLayout_9.addWidget(self.specGraphCebRTInoise, 13, 3, 1, 1)
        
#         spacerItem18 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
#         self.gridLayout_9.addItem(spacerItem18, 4, 3, 1, 1)
        
        self.label_47 = QtGui.QLabel(self.tabgraphSpectra)
        self.label_47.setObjectName(_fromUtf8("label_47"))
        self.gridLayout_9.addWidget(self.label_47, 3, 5, 2, 1)
        self.specGraphSaveSpectra = QtGui.QCheckBox(self.tabgraphSpectra)
        self.specGraphSaveSpectra.setText(_fromUtf8(""))
        self.specGraphSaveSpectra.setObjectName(_fromUtf8("specGraphSaveSpectra"))
        self.gridLayout_9.addWidget(self.specGraphSaveSpectra, 6, 5, 1, 1)
        self.specGraphSaveCross = QtGui.QCheckBox(self.tabgraphSpectra)
        self.specGraphSaveCross.setText(_fromUtf8(""))
        self.specGraphSaveCross.setObjectName(_fromUtf8("specGraphSaveCross"))
        self.gridLayout_9.addWidget(self.specGraphSaveCross, 8, 5, 1, 1)
        self.specGraphSaveRTIplot = QtGui.QCheckBox(self.tabgraphSpectra)
        self.specGraphSaveRTIplot.setText(_fromUtf8(""))
        self.specGraphSaveRTIplot.setObjectName(_fromUtf8("specGraphSaveRTIplot"))
        self.gridLayout_9.addWidget(self.specGraphSaveRTIplot, 9, 5, 1, 1)  
        self.specGraphSaveCoherencemap = QtGui.QCheckBox(self.tabgraphSpectra)
        self.specGraphSaveCoherencemap.setText(_fromUtf8(""))
        self.specGraphSaveCoherencemap.setObjectName(_fromUtf8("specGraphSaveCoherencemap"))
        self.gridLayout_9.addWidget(self.specGraphSaveCoherencemap, 10, 5, 1, 1)             
        self.specGraphSavePowerprofile = QtGui.QCheckBox(self.tabgraphSpectra)
        self.specGraphSavePowerprofile.setText(_fromUtf8(""))
        self.specGraphSavePowerprofile.setObjectName(_fromUtf8("specGraphSavePowerprofile"))
        self.gridLayout_9.addWidget(self.specGraphSavePowerprofile, 11, 5, 1, 1)
        self.specGraphSaveRTInoise = QtGui.QCheckBox(self.tabgraphSpectra)
        self.specGraphSaveRTInoise.setText(_fromUtf8(""))
        self.specGraphSaveRTInoise.setObjectName(_fromUtf8("specGraphSaveRTInoise"))
        self.gridLayout_9.addWidget(self.specGraphSaveRTInoise, 13, 5, 1, 1)  
        
        self.label_19 = QtGui.QLabel(self.tabgraphSpectra)
        self.label_19.setObjectName(_fromUtf8("label_19"))
        self.gridLayout_9.addWidget(self.label_19, 3, 7, 2, 1)
        self.specGraphftpSpectra = QtGui.QCheckBox(self.tabgraphSpectra)
        self.specGraphftpSpectra.setText(_fromUtf8(""))
        self.specGraphftpSpectra.setObjectName(_fromUtf8("specGraphftpSpectra"))
        self.gridLayout_9.addWidget(self.specGraphftpSpectra, 6, 7, 1, 1)
        self.specGraphftpCross = QtGui.QCheckBox(self.tabgraphSpectra)
        self.specGraphftpCross.setText(_fromUtf8(""))
        self.specGraphftpCross.setObjectName(_fromUtf8("specGraphftpCross"))
        self.gridLayout_9.addWidget(self.specGraphftpCross, 8, 7, 1, 1)
        self.specGraphftpRTIplot = QtGui.QCheckBox(self.tabgraphSpectra)
        self.specGraphftpRTIplot.setText(_fromUtf8(""))
        self.specGraphftpRTIplot.setObjectName(_fromUtf8("specGraphftpRTIplot"))
        self.gridLayout_9.addWidget(self.specGraphftpRTIplot, 9, 7, 1, 1)
        self.specGraphftpCoherencemap = QtGui.QCheckBox(self.tabgraphSpectra)
        self.specGraphftpCoherencemap.setText(_fromUtf8(""))
        self.specGraphftpCoherencemap.setObjectName(_fromUtf8("specGraphftpCoherencemap"))
        self.gridLayout_9.addWidget(self.specGraphftpCoherencemap, 10, 7, 1, 1)
        self.specGraphftpPowerprofile = QtGui.QCheckBox(self.tabgraphSpectra)
        self.specGraphftpPowerprofile.setText(_fromUtf8(""))
        self.specGraphftpPowerprofile.setObjectName(_fromUtf8("specGraphftpPowerprofile"))
        self.gridLayout_9.addWidget(self.specGraphftpPowerprofile, 11, 7, 1, 1)
        self.specGraphftpRTInoise = QtGui.QCheckBox(self.tabgraphSpectra)
        self.specGraphftpRTInoise.setText(_fromUtf8(""))
        self.specGraphftpRTInoise.setObjectName(_fromUtf8("specGraphftpRTInoise"))
        self.gridLayout_9.addWidget(self.specGraphftpRTInoise, 13, 7, 1, 1)
        
        spacerItem19 = QtGui.QSpacerItem(39, 15, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_9.addItem(spacerItem19, 27, 4, 1, 1)
        
        self.label_22 = QtGui.QLabel(self.tabgraphSpectra)
        self.label_22.setObjectName(_fromUtf8("label_22"))
        self.gridLayout_9.addWidget(self.label_22, 16, 0, 1, 1)
        self.specGgraphFreq = QtGui.QLineEdit(self.tabgraphSpectra)
        self.specGgraphFreq.setObjectName(_fromUtf8("specGgraphFreq"))
        self.gridLayout_9.addWidget(self.specGgraphFreq, 16, 2, 1, 2)
        
        self.label_16 = QtGui.QLabel(self.tabgraphSpectra)
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.gridLayout_9.addWidget(self.label_16, 17, 0, 1, 1)
        self.specGgraphHeight = QtGui.QLineEdit(self.tabgraphSpectra)
        self.specGgraphHeight.setObjectName(_fromUtf8("specGgraphHeight"))
        self.gridLayout_9.addWidget(self.specGgraphHeight, 17, 2, 1, 2)
        
        self.label_17 = QtGui.QLabel(self.tabgraphSpectra)
        self.label_17.setObjectName(_fromUtf8("label_17"))
        self.gridLayout_9.addWidget(self.label_17, 18, 0, 1, 1)
        self.specGgraphDbsrange = QtGui.QLineEdit(self.tabgraphSpectra)
        self.specGgraphDbsrange.setObjectName(_fromUtf8("specGgraphDbsrange"))
        self.gridLayout_9.addWidget(self.specGgraphDbsrange, 18, 2, 1, 2)

        self.specGraphTminTmaxLabel = QtGui.QLabel(self.tabgraphSpectra)
        self.specGraphTminTmaxLabel.setObjectName(_fromUtf8("specGraphTminTmaxLabel"))
        self.gridLayout_9.addWidget(self.specGraphTminTmaxLabel, 19, 0, 1, 2)
        self.specGgraphTminTmax = QtGui.QLineEdit(self.tabgraphSpectra)
        self.specGgraphTminTmax.setObjectName(_fromUtf8("specGgraphTminTmax"))
        self.gridLayout_9.addWidget(self.specGgraphTminTmax, 19, 2, 1, 2)
        
        self.specGraphMagLabel = QtGui.QLabel(self.tabgraphSpectra)
        self.specGraphMagLabel.setObjectName(_fromUtf8("specGraphMagLabel"))
        self.gridLayout_9.addWidget(self.specGraphMagLabel, 16, 4, 1, 2)
        self.specGgraphmagnitud = QtGui.QLineEdit(self.tabgraphSpectra)
        self.specGgraphmagnitud.setObjectName(_fromUtf8("specGgraphmagnitud"))
        self.gridLayout_9.addWidget(self.specGgraphmagnitud, 16, 6, 1, 2)
        
        self.specGraphPhaseLabel = QtGui.QLabel(self.tabgraphSpectra)
        self.specGraphPhaseLabel.setObjectName(_fromUtf8("specGraphPhaseLabel"))
        self.gridLayout_9.addWidget(self.specGraphPhaseLabel, 17, 4, 1, 2)
        self.specGgraphPhase = QtGui.QLineEdit(self.tabgraphSpectra)
        self.specGgraphPhase.setObjectName(_fromUtf8("specGgraphPhase"))
        self.gridLayout_9.addWidget(self.specGgraphPhase, 17, 6, 1, 2)

        self.label_6 = QtGui.QLabel(self.tabgraphSpectra)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_9.addWidget(self.label_6, 18, 4, 1, 1)
        self.specGgraphChannelList = QtGui.QLineEdit(self.tabgraphSpectra)
        self.specGgraphChannelList.setObjectName(_fromUtf8("specGgraphChannelList"))
        self.gridLayout_9.addWidget(self.specGgraphChannelList, 18, 6, 1, 2)
        
        self.label_29 = QtGui.QLabel(self.tabgraphSpectra)
        self.label_29.setObjectName(_fromUtf8("label_29"))
        self.gridLayout_9.addWidget(self.label_29, 19, 4, 1, 2)
        self.specGgraphftpratio = QtGui.QLineEdit(self.tabgraphSpectra)
        self.specGgraphftpratio.setObjectName(_fromUtf8("specGgraphftpratio"))
        self.gridLayout_9.addWidget(self.specGgraphftpratio, 19, 6, 1, 2)

        self.label_48 = QtGui.QLabel(self.tabgraphSpectra)
        self.label_48.setObjectName(_fromUtf8("label_48"))
        self.gridLayout_9.addWidget(self.label_48, 20, 4, 1, 2)
        self.specGgraphTimeRange = QtGui.QLineEdit(self.tabgraphSpectra)
        self.specGgraphTimeRange.setObjectName(_fromUtf8("specGgraphTimeRange"))
        self.gridLayout_9.addWidget(self.specGgraphTimeRange, 20, 6, 1, 2)
        
        spacerItem15 = QtGui.QSpacerItem(28, 15, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_9.addItem(spacerItem15, 27, 6, 1, 2)
        spacerItem16 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_9.addItem(spacerItem16, 3, 5, 1, 1)
        spacerItem17 = QtGui.QSpacerItem(49, 15, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_9.addItem(spacerItem17, 27, 0, 1, 1)

        
               
        self.tabWidgetSpectra.addTab(self.tabgraphSpectra, _fromUtf8(""))
        self.taboutputSpectra = QtGui.QWidget()
        self.taboutputSpectra.setObjectName(_fromUtf8("taboutputSpectra"))
        self.gridLayout_11 = QtGui.QGridLayout(self.taboutputSpectra)
        self.gridLayout_11.setObjectName(_fromUtf8("gridLayout_11"))
        self.label_39 = QtGui.QLabel(self.taboutputSpectra)
        self.label_39.setObjectName(_fromUtf8("label_39"))
        self.gridLayout_11.addWidget(self.label_39, 0, 0, 1, 1)
        self.specOutputComData = QtGui.QComboBox(self.taboutputSpectra)
        self.specOutputComData.setObjectName(_fromUtf8("specOutputComData"))
        self.specOutputComData.addItem(_fromUtf8(""))
        self.gridLayout_11.addWidget(self.specOutputComData, 0, 2, 1, 2)
        self.label_34 = QtGui.QLabel(self.taboutputSpectra)
        self.label_34.setObjectName(_fromUtf8("label_34"))
        self.gridLayout_11.addWidget(self.label_34, 1, 0, 1, 1)
        self.specOutputPath = QtGui.QLineEdit(self.taboutputSpectra)
        self.specOutputPath.setObjectName(_fromUtf8("specOutputPath"))
        self.gridLayout_11.addWidget(self.specOutputPath, 1, 2, 1, 1)
        spacerItem20 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_11.addItem(spacerItem20, 4, 2, 1, 1)
        self.specOutputToolPath = QtGui.QToolButton(self.taboutputSpectra)
        self.specOutputToolPath.setObjectName(_fromUtf8("specOutputToolPath"))
        self.gridLayout_11.addWidget(self.specOutputToolPath, 1, 3, 1, 1)
        self.specOutputblocksperfile = QtGui.QLineEdit(self.taboutputSpectra)
        self.specOutputblocksperfile.setObjectName(_fromUtf8("specOutputblocksperfile"))
        self.gridLayout_11.addWidget(self.specOutputblocksperfile, 2, 2, 1, 1)
        self.label_9 = QtGui.QLabel(self.taboutputSpectra)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.gridLayout_11.addWidget(self.label_9, 2, 0, 1, 2)
        self.label_38 = QtGui.QLabel(self.taboutputSpectra)
        self.label_38.setObjectName(_fromUtf8("label_38"))
        self.gridLayout_11.addWidget(self.label_38, 3, 0, 1, 1)
        self.specOutputprofileperblock = QtGui.QLineEdit(self.taboutputSpectra)
        self.specOutputprofileperblock.setObjectName(_fromUtf8("specOutputprofileperblock"))
        self.gridLayout_11.addWidget(self.specOutputprofileperblock, 3, 2, 1, 1)
        self.tabWidgetSpectra.addTab(self.taboutputSpectra, _fromUtf8(""))
        self.gridLayout_7.addWidget(self.tabWidgetSpectra, 0, 1, 1, 1)
        
        self.tabWidgetProject.addTab(self.tabSpectra, _fromUtf8(""))
        
        self.tabWidgetSpectra.setCurrentIndex(0)
        
    def retranslateUi(self):
        
        self.specOpOk.setText(_translate("MainWindow", "Ok", None))
        self.specGraphClear.setText(_translate("MainWindow", "Clear", None))
        self.specOpCebCrossSpectra.setText(_translate("MainWindow", "Select  Cross Spectra", None))
        self.specOpComChannel.setItemText(0, _translate("MainWindow", "Value", None))
        self.specOpComChannel.setItemText(1, _translate("MainWindow", "Index", None))
        self.specOpComHeights.setItemText(0, _translate("MainWindow", "Value", None))
        self.specOpComHeights.setItemText(1, _translate("MainWindow", "Index", None))
        self.specOpCebRemoveDC.setText(_translate("MainWindow", "Remove DC", None))
        self.specOpCebHeights.setText(_translate("MainWindow", "Select Heights", None))
        self.specOpCebChannel.setText(_translate("MainWindow", "Select Channel", None))
        self.label_31.setText(_translate("MainWindow", "x-y pairs", None))
        self.label_26.setText(_translate("MainWindow", "nFFTPoints", None))
        self.specOpCebIncoherent.setText(_translate("MainWindow", "Incoherent Integration", None))
        self.specOpCobIncInt.setItemText(0, _translate("MainWindow", "Time Interval", None))
        self.specOpCobIncInt.setItemText(1, _translate("MainWindow", "Profiles", None))
        self.specOpCebRadarfrequency.setText(_translate("MainWindow", "Radar Frequency", None))
        self.label_21.setText(_translate("MainWindow", "Profiles", None))
        self.specOpCebRemoveInt.setText(_translate("MainWindow", "Remove Interference", None))
        self.label_70.setText(_translate("MainWindow", "IppFactor", None))
        self.specOpCebgetNoise.setText(_translate("MainWindow", "Get Noise", None))
        self.specOpComRemoveDC.setItemText(0, _translate("MainWindow", "Mode 1", None))
        self.specOpComRemoveDC.setItemText(1, _translate("MainWindow", "Mode 2", None))
        self.tabWidgetSpectra.setTabText(self.tabWidgetSpectra.indexOf(self.tabopSpectra), _translate("MainWindow", "Operation", None))
        
        self.label_44.setText(_translate("MainWindow", "Coherence Map", None))
        self.specGraphTminTmaxLabel.setText(_translate("MainWindow", "Time range:", None))
        self.label_25.setText(_translate("MainWindow", "Prefix", None))
        self.label_42.setText(_translate("MainWindow", "RTI Plot", None))
        self.label_16.setText(_translate("MainWindow", "Height range", None))
        self.label_17.setText(_translate("MainWindow", "dB range", None))
        self.specGraphMagLabel.setText(_translate("MainWindow", "Coh. Magnitud ", None))
        self.label_24.setText(_translate("MainWindow", "Path", None))
        self.label_46.setText(_translate("MainWindow", "Power Profile", None))
        self.label_22.setText(_translate("MainWindow", "Freq/Vel range:", None))
        self.label_41.setText(_translate("MainWindow", "Cross Spectra Plot", None))
        self.specGraphToolPath.setText(_translate("MainWindow", "...", None))
        self.label_6.setText(_translate("MainWindow", "Channel List:", None))
        self.label_40.setText(_translate("MainWindow", "Spectra Plot", None))
        self.label_43.setText(_translate("MainWindow", "Show", None))
        self.label_29.setText(_translate("MainWindow", "Writing Period:", None))
        self.label_47.setText(_translate("MainWindow", "Save", None))
        self.label_19.setText(_translate("MainWindow", "Ftp", None))
        self.label_45.setText(_translate("MainWindow", "Noise", None))
        self.label_48.setText(_translate("MainWindow", "Time Range:", None))
        self.specGraphPhaseLabel.setText(_translate("MainWindow", "Coh. Phase:", None))
        self.label_48.hide()
        self.specGgraphTimeRange.hide()
        self.tabWidgetSpectra.setTabText(self.tabWidgetSpectra.indexOf(self.tabgraphSpectra), _translate("MainWindow", "Graphics", None))
        
        self.label_39.setText(_translate("MainWindow", "Type:", None))
        self.specOutputComData.setItemText(0, _translate("MainWindow", ".pdata", None))
        self.label_34.setText(_translate("MainWindow", "Path:", None))
        self.specOutputToolPath.setText(_translate("MainWindow", "...", None))
        self.label_9.setText(_translate("MainWindow", "Blocks per File:  ", None))
        self.label_38.setText(_translate("MainWindow", "Profile per Block: ", None))
        self.tabWidgetSpectra.setTabText(self.tabWidgetSpectra.indexOf(self.taboutputSpectra), _translate("MainWindow", "Output", None))
        
        self.tabWidgetProject.setTabText(self.tabWidgetProject.indexOf(self.tabSpectra), _translate("MainWindow", "Spectra", None))
        