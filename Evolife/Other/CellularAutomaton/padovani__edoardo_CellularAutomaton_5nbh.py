#!/usr/bin/env python
#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################


""" Cellular Automaton:


"""

import sys
sys.path.append('../../..')

import Evolife.Ecology.Observer as EO
import Evolife.QtGraphics.Evolife_Window as EW
import Evolife.Tools.Tools as ET
import Evolife.Scenarii.Parameters as EPar

print ET.boost()   # A technical trick that sometimes provides impressive speeding up

	
import random

class Rule:
	" defines all possible automaton rules "
	def __init__(self, RuleNumber):
		" convert the rule number into a list of bits "
		# For each configuration number (3-bit for three-cell neighbourhood --> 8 configurations), 
		# the rule gives the new binary state of the cell.
		# Attention: the following line is only valid for 8 configurations
		self.Rule = [int(b) for b in list(bin(RuleNumber)[2:].rjust(32,'0'))]
		# example: rule 32 --> 00100000
		self.Rule.reverse()
		# example: rule 32 --> 00000100
		# only the 5th configuration: '101', allows the next state to be 1.
		# if this configuation is absent at the beginning, an all-0 state emerges.
		print 'Rule {0}: {1}'.format(RuleNumber, self.Rule)
	
	def Next(self, L2, L, M, R, R2):
		try:
			return self.Rule[(L2 << 4) + (L << 3) + (M << 2) + (R << 1) + R2]
		except IndexError:
			print 'Rule Error: unknown environment {0}{0}{0}'.format(L,M,R)
			return None
		

class CA_Scenario(EPar.Parameters):

	def __init__(self, ConfigFile):
		# Parameter values
		EPar.Parameters.__init__(self, ConfigFile)
		#############################
		# Global variables			#
		#############################
		self.Colours = ['white', 'black']	# corresponds to Evolife colours
		self.Rule = Rule(self.Parameter('Rule'))



# en envoyant des coordonnees (sans noms d'agents) en Layout, 
# on obtient un simple dessin des points en tant que courbe

	
class CA_Observer(EO.Experiment_Observer):
	""" Stores parameters and observation data
	"""
	def __init__(self, Scenario):
		EO.Experiment_Observer.__init__(self, Scenario) # stores global information
		Dim = len(Scenario.Parameter('StartingPattern')) - 2	# Logical size of the grid
		Depth= Scenario.Parameter('TimeLimit')
		# self.CurrentChanges = [(0,0,0),(0,Depth,0),(Dim,0,0),(Dim,Depth,0)]	# stores temporary changes
		self.CurrentChanges = [('dummy',(Dim,Depth,0))]	# stores temporary changes
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
		self.Position = Position
		self.CurrentState = State	
		self.NextState = State	# Avoids mixing time steps during computation

	def content(self):
		return self.CurrentState

	def setContent(self, State):
		self.NextState = State
		return State
	
	def update(self):
		self.CurrentState = self.NextState
	
	def __str__(self):	return 'C%d_%%d' % (self.Position)

class Automaton:
	"""	A 1-D grid that represents the current state of the automaton
	"""
	def __init__(self, Scenario):
		# self.Size = Scenario.Parameter('CASize')
		self.Size = len(Scenario.Parameter('StartingPattern')) - 2
		self.Ground = [Cell(n,int(x)) for (n,x) in enumerate(Scenario.Parameter('StartingPattern')[2:])]
		self.Ground[self.Size//2].setContent(1)	# The middle cell is set to 1
		self.VPosition = 1	# Vertical position in display
		self.display()
		

	def ToricConversion(self, x):
		# circular row
		return x % self.Size

	def Content(self, x):
		" binary state inferred from colour "
		return self.Ground[x].content()

	def display(self):
		for C in self.Ground:
			C.update()
			Depth= Scenario.Parameter('TimeLimit')
			# Cells are displayed as blobs: (x, y, colour, blobsize)
			# Note that Cells are given a different name, based on their position
			Observer.record((str(C) % self.VPosition, (C.Position, (-self.VPosition) % Depth, Scenario.Colours[C.content()], 2)))

	def EvolveCell(self, Cell):
		x= Cell.Position
		Area = map(self.ToricConversion, [x-3, x-1, x, x+1, x+3])
		# print Area,
		Neighbourhood = map(self.Content, Area)
		# print Neighbourhood,
		NewState = Scenario.Rule.Next(*Neighbourhood)
                # print NewState
		return Cell.setContent(NewState)
	
	def OneStep(self):
		Observer.season()	# One step = one agent has moved
		self.display()
		if self.VPosition < Scenario.Parameter('TimeLimit'):
			for C in self.Ground:
				NewState = self.EvolveCell(C)
			self.VPosition += 1
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
	
	
	# EW.Start(CAutomaton.OneStep, Observer, Capabilities='FP')		# F means that all cells must be displayed each time
	EW.Start(CAutomaton.OneStep, Observer, Capabilities='RP')		# R means that only changed positions have to be displayed 


	print "Bye......."
	


__author__ = 'Dessalles'
