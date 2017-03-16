#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################

##############################################################################
# Cocktail Party                                                             #
##############################################################################


""" Emergence of noise level and of discussion group at a 'cocktail party':
Individuals must talk louder to be heard, and may move to smaller discussion groups.
"""

import sys
sys.path.append('..')
sys.path.append('../../..')

import Evolife.Ecology.Observer				as EO
import Evolife.Scenarii.Parameters 			as EPar
import Evolife.QtGraphics.Evolife_Window 	as EW
import Landscapes

from Evolife.Tools.Tools import boost
print(boost())   # A technical trick that sometimes provides impressive speeding up

	
import random
import math

# global functions
#	Sound level (voice) is displayed in blue shades
#	Noise level (due to others' voices) is displayed in red shades
def soundToColour(SoundLevel):	return 45-int(10*SoundLevel/101.0)	# 10 blue shades
def ColourToSound(Colour):		return int(((21-Colour)*100)/11)
def noiseToColour(NoiseLevel):	
	if NoiseLevel > 0.01:	return 33-int(8*NoiseLevel/101.0)	# 8 red shades
	else:	return 2	# white colour == invisible


		
class LandCell(Landscapes.LandCell):
	" Defines what is stored at a given location "

	# Cell content is defined as a couple  (VoiceLevel, NoiseLevel)

	def __init__(self):
		Landscapes.LandCell.__init__(self, (0, 0), VoidCell=(0, 0))

	def free(self):	return (self.Content()[0] == 0)

	# def Update(self):
		# self.Present = self.Future	# erases history
		# return self.Present[0] == 0
		
	def activated(self, Future=False):
		" tells whether a cell is active "
		return self.Content(Future=Future)[0] > 0

		
