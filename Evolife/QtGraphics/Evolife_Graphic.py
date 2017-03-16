#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################


##############################################################################
#  Evolife_Graphic                                                                 #
##############################################################################


""" EVOLIFE: Module Evolife_Graphic:
	Windows that display Genomes, Labyrinth and Social networks for Evolife.

	Useful classes are:
	- Genome_window:  An image area that displays binary genomes
	- Network_window: A drawing area that displays social links
	- Field_window:   A drawing area that displays agent movements
"""

import sys
if __name__ == '__main__':  sys.path.append('../..')  # for tests

from PyQt4 import QtGui, QtCore

import os.path
import sys
sys.path.append('..')


from Evolife.QtGraphics.Plot_Area import AreaView, Image_Area, Draw_Area, Ground
from Evolife.QtGraphics.Curves import EvolifeColourID, EvolifeColourNames
from Evolife.Tools.Tools import Nb2A0, warning



#---------------------------#
# Basic keyboard control    #
#---------------------------#

class Active_Frame(AreaView):
	""" An Active_frame reacts to basic keyboard control
	"""
	def __init__(self, AreaType=None, parent=None, control=None, image=None, width=400, height=300):
		if AreaType is not None:
			AreaView.__init__(self, AreaType=AreaType, parent=parent, image=image, width=width, height=height)	# calling the parents' constructor
		else:
			QtGui.QWidget.__init__(self)
			self.Area = None
		self.Parent = parent
		self.Control = control			  # memorizing who is in charge (buttons)
		if self.Control is None:
			self.control = self.Parent

	def keyPressEvent(self, e):	   
		# Definition of keyboard shortcuts
		if e.key() in [QtCore.Qt.Key_Q, QtCore.Qt.Key_Escape]:
			self.close()
		elif e.key() == QtCore.Qt.Key_M:
			self.Control.Raise()
			#self.Control.raise_()
			#self.Control.activateWindow()
		else:
			self.Control.keyPressEvent(e)

	def Raise(self):
		self.raise_()
		self.activateWindow()


#---------------------------#
# Floating satellite window #
#---------------------------#

class Satellite_window(Active_Frame):
	""" Satellite windows are floating windows with zooming abilities
	"""
	def __init__(self, AreaType=None, control=None, Wtitle='', image=None, width=400, height=300):
		Active_Frame.__init__(self, AreaType=AreaType, control=control, image=image, width=width, height=height)	# calling the parents' constructor
		self.Title = Wtitle
		self.setWindowTitle(Wtitle)
		self.show()
		self.minSize = 8

	def dimension(self, width=None, height=None):	
		if height is None: height = float(width)/self.Area.W * self.Area.H
		self.resize(width, height)	# used at initialization
		# return self.Area.dimension()
	
	def keyPressEvent(self, e):
		Active_Frame.keyPressEvent(self,e)
		# Additional key actions
		if e.key() in [QtCore.Qt.Key_Z, QtCore.Qt.Key_Minus]:
			self.DeZoom()
		if e.key() in [QtCore.Qt.Key_Plus]:
			self.Zoom()

	def image_display(self, Image, windowResize=True):
		if Image is None or not os.path.exists(str(Image)):   return
		self.Area.Board = QtGui.QPixmap(Image) # loads the image
		if windowResize:
			# newWidth = self.Area.W
			newWidth = min(800, self.Area.Board.width())
			newHeight = min(600, self.Area.Board.height())
			try:	zoomFactor = min(float(newWidth) / self.Area.Board.width(), float(newHeight) / self.Area.Board.height())
			except	ZeroDivisionError:	zoomFactor = 1
			self.resize(int(self.Area.Board.width()*zoomFactor), int(self.Area.Board.height()*zoomFactor))
			self.Area.redraw()	
		else:	self.Area.redraw()
		self.setWindowTitle(self.Title + ' - ' + Image)

	def Zoom(self):
		self.resize(int(self.width()*1.1),int(self.height()*1.1))

	def DeZoom(self):
		self.resize(int(self.width()*0.91),int(self.height()*0.91))

	def closeEvent(self, event):
		if self.Control is not None:
			try:
				self.Control.SWDestroyed(self)  # should be done with a signal
			except Error as Msg:
				print(Msg)
		event.accept()

##################################################
# Graphic area for displaying images			#
##################################################

