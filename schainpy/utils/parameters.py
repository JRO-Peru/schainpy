
global_type_string = 'string'
global_type_integer = 'int'
global_type_floatList = 'floatList'
global_type_pairsList = 'pairsList'
global_type_boolean = 'bolean'
global_type_float = 'float'
global_type_colormap = 'colormap'
global_type_list = 'list'
global_type_integer_or_list = 'integer_or_list'

#BeaconPhase
parameters = {
	'id': global_type_string,
	'wintitle': global_type_string,
	'pairsList': global_type_pairsList,
	'showprofile': global_type_boolean,
	'xmin': global_type_float,
	'xmax': global_type_float,
	'ymin': global_type_float,
	'ymax': global_type_float,
	'hmin': global_type_float,
	'hmax': global_type_float,
	'timerange': global_type_float,
	'save': global_type_boolean,
	'figpath': global_type_string,
	'figfile': global_type_string,
	'show': global_type_boolean,
	'ftp': global_type_boolean,
	'wr_period': global_type_integer,
	'server': global_type_string,
	'folder': global_type_string,
	'username': global_type_string,
	'password': global_type_string,
	'ftp_wei': global_type_integer,
	'exp_code': global_type_integer,
	'sub_exp_code': global_type_integer,
	'plot_pos': global_type_integer,
 }


#BeamSelector
parameters = { 
	'beam': global_type_string,
 }


#CohInt
parameters = { 
	'n': global_type_integer, 
	'timeInterval': global_type_float, 
	'overlapping': global_type_boolean, 
	'byblock': global_type_boolean
}


#CoherenceMap
parameters = { 
	'id': global_type_string,
	'wintitle': global_type_string,
	'pairsList': global_type_pairsList,
	'showprofile': global_type_boolean,
	'xmin': global_type_float,
	'xmax': global_type_float,
	'ymin': global_type_float,
	'ymax': global_type_float,
	'zmin': global_type_float,
	'zmax': global_type_float,
	'timerange': global_type_float,
	'phase_min': global_type_float,
	'phase_max': global_type_float,
	'save': global_type_boolean,
	'figpath': global_type_string,
	'figfile': global_type_string,
	'ftp': global_type_boolean,
	'wr_period': global_type_integer,
	'coherence_cmap': global_type_colormap,
	'phase_cmap': global_type_colormap,
	'show': global_type_boolean,
	'server': global_type_string,
	'folder': global_type_string,
	'username': global_type_string,
	'password': global_type_string,
	'ftp_wei': global_type_integer,
	'exp_code': global_type_integer,
	'sub_exp_code': global_type_integer,
	'plot_pos': global_type_integer,
 }


#CombineProfiles
parameters = { 
	'n': global_type_integer,
}


#CorrectSMPhases
parameters = { 
	'phaseOffsets': global_type_pairsList,
	'hmin': global_type_float,
	'hmax': global_type_float,
	'azimuth': global_type_float,
	'channelPositions': global_type_pairsList,
}


#CorrelationPlot
parameters = { 
	'id': global_type_string,
	'wintitle': global_type_string,
	'channelList': global_type_list,
	'showprofile': global_type_boolean,
	'xmin': global_type_float,
	'xmax': global_type_float,
	'ymin': global_type_float,
	'ymax': global_type_float,
	'zmin': global_type_float,
	'zmax': global_type_float,
	'save': global_type_boolean,
	'figpath': global_type_string,
	'figfile': global_type_string,
	'show': global_type_boolean,
	'ftp': global_type_boolean,
	'wr_period': global_type_integer,
	'server': global_type_string,
	'folder': global_type_string,
	'username': global_type_string,
	'password': global_type_string,
	'ftp_wei': global_type_integer,
	'exp_code': global_type_integer,
	'sub_exp_code': global_type_integer,
	'plot_pos': global_type_integer,
	'realtime': global_type_boolean,
 }


