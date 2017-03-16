#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################


##############################################################################
#  Group                                                                     #
##############################################################################


""" EVOLIFE: Module Group:
		Reproduction, selection and behavioural games
		take place within the group """

import sys
if __name__ == '__main__':
	sys.path.append('../..')  # for tests
	from Evolife.Scenarii.MyScenario import InstantiateScenario
	InstantiateScenario('Cooperation')


from random import randint, sample, shuffle

from Evolife.Ecology.Individual import Individual, EvolifeIndividual
from Evolife.Ecology.Observer import Examiner		# for statistics

class Group:
	"   list of individuals "
	def __init__(self, Scenario, ID=1, Size=100):
		self.Scenario = Scenario	# Scenario just holds parameters
		self.size = 0
		self.members = []
		self.ranking = []   # to store a sorted list of individuals in the group
		self.best_score = 0
		self.ID = ID
		self.location = 0   # geographical position 
		self.Examiner = Examiner('GroupObs'+str(self.ID))
		for individual in range(Size):
			Indiv = self.createIndividual(Newborn=False)
			self.receive(Indiv)
		self.update_(flagRanking=True)
		self.statistics()

	def free_ID(self, Prefix=''):
		" returns an available ID "
		IDs = [m.ID for m in self.members]
		for ii in range(100000):
			if Prefix:	ID = '%s%d' % (Prefix, ii)
			else:		ID = '%d_%d' % (self.ID, ii)	# considering group number as prefix
			if ID not in IDs:	return ID
		return -1
			
	def createIndividual(self, ID=None, Newborn=True):
		return Individual(self.Scenario, ID=self.free_ID(), Newborn=Newborn)

	def whoIs(self, Number):
		" Returns the Numberth individual "
		try:	return self.members[Number]
		except IndexError:	error('Group', 'selecting non-existent individual')

	def isMember(self, indiv):	return	indiv in self.members
	
	def update_(self, flagRanking = False, display=False):
		""" updates various facts about the group
		"""
		# removing old chaps
		for m in self.members[:]:  # must duplicate the list to avoid looping over a modifying list
			if m.dead():	self.remove_(self.members.index(m))
		self.size = len(self.members)
		if self.size == 0:	return 0
		# ranking individuals
		if flagRanking:
			# ranking individuals in the group according to their score
			self.ranking = self.members[:]	  # duplicates the list, not the elements
			self.ranking.sort(key=lambda x: x.score(),reverse=True)
			if self.ranking != [] and self.ranking[0].score() == 0 and self.ranking[-1] == 0:
				# all scores are zero
				shuffle(self.ranking)  # not always the same ones first
			self.best_score = self.ranking[0].score()
		return self.size

	def statistics(self):
		""" updates various statistics about the group
		"""
		self.Examiner.reset()
		self.Examiner.open_(self.size)
		for i in self.members:
			i.observation(self.Examiner)
		self.Examiner.close_()		# makes statistics for each slot

	def positions(self):
		" lists agents' locations "
		return [(A.ID, A.location()) for A in self.members]
		
	def season(self, year):
		" This function is called at the beginning of each year "
		" individuals get older each year "
		for m in self.members:	m.aging()
		
	def kill(self, memberNbr):
		" suppress one specified individual of the group "
		# the victim suffers from an accident
		return self.remove_(memberNbr)
			
	def remove_(self, memberNbr):
		indiv = self.whoIs(memberNbr)
		indiv.dies()	# let the victim know
		self.size -= 1
		return self.members.pop(memberNbr)
		
	def receive(self, newcomer):
		" accepts a new member in the group "
		if newcomer:
			self.members.append(newcomer)
			self.size += 1

	def __len__(self):	return len(self.members)
	
	def __iter__(self):	return iter(self.members)
	
	def __repr__(self):
		" printing a sorted list of individuals, one per line "
		if self.ranking:	return ">\n".join(["%s" % ind for ind in self.ranking]) + "\n"
		else:				return "\n".join(["%s" % ind for ind in self.members]) + "\n"

		
		
