#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################



##############################################################################
#  S_SocialClasses                                                           #
##############################################################################


"""		EVOLIFE: Emergence of social classes
		"The essential idea is to show how norms can emerge spontaneously at the social level from the decentralized interactions of many individuals that cumulate over time into a set of social expectations. Due to the self-reinforcing nature of the process, these expectations tend to perpetuate themselves for long periods of time, even though they may have arisen from purely random events and have no a priori justification." 
		( Axtell, Epstein & Young 2000 ) 
		http://teaching.dessalles.fr/ECS/docs/Axtell_Epstein_Young.pdf
"""
	#=============================================================#
	#  HOW TO MODIFY A SCENARIO: read Default_Scenario.py		 #
	#=============================================================#


import sys
if __name__ == '__main__':  sys.path.append('../..')  # for tests

import random

from Evolife.Tools.Tools import percent, noise_mult, error
from Evolife.Scenarii.Default_Scenario import Default_Scenario

######################################
# specific variables and functions   #
######################################

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
		return ['Combative', 'Submissive']

	def phenemap(self):
		""" Defines the set of non inheritable characteristics
		"""
		return ['Badge', 'ActionSame', 'ActionOther']  

	def Same(self, Indiv1, Indiv2):
		"""	Both individuals wear the same badge
		"""
		return (Indiv1.Phene_value('Badge') - 50) * (Indiv2.Phene_value('Badge') - 50) >= 0
		
	def prepare(self, Indiv):
		""" defines what is to be done at the individual level before interactions
			occur - Used in 'start_game'
		"""
		MemorySame = 0.0
		MemoryOther = 0.0
		NumberSame = 0
		NumberOther = 0
		# print Indiv.gurus
		for (Rank, PreviousPartner) in enumerate(Indiv.gurus.names()):
			if Indiv.gurus.size() - Rank > self.Parameter('MemorySpan'):
				Indiv.quit_(PreviousPartner)
				continue
			if self.Same(Indiv, PreviousPartner):
				NumberSame += 1
				MemorySame += Indiv.gurus.performance(PreviousPartner)
			else:
				NumberOther += 1
				MemoryOther += Indiv.gurus.performance(PreviousPartner)
				
		# print Indiv, Indiv.gurus
		
		# Scores are reset
		Indiv.score(0, FlagSet=True)	
			
		if NumberSame:	ActionSame = MemorySame/NumberSame
		else:			ActionSame = random.randint(0,100)				
		if NumberOther:	ActionOther = MemoryOther/NumberOther
		else:			ActionOther = random.randint(0,100)
		
		#Conservatism
		Conservatism = 1
		ActionSame = ((Conservatism - 1) * Indiv.Phene_value('ActionSame') + ActionSame) / Conservatism
		ActionOther = ((Conservatism - 1) * Indiv.Phene_value('ActionOther') + ActionOther) / Conservatism
		Indiv.Phene_value('ActionSame', int(ActionSame))
		Indiv.Phene_value('ActionOther', int(ActionOther))
		
	def strategy(self, Indiv, PartnerExpectedAction):
		if PartnerExpectedAction > 50 + self.Parameter('SecurityMargin'):	# agressive partner
			if random.randint(0,100) < Indiv.gene_relative_value('Submissive'):
				 # return PartnerExpectedAction
				 return 30
			else:
				# return 100 - PartnerExpectedAction - self.Parameter('SecurityMargin')
				return 50
		elif abs(PartnerExpectedAction - 50) <= self.Parameter('SecurityMargin'):	# cooperative partner
			# if random.randint(0,100) < Indiv.gene_relative_value('Cooperative'):
				return PartnerExpectedAction
				# return 50
			# else:
				# return 100 - PartnerExpectedAction - self.Parameter('SecurityMargin')
				return 50
		else:	# partner expected to be submissive
			if random.randint(0,100) < Indiv.gene_relative_value('Combative'):
				 # return PartnerExpectedAction
				 return 70
			else:
				# return 100 - PartnerExpectedAction - self.Parameter('SecurityMargin')
				return 50
			
		# return 30 * (PartnerExpectedAction > 60) + 70 * (PartnerExpectedAction < 40) + 50 * ((PartnerExpectedAction <= 60) and (PartnerExpectedAction >= 40)) + random.randint(0,self.Parameter('Noise'))
		
	def interaction(self, Indiv, Partner):
		""" Individual and partner play the ultimatum game
		"""

		if self.Same(Indiv, Partner):
			IndivAction = self.strategy(Indiv, Indiv.Phene_value('ActionSame'))
			PartnerAction = self.strategy(Partner, Partner.Phene_value('ActionSame'))
		else:
			IndivAction = self.strategy(Indiv, Indiv.Phene_value('ActionOther'))
			PartnerAction = self.strategy(Partner, Partner.Phene_value('ActionOther'))

		Indiv.new_friend(Partner, PartnerAction)
		Partner.new_friend(Indiv, IndivAction)
		if IndivAction + PartnerAction <= 100:
			Indiv.score(IndivAction) ** 3
			Partner.score(PartnerAction) ** 3
			
		
	def update_positions(self, members, start_location):
		""" locates individuals on an 2D space
		"""
		# sorting individuals by gene value
		# duplicate = members[:]
		# duplicate.sort(key=lambda x: x.gene_value('Cooperativeness'))
		# for m in enumerate(duplicate):
			# m[1].location = (start_location + m[0], m[1].gene_relative_value('Exploration'))
		for m in members:
			colour = 4 * (m.Phene_value('Badge') > 50) + 3 * (m.Phene_value('Badge') <= 50)
			# m.location = (m.gene_relative_value('Combative'), m.gene_relative_value('Cooperative'), colour)
			Noise = random.randint(0, self.Parameter('Noise'))
			m.location = (self.strategy(m, m.Phene_value('ActionSame'))+random.randint(-1,1)*Noise, self.strategy(m, m.Phene_value('ActionOther'))+random.randint(-1,1)*Noise, colour)



###############################
# Local Test                  #
###############################

if __name__ == "__main__":
	print(__doc__ + '\n')
	input('[Return]')
	