class Landscape(Landscapes.Landscape):
	" Defines a 2D square grid "

	def __init__(self, Size):
		Landscapes.Landscape.__init__(self, Width=Size, CellType=LandCell)	# calls local LandCell definition

	def randomPosition(self):
		" picks an element of the grid with no 'Content' in it "
		for ii in range(10):
			Row = random.randint(0,self.Size-1)
			Col = random.randint(0,self.Size-1)
			Cell = self.Ground[Col][Row]
			if Cell.free():	return (Col, Row)
			# print 'Cell at %d,%d is not free' % (Col, Row), Cell.Content()
		return None

	def attenuation(self, Level0, Pos0, Pos1):
		" Computes how noise emitted at Pos0 is perceived from a distance, at Pos1 "
		(sx, sy) = self.segment(Pos0, Pos1) 	# computes the shorter segment between the two position on the tore
		distance = sx + sy	# Manhattan distance
		if distance:
			# Level = (Level0 * Influence)/100 / math.log(1+distance,10)
			Level = (Level0 * Gbl.Parameter('Influence'))/100.0 / distance
		else:	Level = 0 # one is not noisy to oneself
		# print Level0, 'gives', int(Level), 'at distance', distance,
		return int(Level)
		
	def activate(self, Pos0):
		" Cell located at position 'Pos0' has been modified and now produces its effect on neighbouring cells "
		# print ' ',Pos0, self.Cell(Pos0)
		Voice = self.Cell(Pos0).Content()[0]
		InfluenceRadius = int(Gbl.Parameter('Influence')*Voice)//100	# distance at which maximal noisesource (100) is attenuated to 1
		# print 'radius around', Pos0, '= %d for Voice %d' % (InfluenceRadius, Voice)
		InfluenceRadius = min(InfluenceRadius, Gbl.Parameter('LandSize') // 2 - 1)
		for Pos1 in self.neighbours(Pos0, InfluenceRadius):
			NoiseDifference = self.attenuation(Voice, Pos0, Pos1)
			(Voice1, Noise1) = self.Content(Pos1)	# current values
			# print Pos1, 'goes from %d to %d' % (Noise1, Noise1+NoiseDifference)
			self.Modify(Pos1, (Voice1, min(100, Noise1+NoiseDifference)))
						
	def noiseLevel(self, Location):	############ unused
		" computes the cumulative sound contribution of all sound sources "
		# sound is supposed to decrease proportionnally to the inverse of distance (true in dB)
		# Manhattan distance is considered
		(x,y) = Location
		Noise = 0
		# for ((Col,Row), Cell) in self.travel():	# too slow to embed iterators
		for Row in range(self.Size):
			for Col in range(self.Size):
				Cell = self.Ground[Col][Row]
				if Cell.Content() and Cell.Content()[0]:
					Noise += self.attenuation(Cell.Content()[0], (Col, Row), (x,y))
		return min(Noise, 100)
						
	def noiseDecay(self):
		" noise decays with time "
		for (Position, Cell) in self.travel():	
			Cell.setContent((Cell.Content()[0], Cell.Content()[1]*(100 - Gbl.Parameter('Attenuation'))/100.0))
			
	def noiseClean(self):
		" erase noise everywhere "
		for (Position, Cell) in self.travel():	
			Cell.setContent((Cell.Content()[0], 0))
				
class Individual:
	""" Defines individual agents
	"""
	def __init__(self, Scenario, ID=None):
		self.Scenario = Scenario
		self.ID = ID
		self.location = None
		self.VoiceLevel = self.Scenario.Parameter('SNR')	# current sound level at which the individual is speaking
		self.Colour = soundToColour(self.VoiceLevel)	# colour reveals voice level
		# print 'creating', self.ID
		self.moves()	# gets a location
	
	def locate(self, NewPosition):
		" place individual at a specific location on the ground "
		# print 'locating', self, 'to', NewPosition
		(Voice, Noise) = Land.Content(NewPosition)
		if not Land.Modify(NewPosition, (self.VoiceLevel, Noise)): # new position on Land
			# print Land.Ground[NewPosition[0]][NewPosition[1]].Content()
			return False		 # NewPosition is not available  
		if self.location and (NewPosition != self.location):
			# erasing previous position on Land
			(Voice, Noise) = Land.Content(self.location)	# old location must be erased
			if not Land.Modify(self.location, (0, Noise)):
				print('Error, agent %s badly placed' % self.ID)
		self.location = NewPosition
		Observer.record((self.ID, self.location + (self.Colour, self.Scenario.Parameter('DotSize')))) # for ongoing display
		return True

	def erase(self):
		" erase individual from the ground "
		# print 'erasing', self
		if self.location:
			(Voice, Noise) = Land.Content(self.location)
			if not Land.Modify(self.location, (0, Noise)):	# erase on Land
				print('Error, agent %s was badly placed' % self.ID, self.location)
			# sending negative colour to display to erase the agent
			# Observer.record((self.ID, self.location + (-self.Colour, self.Scenario.Parameter('DotSize'))))

	def soundChange(self, VoiceLevel):
		" changing voice level "
		if VoiceLevel != self.VoiceLevel:
			# print 'changing voice level of %s from %d to %d' % (self, self.VoiceLevel, VoiceLevel)
			self.VoiceLevel = VoiceLevel
			# self.erase()	# moves away from Land
			self.Colour = soundToColour(VoiceLevel)
			# print self
			return self.locate(self.location)	# let Land know about the new voice
		return False

	def voiceUpdate(self):
		" Computes voice level to speak above noise "
		if self.location:
			oldLevel = self.VoiceLevel
			# Newlevel = min(100, Land.noiseLevel(self.location, self.Scenario.Parameter('Influence')) + self.Scenario.Parameter('SNR'))
			Newlevel = min(100, Land.Content(self.location)[1] + self.Scenario.Parameter('SNR'))
			if not self.soundChange(Newlevel) and Newlevel != oldLevel:
				print('Error: voice level change impossible for %s from %d to %d' % (self, oldLevel, Newlevel))
				return False
			return (Newlevel != oldLevel)
	
	def decisionToMove(self):
		# to be rewritten
		if self.location is None:	return False # may happen if there is no room left	
		return False
	
	def moves(self, Position=None):
		# print 'moving', self
		if Position:
			return self.locate(Position)
		else:
			# pick a random location and go there
			for ii in range(10): # 10 chances to find a free location
				Landing = Land.randomPosition()
				if Landing and self.locate(Landing):
					return True
			# print "Unable to move to", Position,
			return False

	def dies(self):
		" get off from the Land when dying "
		self.erase()
		
	def __repr__(self):
		" string representation of an individual "
		return "(%s,%s,%d) --> " % (self.ID, self.Colour, self.VoiceLevel) + str(self.location)

	
class Population:
	" defines the population of agents "
	
	def __init__(self, Scenario, Observer):
		" creates a population of agents "
		self.Scenario = Scenario
		self.Observer = Observer
		self.popSize = self.Scenario.Parameter('PopulationSize')
		print("population size: %d" % self.popSize)
		self.CallsSinceLastChange = 0  # counts the number of times agents were proposed to move since last actual move
		self.Pop = []		# list of agents
		Land.update()		# update noise
		self.Voices = dict()
			

	def create_agent(self):
		if len(self.Pop) < self.popSize:
			# calling local class 'Individual'
			Indiv = Individual(self.Scenario, ID=len(self.Pop))	# call to local class 'Individual'
			# Individual creation may fail if there is no room available
			if Indiv.location is not None:	
				self.Pop.append(Indiv)
				self.Voices[Indiv.ID] = 0
			
	def One_Decision(self):
		""" This function is repeatedly called by the simulation thread.
			One agent is randomly chosen and decides what it does
		"""

		self.Observer.season()	# increments StepId
		self.year = self.Observer.StepId	# each agent is selected once a year on average

		self.create_agent()	# creates agents while population size is not reached
		# agent = random.choice(self.Pop)	# agent who will play the game	
		self.CallsSinceLastChange += 1
		for agent in self.Pop:
			self.Voices[agent.ID] = agent.VoiceLevel
			if agent.voiceUpdate():	
				# Voice level has changed
				self.CallsSinceLastChange = 0
		# print self.Voices.values()
		
		if self.Observer.Visible():
			if len(self.Voices):
				VoiceLevel = sum(self.Voices.values()) / float(len(self.Voices))
				Observer.curve('Voice', VoiceLevel)
			
		if self.CallsSinceLastChange > 40:
			self.CallsSinceLastChange = 0
			return False	# situation is probably stable

		Land.noiseClean()	# erase previous noise
		Land.activation()	# compute new noise
		Land.update()		# update noise

		NoiseDisplay = max(self.Observer.DispPeriod, self.Scenario.Parameter('NoiseDisplay'))
		if  NoiseDisplay and (self.year % NoiseDisplay) == 0:
			for (Position, Cell) in Land.travel():
				# displaying noise
				Observer.record(('C%d_%d' % Position, Position + (noiseToColour(Cell.Content()[1]), 4))) 
			# redisplaying agents
			for Indiv in self.Pop:
				# negative colour deletes the graphic avatar
				Observer.record((Indiv.ID, Indiv.location + (-Indiv.Colour, self.Scenario.Parameter('DotSize'))))	
				# recreate the avatar
				Observer.record((Indiv.ID, Indiv.location + (Indiv.Colour, self.Scenario.Parameter('DotSize'))))	

		# Selecting one agent that is allowed to move
		# Uncomment the following line to see individuals moving
		# if random.randint(1,100) < 4:	random.choice(self.Pop).moves()
			  
		return True
			


if __name__ == "__main__":
	print(__doc__)

	
	#############################
	# Global objects			#
	#############################
	Gbl = EPar.Parameters(CfgFile='_Params.evo')
	Observer = EO.Experiment_Observer(Gbl)	  # Observer contains statistics
	Observer.curve('Voice', 0, 'blue', Legend='Average Voice level')

	Land = Landscape(Gbl.Parameter('LandSize'))	  # 2D square grid
	# Land.setAdmissible(range(101))	# sound levels
	Pop = Population(Gbl, Observer)   
	
	# Observer.recordInfo('Background', 'white')
	Observer.recordInfo('FieldWallpaper', 'white')
	Observer.record(('dummy',(100, 100, 'white', 0)))	# to set the scale
	
	EW.Start(Pop.One_Decision, Observer, Capabilities='RPC')

	print("Bye.......")
	
__author__ = 'Dessalles'
