You should install "digital_rf_hdf5" module if you want to read USRP data
BeaconPhase
parameters = { 
	'id': 'string',
	'wintitle': 'string',
	'pairsList': 'pairsList',
	'showprofile': 'boolean',
	'xmin': 'float',
	'xmax': 'float',
	'ymin': 'float',
	'ymax': 'float',
	'hmin': 'float',
	'hmax': 'float',
	'timerange': 'float',
	'save': 'boolean',
	'figpath': 'string',
	'figfile': 'string',
	'show': 'boolean',
	'ftp': 'boolean',
	'wr_period': 'int',
	'server': 'string',
	'folder': 'string',
	'username': 'string',
	'password': 'string',
	'ftp_wei': 'int',
	'exp_code': 'int',
	'sub_exp_code': 'int',
	'plot_pos': 'int',
 }


BeamSelector
parameters = { 
	'beam': 'string',
 }


CohInt
parameters = { 
	'n': 'int', 
	'timeInterval': 'float', 
	'overlapping': 'boolean', 
	'byblock': 'boolean'
}


CoherenceMap
parameters = { 
	'id': 'string',
	'wintitle': 'string',
	'pairsList': 'pairsLists',
	'showprofile': 'boolean',
	'xmin': 'float',
	'xmax': 'float',
	'ymin': 'float',
	'ymax': 'float',
	'zmin': 'float',
	'zmax': 'float',
	'timerange': 'float',
	'phase_min': 'float',
	'phase_max': 'float',
	'save': 'boolean',
	'figpath': 'string',
	'figfile': 'string',
	'ftp': 'boolean',
	'wr_period': 'int',
	'coherence_cmap': 'colormap',
	'phase_cmap': 'colormap',
	'show': 'boolean',
	'server': 'string',
	'folder': 'string',
	'username': 'string',
	'password': 'string',
	'ftp_wei': 'int',
	'exp_code': 'int',
	'sub_exp_code': 'int',
	'plot_pos': 'int',
 }


CombineProfiles
parameters = { 
	'n': 'int',
 }


CorrectSMPhases
parameters = { 
	'phaseOffsets': 'pairsLists',
	'hmin': 'float',
	'hmax': 'float',
	'azimuth': 'string',
	'channelPositions': 'string',
 }


CorrelationPlot
parameters = { 
	'id': 'string',
	'wintitle': 'string',
	'channelList': 'string',
	'showprofile': 'string',
	'xmin': 'float',
	'xmax': 'float',
	'ymin': 'float',
	'ymax': 'float',
	'zmin': 'float',
	'zmax': 'float',
	'save': 'boolean',
	'figpath': 'string',
	'figfile': 'string',
	'show': 'boolean',
	'ftp': 'boolean',
	'wr_period': 'int',
	'server': 'string',
	'folder': 'string',
	'username': 'string',
	'password': 'string',
	'ftp_wei': 'string',
	'exp_code': 'int',
	'sub_exp_code': 'int',
	'plot_pos': 'int',
	'realtime': 'string',
 }


CrossSpectraPlot
parameters = { 
	'id': 'string',
	'wintitle': 'string',
	'pairsList': 'pairsLists',
	'xmin': 'float',
	'xmax': 'float',
	'ymin': 'float',
	'ymax': 'float',
	'zmin': 'float',
	'zmax': 'float',
	'coh_min': 'string',
	'coh_max': 'string',
	'phase_min': 'string',
	'phase_max': 'string',
	'save': 'boolean',
	'figpath': 'string',
	'figfile': 'string',
	'ftp': 'boolean',
	'wr_period': 'int',
	'power_cmap': 'string',
	'coherence_cmap': 'string',
	'phase_cmap': 'string',
	'show': 'string',
	'server': 'string',
	'folder': 'string',
	'username': 'string',
	'password': 'string',
	'ftp_wei': 'string',
	'exp_code': 'int',
	'sub_exp_code': 'int',
	'plot_pos': 'int',
	'xaxis': 'string',
 }


Decoder
parameters = { 
	'code': 'string',
	'nCode': 'string',
	'nBaud': 'string',
	'mode': 'string',
	'osamp': 'string',
	'times': 'string',
 }


