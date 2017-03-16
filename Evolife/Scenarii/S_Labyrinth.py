#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################




"""	 EVOLIFE: Scenario Labyrinth:
		The individuals' DNA guides a 'robot' through a labyrinth,
		with the hope of getting out of it
"""
	#=============================================================#
	#  HOW TO MODIFY A SCENARIO: read Default_Scenario.py         #
	#=============================================================#

import sys
if __name__ == '__main__':  sys.path.append('../..')  # for tests

######################################
# specific variables and functions   #
######################################

from random import randint



################################
# Scenario class instance      #
################################

from Evolife.Scenarii.Default_Scenario import Default_Scenario

class Scenario(Default_Scenario):

	######################################
	# Most functions below overload some #
	# functions of Default_Scenario	  #
	######################################

	def initialization(self):
		self.Grid = [	[12,10,10,10,10,10,10,10,10,10],
					[ 4, 8,10,10,10, 8, 9,14, 9,12],
					[ 5, 5,12, 8, 9, 4, 2,11, 4, 2],
					[ 5, 5, 6, 2, 3, 5,12, 8, 1,13],
					[ 7, 4,10, 8,10, 3, 6, 2, 1, 7],
					[14, 1,12, 1,12, 8,15,12, 0,10],
					[13, 5, 5, 5, 6, 2, 8, 1, 5,13],
					[ 4, 1, 5, 6,10, 9, 4, 3, 5, 7],
					[ 5, 7, 4,10,11, 5, 5,14, 2,10],
					[ 6,10, 3,14,10, 2, 2,10,10,10]  ]
		self.season(0,None)

	def grid(self, Location, direction):
		""" The Labyrinth is a 10x10 grid. Each cell C can be of 16 types, depending
			on its surrounding walls. 
			C & 1 : indicates the presence of the right wall
			C & 2 : indicates the presence of the top wall
			C & 4 : indicates the presence of the left wall
			C & 8 : indicates the presence of the bottom wall
			Directions are coded as: 0: right, 1: up, 2: left, 3: down
		"""
		(row,col) = Location
		d = 2 ** direction 
		if not (self.Grid[row][col] & d):
			# the movement is possible
			if d == 1:
				return (row, col+1)
			elif d == 2:
				return (row+1, col)
			elif d == 4:
				return (row, col-1)
			elif d == 8:
				return (row-1, col)
		else:
			return None


	def get_path(self, DNA):

		def get_direction(Location):
			(row,col) = Location
			b1 = DNA[2*(10*row+col)]
			b2 = DNA[2*(10*row+col)+1]
			if b1 and b2:	return 2	# left
			if b1:			return 1	# up
			if b2:			return 3	# down
			return 0		# right


		walls = 0			   # counts the number of times the robot hits a wall
		u_turns = 0			 # counts the number of times the robot makes a u-turn
		poison = 0			  # measures the amount of poison encountered by the robot
		Positions = [(5,0)]
		for step in range(self.Parameter('MaxSteps')):
			NewPosition = self.grid(Positions[-1],get_direction(Positions[-1]))
			if NewPosition == None:
				# we hit a wall
				walls += 1
				# we get another chance by trying a random direction
				NewPosition = self.grid(Positions[-1],randint(0,3))
				if NewPosition == None:
					continue	# try to be more successful with the next step
			if len(Positions) > 1 and NewPosition == Positions[-2]:
				u_turns += 1
			Positions.append(NewPosition)
			if NewPosition[1] > 9:
				break		   # the exit has been found
			poison += self.Poison[NewPosition[0]][NewPosition[1]] # exposure to poison
			# the individual lays down its own poisonous pheromon
			if self.Poison[NewPosition[0]][NewPosition[1]] < self.Parameter('MaxPoison'):
				self.Poison[NewPosition[0]][NewPosition[1]] += 1
		return ((step, walls, u_turns, poison), Positions)

	def eval_path(self, Path):
		(step, walls, u_turns, poison) = Path[0]
		return   self.Parameter('PenaltyWall') * (self.Parameter('MaxSteps') - walls) \
			   + self.Parameter('PenaltyU_turn') * (self.Parameter('MaxSteps') - u_turns)\
			   + self.Parameter('PenaltyPoison') * (self.Parameter('MaxPoison') * self.Parameter('MaxSteps') +1  - poison) \
			   + self.Parameter('RewardExiting') * (self.Parameter('MaxSteps') - step -1)


	def season(self, year, agents):
		self.Poison = [[0,0,0,0,0,0,0,0,0,0] for x in range(10)]   # Caveat:  [ [0] * 10] * 10 would be incorrect
												# as it would make ten shallow copies of the ten-digit list

	def genemap(self):
		""" Defines the name of genes and their position on the DNA.
		Accepted syntax:
		['genename1', 'genename2',...]:   lengths and coding are retrieved from configuration
		[('genename1', 8), ('genename2', 4),...]:   numbers give lengths in bits; coding is retrieved from configuration
		[('genename1', 8, 'Weighted'), ('genename2', 4, 'Unweighted'),...]:	coding can be 'Weighted', 'Unweighted', 'Gray', 'NoCoding'
		"""
		return [('labyr',200)]

	def behaviour(self, indiv, avg):
		""" Defines what the phenotype of individuals consists of
		"""
		path = self.get_path(indiv.get_DNA())[1]
		if path == None:	return None
		RelOffsX = 1.4
		RelOffsY = 0.2
		ScaleX = 8.1
		ScaleY = 9.2
		# strangely, path consists in (y,x) points
		#path = [ (5,0), (6,0), (6,1), (7,1), (7,2), (8,2), (8,3), (9,3), (9,4)]
		transform = lambda P: ((RelOffsX + P[1]+1)*ScaleX, (RelOffsY + P[0]+1)*ScaleY)
		Behaviour = []	# contains list of tailed blobs [(S1,(blobX,blobY,blobColour,blobSize,ToX,ToY,segmentColour,thickness)), (s2, (...)), ...]
		LastStep = (5,0)	# starting point
		for (nro,step) in enumerate(path):	
			Behaviour.append(('S%d' % nro, (transform(LastStep) + (4,0) + transform(step) + (4,4))))
			LastStep = step
		return Behaviour

	def evaluation(self, indiv):
		""" Implements the computation of individuals' scores
		"""
		if indiv.score() == 0:
			# the individual has not yet been evaluated
			B = self.get_path(indiv.get_DNA())
			(step, walls, u_turns, poison) = B[0]
			indiv.score(self.eval_path(B), FlagSet=True)
			indiv.location = (walls, indiv.score(), min(21,10+u_turns))

	def default_view(self):	return ['Genomes', 'Trajectories']
		
		
	def display_(self):
		""" Defines what is to be displayed. It offers the possibility
			of plotting the evolution through time of the best score,
			the average score, any locally defined value,
			and the average value of the various genes and phenes.
			It should return a list of pairs (C,X)
			where C is the curve colour and X can be
			'best', 'average', 'local', any gene name defined in genemap
			or any phene defined in phenemap
		"""
		return [('white','best'),('blue','average')]
		
	def wallpaper(self, Window):
		" displays background image or colour when the window is created "
		# Possible windows are: 'Field', 'Curves', 'Genome', 'Log', 'Help', 'Trajectories', 'Network'
		if Window == 'Trajectories':	return 'Scenarii/Labyr.png'
		return Default_Scenario.wallpaper(self, Window)
		
			

###############################
# Local Test                  #
###############################

if __name__ == "__main__":
	print(__doc__ + '\n')
	import sys
	sys.path.append("..//Genetics")
	import DNA
	G = DNA.DNA(200)
	print(G)
##    print "\nResult: %d" % (eval_path(get_path(G.get_DNA())))
	input('[Return]')
	