#CrossSpectraPlot
parameters = { 
	'id': global_type_string,
	'wintitle': global_type_string,
	'pairsList': global_type_pairsList,
	'xmin': global_type_float,
	'xmax': global_type_float,
	'ymin': global_type_float,
	'ymax': global_type_float,
	'zmin': global_type_float,
	'zmax': global_type_float,
	'coh_min': global_type_float,
	'coh_max': global_type_float,
	'phase_min': global_type_float,
	'phase_max': global_type_float,
	'save': global_type_boolean,
	'figpath': global_type_string,
	'figfile': global_type_string,
	'ftp': global_type_boolean,
	'wr_period': global_type_integer,
	'power_cmap': global_type_colormap,
	'coherence_cmap': global_type_colormap,
	'phase_cmap': global_type_colormap,
	'show': global_type_boolean,
	'server': global_type_string,
	'folder': global_type_string,
	'username': global_type_string,
	'password': global_type_string,
	'ftp_wei': global_type_integer,
	'exp_code': global_type_integer,
	'sub_exp_code': global_type_integer,
	'plot_pos': global_type_integer,
	'xaxis': global_type_string,
 }


#Decoder
parameters = { 
	'code': global_type_list,
	'nCode': global_type_integer,
	'nBaud': global_type_integer,
	'mode': global_type_integer,
	'osamp': global_type_float,
 }


#EWDriftsEstimation
parameters = { 
	'zenith': global_type_list,
	'zenithCorrection': global_type_float,
 }


#EWDriftsPlot
parameters = { 
	'id': global_type_string,
	'wintitle': global_type_string,
	'channelList': global_type_list,
	'xmin': global_type_float,
	'xmax': global_type_float,
	'ymin': global_type_float,
	'ymax': global_type_float,
	'zmin': global_type_float,
	'zmax': global_type_float,
	'zmaxVertfloat': global_type_float,
	'zminVertfloat': global_type_float,
	'zmaxZonafloat': global_type_float,
	'zminZonafloat': global_type_float,
	'timerange': global_type_float,
	'SNRthresh': global_type_float,
	'SNRmin': global_type_float,
	'SNRmax': global_type_float,
	'SNR_1': global_type_boolean,
	'save': global_type_boolean,
	'figpath': global_type_string,
	'lastone': global_type_float,
	'figfile': global_type_string,
	'ftp': global_type_string,
	'wr_period': global_type_integer,
	'show': global_type_string,
	'server': global_type_string,
	'folder': global_type_string,
	'username': global_type_string,
	'password': global_type_string,
	'ftp_wei': global_type_integer,
	'exp_code': global_type_integer,
	'sub_exp_code': global_type_integer,
	'plot_pos': global_type_integer,
 }


Figure
# parameters = { 
# : global_type_string,
#  }


#FitsWriter
parameters = { 
	'path': global_type_string, 
	'dataBlocksPerFile': global_type_integer, 
	'metadatafile': global_type_string,
}


#IncohInt
parameters = { 
	'n': global_type_float,
	'timeInterval': global_type_integer,
	'overlapping': global_type_boolean,
 }


#IncohInt4SpectraHeis
parameters = { 
	'n': global_type_float,
	'timeInterval': global_type_integer,
	'overlapping': global_type_boolean,
 }


#MomentsPlot
parameters = { 
	'id': global_type_string,
	'wintitle': global_type_string,
	'channelList': global_type_list,
	'showprofile': global_type_boolean,
	'xmin': global_type_float,
	'xmax': global_type_float,
	'ymin': global_type_float,
	'ymax': global_type_float,
	'zmin': global_type_float,
	'zmax': global_type_float,
	'save': global_type_boolean,
	'figpath': global_type_string,
	'figfile': global_type_string,
	'show': global_type_boolean,
	'ftp': global_type_boolean,
	'wr_period': global_type_integer,
	'server': global_type_string,
	'folder': global_type_string,
	'username': global_type_string,
	'password': global_type_string,
	'ftp_wei': global_type_string,
	'exp_code': global_type_integer,
	'sub_exp_code': global_type_integer,
	'plot_pos': global_type_integer,
	'realtime': global_type_boolean,
 }


