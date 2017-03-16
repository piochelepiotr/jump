#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################



##############################################################################
#  S_SexRatio                                                                #
##############################################################################


""" EVOLIFE: SexRatio Scenario:
	If the sex ratio in the progeny is genetically controlled, a 50-50 ratio 
	emerges, despite the fact that males consume resources without investing
	in offspring. 
	However, in hymenoptera (wasps, bees, ants), in which males are haploid 
	(one exemplar for each chomosome) whereas females are diploid (two exemplars
	of each chromosome), sex ratio is expected to converge toward 25-75 whenever 
	it is controlled by genes expressed in sisters (workers).
"""
	#=============================================================#
	#  HOW TO MODIFY A SCENARIO: read Default_Scenario.py		 #
	#=============================================================#

import sys
if __name__ == '__main__':  sys.path.append('../..')  # for tests



import random

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
		return ['sexControl']	# the gene's length is given in the configuration

	def phenemap(self):
		""" Defines the set of non inheritable characteristics
		"""
		return ['Sex']  # Sex is considered a phenotypic characteristic !
						# This is convenient because sex is determined at birth
						# and is not inheritable

	def female(self, Indiv):
		if Indiv.Phene_value('Sex') > 50:	return True
		return False
		
	def male(self, Indiv):
		if Indiv.Phene_value('Sex') <= 50:	return True
		return False
		
	def parents(self, candidates):
		""" selects a female and a male for procreation
		"""
		mothers = [m for m in candidates if self.female(m[0])]
		fathers = [f for f in candidates if self.male(f[0])]
		try:	return (random.choice(mothers), random.choice(fathers))
		except	IndexError:	return None
		
	def new_agent(self, child, parents):
		""" makes a child from a couple 
		"""
		# This function is called with an existing child that results from standard hybridation between parents
		if parents:		# (parents is None when the population is initialized)
			# deciding the child's sex
			mother = parents[0]
			# Let's uppose that mom's genes decide
			if random.randint(0,100) >= mother.gene_relative_value('sexControl'):
				child.Phene_value('Sex',100)	# It's a girl !
			else:
				child.Phene_value('Sex',0)		# It's a boy !

			# testing selective death
			if self.Parameter('SelectiveDeath'):
				# male eggs are killed
				if self.male(child) and random.randint(0,100) < self.Parameter('SelectiveDeath'):
					return False
		
			if self.Parameter('Hymenoptera') and self.female(child):
				# The haplo-diploidy of hymenoptera is (remotely) mimicked by
				# increasing the contribution of mother to the child's genome
				child.hybrid(child, mother) # the child is more related to its mother
		return True

	def wallpaper(self, Window):
		" displays background image or colour when the window is created "
		# Possible windows are: 'Field', 'Curves', 'Genome', 'Log', 'Help', 'Trajectories', 'Network'
		if Window == 'Curves':	return 'Scenarii/male-and-female-symbols-vector-246764_.jpg'
		return Default_Scenario.wallpaper(self, Window)
		
	def display_(self):
		" Defines what is to be displayed. "
		return [('red','sexControl'), ('pink','Sex')]

			


###############################
# Local Test				  #
###############################

if __name__ == "__main__":
	print(__doc__ + '\n')
	input('[Return]')
	
