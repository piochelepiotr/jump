#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################



##############################################################################
#  Labyrinth                                                                 #
##############################################################################


""" EVOLIFE: Scenario WernerDyer
"""
	#=============================================================#
	#  HOW TO MODIFY A SCENARIO: read Default_Scenario.py		 #
	#=============================================================#


import sys
if __name__ == '__main__':  sys.path.append('../..')  # for tests


######################################
# specific variables and functions   #
######################################

import random

class Grid(object):
	""" Defines the 2-D grid on which agents move
	"""
	def __init__(self, size):
		self.Size = size
		self.Ground = [[None for x in range(size)] for x in range(size)]
		# Caveat:  [ [None] * size] * size would be incorrect
		# as it would make shallow copies of the rows

	def toric(self, (x,y)):
		return ((x % self.Size, y % self.Size))
	
	def RandPlace(self, Agent):
		" places Agent at a random location "
		Pos = self.toric((random.randint(0, self.Size - 1), random.randint(0, self.Size - 1)))
		if self.Locate(Pos) == None:
			self.move(Agent,Pos)
			return Pos
		return self.RandPlace(Agent)	# lateral recursive call

	def move(self,Agent, Position):
		" places Agent at a specific location if that location is free "
		self.Clear(Agent.location)
		Pos1 = self.toric(Position)
		if self.Ground[Pos1[0]][Pos1[1]] is None:
			self.Ground[Pos1[0]][Pos1[1]] = Agent
			Agent.location = Pos1 + Agent.location[2:]
		return self.Ground[Pos1[0]][Pos1[1]]

	def divert(self, Agent, Position):
		" tries to move Agent to a free neighbouring cell "
		if self.move(Agent, Position) == Agent:
			return self.toric(Position)
		# recursive call
		return self.divert(Agent, random.choice(self.Neighbourhood(Position)[0:4]))

	def Locate(self, Pos):
		# returns whoever is at location Pos
		(x,y) = self.toric(Pos)
		return self.Ground[x][y]

	def Clear(self, Loc):
		if len(Loc) > 1:
			self.Ground[Loc[0]][Loc[1]] = None
		
	def Neighbourhood(self, (x,y)):
		" returns the list of neighbouring locations by increasing Manhattan distances "
		NbH1 = [(x-1,y),(x,y-1),(x+1,y),(x,y+1),
				(x-1,y-1),(x-1,y+1),(x+1,y-1),(x+1,y+1)]	  
		NbH = NbH1 + [(x-2,y),(x,y-2),(x+2,y),(x,y+2),
				(x-2,y-1),(x-2,y+1),(x+2,y-1),(x+2,y+1),
				(x-1,y-2),(x-1,y+2),(x+1,y-2),(x+1,y+2),
				(x-2,y-2),(x-2,y+2),(x+2,y-2),(x+2,y+2)]
		return [self.toric(L) for L in NbH]
	
	def Neighbours(self, Loc):
		" returns the list of neighbours within a 5x5 neighbourhood "
		return [self.Locate(L) for L in self.Neighbourhood(Loc) if self.Locate(L) is not None]

	def Consistency(self):
		" Checks consistency of agents' locations "
		for x in range(self.Size):
			for y in range(self.Size):
				a = self.Ground[x][y]
				if a is None:   continue
				if a.location[:2] != (x,y):
					print('Location Error in')
					print((x,y))
					print(a.location[:2])
		
################################
# Scenario class instance      #
################################

from Evolife.Scenarii.Default_Scenario import Default_Scenario
from Evolife.Tools.Tools import error


