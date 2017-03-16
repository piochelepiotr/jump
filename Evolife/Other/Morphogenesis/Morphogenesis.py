#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################

##############################################################################
# Basic implementation of Turing's reaction-diffusion model                  #
##############################################################################


""" Basic implementation of Turing's reaction-diffusion model              
"""

import sys
import random

sys.path.append('..')
sys.path.append('../../..')

import Evolife.Ecology.Observer				as EO
import Evolife.Scenarii.Parameters 			as EPar
import Evolife.QtGraphics.Evolife_Window 	as EW
import Evolife.QtGraphics.Curves 			as EC
import Landscapes

	

# global functions
Quantify = lambda x, Step: int(x / Step) * Step if Step else x

def Limitate(x, Min=0, Max=1, Step=0): 
	" returns a quantified version of x cut to fit an interval "
	if Step == 0:	Step = Gbl.P('Precision')
	return Quantify(x, Step)
	return min(max(Quantify(x, Step),Min), Max)
	# return min(max(round(x, 3),Min), Max)



class LandCell(Landscapes.LandCell):
	" Defines what is stored at a given location "

	def __init__(self):
		# Cell content is defined as a couple  (ConcentrationA, ConcentrationB)
		Landscapes.LandCell.__init__(self, (0, 0), VoidCell=(0, 0))
		self.Colour = 2	# white == invisible
		self.OldColour = None

	def activated(self, Future=False):
		" tells whether a cell is active "
		return self.Content(Future=Future)[1] > 0
	
	def Update(self):
		self.Present = self.Future	# erases history
		return not self.activated()
		
	def getColour(self, product=1, Max=1):
		" return color corresponding to content, but only if it has changed "
		# self.Colour = EC.Shade(self.Content()[0], BaseColour='red', Max=Max, darkToLight=False)
		self.Colour = '#%02X%02XFF' % ((255 * (1 - self.Content()[product-1]),) * 2)
		Col = None
		if self.Colour != self.OldColour:	Col = self.Colour
		self.OldColour = self.Colour
		return Col
	
	#------------------------#
	# Reaction               #
	#------------------------#
	# Gray-Scott model       #
	#------------------------#
	def Reaction(self, F, k, Noise=0):
		"	Reaction between local products A and B "
		(Ca0, Cb0) = self.Content()
		deltaB = Ca0 * Cb0 * Cb0
		if Noise:	deltaB *= (1 - Noise * (1 - random.random()))
		deltaA = F * (1 - Ca0) - deltaB
		deltaB -= (F + k) * Cb0
		return ((Limitate(Ca0 + deltaA, Max=Gbl.P('MaxA'))), Limitate(Cb0 + deltaB, Max=Gbl.P('MaxB')))
		
	
class Landscape(Landscapes.Landscape):
	" Defines a 2D square grid "

	def __init__(self, Size, DiffusionCoefficients, MaxValues, NeighbourhoodRadius, Precision):
		Landscapes.Landscape.__init__(self, Width=Size, CellType=LandCell)	# calls local LandCell definition
		# Computing actual diffusion coefficients
		self.NeighbourhoodRadius = NeighbourhoodRadius
		self.DcA, self.DcB = DiffusionCoefficients
		self.MaxA, self.MaxB = MaxValues
		self.Precision = Precision

	def Seed(self, Center, Value, Radius=5):
		" Creation of a blob "
		for Pos1 in self.neighbours(Center, Radius):	# immediate neighbours
			self.Modify(Pos1, Value, Future=False)
			
	#------------------------#
	# Diffusion              #
	#------------------------#
	def activate(self, Pos0):
		" Cell located at position 'Pos0' produces its effect on neighbouring cells "
		(Ca0, Cb0) = self.Cell(Pos0).Content()	# actual concentration values
		# NL = self.neighbourhoodLength(Radius=self.NeighbourhoodRadius)
		# Neighbours = self.neighbours(Pos0, self.NeighbourhoodRadius)
		Neighbours = self.neighbours(Pos0, Radius=1)
		# deltaA = (self.DcA * Ca0)/NL	# contribution to neighbouring cells
		# deltaB = (self.DcB * Cb0)/NL	# contribution to neighbouring cells
		NeighbourhoodInfluenceA, NeighbourhoodInfluenceB = (0,0)
		for Pos1 in Neighbours:	# immediate neighbours
			(Ca1, Cb1) = self.Content(Pos1)	# current concentration values
			NeighbourhoodInfluenceA += Ca1
			NeighbourhoodInfluenceB += Cb1
		self.Modify(Pos0, (	Limitate(Ca0 + self.DcA * (NeighbourhoodInfluenceA - 4 * Ca0), Max=self.MaxA, Step=self.Precision), 
							Limitate(Cb0 + self.DcB * (NeighbourhoodInfluenceB - 4 * Cb0), Max=self.MaxB, Step=self.Precision)), 
							Future=True)

