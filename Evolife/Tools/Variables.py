#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################


##############################################################################
#  Result matrix analysis                                                    #
##############################################################################

#################################################################
# Screening of available data to dectect variable parameters    #
#################################################################

""" Analyses a result table and says which parameters vary
"""

import sys
import os.path
import ResultMatrix

class ParamSpace(ResultMatrix.ExpMatrix):
	""" == ExpMatrix plus method for screening available variable parameters
	"""

	def ParamMatrix(self):
		" Builds a centred matrix from the parameter columns of another "

		OutputMatrix = ResultMatrix.ExpMatrix()  # oops, recursive use of the class
		OutputMatrix.Titles = self.Titles + ['Parameter Matrix']
		OutputMatrix.Names = self.Majorities.keys()
		for line in range(self.Height):
			OutputMatrix.Lines.append([str(int(self.Lines[line][self.ColIndex(P)])
									   - int(self.Majorities[P])) for P in self.Majorities])
		OutputMatrix.Update()
		return OutputMatrix
		
		
	def Screening(self):
		self.selectRelevantLines(verbose=True)	# to detect relevant parameters
		ParamColumns = self.ParamMatrix()
		#ParamColumns.Export('toto.csv')
		ParamTuples = []
		for Line in ParamColumns.Lines:
			# noting non-zero parameters for each line
			ParamTuples.append(tuple([P for P in self.Majorities if int(Line[ParamColumns.ColIndex(P)])]))
		#ParamTuples = list(set(ParamTuples))
		ParamTupleValues = sorted([PT for PT in set(ParamTuples) ], key = lambda x: len(x))
		self.ParamTupleCount = dict([(tuple(sorted(PT)), str(ParamTuples.count(PT))) for PT in ParamTupleValues])
##        Triplets = dict([PTC for PTC in self.ParamTupleCount.items() if len(PTC[0]) > 2])
##        print Triplets



	def Save(self, OuputFileName):

		OutputMatrix = ResultMatrix.ExpMatrix()  
		OutputMatrix.Names = [' X '] + sorted(self.Majorities.keys())

		CrossCounts = [['0' for y in range(len(self.Majorities)+1)] for x in self.Majorities]
		for P in self.Majorities:
			PInd = OutputMatrix.ColIndex(P)
			CrossCounts[PInd-1][0] = P
			for Q in self.Majorities:
				QInd = OutputMatrix.ColIndex(Q)
				if (P,Q) in self.ParamTupleCount:
					CrossCounts[PInd-1][QInd] = self.ParamTupleCount[(P,Q)]
					CrossCounts[QInd-1][PInd] = self.ParamTupleCount[(P,Q)]
			CrossCounts[PInd-1][PInd] = self.ParamTupleCount[(P,)]
									
		OutputMatrix.Lines = CrossCounts
		OutputMatrix.Export(OuputFileName)


def usage(Cmd):
	Msg = """

Usage:	%s <ResultMatrix.csv> 

	The programme reads the file <ResultMatrix.csv> and
	determines which variable parameters are available and co-vary
	""" % Cmd
	print Msg


if __name__ == "__main__":

	if len(sys.argv) != 2:
		usage(os.path.basename(sys.argv[0]))
		sys.exit()

	PS = ParamSpace(FileName=sys.argv[1])
	PS.Screening()
	PS.Save('VariableCoupleCounts.csv')


__author__ = 'Dessalles'