EWDriftsEstimation
parameters = { 
	'zenith': 'string',
	'zenithCorrection': 'string',
 }


EWDriftsPlot
parameters = { 
	'id': 'string',
	'wintitle': 'string',
	'channelList': 'string',
	'xmin': 'float',
	'xmax': 'float',
	'ymin': 'float',
	'ymax': 'float',
	'zmin': 'float',
	'zmax': 'float',
	'zmaxVertfloat 'string',
	'zminVertfloat 'string',
	'zmaxZonafloattring',
	'zminZonafloattring',
	'timerange': 'string',
	'SNRthresh': 'string',
	'SNRmin': 'string',
	'SNRmax': 'string',
	'SNR_1': 'string',
	'save': 'boolean',
	'figpath': 'string',
	'lastone': 'string',
	'figfile': 'string',
	'ftp': 'string',
	'wr_period': 'int',
	'show': 'string',
	'server': 'string',
	'folder': 'string',
	'username': 'string',
	'password': 'string',
	'ftp_wei': 'string',
	'exp_code': 'int',
	'sub_exp_code': 'int',
	'plot_pos': 'int',
 }


Figure
parameters = { 
: 'string',
 }


FitsWriter
parameters = { 
: 'string',
 }


IncohInt
parameters = { 
	'n': 'string',
	'timeInterval': 'string',
	'overlapping': 'string',
 }


IncohInt4SpectraHeis
parameters = { 
: 'string',
 }


MomentsPlot
parameters = { 
	'id': 'string',
	'wintitle': 'string',
	'channelList': 'string',
	'showprofile': 'string',
	'xmin': 'float',
	'xmax': 'float',
	'ymin': 'float',
	'ymax': 'float',
	'zmin': 'float',
	'zmax': 'float',
	'save': 'boolean',
	'figpath': 'string',
	'figfile': 'string',
	'show': 'string',
	'ftp': 'string',
	'wr_period': 'int',
	'server': 'string',
	'folder': 'string',
	'username': 'string',
	'password': 'string',
	'ftp_wei': 'string',
	'exp_code': 'int',
	'sub_exp_code': 'int',
	'plot_pos': 'int',
	'realtime': 'string',
 }


NSMeteorDetection1Plot
parameters = { 
	'id': 'string',
	'wintitle': 'string',
	'channelList': 'string',
	'showprofile': 'string',
	'xmin': 'float',
	'xmax': 'float',
	'ymin': 'float',
	'ymax': 'float',
	'SNRmin': 'string',
	'SNRmax': 'string',
	'vmin': 'string',
	'vmax': 'string',
	'wmin': 'string',
	'wmax': 'string',
	'mode': 'string',
	'save': 'boolean',
	'figpath': 'string',
	'figfile': 'string',
	'show': 'string',
	'ftp': 'string',
	'wr_period': 'int',
	'server': 'string',
	'folder': 'string',
	'username': 'string',
	'password': 'string',
	'ftp_wei': 'string',
	'exp_code': 'int',
	'sub_exp_code': 'int',
	'plot_pos': 'int',
	'realtime': 'string',
	'xaxis': 'string',
 }


NSMeteorDetection2Plot
parameters = { 
	'id': 'string',
	'wintitle': 'string',
	'channelList': 'string',
	'showprofile': 'string',
	'xmin': 'float',
	'xmax': 'float',
	'ymin': 'float',
	'ymax': 'float',
	'SNRmin': 'string',
	'SNRmax': 'string',
	'vmin': 'string',
	'vmax': 'string',
	'wmin': 'string',
	'wmax': 'string',
	'mode': 'string',
	'save': 'boolean',
	'figpath': 'string',
	'figfile': 'string',
	'show': 'string',
	'ftp': 'string',
	'wr_period': 'int',
	'server': 'string',
	'folder': 'string',
	'username': 'string',
	'password': 'string',
	'ftp_wei': 'string',
	'exp_code': 'int',
	'sub_exp_code': 'int',
	'plot_pos': 'int',
	'realtime': 'string',
	'xaxis': 'string',
 }


