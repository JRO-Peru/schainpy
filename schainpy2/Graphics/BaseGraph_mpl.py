'''
Created on Feb 7, 2012

@autor $Author$
@version $Id$

'''

import numpy

import time
import datetime


import matplotlib as mpl
mpl.use('TKAgg')
import matplotlib.pyplot as plt

import scitools.numpyutils as sn

def cmap1_init(colormap='gray'):
	pass

def setColormap(colormap='jet'):
	pass

def savePlplot(filename,width,height):
	pass

def initMatplotlib(indexFig,ncol,nrow,winTitle,width,height):

	plt.ioff()
	fig = plt.figure(indexFig)
	fig.canvas.manager.set_window_title(winTitle)
	fig.canvas.manager.resize(width,height)
#	fig.add_subplot(nrow,ncol,1)
	plt.ion()

def setNewPage():
	plt.clf()

def closePage():
	pass
	
def clearData(objGraph):
	objGraph.plotBox(objGraph.xrange[0], objGraph.xrange[1], objGraph.yrange[0], objGraph.yrange[1], 'bc', 'bc')
	
	objGraph.setColor(15) #Setting Line Color to White
	
	if objGraph.datatype == 'complex':		
		objGraph.basicXYPlot(objGraph.xdata,objGraph.ydata.real)
		objGraph.basicXYPlot(objGraph.xdata,objGraph.ydata.imag)

	if objGraph.datatype == 'real':
		objGraph.basicXYPlot(objGraph.xdata,objGraph.ydata)
	
	objGraph.setColor(1) 

def setFigure(indexFig):
	plt.figure(indexFig)

def refresh():
	plt.draw()

def show():
	plt.ioff()
	plt.show()
	plt.ion()
	
def setPlTitle(pltitle,color, szchar=0.7):
	pass
	
def setSubpages(ncol,nrow):
	pass

class BaseGraph:
	
	__name = None
	__xpos = None
	__ypos = None
	__subplot = None
	__xg = None
	__yg = None
	__axesId = None
	xdata = None
	ydata = None
	getGrid = True
	xaxisIsTime = False
	deltax = None
	xmin = None
	xmax = None
	
	def __init__(self,name,subplot,xpos,ypos,xlabel,ylabel,title,szchar,xrange,yrange,zrange=None,deltax=1.0):
		
		self.setName(name)
		self.setScreenPos(xpos, ypos)
		self.setSubPlot(subplot)
		self.setXYZrange(xrange,yrange,zrange)
		self.setSizeOfChar(szchar)
		self.setLabels(xlabel,ylabel,title)
		self.getGrid = True
		self.xaxisIsTime = False
		self.deltax = deltax
		pass
	
	def makeAxes(self,indexFig,nrow,ncol,subplot):
		fig = plt.figure(indexFig)
		self.__axesId = fig.add_subplot(nrow,ncol,subplot)

	def setParentAxesId(self,parent):
		self.__axesId = parent.__axesId

	def setName(self, name):
		self.__name = name

	def setScreenPos(self,xpos,ypos):
		self.__xpos = xpos
		self.__ypos = ypos
	
	def setSubPlot(self,subplot):
		self.__subplot = subplot
	
	def setXYZrange(self,xrange,yrange,zrange):
		self.xrange = xrange
		self.yrange = yrange
		self.zrange = zrange

	def setSizeOfChar(self,szchar):
		self.__szchar = szchar

	def setLabels(self,xlabel=None,ylabel=None,title=None):
		if xlabel != None: self.xlabel = xlabel
		if ylabel != None: self.ylabel = ylabel
		if title != None: self.title = title
			
	def setXYData(self,xdata=None,ydata=None,datatype='real'):
		if ((xdata != None) and (ydata != None)):
			self.xdata = xdata
			self.ydata = ydata
			self.datatype = datatype
		if ((self.xdata == None) and (self.ydata == None)):
			return None
		return 1
	
	def setLineStyle(self, style):
		pass
	
	def setColor(self, color):
		pass
	
	def setXAxisAsTime(self, value=False):
		self.xaxisIsTime = value
	
	def basicLineTimePlot(self, x, y, colline=1):
		ax = self.__axesId
		if self.setXYData() == None:
			ax.plot(x,y)
			plt.tight_layout()
		else:
			ax.lines[0].set_data(x,y)
	
	def basicXYPlot(self, x, y):
		ax = self.__axesId
		if self.setXYData() == None:
			ax.plot(x,y)
		else:
			ax.lines[0].set_data(x,y)
	
	def basicPcolorPlot(self, data, x, y, xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None):
		pass
	
	def __getBoxpltr(self, x, y, deltax=None, deltay=None):		
		pass
	
	def advPcolorPlot(self, data, x, y, xmin=None, xmax=None, ymin=None, ymax=None, zmin=0., zmax=0., deltax=1.0, deltay=None, getGrid = True):
		ax = self.__axesId
		ax.pcolormesh(x,y,data.T,vmin=zmin,vmax=zmax)

	def colorbarPlot(self, xmin=0., xmax=1., ymin=0., ymax=1.):
		ax = self.__axesId
		cax, kw = mpl.colorbar.make_axes(ax)
		norm = mpl.colors.Normalize(vmin=ymin, vmax=ymax)
		cb = mpl.colorbar.ColorbarBase(cax,norm=norm,**kw)
		self.__colorbarId = cb
		cb.set_label(self.title)
		
	def plotBox(self, xmin, xmax, ymin, ymax, xopt, yopt, nolabels=False):
		ax = self.__axesId
		ax.set_xlim([xmin,xmax])
		ax.set_ylim([ymin,ymax])
		
		if not(nolabels):
			ax.set_xlabel(self.xlabel)
			ax.set_ylabel(self.ylabel)
			ax.set_title(self.title)
			
	def delLabels(self):
		pass
	
	def plotImage(self,x,y,z,xrange,yrange,zrange):
		pass


