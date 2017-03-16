#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################


##############################################################################
#  Evolife (main program)                                                    #
##############################################################################


""" EVOLIFE: Main module :
	Retrieves a scenario from the set of available scenarii
	and launches the window application
"""

###############################
# Analyse of the command line #
###############################

import sys
import os
import os.path
import time	# for sleep

# Retrieving the configuration file name
CfgFileName = ''
for Arg in sys.argv:
	if os.path.splitext(Arg)[1] == '.evo':	CfgFileName = Arg
if CfgFileName == '':	CfgFileName = 'Evolife.evo'

sys.path.append('..')

# Retrieving the name of the scenario
from Evolife.Scenarii.Parameters import Parameters

ScenarioName = ''
ScenarioName = Parameters(CfgFileName)['ScenarioName']
if ScenarioName == '':	ScenarioName = input('Name of the scenario: ')

#####################################
# Creation of the scenario instance #
#####################################

# Instantiating 'MyScenario', which contains :
# - parameters read from the configuration file
# - the organisation of the genome (where genes are located)
# - particular functions that decide how individuals interact
#   in the chosen scenario
import Evolife.Scenarii.MyScenario
ScenarioClass = Evolife.Scenarii.MyScenario.RetrieveScenarioClass(ScenarioName)

# Creation of the scenario instance 
# InstantiateScenario accepts three parameters:
#   - <scenario class>
#   - <scenario name>
#   - <configuration file> (text file containing a list of parameter value pairs)

# Getting the actual scenario
MyScenario = Evolife.Scenarii.MyScenario.InstantiateScenario(ScenarioClass, ScenarioName, CfgFileName)

	


############################################################
# Creation of an observer that collects simulation results #
############################################################

# Observers merely record data that are sent to them
# An EvolifeObserver is an observer that is aware of the kind of data
# resulting from Evolife simulations (average score, best score, genomes, ...)

from Evolife.Ecology.Observer import EvolifeObserver
from Evolife.Genetics.Genetic_map import Genetic_map


Obs = EvolifeObserver(MyScenario)

# printing information
import platform
Obs.TextDisplay('Python: %s on %s (%s)\n' % (platform.python_version(), platform.system(), platform.machine()))
Obs.TextDisplay('\n' + Genetic_map.__repr__(MyScenario)+'\n')
Obs.TextDisplay('\nScenario ' + ScenarioName + ' initialized\n')
	
# import Evolife.Tools.Tools 
# Obs.TextDisplay('(boosting Python: %s)\n' % Evolife.Tools.Tools.boost())


######################################
# Creation of a population of agents #
######################################

# The size of the population is determined in the parameters
# imported into 'MyScenario'

# sys.path.append('Scenarii')
try:
	import Evolife.Ecology.Population

	Pop = Evolife.Ecology.Population.EvolifePopulation(MyScenario, Obs)
	Obs.TextDisplay('%s\n' % Pop)
except:
	# the error stack is displayed
	from sys import excepthook, exc_info
	excepthook(exc_info()[0],exc_info()[1],exc_info()[2])
	input('[Entree]')



####################################################
# Launching the window system (or the batch mode)  #
####################################################


if MyScenario.Parameter('BatchMode') == 0:
	#import Evolife.TkGraphics.Evolife_Window		 # window application
	import Evolife.QtGraphics.Evolife_Window		 # window application
	try:
		#Evolife.TkGraphics.Evolife_Window.Start(Pop.one_year, Obs)
		Evolife.QtGraphics.Evolife_Window.Start(Pop.one_year, Obs, 'CFGLNPT')
	except:
		# the error stack is displayed
		from sys import excepthook, exc_info
		excepthook(exc_info()[0],exc_info()[1],exc_info()[2])
		input('[Entree]')
else:   # Batch mode: No display whatsoever
	import Evolife.QtGraphics.Evolife_Batch
	Evolife.QtGraphics.Evolife_Batch.Start(Pop.one_year, Obs)

# The window system runs the simulation by repeatedly
# calling back the function 'Pop.one_year'


# At this point, the simulation is over


#############################
# Exiting the programme     #
#############################

# saving relevant parameters 
MyScenario.cfg_to_txt('Evolife_' + '.evo') 

if MyScenario['BatchMode'] == 0:
	print(Evolife.Scenarii.MyScenario.signature())
	time.sleep(3.1)
#    raw_input('[Enter]')

__author__ = 'Dessalles'