class Scenario(Default_Scenario):
	######################################
	# Most functions below overload some #
	# functions of Default_Scenario	  #
	######################################

	def initialization(self):
		self.Ground = Grid(self.Parameter('WDGridSize'))
		self.Parents = []	# stores couples that successfully met to procreate
		self.CurrentReproductionNumber = []
		self.MovMap = {0:(1,0), 1:(0,-1), 2:(-1,0), 3:(0,1)} # successive 90d rotations
		self.MapMov = {(1,0):0, (0,-1):1, (-1,0):2, (0,1):3} # absolute directions
		if self.Parameter('Compass'):
			self.TurnMap = {0:0, 1:1, 2:3, 3:2} # Absolute directions, with Gray code
		else:
			self.TurnMap = {0:0, 1:-1, 2:1, 3:2} # important to have a Gray code here: a U-turn requires more genetic change
		self.PopSize = 0

	def genemap(self):
		""" Defines the name of genes and their position on the DNA. (see Genetic_map.py)
			Females have a 5x5 vision field, in which they can perceive males
			(the closest if several are present) together with their orientation
			(there are thus 24 x 4 possibilities).
			From this, they utter a song chosen among four possible calls.
			The female part of the genome thus requires 192 bits to code for this behaviour.
			Males hear the call of the closest female if any
			(within a 5x5 range). They decide to move or turn accordingly.
			The male part of the genome thus requires only 8 bits for this mapping. 
		"""
		if self.Parameter('Compass'):
			return [('coding',8), ('decoding',48)]
		else:
			return [('coding',8), ('decoding',192)]

	def phenemap(self):
		""" Defines the set of non inheritable characteristics
		"""
		# Sex is considered a phenotypic characteristic !
		# This is convenient because sex is determined at birth
		# and is not inheritable
		return ['Sex', 'Direction', 'Penalty']

	def female(self, Agent):
		return Agent.Phene_relative_value('Sex') > 50

	def direction(self, Agent):
		# determines the current moving direction of an individual
		return Agent.Phene_value('Direction')

	def colour(self, Agent):
		if self.female(Agent):
			return 8
		else:
			return 7

	def paint(self, Agent, Colour = None):
		if Colour == None:
			Agent.location = Agent.location[0:2] + (self.colour(Agent),)
		else:
			Agent.location = Agent.location[0:2] + (Colour,)

	def behaviour(self, Best_Indiv, Avg_Indiv):
		" defines a phenotype for individual and returns it "

		#print reduce(lambda x,y: x+str(y), Avg_Indiv.get_DNA()[:60],'')
		Paths = []
		grid = self.Ground.Neighbourhood((3,3))
		# Entrance: [(direction, ways in)...]
		Entrance = [(self.MapMov[(1,0)],((1,5),(1,4),(1,3),(1,2),(1,1))),
					(self.MapMov[(0,1)],((1,1),(2,1),(3,1),(4,1),(5,1))),
					(self.MapMov[(-1,0)],((5,1),(5,2),(5,3),(5,4),(5,5))),
					(self.MapMov[(0,-1)],((1,5),(2,5),(3,5),(4,5),(5,5)))]
		for (FirstDir,Entries) in Entrance:
			for FirstPos in Entries:
				(Pos,Dir) = (FirstPos, FirstDir)
				try:
					Cell = grid.index(Pos)
				except ValueError:
					# maybe because restricted neighbourhood
					Pos = self.moving(Pos, Dir) # provisoire
					try:
						Cell = grid.index(Pos)
					except ValueError:
						# still not in the neighbourhood
						Paths.append([Pos])
						continue
				Path = [Pos]
				for ii in range(15):
					Dir = self.communication(Avg_Indiv, Avg_Indiv, Cell, Dir)
					Pos = self.moving(Pos, Dir)
					Path.append(Pos)
					try:
						Cell = grid.index(Pos)
					except ValueError:
						break
				Paths.append(Path)

		if Paths == None:	return None

		# Adapting Paths to display
		ScaleX = 8.3  #TODO
		ScaleY = 8.3
		RelOffsX = -0.16 
		RelOffsY = -0.16
		sh = 0.08	# shift to avoid overlapping curves
		transform = lambda P: ((RelOffsX + P[1])*ScaleX, (RelOffsY + P[0])*ScaleY)		
		Behaviour = []	# contains list of tailed blobs [(S1,(blobX,blobY,blobColour,blobSize,ToX,ToY,segmentColour,thickness)), (s2, (...)), ...]
		for P in range(5):
			LastStep = ( 0, 5 - P + sh*P)	# startpoint
			for (nro,step) in enumerate(Paths[P]):
				NewStep = (step[0] + sh*P, step[1] + sh*P)
				Behaviour.append(("S1_%d" % (nro+15*P), (transform(LastStep) + (3+P, 0) + transform(NewStep) + (3+P,3))))
				LastStep = NewStep

		for P in range(5):
			LastStep = (8.0 + P + sh*P, 0)	# startpoint
			for (nro,step) in enumerate(Paths[5+P]):
				NewStep = (step[0] + 7 + sh*P, step[1] + sh*P)
				Behaviour.append(("S2_%d" % (nro+15*P), (transform(LastStep) + (3+P, 0) + transform(NewStep) + (3+P,3))))
				LastStep = NewStep
		for P in range(5):
			LastStep = (13.0, 8 + P + sh*P)	# startpoint
			for (nro,step) in enumerate(Paths[10+P]):
				NewStep = (step[0] + 7 + sh*P, step[1] + 7 + sh*P)
				Behaviour.append(("S3_%d" % (nro+15*P), (transform(LastStep) + (3+P, 0) + transform(NewStep) + (3+P,3))))
				LastStep = NewStep
		for P in range(5):
			LastStep = (1 + P + sh*P, 13.)	# startpoint
			for (nro,step) in enumerate(Paths[15+P]):
				NewStep = (step[0] + sh*P, step[1] + 7+ sh*P)
				Behaviour.append(("S4_%d" % (nro+15*P), (transform(LastStep) + (3+P, 0) + transform(NewStep) + (3+P,3))))
				LastStep = NewStep

		return Behaviour
		

				
	def couples(self, members):
		""" Returns a set of couples that will beget newborns
		"""
		Amplification = self.Parameter('Selectivity')   # to accelerate evolution
		Couples = Amplification*self.Parents   # couples waiting for procreation
		self.CurrentReproductionNumber = self.CurrentReproductionNumber[-50:] + [len(self.Parents)]
		self.Parents = []
		return Couples
			
	def new_agent(self, child, parents):
		" initializes newborns "
		child.location = ()
		child.location = self.Ground.RandPlace(child)
		child.Phene_value('Direction',random.randint(0,3))
		child.Phene_value('Penalty',0)
		child.Phene_value('Sex', random.randint(1,100))
		self.paint(child)
		return True

	def remove_agent(self, Agent):
		" action to be performed when an agent dies "
		if Agent.location:	self.Ground.Clear(Agent.location[0:2])

	def update_positions(self, members, groupID):
		pass
	
	def communication(self, Male, Female, MaleRelativeLocation, MaleDirection):
		""" The song is emitted by the female, depending on the male's position
			and his direction. The male's next direction depends on the song.
		"""
		# Where to look in the female's DNA
		if self.Parameter('Compass'):
			# Female's DNA codes for Male's next absolute direction
			Locus = 8 + 2 * (MaleRelativeLocation)
		else:
			# Female's DNA codes for Male's change of direction
			Locus = 8 + 2 * (MaleRelativeLocation * 4 + MaleDirection)
		# Female sings, Male moves