class LinearPlot():
	linearObjDic = {}
	__xpos = None
	__ypos = None
	isPlotIni = None
	
	def __init__(self, indexFig,nsubplot,winTitle):
		self.width = 700
		self.height = 150
		self.indexFig = indexFig
		self.ncol = 1
		self.nrow = nsubplot
		initMatplotlib(indexFig,self.ncol,self.nrow,winTitle,self.width,self.height)
		
		self.isPlotIni = False
		
		
	def setFigure(self,indexFig):
		setFigure(indexFig)
	
	def setNewPage(self, pltitle='No title'):
		szchar = 0.7
#		setNewPage()
		setPlTitle(pltitle,'black', szchar=szchar)
		setSubpages(self.ncol, self.nrow)
	
	def setPosition(self): 
		xi = 0.07; xf = 0.9 
		yi = 0.15; yf = 0.8
		
		xpos = [xi,xf]
		ypos = [yi,yf]
		
		self.__xpos = xpos
		self.__ypos = ypos
		
		return xpos,ypos
	
	def createObjects(self,subplot,xmin,xmax,ymin,ymax,title,xlabel,ylabel):
		szchar = 0.7
		name = 'linear'
		key = name + '%d'%subplot
		xrange = [xmin,xmax]
		yrange = [ymin,ymax]
		
		xpos,ypos = self.setPosition()
		linearObj = BaseGraph(name,subplot,xpos,ypos,xlabel,ylabel,title,szchar,xrange,yrange)
		self.linearObjDic[key] = linearObj
	
	def iniPlot(self,subplot):
		name = 'linear'
		key = name + '%d'%subplot
		
		linearObj = self.linearObjDic[key]
		linearObj.makeAxes(self.indexFig,self.nrow,self.ncol,subplot)
		linearObj.plotBox(linearObj.xrange[0], linearObj.xrange[1], linearObj.yrange[0], linearObj.yrange[1], 'bcnst', 'bcnstv')
		
	
	def plot(self,subplot,x,y,type='abs'):
		name = 'linear'
		key = name + '%d'%subplot
		
		linearObj = self.linearObjDic[key]
		
		if type.lower() == 'simple':
			colline = 9
			linearObj.basicLineTimePlot(x, y)
			linearObj.setXYData(x,y,'real')
		
	def refresh(self):
		refresh()
	
	def show(self):
		show()
		
