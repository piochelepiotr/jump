#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################



##############################################################################
#  S_StagHunt                                                                    #
##############################################################################


""" EVOLIFE: Stag Hunt Scenario (after Brian Skyrms, "The stag hunt",
	Cambridge University Press 2004, pp. 67-70)
	In the stag hunt scenario, two players have the choice:
	- either to cooperate to hunt a stag (S)
	- or to defect and hunt a hare (H) for themselves.
	The payoff matrix is typically as follows:
	
						  opponent
							S   H
						S   9   1
				player  
						H   8   7

	This is a particular case of stag hunt in which it is better to
	hunt hare against a stag hunter rather than against a hare hunter.
	Such game is also called "assurance game".
	Individuals are allowed to send a binary signal before interacting.
	They then decide to hunt stag or hare depending on that signal.
	Various strategies can be opposed.
	- Ex1: individuals play stag against those who send the same signal,
	and hunt hare otherwise.
	It is a case of bistability: everyone ends up sending 0 (or 1).
	- Ex2: individuals play stag against those who send a different signal
	and hunt stag otherwise.
	It is a case of honest cheap signalling: 1-senders and 0-senders
	balance each other (a 50-50 equilibrium is stable) and their best
	strategy is to honestly signal who they are.
	- Ex3: all eight strategies are implemented
	(send 1 or 0  X  play S or H if 0 observed  X  play S or H if 1 observed)
	Stag hunting becomes the rule virtually all the time (and signals become
	neutral) though other equilibria are theoretically possible.
"""
	#=============================================================#
	#  HOW TO MODIFY A SCENARIO: read Default_Scenario.py		 #
	#=============================================================#

import sys
if __name__ == '__main__':  sys.path.append('../..')  # for tests


import random
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
		return [('signal',1),('hunt_if_0',1),('hunt_if_1',1)]

	def start_game(self, members):
		""" defines what to be done at the group level before interactions
			occur
		"""
		for m in members:
			m.score(0, FlagSet=True)	# resetting scores each year

	def interaction(self, indiv, others):

		def signals(indiv,noisy=0):
			if noisy:
				return noise_add(indiv.gene_relative_value('signal'),self.Parameter('Noise')) > 50
			else:
				return indiv.gene_relative_value('signal') > 50

		def hunts_stag(indiv,signal):
			""" defines indiv's actual hunting behaviour depending on the signal emitted
				by the opponent
			"""
			if signal:
				return noise_add(indiv.gene_relative_value('hunt_if_1'),
							 self.Parameter('Noise')) > 50
			else:
				return noise_add(indiv.gene_relative_value('hunt_if_0'),
							 self.Parameter('Noise')) > 50
	##		return signals(indiv) == signal

		# implementing the payoff matrix
		if hunts_stag(indiv,signals(Partner,noisy=1)):
			if hunts_stag(Partner, signals(indiv)):
				indiv.score(self.Parameter('StagStag'))
				Partner.score(self.Parameter('StagStag'))
			else:
				indiv.score(self.Parameter('StagHare'))
				Partner.score(self.Parameter('HareStag'))
		else:
			if hunts_stag(Partner, signals(indiv)):
				indiv.score(self.Parameter('HareStag'))
				Partner.score(self.Parameter('StagHare'))
			else:
				indiv.score(self.Parameter('HareHare'))
				Partner.score(self.Parameter('HareHare'))


		



###############################
# Local Test                  #
###############################

if __name__ == "__main__":
	print(__doc__ + '\n')
	input('[Return]')
	