class EvolifeGroup(Group):
	"   class Group: list of individuals that interact and reproduce "
	# Same as Group + reproduction + calls to Scenario functions

	def createIndividual(self, Newborn=True):
		# Indiv = Group.createIndividual(self, Newborn=Newborn)
		Indiv = EvolifeIndividual(self.Scenario, ID=self.free_ID(), Newborn=Newborn)
		self.Scenario.new_agent(Indiv, None)  # let scenario know that there is a newcomer	
		return Indiv

	def uploadDNA(self, Start):
		" loads given DNAs into individuals"
		if Start:	
			# if len(Start) != self.size:
				# error("Group", "%d DNAs for %d individuals" % (len(Start), self.size))
			for m in self.members:
				m.DNAfill([int(n) for n in self.Start.pop(0).split()])
							
	def update_(self, flagRanking = False, display=False):
		""" updates various facts about the group + positions
		"""
		size = Group.update_(self, flagRanking=flagRanking)
		if display:
			if flagRanking:	self.Scenario.update_positions(self.ranking, self.location)
			else:			self.Scenario.update_positions(self.members, self.location)
		# updating social links
		for m in self.members:	m.checkNetwork(membershipFunction=self.isMember)
		return size
		
	def reproduction(self):
		""" reproduction within the group
			reproduction_rate is expected in %
		"""		
		# The function 'couples' returns as many couples as children are to be born
		# The probability of parents to beget children depends on their rank within the group
		self.update_(flagRanking=True)   # updates individual ranks
		for C in self.Scenario.couples(self.ranking):
			# making of the child
			# child = Group.createIndividual(self)	# blank individual
			child = EvolifeIndividual(self.Scenario, ID=self.free_ID(), Newborn=True)			
			if child:
				child.hybrid(C[0],C[1]) # child's DNA results from parents' DNA crossover
				child.mutate()
				child.update()  # computes the value of genes, as DNA is available only now
				if self.Scenario.new_agent(child, C):  # let scenario decide something about the newcomer
					self.receive(child) # adds child to the group

	def season(self, year):
		" This function is called at the beginning of each year "
		Group.season(self, year)
		self.Scenario.season(year, self.members)
		
	def kill(self, memberNbr):
		" kills or weakens one specified individual of the group "
		# the victim suffers from an accident
		indiv = self.whoIs(memberNbr)
		indiv.accident()
		if indiv.dead():	return self.remove_(memberNbr)
		return None
			
	def remove_(self, memberNbr):
		indiv = self.whoIs(memberNbr)
		self.Scenario.remove_agent(indiv)   # let scenario know
		return Group.remove_(self, memberNbr)
		
	def life_game(self):
		# Let's play the game as defined in the scenario
		self.Scenario.life_game(self.members)
		# life game is supposed to change individual scores and life points

	def get_average(self):
		" computes an average individual "
		Avg_DNA = [int(round(B)) for B in self.Examiner.storages['DNA'].average]
		Avg = EvolifeIndividual(self.Scenario, Newborn=True)	# individual with average DNA (standard Evolife (dummy) individual
		Avg.DNAfill(Avg_DNA)
		return Avg
		
	def get_best(self):
		" returns the phenotype of the best or representative individual "
		return self.Scenario.behaviour(self.ranking[0], self.get_average())
	
			
###############################
# Local Test                  #
###############################

if __name__ == "__main__":
	print(__doc__)
	print(Group.__doc__ + '\n')
	gr_size = 10
	MyGroup = Group(1,gr_size)
	print(MyGroup)
	raw_input('[Return to continue]')
	for ii in range(22):
		MyGroup.life_game()
		MyGroup.update_(flagRanking = True)
		print("%d > " % ii)
		print("%.02f" % (sum([1.0*i.score() for i in MyGroup.members])/gr_size))
		print(MyGroup.Examiner)
		MyGroup.reproduction(MyScenario.Parameter('ReproductionRate'))
		while MyGroup.size > gr_size:
			MyGroup.kill(randint(0,MyGroup.size-1))
	#print toto
	raw_input('[Return to terminate]')
	
__author__ = 'Dessalles'
