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
import Evolife.Scenarii.Parameters as EPar
import re

import random

class Rule:
	" defines all possible automaton rules "
	def __init__(self, RuleNumber):
		" convert the rule number into a list of bits "
		# For each configuration number (3-bit for three-cell neighbourhood --> 8 configurations), 
		# the rule gives the new binary state of the cell.
		# Attention: the following line is only valid for 8 configurations
		self.Rule = [int(b) for b in list(bin(RuleNumber)[2:].rjust(8,'0'))]
		# example: rule 32 --> 00100000
		self.Rule.reverse()
		# example: rule 32 --> 00000100
		# only the 5th configuration: '101', allows the next state to be 1.
		# if this configuation is absent at the beginning, an all-0 state emerges.
		print('Rule {0}: {1}'.format(RuleNumber, self.Rule))
	
	def Next(self, Left, Middle, Right):
		try:
			return self.Rule[(Left << 2) + (Middle << 1) + Right]
		except IndexError:
			print('Rule Error: unknown environment {0}{0}{0}'.format(Left,Middle,Right))
			return None
		

class CA_Scenario(EPar.Parameters):

	def __init__(self, ConfigFile):
		# Parameter values
		EPar.Parameters.__init__(self, ConfigFile)
		#############################
		# Global variables			#
		#############################
		self.Colours = ['red', 'yellow']	# corresponds to Evolife colours
		self.Rule = Rule(self.Parameter('Rule'))

	
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
		# Pattern = re.split('\D+', Scenario.Parameter('StartingPattern'))[1]
		Pattern = eval(Scenario.Parameter('StartingPattern')[2:])
		self.Size = len(Pattern)
		print('Size = %d' % self.Size)
		# self.Ground[self.Size//2].setContent(1)	# The middle cell is set to 1
		self.Ground = [Cell(n,int(x)) for (n,x) in enumerate(Pattern)]
		self.VPosition = 1	# Vertical position in display
		# self.display()
		

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
			# Fractional size means a fraction of window width
			# Observer.record((str(C) % self.VPosition, (C.Position, (-self.VPosition) % Depth, Scenario.Colours[C.content()], 1.0/self.Size)))
			Observer.record((C.Position, (-self.VPosition) % Depth, Scenario.Colours[C.content()], 1.0/self.Size))

	def EvolveCell(self, Cell):
		x= Cell.Position
		Area = map(self.ToricConversion, [x-1, x, x+1])		# neighbourhood is circular
		# print Area,
		Neighbourhood = map(self.Content, Area)		
		# print Neighbourhood,
		NewState = Scenario.Rule.Next(*Neighbourhood)	# computes new state for central cell
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
	print(__doc__)

	
	#############################
	# Global objects			#
	#############################
	Scenario = CA_Scenario('_Params.evo')
	
	CAutomaton = Automaton(Scenario)	  # logical settlement grid
	
	Observer = EO.Generic_Observer()	  # Observer records display orders
	Observer.recordInfo('FieldWallpaper', 'white')
	margin = 4	# horizontal margins in the window
	zoom = 4
	Observer.recordInfo('DefaultViews', [('Field', CAutomaton.Size * zoom + 2 * margin)])
	
	
	EW.Start(CAutomaton.OneStep, Observer, Capabilities='RP')		# R means that only changed positions have to be displayed; P enables photos


	print("Bye.......")
	


__author__ = 'Dessalles'
