#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################

##############################################################################
# Example to show how to use Evolife's ecology (population and groups)       #
##############################################################################


""" This class defines a 2D square grid on which agents can move
"""

import random
		
# class MySet(set):
	# " set without duplicates "
	# def append(self, Item):	self.add(Item)
	
	# def list(self):	return list(self)

class LandCell:
	""" Defines what's in one location on the ground
	"""
	def __init__(self, Content=None, VoidCell=None):
		self.VoidCell = VoidCell
		self.Present = None	# actual content
		self.Future = None	# future content
		self.Previous = None
		self.setContent(Content, Future=False)

	def Content(self, Future=False):	return self.Future if Future else self.Present

	def free(self):	return (self.Present == self.VoidCell)
	
	def clean(self):	return self.setContent(self.VoidCell)
	
	def setContent(self, Content=None, Future=False):
		if Content is None:	Content = self.VoidCell
		self.Previous = (self.Present, self.Future)
		if Future and Content != self.Future:	
			self.Future = Content	# here Present and Future diverge
			return True	# content changed
		elif Content != self.Present:
			self.Present = Content
			self.Future = Content
			return True	# content changed
		return False	# content unchanged

	def activated(self, Future=False):	# indicates relevant change
		" tells whether a cell is active "
		return self.Content(Future=Future) != self.Previous[1*Future]
	
	def Update(self):
		self.Present = self.Future	# erases history
		return self.free()

	def __str__(self):	return str(self.Content())
	
