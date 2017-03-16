#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################



##############################################################################
#  S_Coordination                                                            #
##############################################################################


""" EVOLIFE: Coordination Scenario
	In the coordination scenario, players have to do opposite actions
	to succeed, such as 'you pull, I push'. 
	Individuals are given the possibility to emit a binary or n-ary signal.
"""
	#=============================================================#
	#  HOW TO MODIFY A SCENARIO: read Default_Scenario.py		 #
	#=============================================================#


import sys
if __name__ == '__main__':  sys.path.append('../..')  # for tests

import random
from math import log, ceil

from Evolife.Tools.Tools import noise_add
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
		nb_signaux = self.Parameter('Nb_signaux')
		return [('signal',int(ceil(log(nb_signaux,2)))),('push_mask',nb_signaux)]

	def start_game(self, members):
		""" defines what to be done at the group level before interactions
			occur
		"""
		for m in members:
			m.score(0, FlagSet=True)	# resetting scores each year
		Default_Scenario.start_game(self, members)

	def interaction(self, indiv, Partner):

		def signal(indiv):
			return indiv.gene_value('signal')

		def pushes(indiv,signal):
			""" defines indiv's actual hunting behaviour depending on the signal emitted
				by the opponent
			"""
			return indiv.gene_value('push_mask') & (1 << signal)
		
		# individuals engage in the push-pull coordination game
		# implementing the payoff matrix
		if pushes(indiv,signal(Partner)):
			if not pushes(Partner, signal(indiv)):
				indiv.score(1)
				Partner.score(1)
		else:
			if pushes(Partner, signal(indiv)):
				indiv.score(1)
				Partner.score(1)

			

	def display_(self):
		""" Defines what is to be displayed. It offers the possibility
			of plotting the evolution through time of the best score,
			the average score, and the average value of the
			various genes defined on the DNA.
			It should return a list of pairs (C,X)
			where C is the curve colour and X can be
			'best', 'average', or any gene name as defined by genemap
		"""
	##	return [(2,'signal')]
		return [(2,'signal'),(3,'push_mask'),(4,'average')]
		



###############################
# Local Test                  #
###############################

if __name__ == "__main__":
	print(__doc__ + '\n')
	input('[Return]')
	
