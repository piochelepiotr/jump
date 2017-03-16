#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################



##############################################################################
#  S_SumBits                                                                 #
##############################################################################


"""	 EVOLIFE: SumBits Scenario:
		A scenario to study how fast all bits in the DNA evolve to 1
		A useful scenario for didactic purposes
"""
	#=============================================================#
	#  HOW TO MODIFY A SCENARIO: read Default_Scenario.py		 #
	#=============================================================#


import sys
if __name__ == '__main__':  sys.path.append('../..')  # for tests



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
		return [('sumbit',100,'Unweighted')]  # Add new elements to the list to insert new genes

	def evaluation(self,indiv):
		""" Implements the computation of individuals' scores
		"""
		if indiv.score() == 0:  # just check whether it's a newborn, to avoid computing score n times
			# score() without input value returns the current value of the score 
			# gene_value('sumbit') returns the number of bits set to 1 (if UNWEIGHTED is chosen in the configuration file)
			# gene_relative_value('sumbit') returns that value brought back between 0 and 100
			# The value is merely copied into the score
			# (Flagset=True means that thre previous value of the score is deleted)
			indiv.score(indiv.gene_relative_value('sumbit'), FlagSet=True)
				

	def update_positions(self, members, start_location):
		""" locates individuals on a 2-D space
		"""
		# sorting individuals by gene value (provisory)
		duplicate = members[:]
		duplicate.sort(key=lambda x: x.gene_value('sumbit'))
		for m in enumerate(duplicate):
			m[1].location = (start_location+m[0], m[1].score())

	def default_view(self):	return [('Genomes', 512), 'Legend']

	def legends(self):
		"""	The returned string will be displayed at the bottom ot the Legend window.
			Useful to describe what is to be seen in the various windows.
		"""
		return """<u>Genome Window</u>:<p>Each horizontal line represents the genome of an individual.<p><u>Field window</u>:<p>Individuals are displayed by they rank (x-axis) and their score (y-axis).
		"""
		
		
	def display_(self):
		""" Defines what is to be displayed. It offers the possibility
			of plotting the evolution through time of the best score,
			the average score, and the average value of the
			various genes defined on the DNA.
			It should return a list of pairs (C,X)
			where C is the curve colour and X can be
			'best', 'average', or any gene name as defined by genemap
		"""
		return [('white','best'),('blue','average')]
		


###############################
# Local Test                  #
###############################

if __name__ == "__main__":
	print(__doc__ + '\n')
	SB = Scenario()
	input('[Return]')
	
