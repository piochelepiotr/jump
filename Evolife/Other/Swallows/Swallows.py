#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################


""" Studying Collective Decision:
Though individual agents may have a tendency to
take a decision (e.g. to migrate away) that smoothly
increases with time, the collective takes a sharp decision.
"""

# In this story, swallows' tendency to perch (on a wire, say) increases
# smoothly with time. But swallows tend to imitate each other: their
# tendency to join a group of perched birds is proportional to its size
# The simulation shows that at some point, a collective decision to
# perch takes place. This offers an insight into the kind of collective
# processes involved when birds decide to migrate away.



##############################################################################
#  Launching a simulation													#
##############################################################################

""" Simulation Control
"""
import sys
import random
from time import sleep

sys.path.append('../../..')

import Evolife.QtGraphics.Evolife_Window as EW
import Evolife.Ecology.Observer as EO
from Evolife.Scenarii.Parameters import Parameters

WirePosition = 15	# position of the wire on display

Params = Parameters('_Params.evo')

def PerchingProb(Time, TimeSlope, MaxTime):
	" computes the rising probability for an individual swallow to perch down on the wire "
	TimeOffset = 0	# time before considering perching down
	return max(0, min(1.0, 0.002 + ((TimeSlope/1000.0 + 0.001) * (Time - TimeOffset))/MaxTime))

class Swallow_Observer(EO.Experiment_Observer):
	" This class stores values about the simulation "

	def __init__(self):
		EO.Experiment_Observer.__init__(self, Params) # stores global information

		#additional parameters	  
		self.Perched = 0		# number of agents perched
		
		self.curve('#indiv', Color='blue', Legend='proportion of individuals perched')
		self.curve('timeslope', Color='yellow', Legend='perching probability x 1000')

	def Field_grid(self):
		" initial display "
		return [('Wire',(1, WirePosition-3, 'black', 3, self.Parameter('NbAgents'), WirePosition-3, 'grey', 3),)]
	

class Swallow:
	""" Defines individual agents
	"""
	def __init__(self, IdNb):
		self.GroupOffset = Observer.Parameter('GroupOffset')	# minimum size of group worth joinning
		self.Inertia = Observer.Parameter('Inertia')	# minimum time spent on the wire
		self.IdNb = IdNb	# Identity number
		self.Name = 'S%d'   % self.IdNb
		self.TimeSlope = Observer.Parameter('TimeSlope') * random.random()	# time derivative of the probability of perching
		self.GroupSlope = Observer.Parameter('GroupSlope') * random.random() + 0.5  # derivative of the probability of joining a perched group
		self.perched = False
		self.PerchingTime = -1  # last time of perching (-1 if never perched)
		self.Position = random.randint(50,100) # vertical position

	def lands(self, TimeStep, MaxTime, GroupSize, NbAgents):
		" the agent decides to perch on the wire "
		if self.perched and TimeStep < self.PerchingTime + self.Inertia:
			# in this version, perched individuals do not fly up easily 
			return True
		Prob1 = PerchingProb(TimeStep, self.TimeSlope, MaxTime)
		Prob2 = max(0, min(1.0, (0.02 + self.GroupSlope * (GroupSize-self.GroupOffset))/NbAgents))
		if (random.random() < Prob1) or (random.random() < Prob2):
			self.perched = True
			self.Position = WirePosition  # on the wire
			self.PerchingTime = TimeStep
			return True
		else:
			self.perched = False
			self.Position = random.randint(50,100) # new vertical position
			self.PerchingTime = -1
			return False

class Population:
	" defines the population of agents "
	def __init__(self, NbAgents):
		" creates a population of swallow agents "
		self.Pop = [Swallow(IdNb) for IdNb in range(NbAgents)]
		self.PopSize = NbAgents
		self.Perched = 0	# number of swallows on the wire
		self.Decisions = 0
		Observer.record(self.positions())
				 
	def positions(self):
		return [(A.Name,(A.IdNb,A.Position, 'black', 30, 'shape=swallow.gif')) for A in self.Pop]
	
	def One_Decision(self):
		" one swallow is randomly chosen and decides whether to perch or not "
		# This procedure is repeatedly called by the simulation thread
		agent = self.Pop[random.randint(0,self.PopSize-1)]
		OldPosition = agent.perched
		Landing = agent.lands(Observer.StepId, Observer.TimeLimit, self.Perched, self.PopSize)
		if OldPosition != Landing:
			if OldPosition:	self.Perched -= 1
			else:			self.Perched += 1
		self.Decisions += 1
		Observer.season(self.Decisions / self.PopSize)  # sets StepId
		Observer.Perched = self.Perched
		Observer.record((agent.Name,(agent.IdNb,agent.Position, 'black', 30, 'shape=swallow.gif')))
		# Observer.Positions[agent.IdNb] = (agent.Name,(agent.IdNb,agent.Position, 'black', 6))	# last coord = size
		# % of individuals perched
		Observer.curve('#indiv', 100.0 * self.Perched/self.PopSize)
		# perching probability
		Observer.curve('timeslope', 1000 * PerchingProb(Observer.StepId, Observer.Parameter('TimeSlope'), Observer.TimeLimit))
		return agent.IdNb	 

	def Many_decisions(self):
		" every swallow on average has been given a chance to perch down "
		for Sw in range(self.PopSize):
			self.One_Decision()
		return True
	
if __name__ == '__main__':

	print(__doc__)

	Observer = Swallow_Observer()   # Observer contains statistics
	#Observer.recordInfo('Background', 'blue11')	# windows will have this background by default
	Observer.recordInfo('DefaultViews', [('Field', 1100, 700)])	# windows will have this background by default
	Observer.recordInfo('CurvesWallpaper', 'swallow_.gif')
	Pop = Population(Observer.Parameter('NbAgents'))   # set of flying swallows
	
	EW.Start(Pop.Many_decisions, Observer, Capabilities='RCP')

	

__author__ = 'Dessalles'
