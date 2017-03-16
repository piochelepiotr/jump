#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################


##############################################################################
#  S_HeteroclineCycle                                                        #
##############################################################################

						
""" EVOLIFE: HeteroclineCycle Scenario:

		Alan FERREIROS (Telecom Paristech)

	Collective Intelligence Projet
	Athens course at Mars/2011
	Professor : Jean-Louis DESSALLES

	 We suppose that we observe three species, such as bacteria in the gut.
	 Suppose that in the absence of the third species, species 2 dominates 1,
	 3 dominates 2 and 1, in turn, dominates 3. For example, species 2
	 develops both a substance that is poisonous for 1 and a substance
	 that makes itself immune to the poison. Species 3 develops the antidote
	 but avoids the burden of synthesizing the poison. Species 1 devotes no
	 energy to synthesizing either the poison or the antidote.

	 The purpose of the study is to observe the dynamics of the three species.
	 Some reasonable diffusion delays, possibly implemented through spatial
	 diffusion, might be necessary for the phenomenon to occur.

"""

	##############################################
	#  Modified by JL Dessalles - 11.2013		 #
	##############################################


import sys
if __name__ == '__main__':  sys.path.append('../..')  # for tests

######################################
# specific variables and functions   #
######################################

import random
from Evolife.Scenarii.Default_Scenario import Default_Scenario
from Evolife.Tools.Tools import percent


class Scenario(Default_Scenario):

	######################################
	# Most functions below overload some #
	# functions of Default_Scenario	  #
	######################################

	def genemap(self):
		""" Defines the name of genes and their position on the DNA.
		Accepted syntax:
		['genename1', 'genename2',...]:   lengths and coding are retrieved from configuration
		[('genename1', 8), ('genename2', 4),...]:   numbers give lengths in bits; coding is retrieved from configuration
		[('genename1', 8, 'Weighted'), ('genename2', 4, 'Unweighted'),...]:	coding can be 'Weighted', 'Unweighted', 'Gray', 'NoCoding'
		"""
		return [('Species',3)]	

	def Species(self,indiv):
		""" 
			A = no poison, no antidote
q			B = poison and antidote
			C = no poison but has antidote
			D = this species cannot live

			In this model, each bacteria can be described by two possible triples
			that can be changed one for the other by a single mutation.
			It can be noticed that the probability of mutating from one species to another
			will be always the same.
			
			A  101  5
			A' 001  1
			B  000  0
			B' 010  2
			C  110  6
			C' 111  7
		"""
		a = indiv.gene_value('Species')
		if a == 5 or a == 1:	return 'A'
		elif a == 0 or a == 2:  return 'B'
		elif a == 6 or a == 7:  return 'C'
		else:				   return 'D'

	def initialization(self):
		self.Pollution = 0 # stores the quantity of poison in the enviroment
		self.InitPollution = 0 # stores the initial quantity of poison in the enviroment
		self.TotalA = 0   # total number of individuals A (used to display on the graph)
		self.TotalB = 0   # total number of individuals B (used to display on the graph)
		self.TotalC = 0   # total number of individuals C (used to display on the graph)

	def start_game(self, members):
		""" defines what is to be done at the group level before interactions
			occur - Used in 'life_game'
		"""
		for indiv in members:
			# set offset values
			indiv.score(self.Parameter('EmittedPoison') * len(members), FlagSet=True)
			if self.Species(indiv) == 'B':
				# this individual polutes the enviroment with poison
				self.Pollution += self.Parameter('EmittedPoison')
				indiv.score(-self.Parameter('PoisonCost'),FlagSet=False)
		self.InitPollution = self.Pollution
		Default_Scenario.start_game(self, members)
		
	def evaluation(self, indiv):
		" individuals pay the price for antidotes or pollution "

		# amount of poison to be absorbed
		# absorbs only a fraction of all the pollution of the enviroment
		poison = min(self.Parameter('EmittedPoison'), self.Pollution * self.Parameter('Absorption') / 1000.0)
		# poison = percent(poison * random.randint(1,100))

		Type = self.Species(indiv)
		if Type == 'D':
			indiv.score(-1, FlagSet=True)	# the individual will be eliminated
		elif Type ==  'A':
			# the A ebdures the damage
			indiv.score(-poison,FlagSet=False)
			# this individual absorbs the pollution
			self.Pollution -= poison
		else:
			# B and C pay the price for antidote
			indiv.score(-self.Parameter('AntidoteCost'),FlagSet=False)
			# this individual absorbs the pollution, even if it's not affected
			self.Pollution -= poison

		# update enviroment's pollution
		if self.Pollution < 0:	self.Pollution = 0
				
	def end_game(self,members):
		self.TotalA = self.TotalB = self.TotalC = 0
		for indiv in members:
			Type = self.Species(indiv)
			if   Type == 'A':	self.TotalA += 1
			elif Type == 'B':	self.TotalB += 1
			elif Type == 'C':	self.TotalC += 1
		
	def display_(self):
		disp = [('black','Pollution')]		
		disp +=  [('white','TotalA')] 
		disp += [('red','TotalB')] 
		disp += [('blue','TotalC')] 

		return disp		

	def local_display(self,VariableID):
		if VariableID == 'Pollution':
			try:
				return self.Pollution / self.Parameter('EmittedPoison')
			except ZeroDivisionError: return 1
		elif VariableID == 'TotalA':
			return self.TotalA
		elif VariableID == 'TotalB':
			return self.TotalB
		elif VariableID == 'TotalC':
			return self.TotalC
		return 0

	def default_view(self):	return ['Genomes']		

###############################
# Local Test                  #
###############################

if __name__ == "__main__":
	print(__doc__ + '\n')
	input('[Return]')
	