#NSMeteorDetection1Plot
parameters = { 
	'id': global_type_string,
	'wintitle': global_type_string,
	'channelList': global_type_list,
	'showprofile': global_type_boolean,
	'xmin': global_type_float,
	'xmax': global_type_float,
	'ymin': global_type_float,
	'ymax': global_type_float,
	'SNRmin': global_type_float,
	'SNRmax': global_type_float,
	'vmin': global_type_float,
	'vmax': global_type_float,
	'wmin': global_type_float,
	'wmax': global_type_float,
	'mode': global_type_string,
	'save': global_type_boolean,
	'figpath': global_type_string,
	'figfile': global_type_string,
	'show': global_type_boolean,
	'ftp': global_type_string,
	'wr_period': global_type_integer,
	'server': global_type_string,
	'folder': global_type_string,
	'username': global_type_string,
	'password': global_type_string,
	'ftp_wei': global_type_integer,
	'exp_code': global_type_integer,
	'sub_exp_code': global_type_integer,
	'plot_pos': global_type_integer,
	'realtime': global_type_boolean,
	'xaxis': global_type_string,
 }


#NSMeteorDetection2Plot
parameters = { 
	'id': global_type_string,
	'wintitle': global_type_string,
	'channelList': global_type_list,
	'showprofile': global_type_boolean,
	'xmin': global_type_float,
	'xmax': global_type_float,
	'ymin': global_type_float,
	'ymax': global_type_float,
	'SNRmin': global_type_float,
	'SNRmax': global_type_float,
	'vmin': global_type_float,
	'vmax': global_type_float,
	'wmin': global_type_float,
	'wmax': global_type_float,
	'mode': global_type_string,
	'save': global_type_boolean,
	'figpath': global_type_string,
	'figfile': global_type_string,
	'show': global_type_string,
	'ftp': global_type_boolean,
	'wr_period': global_type_integer,
	'server': global_type_string,
	'folder': global_type_string,
	'username': global_type_string,
	'password': global_type_string,
	'ftp_wei': global_type_integer,
	'exp_code': global_type_integer,
	'sub_exp_code': global_type_integer,
	'plot_pos': global_type_integer,
	'realtime': global_type_boolean,
	'xaxis': global_type_string,
 }


#Noise
parameters = { 
	'id': global_type_string,
	'wintitle': global_type_string,
	'channelList': global_type_list,
	'showprofile': global_type_boolean,
	'xmin': global_type_float,
	'xmax': global_type_float,
	'ymin': global_type_float,
	'ymax': global_type_float,
	'timerange': global_type_float,
	'save': global_type_boolean,
	'figpath': global_type_string,
	'figfile': global_type_string,
	'show': global_type_boolean,
	'ftp': global_type_boolean,
	'wr_period': global_type_integer,
	'server': global_type_string,
	'folder': global_type_string,
	'username': global_type_string,
	'password': global_type_string,
	'ftp_wei': global_type_integer,
	'exp_code': global_type_integer,
	'sub_exp_code': global_type_integer,
	'plot_pos': global_type_integer,
 }


#NonSpecularMeteorDetection
parameters = { 
	'mode': global_type_string,
	'SNRthresh': global_type_float,
	'phaseDerThresh': global_type_float,
	'cohThresh': global_type_float,
	'allData': global_type_boolean,
 }


Operation
parameters = { 
	'dataIn': global_type_string,
 }


#ParamWriter
parameters = { 
	'path': global_type_string,
	'blocksPerFile':global_type_integer, 
	'metadataList': global_type_list, 
	'dataList': global_type_list,  
	'mode': global_type_integer,
}


#Parameters1Plot
parameters = { 
	'id': global_type_string,
	'wintitle': global_type_string,
	'channelList': global_type_list,
	'showprofile': global_type_boolean,
	'xmin': global_type_float,
	'xmax': global_type_float,
	'ymin': global_type_float,
	'ymax': global_type_float,
	'zmin': global_type_float,
	'zmax': global_type_float,
	'timerange': global_type_float,
	'parameterIndex': global_type_float,
	'onlyPositive': global_type_boolean,
	'SNRthresh': global_type_float,
	'SNR': global_type_boolean,
	'SNRmin': global_type_float,
	'SNRmax': global_type_float,
	'onlySNR': global_type_boolean,
	'DOP': global_type_boolean,
	'zlabel': global_type_string,
	'parameterName': global_type_string,
	'parameterObject': global_type_string,
	'save': global_type_boolean,
	'figpath': global_type_string,
	'lastone': global_type_integer,
	'figfile': global_type_string,
	'ftp': global_type_boolean,
	'wr_period': global_type_integer,
	'show': global_type_string,
	'server': global_type_string,
	'folder': global_type_string,
	'username': global_type_string,
	'password': global_type_string,
	'ftp_wei': global_type_integer,
	'exp_code': global_type_integer,
	'sub_exp_code': global_type_integer,
	'plot_pos': global_type_integer,
 }


