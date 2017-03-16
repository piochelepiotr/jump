#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################



##############################################################################
#  S_CostlySignal : implements Costly Signalling theory                      #
# see for instance http://faculty.washington.edu/easmith/JTB2001.pdf         #
##############################################################################


""" EVOLIFE: Costly Signal Scenario:
	Individuals may emit a signal in relation with their quality.
	Emitting this signal involves a cost.
	Receivers read the signal and decide to associate or not with the emitter.
	Association provides benefit to emitters.
	Association provides benefit to receivers only if emitter is oh high quality.
	Evolution leads to a situation in which communication is honest,
	i.e. individuals signal their true quality.
	This is due to the fact that liars (l-q signalling individuals) cannot
	afford the cost of high signals.
"""

	#=============================================================#
	#  HOW TO MODIFY A SCENARIO: read Default_Scenario.py		 #
	#=============================================================#

import sys
if __name__ == '__main__':  sys.path.append('../..')  # for tests

from Evolife.Scenarii.Default_Scenario import Default_Scenario
from Evolife.Tools.Tools import percent, noise_add, error

######################################
# specific variables and functions   #
######################################

class Scenario(Default_Scenario):

	######################################
	# All functions in Default_Scenario  #
	# can be overloaded				  #
	######################################


	def initialization(self):
		self.GlobalComm = 0 # Average investment in communication by actual individuals
		self.QualityHistogram = [[0,0] for ii in range(self.Parameter('ControlGeneNumber'))]
		# stores individual repartition by Quality
		self.PopSize = 0	# number of individuals currently present

	def genemap(self):
		""" Defines the name of genes and their position on the DNA.
		Accepted syntax:
		['genename1', 'genename2',...]:   lengths and coding are retrieved from configuration
		[('genename1', 8), ('genename2', 4),...]:   numbers give lengths in bits; coding is retrieved from configuration
		[('genename1', 8, 'Weighted'), ('genename2', 4, 'Unweighted'),...]:	coding can be 'Weighted', 'Unweighted', 'Gray', 'NoCoding'
		"""
		return ['SignalByQualityRange'+str(ControlGene) for ControlGene in range(self.Parameter('ControlGeneNumber'))]	# default lengths

	def phenemap(self):
		""" Defines the set of non inheritable characteristics
		"""
		return ['Quality',  # quality is a non-heritable characteristic
				'SignalInvestment', # efforts devoted to signalling
				'Signal']   # emitted signal

	def QualityRange(self, Indiv):
		" assigns an individual to a category depending on its Quality "
		return int((Indiv.Phene_relative_value('Quality') * self.Parameter('ControlGeneNumber')) / 100.01)
	
	def Quality(self, Indiv, Apparent=False):
		" Adds a bottom value to Quality "
		BC = self.Parameter('BottomQuality')
		Comp = percent(100-BC) * Indiv.Phene_relative_value('Quality') + BC
		VisibleQuality = percent(Comp * Indiv.Phene_relative_value('SignalInvestment'))
		if Apparent:
			return VisibleQuality
		else:
			return Comp
	
	def new_agent(self, Child, parents):
		" initializes newborns "
		# determination of the newborn's signal level
		#   Investment in communication is genetically controlled
		#	   Genetic control may vary according to Quality range
		SignalInvestment = Child.gene_relative_value('SignalByQualityRange'
														 +str(self.QualityRange(Child)))
		Child.Phene_value('SignalInvestment', int(SignalInvestment), Levelling=True)
		
		#   The signal is based on the signaller's Quality
		Signal = self.Quality(Child, Apparent=True)
		Signal = noise_add(Signal,self.Parameter('Noise'))
		Child.Phene_value('Signal', int(Signal), Levelling=True)

	def season(self, year, members):
		""" This function is called at the beginning of each year
		"""
		self.GlobalComm = 0
		self.QualityHistogram = [[0,0] for ii in range(self.Parameter('ControlGeneNumber'))]
		self.PopSize = 0	# number of individuals currently present

	def start_game(self,members):
		""" defines what is to be done at the group level before interactions
			occur
		"""
 
		for Indiv in members:
			# resetting scores so that scors remain positive
			Indiv.score(self.Parameter('CostlySignalCost'), FlagSet=True)
			SigInv = Indiv.Phene_value('SignalInvestment')
			SignalCost = percent(SigInv * self.Parameter('CostlySignalCost'))
			Indiv.score(-SignalCost)

			# Monitoring Quality distribution
			self.GlobalComm += SigInv
			self.QualityHistogram[self.QualityRange(Indiv)][0] += SigInv
			self.QualityHistogram[self.QualityRange(Indiv)][1] += 1
				
		self.PopSize += len(members)	# number of individuals currently present
			
		# Individuals first interact one more time with their current friends
		for Indiv in members:
			for Friend in Indiv.friends():
				self.interaction(Indiv, Friend)

	def interaction(self, Indiv, Partner):
		""" Partner may choose to join Indiv based on Indiv's signal
		"""

		# new interaction puts previous ones into question
		if Indiv in Partner.gurus.names():
			Partner.quit_(Indiv)

		# Negociation takes place
		#IndivOffer = self.Quality(Indiv, Apparent=True)
		IndivOffer = Indiv.Phene_value('Signal')
		Partner.new_friend(Indiv, IndivOffer)   # possibly establishes a new link
	

	def end_game(self, members):
		""" Individuals get benefit from their alliances
		"""
		# Followees get benefit from being followed
		# Followers get benefit from following high quality individuals

		for Follower in members:
			for Friend in Follower.friends():
				Friend.score(self.Parameter('FollowerSupport'))
				Follower.score(percent(self.Parameter('FollowerBenefit') * self.Quality(Friend, Apparent=False)))