Noise
parameters = { 
	'id': 'string',
	'wintitle': 'string',
	'channelList': 'string',
	'showprofile': 'string',
	'xmin': 'float',
	'xmax': 'float',
	'ymin': 'float',
	'ymax': 'float',
	'timerange': 'string',
	'save': 'boolean',
	'figpath': 'string',
	'figfile': 'string',
	'show': 'string',
	'ftp': 'string',
	'wr_period': 'int',
	'server': 'string',
	'folder': 'string',
	'username': 'string',
	'password': 'string',
	'ftp_wei': 'string',
	'exp_code': 'int',
	'sub_exp_code': 'int',
	'plot_pos': 'int',
 }


NonSpecularMeteorDetection
parameters = { 
	'mode': 'string',
	'SNRthresh': 'string',
	'phaseDerThresh': 'string',
	'cohThresh': 'string',
	'allData': 'string',
 }


Operation
parameters = { 
	'dataIn': 'string',
 }


ParamWriter
parameters = { 
: 'string',
 }


Parameters1Plot
parameters = { 
	'id': 'string',
	'wintitle': 'string',
	'channelList': 'string',
	'showprofile': 'string',
	'xmin': 'float',
	'xmax': 'float',
	'ymin': 'float',
	'ymax': 'float',
	'zmin': 'float',
	'zmax': 'float',
	'timerange': 'string',
	'parameterIndex': 'string',
	'onlyPositive': 'string',
	'SNRthresh': 'string',
	'SNR': 'string',
	'SNRmin': 'string',
	'SNRmax': 'string',
	'onlySNR': 'string',
	'DOP': 'string',
	'zlabel': 'string',
	'parameterName': 'string',
	'parameterObject': 'string',
	'save': 'boolean',
	'figpath': 'string',
	'lastone': 'string',
	'figfile': 'string',
	'ftp': 'string',
	'wr_period': 'int',
	'show': 'string',
	'server': 'string',
	'folder': 'string',
	'username': 'string',
	'password': 'string',
	'ftp_wei': 'string',
	'exp_code': 'int',
	'sub_exp_code': 'int',
	'plot_pos': 'int',
 }


ParametersPlot
parameters = { 
	'id': 'string',
	'wintitle': 'string',
	'channelList': 'string',
	'paramIndex': 'string',
	'colormap': 'string',
	'xmin': 'float',
	'xmax': 'float',
	'ymin': 'float',
	'ymax': 'float',
	'zmin': 'float',
	'zmax': 'float',
	'timerange': 'string',
	'showSNR': 'string',
	'SNRthresh': 'string',
	'SNRmin': 'string',
	'SNRmax': 'string',
	'save': 'boolean',
	'figpath': 'string',
	'lastone': 'string',
	'figfile': 'string',
	'ftp': 'string',
	'wr_period': 'int',
	'show': 'string',
	'server': 'string',
	'folder': 'string',
	'username': 'string',
	'password': 'string',
	'ftp_wei': 'string',
	'exp_code': 'int',
	'sub_exp_code': 'int',
	'plot_pos': 'int',
 }


PhasePlot
parameters = { 
	'id': 'string',
	'wintitle': 'string',
	'pairsList': 'pairsLists',
	'showprofile': 'string',
	'xmin': 'float',
	'xmax': 'float',
	'ymin': 'float',
	'ymax': 'float',
	'timerange': 'string',
	'save': 'boolean',
	'figpath': 'string',
	'figfile': 'string',
	'show': 'string',
	'ftp': 'string',
	'wr_period': 'int',
	'server': 'string',
	'folder': 'string',
	'username': 'string',
	'password': 'string',
	'ftp_wei': 'string',
	'exp_code': 'int',
	'sub_exp_code': 'int',
	'plot_pos': 'int',
 }


PlotCOHData
parameters = { 
: 'string',
 }


PlotCrossSpectraData
parameters = { 
: 'string',
 }


PlotDOPData
parameters = { 
: 'string',
 }


PlotData
parameters = { 
: 'string',
 }


PlotNoiseData
parameters = { 
: 'string',
 }


