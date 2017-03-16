#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################


##############################################################################
#  Population                                                                #
##############################################################################


""" EVOLIFE: Module Population:
		A population is a set of semi-permeable groups
		"""


import sys
if __name__ == '__main__':  # for tests
	sys.path.append('../..')
	from Evolife.Scenarii.MyScenario import InstantiateScenario
	InstantiateScenario('Cooperation','../Evolife')



import math
from random import randint, choice

from Evolife.Tools.Tools import EvolifeError, error
from Evolife.Ecology.Group import Group, EvolifeGroup			 # definition of groups

class Population:	
	"""   class Population: list of Groups
		Minimal version  """
	
	def __init__(self, Scenario, Observer):
		""" Creation of the groups """
		self.Scenario = Scenario
		self.popSize = self.Scenario.Parameter('PopulationSize')
		self.groupMaxSize = self.popSize + 1
		self.groups = []
		self.year = -1		   # to keep track of time
		self.Observer = Observer # contains instantaneous data for statistics and display
		self.best_score = 0
		nb_groups = self.Scenario.Parameter('NumberOfGroups', Default=1)
		group_size = self.popSize // nb_groups
		self.groupMaxSize = 2 * group_size	# groups beyond that size split
		while (nb_groups > 0):
			self.groups.append(self.createGroup(ID=nb_groups, Size=group_size))
			nb_groups -= 1
		self.statistics(Display=True)	# updates popSize
		
	def createGroup(self, ID=0, Size=0):
		return Group(self.Scenario, ID=ID, Size=Size)
		
	def selectIndividual(self):
		" random selection of an individual in the population "
		(group, winner) = self.lottery()
		return group.whoIs(winner)
		
	def lottery(self):
		" random selection of an individual by number in the population "
		winner = randint(0,self.popSize-1)
		for gr in self.groups:
			if gr.size > winner:	return (gr,winner)
			else:	winner -= gr.size
		error("Population: wrong population size", str(self.popSize))

	def season(self):
		self.year += 1		  # keeps track of time
		self.Observer.season(self.year)
		for gr in self.groups:	gr.season(self.year)

	def migration(self):
		" migration between groups of some percentage of individuals "
		if len(self.groups) < 2 or self.Scenario.Parameter('MigrationRate', Default=0) == 0:
			return	# no migration if only one group
		migrants = int(self.Scenario.Parameter('MigrationRate') * self.popSize/100.0 + 0.5)
		while migrants:
			(gr_out, migrant) = self.lottery() # choosing the migrant
			(gr_in,dummy) = self.lottery()	# choosing where to go
			gr_in.receive(gr_out.remove_(migrant))  # symbolically murdered, and then born-again
			migrants -= 1

	def group_splitting(self):
		""" groups that are too big are split in two,
			and too small groups are dispersed """
		##############
		##  TO BE REWRITTEN: restart the whole splitting process after one split
		##############
		grps = self.groups[:]   # copy of the list, necessary since 'groups' is modified within the loop
		for gr in grps:
			if gr.size > self.groupMaxSize:
				effectif = int(gr.size/2.0 + .5)
				newgroup = self.createGroup(ID=len(self.groups)+1)		# create empty group
				while effectif:
					newgroup.receive(gr.remove_(randint(0,gr.size-1)))   # symbolically murdered, and then born-again
					effectif -= 1
				newgroup.update_()
				self.groups.append(newgroup)

		##############
		##  TO BE REWRITTEN: restart the whole destruction process after one destruction
		##############
		if self.Scenario.Parameter('GroupMinSize', Default=0) ==0: return	# No group minimum size
		grps = self.groups[:]   # copy of the list, necessary since 'groups' is modified within the loop
		for gr in grps:
			if gr.size < self.Scenario.Parameter('GroupMinSize'):
				self.groups.remove(gr)
				self.popSize -= gr.size	# necessary for lottery()
				# for dummy in gr.members:
				for dummy in list(gr):
					try:
						gr_in = choice(self.groups) # dispersed members join groups independently of their size
					except IndexError:
						return  # dying population 
##					(gr_in,dummy) = self.lottery() # choosing where to go
					gr_in.receive(gr.remove_(0))  # symbolically murdered, and then born-again
					self.popSize += 1

	def limit(self):
		" randomly kills individuals until size is reached "
