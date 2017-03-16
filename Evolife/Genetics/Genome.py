#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################


##############################################################################
#  Genome                                                                    #
##############################################################################

""" EVOLIFE: Module Genome:
		Definition of genes as DNA segments having semantics """


import sys
if __name__ == '__main__':  sys.path.append('../..')  # for tests



from Evolife.Genetics.DNA import DNA

class Gene:
	"   class Gene: actual gene (semantic segment on DNA) with intensity "

	def __init__(self, gene_locus, intensity = 0):
		self.locus = gene_locus
		self.intensity = intensity

	def __repr__(self):
		# return ' L' + str(self.locus) + ': ' + MyScenario.get_gene_name(self.locus) + ' ('+ str(self.intensity) + ')'
		return ' L' + str(self.locus) + ': ' + ' ('+ str(self.intensity) + ')'

class Genome(DNA):
	"   class Genome: set of genes carried by individuals "

	def __init__(self, Scenario):
		self.Scenario = Scenario
		self.genome = []
		for g in self.Scenario.GeneMap:
			self.genome.append(Gene(g.locus))
		DNA.__init__(self, self.Scenario, self.Scenario.geneMap_length())

	def update(self):
		# gene values are read from DNA
		for locus in range(0,len(self.Scenario.GeneMap)):
			(b1,b2) = self.Scenario.get_gene_boundaries(locus)
			coding = self.Scenario.get_coding(locus)
			self.genome[locus].intensity = self.read_DNA(b1, b2, coding=coding)

	def gene_value(self, name):
		# absolute intensity addressed trough name
		return self.genome[self.Scenario.get_locus(name)].intensity

	def gene_relative_value(self, name):
		# relative intensity addressed through name
		return self.locus_relative_value(self.Scenario.get_locus(name))

	def locus_value(self, locus):
		# absolute intensity addressed trough locus
		return self.genome[locus].intensity

	def locus_relative_value(self, locus):
		# relative intensity addressed through locus
		return 100 * float(self.genome[locus].intensity) / self.Scenario.locus_range(locus)

	def signature(self):
		# returns all gene relative values - useful for statistics and display
		return [self.locus_relative_value(locus[0]) for locus in enumerate(self.Scenario.GeneMap)]
		
	def __repr__(self):
		return ' || '.join([g.__repr__() for g in self.genome])


if __name__ == "__main__":
	print(__doc__)
	print(Gene.__doc__)
	print(Genome.__doc__ + '\n')
	GG = Genome(Blank=False)
	print(GG)
	print(DNA.__repr__(GG))
	GG.update()
	print(GG)
	raw_input('[Return]')


__author__ = 'Dessalles'