class Image_window(Satellite_window):
	""" Image_window: Merely contains an image area
	"""
	def __init__(self, control=None, Wtitle='', outputDir='.'):
		self.OutputDir = outputDir
		self.W = 300
		self.H = 200
		self.defaultSize = True   # will become false when we know genome size
		Satellite_window.__init__(self, Draw_Area, control=control, Wtitle='Images', width=self.W, height=self.H)
		self.Area.set_margins(1, 1, 1, 1)

		
##################################################
# Graphic area for displaying genomes			#
##################################################

class Genome_window(Satellite_window):
	""" Genome_window: An image area that displays binary genomes
	"""
	def __init__(self, control=None, image=None, genome=None, gene_pattern=None, outputDir='.'):
		self.gene_pattern = gene_pattern
		self.OutputDir = outputDir
		self.H = 100
		self.W = 100
		self.defaultSize = True   # will become false when we know genome size
		if genome is not None:
			self.H = len(genome)
			self.W = len(genome[0])
			self.defaultSize = False
		Satellite_window.__init__(self, Draw_Area, control=control, Wtitle='Genomes', image=image, width=self.W, height=self.H)
		self.minSize = 100
		self.Area.set_margins(1, 1, 1, 1)
		if genome is not None:
			self.genome_display(genome=genome, gene_pattern=self.gene_pattern)
		self.Area.grid = self.axes

	def axes(self):
		if self.gene_pattern is None:	return
		gridPen = QtGui.QPen()
		gridPen.setColor(QtGui.QColor('#FF0000'))
		gridPen.setWidth(1)
		pattern = list(self.gene_pattern)
		G = 1
		HPos = 0
		while G in pattern:
			# vertical lines
			HPos += (pattern.index(G) * self.Area.W)/self.W
			self.Area.addLine( self.Area.LeftMargin + HPos, self.Area.TopMargin,
						  self.Area.LeftMargin + HPos, self.Area.H - self.Area.BottomMargin, gridPen)
			del pattern[:pattern.index(G)]
			G = 1-G

	def genome_display(self, genome=None, gene_pattern=(), Photo=0, CurrentFrame=-1, Prefix=''):
		""" genome gives, for each individual, the sequence of binary nucleotides 
			gene_pattern is a binary flag to signal gene alternation
		"""

		PhotoName = ''
		if Photo:
			if Prefix == '':	Prefix = '___Genome_'
			PhotoName = self.photo(Prefix, CurrentFrame, outputDir=self.OutputDir)

		if genome is None or len(genome) == 0:  return ''
		if gene_pattern is not None:	self.gene_pattern = gene_pattern
		self.H = len(genome)
		self.W = len(genome[0])
		if self.defaultSize:
			self.resize(max(self.W, self.minSize), max(self.H, self.minSize))
			self.defaultSize = False

		#GenomeImg = QtGui.QImage(W,H,QtGui.QImage.Format_RGB32)	# why not this (?) format ?
		GenomeImg = QtGui.QImage(self.W, self.H, QtGui.QImage.Format_Mono)

		for line in range(self.H):
			for pixel in range(self.W):
				if genome[line][pixel]:
					GenomeImg.setPixel(pixel,line, 1)
				else:
					GenomeImg.setPixel(pixel,line, 0)
		# We should add the bitmap with window background. Don't know how to do this
		self.Area.Board = QtGui.QBitmap.fromImage(GenomeImg.scaled(self.Area.W,self.Area.H))
		self.Area.redraw()
		return PhotoName

									
##################################################
# A graphic area that displays social links	  #
##################################################