##                Follower.score(self.Quality(Friend, Apparent=False)/Friend.followers.size())
			
	def update_positions(self, members, start_location):
		""" locates individuals in a 3D space (2D + colour)
		"""
		# sorting individuals by quality
		duplicate = members[:]
		duplicate.sort(key=lambda x: x.Phene_value('Quality'))
		for m in enumerate(duplicate):
			m[1].location = (1+start_location + m[1].Phene_value('Quality'),
##                             m[1].score(),
							 m[1].Phene_value('Signal'),
							 self.QualityRange(m[1])+1)
##            m[1].location = (1+start_location + m[1].Phene_value('Quality'), m[1].Phene_value('SignalInvestment'))
##            m[1].location = (1+start_location + m[0], m[1].score(), min(1+m[1].Phene_value('Sociability'),20))            

	def local_display(self,VariableID):
		" allows to display locally defined values "
		if VariableID == 'AvgCommunicationInvestment':
			if self.PopSize:
				self.GlobalComm /= float(self.PopSize)
				return int(self.GlobalComm)
			else:
				return -1
		elif VariableID.startswith('TrueSignalByQualityGene'):
			if self.QualityHistogram[int(VariableID.split('TrueSignalByQualityGene')[1])][1] < 7:
				return -1   # not enough representants
			else:
				return int(self.QualityHistogram[int(VariableID.split('TrueSignalByQualityGene')[1])][0] / \
					   float(self.QualityHistogram[int(VariableID.split('TrueSignalByQualityGene')[1])][1]))
		return -1   # should never occur			
 
	def display_(self):
		# Merely display all genes of GeneMap
		disp = [(1,'AvgCommunicationInvestment')]
		disp += [(2*i+10,'TrueSignalByQualityGene'+str(i)) for i in range(self.Parameter('ControlGeneNumber'))]
		return disp


###############################
# Local Test                  #
###############################

if __name__ == "__main__":
	print(__doc__ + '\n')
	SB = Scenario()
	input('[Return]')
	