PlotPHASEData
parameters = { 
: 'string',
 }


PlotRTIData
parameters = { 
: 'string',
 }


PlotSNRData
parameters = { 
: 'string',
 }


PlotSpectraData
parameters = { 
: 'string',
 }


PlotSpectraMeanData
parameters = { 
: 'string',
 }


PlotWindProfilerData
parameters = { 
: 'string',
 }


PowerProfilePlot
parameters = { 
	'id': 'string',
	'wintitle': 'string',
	'channelList': 'string',
	'xmin': 'float',
	'xmax': 'float',
	'ymin': 'float',
	'ymax': 'float',
	'save': 'boolean',
	'figpath': 'string',
	'figfile': 'string',
	'show': 'string',
	'ftp': 'string',
	'wr_period': 'int',
	'server': 'string',
	'folder': 'string',
	'username': 'string',
	'password': 'string',
 }


PrintInfo
parameters = { 
: 'string',
 }


ProfileConcat
parameters = { 
	'm': 'string',
 }


ProfileSelector
parameters = { 
	'profileList': 'string',
	'profileRangeList': 'string',
	'beam': 'string',
	'byblock': 'string',
	'rangeList': 'string',
	'nProfiles': 'string',
 }


ProfileToChannels
parameters = { 
: 'string',
 }


PublishData
parameters = { 
: 'string',
 }


RTIPlot
parameters = { 
	'id': 'string',
	'wintitle': 'string',
	'channelList': 'string',
	'showprofile': 'string',
	'xmin': 'float',
	'xmax': 'float',
	'ymin': 'float',
	'ymax': 'float',
	'zmin': 'float',
	'zmax': 'float',
	'timerange': 'string',
	'save': 'boolean',
	'figpath': 'string',
	'lastone': 'string',
	'figfile': 'string',
	'ftp': 'string',
	'wr_period': 'int',
	'show': 'string',
	'server': 'string',
	'folder': 'string',
	'username': 'string',
	'password': 'string',
	'ftp_wei': 'string',
	'exp_code': 'int',
	'sub_exp_code': 'int',
	'plot_pos': 'int',
 }


RTIfromSpectraHeis
parameters = { 
	'id': 'string',
	'wintitle': 'string',
	'channelList': 'string',
	'showprofile': 'string',
	'xmin': 'float',
	'xmax': 'float',
	'ymin': 'float',
	'ymax': 'float',
	'timerange': 'string',
	'save': 'boolean',
	'figpath': 'string',
	'figfile': 'string',
	'ftp': 'string',
	'wr_period': 'int',
	'show': 'string',
	'server': 'string',
	'folder': 'string',
	'username': 'string',
	'password': 'string',
	'ftp_wei': 'string',
	'exp_code': 'int',
	'sub_exp_code': 'int',
	'plot_pos': 'int',
 }


Reshaper
parameters = { 
	'shape': 'string',
	'nTxs': 'string',
 }


SALags
parameters = { 
: 'string',
 }


SMDetection
parameters = { 
	'hei_ref': 'string',
	'tauindex': 'string',
	'phaseOffsets': 'string',
	'cohDetection': 'string',
	'cohDet_timeStep': 'string',
	'cohDet_thresh': 'string',
	'noise_timeStep': 'string',
	'noise_multiple': 'string',
	'multDet_timeLimit': 'string',
	'multDet_rangeLimit': 'string',
	'phaseThresh': 'string',
	'SNRThresh': 'string',
	'hmin': 'string',
	'hmax': 'string',
	'azimuth': 'string',
	'channelPositions': 'string',
 }


SMPhaseCalibration
parameters = { 
	'hmin': 'string',
	'hmax': 'string',
	'channelPositions': 'string',
	'nHours': 'string',
 }


Scope
parameters = { 
	'id': 'string',
	'wintitle': 'string',
	'channelList': 'string',
	'xmin': 'float',
	'xmax': 'float',
	'ymin': 'float',
	'ymax': 'float',
	'save': 'boolean',
	'figpath': 'string',
	'figfile': 'string',
	'show': 'string',
	'wr_period': 'int',
	'ftp': 'string',
	'server': 'string',
	'folder': 'string',
	'username': 'string',
	'password': 'string',
	'type': 'string',
 }