class Network_window(Satellite_window):
	""" Network_window: A drawing area that displays social links
	"""
	def __init__(self, control, image=None, outputDir='.', width=540, height=200):
		Satellite_window.__init__(self, Draw_Area, control=control, Wtitle='Social network',
								  width=width, height=height, image=image)
		self.OutputDir = outputDir
		#self.Area.grid = self.axes
		# self.Area.Board.fill(QtGui.QColor(QtCore.Qt.white))
		self.Area.set_margins(20,20,20,20)
		self.axes()
		self.friends = {}


	def axes(self):
		""" Draws two horizontal axes; each axis represents the population;
			social links are shown as vectors going from the lower line
			to the upper one
		"""
		self.Area.move(6, (0, self.Area.scaleY))
		self.Area.plot(6, (self.Area.scaleX, self.Area.scaleY))
		self.Area.move(6, (0, 0))
		self.Area.plot(6, (self.Area.scaleX, 0))

	def Network_display(self, Layout, network=None, Photo=0, CurrentFrame=-1, Prefix=''):

		PhotoName = ''
		if Photo:
			PhotoName = self.Dump_network(self.friends, CurrentFrame, Prefix=Prefix)

		# print(network)
		if not network:	return ''
		positions = dict([L for L in Layout if len(L) == 2 and type(L[1]) == tuple]) # positions of individuals
		self.friends = dict(network)
		self.Area.scaleX = max(self.Area.scaleX, max([positions[individual][0] for individual in positions]))
		self.Area.erase()
		self.axes()
		for individual in self.friends:
			if len(self.friends[individual]):
				bestFriend = self.friends[individual][0]
				self.Area.move(6, (positions[individual][0],0))
				try:
					self.Area.plot(6, (positions[bestFriend][0],self.Area.scaleY), 2)
				except KeyError:	warning('friend has vanished', bestFriend)
##				if len(self.friends[friend]) and individual == self.friends[friend][0]:
##					self.plot(6, (positions[friend][0],self.scaleY), 3)
##				else:
##					# changing thickness of asymmetrical links
##					self.plot(6, (positions[friend][0],self.scaleY), 1)
		return PhotoName

	def Dump_network(self, friends, CurrentFrame=-1, Prefix=''):
		if Prefix == '':	Prefix = '___Network_'
		PhotoName = self.photo(Prefix, CurrentFrame, outputDir=self.OutputDir)
		MatrixFileName = os.path.join(self.OutputDir, Prefix + Nb2A0(self.FrameNumber) + '.txt')
		MatrixFile = open(MatrixFileName,'w')
		for Individual in friends:
			MatrixFile.write(str(Individual))
			for F in friends[Individual]:
				MatrixFile.write('\t%s' % F)
			MatrixFile.write('\n')
		MatrixFile.close()
		return PhotoName


##################################################
# A graphic area that displays moving agents	 #
##################################################

class Field_window(Satellite_window):
	""" Field: A 2D widget that displays agent movements
	"""

	def __init__(self, control=None, Wtitle='', image=None, outputDir='.', width=400, height=300):
		if image:
			Satellite_window.__init__(self, Ground, control=control, Wtitle=Wtitle, image=image)
			self.image_display(image, windowResize=True)	# to resize
		else:
			Satellite_window.__init__(self, Ground, control=control, Wtitle=Wtitle, image=None, width=width, height=height)
		self.FreeScale = not self.Area.fitSize	# no physical rescaling has occurred - useful to shrink logical scale to acual data
		# if self.FreeScale:
			# self.Area.scaleX = 100.0 # virtual coordinates by default
			# self.Area.scaleY = 100.0 # virtual coordinates by default
			# self.Area.redraw()	
		self.OutputDir = outputDir
		self.Area.grid()

	def Field_display(self, Layout=None, Photo=0, CurrentFrame=-1, Ongoing=False, Prefix=''):
		""" displays agents at indicated positions
			If Ongoing is false, agents that are not given positions are removed
		"""

		PhotoName = ''
		if Photo:
			if Prefix == '':	Prefix = '___Field_'
			PhotoName = self.photo(Prefix, CurrentFrame, outputDir=self.OutputDir)

		if not Layout:   return ''

		# Layout may come with two syntaxes:
		# (coord1, coord2, ...)
		# or
		# ((agent1, coord1), (agent2, coord2), ...)
		# where coord = (x, y, colour, size, toX, toY, colour, thickness, 'shape=ellipse|rectangle|<image_filename>')
		# These tuples are completed with default values if incomplete.
		
		# separating agents from mere coordinates
		AgentLayout = dict([L for L in Layout if len(L) == 2 and type(L[1]) == tuple]) # positions of individuals
		DrawingLayout = [L for L in Layout if len(L) != 2 or type(L[1]) != tuple]
		
		if AgentLayout:
			# adapting scale at first call
			if self.FreeScale:	
				self.adaptscale(AgentLayout.values())
			# getting the list of agents already present
			if not Ongoing:
				OnGround = self.Area.on_ground()
				for agent in OnGround:
					if agent not in AgentLayout:
						self.Area.remove_agent(agent)
			for Individual in AgentLayout:
				self.Area.move_agent(Individual, AgentLayout[Individual])
				# creates agent if not already existing
				
		if DrawingLayout:
			# adapting scale at first call
			if self.FreeScale:	self.adaptscale(DrawingLayout)
			# agent names are not given, Layout designates mere drawing instructions and not agents
			for Pos in DrawingLayout:
				self.Area.draw_tailed_blob(Pos)

		self.FreeScale = False
		
		return PhotoName


	def adaptscale(self, Layout):
		self.Area.scaleX = max([pos[0] for pos in Layout])
		self.Area.scaleY = max([pos[1] for pos in Layout])
		self.Area.redraw()
		
	def Field_scroll(self):
		self.Area.scroll()

		
		