#ParametersPlot
parameters = { 
	'id': global_type_string,
	'wintitle': global_type_string,
	'channelList': global_type_list,
	'paramIndex': global_type_integer,
	'colormap': global_type_colormap,
	'xmin': global_type_float,
	'xmax': global_type_float,
	'ymin': global_type_float,
	'ymax': global_type_float,
	'zmin': global_type_float,
	'zmax': global_type_float,
	'timerange': global_type_float,
	'showSNR': global_type_boolean,
	'SNRthresh': global_type_float,
	'SNRmin': global_type_float,
	'SNRmax': global_type_float,
	'save': global_type_boolean,
	'figpath': global_type_string,
	'lastone': global_type_integer,
	'figfile': global_type_string,
	'ftp': global_type_boolean,
	'wr_period': global_type_integer,
	'show': global_type_boolean,
	'server': global_type_string,
	'folder': global_type_string,
	'username': global_type_string,
	'password': global_type_string,
	'ftp_wei': global_type_integer,
	'exp_code': global_type_integer,
	'sub_exp_code': global_type_integer,
	'plot_pos': global_type_integer,
 }


#PhasePlot
parameters = { 
	'id': global_type_string,
	'wintitle': global_type_string,
	'pairsList': global_type_pairsList,
	'showprofile': global_type_boolean,
	'xmin': global_type_float,
	'xmax': global_type_float,
	'ymin': global_type_float,
	'ymax': global_type_float,
	'timerange': global_type_float,
	'save': global_type_boolean,
	'figpath': global_type_string,
	'figfile': global_type_string,
	'show': global_type_boolean,
	'ftp': global_type_boolean,
	'wr_period': global_type_integer,
	'server': global_type_string,
	'folder': global_type_string,
	'username': global_type_string,
	'password': global_type_string,
	'ftp_wei': global_type_integer,
	'exp_code': global_type_integer,
	'sub_exp_code': global_type_integer,
	'plot_pos': global_type_integer,
 }


PlotCOHData
parameters = { 
: global_type_string,
 }


PlotCrossSpectraData
parameters = { 
: global_type_string,
 }


PlotDOPData
parameters = { 
: global_type_string,
 }


PlotData
parameters = { 
: global_type_string,
 }


PlotNoiseData
parameters = { 
: global_type_string,
 }


PlotPHASEData
parameters = { 
: global_type_string,
 }


PlotRTIData
parameters = { 
: global_type_string,
 }


PlotSNRData
parameters = { 
: global_type_string,
 }


PlotSpectraData
parameters = { 
: global_type_string,
 }


PlotSpectraMeanData
parameters = { 
: global_type_string,
 }


PlotWindProfilerData
parameters = { 
: global_type_string,
 }


PowerProfilePlot
parameters = { 
	'id': global_type_string,
	'wintitle': global_type_string,
	'channelList': global_type_list,
	'xmin': global_type_float,
	'xmax': global_type_float,
	'ymin': global_type_float,
	'ymax': global_type_float,
	'save': global_type_boolean,
	'figpath': global_type_string,
	'figfile': global_type_string,
	'show': global_type_boolean,
	'ftp': global_type_boolean,
	'wr_period': global_type_integer,
	'server': global_type_string,
	'folder': global_type_string,
	'username': global_type_string,
	'password': global_type_string,
 }


PrintInfo
parameters = { 
: global_type_string,
 }


ProfileConcat
parameters = { 
	'm': global_type_string,
 }


ProfileSelector
parameters = { 
	'profileList': global_type_string,
	'profileRangeList': global_type_string,
	'beam': global_type_string,
	'byblock': global_type_string,
	'rangeList': global_type_string,
	'nProfiles': global_type_string,
 }


ProfileToChannels
parameters = { 
: global_type_string,
 }


PublishData
parameters = { 
: global_type_string,
 }


