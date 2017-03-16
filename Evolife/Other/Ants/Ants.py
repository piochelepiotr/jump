#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################

##############################################################################
# Ants                                                                       #
##############################################################################

""" Collective foraging:
Though individual agents follow erratic paths to find food,
the collective may discover optimal paths.
"""

# In this story, 'ants' move in search for food
# In the absence of pheromone, ants move randomly for some time,
# and then head back toward the colony.
# When they find food, they return to the colony while laying down pheromone.
# If they find pheromone, ants tend to follow it.


import sys
from time import sleep
import random
		
sys.path.append('..')
sys.path.append('../../..')
import Evolife.Scenarii.Parameters			as EPar
import Evolife.Ecology.Observer				as EO
import Evolife.QtGraphics.Evolife_Window	as EW
import Evolife.Tools.Tools					as ET
import Landscapes

print(ET.boost())	# significantly accelerates python on some platforms


# two functions to convert from complex numbers into (x,y) coordinates
c2t = lambda c: (int(round(c.real)),int(round(c.imag))) # converts a complex into a couple
t2c = lambda P: complex(*P) # converts a couple into a complex

#################################################
# Aspect of ants, food and pheromons on display
#################################################
AntAspect = ('black', 28, 'shape=ant_stencil.gif')	# 28 = size
AntAspectWhenLaden = ('black', 28, 'shape=ant_stencil_red.gif')	# 28 = size
# AntAspectWhenLaden = ('red', 18)
FoodAspect = ('yellow', 14)
FoodDepletedAspect = ('brown', 14)
PPAspect = (17, 2)	# 17th colour
NPAspect = ('blue', 2)
	

class LandCell(Landscapes.LandCell):
	""" Defines what's in one location on the ground
	"""

	# Cell content is defined as a triple  (Food, NegativePheromon, PositivePheromon)

	def __init__(self, F=0, NP=0, PP=0):
		Landscapes.LandCell.__init__(self, (0, 0), VoidCell=(0, 0, 0))
		self.setContent((F,NP,PP))

	def clean(self):	
		return self.setContent((self.Content()[0],0,0))

	def food(self, addendum=0):	
		(F,NP,PP) = self.Content()
		if addendum:	self.setContent((F + addendum, NP, PP))
		return F + addendum
		
	def np(self, addendum=0):	
		(F,NP,PP) = self.Content()
		if addendum:	self.setContent((F, self.limit(NP + addendum), PP))
		return NP + addendum

	def pp(self, addendum=0):	
		(F,NP,PP) = self.Content()
		if addendum:	self.setContent((F, NP, self.limit(PP + addendum)))
		return PP + addendum

	def limit(self, Pheromone):
		return min(Pheromone, Gbl.Parameter('Saturation'))
		
	# def __add__(self, Other):
		# # redefines the '+' operation between cells
		# return LandCell(self.food()+Other.food(),
						# self.limit(self.np() + Other.np()),
						# self.limit(self.pp() + Other.pp())

	def evaporate(self):
		# Pheromone evaporation should be programmed about here
		if self.np() > 0:
			self.np(-Gbl.Parameter('Evaporation')) # Repulsive ('negative') pheromone
		if self.pp() > 0:
			self.pp(-Gbl.Parameter('Evaporation')) # Attractive ('positive') Pheromone
		if self.np() <= 0 and self.pp() <= 0:
			self.clean()
			return True
		return False

class FoodSource:
	""" Location where food is available
	"""
	def __init__(self, Name):
		self.Name = Name
		self.FoodAmount = 0
		self.Location = (-1,-1)
		self.Radius = (Gbl.Parameter('FoodSourceSize')+1)//2
		self.Distribution = Gbl.Parameter('FoodQuantity') // ((2*self.Radius+1) ** 2)
		self.Area = []

	def locate(self, Location = None):
		if Location:
			self.Location = Location
		return self.Location

	def __repr__(self):
		return "[%s, %d, %s...]" % (self.Name, self.FoodAmount, str(self.Area)[:22])
		
	
