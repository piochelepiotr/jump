#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################



""" EVOLIFE: Runaway selection

The mechanism of 'Runaway selection' has been imagined by Ron Fischer to explain extravagant 
features such as the peacock tail as results of sexual selection.	

	

"""

	#=============================================================#
	#  HOW TO MODIFY A SCENARIO: read Default_Scenario.py		 #
	#=============================================================#


import random
import sys
from Evolife.Scenarii.Default_Scenario import Default_Scenario
from Evolife.Tools.Tools import error, chances

Numpy = True
try:	import numpy
except ImportError:	Numpy = False

######################################
# specific variables and functions   #
######################################


class Scenario(Default_Scenario):

	######################################
	# All functions in Default_Scenario  #
	# can be overloaded				  #
	######################################

	def initialization(self):
		self.GeneCorrelation = 0 # Will measure the correlation between the two genes
		self.FemaleActualDemand = 0 # converts the female gene into actual demand
	
	def genemap(self):
		""" Defines the name of genes and their position on the DNA.
		"""
		return ['FemaleDemand', 'MaleInvestment'] 	

	def phenemap(self):
		""" Defines the set of non inheritable characteristics
		"""
		if True:
			# ........  To be changed ........
			return ['Sex', 'MaleQuality']  # Sex is considered a phenotypic characteristic !
						# This is convenient because sex is determined at birth and is not inheritable
						# Male quality is what will be signalled by males.
			# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

	def female(self, Indiv):
		if Indiv.Phene_value('Sex') > 50:	return True
		return False
		
	def male(self, Indiv):
		if Indiv.Phene_value('Sex') <= 50:	return True
		return False

	def start_game(self, members):
		""" defines what is to be done at the group level each year
			before interactions occur - Used in 'life_game'
		"""
		
		# setting scores
		self.FemaleActualDemand = 0
		for indiv in members:
			# individuals get a capital in points
			indiv.score(min(self.Parameter('MaleSignallingCost'), self.Parameter('FemaleDemandCost')), FlagSet=False)
			
			if self.male(indiv):	
				# males pay proportional cost for signalling
				indiv.score(-indiv.gene_relative_value('MaleInvestment') * self.Parameter('MaleSignallingCost')/100.0)
			else:
				# females pay proportional cost for being demanding
				indiv.score(-indiv.FD * self.Parameter('FemaleDemandCost')/100.0)

			self.FemaleActualDemand += indiv.FD		# to compute average value
		if len(members):	self.FemaleActualDemand /= len(members)	# average value

		# Computing gene correlation
		if Numpy:
			C = numpy.corrcoef([i.gene_value('FemaleDemand') for i in members], [i.gene_value('MaleInvestment') for i in members])[0][1]
			if numpy.isnan(C):	C = 0	# check for undefined results
			self.GeneCorrelation = C	


	def parenthood(self, RankedCandidates, Def_Nb_Children):
		" Determines the number of children "
		# Polygamy: males get a higher number of potential children than females
		candidates = [[m,0] for m in RankedCandidates]
		for P in candidates:
			# call to 'chances' allow parameters < 1
			if self.female(P[0]):	P[1] = chances(1, self.Parameter('FemaleFertility'))
			elif self.male(P[0]):	P[1] = chances(1, self.Parameter('MaleFertility'))
		return candidates
		
	def parents(self, Candidates):						
		"""	Demanding females will compare more males based on their signals
			Candidates are (indiv, NbChildren) pairs, where NbChildren indicates the number of
			children that indiv can still have
		"""
		females = [F for F in Candidates if self.female(F[0])]
		males = [M for M in Candidates if self.male(M[0])]
		if len(females) == 0:	return None
		if len(males) == 0:	return None
		mother = random.choice(females)
		bestSignal = 0
		father = None
		for trial in range(1+int(mother[0].FD * self.Parameter('MaxCourtship') / 100.0)):
			# print(int(bestSignal), end=' ', flush=True)
			male = random.choice(males)
			MaleQuality = male[0].Phene_value('MaleQuality')
			signal = male[0].gene_relative_value('MaleInvestment') * MaleQuality
			if signal >= bestSignal:
				bestSignal = signal
				father = male
		if father:	
			# the male's quality may influence the female's viability (e.g. if he has parasites)
			FatherQuality = father[0].Phene_value('MaleQuality')
			if True:
				# ........  To be changed ........
				mother[0].score(-(100-FatherQuality) * self.Parameter('LowQualityCost') / 100.0)
				# user self.Parameter('ParasiteProbability') to make penalty binary rather than proportional
				# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
			return (mother, father)
		return None
			
	def new_agent(self, child, parents):
		" initializes newborns - parents==None when the population is created"
		# Gene 'FemaleDemand' is interpreted as generating zero demand if < 50.
		# The purpose is to avoid a 'wall effect'.
		# Mutation are now as likely to cancel female demand as to increase it.
		child.FD = 2 * max(0, child.gene_relative_value('FemaleDemand') - 50)	
		if True:
			# ........  To be changed ........
			pass
			# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
		return True

	
	def update_positions(self, members, groupLocation):
		" Allows to define spatial coordinates for individuals. "
		for m in members:
			colour = 'pink' if self.female(m) else 'lightblue'
			if self.female(m):
				m.location = (groupLocation + m.FD, random.randint(1,99), colour, 6)
			else:
				m.location = (groupLocation + m.Phene_value('MaleQuality'),
					m.gene_relative_value('MaleInvestment'), colour, 6)		

					
	def local_display(self, ToBeDisplayed):
		" allows to diplay locally defined values "
		if ToBeDisplayed == 'Correlation':
			return 50 * (1 + self.GeneCorrelation)  # displaying correlation around 50
		if ToBeDisplayed == 'FemaleActualDemand':	return self.FemaleActualDemand
		return None

	def display_(self):
		""" Defines what is to be displayed. 
		"""
		disp = [('red', 'FemaleActualDemand', 'Average value of female demand for signal in the population'), ('blue', 'MaleInvestment')]
		disp.append(('white', 'Correlation', 'Correlation between the two genes'))
		return disp
		
	def default_view(self):	return ['Field', 'Legend']
	
	def legends(self):
		return """<u>Field window</u>:<P>
		    Pink dots: Females horizontally ranked by demand
		<br>Blue dots: Males horizontally ranked by quality and vertically by investment
		<P>
		"""	+ Default_Scenario.legends(self)

	def wallpaper(self, Window):
		" displays background image or colour when the window is created "
		# Possible windows are: 'Field', 'Curves', 'Genome', 'Log', 'Help', 'Trajectories', 'Network'
		if Window == 'Field':	return 'yellow'
		elif Window == 'Curves':	return 'Scenarii/Line_50.png'	# horizontal line at y=50
		return Default_Scenario.wallpaper(self, Window)
		
		
###############################
# Local Test                  #
###############################

if __name__ == "__main__":
	print(__doc__ + '\n')
	SB = Scenario()
	input('[Return]')
	
