#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################


##############################################################################
#  Computes average values from a result matrices                            #
##############################################################################

"""   Computes average values from a result matrix
"""

def usage(command, verbose=True):
	Msg = """ \nUsage:
	
%s <DateList> <MinYear> <MaxYear> 
		""" % command
	if verbose:
		Msg += """
		
	This programme computes average values from columns in result files.
	The DateStamp of these files are read from the file <DateList>.
	Averages are computed from timestamps <MinYear> to <MaxYear> (read from the
	first columns)
	"""
	print(Msg)

#########
# Boost #
#########

try:
##    psyco.profile()
	from psyco.classes import *
	import psyco
	psyco.full()
except:
	print "Warning: psyco absent"
	pass


import sys
import re
from Tools import transpose, FileAnalysis
from ResultMatrix import ExpMatrix

class EvolutionMatrix(ExpMatrix):
	""" Columns in this type of matrix store parameter values as they evolve through time.
		Fist columns gives timestamps.
	"""

	def selectTimeSlice(self, MinYear, MaxYear):
		""" Selects lines with appropriate timestamps
		"""
			
		SelectedLines = []
		for Line in self.Lines:
			Year = int(Line[self.ColIndex('Year')])
			if Year >= MinYear and Year <= MaxYear:
				SelectedLines.append(Line)

		OutputMatrix = EvolutionMatrix()  # oops, recursive use of the class
		OutputMatrix.Titles = self.Titles
		OutputMatrix.Names = self.Names
		OutputMatrix.Lines = SelectedLines
		OutputMatrix.Update()
		return OutputMatrix

	def ComputeAvg(self):
		Columns = transpose(self.Lines)
		for C in range(len(Columns)):
			Columns[C] = [float(N) for N in Columns[C] if float(N) >= 0]
			if Columns[C] == []:
			   Columns[C] = [-1] 
		averages = ["%d" % int(round((1.0*sum(C))/len(C))) for C in Columns]
		# return dict(zip(self.Names,averages))
		return averages

def TimeSliceAverage(EvolFile, MinYear, MaxYear):
	EV0 = EvolutionMatrix(FileName=EvolFile)
	EV1 = EV0.selectTimeSlice(MinYear,MaxYear)
	return EV1.ComputeAvg()
	
def main():
	if len(sys.argv) < 2:
		usage(sys.argv[0])
		sys.exit()

	DateList = FileAnalysis(sys.argv[1], "(^\d+)\s*$")	
	for D in DateList:
		print '0' + D
		FName = 'e:/recherch/Evopy/Expe/___Signalling_Files/Signalling_0' + D
		Avgs = TimeSliceAverage(FName + '.csv', 200, 2000)
		Names = FileAnalysis(FName + '.res', "^[A-Z].*$")
		Values = FileAnalysis(FName + '.res', "^[0-9].*$")
		ValList = re.findall('(-?\d+)\s', Values[0])
		ValList = ValList[:-len(Avgs)+2] + Avgs[1:]
		NewResFile = open(FName + '_1.res', 'w')
		NewResFile.write(Names[0] + '\n')
		NewResFile.write('\t'.join(ValList) + '\n')
		NewResFile.close()


if __name__ == "__main__":

	main()
	print '. . . Done'


__author__ = 'Dessalles'
