#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################



##############################################################################
#  S_GreenBeard                                                              #
##############################################################################


						
""" EVOLIFE: GreenBeard Scenario:
	This small experiment was proposed in Richard Dawkins's book
	*The selfish gene*. It shows how some interesting coupling
	between genes may emerge in a population.
	Suppose a given gene has two effects on its carriers:
	(1) they get a conspicuous characteristic, like a green beard;
	(2) they tend to behave altruistically toward green-bearded individuals.
	Such a gene is expected to invade the population, whereas its supposed
	allele (no green beard + no altruism) tends to disappear. 
	However, as soon as the gene gets split in two genes with their own alleles
	(green beard vs. no green beard, and altruism toward green beard vs.
	no altruism) then altruism disappears. 
"""
	#=============================================================#
	#  HOW TO MODIFY A SCENARIO: read Default_Scenario.py		 #
	#=============================================================#


import sys
if __name__ == '__main__':  sys.path.append('../..')  # for tests


######################################
# specific variables and functions   #
######################################

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
		return [('GreenBeard',1),('Altruist',1)]

	def start_game(self,members):
		""" defines what to be done at the group level before interactions
			occur - Used in 'life_game'
		"""
		for indiv in members:
			#Don't forget that scores MUST REMAIN POSITIVE
			# So include a line such as:
			indiv.score(len(members)*10, FlagSet=True) # or whatever appropriate value to set scores to some initial value each year
		Default_Scenario.start_game(self, members)


	def interaction(self, indiv, partner):
		""" Genes control the behaviour of 'indiv' toward 'partner'
		"""

		###  TO BE WRITTEN  !!!!, using "indiv.score()" and "partner.score()"
		# Read individuals' genes using "indiv.gene_value('GreenBeard')"
		# Read parameter values using self.Parameter('GB_Gift')


		# Be careful when using parameter 'SelectionPressure' that scores remain discernible.
		# The method wouldn't favour individuals having 5054 point over those having 5017 points !
		# Note that the 'Selectivity' method would make this distinction(but its has other flaws) 
		# (see parameter documentation in the Configuration Editor)
	
		# if indiv.gene_value('GreenBeard') !=0:
			# pass


	def display_(self):
		""" Defines what is to be displayed. It offers the possibility
			of plotting the evolution through time of the best score,
			the average score, and the average value of the
			various genes defined on the DNA.
			It should return a list of pairs (C,X)
			where C is the curve colour and X can be
			'best', 'average', any gene name as defined by genemap
			or any phene of the phenemap
		"""
		return [('green1','GreenBeard'),('red','Altruist')]





###############################
# Local Test                  #
###############################

if __name__ == "__main__":
	print(__doc__ + '\n')
	input('[Return]')
	