class PcolorPlot:
	
	pcolorObjDic = {}
	colorbarObjDic = {}
	pwprofileObjDic = {}
	showColorbar = None
	showPowerProfile = None
	XAxisAsTime = None
	width = None
	height = None
	__spcxpos = None
	__spcypos = None
	__cmapxpos = None
	__cmapypos = None
	__profxpos = None
	__profypos = None
	__lastTitle = None
	
	def __init__(self,indexFig,nsubplot,winTitle,colormap,showColorbar,showPowerProfile,XAxisAsTime):

		self.width = 460
		self.height = 300
		self.showColorbar = showColorbar
		self.showPowerProfile = showPowerProfile
		self.XAxisAsTime = XAxisAsTime
		
		ncol = int(numpy.sqrt(nsubplot)+0.9)
		nrow = int(nsubplot*1./ncol + 0.9)
		
		self.ncol = ncol
		self.nrow = nrow
		self.indexFig = indexFig
	
		initMatplotlib(indexFig,ncol,nrow,winTitle,self.width,self.height)
		setColormap(colormap)

	def setFigure(self,indexFig):
		setFigure(indexFig)

	def setSpectraPos(self): #modificar valores de acuerdo al colorbar y pwprofile
		if self.showPowerProfile: xi = 0.09; xf = 0.6 #0.075
		else:   xi = 0.15; xf = 0.8 #0.8,0.7,0.5 
		yi = 0.15; yf = 0.80
		
		xpos = [xi,xf]
		ypos = [yi,yf]
		
		self.__spcxpos = xpos
		self.__spcypos = ypos
		
		return xpos,ypos
	
	def setColorbarScreenPos(self):
						
		xi = self.__spcxpos[1] + 0.03; xf = xi + 0.03
		yi = self.__spcypos[0]; yf = self.__spcypos[1]
		
		xpos = [xi,xf]
		ypos = [yi,yf]
		
		self.__cmapxpos = xpos
		self.__cmapypos = ypos

		return xpos,ypos
	
	def setPowerprofileScreenPos(self):
		
		xi = self.__cmapxpos[1] + 0.07; xf = xi + 0.25
		yi = self.__spcypos[0]; yf = self.__spcypos[1]
		
		xpos = [xi,xf]
		ypos = [yi,yf]
		
		self.__profxpos = [xi,xf]
		self.__profypos = [yi,yf]

		return xpos,ypos
	
	def createObjects(self,subplot,xmin,xmax,ymin,ymax,zmin,zmax,title,xlabel,ylabel):

		'''
		Crea los objetos necesarios para un subplot
		'''
		
		# Config Spectra plot
		
		szchar = 0.7
		name = 'spc'
		key = name + '%d'%subplot
		xrange = [xmin,xmax]
		yrange = [ymin,ymax]
		zrange = [zmin,zmax]
		
		xpos,ypos = self.setSpectraPos()
		pcolorObj = BaseGraph(name,subplot,xpos,ypos,xlabel,ylabel,title,szchar,xrange,yrange,zrange)
		#pcolorObj.makeAxes(self.indexFig,self.nrow,self.ncol,subplot)
		self.pcolorObjDic[key] = pcolorObj
		
		# Config Colorbar
		if self.showColorbar:
			szchar = 0.65
			name = 'colorbar'
			key = name + '%d'%subplot
			
			xpos,ypos = self.setColorbarScreenPos()
			xrange = [0.,1.]
			yrange = [zmin,zmax]
			cmapObj = BaseGraph(name,subplot,xpos,ypos,'','','dB',szchar,xrange,yrange)
			self.colorbarObjDic[key] = cmapObj
		
		# Config Power profile
		if self.showPowerProfile:
			szchar = 0.55
			name = 'pwprofile'
			key = name + '%d'%subplot
			
			xpos,ypos = self.setPowerprofileScreenPos()
			xrange = [zmin,zmax]
			yrange = [ymin,ymax]
			powObj = BaseGraph(name,subplot,xpos,ypos,'dB','','Power Profile',szchar,xrange,yrange)
			#powObj.makeAxes(self.indexFig,self.nrow,self.ncol,subplot)
			self.pwprofileObjDic[key] = powObj
	
	def setNewPage(self, pltitle='No title'):
		szchar = 0.7
		setNewPage()
		setPlTitle(pltitle,'black', szchar=szchar)
		setSubpages(self.ncol, self.nrow)
		
	def closePage(self):
		closePage()
		
	def show(self):
		show()
		
	def iniPlot(self,subplot):
		'''
		Inicializa los subplots con su frame, titulo, etc
		'''
		
		# Config Spectra plot
		name = 'spc'
		key = name + '%d'%subplot
		
		pcolorObj = self.pcolorObjDic[key]
		pcolorObj.makeAxes(self.indexFig,self.nrow,self.ncol,subplot)
		pcolorObj.plotBox(pcolorObj.xrange[0], pcolorObj.xrange[1], pcolorObj.yrange[0], pcolorObj.yrange[1], 'bcnst', 'bcnstv')
		
		# Config Colorbar
		if self.showColorbar:
			name = 'colorbar'
			key = name + '%d'%subplot
			
			cmapObj = self.colorbarObjDic[key]
			cmapObj.setParentAxesId(pcolorObj)
