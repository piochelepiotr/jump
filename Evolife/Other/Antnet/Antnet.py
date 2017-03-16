#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################

##############################################################################
# AntNet                                                                       #
##############################################################################

""" Antnet:
'Ants' travel through the network.
Messages choose nodes ants come from.
"""



import sys
from time import sleep
import random
import re
		
sys.path.append('..')
sys.path.append('../../..')
import Evolife.Scenarii.Parameters			as EPar
import Evolife.Ecology.Observer				as EO
import Evolife.QtGraphics.Evolife_Window	as EW
import Evolife.Tools.Tools					as ET


#################################################
# Aspect of ants, food and pheromons on display
#################################################
LinkAspect = ('green3', 2)	# 2 = thickness
AntAspect = ('black', 5)	# 4 = size
AntAspectWhenOld = ('brown', 4)	# 4 = size
MessagePathAspect = ('blue', 4)	# 4 = thickness

#################################################
# Other constants
#################################################
# . . .
	
class Antnet_Observer(EO.Observer):
	""" Stores global variables for observation
	"""
	def __init__(self, Scenario):
		EO.Observer.__init__(self, Scenario)
		self.Positions = []	# stores temporary changes of ant position
		self.Trajectories = []	# stores temporary changes
		# self.recordInfo('CurveNames', [('yellow', 'Year (each ant moves once a year on average)')])
		self.MsgLength = dict()

	def recordChanges(self, Info, Slot='Positions'):
		# stores current changes
		# Info is a couple (InfoName, Position) and Position == (x,y) or a longer tuple
		if Slot ==  'Positions':	self.Positions.append(Info)
		elif Slot == 'Trajectories':	self.Trajectories.append(Info)
		else:	ET.error('Antnet Observer', 'unknown slot')

	def get_info(self, Slot, default=None):
		" this is called when display is required "
		if Slot == 'PlotOrders':
			return [(10+M[0], (self.StepId//Gbl.Parameter('PopulationSize'), 
					self.MsgLength[M[1]])) for M in enumerate(list(self.MsgLength.keys()))]	# curves
		elif Slot == 'CurveNames':	
			return [(10+M[0], 'Message #%d' % M[0]) for M in enumerate(list(self.MsgLength.keys()))]
		elif Slot == 'Trajectories':
			CC = self.Trajectories
			self.Trajectories = []
			return tuple(CC)
		else:	return EO.Observer.get_info(self, Slot, default=default)
		
	def get_data(self, Slot):
		if Slot == 'Positions':
			CC = self.Positions
			# print CC
			self.Positions = []
			return tuple(CC)
		else:	return EO.Observer.get_data(self, Slot)

class Node:
	"""	Defines a node of the communication network
	"""
	def __init__(self, Name, Location):
		self.Name = Name
		self.Location = Location	# physical location
		self.Neighbours = []	# Nodes linked to self
		self.Table = {}	# Routing table: for each target node, probabilities to move to neighbouring nodes
		self.Ages = {}	# For each target node, minimum age of incoming ants
		self.Load = 0	# Current load of the node
		self.time = 0	# keeps time of last load change
		self.Size = 3	# for display
		self.Colour = 'blue'	# for display
	
	def NextNode(self, Target, deterministic=False):
		" determines the most attractive neighbouring node when heading to Target"
		if len(self.Table):
			if deterministic:
				return max([(self.Table[Target][n], n) for n in self.Table[Target]])[1]
			return list(self.Table[Target].keys())[ET.fortune_wheel(self.Table[Target].values())]
		return None

	def CreateTable(self, Nodes, Neighbours):
		" A routing table indicates, for each target node, the probability of choosing a neighbouring node "
		self.Neighbours = Neighbours
		for n in Nodes:
			if n == self:	continue
			self.Table[n] = {}
			for p in Neighbours:
				self.Table[n][p] = 1.0
	
	def TableUpdate(self, Target, NeighnourNode, AntAge):
		" updates the routing table when an ant arrives "
		if Target in self.Ages and AntAge >= self.Ages[Target]:	pass
		else:	self.Ages[Target] = AntAge	# update minimum age
		AgeDelta = AntAge - self.Ages[Target]
		delta = Gbl.Parameter('AntInfluence') / (100.0*(1 + AgeDelta))
		self.Table[Target][NeighnourNode] *= (1 + delta)
		self.TableNormalization(Target)
		
	def TableNormalization(self, Target):
		" restores normalization of probabilities "
		S = sum([self.Table[Target][n] for n in self.Table[Target]])
		if S:
			for n in self.Table[Target]:
				self.Table[Target][n] /= S
		
	def visit(self, currentTime):
		" each visit updates the Load "
		# Load decays with time
		NewLoad = max(0, self.Load - Gbl.Parameter('LoadDecay') * (currentTime - self.time) /100.0)
		self.Load = NewLoad + 1	# taking the current visit into account
		return self.Load
		
	def draw(self):	return self.Location + (self.Colour, self.Size)
	
	def highlight(self):	self.Colour = 'red'; self.Size = 8
	
	def __lt__(self, other):	return  self.Name < other.Name	# just for display
	
	def __repr__(self):	return self.Name + str(self.Location)
		