class Help_window(QtGui.QTextBrowser):
	""" Displays a text file supposed to provide help
	"""
	def __init__(self, Control=None, Wtitle='Help'):
		QtGui.QTextBrowser.__init__(self)
		self.setWindowTitle(Wtitle)
		self.Control = Control

	def keyPressEvent(self, e):	   
		# Definition of keyboard shortcuts
		if e.key() in [QtCore.Qt.Key_Q, QtCore.Qt.Key_Escape]:
			self.close()
		elif e.key() == QtCore.Qt.Key_M:
			self.Control.Raise()
		else:
			self.Control.keyPressEvent(e)

	def display(self, HelpFilename):
		self.setPlainText(open(HelpFilename).read())
		self.setOverwriteMode(False)
		self.setGeometry(400, 120, 600, 500)		
		self.show()

	def Raise(self):
		self.raise_()
		self.activateWindow()

	def closeEvent(self, event):
		if self.Control is not None:
			try:
				self.Control.SWDestroyed(self)  # should be done with a signal
			except Error as Msg:
				print(Msg)
		event.accept()

class Legend_window(Help_window):
	" displays legend for curves "
	
	def __init__(self, Control=None, Wtitle='Legend'):
		Help_window.__init__(self, Control=Control, Wtitle=Wtitle)
	
	def display(self, Legend, Comments=''):
		" Legend comes as a list of couples (ColourName, Meaning) "
		# self.setPlainText(Text + '\n\npress [Esc]')
		self.setOverwriteMode(False)
		self.setGeometry(50, 550, 600, 350)		
		
		# self.insertPlainText('\nCurves:')
		self.insertHtml('<P><u>Curves</u>:<br>')
		try:
			for (CID, Ccolour, Ccolourname, CName, CLegend) in Legend:
				# self.insertPlainText('\n')
				if CID == 2: # white colour, printed in black
					self.insertHtml('<br><b><font color="black">%s:</font></b>' % (Ccolour))
				else:
					self.insertHtml('<br><b><font color="%s">%s:</font></b>' % (Ccolour, Ccolourname))
				self.insertPlainText('\t')
				self.insertHtml('%s' % CLegend)
		except IndexError:
			error("Curves: unknown Curve ID")
			
		if Comments:	
			self.insertPlainText('\n')
			self.insertHtml('%s' % Comments)
		self.insertPlainText('\n=============\n( [Esc] to close )')

		# resizing window around text (from http://stackoverflow.com/questions/9506586/qtextedit-resize-to-fit )
		text = self.document().toPlainText()    # or another font if you change it
		font = self.document().defaultFont()    # or another font if you change it
		fontMetrics = QtGui.QFontMetrics(font)      # a QFontMetrics based on our font
		textSize = fontMetrics.size(0, text)
		textWidth = textSize.width() + 30       # constant may need to be tweaked
		textHeight = textSize.height() + 30     # constant may need to be tweaked
		self.setMinimumSize(textWidth, textHeight)  # good if you want to insert this into a layout
		# self.resize(textWidth, textHeight)          # good if you want this to be standalone		
		
		self.moveCursor(QtGui.QTextCursor.Start)
		self.ensureCursorVisible() ;

		
		
		# self.setTextColor(QColor(EvolifeColourID(Position.colour)[1]))
		self.show()

	
##################################################
# Local Test									 #
##################################################

if __name__ == "__main__":

	print(__doc__)


__author__ = 'Dessalles'