#			cmapObj.plotBox(cmapObj.xrange[0], cmapObj.xrange[1], cmapObj.yrange[0], cmapObj.yrange[1], 'bc', 'bcmtsv')
			cmapObj.colorbarPlot(cmapObj.xrange[0], cmapObj.xrange[1], cmapObj.yrange[0], cmapObj.yrange[1])
#			cmapObj.plotBox(cmapObj.xrange[0], cmapObj.xrange[1], cmapObj.yrange[0], cmapObj.yrange[1], 'bc', 'bcmtsv')
			
		# Config Power profile
		if self.showPowerProfile:
			name = 'pwprofile'
			key = name + '%d'%subplot
			
			powObj = self.pwprofileObjDic[key]
			powObj.setLineStyle(2)
			powObj.plotBox(powObj.xrange[0], powObj.xrange[1], powObj.yrange[0], powObj.yrange[1], 'bcntg', 'bc')
			powObj.setLineStyle(1)
			powObj.plotBox(powObj.xrange[0], powObj.xrange[1], powObj.yrange[0], powObj.yrange[1], 'bc', 'bc')
	
	def printTitle(self,pltitle):
		
		setPlTitle(pltitle,'black')
		
	def plot(self,subplot,x,y,z,subtitle=''):
		# Spectra plot
		
		name = 'spc'
		key = name + '%d'%subplot
		
#		newx = [x[0],x[-1]]
		pcolorObj = self.pcolorObjDic[key]
#		pcolorObj.plotBox(pcolorObj.xrange[0], pcolorObj.xrange[1], pcolorObj.yrange[0], pcolorObj.yrange[1], 'bcst', 'bcst')
		
		#pcolorObj.delLabels()
		pcolorObj.setLabels(title=subtitle)

		deltax = None; deltay = None
		
		pcolorObj.advPcolorPlot(z, 
								x,
								y, 
								xmin=pcolorObj.xrange[0], 
								xmax=pcolorObj.xrange[1], 
								ymin=pcolorObj.yrange[0], 
								ymax=pcolorObj.yrange[1], 
								zmin=pcolorObj.zrange[0], 
								zmax=pcolorObj.zrange[1],
								deltax=deltax, 
								deltay=deltay, 
								getGrid=pcolorObj.getGrid)
		
		#Solo se calcula la primera vez que se ingresa a la funcion
		pcolorObj.getGrid = False
		
		#pcolorObj.plotBox(pcolorObj.xrange[0], pcolorObj.xrange[1], pcolorObj.yrange[0], pcolorObj.yrange[1], 'bcst', 'bcst', nolabels=True)
		
		# Power Profile
		if self.showPowerProfile:
			power = numpy.average(z, axis=0)
			name = 'pwprofile'
			key = name + '%d'%subplot
			powObj = self.pwprofileObjDic[key]
			
			if powObj.setXYData() != None:
				#clearData(powObj)
				powObj.setLineStyle(2)
				powObj.plotBox(powObj.xrange[0], powObj.xrange[1], powObj.yrange[0], powObj.yrange[1], 'bcntg', 'bc')
				powObj.setLineStyle(1)
			else:
				powObj.setXYData(power,y)
			
			powObj.plotBox(powObj.xrange[0], powObj.xrange[1], powObj.yrange[0], powObj.yrange[1], 'bc', 'bc')
			powObj.basicXYPlot(power,y)
			powObj.setXYData(power,y)
	
	def savePlot(self,indexFig,filename):
		
		width = self.width*self.ncol
		hei = self.height*self.nrow
		savePlplot(filename,width,hei)
	
	def refresh(self):
		refresh()

