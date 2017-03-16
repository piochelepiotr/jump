#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################


""" A basic framework to run social simulations
"""


from time import sleep
from random import sample, randint

import sys
import os.path
sys.path.append('../../..')	# to include path to Evolife

import Evolife.Scenarii.Parameters as EP
import Evolife.QtGraphics.Evolife_Window as EW
import Evolife.QtGraphics.Evolife_Batch  as EB
# import Evolife.Scenarii.Parameters 	as EP
import Evolife.Tools.Tools as ET
import Evolife.Ecology.Observer as EO
import Evolife.Ecology.Alliances as EA
import Evolife.Ecology.Learner as EL


# Global elements
class Global(EP.Parameters):
	def __init__(self, ConfigFile='_Params.evo'):
		# Parameter values
		EP.Parameters.__init__(self, ConfigFile)
		self.Parameters = self	# compatibility
		self.ScenarioName = self.Parameter('ScenarioName')
		# Definition of interactions
		self.Interactions = None	# to be overloaded

	def Dump_(self, PopDump, ResultFileName, DumpFeatures, ExpeID, Verbose=False):
		""" Saves parameter values, then agents' investment in signalling, then agents' distance to best friend
		"""
		if Verbose:	print("Saving data to %s.*" % ResultFileName)
		SNResultFile = open(ResultFileName + '_res.csv', 'a')
		SNResultFile.write('%s\n' % ExpeID)	  
		for Feature in DumpFeatures:
			SNResultFile.write("\t".join(PopDump(Feature)))	  
			SNResultFile.write("\n")	  
		SNResultFile.close()
		
	def Param(self, ParameterName):	return self.Parameters.Parameter(ParameterName)


class Social_Observer(EO.Experiment_Observer):
	" Stores some global observation and display variables "

	def __init__(self, Parameters=None):
		EO.Experiment_Observer.__init__(self, Parameters)
		#additional parameters	  
		self.Alliances = []		# social links, for display
		self.curve('FriendDistance', Color='green2', Legend='Avg quality sistance to best friend')
		# self.curve('SignalLevel', 50, Color='yellow', Legend='Avg Signal Level')	
		self.recordInfo('DumpFeatures', ['SignalInvestment', 'DistanceToBestFriend'])
		
	def get_data(self, Slot, Consumption=True):
		if Slot == 'Network':	return self.Alliances			# returns stored links
		return EO.Experiment_Observer.get_data(self, Slot, Consumption=Consumption)

	def hot_phase(self):
		return self.StepId < self.TimeLimit * self.Parameter('LearnHorizon') / 100.0

class Social_Individual(EA.Follower, EL.Learner):
	"   A social individual has friends and can learn "

	def __init__(self, IdNb, features={}, maxQuality=100, parameters=None):
		if parameters: 	self.Param = parameters.Param
		else:	self.Param = None	# but this will provoke an error
		self.id = "A%d" % IdNb	# Identity number
		EA.Follower.__init__(self, self.Param('MaxFriends'), self.Param('MaxFriends'))
		# # if self.Param('SocialSymmetry'):
		# # else:
			# # EA.Follower.__init__(self, self.Param('MaxFriends'), self.Param('MaxFollowers'))
		self.Quality = (100.0 * IdNb) / maxQuality # quality may be displayed
		# Learnable features
		EL.Learner.__init__(self, features, MemorySpan=self.Param('MemorySpan'), AgeMax=self.Param('AgeMax'), 
							Infancy=self.Param('Infancy'), Imitation=self.Param('ImitationStrength'), 
							Speed=self.Param('LearningSpeed'), Conservatism=self.Param('LearningConservatism'), toric=self.Param('Toric'))
		self.Points = 0	# stores current performance
		self.update()

	def Reset(self):	# called by Learner when born again
		self.forgetAll()	# erase friendships
		EL.Learner.Reset(self)
		
	def update(self, infancy=True):
		"	updates values for display "
		Colour = 'green%d' % int(1 + 10 * (1 - float(self.Age)/(1+self.Param('AgeMax'))))
		if infancy and not self.adult():	Colour = 'red'
		if self.Features:	y = self.Features[self.Features.keys()[0]]
		else:	y = 17
		self.Position = (self.Quality, y, Colour)


	def Interact(self, Partner):	
		pass	# to be overloaded
		return True

	def assessment(self):
		" Social benefit from having friends "
		pass		# to be overloaded
		return self.Points	
		
	def __str__(self):
		return "%s[%s]" % (self.id, str(self.Features))
		