class Network:
	"""	Defines a network as a graph
	"""
	def __init__(self, Size=100, NbNodes=0, NetworkFileName=None):
		self.TestMessages = []	# Messages used to test the efficiency of the network
		margin = 5 if Size > 20 else 0
		self.NodeNames = {}
		self.Nodes = []
		self.Links = []
		if Gbl.Parameter('RandomNetwork') and NbNodes > 1:
			self.Nodes = [Node('N%d' % i, (random.randint(margin, Size-margin), random.randint(margin, Size-margin))) for i in range(NbNodes)]
			if NbNodes > 1:
				for n in self.Nodes:
					OtherNodes = self.Nodes[:]
					OtherNodes.remove(n)	# does not need to be efficient
					if OtherNodes:
						self.Links.append((n, random.choice(OtherNodes)))
						self.Links.append((n, random.choice(OtherNodes)))
			self.Links = list(set(self.Links))	# to remove duplicates
			self.NodeNames = dict([(n.Name, n) for n in self.Nodes])
		else:	# loading network from file
			#	file format:
			#		Name1	x1	y1
			#		Name2	x2	y2
			#		...
			#		Link	NameA	NameB	C	(C = capacity)
			#		...
			#	('Link' = keyword)
			LinkDefinitions = []
			try:
				for Line in open(Gbl.Parameter('NetworkFileName'), 'r', 1):	# read one line at a time
					Link = re.match('(?i)link\s+(.*)', Line)
					if Link is not None:	LinkDefinitions.append(Link.group(1).split())
					elif Line:	
						NodeDef = Line.split()
						self.Nodes.append(Node(NodeDef[0], tuple(map(int, NodeDef[1:]))))
						self.NodeNames[NodeDef[0]] = self.Nodes[-1]
			except IOError:	ET.error('Unable to find Network description', Gbl.Parameter('NetworkFileName'))
			for L in LinkDefinitions:	
				self.Links.append((self.NodeNames[L[0]],self.NodeNames[L[1]],))
			for N in self.Nodes:	print(N)
		self.Size = len(self.Nodes)
		
		self.TestMessages = [Message('M1', self.Nodes[0], self.Nodes[1])]
		
		# Creating routing tables
		for n in self.Nodes:	n.CreateTable(self.Nodes, self.Neighbours(n))
				
	def nodes(self):	return self.Nodes
	
	def Neighbours(self, Node):
		return [n for n in self.Nodes if (Node, n) in self.Links or (n, Node) in self.Links]
			
	def draw(self):
		" returns drawing instructions "
		return list(map(lambda x: ('L%d' % x[0], x[1]), 
				list(enumerate([n1.draw()  + n2.Location + LinkAspect for (n1, n2) in self.Links]))))
	   
	   
class Ant:
	""" Defines individual agents
	"""
	def __init__(self, IdNb, InitialNode=None):
		self.ID = IdNb
		self.Origin = InitialNode	# Ants have a birth place and keep it
		self.location = InitialNode		# location in the network
		self.target = None		# future location in the network
		self.position = 0	# physical location between two nodes
		self.Age = 0 
		self.NbSteps = 1	# number of hops when displaying travel between two nodes
		# 'time' keeps track of time of last visit to a node
		self.time = random.randint(1, 1+ int(IdNb[1:]) * Gbl.Parameter('AgeMax'))	 # for desynchronized display

	def dead(self):	return False # eternal beings
	
	def Sniff(self):
		" Looks for the next place to go "
		# The ant makes a biased choice of its next location
		# More probable links leading from neighbouring nodes to the ant's origin are more likely to be chosen
		Neighbours = self.location.Neighbours[:]
		if self.Origin in Neighbours: Neighbours.remove(self.Origin)
		Probabilities = [n.Table[self.Origin][self.location] for n in Neighbours]
		if Probabilities:
			NodeRank = ET.fortune_wheel(Probabilities)	# chooses a neighbour based on probabilities
			return Neighbours[NodeRank]
		return None

	def moves(self, Time, NbSteps):
		self.NbSteps = max(1, NbSteps)
		if self.Age >= Gbl.Parameter('AgeMax'):
			# the ant is reborn
			self.location = self.Origin		# location in the network
			self.target = None		# future location in the network
			self.Age = 0 
		while Time >= self.time + self.NbSteps:
			# the ant has reached the next node
			if self.target is not None:
				self.target.TableUpdate(self.Origin, self.location, self.Age)
				self.location = self.target
				# self.Age += self.location.visit(Time)	# loaded nodes grow you old
				self.Age += 1
			self.target = self.Sniff()		# new target
			self.time += self.NbSteps
		NewPosition = Time - self.time
		if NewPosition != self.position:
			# print('moving from', self.position, 'to', NewPosition)
			self.position = NewPosition
			return True if self.position >= 0 else False	# otherwise delay at birth
		return False
		
	def draw(self):
		" returns drawing instructions "
		return (self.ID, self.coordinates() + (AntAspect if self.young() else AntAspectWhenOld))

	def young(self):	return self.Age < Gbl.Parameter('AgeMax') / 2
			
	def coordinates(self):
		" interpolates between last visited node and target node "
		(x1, y1) = self.location.Location
		if self.target is None:	return (x1,y1)
		(x2, y2) = self.target.Location
		x = int(x1 + (x2-x1) * self.position / float(self.NbSteps))
		y = int(y1 + (y2-y1) * self.position / float(self.NbSteps))
		return (x,y)
		

