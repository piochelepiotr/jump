#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################



"""	 EVOLIFE: Favourable Scenario:
		A scenario to study the fate of favourable / unfavourable mutation
		(i.e. the most basic Darwinian case)
		Also: allows to define the benefit at the group level, what allows
		the study of the so-called 'group selection'
"""

	#=============================================================#
	#  HOW TO MODIFY A SCENARIO: read Default_Scenario.py		 #
	#=============================================================#


import sys
if __name__ == '__main__':  sys.path.append('../..')  # for tests


from Evolife.Scenarii.Default_Scenario import Default_Scenario
from Evolife.Tools.Tools import percent


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
		return ['favourable', 'neutral']  

	def initialization(self):
		self.CollectiveAsset = 0 # collective wealth due to group members
		self.Cumulative = bool(self.Parameter('Cumulative'))	# indicates whether scores are accumulated or are reset each year

	def start_game(self,members):
		""" defines what to be done at the group level each year
			before interactions occur - Used in 'life_game'
		"""

		if len(members) == 0:   return
		InitialBonus = 0
		
		# special case of negative benefits: Individuals are given an initial bonus to keep scores positive
		if self.Parameter('CollectiveBenefit') < 0:
			InitialBonus = -self.Parameter('CollectiveBenefit')		# just to keep scores positive
		if self.Parameter('IndividualBenefit') < 0:
			InitialBonus -= self.Parameter('IndividualBenefit')	# just to keep scores positive

		self.CollectiveAsset = 0	# reset each year

		for indiv in members:
			indiv.score(InitialBonus, FlagSet=not self.Cumulative)	# Initial bonus is added (FlagSet=False) or assigned (FlagSet=True) to Score
			
			################################
			# computing collective benefit #
			################################
			# each agent contributes to collective benefit in proportion of its 'favourable' gene value
			self.CollectiveAsset += indiv.gene_relative_value('favourable')
		self.CollectiveAsset = float(self.CollectiveAsset) / len(members)

	def evaluation(self,indiv):
		""" Implements the computation of individuals' scores -  - Used in 'life_game'
		"""
		################################
		# computing individual benefit #
		################################
		IndividualValue = indiv.gene_relative_value('favourable')	# between 0 and 100
		# Bonus = <individual value> * <Individual benefit parameter> / 100 
		Bonus = percent(IndividualValue * self.Parameter('IndividualBenefit'))
		# Collective profit is merely added
		Bonus += percent(self.CollectiveAsset * self.Parameter('CollectiveBenefit'))
		indiv.score(Bonus, FlagSet=False)  # Bonus is added to Score 

	def default_view(self):	return ['Genomes']		

	def update_positions(self, members, groupLocation):
		""" Allows to define spatial coordinates for individuals.
			These positions are displayed in the Field window.
		"""
		for indiv in enumerate(members):
			indiv[1].location = (groupLocation + indiv[0], indiv[1].score())

	def wallpaper(self, Window):
		" displays background image or colour when the window is created "
		# Possible windows are: 'Field', 'Curves', 'Genome', 'Log', 'Help', 'Trajectories', 'Network'
		if Window == 'Curves':	return 'Scenarii/Landscape_.png'
		return Default_Scenario.wallpaper(self, Window)
		
	def display_(self):
		" Defines what is to be displayed. "
		return [('red','favourable'),('yellow','neutral')]


		
###############################
# Local Test                  #
###############################

if __name__ == "__main__":
	print(__doc__ + '\n')
	input('[Return]')
	