class Landscape(Landscapes.Landscape):
	""" A 2-D grid with cells that contains food or pheromone
	"""
	def __init__(self, Size, NbFoodSources):
		Landscapes.Landscape.__init__(self, Size, CellType=LandCell)
		
		# Positioning Food Sources
		self.FoodSourceNumber = NbFoodSources
		self.FoodSources = []
		for FSn in range(self.FoodSourceNumber):
			FS = FoodSource('FS%d' % FSn)
			FS.locate((random.randint(0,Size-1),random.randint(0,Size-1)))
			self.FoodSources.append(FS)
			for Pos in self.neighbours(FS.locate(), Radius=FS.Radius):
				FS.Area.append(Pos)
				self.food(Pos, FS.Distribution)  # Cell contains a certain amount of food
			Observer.record((FS.Name, FS.locate() + FoodAspect))	# to display food sources

	# def Modify(self, (x,y), Modification):
		# self.Ground[x][y] += Modification   # uses addition as redefined in LandCell
		# return self.Ground[x][y]

	# def FoodSourceConsistency(self):
		# for FS in self.FoodSources:
			# amount = 0
			# for Pos in FS.Area:
				# amount += self.food(Pos)
			# if amount != FS.FoodAmount:
				# print('************ error consistency %s: %d %d' % (FS.Name, amount, FS.FoodAmount))
				# print [self.food(Pos) for Pos in FS.Area]
				# FS.FoodAmount = amount
						
	def food(self, Pos, delta=0):
		if delta:
			# let the food source know
			for FS in self.FoodSources:
				if Pos in FS.Area:
					FS.FoodAmount += delta
					if FS.FoodAmount <= 0:
						Observer.record((FS.Name, FS.locate() + FoodDepletedAspect))	# to display food sources
		return self.Cell(Pos).food(delta)	# adds food
	
	def foodQuantity(self):
		return sum([FS.FoodAmount for FS in self.FoodSources])
	
	def npheromone(self, Pos, delta=0):	
		if delta:	
			self.ActiveCells.add(Pos)
			Observer.record(('NP%d_%d' % Pos, Pos + NPAspect)) # for ongoing display of negative pheromone
		return self.Cell(Pos).np(delta)	# adds repulsive pheromone
		
	def ppheromone(self, Pos, delta=0):	
		if delta:
			self.ActiveCells.add(Pos)
			Observer.record(('PP%d_%d' % Pos, Pos + PPAspect)) # for ongoing display of positive pheromone
		return self.Cell(Pos).pp(delta)	# adds attractive pheromone

	def evaporation(self):
		for Pos in list(self.ActiveCells):
			if self.Cell(Pos).evaporate(): # no pheromone left
				# call 'erase' for updating display when there is no pheromone left
				self.erase(Pos) # for ongoing display
				self.ActiveCells.remove(Pos)

	def erase(self, Pos):
		" says to Observer that there is no pheromon left at that location "
		Observer.record(('NP%d_%d' % Pos, Pos + (-1,))) # negative colour means erase from display
		Observer.record(('PP%d_%d' % Pos, Pos + (-1,))) # negative colour means erase from display
		
	def update_(self):
		# scans ground for food and pheromone - May be used for statistics
		Food = NPher = PPher = []
		for (Position, Cell) in Land.travel():
			if Cell.Food:		Food.append((Pos, Cell.food()))
			if Cell.NPheromone:	NPher.append((Pos, Cell.np()))
			if Cell.PPheromone:	PPher.append((Pos, Cell.pp()))
		return (Food, NPher, PPher)
	   
	   
class Ant:
	""" Defines individual agents
	"""
	def __init__(self, IdNb, InitialPosition):
		self.ID = IdNb
		self.Colony = InitialPosition # Location of the colony nest
		self.location = InitialPosition
		self.PPStock = Gbl.Parameter('PPMax') 
		self.Action = 'Move'
		self.moves()

	def Sniff(self):
		" Looks for the next place to go "
                Neighbourhood = list(Land.neighbours(self.location,
                Gbl.Parameter('SniffingDistance')))
		random.shuffle(list(Neighbourhood)) # to avoid anisotropy
		acceptable = None
		best = -Gbl.Parameter('Saturation')	# best == pheromone balance found so far
		for NewPos in Neighbourhood:
			# looking for position devoid of negative pheromon
			if NewPos == self.location: continue
			if Land.food(NewPos) > 0:
				# Food is always good to take
				acceptable = NewPos
				break
			found = Land.ppheromone(NewPos)   # attractiveness of positive pheromone
			found -= Land.npheromone(NewPos)   # repulsiveness of negative pheromone
			if found > best:			  
				acceptable = NewPos
				best = found
		return acceptable

	def returnHome(self):
		" The ant heads toward the colony "
		Direction = t2c(self.Colony) - t2c(self.location)   # complex number operation
		Distance = abs(Direction)
		if Distance >= Gbl.Parameter('SniffingDistance'):
			# Negative pheromone
			if Gbl.Parameter('NPDeposit'):
				Land.npheromone(self.location, Gbl.Parameter('NPDeposit')) # marking current position as visited with negative pheromone
			# Positive pheromone
			Land.ppheromone(self.location, self.PPStock) # marking current posiiton as interesting with positive pheromone
			Direction /= Distance	# normed vector
			# MaxSteps = int(Gbl.Parameter('LandSize') / 2 / Distance)	# 
			Decrease = int(self.PPStock / Distance)	# Linear decrease
			self.PPStock -= Decrease
			# if self.PPStock <= Gbl.Parameter('PPMin'):   self.PPStock = Gbl.Parameter('PPMin')	# always lay some amount of positive pheromone
			self.location = c2t(t2c(self.location) + 2 * Direction)	# complex number operation
			self.location = Land.ToricConversion(self.location)		# landscape is a tore
			Observer.record((self.ID, self.location + AntAspectWhenLaden)) # for ongoing display of ants
		else:
			# Home reached
			self.PPStock = Gbl.Parameter('PPMax') 
			self.Action = 'Move'
		
	def moves(self):
		""" Basic behavior: move by looking for neighbouring unvisited cells.
			If food is in sight, return straight back home.
			Lay down negative pheromone on visited cells.
			Lay down positive pheromone on returning home.
		"""
		if self.Action == 'BackHome':
			self.returnHome()
		else:
			NextPos = self.Sniff()
			# print self.ID, 'in', self.location, 'sniffs', NextPos
			if NextPos is None or random.randint(0,100) < Gbl.Parameter('Exploration'): 
				# either all neighbouring cells have been visited or in the mood for exploration
				NextPos = c2t(t2c(self.location) + complex(random.randint(-1,1),random.randint(-1,1)))
				NextPos = Land.ToricConversion(NextPos)
			# Marking the old location as visited
			if Gbl.Parameter('NPDeposit'):
				Land.npheromone(self.location, Gbl.Parameter('NPDeposit'))
				# Observer.record(('NP%d_%d' % self.location, self.location + NPAspect)) # for ongoing display of negative pheromone
			self.location = NextPos
			Observer.record((self.ID, self.location + AntAspect)) # for ongoing display of ants
			foundFood = False
			if Land.food(self.location) > 0:	
				Land.food(self.location, -1)	# consume one unit of food
				foundFood = True
				# # # Observer.FoodCollected += 1
				self.Action = 'BackHome'	# return when having found food
			return foundFood

	def position(self):
		return c2t(self.Position)

					
