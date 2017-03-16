#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################


##############################################################################
#  Phenotype                                                                     #
##############################################################################

""" EVOLIFE: Module Phenotype:
		Definition of phenotype as non inheritable characters
"""

import sys
if __name__ == '__main__':  sys.path.append('../..')  # for tests



import random
from Evolife.Tools.Tools import error



class Phene:
	" class Phene: define a non-heritable characteristics "

	MaxPheneValue = 100

	def __init__(self, Name, FlagRandom=True):
		self.Name = Name
		if FlagRandom:
			self.__value = random.randint(0, self.MaxPheneValue)
		else:
			self.__value = 0

	def relative_value(self):
		return (100.0 * self.__value) / self.MaxPheneValue

	def value(self, Value=None, Levelling = False):
		if Value is None:	return self.__value
		if Value <= Phene.MaxPheneValue:	self.__value = Value
		elif Levelling:	self.__value = Phene.MaxPheneValue
		else:	error("Phenotype: ", "Maximum value exceeded")
		return self.__value

	def __repr__(self):
		return self.Name + '=' + "%d" % self.value()
	
class Phenome:
	"   class Phenome: set of non inheritable characteristics "

	def __init__(self, Scenario, FlagRandom = True):
		self.Scenario = Scenario
		self.Phenes = dict([(PN, Phene(PN,FlagRandom))
							for PN in self.Scenario.phenemap()])   

	def Phene_value(self, name, Value=None, Levelling=False):
		" reads or sets the value of a phene "
		return self.Phenes[name].value(Value, Levelling)

	def Phene_relative_value(self, name):
		return self.Phenes[name].relative_value()
	
	def signature(self):
		return [self.Phenes[PN].relative_value() for PN in self.Scenario.phenemap()]
				
	def __repr__(self):
		return 'Phenotype:\n ' + ' <> '.join([Ph.__repr__() for Ph in self.Phenes.values()])




if __name__ == "__main__":
	print(__doc__)
	from Evolife.Scenarii.MyScenario import InstantiateScenario
	InstantiateScenario('Signalling')
	from Evolife.Scenarii.MyScenario import MyScenario
	Ph = Phenome(FlagRandom = True)
	print(Ph)
	raw_input('[Return]')


__author__ = 'Dessalles'
