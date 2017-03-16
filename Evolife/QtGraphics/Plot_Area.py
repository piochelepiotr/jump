#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################


##############################################################################
#  Plot Area                                                                 #
##############################################################################


""" EVOLIFE: Module Plot_Area:
	Windows that display Curves or images.
	This module can be used independently.

	Useful classes are:
	- Image_Area:   An area that displays an image
		function:   display(<bitmap>)
	- Draw_Area:	Basic drawing Area
		function:   plot(<plot_number>, (<x>, <y>) )
	- Plot_Area:	Draw_Area + grid + automatic resizing
		function:   plot(<plot_number>, (<x>, <y>) )
	- Ground:	   Defines a 2-D region where agents are located and may move
		functions:  create_agent(<name>, <colour_number>, (<x>, <y>) )
					move_agent(<name>, (<Newx>, <Newy>) )

	Usage:
		#self.W = QPlot_Area.AreaView(QPlot_Area.Image_Area)
		self.W = QPlot_Area.AreaView(QPlot_Area.Draw_Area)
		#self.W = QPlot_Area.AreaView(QPlot_Area.Plot_Area)
		self.W.Area.plot(3,(10,10))
		self.W.Area.plot(3,(20,40))
		self.W.Area.plot(3,(10,22))
"""


import sys
if __name__ == '__main__':  sys.path.append('../..')  # for tests


from math import log
import os, os.path

import PyQt4 
from PyQt4.QtCore import *	
from PyQt4.QtGui import *	
from time import sleep
import random

sys.path.append('..')

from Evolife.QtGraphics.Curves import Curves, Stroke, EvolifeColourID
from Evolife.Tools.Tools import error, Nb2A0
	
#	compatibility with python 2
if sys.version_info >= (3,0):	QString = lambda x: x

##################################################
# Basic graphic area type                        #
##################################################

class Image_Area(QGraphicsScene):
	""" Defines a logical Area on which objects are drawn (hidden from screen)
	"""

	def __init__(self, image=None, width=1000, height=1000):
		QGraphicsScene.__init__(self, 0, 0, width, height)   # calling the parent's constructor
		if image is not None and os.path.exists(str(image)):
			#print "Loading %s . . ." % image
			self.ScaledBoard = self.Board = QPixmap(image) # loads the image
			#error("Plot","Unable to find image %s" % image)
			self.fitSize = True
		else:
			# By default, a Scene has a graphic area (pixmap) on which one can draw
			self.ScaledBoard = self.Board = QPixmap(width,height)
			image_ID = EvolifeColourID(image, default=None)
			if image_ID is not None:
				self.Board.fill(QColor(image_ID[1]))
			elif image and image.startswith('#'):	# background colour given by code
				self.Board.fill(QColor(image))
			else:	# default
				# self.Board.fill(QColor("#F0B554"))
				self.Board.fill(QColor("#FFFFFF"))
			self.fitSize = False
		self.Canvas = self.addPixmap(self.ScaledBoard)
		self.W = int(self.width())
		self.H = int(self.height())
		self.FrameNumber = 0
##		self.changed.connect(self.Changing)

##	def Changing(self, e):
##		print 'Changing', e
		
	def resize(self, w, h):
		self.W = int(w)
		self.H = int(h)
		#self.ScaledBoard = self.Board.scaled(w, h)
		self.redraw()
		
	def dimension(): return (self.width(), self.height())

	def redraw(self):
		" the whole scene is redrawn when the scale changes "
		for obj in self.items():
			self.removeItem(obj)
		self.ScaledBoard = self.Board.scaled(self.W, self.H)
		self.Canvas = self.addPixmap(self.ScaledBoard)
		self.setSceneRect(self.itemsBoundingRect())
		#self.setSceneRect(0, 0, self.W/10.0, self.H/10.0)
		
		
	def drawPoints(self):
		# just for test
		item = QGraphicsEllipseItem(20, 10, 40, 20, None, self)
		qp = QPainter()
		qp.begin(self.Board)
		pen = QPen()
		pen.setColor(Qt.red)
		pen.setWidth(3)
		qp.setPen(pen)
		for i in range(10):
			x = random.randint(1, self.W-1)
			y = random.randint(1, self.H-1)
			qp.drawLine(0,0,x, y)	 
		qp.end()
		self.Canvas.setPixmap(self.ScaledBoard)

