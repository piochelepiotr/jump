#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################



""" EVOLIFE: HawkDove Scenario

Two players confront each other over a resource whose full value is V to either of them. Each player may play one of two strategies: H (Hawk) or D (Dove). Doves signal that they wish to share the resource equally. Hawks signal they are willing to fight to get the resource. When two Doves meet, each gives the characteristic sharing signal and the resource is divided equally, or, perhaps, a fair coin is tossed and the winner gets all. In any case, the expected return to each of the two Doves is V/2. When a Hawk meets a Dove, the Hawk (as it always does) signals fight, the Dove (as it always does) signals share, then the Dove retreats and the Hawk takes the entire resource. Finally, when two Hawks meet, each signal fight, neither retreats, both fight at a cost of C. In the end, the resource is shared equally, minus the cost, or, perhaps, half the time one Hawk gets the entire resource and half the time the other Hawk gets it. In any case, the expected return to each of the Hawks is (V - C)/2.	 


"""

	#=============================================================#
	#  HOW TO MODIFY A SCENARIO: read Default_Scenario.py		 #
	#=============================================================#

import sys
import random
if __name__ == '__main__':  sys.path.append('../..')  # for tests


from Evolife.Scenarii.Default_Scenario import Default_Scenario

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
		if True:
			# ........  To be changed ........
			# Consider a gradual gene
			return [('Hawk',1)] 	# Doves are non-hawks
			# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

	def phenemap(self):
		""" Defines the set of non inheritable characteristics
		"""
		# NOT USED
		return ['Strength']	# Elements in phenemap are integers between 0 and 100 and are initialized randomly

	def initialization(self):	
		self.Peace = 0	# done only once
		self.Encounters = 0
		self.GroupSize = 0
		
	def start_game(self, members):
		self.Peace = 0	# done every year
		self.GroupSize = len(members)
		self.Encounters = 0
		Default_Scenario.start_game(self, members)
		
	def prepare(self, indiv):
		" defines what is to be done at the individual level before interactions "
		# scores are intialized so that they remain positive
		indiv.score(self.Parameter('BattleCost') * self.GroupSize * self.Parameter('Rounds'), FlagSet=True)

	def hawk(self, indiv):
		if random.randint(0,100) < self.Parameter('Noise'):
			return random.choice([True, False])
		if True:
			# ........  To be changed ........
			# Consider a gradual gene
			return indiv.gene_value('Hawk') > 0
			# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
		
	def interaction(self, indiv, partner):
		self.Encounters += 1
		if self.hawk(indiv):
			if self.hawk(partner):	# Hawk - Hawk #
				# print indiv
				indiv.score((self.Parameter('PieToShare') - self.Parameter('BattleCost')) /2 )		# score is updated
				partner.score((self.Parameter('PieToShare') - self.Parameter('BattleCost')) /2)	# score is updated
			else:					# Hawk - Dove #
				indiv.score(self.Parameter('PieToShare'))		# score is updated
		else:	# indiv == dove
			# print indiv
			if self.hawk(partner):	# Dove - Hawk #
				partner.score(self.Parameter('PieToShare'))		# score is updated
			else:					# Dove - Dove #
				self.Peace += 1
				indiv.score(self.Parameter('PieToShare')/2)		# score is updated
				partner.score(self.Parameter('PieToShare')/2)	# score is updated

	def local_display(self, LocalVariable):
		if LocalVariable == 'Peace' and self.Encounters:	
			# relative proportion of peaceful encounters
			return (100.0 * self.Peace) / self.Encounters
		return 0
		
	def display_(self):
		" Defines what is to be displayed. "
		# The default behaviour is to display all genes of GeneMap
		return [('brown', 'Hawk', 'toto'), ('green', 'Peace', 'proportion of peaceful encounters')]
		
	def default_view(self):	return ['Genomes']
	
		
###############################
# Local Test                  #
###############################

if __name__ == "__main__":
	print(__doc__ + '\n')
	SB = Scenario()
	input('[Return]')
	