##        Song = Female.read_DNA(Locus, Locus+2, coding = self.Parameter('Weighted'))
##        RelativeDirection = Male.read_DNA(2 * Song, 2 * Song + 2, coding = self.Parameter('Weighted'))
		FDNA = Female.get_DNA()
		MDNA = Male.get_DNA()
		Song = 2*FDNA[Locus] + FDNA[Locus+1]
		TurnCode = 2*MDNA[2*Song] + MDNA[2*Song+1]
##        if MaleRelativeLocation < 8:    # test with a restricted neighbouhood
##            return self.TurnMap[Song]%4 
##        else:
##            return MaleDirection    #test

		if self.Parameter('Compass'):
			# Female's DNA codes for Male's next absolute direction
			return self.TurnMap[TurnCode]%4
		else:
			# Female's DNA codes for Male's change of direction
			Turn = self.TurnMap[TurnCode]
			return (MaleDirection + Turn) % 4   # new absolute direction

		
	def decision(self, Male, Female):
		""" The male decides which direction to take depending on the female's song
		"""
		AbsoluteDirection = self.direction(Male) 
		try:
			# Relative position of the male (position are numbered by increasing Manhattan distance)
			Cell = self.Ground.Neighbourhood(Female.location[0:2]).index(Male.location[0:2])
		except ValueError:
			print(Male.location)
			print(Female.location)
			error("Ghost male")

		return self.communication(Male, Female, Cell, AbsoluteDirection)

	def life_game(self, members):
		""" gives every agent an opportunity to perform an action
			(moving if male, singing if female)
		"""
		self.PopSize = len(members)
		Beloved = []
		# self.Ground.Consistency()

		for Female in members:
			Female.score(self.Parameter('AgeMax')-Female.age,FlagSet=True)  # all individuals deteriorate
			if not self.female(Female):
				continue	# males wait for a song

			# locating the closest male
			if Female.location is not None:
				Suitors = [S for S in self.Ground.Neighbours(Female.location[0:2])
						   if not (self.female(S) or S in Beloved or S.Phene_value('Penalty')) ]
			else:	Suitors = []
			if Suitors == []:
				continue
			Male = Suitors[0] # the closest male is preferred
			Beloved.append(Male)

			NewDirection = self.decision(Male,Female)
			self.Move(Male, NewDirection)

		for Male in members:
			if self.female(Male) or Male in Beloved:
				continue
			# lonely males go straight most of the time
			self.Move(Male, self.direction(Male))

	def Move(self, Male, Direction):
		" Male moves and possibily mates "

		if Male.location is None:	return
		if random.randint(0,99) < self.Parameter('Noise'):
			Dir = random.randint(0,3)
		else:
			Dir = Direction
		OldPosition = Male.location[0:2]
		NewPosition = self.moving(Male.location, Dir)

		if Direction != Male.Phene_value('Direction'):
			Male.Phene_value('Penalty', 1)  # time needed to turn

		# storing Male's new direction
		Male.Phene_value('Direction', Dir)

		if Male.Phene_value('Penalty'):
			# Males changing direction are stuck for a while
			Male.Phene_value('Penalty', Male.Phene_value('Penalty')-1)
			return
		
		# actual movement
		Partner = self.Ground.Locate(NewPosition)	# Did Male bumb into someone ?
		if Partner is not None and self.female(Partner):
			# Reproduction takes place
			self.Parents.append((Male,Partner))	# the couple is added to the list of parents
			self.Ground.RandPlace(Male)			# both individuals are moved to a random place.
			self.Ground.RandPlace(Partner)
		else:
			self.Ground.divert(Male, NewPosition)	#	Male moves
		return
						
	def moving(self, OldPosition, AbsDirection):
		""" computes a new position from the direction of movement
		"""
		return (OldPosition[0] + self.MovMap[AbsDirection][0],
				OldPosition[1] + self.MovMap[AbsDirection][1])	  
				
						
	def display_(self):
		""" Defines what is to be displayed. 
		"""
		return [('white','Reproduction'), ('green2','PopSize')]
		
	def local_display(self,PlotNumber):
		" allows to diplay locally defined values "
		# sums the number of reproductions during the past moves
		if PlotNumber == 'Reproduction':
			return 100*sum(self.CurrentReproductionNumber,0.0)/max(len(self.CurrentReproductionNumber),1)
		elif PlotNumber == 'PopSize':
			return self.PopSize // 10

	def wallpaper(self, Window):
		" displays background image or colour when the window is created "
		# Possible windows are: 'Field', 'Curves', 'Genome', 'Log', 'Help', 'Trajectories', 'Network'
		if Window == 'Trajectories':	return 'Scenarii/WD.png'
		return Default_Scenario.wallpaper(self, Window)
	
	def default_view(self):	return ['Trajectories', 'Field']			

###############################
# Local Test                  #
###############################

if __name__ == "__main__":
	print(__doc__ + '\n')
	input('[Return]')
	
