#!/usr/bin/env python

from SelectColumns import ExpMatrix
from Tools import transpose

##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################

class Histogram(ExpMatrix):
	""" Computes an histogram from another matrix
	"""

	def __init__(self, FileName='', Matrix=None):
		ExpMatrix.__init__(self)	# creating an empty matrix
		if Matrix is not None:
			self.DataMatrix = Matrix
		else:
			self.DataMatrix = ExpMatrix([],FileName)
		# If the first column is 'Date' it should be ignored
		if 'Date' in self.DataMatrix.Names:
			self.DataMatrix.Names.remove('Date')
			NewColumns = [self.DataMatrix.Columns[C].vect for C in self.DataMatrix.Names]
			self.DataMatrix = ExpMatrix([self.DataMatrix.Names] +
									 transpose(NewColumns))
		self.DataColumns = [self.DataMatrix.Columns[N].vect
						for N in self.DataMatrix.Names]
		self.ComputeHistogram()

	def ComputeHistogram(self):
		# One assumes that the first column corresponds to the first coordinate
		self.Values = list(set([int(v) for v in self.DataColumns[0]]))
		self.Values.sort()

		self.Histogram = [[[] for ii in self.DataColumns[1:]] for ii in self.Values]

		for val in range(len(self.Values)):
			print "\n", self.Values[val],
			for line in self.DataMatrix.Lines:
				if int(line[0]) == self.Values[val]:
					print '.',
					for col in range(1,len(self.DataColumns)):
						self.Histogram[val][col-1].append(int(line[col]))
		print ''

	def ComputeAvg(self):
		# Mins =  [ [str(min(Col)) for Col in Histogram[val]] for val in range(len(Values))]   
		# Maxs =  [ [str(max(Col)) for Col in Histogram[val]] for val in range(len(Values))]   
		self.Lines = [ [str(self.Values[val])] + ["%2.2f" % ((1.0*sum(Col))/len(Col))
					  for Col in self.Histogram[val]] for val in range(len(self.Values))]
		self.Names = self.DataMatrix.Names
		

if __name__ == "__main__":

	PlotFileName = 'e:/recherch/Evopy/Expe/Plots.csv'
	H = Histogram(PlotFileName)
	H.ComputeAvg()
	H.Export('Histogram.csv')

##
##    # Converting a file into a table of values
##    ResultMatrix = ExpMatrix([],PlotFileName)
##    
##    # If the first column is 'Date' it should be ignored
##    if 'Date' in ResultMatrix.Names:
##        ResultMatrix.Names.remove('Date')
##        NewColumns = [ResultMatrix.Columns[C].vect for C in ResultMatrix.Names]
##        ResultMatrix = ExpMatrix([ResultMatrix.Names] +
##                                 transpose(NewColumns))
##        
##    Columns = [ResultMatrix.Columns[N].vect for N in ResultMatrix.Names]
##
##    # One assumes that the first column corresponds to the first coordinate
##    Values = list(set([int(v) for v in Columns[0]]))
##    Values.sort()
##
##    ##ValueCounts = [Columns[0].count(v) for v in Values]
##    Histogram = [[[] for ii in Columns[1:]] for ii in Values]
##
##
##    for val in range(len(Values)):
##        print "\n", Values[val],
##        for line in ResultMatrix.Lines:
##            if int(line[0]) == Values[val]:
##                print '.',
##                for col in range(1,len(Columns)):
##                    Histogram[val][col-1].append(int(line[col]))
##    print ''
##    
##    Averages = [ ["%2.2f" % ((1.0*sum(Col))/len(Col)) for Col in Histogram[val]] for val in range(len(Values))]
##    Mins =  [ [str(min(Col)) for Col in Histogram[val]] for val in range(len(Values))]   
##    Maxs =  [ [str(max(Col)) for Col in Histogram[val]] for val in range(len(Values))]   
##
##
##    try:
##        Filout = open('Histogram.csv',"w")
##        Filout.write(';'.join(ResultMatrix.Names) + '\n')
##        Filout.write('\n'.join([';'.join([str(Values[L])] + Averages[L])
##                                for L in range(len(Values))]))
##        Filout.close()
##    except:
##        from sys import excepthook, exc_info
##        excepthook(exc_info()[0],exc_info()[1],exc_info()[2])

	raw_input('[Enter]')


__author__ = 'Dessalles'