SendByFTP
parameters = { 
	'ext': 'string',
	'localfolder': 'string',
	'remotefolder': 'string',
	'server': 'string',
	'username': 'string',
	'password': 'string',
	'period': 'string',
 }


SkyMapPlot
parameters = { 
	'id': 'string',
	'wintitle': 'string',
	'channelList': 'string',
	'showprofile': 'string',
	'tmin': 'string',
	'tmax': 'string',
	'timerange': 'string',
	'save': 'boolean',
	'figpath': 'string',
	'figfile': 'string',
	'show': 'string',
	'ftp': 'string',
	'wr_period': 'int',
	'server': 'string',
	'folder': 'string',
	'username': 'string',
	'password': 'string',
	'ftp_wei': 'string',
	'exp_code': 'int',
	'sub_exp_code': 'int',
	'plot_pos': 'int',
	'realtime': 'string',
 }


SpectraCutPlot
parameters = { 
	'id': 'string',
	'wintitle': 'string',
	'channelList': 'string',
	'xmin': 'float',
	'xmax': 'float',
	'ymin': 'float',
	'ymax': 'float',
	'save': 'boolean',
	'figpath': 'string',
	'figfile': 'string',
	'show': 'string',
	'ftp': 'string',
	'wr_period': 'int',
	'server': 'string',
	'folder': 'string',
	'username': 'string',
	'password': 'string',
	'xaxis': 'string',
 }


SpectraHeisScope
parameters = { 
	'id': 'string',
	'wintitle': 'string',
	'channelList': 'string',
	'xmin': 'float',
	'xmax': 'float',
	'ymin': 'float',
	'ymax': 'float',
	'save': 'boolean',
	'figpath': 'string',
	'figfile': 'string',
	'ftp': 'string',
	'wr_period': 'int',
	'show': 'string',
	'server': 'string',
	'folder': 'string',
	'username': 'string',
	'password': 'string',
	'ftp_wei': 'string',
	'exp_code': 'int',
	'sub_exp_code': 'int',
	'plot_pos': 'int',
 }


SpectraHeisWriter
parameters = { 
: 'string',
 }


SpectraPlot
parameters = { 
	'id': 'string',
	'wintitle': 'string',
	'channelList': 'string',
	'showprofile': 'string',
	'xmin': 'float',
	'xmax': 'float',
	'ymin': 'float',
	'ymax': 'float',
	'zmin': 'float',
	'zmax': 'float',
	'save': 'boolean',
	'figpath': 'string',
	'figfile': 'string',
	'show': 'string',
	'ftp': 'string',
	'wr_period': 'int',
	'server': 'string',
	'folder': 'string',
	'username': 'string',
	'password': 'string',
	'ftp_wei': 'string',
	'exp_code': 'int',
	'sub_exp_code': 'int',
	'plot_pos': 'int',
	'realtime': 'string',
	'xaxis': 'string',
 }


SpectraWriter
parameters = { 
	'path': 'string',
	'blocksPerFile': 'string',
	'profilesPerBlock': 'string',
	'set': 'string',
	'ext': 'string',
	'datatype': 'string',
 }


SpectralFitting
parameters = { 
	'getSNR': 'string',
	'path': 'string',
	'file': 'string',
	'groupList': 'string',
 }


SpectralFittingPlot
parameters = { 
	'id': 'string',
	'cutHeight': 'string',
	'fit': 'string',
	'wintitle': 'string',
	'channelList': 'string',
	'showprofile': 'string',
	'xmin': 'float',
	'xmax': 'float',
	'ymin': 'float',
	'ymax': 'float',
	'save': 'boolean',
	'figpath': 'string',
	'figfile': 'string',
	'show': 'string',
 }


SpectralMoments
parameters = { 
: 'string',
 }


SplitProfiles
parameters = { 
	'n': 'string',
 }


USRPWriter
parameters = { 
	'dataIn': 'string',
 }


