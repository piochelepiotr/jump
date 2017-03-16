#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################


##############################################################################
#  Individual                                                                #
##############################################################################

""" EVOLIFE: Module Individual:
		An Individual has a genome, several genes, a score and behaviours """

import sys
if __name__ == '__main__':  # for tests
	sys.path.append('../..')
	from Evolife.Scenarii.MyScenario import InstantiateScenario
	InstantiateScenario('SexRatio')


from random import randint

from Evolife.Genetics.Genome import Genome
from Evolife.Ecology.Phenotype import Phenome
from Evolife.Ecology.Alliances import Friend as SocialLink

class Individual:
	"   class Individual: basic individual "

	def __init__(self, Scenario, ID=None, Newborn = True):
		self.Scenario = Scenario
		if not Newborn:
			# Aged individuals are created when initializing a population
			AgeMax = self.Scenario.Parameter('AgeMax', Default=100)
			self.age = randint(1,AgeMax)
		else:	self.age = 0
		if ID:
			self.ID = ID
		else:
			self.ID = 'A' + str(randint(0,9999)) # permanent identification in the population
		self.location = None   # location in a multi-dimensional space 
		self.__score = 0
		self.LifePoints = 0	  # some individuals may be more resistant than others

	def aging(self, step=1):
		self.age += step
		return self.age
		
	def accident(self):
		" The victim suffers from a loss of life points "
		self.LifePoints -= 1
		
	def dead(self):
		if self.LifePoints < 0:	return True
		AgeMax = self.Scenario.Parameter('AgeMax', Default=0)
		if AgeMax and (self.age > AgeMax):	return True
		return False		
	
	def dies(self):
		"	Action to be performed when dying	"
	pass
	
	def score(self, bonus=0, FlagSet=False):
		if FlagSet:	self.__score = bonus
		else:		self.__score += bonus
		return self.__score

	def signature(self):
		return [self.age, self.__score]

	def observation(self, GroupExaminer):
		GroupExaminer.store('Properties',self.signature())

		
	def __repr__(self):
		# printing one individual 
		return "ID: " + str(self.ID) + "\tage: " + str(self.age) + "\tscore: " \
			   + "%.02f" % self.score()

				
				
				
				
class EvolifeIndividual(Individual, Genome, Phenome, SocialLink):
	"   Individual + genome + phenome + social links "

	def __init__(self, Scenario, ID=None, Newborn=True):
		Individual.__init__(self, Scenario, ID=ID, Newborn=Newborn)
		if not Newborn:
			Genome.__init__(self, self.Scenario)
			Genome.update(self)  # gene values are read from DNA
		else:
			Genome.__init__(self, self.Scenario) # newborns are created with blank DNA
		Phenome.__init__(self, self.Scenario, FlagRandom=True)
		# SocialLink.__init__(self, self.Scenario.Parameter('MaxGurus', Default=0), self.Scenario.Parameter('PopulationSize'))
		SocialLink.__init__(self, self.Scenario.Parameter('MaxGurus', Default=0))

	def observation(self, GroupExaminer):
		Individual.observation(self, GroupExaminer)
		GroupExaminer.store('Genomes',Genome.signature(self))
		GroupExaminer.store('DNA',list(self.get_DNA()), Numeric=True)
		GroupExaminer.store('Phenomes',Phenome.signature(self))
		GroupExaminer.store('Network',(self.ID,[T.ID for T in SocialLink.signature(self)]), Numeric=False)
		GroupExaminer.store('Positions', (self.ID,self.location), Numeric=False)

	def dies(self):
		"	Action to be performed when dying	"
		SocialLink.detach(self)
		Individual.dies(self)
		
	def __repr__(self):
		# printing one individual 
		return Individual.__repr__(self) + "\tPhen: " + Phenome.__repr__(self)
	
	
			
###############################
# Local Test                  #
###############################

if __name__ == "__main__":
	print(__doc__)
	print(Individual.__doc__ + '\n\n')
	John_Doe = Individual(7)
	print("John_Doe:\n")
	print(John_Doe)
	raw_input('[Return]')


__author__ = 'Dessalles'