class Population:
	" defines the population of agents "
	
	def __init__(self, PopulationSize,  Observer, ColonyPosition):
		" creates a population of ant agents "
		self.ColonyPosition = ColonyPosition
		self.Pop = []
		self.PopulationSize = PopulationSize
		for ID in range(self.PopulationSize):	self.Pop.append(Ant('A%d' % ID, ColonyPosition))
		self.AllMoved = 0  # counts the number of times all agents have moved on average
		self.SimulationGoes = 400 * self.PopulationSize
		# allows to run on the simulation beyond stop condition
		self.year = -1
		self.FoodCollected = 0

	def selectIndividual(self):
		if self.Pop:	return random.choice(self.Pop)
		return None
	
	def One_Decision(self):
		""" This function is repeatedly called by the simulation thread.
			One ant is randomly chosen and decides what it does
		"""
		# print('.', end="", flush=True)
		self.year += 1
		Observer.season()
		ant = self.selectIndividual()
		if ant and ant.moves(): self.FoodCollected += 1
		Moves = self.year // self.PopulationSize	# One step = all Walkers have moved once on average
		# print (self.year, self.AllMoved, Moves),
		if Moves > self.AllMoved:
			Land.evaporation()
			self.AllMoved = Moves
		if Observer.Visible():	Observer.curve('Food', (self.year//Gbl.Parameter('PopulationSize'), self.FoodCollected))
		if (Land.foodQuantity() <= 0):	self.SimulationGoes -= 1
		return self.SimulationGoes > 0	 # stops the simulation when False

		
if __name__ == "__main__":
	print(__doc__)

	#############################
	# Global objects			#
	#############################
	Gbl = EPar.Parameters('_Params.evo')	# Loading global parameter values
	Observer = EO.Observer(Gbl)   # Observer contains statistics
	Land = Landscape(Gbl.Parameter('LandSize'), Gbl.Parameter('NbFoodSources'))
	Pop = Population(Gbl.Parameter('PopulationSize'), Observer, (Gbl.Parameter('LandSize')//2, Gbl.Parameter('LandSize')//2))   # Ant colony

	Observer.recordInfo('Background', 'ants-1_pale.jpg')
	Observer.recordInfo('FieldWallpaper', 'Grass1.jpg')
	# Observer.recordInfo('DefaultViews', [('Field', Gbl.Parameter('LandSize')*12)])
	Observer.recordInfo('DefaultViews', [('Field', Gbl.Parameter('WindowSize'))])
	# Observer.recordInfo('FieldWallpaper', 'white')
	Observer.curve(Name='Food', Color='green1', Legend='Year (each ant moves once a year on average)&nbsp;&nbsp;&nbsp;x&nbsp;&nbsp;&nbsp;Amount of food collected')	# declaration of a curve

	EW.Start(Pop.One_Decision, Observer, Capabilities='RPC')

	print("Bye.......")
	sleep(1.0)

__author__ = 'Dessalles'
