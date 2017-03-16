#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################

##############################################################################
# Worm                                                                       #
##############################################################################

""" Cellular automaton :
Complex shapes emerging from very simple rules
"""

# A worm moves on a triangular grid, and eat everything on his path
# It cannot take a path it already visited because it would starve
# When it is on a node, if it already encountered the same distribution of eaten and non-eaten paths in front of itself, it will take the same decision as the last time it encountered this distribution

import sys
sys.path.append('..')
sys.path.append('../../..')

import Evolife.Scenarii.Parameters			as EPar
import Evolife.Ecology.Observer				as EO
import Evolife.QtGraphics.Evolife_Window		as EW
import Evolife.Tools.Tools				as ET

import time
import random


class Worm_Observer(EO.Observer): 
	""" Stores global variables for observation
	"""
	def __init__(self, Scenario):
		self.Size = 2*Scenario.Parameter('Size')
		EO.Observer.__init__(self, Scenario) # The observer prints the grid and the worm
		self.Trajectories = []
		self.MsgLength = dict()
	
	# Initialization of the grid
	def Field_grid(self):
		Trajectories = [] 	
		for k in range(0, self.Size, 2):
			for j in range(0, self.Size, 2):
				if (j/2)%2 == 1 : 	i = k-1
				else :	i = k
				Trajectories.append((i,j,'black',2))
		return Trajectories



class Worm:
	
	def __init__(self, Observer, RuleString="0", speed=100, startPosition=[0,0]):
		
		# Initialization of the Rule
		RuleArray = []
		try:
			RuleString = str(RuleString)
			for digit in RuleString:
				RuleArray.append(int(digit))
		except ValueError:
			RuleArray = []
		self.Rule = Rule(RuleArray)
		
		# Initialization of the start position of the Worm
		self.LastPosition = [startPosition[0], startPosition[1]]
		self.CurrentPosition = [startPosition[0]+2, startPosition[1]]

		#Initialization of the grid and the speed of the worm
		self.Grid = Grid(Observer)
		self.sleepTime = 10 / float(speed)
		self.step = 1

	def doStep(self):
		if self.Grid.eat(self.LastPosition[:], self.CurrentPosition[:]) :
			Observer.season()
			
			AdjacentNodes = self.Grid.getAdjacentNodes(self.LastPosition[:], self.CurrentPosition[:])
			# getAdjacentNodes returns the 6 positions adjacent to the current position of the worm
			# the AdjacentNodes are sorted from 0 to 5, where 3 is the last node the worm visited. 
			
			EatenPaths = []
			for i in range(0, 6):
				if self.Grid.isEaten(AdjacentNodes[i][:], self.CurrentPosition[:]): 
					# If the path to an adjacent node has already been visited
					EatenPaths.append(i)

			todo = self.Rule.todo(EatenPaths) #Given the already eaten paths, the rule tells what the worm should do next

			if todo == -1: # If every paths around a node are already visited
				print("Dead worm in %s steps" % self.step) # The worm dies
				return False

			self.LastPosition = self.CurrentPosition[:]
			self.CurrentPosition = AdjacentNodes[todo][:]
			self.step += 1
			time.sleep(self.sleepTime)
			return True

		else : 				# If the rule makes the worm eat a path he already visited, the algorithm ends
			print("The worm cannot eat a path he already visited")
			return False

class Rule:

	def __init__(self, Rule=[]):

		self.Choices = Rule[:] # The list of choices to make if the worm doesn't know what to do.
		
		self.Todo = {}
		# The Todo dictionnary saves which path the worm should take, given the path it already visited around itself
		# A dictionnary is a set of (key, value)
		# The keys are numbers between 0 and 63, representing a set of eaten paths.
		# If the paths 0, 1 and 3 are eaten, it's represented by the key 2**0 + 2**1 + 2**3 = 11
		# Each value is a number between 0 and 5, giving which path the worm should take if it encounters this set of eaten paths.
		
		self.Todo[63] = -1 # If the key=63, every paths are eaten and the worm dies
		for i in range (0, 6):
			self.Todo[63 - 2**i] = i # When only one path is not eaten, then the worm takes it.

	def todo(self, EatenPaths):
		key = 0
		for direction in EatenPaths : # Generates the key of the dictionnary, given the list of the eaten paths
			 key += 2**direction
		if key in self.Todo : # This pattern has already been encountered. The worm knows what to do.
			return self.Todo[key]
		return self.addChoice(EatenPaths) # It's a new pattern, which must be processed	
		
	def addChoice(self, EatenPaths): # This function fills the Todo dictionnary
		key = 0
		for direction in EatenPaths : # Generates the key of the dictionnary, given the list of the eaten paths
			 key += 2**direction
		if key not in self.Todo : 
			if len(self.Choices)>0 and self.Choices[0] not in EatenPaths : # If the list of default choices is not empty, and the default choice is allowed, then it's used for this pattern of eaten paths
				self.Todo[key] = self.Choices[0]
				del self.Choices[0] # Then this choice is removed from the default choices
			else : # If there is no good default choice to do, the choice is random among the possible ones
				NotEatenPaths = [i for i in range(0,6) if i not in EatenPaths]
				self.Todo[key] = NotEatenPaths[int(len(NotEatenPaths)*random.random())]
		print("added choice : %s --> %s" %(EatenPaths,self.Todo[key]))
		return self.Todo[key]
	