class Landscape:
	""" A 2-D square toric grid 
	"""
	def __init__(self, Width=100, Height=0, CellType=LandCell):
		self.ContentType = None	# may constrain what content can be
		self.Size = Width	
		self.Width = Width
		if Height > 0:	self.Height = Height
		else:	self.Height = self.Size
		self.Ground = [[CellType() for y in range(self.Height)] for x in range(self.Width)]
		# self.Ground = [[CellType() for y in range(self.Width)] for x in range(self.Height)]
		self.ActiveCells = set()   # list of Positions that have been modified
		self.Statistics = {}	# will contain lists of cells for each content type

	def setAdmissible(self, ContentType):	
		self.ContentType = ContentType
		self.statistics()	# builds lists of cell per content
	
	def Admissible(self, Content):
		if self.ContentType:	return (Content in self.ContentType)
		return True
		
	def ToricConversion(self, P):
		# toric landscape
		(x,y) = P
		return (x % self.Width, y % self.Height)
	
	def Modify(self, P, NewContent, check=False, Future=False):
		" Changes content at a location "
		# print 'Modyfying', (x,y), NewContent
		(x,y) = P
		Cell = self.Ground[x][y]
		if check:	
			if NewContent:	# put only admissible content only at free location
				if not self.Admissible(NewContent) or not Cell.free():
					return False
			else: # erase only when content is already there
				if Cell.free():	return False
		Cell.setContent(NewContent, Future=Future)
		if Cell.activated(Future=Future):
			# only activate cells that have actually changed state
			self.ActiveCells.add((x,y))
		return True

	def Content(self, P, Future=False):	
		(x,y) = P
		return self.Ground[x][y].Content(Future=Future)

	def Cell(self, P):		
		(x,y) = P
		try:	return self.Ground[x][y]
		except IndexError:	
			raise Exception('Bad coordinates for Cell (%d, %d)' % (x,y))
		
	def free(self, P):
		(x,y) = P
		return self.Ground[x][y].free()	# checks whether cell is free
	
	def neighbourhoodLength(self, Radius=1):
		return (2*Radius+1) ** 2  - 5	# square minus self and four corners
	
	def neighbours(self, P, Radius=1):
		" returns neighbouring cells "
		# N = []
		(x,y) = P
		for distx in range(-Radius, Radius+1):
			for disty in range(-Radius, Radius+1):
				if distx == 0 and disty == 0:	continue	# self not in neighbourhood
				if abs(distx) + abs(disty) == 2 * Radius:	continue	# corners not in neighbourhood
				# N.append(self.ToricConversion((x + distx, y + disty)))
				yield self.ToricConversion((x + distx, y + disty))
		# return N

	def segment(self, P0, P1):
		(x0,y0) = P0
		(x1,y1) = P1
		" computes the shorter segment between two points on the tore "
		(vx,vy) = self.ToricConversion((x0-x1, y0-y1))
		(wx,wy) = self.ToricConversion((x1-x0, y1-y0))
		return (min(vx,wx), min(vy,wy))
		
	def InspectNeighbourhood(self, Pos, Radius):
		""" Makes statistics about local content 
			Returns a dictionary by Content.
			The center position is omitted
		"""
		Neighbourhood = self.neighbours(Pos, Radius)
		if self.ContentType:
			LocalStatistics = dict(map(lambda x: (x,0), self.ContentType))	# {Content_1:0, Content_2:0...}
		else:	LocalStatistics = dict()
		for NPos in Neighbourhood:
			if self.Content(NPos):	
				if self.Content(NPos) in LocalStatistics:	LocalStatistics[self.Content(NPos)] += 1
				else: LocalStatistics[self.Content(NPos)] = 1
		return LocalStatistics

	def statistics(self):
		" scans ground and builds lists of cells depending on Content "
		if self.ContentType:
			self.Statistics = dict(map(lambda x: (x,[]), self.ContentType + [None]))	# {Content_1:[], Content_2:[]..., None:[]}
		for (Pos, Cell) in self.travel():
			if Cell.Content() in self.Statistics:
				self.Statistics[Cell.Content()].append(Pos)
			else:
				self.Statistics[Cell.Content()] = [Pos]

	def update(self):
		" updates the delayed effect of cells that have been modified "
		CurrentlyActiveCells = list(self.ActiveCells)
		# print '\n%d active cells' % len(CurrentlyActiveCells)
		# setting active cells to their last state
		for Pos in CurrentlyActiveCells:
			if self.Cell(Pos).Update():	# erases history, keeps last state - True if cell ends up empty
				self.ActiveCells.remove(Pos)	# cell is empty
		# self.ActiveCells.reset()

	def activation(self):
		" Active cells produce their effect "
		for Pos in list(self.ActiveCells):
			self.activate(Pos)	# may activate new cells
			
	def activate(self, Pos):
		" Cell located at position 'Pos' has been modified and now produces its effect, possibly on neighbouring cells "
		pass	# to be overloaded	
				
	def randomPosition(self, Content=None, check=False):
		" picks an element of the grid with 'Content' in it "
		if check and self.Statistics:
			for ii in range(10): # as Statistics may not be reliable
				if self.Statistics[Content]:
					Pos = random.choice(self.Statistics[Content])
					if self.Content(Pos) == Content:	# should be equal if statistics up to date
						return Pos
			# at this point, no location found with Content in it - Need to update
			self.statistics()
		else:	# blind search
			for ii in range(10):
				Row = random.randint(0,self.Height-1)
				Col = random.randint(0,self.Width-1)
				if check: 
					if self.Content((Col,Row)) == Content:	return (Col, Row)
				else: return (Col, Row)
		return None		  

	def travel(self):
		" Iteratively returns Cells of the grid "
		Pos = 0	# used to travel over the grid
		for Col in range(self.Width):
			for Row in range(self.Height):
				try:	yield ((Col,Row), self.Ground[Col][Row])
				except IndexError:
					print(self.Width, self.Height)
					print(Col, Row, Pos)
					raise
		   

class LandCell_3D(LandCell):
	""" Same as LandCell, plus a third dimension
	"""
	def __init__(self, Altitude=0, Content=None, VoidCell=None):
		LandCell.__init__(self, Content=Content, VoidCell=VoidCell)
		self.Altitude = Altitude
		
class Landscape_3D(Landscape):
	""" Same as Landscape, but stores a third dimension in cells
	"""
	def __init__(self, Altitudes=[], AltitudeFile='', CellType=LandCell_3D):
		Height = len(Altitudes)	# number of rows
		if Height == 0:
			# Altitudes are retrieved from file
			Rows = open(AltitudeFile).readlines()
			# Altitudes = [Row.split() for Row in Rows if len(Row.split()) > 1 ]
			Altitudes = [list(map(int,Row.split())) for Row in Rows]
			Height = len(Altitudes)	# number of rows
		Width = len(Altitudes[0])	# assuming rectangular array correct
		print('Ground = %d x %d' % (Width, Height))
		Landscape.__init__(self, Width=Width, Height=Height, CellType=CellType)
		for ((Col,Row), Cell) in self.travel():
			try:
				Cell.Altitude = Altitudes[Height-1-Row][Col]
			except IndexError:
				print(Width, Height)
				print(Col, Row)
				raise
	

			   
if __name__ == "__main__":
	print(__doc__)

	
	
__author__ = 'Dessalles'
