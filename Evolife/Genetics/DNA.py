#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################


##############################################################################
#  DNA                                                                       #
##############################################################################

""" EVOLIFE: Module DNA:
		The genome of each creature in EVOLIFE is defined as a binary string
		The way this binary string is implemented (e.g. list of binary numbers
		or bits compacted into integers) should remain private to this module """



import sys
if __name__ == '__main__':
	sys.path.append('../..')  # for tests
	from Evolife.Scenarii.MyScenario import InstantiateScenario
	InstantiateScenario('Cooperation','../Evolife')

import random
# try:	import numpy; NUMPY = True; print('Loading Numpy')
# except ImportError:	NUMPY = False
NUMPY=False	# slower with Numpy !!

import Evolife.Tools.Tools as Tools

class DNA:
	"""   class DNA: individuals' 'DNA' defined as a string of bits
	"""

	def __init__(self, Scenario, Nb_nucleotides):
		self.Scenario = Scenario
		self.nb_nucleotides = Nb_nucleotides
		self.__dna = []
		Fill = self.Scenario.Parameter('DNAFill', Default=-1)	# 0 or 1 or -1=random
		for pos in range(self.nb_nucleotides):
			if (Fill==1):	self.__dna.append(1)
			elif (Fill==0):	self.__dna.append(0)
			else:			self.__dna.append(random.randint(0,1))
		if NUMPY:	self.__dna = numpy.array(self.__dna)	# doesn't seem to be very efficient !
			
	def DNAfill(self, Nucleotides):
		" fills the DNA with given Nucleotides "
		self.__dna = Nucleotides[:] # important: make a ground copy
		if len(Nucleotides) > 0 and len(Nucleotides) != self.nb_nucleotides:
			Tools.error('DNA: initialization','Provided genome length does not match gene map')
		if len(Nucleotides) > 0 and not set(Nucleotides) <= set([0,1]):
			Tools.error('DNA: initialization','Provided genome is not binary')
		
	def hybrid(self, mother, father, number_crossover = -1):
		" builds the child's DNA from the parents' DNA "
		#   computing random crossover points
		if number_crossover < 0:	number_crossover = self.Scenario.Parameter('NbCrossover')
		if self.nb_nucleotides > 1:
			Loci_crossover = random.sample(range(1,self.nb_nucleotides), number_crossover)
			Loci_crossover = [0] + sorted(Loci_crossover)
		else:
			Loci_crossover = [0]
		Loci_crossover.append(self.nb_nucleotides)
		# print Loci_crossover
		# the child's DNA will be read alternatively from parent1 and parent2
		parent1 = mother.__dna
		parent2 = father.__dna
		if random.randint(0,1):	# starting indifferently from mother or father
			parent1, parent2 = parent2, parent1	 # swapping parents
		self.__dna = []
		for cut_point in range(len(Loci_crossover)-1):
			self.__dna += list(parent1[Loci_crossover[cut_point]:Loci_crossover[cut_point+1]])
			parent1, parent2 = parent2, parent1	 # swapping parents		
		if NUMPY:	self.__dna = numpy.array(self.__dna)

	def mutate(self, mutation_rate = -1):
		" computing the expected number of mutations "
		if mutation_rate < 0:	mutation_rate = self.Scenario.Parameter('MutationRate')
		mutation_number = Tools.chances(mutation_rate/1000.0, self.nb_nucleotides)
##        mutation_number =  (mutation_rate * self.nb_nucleotides) / 1000
##        if randint(1,1000) < 1 + ((mutation_rate * self.nb_nucleotides) % 1000) :
##            mutation_number += 1
		# performing mutations
		for mutation in range(mutation_number):
			pos = random.randint(0, self.nb_nucleotides - 1)
			self.__dna[pos] = 1 - self.__dna[pos]
		return mutation_number

	def read_DNA(self, start, end, coding = None):
		" reads a chunk of DNA "
		if coding == None:	coding = self.Scenario.Parameter('GeneCoding')
		if coding in range(-1,3):
			# old numeric designation of coding
			coding = ['Nocoding', 'Weighted', 'Unweighted', 'Gray'][coding+1]
		value = 0
		coding = coding.lower()
		if coding == 'nocoding':
			return 0
		if coding not in ['weighted', 'unweighted', 'gray']:
			Tools.error("DNA", 'unknown binary coding mode')
		try:
			for pos in range(start,end):
				if coding == 'unweighted':
					value += self.__dna[pos]
				else:   # Weighted or Gray
##                    value += self.__dna[pos]* 2 ** (end - 1 - pos)
					value += (self.__dna[pos] << (end - 1 - pos))
			if coding == 'gray':
				value = Tools.GrayTable.Gray2Int(value)
			return(value)
		except IndexError:
			Tools.error("DNA", "reading outside the DNA")

	def hamming(self, alter):
		" computes the Hamming distance between two DNA strings "
		distance = 0
		for pos in range(self.nb_nucleotides):
			distance += (self.__dna[pos] != alter.__dna[pos])
		return distance

	def get_DNA(self):
		# returns DNA as a tuple
		return tuple(self.__dna)

	def __repr__(self, compact=0):
		if compact:
				return str(sum(self.__dna))
		# printing bits separated by "-"
		return "-".join(["%s" %pos for pos in self.__dna])

	def display(self):
		pass

	def save(self):
		pass


if __name__ == "__main__":
	print(__doc__)
	print(DNA.__doc__ + '\n')
	mother = DNA(9, Blank=False)
	print('mother: ')
	print(mother)
	father = DNA(9, Blank=False)
	print('father: ')
	print(father)
	child = DNA(9)
	child.hybrid(mother,father,2)
	print('child:  ')
	print(child)
	child.mutate(80)
	print('child:  ')
	print(child)
	print(' (mutated)')
	print('child\'s value (weighted)  :')
	print(child.read_DNA(0,4, coding = MyScenario.Parameter('Weighted')))
	print('child\'s value (unweighted):')
	print(child.read_DNA(0,4, coding = MyScenario.Parameter('Unweighted')))
	print('distance with mother:')
	print(child.hamming(mother))
	print('distance with father:')
	print(child.hamming(father))
	raw_input('\n[Return]')



__author__ = 'Dessalles'
