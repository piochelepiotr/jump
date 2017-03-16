#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################


##############################################################################
#  Learner                                                                   #
##############################################################################

""" EVOLIFE: Module Learner:
		Simple trial-and-error learning mechanism """

if __name__ == '__main__':  # for tests
	import sys
	sys.path.append('../..')
	# from Evolife.Scenarii.MyScenario import InstantiateScenario
	# InstantiateScenario('SexRatio')


from random import random, randint
from Evolife.Tools.Tools import boost, LimitedMemory, error

# Global elements
class Global:
	def __init__(self):
		# General functions
		# Closer pushes x towards Target
		self.Closer = lambda x, Target, Attractiveness: ((100.0 - Attractiveness) * x + Attractiveness * Target) / 100
		# Perturbate is a mutation function
		self.Perturbate = lambda x, Amplitude: x + (2 * random() - 1) * Amplitude
		# Limitate keeps x within limits
		self.Limitate = lambda x, Min, Max: min(max(x,Min), Max)
		# Decrease is a linear decreasing function between 100 and MinY
		self.Decrease = lambda x, MaxX, MinY: max(MinY, (100 - x * ((100.0 - MinY)/ MaxX)))


Gbl = Global()

class Learner:
	"	defines learning capabilities "
	def __init__(self, Features, MemorySpan=5, AgeMax=100, Infancy=0, Imitation=0, Speed=3, Conservatism=0, toric=False):	
		self.Features = Features	# Dictionary of variables: values that will be learned
		self.MemorySpan = MemorySpan
		self.Scores = LimitedMemory(self.MemorySpan)  # memory of past benefits
		self.AgeMax = AgeMax
		self.Performance = []	# stores current performances
		self.Infancy = Infancy	# percentage of lifetime when the learner is considered a child
		self.Imitation = Imitation	# forced similarity wiht neighbouring values when learning continuous function
		self.Speed = Speed	# learning speed
		self.Conservatism = Conservatism
		self.Toric = toric
		self.Reset()
		self.Age = randint(0, AgeMax)	# age is random at initialization
		
	def Reset(self):
		self.Age = 0
		for F in self.Features:	self.Features[F] = randint(0,100)
		# for F in self.Features:	self.Features[F] = 0
		self.Scores.reset()

	def adult(self):	return self.Age > self.AgeMax * self.Infancy / 100.0

	def feature(self, F, Value=None):
		if F is None:	F = list(self.Features.keys())[0]	
		if Value is not None:	self.Features[F] = Value
		return self.Features[F]

	def Limitate(self, x, Min, Max):
		if self.Toric: return (x % Max)
		else:	return Gbl.Limitate(x, Min, Max)
	
	
	def imitate(self, models, Feature):
		" the individual moves its own feature closer to its models' features "
		TrueModels = [m for m in models if m.adult()]
		if TrueModels:
			ModelValues = list(map(lambda x: x.feature(Feature), TrueModels))
			Avg = float(sum(ModelValues)) / len(ModelValues)
			return Gbl.Closer(self.feature(Feature), Avg, self.Imitation)
		return self.feature(Feature)

	def bestRecord(self, second=False):
		" retrieve the best (or the second best) solution so far "
		# print self.Scores.past
		if self.Scores.Length() > 0:
			if self.Scores.Length() > 1:
				# retrieve the best solution so far
				past = self.Scores.retrieve()[:]
				Best = max(past, key = lambda x: x[1])
				if second:	
					# retrieve the SECOND best solution so far
					past.remove(Best)
					Best = max(past, key = lambda x: x[1])
			else:
				Best = self.Scores.last()
		else:	Best = None
		return Best
		
	
	def explore(self, Feature, Speed):
		"   the individual changes its feature to try to get more points "
		try:	Best = self.bestRecord(second=True)[0][Feature]
		except (TypeError, IndexError):	Best = self.Features[Feature]
		# print self.Scores, sorted(self.Scores.retrieve(), key = lambda x: x[1])[-1]
		# print self.feature(Feature),
		# print Feature, self.Scores.past
		Target = self.Limitate(Gbl.Perturbate(Best, Speed), 0, 100)
		return Gbl.Closer(Target, self.feature(Feature), self.Conservatism)

	def Learns(self, neighbours, hot=True):
		""" Learns by randomly changing current value.
			Starting point depends on previous success and on neighbours.
			If 'hot' is true, perturbation is larger for children 
		"""
		if self.Age > self.AgeMax:
			self.Reset()
		self.Age += 1
		# Averaging performances obtained for current feature values
		Performance = 0
		if len(self.Performance): Performance = float(sum(self.Performance)) / len(self.Performance)
		self.Performance = []	# resetting performance
		self.Scores.push((self.Features.copy(), Performance))	# storing current performance
		if self.Age == 1:	return False	# Newborn, no learning

		# (1) imitation
		FeatureNames = list(self.Features.keys()) # safer to put 'list'
		# get features closer to neighbours' values
		if self.Imitation:
			for F in FeatureNames:	self.feature(F, self.imitate(neighbours, F))

		# (2) exploration
		if hot and not self.adult():	# still a kid
			LearningSpeed = Gbl.Decrease(self.Age, self.Infancy, self.Speed)
		else:	LearningSpeed = self.Speed
		# compromise between current value and a perturbation of past best value
		for F in FeatureNames:	self.feature(F, self.explore(F, LearningSpeed))
		return True

	def wins(self, Points):
		"   stores a benefit	"
		self.Performance.append(Points)
	
	def __str__(self):	return str(self.Features)



			
###############################
# Local Test                  #
###############################

if __name__ == "__main__":
	print(__doc__)
	print(Learner.__doc__ + '\n\n')
	John_Doe = Learner({'F':0})
	print("John_Doe:\n")
	print(John_Doe)
	raw_input('[Return]')


__author__ = 'Dessalles'