import cProfile
def One_Step1():
	print(Observer.StepId)
	if Observer.StepId % 5 == 0:
		cProfile.run("One_Step1()")
		return True
	else:	return One_Step1()

def One_Step():
	""" This function is repeatedly called by the simulation thread.
		One agent is randomly chosen and decides what it does
	"""

	Observer.season()	# increments StepId
	dotSize = Gbl.P('DotSize')
	maxA = Gbl.P('MaxA')
	maxB = Gbl.P('MaxB')
	if Observer.Visible():	
		# for (Position, Cell) in Land.travel():
		for Position in Land.ActiveCells:
			Cell = Land.Cell(Position)
			# displaying concentrations
			Colour1 = Cell.getColour(1, Max=maxA)	# quantity of A
			Colour2 = Cell.getColour(2, Max=maxB)	# quantity of B
			if Colour1 is not None:
				Observer.record(('C%d_%d' % Position, Position + (Colour1, dotSize, 'shape=rectangle'))) 
			if Colour2 is not None:
				Observer.record(('C%d_%d' % Position, Position + (Colour2, dotSize, 'shape=rectangle')), Window='Trajectories') 

	#############
	# Diffusion #
	#############
	for (Position, Cell) in Land.travel():
		Land.activate(Position)	# diffusion
	Land.update()	# Let's update concentrations
	
	#############
	# Reaction  #
	#############
	for (Position, Cell) in Land.travel():
		Land.Modify(Position, Cell.Reaction(Gbl.P('F'), Gbl.P('k'), Noise=Gbl.P('Noise')), Future=False)
	# for Cell in Land.ActiveCells:
		# Cell.Reaction(Gbl.P('F'), Gbl.P('k'))

	if len(Land.ActiveCells) == 0: return False

	return True
			


if __name__ == "__main__":
	print(__doc__)

	
	#############################
	# Global objects			#
	#############################
	Gbl = EPar.Parameters(CfgFile='_Params.evo')
	Gbl.P = lambda x: Gbl.Parameter(x)	# to shorten writings
	
	Observer = EO.Experiment_Observer(Gbl)	  # Observer contains statistics
	# Observer.recordInfo('Background', 'white')
	# Observer.recordInfo('FieldWallpaper', 'white')
	Observer.recordInfo('Background', 'white')
	PhysicalSize = Gbl.P('DotSize') * Gbl.P('LandSize')
	Observer.recordInfo('DefaultViews',	[('Field', PhysicalSize, PhysicalSize),('Trajectories', PhysicalSize, PhysicalSize)])
	Observer.record([(0, Gbl.P('LandSize'),2,0), (Gbl.P('LandSize'), 0, 2,0)]) 	# to resize
	Observer.record([(0, Gbl.P('LandSize'),2,0), (Gbl.P('LandSize'), 0, 2,0)], Window='Trajectories') 	# to resize
	
	Land = Landscape(	Gbl.P('LandSize'), 
						(Gbl.P('Da'), Gbl.P('Db')), 
						(Gbl.P('MaxA'), Gbl.P('MaxB')), 
						Gbl.P('NeighbourhoodRadius'), 
						Gbl.P('Precision')
						)	  # 2D square grid
	Land.Seed((Gbl.P('LandSize')//3, Gbl.P('LandSize')//3), (0.4, 0.9), Radius=4)
	Land.Seed((2*Gbl.P('LandSize')//3, 2*Gbl.P('LandSize')//3), (0.4, 0.9), Radius=4)
	# print len(Land.ActiveCells)
	
	# Land.setAdmissible(range(101))	# max concentration
	
	EW.Start(One_Step, Observer, Capabilities='RPT')

	print("Bye.......")
	
__author__ = 'Dessalles'