RTIPlot
parameters = { 
	'id': global_type_string,
	'wintitle': global_type_string,
	'channelList': global_type_list,
	'showprofile': global_type_boolean,
	'xmin': global_type_float,
	'xmax': global_type_float,
	'ymin': global_type_float,
	'ymax': global_type_float,
	'zmin': global_type_float,
	'zmax': global_type_float,
	'timerange': global_type_float,
	'save': global_type_boolean,
	'figpath': global_type_string,
	'lastone': global_type_string,
	'figfile': global_type_string,
	'ftp': global_type_boolean,
	'wr_period': global_type_integer,
	'show': global_type_boolean,
	'server': global_type_string,
	'folder': global_type_string,
	'username': global_type_string,
	'password': global_type_string,
	'ftp_wei': global_type_integer,
	'exp_code': global_type_integer,
	'sub_exp_code': global_type_integer,
	'plot_pos': global_type_integer,
 }


RTIfromSpectraHeis
parameters = { 
	'id': global_type_string,
	'wintitle': global_type_string,
	'channelList': global_type_list,
	'showprofile': global_type_boolean,
	'xmin': global_type_float,
	'xmax': global_type_float,
	'ymin': global_type_float,
	'ymax': global_type_float,
	'timerange': global_type_float,
	'save': global_type_boolean,
	'figpath': global_type_string,
	'figfile': global_type_string,
	'ftp': global_type_boolean,
	'wr_period': global_type_integer,
	'show': global_type_boolean,
	'server': global_type_string,
	'folder': global_type_string,
	'username': global_type_string,
	'password': global_type_string,
	'ftp_wei': global_type_integer,
	'exp_code': global_type_integer,
	'sub_exp_code': global_type_integer,
	'plot_pos': global_type_integer,
 }


Reshaper
parameters = { 
	'shape': global_type_string,
	'nTxs': global_type_string,
 }


SALags
parameters = { 
: global_type_string,
 }


SMDetection
parameters = { 
	'hei_ref': global_type_string,
	'tauindex': global_type_string,
	'phaseOffsets': global_type_string,
	'cohDetection': global_type_string,
	'cohDet_timeStep': global_type_string,
	'cohDet_thresh': global_type_string,
	'noise_timeStep': global_type_string,
	'noise_multiple': global_type_string,
	'multDet_timeLimit': global_type_string,
	'multDet_rangeLimit': global_type_string,
	'phaseThresh': global_type_string,
	'SNRThresh': global_type_string,
	'hmin': global_type_string,
	'hmax': global_type_string,
	'azimuth': global_type_string,
	'channelPositions': global_type_string,
 }


SMPhaseCalibration
parameters = { 
	'hmin': global_type_string,
	'hmax': global_type_string,
	'channelPositions': global_type_string,
	'nHours': global_type_string,
 }


Scope
parameters = { 
	'id': global_type_string,
	'wintitle': global_type_string,
	'channelList': global_type_list,
	'xmin': global_type_float,
	'xmax': global_type_float,
	'ymin': global_type_float,
	'ymax': global_type_float,
	'save': global_type_boolean,
	'figpath': global_type_string,
	'figfile': global_type_string,
	'show': global_type_boolean,
	'wr_period': global_type_integer,
	'ftp': global_type_boolean,
	'server': global_type_string,
	'folder': global_type_string,
	'username': global_type_string,
	'password': global_type_string,
	'type': global_type_string,
 }


SendByFTP
parameters = { 
	'ext': global_type_string,
	'localfolder': global_type_string,
	'remotefolder': global_type_string,
	'server': global_type_string,
	'username': global_type_string,
	'password': global_type_string,
	'period': global_type_string,
 }


SkyMapPlot
parameters = { 
	'id': global_type_string,
	'wintitle': global_type_string,
	'channelList': global_type_list,
	'showprofile': global_type_boolean,
	'tmin': global_type_string,
	'tmax': global_type_string,
	'timerange': global_type_float,
	'save': global_type_boolean,
	'figpath': global_type_string,
	'figfile': global_type_string,
	'show': global_type_boolean,
	'ftp': global_type_boolean,
	'wr_period': global_type_integer,
	'server': global_type_string,
	'folder': global_type_string,
	'username': global_type_string,
	'password': global_type_string,
	'ftp_wei': global_type_integer,
	'exp_code': global_type_integer,
	'sub_exp_code': global_type_integer,
	'plot_pos': global_type_integer,
	'realtime': global_type_boolean,
 }


