#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################

##############################################################################
# Travelling salesperson problem                                             #
##############################################################################

""" Travelling salesperson problem:
'Ants' travel through the road network.
They lay down pheromone.
"""



import sys
from time import sleep
import random
		
sys.path.append('..')
sys.path.append('../../..')
import Evolife.Scenarii.Parameters			as EPar
import Evolife.Ecology.Observer				as EO
import Evolife.Ecology.Individual			as EI
import Evolife.Ecology.Group				as EG
import Evolife.Ecology.Population			as EP
import Evolife.QtGraphics.Evolife_Window	as EW
import Evolife.Tools.Tools					as ET

print(ET.boost())	# significantly accelerates python on some platforms


from Antnet import Antnet_Observer, Node, Network, Ant, Group, Population

#################################################
# Aspect of ants, food and pheromons on display
#################################################
LinkAspect = ('green5', 2)	# 2 = thickness
AntAspect = ('black', 5)	# 4 = size
AntAspectWhenOld = ('red5', 4)	# 4 = size
PPAspect = (17, 2)	# 17th colour
	
class City(Node):
	def __init__(self, Name, Location):
		Node.__init__(self, Name, Location)
		self.Distance = {}	# distances to neighbour cities
		self.Pheromone = {}	# pheromone to neighbour cities
		
	def Attractiveness(self, city):
		" returns the city's attractiveness as a compromise between distance and pheromone "
		return self.Pheromone[city] ** Gbl.Parameter('PheromoneAttraction') + self.Distance[city] ** Gbl.Parameter('DistanceAttraction')
	
	def ChooseNeighbour(self):
		
	
class RoadNetwork(Network):
	def __init__(self, Size=100, NbNodes=0):
		Network.__init__(self, Size, NbNodes)
		self.Distance = dict([((n1,n2), n1.distanceTo(n2)) for (n1,n2) in self.Links])
		self.Pheromone = dict([((n1,n2), 0) for (n1,n2) in self.Links])
		
		
class TSPAnt(Ant):

	def __init__(self, Scenario, IdNb, InitialNode):
		Ant.__init__(self, Scenario, IdNb, InitialNode)
		self.Tour = []	# current tour
		
	def Sniff(self):
		" Looks for the next place to go "
		# The ant makes a biased choice of its next location
		# There is an exploitation/exploration dilemma
		# exploitation = pheromone
		# exploration = short distance and probability
		try:
			Neighbourhood = [(n, n.Table[self.location]) for n in self.location.Prenodes()]
		except KeyError:
			print('%s and %s are not symmetrically linked' % (self.location, str(self.location.Prenodes())))
		Lottery = random.uniform(0, sum([n[1] for n in Neighbourhood]))
		p = 0	# cumulative probability
		for n in Neighbourhood:
			p += n[1]
			if p >= Lottery:	break
		return n[0]


	def moves(self, Time):
		if self.Age >= Gbl.Parameter('AgeMax'):
			# the ant is reborn
			self.location = self.Origin		# location in the network
			self.target = None		# future location in the network
			self.position = 0	# physical location between two nodes
			self.Age = 0 
			return True
		while Time >= self.time + Gbl.Parameter('NbSteps'):
			# the ant has reached the next node
			if self.target is not None:		
				self.target.TableUpdate(self.location, self.Age)
				self.location = self.target
				self.Age += 1
			self.target = self.Sniff()		# new target
			self.time += Gbl.Parameter('NbSteps')
		NewPosition = max(0, Time - self.time)
		if NewPosition != self.position:
			# print('moving from', self.position, 'to', NewPosition)
			self.position = NewPosition
			return True
		return False
		
if __name__ == "__main__":
	print __doc__

	#############################
	# Global objects			#
	#############################
	Gbl = EPar.Parameters('_Params.evo')	# Loading global parameter values
	Observer = Antnet_Observer(Gbl)   # Observer contains statistics
	Ntwrk = Network(Size=Gbl.Parameter('LandSize'))
	Pop = Population(Gbl, Observer, Ntwrk.nodes())   # Ant colony
	
	# Initial draw
	Observer.recordInfo('FieldWallpaper', 'yellow')
	Observer.recordChanges(('Dummy',(Gbl.Parameter('LandSize'), Gbl.Parameter('LandSize'), 0, 1)))	# to resize the field
	for link in Ntwrk.draw():	Observer.recordChanges(link) # for intial display of network

	EW.Start(Pop.One_Decision, Observer, Capabilities='RPC')

	print "Bye......."
	sleep(1.0)
##	raw_input("\n[Return]")

__author__ = 'Dessalles'
