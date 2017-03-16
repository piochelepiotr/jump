#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################


##############################################################################
#  Scenario initialization                                                   #
##############################################################################


""" Initialization of the scenario mentioned in Evolife_Defitions
"""


import sys
from os import listdir
from os.path import basename, splitext
from traceback import print_exc


####################################################################
# Definition of the global variable that will contain the scenario #
####################################################################

class MyScenario:	pass


def signature():
	return """
	\t   http://evolife.telecom-paristech.fr
	\t   -----------------------------------
	\t               . . .
	"""
	"""
	\t--------------------------------------------
	\tEvolife - Telecom ParisTech - J-L. Dessalles
	\t	 http://evolife.telecom-paristech.fr
	\t--------------------------------------------\n """

def AvailableScenarii():
	Scenarii = []
	for Dir in sys.path:
		# Looking for all files starting with 'S_' in path
		try:
			Scenarii += [S for S in listdir(Dir) if S.find('S_') == 0]
		except:
			pass
	ScnList = set([splitext(f.split('S_')[1])[0] for f in Scenarii])
	if len(ScnList) > 0:
		print('Available scenarii are: ')
		print('\t\t\t' + '\n\t\t\t'.join(sorted(list(ScnList))), '\n')

def usage():
	print('Usage:', splitext(basename(sys.argv[0]))[0], '<configuration_file (xxx.evo)>')

def RetrieveScenarioClass(ScenarioName):
	""" imports the file containing the scenario to retrieve the scenario class
	"""

	def my_import(name):
		# this function is taken from Python's help
		mod = __import__(name)
		components = name.split('.')
		for comp in components[1:]:
			mod = getattr(mod, comp)
		return mod


	try:
		ScenarioModule = my_import('Evolife.Scenarii.S_' + ScenarioName)
		return ScenarioModule.Scenario
##        return __import__('Evolife.Scenarii.S_' + ScenarioName, globals(), locals(), ['Scenario'])
	except ImportError:
		# The scenario could not be found
		print(signature())
		usage()
		AvailableScenarii()
		print('File S_' + ScenarioName + '.py not found or incorrect\n')
		input('[Enter]')
		print_exc()
		input('[Enter]')
		raise SystemExit('Exiting Evolife')


def InstantiateScenario(ScenarioClass, ScenarioName, CfgFileName=''):
	""" creates an actual scenario by instantiating the corresponding class
	"""

	global MyScenario

	MyScenario = ScenarioClass(Name=ScenarioName, CfgFile=CfgFileName)
	return MyScenario



###############################
# Local Test                  #
###############################

if __name__ == "__main__":
	print(__doc__ + '\n')
	AvailableScenarii()
	input('[Return]')


__author__ = 'Dessalles'