SpectraCutPlot
parameters = { 
	'id': global_type_string,
	'wintitle': global_type_string,
	'channelList': global_type_list,
	'xmin': global_type_float,
	'xmax': global_type_float,
	'ymin': global_type_float,
	'ymax': global_type_float,
	'save': global_type_boolean,
	'figpath': global_type_string,
	'figfile': global_type_string,
	'show': global_type_boolean,
	'ftp': global_type_boolean,
	'wr_period': global_type_integer,
	'server': global_type_string,
	'folder': global_type_string,
	'username': global_type_string,
	'password': global_type_string,
	'xaxis': global_type_string,
 }


SpectraHeisScope
parameters = { 
	'id': global_type_string,
	'wintitle': global_type_string,
	'channelList': global_type_list,
	'xmin': global_type_float,
	'xmax': global_type_float,
	'ymin': global_type_float,
	'ymax': global_type_float,
	'save': global_type_boolean,
	'figpath': global_type_string,
	'figfile': global_type_string,
	'ftp': global_type_boolean,
	'wr_period': global_type_integer,
	'show': global_type_boolean,
	'server': global_type_string,
	'folder': global_type_string,
	'username': global_type_string,
	'password': global_type_string,
	'ftp_wei': global_type_integer,
	'exp_code': global_type_integer,
	'sub_exp_code': global_type_integer,
	'plot_pos': global_type_integer,
 }


SpectraHeisWriter
parameters = { 
: global_type_string,
 }


SpectraPlot
parameters = { 
	'id': global_type_string,
	'wintitle': global_type_string,
	'channelList': global_type_list,
	'showprofile': global_type_boolean,
	'xmin': global_type_float,
	'xmax': global_type_float,
	'ymin': global_type_float,
	'ymax': global_type_float,
	'zmin': global_type_float,
	'zmax': global_type_float,
	'save': global_type_boolean,
	'figpath': global_type_string,
	'figfile': global_type_string,
	'show': global_type_boolean,
	'ftp': global_type_boolean,
	'wr_period': global_type_integer,
	'server': global_type_string,
	'folder': global_type_string,
	'username': global_type_string,
	'password': global_type_string,
	'ftp_wei': global_type_integer,
	'exp_code': global_type_integer,
	'sub_exp_code': global_type_integer,
	'plot_pos': global_type_integer,
	'realtime': global_type_boolean,
	'xaxis': global_type_string,
 }


SpectraWriter
parameters = { 
	'path': global_type_string,
	'blocksPerFile': global_type_string,
	'profilesPerBlock': global_type_string,
	'set': global_type_string,
	'ext': global_type_string,
	'datatype': global_type_string,
 }


SpectralFitting
parameters = { 
	'getSNR': global_type_string,
	'path': global_type_string,
	'file': global_type_string,
	'groupList': global_type_string,
 }


SpectralFittingPlot
parameters = { 
	'id': global_type_string,
	'cutHeight': global_type_string,
	'fit': global_type_string,
	'wintitle': global_type_string,
	'channelList': global_type_list,
	'showprofile': global_type_boolean,
	'xmin': global_type_float,
	'xmax': global_type_float,
	'ymin': global_type_float,
	'ymax': global_type_float,
	'save': global_type_boolean,
	'figpath': global_type_string,
	'figfile': global_type_string,
	'show': global_type_boolean,
 }


SpectralMoments
parameters = { 
: global_type_string,
 }


SplitProfiles
parameters = { 
	'n': global_type_string,
 }


USRPWriter
parameters = { 
	'dataIn': global_type_string,
 }


VoltageWriter
parameters = { 
	'path': global_type_string,
	'blocksPerFile': global_type_string,
	'profilesPerBlock': global_type_string,
	'set': global_type_string,
	'ext': global_type_string,
	'datatype': global_type_string,
 }


WindProfiler
parameters = { 
	'technique': global_type_string,
 }


