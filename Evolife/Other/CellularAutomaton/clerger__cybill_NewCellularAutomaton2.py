#!/usr/bin/env python
#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################


""" 2D Cellular Automaton with coloring mutation:
	Modified by Cybill Clerger
"""

import sys
sys.path.append('../../..')

import Evolife.Ecology.Observer as EO
import Evolife.QtGraphics.Evolife_Window as EW
import Evolife.Tools.Tools as ET
import Evolife.Scenarii.Parameters as EPar

print ET.boost()   # A technical trick that sometimes provides impressive speeding up


import random
import math

class Rule:
	" defines all possible automaton rules "
	def __init__(self, RuleNumber):
		" convert the rule number into a list of bits "
		# For each configuration number (9-bit for nine-cell neighbourhood --> 512 configurations),
		# the rule gives the new binary state of the cell.
		self.Rule = [int(b) for b in list(bin(RuleNumber)[2:].rjust(512,'0'))]
		self.Rule.reverse()
		# if this configuration is absent at the beginning, an all-0 state emerges.
		print 'Rule {0}: {1}'.format(RuleNumber, self.Rule)

	def Next(self, neighbors):
		try:
			#order: LowerRight, LowerMiddle, LowerLeft, Right, Middle, Left, UpperRight, UpperMiddle, UpperLeft
			nbRedNeighbors = len([neighbor for neighbor in neighbors if neighbor == 2])
			for index, neighbor in enumerate(neighbors):
				if neighbor == 2:
					neighbors[index] = 1
			answer = self.Rule[sum([neighbors[i] << i for i in range(len(neighbors))])]
			if answer:
				infectionProba = Scenario.Parameter('InfectionRate')
				if nbRedNeighbors >= 1 and random.random() <= infectionProba:
					return 2
				else:
					return 1
			else:
				return 0
		except IndexError:
			print 'Rule Error: unknown environment {0}{0}{0}{0}{0}{0}{0}{0}{0}'.format(*neighbors)
			return None


class CA_Scenario(EPar.Parameters):

	def __init__(self, ConfigFile):
		# Parameter values
		EPar.Parameters.__init__(self, ConfigFile)
		#############################
		# Global variables			#
		#############################
		self.Colours = ['red', 'yellow', 'green']	# corresponds to Evolife colours
		self.Rule = Rule(self.Parameter('Rule'))



# en envoyant des coordonnees (sans noms d'agents) en Layout,
# on obtient un simple dessin des points en tant que courbe


class CA_Observer(EO.Experiment_Observer):
	""" Stores parameters and observation data
	"""
	def __init__(self, Scenario):
		EO.Experiment_Observer.__init__(self, Scenario) # stores global information
		Dim = int(math.sqrt(len(Scenario.Parameter('StartingPattern'))-2))	# Logical size of the grid
		TimeLimit= Scenario.Parameter('TimeLimit')
		self.CurrentChanges = [('dummy',(Dim,Dim,0))]	# stores temporary changes
		self.recordInfo('DefaultViews', ['Field'])

	def record(self, Info):
		# stores current changes
		# Info is a couple (InfoName, Position) and Position == (x, y, color, size)
		self.CurrentChanges.append(Info)

	def get_data(self, Slot):
		if Slot == 'Positions':
			CC = self.CurrentChanges
			self.CurrentChanges = []
			return tuple(CC)
		return None

class Cell:
	""" Defines what's in one location on the ground
	"""
	def __init__(self, Position, State=None):
		self.Position = Position # Here Position is a tuple (x,y)
		self.CurrentState = State
		self.NextState = State	# Avoids mixing time steps during computation

	def content(self):
		return self.CurrentState

	def setContent(self, State):
		self.NextState = State
		return State

	def update(self):
		self.CurrentState = self.NextState

	def __str__(self):	return 'C%d%d' % (self.Position[0], self.Position[1])

class Automaton:
	"""	A 1-D grid that represents the current state of the automaton
	"""
	def __init__(self, Scenario):
		self.Size = int(math.sqrt(len(Scenario.Parameter('StartingPattern'))-2))
		self.Ground = [[Cell((i, n // self.Size), int(x)) for (n,x) in enumerate(Scenario.Parameter('StartingPattern')[2:]) if n % self.Size == i] for i in range(self.Size)]
		if Scenario.Parameter('InitialMutant'):
			self.Ground[self.Size//2][self.Size//2].setContent(2)
		else:
			self.Ground[self.Size//2][self.Size//2].setContent(1)
		self.Time = 1	# Instant in display
		self.display()


	def ToricConversion(self, pos):
		# circular row
		return (pos[0] % self.Size, pos[1] % self.Size)

	def Content(self, pos):
		" terniary state inferred from colour "
		return self.Ground[pos[0]][pos[1]].content()

	def display(self):
		for x in range(self.Size):
			for y in range(self.Size):
				C = self.Ground[x][y]
				C.update()
				# Cells are displayed as blobs: (x, y, colour, blobsize)
				# Note that Cells are given a different name, based on their position
				Observer.record((str(C), (x, y, Scenario.Colours[self.Content((x,y))], 2)))

	def EvolveCell(self, Cell):
		(x,y)= Cell.Position
		Area = map(self.ToricConversion, [(x+1,y+1), (x,y+1), (x-1,y+1), (x+1,y), (x,y), (x-1,y), (x+1,y-1), (x,y-1), (x-1,y-1)])
		Neighbourhood = map(self.Content, Area)
		NewState = Scenario.Rule.Next(Neighbourhood)
		mutationProba = 1.0*Scenario.Parameter('MutationRate')/1000
		if NewState == 1 and random.random() <= mutationProba:
			return Cell.setContent(2)
		else:
			return Cell.setContent(NewState)

	def OneStep(self):
		Observer.season()	# One step = one agent has moved
		if self.Time < Scenario.Parameter('TimeLimit'):
			for x in range(self.Size):
				for y in range(self.Size):
					NewState = self.EvolveCell(self.Ground[x][y])
			self.display()
			self.Time += 1
			return True
		return False


if __name__ == "__main__":
	print __doc__


	#############################
	# Global objects			#
	#############################
	Scenario = CA_Scenario('_Params.evo')
	Observer = CA_Observer(Scenario)	  # Observer contains statistics
	CAutomaton = Automaton(Scenario)	  # logical settlement grid


	EW.Start(CAutomaton.OneStep, Observer, Capabilities='FP')		# F means that all cells must be displayed each time
	#EW.Start(CAutomaton.OneStep, Observer, Capabilities='RP')		# R means that only changed positions have to be displayed


	print "Bye......."



__author__ = 'Dessalles'