class AreaView(QGraphicsView):
	""" Standard canvas plus resizing capabilities
	"""
	def __init__(self, AreaType=Image_Area, parent=None, image=None, width=400, height=300):
		# Defining View
		QGraphicsView.__init__(self, parent)	  # calling the parent's constructor
		self.Area = AreaType(image, width=width, height=height)	 # View is a kind of camera on Area
		self.setScene(self.Area)
		self.resize(self.Area.W, self.Area.H)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)	# necessary to avoir infinite loop with resizing events
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		
	def paintEvent(self, e):
		#print '.',
		QGraphicsView.paintEvent(self,e)

	def resizeEvent(self,e):
		if self.Area is not None:
			self.Area.resize(e.size().width(), e.size().height())
		QGraphicsView.resizeEvent(self,e)

	def updateScene(self, L):
		pass
	
	def photo(self, Name, FrameNumber=-1, outputDir='.', extension='png'):
		" takes a snapshot and saves it to a new file "
		if FrameNumber >= 0:
			self.FrameNumber = FrameNumber
		else:
			self.FrameNumber += 1
		sleep(0.1)
		picture = QPixmap.grabWidget(self)
		ImFileName = Name + Nb2A0(self.FrameNumber)
		picture.save(os.path.join(outputDir, ImFileName + '.' + extension))
		return ImFileName
		

##################################################
# Graphic area with drawing capabilities		 #
##################################################

##class BoundedPath(QPainterPath):
##	" Long paths take too long to display - We split them into limited chunks "
##
##	def __init__(self, StartPoint):
##		self.SizeLimit= 30
##		QPainterPath.__init__(self, StartPoint)
##		self.Length = 1
##		
##	def lineTo(self, Point):
##		QPainterPath.lineTo(self,Point)
##		self.Length += 1
##
##	def full(self):
##		return self.Length > self.SizeLimit
		
	
class Draw_Area(Image_Area, Curves):
	""" Draw_Area: Basic drawing Area
	"""
	
	def __init__(self, image=None, width=400, height=400):
		Image_Area.__init__(self, image, width, height)
		self.set_margins(6, 6, 6, 6)
		if True:
		# if not self.fitSize:
			self.scaleX = 100.0	# current maximal horizontal value
			self.scaleY = 100.0	# current maximal vertical value
		# else:
			# self.scaleX = self.W
			# self.scaleY = self.H
		Curves.__init__(self)
		self.init_Pens()	# initializes pens for drawing curves

	def set_margins(self, Left, Right, Bottom, Top):
		" surrounding margins (in Image_Area pixels) "
		self.LeftMargin = Left
		self.RightMargin = Right
		self.BottomMargin = Bottom
		self.TopMargin = Top
		
	def init_Pens(self):
		# Defining one pen and one QPainterPath per curve
		self.Pens = dict()
##		self.PainterPaths = dict()   # polygons
##		self.PainterPathRefs = dict()	# reference to polygons in the scene
		for Curve in self.Curves:
			self.Pens[Curve.ID] = QPen()
			self.Pens[Curve.ID].setColor(QColor(Curve.colour))
			self.Pens[Curve.ID].setWidth(3)
##			self.PainterPaths[Curve.ID] = BoundedPath(QPointF(self.convert((0,0))[0], self.convert((0,0))[1]))
##			self.PainterPathRefs[Curve.ID] = self.addPath(self.PainterPaths[Curve.ID], self.Pens[Curve.ID])
				   
	def grid(self):
		pass
	
	def convert(self, Point):
		" Conversion of input units into local coordinates "
		(x,y) = Point
		if self.scaleX and self.scaleY:
			return (self.LeftMargin + ((self.W - self.LeftMargin - self.RightMargin) * x) / self.scaleX,
					self.H - self.BottomMargin - ((self.H - self.BottomMargin - self.TopMargin) * y) / self.scaleY )
		return (0,0)

	def Q_Convert(self, Point):
		(x,y) = self.convert(Point)
		#print "(%02f, %02f) converti en (%02f, %02f) avec scale=(%02f, %02f)" % (Point[0], Point[1], x ,y, self.scaleX, self.scaleY)
		return QPointF(x, y)
	
	def draw(self,oldpoint, newpoint, Width=3, ColorID=0, Tag=''):
		" draws a further segment on a given curve "
		#print 'drawing from', oldpoint, 'to', newpoint