WindProfilerPlot
parameters = { 
	'id': global_type_string,
	'wintitle': global_type_string,
	'channelList': global_type_list,
	'showprofile': global_type_boolean,
	'xmin': global_type_float,
	'xmax': global_type_float,
	'ymin': global_type_float,
	'ymax': global_type_float,
	'zmin': global_type_float,
	'zmax': global_type_float,
	'zmax_ver': global_type_string,
	'zmin_ver': global_type_string,
	'SNRmin': global_type_float,
	'SNRmax': global_type_float,
	'timerange': global_type_float,
	'SNRthresh': global_type_string,
	'save': global_type_boolean,
	'figpath': global_type_string,
	'lastone': global_type_string,
	'figfile': global_type_string,
	'ftp': global_type_boolean,
	'wr_period': global_type_integer,
	'show': global_type_boolean,
	'server': global_type_string,
	'folder': global_type_string,
	'username': global_type_string,
	'password': global_type_string,
	'ftp_wei': global_type_integer,
	'exp_code': global_type_integer,
	'sub_exp_code': global_type_integer,
	'plot_pos': global_type_integer,
 }


Writer
parameters = { 
	'dataIn': global_type_string,
 }


AMISRProc
parameters = { 
: global_type_string,
 }


AMISRReader
parameters = { 
: global_type_string,
 }


CorrelationProc
parameters = { 
	'lags': global_type_string,
	'mode': global_type_string,
	'pairsList': 'pairsLists',
	'fullBuffer': global_type_string,
	'nAvg': global_type_string,
	'removeDC': global_type_string,
	'splitCF': global_type_string,
 }


FitsReader
parameters = { 
: global_type_string,
 }


HFReader
parameters = { 
: global_type_string,
 }


ParamReader
parameters = { 
: global_type_string,
 }


ParametersProc
parameters = { 
: global_type_string,
 }


ProcessingUnit
parameters = { 
: global_type_string,
 }


ReceiverData
parameters = { 
: global_type_string,
 }


SendToServer
parameters = { 
: global_type_string,
 }


SpectraAFCProc
parameters = { 
	'nProfiles': global_type_string,
	'nFFTPoints': global_type_string,
	'pairsList': 'pairsLists',
	'code': global_type_string,
	'nCode': global_type_string,
	'nBaud': global_type_string,
 }


SpectraHeisProc
parameters = { 
: global_type_string,
 }


SpectraLagsProc
parameters = { 
	'nProfiles': global_type_string,
	'nFFTPoints': global_type_string,
	'pairsList': 'pairsLists',
	'code': global_type_string,
	'nCode': global_type_string,
	'nBaud': global_type_string,
	'codeFromHeader': global_type_string,
	'pulseIndex': global_type_string,
 }


SpectraProc
parameters = { 
	'nProfiles': global_type_string,
	'nFFTPoints': global_type_string,
	'pairsList': 'pairsLists',
	'ippFactor': global_type_string,
 }


SpectraReader
parameters = { 
	'path': global_type_string,
	'startDate': global_type_string,
	'endDate': global_type_string,
	'startTime': global_type_string,
	'endTime': global_type_string,
	'set': global_type_string,
	'expLabel': global_type_string,
	'ext': global_type_string,
	'online': global_type_string,
	'delay': global_type_string,
	'walk': global_type_string,
	'getblock': global_type_string,
	'nTxs': global_type_string,
	'realtime': global_type_boolean,
	'blocksize': global_type_string,
	'blocktime': global_type_string,
	'queue': global_type_string,
	'skip': global_type_string,
	'cursor': global_type_string,
	'warnings': global_type_string,
	'verbose': global_type_string,
 }


USRPReader
parameters = { 
: global_type_string,
 }


VoltageProc
parameters = { 
: global_type_string,
 }


VoltageReader
parameters = { 
	'path': global_type_string,
	'startDate': global_type_string,
	'endDate': global_type_string,
	'startTime': global_type_string,
	'endTime': global_type_string,
	'set': global_type_string,
	'expLabel': global_type_string,
	'ext': global_type_string,
	'online': global_type_string,
	'delay': global_type_string,
	'walk': global_type_string,
	'getblock': global_type_string,
	'nTxs': global_type_string,
	'realtime': global_type_boolean,
	'blocksize': global_type_string,
	'blocktime': global_type_string,
	'queue': global_type_string,
	'skip': global_type_string,
	'cursor': global_type_string,
	'warnings': global_type_string,
	'verbose': global_type_string,
 }


