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
# Interpolation for filling in missing data                     #
#################################################################

import sys
import os.path
import ResultMatrix 


class InterpMatrix(ResultMatrix.ExpMatrix):
	""" InterpMatrix is a ExpMatrix seen as a two-dimensional array
		with numerical values in first column and first row.
		The purpose is to replace missing values (indicated by -1)
		by interpolating between neighbouring cells
	"""

	def Value(self, (line,col)):
		return float(self.Lines[line][col])
	
	def HAvg(self,Points):
		Diff = (self.Value(Points[2]) - self.Value(Points[0]))
		Gap = (float(self.Names[Points[2][1]]) - float(self.Names[Points[0][1]]))
		Dist = (float(self.Names[Points[1][1]]) - float(self.Names[Points[0][1]]))
		return  self.Value(Points[0]) + Dist * Diff / Gap
		
	def VAvg(self,Points):
		Diff = (self.Value(Points[2]) - self.Value(Points[0]))
		Gap = (self.Value((Points[2][0],0)) - self.Value((Points[0][0],0)))
		Dist = (self.Value((Points[1][0],0)) - self.Value((Points[0][0],0)))
		return  self.Value(Points[0]) + Dist * Diff / Gap
		

	def HInterpolate(self, (line,col)):
		if col > 1 and col < self.Width-1:
			return self.HAvg([(line, col-1),(line,col),(line,col+1)])
		if col > 1:
			return self.Value((line,col-1))
		return self.Value((line,col+1))
		
	def VInterpolate(self, (line,col)):
		if line and line < self.Height-1:
			return self.VAvg([(line-1, col),(line,col),(line+1,col)])
		if line:
			return self.Value((line-1,col))
		return self.Value((line+1,col))
		
	def CellInterpolate(self,(line,col)):
		return (self.HInterpolate((line,col)) + self.VInterpolate((line,col))) / 2

	def Interpolate(self):	
		" Allows to fill blanks in a matrix through interpolation "
		print '\nReplacing -1 by interpolating between neighbouring values'
		for line in range(self.Height):
			for col in range(1,self.Width):
				if self.Lines[line][col] == '-1':
					print "(%d,%d)->%2.2f" % (line,col,self.CellInterpolate((line,col)))
					self.Lines[line][col] = "%2.2f" % self.CellInterpolate((line,col))
		print ''


def usage(Cmd,OuputExt):
	Msg = """

Usage:	%s <MatrixToInterpolate.csv> 

	The programme reads the file <MatrixToInterpolate.csv> and replaces
	"-1" by interpolating non-negative neighbouring values.
	Ouput: <MatrixToInterpolate>%s
	""" % (Cmd,OuputExt)
	print Msg

	
if __name__ == "__main__":

	OutputExt = '_Interp.csv'
	
	if len(sys.argv) != 2:
		usage(os.path.basename(sys.argv[0]),OutputExt)
		sys.exit()

	InputMatrix = InterpMatrix(FileName=sys.argv[1])
	InputMatrix.Interpolate()	
	InputMatrix.Export(os.path.splitext(sys.argv[1])[0] + OutputExt)
		


__author__ = 'Dessalles'