##		MaxLives =  self.Scenario.Parameter('SelectionPressure')
		self.update()
		while self.popSize > self.Scenario.Parameter('PopulationSize'):
			(gr,Unfortunate) = self.lottery()
			if gr.kill(Unfortunate):
				self.popSize -= 1
		self.update(display=True)
		
	def update(self, flagRanking = False, display=False):
		" updates groups and looks for empty groups "
		self.popSize = 0	# population size will be recomputed
		toBeRemoved = []
		for gr in self.groups:
			gr.location = self.popSize  # useful for separating groups when displaying them on an axis
			grsize = gr.update_(flagRanking, display=display)
			if grsize == 0:	toBeRemoved.append(gr)
			self.popSize += grsize
		for gr in toBeRemoved:	self.groups.remove(gr)
		if self.popSize == 0:	error("Population is empty")
		self.best_score = max([gr.best_score for gr in self.groups])
		return self.popSize

	def statistics(self, Complete=True, Display=False):
		" Updates statistics about the population "
		self.update(display=Display)  # updates facts
		self.Observer.reset()
		if Complete:
			self.Observer.open_()
			for gr in self.groups:
				gr.statistics()
				self.Observer.store(gr.Examiner)
			self.Observer.close_()	# computes statistics in Observer
		
	def one_year(self):
		" one year of life "
		if self.year < 0:
			# just to get a snapshot of the initial situation
			self.season()			# annual resetting and time increment
			self.statistics()
			return True
		try:
			self.limit()			# some individuals die to limit population size	
			self.migration()		# some individuals change group
			self.group_splitting()  # big groups split and small groups are dissolved
			self.season()			# annual resetting and time increment
			if self.Observer.Visible():
				self.statistics(Complete=True, Display=True)	   # compute statistics before reproduction
				try:	self.Observer.recordInfo('Best', self.groups[0].get_best())
				except (IndexError, AttributeError): pass	# no record of best individual
			return True
		except Exception as Msg:
			error("Population", str(Msg))
			return False

	def members(self):
		for gr in self.groups:
			# for i in gr.members:
			for i in gr:
				yield i
			
	def __repr__(self):
		# printing global statistics
		# and then a list of groups, one per line
		return "\n  Population Statistics:\n" + \
			   "> Popul: %d members\tbest: %d\tavg: %.02f\tyear: %d\n" \
					% (self.Observer.Statistics['Properties']['length'],
					   self.Observer.Statistics['Properties']['best'][1],
					   self.Observer.Statistics['Properties']['average'][1], self.year) + \
				"\n".join(["group %d: %d members\tbest: %d\tavg: %.02f" \
					% (i, grObs.storages['Properties'].length, grObs.storages['Properties'].best[1],
					   grObs.storages['Properties'].average[1]) \
						  for (i,grObs) in enumerate(self.Observer.storage)]) + "\n"


						  										  
	
class EvolifePopulation(Population):
	"   Population + reproduction + call to Scenario life_game "

	def __init__(self, Scenario, Evolife_Obs):
		""" Creation of the groups """
		Population.__init__(self, Scenario, Evolife_Obs)
		# Possibility of intialiazing genomes from file
		if self.Scenario.Parameter('StartFromFile', Default=0):
			StartFile = open('EvoStart.gen','r')
			self.Observer.TextDisplay('Retrieving population from EvoStart.gen\n')
			Genomes = StartFile.readlines() # put lines in a list
			StartFile.close()
			self.popSize = len(Genomes) # priority over configuration file
			for gr in self.groups:	gr.uploadDNA(Genomes)
		else:
			Genomes = []
		self.statistics()	# updates popSize

	def createGroup(self, ID=0, Size=0):
		return EvolifeGroup(self.Scenario, ID=ID, Size=Size)
		
	def reproduction(self):
		" launches reproduction in groups "
		for gr in self.groups:
			gr.reproduction()
		self.update()
				
	def life_game(self):
		for gr in self.groups:
			gr.life_game()
					
	def one_year(self):
		if self.year >= 0:
			self.reproduction()	 # reproduction depends on scores
			self.life_game()		# where individual earn their score
		Res = Population.one_year(self)
		return Res


if __name__ == "__main__":
	print(__doc__)
	print(Population.__doc__ + '\n\nTest:\n')


###################################
# Test							#
###################################

if __name__ == "__main__":
	from Evolife.Ecology.Observer import Meta_Observer
	Obs = Meta_Observer('PopObs')
	Pop = Population(Obs)
	print(Pop)
	
	for ii in range(16):
		Pop.one_year()
		print(Pop)
	raw_input('[Return]')

__author__ = 'Dessalles'