##		self.PainterPaths[ColorID].moveTo(self.Q_Convert(oldpoint))
##		self.drawTo(newpoint, Width, ColorID, Tag=Tag)
		self.Pens[ColorID].setWidth(Width)
		self.addLine(QLineF(self.Q_Convert(oldpoint), self.Q_Convert(newpoint)), self.Pens[ColorID])

	def drawTo(self, newpoint, Width=3, ColorID=0, Drawing=True, Tag=''):
		" draws a further segment on a given curve "
		#print ">>>>>>>>", newpoint, self.Q_Convert(newpoint)
##		if Drawing:	self.PainterPaths[ColorID].lineTo(self.Q_Convert(newpoint))
##		else:	   self.PainterPaths[ColorID].moveTo(self.Q_Convert(newpoint))
##		self.PainterPathRefs[ColorID].setPath(self.PainterPaths[ColorID])
##		if self.PainterPaths[ColorID].full():
##			self.PainterPaths[ColorID] = BoundedPath(self.PainterPaths[ColorID].currentPosition())
##			self.PainterPathRefs[ColorID] = self.addPath(self.PainterPaths[ColorID], self.Pens[ColorID])
		self.draw(self.Curves[ColorID].last(), newpoint, Width, ColorID, Tag)

		
	def erase(self):
		for P in self.Curves:
			P.erase()
		for obj in self.items():
			if obj != self.Canvas:
				self.removeItem(obj)
		self.init_Pens()
		self.grid()
				
	def redraw(self):
		" the whole picture is redrawn when the scale changes "
		Image_Area.redraw(self)
		self.init_Pens()
		self.grid()
		for Curve in self.Curves:
			for Segment in Curve:
				# print(Segment)
				self.draw(Segment[0], Segment[1], Width=Curve.thick, ColorID=Curve.ID)
				pass
		pass

	def reframe(self, Point, Anticipation=False):
		" performs a change of scale when necessary "
		self.change = False

		def rescale(Scale, coord):
			# print(coord, Scale)
			if coord <= Scale:
				return Scale
			self.change = True
			if Anticipation:
				ordre = 10 ** (int(log(coord,10)))  # order of magnitude
				Scale = (coord // ordre + 1) * ordre
			else:
				Scale = coord
			return Scale

		(x,y) = Point
		self.scaleX = rescale(self.scaleX, x)
		self.scaleY = rescale(self.scaleY, y)
		return self.change

	def plot(self, Curve_designation, newpoint, Width=3):
		" draws an additional segment on a curve "
		# one is tolerant about the meaning of Curve_designation
		Curve_id = EvolifeColourID(Curve_designation)[0]
		# print('plotting to', Curve_designation, Curve_id, newpoint)
		try:
			self.drawTo(newpoint, Width, Curve_id)	# action on display
			self.Curves[Curve_id].add(newpoint)		# memory
			# if Width != self.Curves[Curve_id].thick:	print('changing thickness to', Width)
			self.Curves[Curve_id].thick = Width		# update thickness
		except IndexError:
			error("Draw_Area: unknown Curve ID")

	def move(self, Curve_designation, newpoint):
		" introduces a discontinuity in a curve "
		# one is tolerant about the meaning of Curve_designation
		Curve_id = EvolifeColourID(Curve_designation)[0]
		# print('moving to', Curve_designation, Curve_id, newpoint)
		try:
##			self.drawTo(newpoint, Curve_id, Drawing=False)
			self.Curves[Curve_id].add(newpoint, Draw=False)
		except IndexError:
			error("Draw_Area: unknown Curve ID")
	
	def speck(self, Curve_id, newpoint, Size=3):
		" draws a spot "
		# print('about to draw speck at', Curve_id, newpoint)
		if self.reframe(newpoint):
			self.redraw()
		self.move(Curve_id, newpoint)
		self.plot(Curve_id, newpoint, Width=Size)
	
		
##################################################
# Graphic area for displaying curves			 #
##################################################
	
class Plot_Area(Draw_Area):
	""" Definition of the drawing area, with grid, legend and curves
	"""
	def __init__(self, image=None, width=556, height=390):
		Draw_Area.__init__(self, image, width, height)
		self.set_margins(32, 20, 28, 20)
		#self.grid()	 # drawing the grid
		self.init_Pens()	# redo it because offsets have changed
		
	def grid(self):
		" Drawing a grid with axes and legend  "
		NbMailles = 5
		mailleX = (0.5 + self.W - self.RightMargin - self.LeftMargin)/NbMailles
		mailleY = (0.5 + self.H - self.TopMargin - self.BottomMargin)/NbMailles
		GridColour = '#A64910'
		gridPen = QPen()
		gridPen.setColor(QColor(GridColour))
		gridPen.setWidth(1)
		# drawing the grid
		for i in range(NbMailles+1): 
			# vertical lines 
			self.addLine( self.LeftMargin + i*mailleX, self.TopMargin,
								self.LeftMargin + i*mailleX, self.H - self.BottomMargin, gridPen)
			# horizontal lines
			self.addLine( self.LeftMargin, self.TopMargin + i*mailleY,
								self.W - self.RightMargin, self.TopMargin + i*mailleY, gridPen)
		# drawing axes
		gridPen.setWidth(2)
		self.addRect(self.LeftMargin,self.TopMargin,self.W-self.RightMargin+1-self.LeftMargin,
					 self.H-self.BottomMargin+1-self.TopMargin, gridPen)

		# drawing legend
		PSize = 13 - 2 * int(log(max(self.scaleX, self.scaleY), 10))	# size of police
		for i in range(NbMailles+1):
			# legend on the x-axis
			self.addSimpleText(QString(str(int(i*self.scaleX//NbMailles)).center(3)),
						QFont(QString("Arial"), PSize)).setPos(QPointF(self.LeftMargin+i*mailleX-12, self.H-self.BottomMargin+5))
			# legend on the y-axis
			self.addSimpleText(QString(str(int(i*self.scaleY//NbMailles)).rjust(3)),
						QFont(QString("Arial"), PSize)).setPos(QPointF(self.LeftMargin-25, self.H - self.BottomMargin - i*mailleY-6))

		# drawing colour code
		for C in self.Curves[1:]:
			self.addEllipse(self.W - self.RightMargin/2, self.H - C.ID * self.BottomMargin/2 - 20,
							  4,4,QPen(QColor(C.colour)), QBrush(QColor(C.colour), Qt.SolidPattern))

			

	def plot(self, Curve_id, newpoint):
		""" A version of PLOT that checks whether the new segment
			remains within the frame. If not, the scale is changed
			and all curves are replotted
		"""
		if self.reframe(newpoint, Anticipation=True):
			self.redraw()
		Draw_Area.plot(self, Curve_id, newpoint)


##################################################
# 2-D Graphic area for displaying moving agents  #
##################################################
class Ground(Draw_Area):
	""" Defines a 2-D region where agents are located and may move
	"""

	DEFAULTSHAPE = 'ellipse'
	# DEFAULTSHAPE = 'rectangle'

	def __init__(self, image=None, width=400, height=300, legend=True):
		self.Legend = legend and (image == None or EvolifeColourID(image)[0])
		self.Toric = False  # says whether right (resp. top) edge
							# is supposed to touch left (resp. bottom) edge
		Draw_Area.__init__(self, image, width, height)
		self.set_margins(6, 6, 6, 6)
		#self.Board.fill(QColor(Qt.white))
		self.Canvas.setPixmap(self.ScaledBoard)
		self.positions = dict() # positions of agents
		self.segments = dict()	# line segments pointing out from agents
		self.shapes = dict()	# shape of agents
		self.GraphicAgents = dict()	# Q-references of agents 
		self.KnownShapes = {}

			
	def setToric(self, Toric=True):
		self.Toric = Toric
		
	def grid(self):
		" Writing maximal values  "
		# Writing maximal values for both axes
		if self.Legend:
			self.addSimpleText(QString(str(int(self.scaleY))),
						QFont(QString("Arial"), 8)).setPos(QPointF(self.LeftMargin + 3,
																   7 + self.TopMargin))
			self.addSimpleText(QString(str(int(self.scaleX))),
						QFont(QString("Arial"), 8)).setPos(QPointF(self.W - self.RightMargin-16 ,
																   self.H-self.BottomMargin - 8))

	def redraw(self):
		" the whole picture is redrawn when the scale changes "
		# First, delete all unnamed objects (named objects are agents)
##		for Agent in self.GraphicAgents:
##			self.removeItem(self.GraphicAgents[Agent])
		Draw_Area.redraw(self)  # destroys all agents in the scene
		for Agent in self.GraphicAgents:
			self.restore_agent(Agent)

	def coordinates(self, Coord):
		"""	Coord is a tuple.
			complete version: (X,Y,Colour,size, ToX,ToY,ToColour,ToSize) 
			Any trailing part may be missing.
			To... indicates that a segment should be drawn starting from (X,Y)
		"""

		Shape = None
		# shape is indicated anywhere as a string
		Coord1 = tuple()
		for x in Coord:
			if type(x) == str and x.startswith('shape'):	Shape = x[x.rfind('=')+1:].strip()
			else:	Coord1 += (x,)
		Start = Stroke(Coord1[:4], self.W)
		if len(Coord1) > 4:	End = Stroke(Coord1[4:], self.W)
		else:	End = Stroke(None)	# no segment
		return (Start, End, Shape)
				
	def convert(self, Coord):
		if self.Toric:
			Coord = (Coord[0] % self.scaleX, Coord[1] % self.scaleY)
		return Draw_Area.convert(self, Coord)
								 
	def create_agent(self, Name, Coord):
		""" creates a dot at some location that represents an agent 
		"""
		self.move_agent(Name, Coord)	# move_agent checks for agent's existence and possibly creates it
		
	def move_agent(self, Name, Coord=None, Position=None, Segment=None, Shape=None):
		""" moves an agent's representative dot to some new location 
		"""	  
		# Coord in analysed as a Position + an optional segment starting from that position, 
		# and missing coordinates are completed
		if Coord:	(Position, Segment, Shape) = self.coordinates(Coord)	
		if not self.Toric and self.reframe(Position.point()):   # The window is reframed if necessary
			self.redraw()
		Location = self.convert(Position.point()) # Translation into physical coordinates
		if Name in self.positions:  	
			if self.positions[Name].colour != Position.colour or self.shapes.get(Name) != Shape:
				# Colour or shape has changed, the agent is destroyed and reborn
				# print 'Changing colour'
				self.remove_agent(Name)
				if str(Position.colour).startswith('-'):
					# print 'destorying agent'
					return  # negative colour means the agent is removed
				self.move_agent(Name, Coord)	# false recursive call
			if self.positions[Name].Coord == Position.Coord \
					and self.segments[Name].Coord == Segment.Coord \
					and self.shapes.get(Name) == Shape:
				return  # nothing to do
			#### moving an existing agent ####
			# print Name, Position.Coord,  self.positions[Name].Coord
			self.positions[Name] = Position	# recording the agent's new position
			self.shapes[Name] = Shape	# recording the agent's new shape
			AgentRef = self.GraphicAgents[Name][0]
			AgentRef.setPos(QPointF(Location[0],Location[1]))	# performing actual move
			if self.segments[Name].Coord:	# the segment is re-created
				self.remove_segment(Name)
			if Segment.Coord:
				SegmentRef = self.create_graphic_segment(Position, Segment)
			else:	SegmentRef = None
			self.segments[Name] = Segment
			self.GraphicAgents[Name] = (AgentRef, SegmentRef)	# New Q-reference to graphic objects are memorized
		else:   #### creating the agent ####
			# print 'displaying', Name, 'in', Position.Coord
			try:
				if str(Position.colour).startswith('-'):
					# print 'Error negative colour in display -->\t\t', Position.Coord
					return
				AgentRef = self.create_graphic_agent(Position, Shape)			
				AgentRef.setPos(QPointF(Location[0],Location[1]))
				if Segment.Coord:
					SegmentRef = self.create_graphic_segment(Position, Segment)
				else:	SegmentRef = None
				self.positions[Name] = Position	# recording the agent's new position
				self.shapes[Name] = Shape	# recording the agent's new shape
				self.segments[Name] = Segment
				self.GraphicAgents[Name] = (AgentRef, SegmentRef)	# Q-reference to graphic objects are memorized
			except IndexError:
				error("Draw_Area: unknown colour ID")

	def create_graphic_agent(self, Position, Shape=None):
		" creates a graphic agent and returns the Q-reference "
		if Shape is None: Shape = self.DEFAULTSHAPE
		if Shape == 'ellipse':
			return self.addEllipse(0, 0, Position.size, Position.size,
								   QPen(QColor(EvolifeColourID(Position.colour)[1])),
								 QBrush(QColor(EvolifeColourID(Position.colour)[1]), Qt.SolidPattern))
		if Shape == 'rectangle':
			return self.addRect(0, 0, Position.size, Position.size,
								   QPen(QColor(EvolifeColourID(Position.colour)[1])),
								 QBrush(QColor(EvolifeColourID(Position.colour)[1]), Qt.SolidPattern))
		if Shape not in self.KnownShapes:
			if os.path.exists(Shape):
				# print('Existing shape: %s' % Shape)
				self.KnownShapes[Shape] = QPixmap(Shape) # loads the image
		if Shape in self.KnownShapes: 
			agent = self.addPixmap(self.KnownShapes[Shape])
			scale = float(Position.size) / agent.boundingRect().width()
			agent.scale(scale, scale)
			return agent
		error("Ground: unknown shape: %s" % Shape)
		

	def create_graphic_segment(self, Position, Segment):
		" creates a graphic segment and returns the Q-reference "
		Colour = EvolifeColourID(Segment.colour)[0]
		self.Pens[Colour].setWidth(Segment.size)
		Location1 = self.convert(Position.point())	# Translation into physical coordinates
		Location2 = self.convert(Segment.point())	# Translation into physical coordinates
		return self.addLine(Location1[0], Location1[1], Location2[0], Location2[1], self.Pens[Colour])
							 
	def remove_agent(self, Name):
		""" removes an agent from the ground
		"""
		self.remove_segment(Name)
		self.removeItem(self.GraphicAgents[Name][0])
		del self.positions[Name]
		del self.GraphicAgents[Name]

	def remove_segment(self, Name):
		" removes a segment from the ground"
		if self.segments[Name].Coord:
			self.removeItem(self.GraphicAgents[Name][1])
		del self.segments[Name]
		
	def restore_agent(self, Name):
		# the agent is still present in 'positions' and in 'segments', but is graphically dead 
		self.move_agent(Name, Position=self.positions.pop(Name), Segment=self.segments.pop(Name), 
				Shape=self.shapes.get(Name))	
		
	def on_ground(self):
		" Returns the identificiation of all agents on the ground "
		return list(self.GraphicAgents.keys())

	def scroll(self):
		for Name in self.GraphicAgents:
			self.positions[Name].scroll()
			self.move_agent(Name, Position + Segment)	# addition has been  redefined

	def draw_tailed_blob(self, Coord):
		" draws a blob and a segment, as for an agent, but without agent name and without moving and removing options "
		(Position, Segment, Shape) = self.coordinates(Coord)	
		# print(Position)
		# print(Segment)
		if not self.Toric and self.reframe(Position.point()):   # The window is reframed if necessary
			self.redraw()
		if Segment.Coord:
			self.move(Segment.colour, Position.point())
			self.plot(Segment.colour, Segment.point(), Width=Segment.size)
		self.speck(Position.colour, Position.point(), Size=Position.size)
	
		
	
##################################################
# Local Test									 #
##################################################

if __name__ == "__main__":

	print(__doc__)


__author__ = 'Dessalles'