class Social_Population:
	" defines a population of interacting agents "

	def __init__(self, parameters, NbAgents, Observer, IndividualClass=None):
		" creates a population of agents "
		if IndividualClass is None:	IndividualClass = Social_Individual
		self.Pop = [IndividualClass(IdNb, maxQuality=NbAgents, parameters=parameters) for IdNb in range(NbAgents)]
		self.PopSize = NbAgents
		self.Obs = Observer
		# self.Obs.Positions = self.positions()
		self.Param = parameters.Param
				 
	def positions(self):	return [(A.id, A.Position) for A in self.Pop]

	def neighbours(self, Agent):
		" Returns a list of neighbours for an agent "
		AgentQualityRank = self.Pop.index(Agent)
		return [self.Pop[NBhood] for NBhood in [AgentQualityRank - 1, AgentQualityRank + 1]
				if NBhood >= 0 and NBhood < self.PopSize]
		  
	def SignalAvg(self):
		Avg = 0
		for I in self.Pop:	Avg += I.SignalLevel
		if self.Pop:	Avg /= len(self.Pop)
		return Avg
	
	def FeatureAvg(self, Feature):
		Avg = 0
		for I in self.Pop:	Avg += I.feature(Feature)
		if self.Pop:	Avg /= len(self.Pop)
		return Avg
	
	def FriendDistance(self):	
		FD = []
		for I in self.Pop:	
			BF = I.best_friend()
			if BF:	FD.append(abs(I.Quality - BF.Quality))
		if FD:	return sum(FD) / len(FD)
		return 0
		
	def display(self):
		if self.Obs.Visible():	# Statistics for display
			for agent in self.Pop:
				agent.update(infancy=self.Obs.hot_phase())	# update position for display
				# self.Obs.Positions[agent.id] = agent.Position	# Observer stores agent position 
			# Observer stores social links
			self.Obs.Alliances = [(agent.id, [T.id for T in agent.social_signature()]) for agent in self.Pop]
			self.Obs.record(self.positions())
			# self.Obs.curve('SignalLevel', self.SignalAvg())
			# self.Obs.curve('FriendDistance', self.FriendDistance())
			if self.Pop:
				Features = self.Pop[0].Features
				Colours = ['blue', 'yellow', 'red', 'white', 'brown']
				C = 0
				for F in sorted(list(Features.keys())):
					self.Obs.curve(F, self.FeatureAvg(F), Color=Colours[C], Legend='Avg of %s' % F)
					C += 1

	def season_initialization(self):
		for agent in self.Pop:
			# agent.lessening_friendship()	# eroding past gurus performances
			if self.Param('EraseNetwork'):	agent.forgetAll()
			agent.Points = 100
	
	def interactions(self):
		successful = 0
		for Run in range(self.Param('NbInteractions')):
			(Player, Partner) = sample(self.Pop, 2)
			if Partner.Interact(Player):	successful += 1
		# if randint(1, 100) < 10:
			# print '%d%%' % int((100.0 * successful) / self.Param('NbInteractions')),
	
	def learning(self):
		for agent in self.Pop:	agent.assessment()	# storing current scores (with possible cross-benefits)
		# some agents learn
		Learners = sample(self.Pop, ET.chances(self.Param('LearningProbability')/100.0, len(self.Pop)))	
		for agent in self.Pop:
			agent.wins(agent.Points)	# Stores points for learning
			if agent in Learners:
				if not agent.Learns(self.neighbours(agent), hot=self.Obs.hot_phase()):
					# agent.update()	# this is a newborn - update position for display
					pass
				agent.update()	# update position for display
				# self.Obs.Positions[agent.id] = agent.Position
				
	def One_Run(self):
		# This procedure is repeatedly called by the simulation thread
		# ====================
		# Display
		# ====================
		self.Obs.season()	# increments year
		self.display()
		# ====================
		# Interactions
		# ====================
		for Run in range(self.Param('NbRunPerYear')):	
			self.season_initialization()
			self.interactions()
			self.learning()
		return True	# This value is forwarded to "ReturnFromThread"

		
		
def Start(Params=None, PopClass=Social_Population, ObsClass=Social_Observer, Windows='FNC'):
	if Params is None:	Params = Global()
	Observer = ObsClass(Params)   # Observer contains statistics
	Observer.setOutputDir('___Results')
	Views = [('Field', 500, 350), ('Network', 530, 200)]
	if 'T' in Windows:	Views.append(('Trajectories', 500, 350))
	Observer.recordInfo('DefaultViews',	Views)	# Evolife should start with that window open
	# Observer.record((100, 100, 0, 0), Window='Field')	# to resize the field
	Pop = PopClass(Params, Params.Param('NbAgents'), Observer)   # population of agents
	BatchMode = Params.Param('BatchMode')
	
	if BatchMode :
		####################
		# Batch mode
		####################
		# # # # for Step in range(Gbl.Param('TimeLimit')):
			# # # # #print '.',
			# # # # Pop.One_Run()
			# # # # if os.path.exists('stop'):	break
		EB.Start(Pop.One_Run, Observer)
		# writing header to result file
		open(Observer.get_info('ResultFile')+'_res.csv', 'w').write(Observer.get_info('ResultHeader'))
	else:
		####################
		# Interactive mode
		####################
		print(__doc__)
		" launching window "
		try:
			EW.Start(Pop.One_Run, Observer, Capabilities=Windows+'P', Options=[('Background','lightblue')])
		except Exception as Msg:
			from sys import excepthook, exc_info
			excepthook(exc_info()[0],exc_info()[1],exc_info()[2])
			input('[Entree]')
		print("Bye.......")
		
	Params.Dump_(Pop.Dump, Observer.get_info('ResultFile'), Observer.get_info('DumpFeatures'), 
					Observer.get_info('ExperienceID'), Verbose = not BatchMode)
	sleep(2.1)	
	return
	


if __name__ == "__main__":
	Gbl = Global()
	Start(Gbl)



__author__ = 'Dessalles'