class RtiPlot:
	
	pcolorObjDic = {}
	colorbarObjDic = {}
	pwprofileObjDic = {}
	showColorbar = None
	showPowerProfile = None
	XAxisAsTime = None
	widht = None
	height = None
	__rtixpos = None
	__rtiypos = None
	__cmapxpos = None
	__cmapypos = None
	__profxpos = None
	__profypos = None
	
	def __init__(self,indexFig,nsubplot,winTitle,colormap,showColorbar,showPowerProfile,XAxisAsTime):
		self.width = 700
		self.height = 150
		self.showColorbar = showColorbar
		self.showPowerProfile = showPowerProfile
		self.XAxisAsTime = XAxisAsTime
		
		ncol = 1
		nrow = nsubplot
		initMatplotlib(indexFig,ncol,nrow,winTitle,self.width,self.height)
		setColormap(colormap)
		self.ncol = ncol
		self.nrow = nrow
	
	def setFigure(self,indexFig):
		setFigure(indexFig)
	
	def setRtiScreenPos(self):
					
		if self.showPowerProfile: xi = 0.07; xf = 0.65
		else:   xi = 0.07; xf = 0.9 
		yi = 0.15; yf = 0.80
		
		xpos = [xi,xf]
		ypos = [yi,yf]
		
		self.__rtixpos = xpos
		self.__rtiypos = ypos
		
		return xpos,ypos
	
	def setColorbarScreenPos(self):
						
		xi = self.__rtixpos[1] + 0.03; xf = xi + 0.03
		
		yi = self.__rtiypos[0]; yf = self.__rtiypos[1]
		
		xpos = [xi,xf]
		ypos = [yi,yf]
		
		self.__cmapxpos = xpos
		self.__cmapypos = ypos

		return xpos,ypos
	
	def setPowerprofileScreenPos(self):
		
		xi = self.__cmapxpos[1] + 0.05; xf = xi + 0.20

		yi = self.__rtiypos[0]; yf = self.__rtiypos[1]
		
		xpos = [xi,xf]
		ypos = [yi,yf]
		
		self.__profxpos = [xi,xf]
		self.__profypos = [yi,yf]

		return xpos,ypos

	def setup(self,subplot,xmin,xmax,ymin,ymax,zmin,zmax,title,xlabel,ylabel,timedata,timezone='lt',npoints=100):
		# Config Rti plot
		szchar = 1.10
		name = 'rti'
		key = name + '%d'%subplot
		
		# xmin, xmax --> minHour, max Hour : valores que definen el ejex x=[horaInicio,horaFinal]
		thisDateTime = datetime.datetime.fromtimestamp(timedata)
		startDateTime = datetime.datetime(thisDateTime.year,thisDateTime.month,thisDateTime.day,xmin,0,0)
		endDateTime = datetime.datetime(thisDateTime.year,thisDateTime.month,thisDateTime.day,xmax,59,59)
		deltaTime = 0
		if timezone == 'lt':
			deltaTime = time.timezone
		startTimeInSecs = time.mktime(startDateTime.timetuple()) - deltaTime
		endTimeInSecs = time.mktime(endDateTime.timetuple()) - deltaTime
		
		xrange = [startTimeInSecs,endTimeInSecs]
		totalTimeInXrange = endTimeInSecs - startTimeInSecs + 1.
		deltax = totalTimeInXrange / npoints
		
		yrange = [ymin,ymax]
		zrange = [zmin,zmax] 
		
		xpos,ypos = self.setRtiScreenPos()
		pcolorObj = BaseGraph(name,subplot,xpos,ypos,xlabel,ylabel,title,szchar,xrange,yrange,zrange,deltax)
		if self.XAxisAsTime:
			pcolorObj.setXAxisAsTime(self.XAxisAsTime)
			xopt = 'bcnstd'
			yopt = 'bcnstv'
		else:
			xopt = 'bcnst'
			yopt = 'bcnstv'
		
		pcolorObj.plotBox(pcolorObj.xrange[0], pcolorObj.xrange[1], pcolorObj.yrange[0], pcolorObj.yrange[1], xopt, yopt)
		self.pcolorObjDic[key] = pcolorObj
		

		# Config Colorbar
		if self.showColorbar:
			szchar = 0.9
			name = 'colorbar'
			key = name + '%d'%subplot
			
			xpos,ypos = self.setColorbarScreenPos()
			xrange = [0.,1.]
			yrange = [zmin,zmax]
			cmapObj = BaseGraph(name,subplot,xpos,ypos,'','','dB',szchar,xrange,yrange)
			cmapObj.plotBox(cmapObj.xrange[0], cmapObj.xrange[1], cmapObj.yrange[0], cmapObj.yrange[1], 'bc', 'bcm')
			cmapObj.colorbarPlot(cmapObj.xrange[0], cmapObj.xrange[1], cmapObj.yrange[0], cmapObj.yrange[1])
			cmapObj.plotBox(cmapObj.xrange[0], cmapObj.xrange[1], cmapObj.yrange[0], cmapObj.yrange[1], 'bc', 'bcmtsv')
			self.colorbarObjDic[key] = cmapObj
		
		
		# Config Power profile
		if self.showPowerProfile:
			szchar = 0.8
			name = 'pwprofile'
			key = name + '%d'%subplot
			
			xpos,ypos = self.setPowerprofileScreenPos()
			xrange = [zmin,zmax]
			yrange = [ymin,ymax]
			powObj = BaseGraph(name,subplot,xpos,ypos,'dB','','Power Profile',szchar,xrange,yrange)
			powObj.setLineStyle(2)
			powObj.plotBox(powObj.xrange[0], powObj.xrange[1], powObj.yrange[0], powObj.yrange[1], 'bcntg', 'bc')
			powObj.setLineStyle(1)
			powObj.plotBox(powObj.xrange[0], powObj.xrange[1], powObj.yrange[0], powObj.yrange[1], 'bc', 'bc')
			self.pwprofileObjDic[key] = powObj

	
	def plot(self,subplot,x,y,z):
		# RTI plot
		name = 'rti'
		key = name + '%d'%subplot
		
		data = numpy.reshape(z, (1,-1))
		data = numpy.abs(data)
		data = 10*numpy.log10(data)
		newx = [x,x+1]
		
		pcolorObj = self.pcolorObjDic[key]
		
		if pcolorObj.xaxisIsTime:
			xopt = 'bcstd'
			yopt = 'bcst'
		else:
			xopt = 'bcst'
			yopt = 'bcst'
			
		pcolorObj.plotBox(pcolorObj.xrange[0], pcolorObj.xrange[1], pcolorObj.yrange[0], pcolorObj.yrange[1], xopt, yopt)
		
		deltax = pcolorObj.deltax
		deltay = None
		
		if pcolorObj.xmin == None and pcolorObj.xmax == None:
			pcolorObj.xmin = x
			pcolorObj.xmax = x
		
		if x >= pcolorObj.xmax:
			xmin = x
			xmax = x + deltax
			x = [x]
			pcolorObj.advPcolorPlot(data, 
									x, 
									y, 
									xmin=xmin, 
									xmax=xmax, 
									ymin=pcolorObj.yrange[0], 
									ymax=pcolorObj.yrange[1], 
									zmin=pcolorObj.zrange[0], 
									zmax=pcolorObj.zrange[1],
									deltax=deltax, 
									deltay=deltay, 
									getGrid=pcolorObj.getGrid)
			
			pcolorObj.xmin = xmin
			pcolorObj.xmax = xmax
			
		
		# Power Profile
		if self.showPowerProfile:
			data = numpy.reshape(data,(numpy.size(data)))
			name = 'pwprofile'
			key = name + '%d'%subplot
			powObj = self.pwprofileObjDic[key]
			
			if powObj.setXYData() != None:
				clearData(powObj)
				powObj.setLineStyle(2)
				powObj.plotBox(powObj.xrange[0], powObj.xrange[1], powObj.yrange[0], powObj.yrange[1], 'bcntg', 'bc')
				powObj.setLineStyle(1)
			else:
				powObj.setXYData(data,y)
			
			powObj.plotBox(powObj.xrange[0], powObj.xrange[1], powObj.yrange[0], powObj.yrange[1], 'bc', 'bc')
			powObj.basicXYPlot(data,y)
			powObj.setXYData(data,y)
			
	def savePlot(self,indexFig,filename):
		
		width = self.width*self.ncol
		hei = self.height*self.nrow
		savePlplot(filename,width,hei)
		
	def refresh(self):
		refresh()


