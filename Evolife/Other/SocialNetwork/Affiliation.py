#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################


""" Study of the role of signalling in the emergence of social networks:
Individuals signal their quality to attract followers
"""


from time import sleep
from random import sample, choice

import sys
sys.path.append('../../..')

import SocialSimulation as SSim
import Evolife.Ecology.Alliances as EA
import Evolife.Ecology.Learner as EL

		
class Observer(SSim.Social_Observer):
	def Field_grid(self):
		" initial draw: here a green square "
		return [(0, 0, 'red', 1, 100, 100, 'red', 1), (100, 100, 1, 0)]
	
class Individual(EA.Follower, EL.Learner):
	"   A social individual has friends and can learn "

	def __init__(self, IdNb, maxQuality=100, parameters=None):
		if parameters is None:	parameters = Gbl
		self.Param = parameters.Param
		Features = {'SignalInvestment': 0 }   # propensity to be moral oneself
		self.SignalLevel = 0
		self.BestSignal = 0	# best signal value in memory
		self.id = "A%d" % IdNb	# Identity number
		EA.Follower.__init__(self, self.Param('MaxFriends'), self.Param('MaxFollowers'))
		self.Quality = (100.0 * IdNb) / maxQuality # quality may be displayed
		# Learnable features
		EL.Learner.__init__(self, Features, MemorySpan=self.Param('MemorySpan'), AgeMax=self.Param('AgeMax'), 
							Infancy=self.Param('Infancy'), Imitation=self.Param('ImitationStrength'), 
							Speed=self.Param('LearningSpeed'), Conservatism=self.Param('LearningConservatism'), toric=self.Param('Toric'))
		self.Points = 0	# stores current performance
		self.update()

	def Reset(self):
		self.detach()	# erase friendships
		EL.Learner.Reset(self)
		self.Points = 0
		# self.update()
		
	def update(self, infancy=True):
		"	updates values for display "
		Colour = 'brown'
		if infancy and not self.adult():	Colour = 'pink'
		self.SignalLevel = self.Signal()
		BR = self.bestRecord()
		if BR:	self.BestSignal = BR[0]['SignalInvestment'] * self.Quality / 100.0
		else:	self.BestSignal = 0
		# self.Position = (self.Quality, self.Features['SignalInvestment'], Colour, 8)
		self.Position = (self.Quality, self.BestSignal+1, Colour, 8)	# 8 == size of blob in display
		if Gbl.Param('Links') and self.best_friend():
			self.Position += (self.best_friend().Quality, self.best_friend().BestSignal+1, 21, 1)

	def Signal(self, Transparent=False):
		" returns the actual quality of an individual or its displayed version "
		if Transparent:	return self.Quality
		BC = Gbl.Param('BottomCompetence')
		Comp = (100.0-BC) * self.Quality/100.0 + BC
		# Comp = BC + self.Quality
		VisibleCompetence = Comp * self.Features['SignalInvestment'] / 100.0
		return self.Limitate(VisibleCompetence, 0, 100)

	def Interact(self, Signallers):
		if Signallers == []:	return
		# The agent chooses the best available Signaller from a sample.
		OldFriend = self.best_friend()
		Signallers.sort(key=lambda S: S.SignalLevel, reverse=True)
		for Signaller in Signallers:
			if Signaller == self:	continue
			if OldFriend and OldFriend.SignalLevel >= Signaller.SignalLevel:
				break	# no available interesting signaller
			if Signaller.followers.accepts(0) >= 0:
				# cool! Self accepted as fan by Signaller.
				if OldFriend is not None and OldFriend != Signaller:
					self.G_quit_(OldFriend)
				self.F_follow(0, Signaller, Signaller.SignalLevel)
				break

	def assessment(self):
		" Social benefit from having friends "
		self.Points -= Gbl.Param('SignallingCost') * self.Features['SignalInvestment'] / 100.0
		if self.best_friend() is not None:
			self.best_friend().Points += Gbl.Param('JoiningBonus')

	def __repr__(self):
		return "%s[%0.1f]" % (self.id, self.SignalLevel)
		
class Population(SSim.Social_Population):
	" defines the population of agents "

	def __init__(self, parameters, NbAgents, Observer):
		" creates a population of agents "
		SSim.Social_Population.__init__(self, parameters, NbAgents, Observer, IndividualClass=Individual)
		

	def season_initialization(self):
		for agent in self.Pop:
			if self.Param('EraseNetwork'):	agent.detach()
			agent.Points = 0
		
	def interactions(self):
		for Run in range(Gbl.Param('NbInteractions')):
			Fan = choice(self.Pop)
			# Fan chooses from a sample
			Fan.Interact(sample(self.Pop, Gbl.Param('SampleSize')))

			
	def Dump(self, Slot):
		""" Saving investment in signalling for each adult agent
			and then distance to best friend for each adult agent having a best friend
		"""
		if Slot == 'SignalInvestment':
			#D = [(agent.Quality, "%2.03f" % agent.Features['SignalInvestment']) for agent in self.Pop if agent.adult()]
			#D += [(agent.Quality, " ") for agent in self.Pop if not agent.adult()]
			D = [(agent.Quality, "%2.03f" % agent.Features['SignalInvestment']) for agent in self.Pop]
		if Slot == 'DistanceToBestFriend':
			D = [(agent.Quality, "%d" % abs(agent.best_friend().Quality - agent.Quality)) for agent in self.Pop if agent.adult() and agent.best_friend() is not None]
			D += [(agent.Quality, " ") for agent in self.Pop if agent.best_friend() == None or not agent.adult()]
		return [Slot] + [d[1] for d in sorted(D, key=lambda x: x[0])]
		

		
if __name__ == "__main__":
	Gbl = SSim.Global()
	SSim.Start(Params=Gbl, PopClass=Population, ObsClass=Observer)



__author__ = 'Dessalles'