VoltageWriter
parameters = { 
	'path': 'string',
	'blocksPerFile': 'string',
	'profilesPerBlock': 'string',
	'set': 'string',
	'ext': 'string',
	'datatype': 'string',
 }


WindProfiler
parameters = { 
	'technique': 'string',
 }


WindProfilerPlot
parameters = { 
	'id': 'string',
	'wintitle': 'string',
	'channelList': 'string',
	'showprofile': 'string',
	'xmin': 'float',
	'xmax': 'float',
	'ymin': 'float',
	'ymax': 'float',
	'zmin': 'float',
	'zmax': 'float',
	'zmax_ver': 'string',
	'zmin_ver': 'string',
	'SNRmin': 'string',
	'SNRmax': 'string',
	'timerange': 'string',
	'SNRthresh': 'string',
	'save': 'boolean',
	'figpath': 'string',
	'lastone': 'string',
	'figfile': 'string',
	'ftp': 'string',
	'wr_period': 'int',
	'show': 'string',
	'server': 'string',
	'folder': 'string',
	'username': 'string',
	'password': 'string',
	'ftp_wei': 'string',
	'exp_code': 'int',
	'sub_exp_code': 'int',
	'plot_pos': 'int',
 }


Writer
parameters = { 
	'dataIn': 'string',
 }


AMISRProc
parameters = { 
: 'string',
 }


AMISRReader
parameters = { 
: 'string',
 }


CorrelationProc
parameters = { 
	'lags': 'string',
	'mode': 'string',
	'pairsList': 'pairsLists',
	'fullBuffer': 'string',
	'nAvg': 'string',
	'removeDC': 'string',
	'splitCF': 'string',
 }


FitsReader
parameters = { 
: 'string',
 }


HFReader
parameters = { 
: 'string',
 }


ParamReader
parameters = { 
: 'string',
 }


ParametersProc
parameters = { 
: 'string',
 }


ProcessingUnit
parameters = { 
: 'string',
 }


ReceiverData
parameters = { 
: 'string',
 }


SendToServer
parameters = { 
: 'string',
 }


SpectraAFCProc
parameters = { 
	'nProfiles': 'string',
	'nFFTPoints': 'string',
	'pairsList': 'pairsLists',
	'code': 'string',
	'nCode': 'string',
	'nBaud': 'string',
 }


SpectraHeisProc
parameters = { 
: 'string',
 }


SpectraLagsProc
parameters = { 
	'nProfiles': 'string',
	'nFFTPoints': 'string',
	'pairsList': 'pairsLists',
	'code': 'string',
	'nCode': 'string',
	'nBaud': 'string',
	'codeFromHeader': 'string',
	'pulseIndex': 'string',
 }


SpectraProc
parameters = { 
	'nProfiles': 'string',
	'nFFTPoints': 'string',
	'pairsList': 'pairsLists',
	'ippFactor': 'string',
 }


SpectraReader
parameters = { 
	'path': 'string',
	'startDate': 'string',
	'endDate': 'string',
	'startTime': 'string',
	'endTime': 'string',
	'set': 'string',
	'expLabel': 'string',
	'ext': 'string',
	'online': 'string',
	'delay': 'string',
	'walk': 'string',
	'getblock': 'string',
	'nTxs': 'string',
	'realtime': 'string',
	'blocksize': 'string',
	'blocktime': 'string',
	'queue': 'string',
	'skip': 'string',
	'cursor': 'string',
	'warnings': 'string',
	'verbose': 'string',
 }


USRPReader
parameters = { 
: 'string',
 }


VoltageProc
parameters = { 
: 'string',
 }


VoltageReader
parameters = { 
	'path': 'string',
	'startDate': 'string',
	'endDate': 'string',
	'startTime': 'string',
	'endTime': 'string',
	'set': 'string',
	'expLabel': 'string',
	'ext': 'string',
	'online': 'string',
	'delay': 'string',
	'walk': 'string',
	'getblock': 'string',
	'nTxs': 'string',
	'realtime': 'string',
	'blocksize': 'string',
	'blocktime': 'string',
	'queue': 'string',
	'skip': 'string',
	'cursor': 'string',
	'warnings': 'string',
	'verbose': 'string',
 }