class Message(Ant):
	""" Messages travel through the network by following routing table deterministically
	"""
	def __init__(self, IdNb, InitialNode, TargetNode):	
		Ant.__init__(self, IdNb, InitialNode=InitialNode)
		self.Destination = TargetNode
		self.Origin.highlight()
		self.Destination.highlight()
		self.CurrentPath = []
		
		
	def Sniff(self):
		return self.location.NextNode(self.Destination)
		
	def Path(self, MaxPath=50):
		self.location = self.Origin
		self.CurrentPath = [self.Origin]
		while self.location != self.Destination:
			self.location = self.location.NextNode(self.Destination, deterministic=True)
			if self.location is not None: self.CurrentPath.append(self.location)
			if len(self.CurrentPath) > MaxPath:	break	# completely lost
		return self.CurrentPath

	def erase(self):	return self.drawPath(self.CurrentPath, LinkAspect)
	
	def draw(self, MaxPath=50):	return self.drawPath(self.Path(MaxPath=MaxPath), MessagePathAspect)
		
	def drawPath(self, Path, Aspect):
		Route = []
		if len(Path) > 1:
			for i in range(0, len(Path)-1):
				Route.append((self.ID+str(i), (Path[i].Location) + (0,0) + Path[i+1].Location + Aspect))
		return Route
	
						
class AntPopulation:
	" defines the population of agents "
	
	def __init__(self, Scenario, Observer, Nodes):
		" creates a population of ant agents "
		self.Scenario = Scenario
		self.Observer = Observer
		self.popSize = self.Scenario.Parameter('PopulationSize')
		self.SimulationEnd = 400 * self.popSize
		# allows to run on the simulation beyond stop condition
		self.Pop = []
		for ID in range(self.popSize):
			Node = Nodes[ID % len(Nodes)]	# looping through Nodes
			self.Pop.append(Ant('A%d' % ID, InitialNode=Node))

		
	def one_decision(self):
		""" This function is repeatedly called by the simulation thread.
			One ant is randomly chosen and decides what it does
		"""
		self.Observer.season()	# augments year
		ant = random.choice(self.Pop)
		year = self.Observer.StepId
		Moves = year // self.popSize	# One step = all ants have moved once on average
		if ant.moves(Moves, max(1, 100//self.Observer.DispPeriod)):
			Observer.recordChanges(ant.draw()) # for ongoing display of ants
		ShowMessages = (Moves % Gbl.Parameter('MessageDisplay')) == 0
		if ShowMessages:	
			for M in Ntwrk.TestMessages:
				for link in M.erase():	Observer.recordChanges(link, Slot='Trajectories') # display of message route
				Route = M.draw(MaxPath=Ntwrk.Size)
				self.Observer.MsgLength[M] = len(Route)
				for link in Route:	Observer.recordChanges(link, Slot='Trajectories') # display of message route
		# print (year, self.AllMoved, Moves),
		return self.SimulationEnd > 0	 # stops the simulation when True

		
if __name__ == "__main__":
	print(__doc__)
	print(ET.boost())	# significantly accelerates python on some platforms

	#############################
	# Global objects			#
	#############################
	Gbl = EPar.Parameters('_Params.evo')	# Loading global parameter values
	Observer = Antnet_Observer(Gbl)   # Observer contains statistics
	Ntwrk = Network(Size=Gbl.Parameter('DisplaySize'), NbNodes=Gbl.Parameter('NumberOfNodes'))
	Pop = AntPopulation(Gbl, Observer, Ntwrk.nodes())   # Ant colony
	
	# Initial draw
	Observer.recordInfo('FieldWallpaper', 'yellow')
	Observer.recordInfo('TrajectoriesWallpaper', 'lightblue')
	Observer.recordInfo('DefaultViews', ['Field', 'Trajectories'])
	Observer.recordChanges(('Dummy',(Gbl.Parameter('DisplaySize'), Gbl.Parameter('DisplaySize'), 0, 1)))	# to resize the field
	Observer.recordChanges(('Dummy',(Gbl.Parameter('DisplaySize'), Gbl.Parameter('DisplaySize'), 0, 1)), Slot='Trajectories')	# to resize the field
	# Initial display of network on Field window
	for link in Ntwrk.draw():	Observer.recordChanges(link, Slot='Positions') 
	# Initial display of network on trajectory window
	for link in Ntwrk.draw():	Observer.recordChanges(link, Slot='Trajectories') 

	
	EW.Start(Pop.one_decision, Observer, Capabilities='RPCT')

	print("Bye.......")
	sleep(1.0)
##	raw_input("\n[Return]")

__author__ = 'Dessalles'