if __name__ == '__main__':
	
	"""
	Ejemplo1
	"""
	#Setting the signal
	fs = 8000
	f0 = 200
	f1 = 400
	T = 1./fs
	x = numpy.arange(160)
	y1 = numpy.sin(2*numpy.pi*f0*x*T)
	y2 = numpy.sin(2*numpy.pi*f1*x*T)
	signalList = [y1,y2]
	
	xmin = numpy.min(x)
	xmax = numpy.max(x)
	ymin = numpy.min(y1) - 10
	ymax = numpy.max(y1) + 10
	
	subplotTitle = "subplot no. "
	xlabel = ""
	ylabel = ""
	
	indexFig = 1
	nsubplot = 2
	winTitle = "figura"
	
	isPlotIni = False
	isPlotConfig = False
	ntimes = 10
	
	
	# Instancia del objeto
	linearObj = LinearPlot(indexFig,nsubplot,winTitle)
		
	
	for i in range(ntimes):
		# Crea los subplots
		if not(linearObj.isPlotIni):
			for index in range(nsubplot):
				indexplot = index + 1
				title = subplotTitle + '%d'%indexplot
				linearObj.createObjects(indexplot,xmin,xmax,ymin,ymax,title,xlabel,ylabel)
			linearObj.isPlotIni = True
		
		# Inicializa el grafico en cada iteracion
		linearObj.setFigure(indexFig)
		linearObj.setNewPage("")
		
		for index in range(nsubplot):
			subplot = index
			linearObj.iniPlot(subplot+1)

		#plotea los datos
		for channel in range(nsubplot):
			data = y1 + numpy.random.rand(len(y1))
			linearObj.plot(channel+1, x, data, type='simple')
			
		linearObj.refresh()
		