class Grid:	
	
	Directions = [
		[1, 2],
		[-1, 2],
		[-2, 0],
		[-1, -2],
		[1, -2],
		[2, 0]
	] # The cartesian coordinates of the six possible paths, centered on the node
	
	def __init__(self, Observer):
		self.EatenPaths = [] # List of the eaten paths (which cannot be visited again)
		self.Color = Color()
		self.Observer = Observer

	def eat(self, lastPosition, currentPosition):
		if self.isEaten(lastPosition, currentPosition):
			return False # If the path is already eaten, return False
		self.EatenPaths.append([lastPosition, currentPosition]) # Adds the path to the list of the eaten ones
		color = self.Color.next()
		Observer.record((lastPosition[0], lastPosition[1], color, 2, currentPosition[0], currentPosition[1], color, 2))
		Observer.record(('Worm',(lastPosition[0],lastPosition[1],'black',4,currentPosition[0],currentPosition[1], 'black', 5)))
		return True

	def isEaten(self, Start, End): # True if a path between two nodes is already eaten
		if [Start, End] in self.EatenPaths or [End, Start] in self.EatenPaths:
			return True
		return False
	
	# getAdjacentNodes returns the 6 positions adjacent to the current position of the worm
	# the AdjacentNodes are sorted from 0 to 5, where 3 is the last node the worm visited. 
	def getAdjacentNodes(self, lastPosition, currentPosition):
		AdjacentNodes = dict()
		lastMove = [currentPosition[0]-lastPosition[0], currentPosition[1]-lastPosition[1]]
		directionIndex = Grid.Directions.index(lastMove)
		for i in range (0,6) :
			AdjacentNodes[i] = [
				currentPosition[0] + Grid.Directions[directionIndex%6][0], 
				currentPosition[1] + Grid.Directions[directionIndex%6][1]
			]
			directionIndex += 1
		return AdjacentNodes

class Color:

	Colors = [
		'red',
		'green',
		'blue'
	]
	
	def __init__(self, period=50):
		self.Index = 0
		self.Shade = 1
		self.Period = period
		self.Step = 0
	
	def next(self):
		self.Step += 1
		if self.Step%self.Period == 0:
			self.Shade += 1
			if self.Shade == 12:
				self.Shade = 1
				self.Index = (self.Index+1)%3
		return Color.Colors[self.Index]+str(self.Shade)
		




if __name__ == "__main__":
	
	print(__doc__)
	print(ET.boost())	# significantly accelerates python on some platforms

	# Global objects	   
	Gbl = EPar.Parameters('_Params.evo')	# Loading global parameter values
	Observer = Worm_Observer(Gbl)   # Observer prints the worm

	StartPosition = [4*(Gbl.Parameter('Size')/4), 4*((Gbl.Parameter('Size')-1)/4)]
	
	# Initial draw
	Observer.recordInfo('FieldWallpaper', 'white')
	Observer.recordInfo('DefaultViews', ['Field'])
	Observer.record(('Worm',(StartPosition[0], StartPosition[1], 'black', 2)))	
	
	# Initialization of the worm
	TheWorm = Worm(Observer, RuleString=Gbl.Parameter('Rule'), speed=Gbl.Parameter('Speed'), startPosition=StartPosition)	
	EW.Start(TheWorm.doStep, Observer, Capabilities='PCR')

	print("Bye.......")
		
