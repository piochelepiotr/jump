#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################



""" EVOLIFE: Gazelle Scenario

Imagine two species, call them gazelles and lions. Gazelles have the genetically choice to invest energy in jumping vertically when lions approach. Of course, this somewhat reduces their ability to run away in case of pursuit. If lions prefer to chase non jumping gazelles, and poorly jumping ones among those who are jumping, show that investment in jumping evolves, at least for healthy individuals.	

	
"""

	#=============================================================#
	#  HOW TO MODIFY A SCENARIO: read Default_Scenario.py		 #
	#=============================================================#

from __future__ import print_function


import random
from math import sqrt

import sys
if __name__ == '__main__':  sys.path.append('../..')  # for tests

from Evolife.Scenarii.Default_Scenario import Default_Scenario
from Evolife.Tools.Tools import error, noise_add, percent, chances, decrease


######################################
# specific variables and functions   #
######################################


class Scenario(Default_Scenario):

	######################################
	# All functions in Default_Scenario  #
	# can be overloaded				  #
	######################################


	
	def genemap(self):
		""" Defines the name of genes and their position on the DNA.
		Accepted syntax:
		['genename1', 'genename2',...]:   lengths and coding are retrieved from configuration
		[('genename1', 8), ('genename2', 4),...]:   numbers give lengths in bits; coding is retrieved from configuration
		[('genename1', 8, 'Weighted'), ('genename2', 4, 'Unweighted'),...]:	coding can be 'Weighted', 'Unweighted', 'Gray', 'NoCoding'
		"""
		return ['Gazelle Threshold', 'Lion Threshold'] 	

	def phenemap(self):
		""" Defines the set of non inheritable characteristics
		"""
		# Elements in phenemap are integers between 0 and 100 and are initialized randomly
		# Lions and gazelles belong to the same species (!)
		# Their nature is decided at birth by the Phene 'Lion'
		return ['Lion', 'Gazelle Strength', 'ChaseNumber']

	def gazelle(self, indiv):
		" decides whether an individual is a gazelle or a lion "
		if indiv:
			return indiv.Phene_relative_value('Lion') < self.Parameter('GazelleToLionRatio')	# typically more gazelles than lions
		return False

	def lion(self, indiv):	return not self.gazelle(indiv)
	
	
	def initialization(self):
		self.Jumps = 0 	# unused
		self.Gazelles = []
		self.Lions = []
		self.GazelleAsset = 0
		self.PreyCost = 1	
		self.HunterReward = 1
		

	def census(self, members):	
		self.Gazelles = [g for g in members if self.gazelle(g)]
		self.Lions = [l for l in members if self.lion(l)]
		
	def start_game(self, members):
		""" defines what is to be done at the group level each year
			before interactions occur - Used in 'life_game'
		"""
		if self.Parameter('Selectivity') == 0:	error('Selection method should be "Selectivity"')
		self.census(members)
		for indiv in members:	self.prepare(indiv)
		# print('>',len(members), len(self.Gazelles), len(self.Lions), len(self.Gazelles)/len(members))


	def prepare(self, indiv):
		""" defines what is to be done at the individual level before interactions occur
		"""
		# set initial scores 
		if self.lion(indiv):	
			indiv.Phene_value('ChaseNumber', max(1, self.Parameter('Rounds') * self.Parameter('HuntingRatio') / 100.0))
			indiv.score(0, FlagSet=True)
		else:	# gazelle
			# gazelles with negative scores will be considered dead
			# indiv.score(self.PreyCost * self.Parameter('Rounds'), FlagSet=True)
			indiv.score(self.GazelleAsset, FlagSet=True)
			pass
			

	def partner(self, indiv, members):
		""" Decides whom indiv will interact with - Used in 'life_game'
		"""
		# this version makes sure that gazelles interact only with lions and vice versa
		if self.lion(indiv):
			if self.Gazelles:	return random.choice(self.Gazelles)
			else:			return None
		return None
		
		
	def jump(self, gazelle):
		" Gazelles show their strength only if it exceeds its signalling threshold "
		if gazelle.Phene_relative_value('Gazelle Strength') > gazelle.gene_relative_value('Gazelle Threshold'): 
			# return sqrt(1000 * sqrt(gazelle.Phene_relative_value('Gazelle Strength')))
			return gazelle.Phene_relative_value('Gazelle Strength')
			# return 40 * (gazelle.Phene_relative_value('Gazelle Strength') > 70) + 20
		return 0
	
	def interaction(self, indiv1, indiv2):

		# print('.', end="")
		if indiv1 is None or indiv2 is None:	return
		if self.gazelle(indiv1):	(gazelle, lion) = (indiv1, indiv2)
		else:						(gazelle, lion) = (indiv2, indiv1)

		# print(lion.Phene_value('ChaseNumber') , end=" ")
		if lion.Phene_value('ChaseNumber') <= 0:	return		# lion has exhausted all its opportunities
		if gazelle.score() < 0:	return	# the gazelle is dead
		
		# A lion is approaching - The gazelle decides whether it should jump
		GazelleCurrentStrength = gazelle.Phene_relative_value('Gazelle Strength')
		GazelleJump = self.jump(gazelle)

		# the gazelle pays a temporary price
		if GazelleJump:	GazelleCurrentStrength -= self.Parameter('JumpEnergy')
		
		# The lion makes its own decision
		chase = (GazelleJump < lion.gene_relative_value('Lion Threshold'))
		# if GazelleJump and chase:
			# print(lion.gene_relative_value('Lion Threshold') - GazelleJump, end=" ")
		
		if chase:	# the lion is not impressed - the hunt begins
			# print(lion.Phene_value('ChaseNumber'), end=" -> ")
			lion.Phene_value('ChaseNumber', lion.Phene_value('ChaseNumber')-1)	# count the chase
			# print(lion.Phene_value('ChaseNumber'))
			# print('>',GazelleCurrentStrength, end="")
			Vulnerability = self.Parameter('Vulnerability')	# Slope of exposure decrease with strength
			Exposure = decrease(max(0,GazelleCurrentStrength), 100, Vulnerability)/decrease(0, 100, Vulnerability)
			if (GazelleCurrentStrength > 0) and (random.random() > Exposure):
				# Unsuccessful hunt - Lion gets penalized
				# print('-', end=" ", flush=True)
				# print(GazelleCurrentStrength)
				# lion.score(-self.Parameter('LostPreyCost'))
				pass
			else:	# Successful hunt
				# print('+', end=" ", flush=True)
				# print('+', GazelleJump, '%0.01f' % lion.gene_relative_value('Lion Threshold'))
				lion.score(self.HunterReward)
				gazelle.score(-self.PreyCost)
			# print("%.01d-%.01d" % (gazelle.score(), lion.score()))

	def end_game(self, members):
		""" defines what to do  at the group level once all interactions
			have occurred - Used in 'life_game'
		"""
		for m in members:
			if m.score() < 0: self.LifePoints = -1	# individual is dead
		
	def couples(self, RankedMembers):						
		"""	Lions and gazelles should not attempt to mate
			(because the selection of both subspecies operates on different scales)
		"""
		if len(RankedMembers) == 0:	return []
		livingGazelles = [G for G in RankedMembers if self.gazelle(G) and G.score() >= 0]
		lions = [L for L in RankedMembers if self.lion(L)]
		# print([G.score() for G in gazelles])
		# print([L.score() for L in lions])
		Desired_ratio = self.Parameter('GazelleToLionRatio')
		# global number of children
		nb_children = chances(self.Parameter('ReproductionRate') / 100.0, len(livingGazelles) + len(lions))
		# Distribution:
		nb_gazelle_target =  int(round(Desired_ratio * nb_children / 100.0))
		nb_lion_target =  1 + int(round((100 - Desired_ratio) * nb_children / 100.0))
		# Correction
		nb_gazelle_target += len(lions) * Desired_ratio / (100.0-Desired_ratio) - len(livingGazelles)
		# print(len(RankedMembers), len(livingGazelles), Desired_ratio, nb_gazelle_target, nb_lion_target)
		Couples = Default_Scenario.couples(self, livingGazelles, int(nb_gazelle_target)) + Default_Scenario.couples(self, lions, int(nb_lion_target))
		# print(len(livingGazelles), len(lions))
		# print(["%d%d (%.01f/%0.1f)" % (1*self.gazelle(C[0]),1*self.gazelle(C[1]), C[0].score(), C[1].score(), ) for C in Couples], end="\n")
		# print()
		return Couples
					
	def new_agent(self, child, parents):	
		" make sure that lions make lions and gazelles make gazelles "
		if parents:
			# print("%d%d" % (1*self.gazelle(parents[0]),1*self.gazelle(parents[1])), end="")
			if self.gazelle(parents[0]):	child.Phene_value('Lion', 0)
			else:							child.Phene_value('Lion', 100)
		return True

	
	def update_positions(self, members, groupLocation):
		" Allows to define spatial coordinates for individuals. "
		self.census(members)
		for m in self.Gazelles:
			gcolour = 'blue' if m.score() >= 0 else 'lightblue'
			m.location = (groupLocation + m.Phene_relative_value('Gazelle Strength'), 
					1+self.jump(m), gcolour, 6)		# gazelles in blue
		if self.Lions:
			for m in enumerate(self.Lions):
				m[1].location = (groupLocation + 100 + m[0], 
					m[1].gene_relative_value('Lion Threshold'), 'red', 6)	# lions in red
				# print(m[1].Phene_value('ChaseNumber'), '\t', m[1].score())
			# print(len(members), len(self.Gazelles), len(self.Lions), len(self.Gazelles)/len(members))
			# print()

	def default_view(self):	return ['Field', 'Legend']
	
	def legends(self):
		return "<u>Field window</u><p>Blue dots: gazelles ranked by strength - lightblue dots: dead gazelles - y-axis: jump<br>Red dots: lions - y-axis: lion threshold<P>" \
				+ Default_Scenario.legends(self)
	
	def wallpaper(self, Window):
		" displays background image or colour when the window is created "
		# Possible windows are: 'Field', 'Curves', 'Genome', 'Log', 'Help', 'Trajectories', 'Network'
		if Window == 'Field':	return 'Scenarii/lion_gazelle_bkg.jpg'
		return Default_Scenario.wallpaper(self, Window)
		
	def local_display(self, ToBeDisplayed):
		" allows to diplay locally defined values "
		if ToBeDisplayed == 'Jumps':
			return self.Jumps
		elif ToBeDisplayed == 'GazelleAvgThreshold':
			if self.Gazelles:
				return sum([G.gene_relative_value('Gazelle Threshold') for G in self.Gazelles])/len(self.Gazelles)
			return 0
		elif ToBeDisplayed == 'LionAvgThreshold':
			if self.Lions:
				return sum([L.gene_relative_value('Lion Threshold') for L in self.Lions])/len(self.Lions)
			return 0
		elif ToBeDisplayed == 'LionAvgScore':
			if self.Lions:
				return sum([(100.0 * L.score())/(self.HunterReward * max(1, self.Parameter('Rounds') * self.Parameter('HuntingRatio') / 100.0)) for L in self.Lions])/len(self.Lions)
			return 0
		elif ToBeDisplayed == '#Lions':
			return len(self.Lions)
		return None	
					
	def display_(self):
		""" Defines what is to be displayed. 
			It should return a list of pairs (C,X)
			where C is the curve colour and X can be
			'best', 'average', 'n' (where n is any string processed by local_display, e.g. 'Jumps'),
			any gene name defined in genemap or any phene defined in phenemap
		"""
		return [('blue', 'GazelleAvgThreshold', "Gazelles' average threshold"),  
				('red', 'LionAvgThreshold', "Lions' average threshold"), 
				('yellow', 'LionAvgScore', "Lions' average score")]
		

		
###############################
# Local Test                  #
###############################

if __name__ == "__main__":
	print(__doc__ + '\n')
	SB = Scenario()
	input('[Return]')
	