#		linearObj.closePage() #descomentar esta linea para mas iteraciones
		
		time.sleep(0.05)
		
	linearObj.show()

	print "example 1 completed"
		


	"""
	Ejemplo2
	"""

	# make these smaller to increase the resolution
	dx, dy = 0.05, 0.05
	x = numpy.arange(-3.0, 3.0001, dx)
	y = numpy.arange(-2.0, 2.0001, dy)
#	X,Y = numpy.meshgrid(x, y)
	X,Y = sn.ndgrid(x, y)
	Z = (1- X/2 + X**5 + Y**3)*numpy.exp(-X**2-Y**2)
	
	# Creating Object
	indexPlot = 2
	nsubplot = 1
	winTitle = "mi grafico pcolor"
	colormap = "br_green"
	showColorbar = True
	showPowerProfile = False
	XAxisAsTime = False
	
	subplotTitle = "subplot no. "
	xlabel = ""
	ylabel = ""
	
	xmin = -3.0
	xmax = 3.0
	ymin = -2.0
	ymax = 2.0
	zmin = -0.3
	zmax = 1.0
	
	isPlotIni = False
	isPlotConfig = False
	ntimes = 10
	
	
	for i in range(ntimes):		
		
		# Instancia del objeto
		if not(isPlotConfig):
			pcolorObj = PcolorPlot(indexPlot, nsubplot, winTitle, colormap, showColorbar, showPowerProfile, XAxisAsTime)
			isPlotConfig = True
		
		# Crea los subplots
		if not(isPlotIni):
			for index in range(nsubplot):
				indexplot = index + 1
				title = subplotTitle + '%d'%indexplot
				subplot = index
				pcolorObj.createObjects(indexplot,xmin,xmax,ymin,ymax,zmin,zmax,title,xlabel,ylabel)
			isPlotIni = True
		
		# Inicializa el grafico en cada iteracion
		pcolorObj.setFigure(indexPlot)
		pcolorObj.setNewPage("")
		
		for index in range(nsubplot):
			subplot = index
			pcolorObj.iniPlot(subplot+1)
		
		#plotea los datos
		for channel in range(nsubplot):
			data = Z+0.1*numpy.random.randn(len(x),len(y))
			pcolorObj.plot(channel+1, x, y, data)
			
		pcolorObj.refresh()
		
#		pcolorObj.closePage() #descomentar esta linea para mas iteraciones
		
		time.sleep(1)
	
	pcolorObj.show()

	print "example 2 completed"