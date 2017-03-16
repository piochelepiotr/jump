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
# Selection of relevant columns and lines in a numerical matrix #
#################################################################

""" Selection of relevant columns and lines in a numerical matrix
"""
from __future__ import print_function


def usage(command, Ext1='', Ext2='', Ext3='', Ext4='', verbose=False):
	Msg = """ \nUsage:
	
%s [-h] -r <ResultFile.res> [-x <x-parameter>][-y <y-parameter>
		-z <z-data>] [-p <imposed parameter>[=<value>]]*
		[-d <imposed data>]*
		""" % (command, )
	if verbose:	Msg += """
		
The programme eliminates constant columns in <ResultFile.res>
(output: <ResultFile>%s); then stores data corresponding to <x-parameter>
values (output: <ResultFile>%s), taking majority values for non-imposed
parameters; then stores average values for each <x-parameter> value
(output: <ResultFile>%s).
If <y-parameter> is present, the programme computes average values
of <z-data> for each (x-parameter, y-parameter) couple
(output: <ResultFile>%s).
Option "-d" can be used to force the program to consider <imposed data> 
as a relevant column (and not as a fixed parameter). Useful when a
dimension does not vary much.


Note: the elimination of constant columns can be made once only:
	First launch:  %s -r <ResultFile.res>
	then launch %s <ResultFile>%s ...
	as often as wanted with various x- and y- parameters.
		""" % (Ext1,Ext2,Ext3,Ext4,command,command,Ext1)
	else:	Msg += "\nFor more:	%s -h\n" % command

	print(Msg)



import sys
import re
import os
##import math
##import dislin
import getopt
from Tools import transpose

class ExpVector(object):
	""" vector containing values for one parameter obtained in successive experiments
	""" 

	def __init__(self, Vect):
		self.vect = Vect
		self.size = len(Vect)
		try:	self.values = sorted(set(Vect), key=lambda x: float(x))
		except ValueError:	self.values = sorted(set(Vect))
		# self.values = sorted(set(Vect))
		self.variation = None
		self.majority = None
		
	def hitpar(self):
		" histogram of values in a vector "
		return sorted([(self.vect.count(v),v) for v in self.values],reverse=True)

	def Majority(self):
		" returns the majority value in the vector "
		if self.majority is None:
			self.majority = self.hitpar()[0][1]
		return self.majority	   
		
	def Variation(self):
		" Decides whether a vector is constant, slightly variable or highly variable "

		if self.variation is not None:
			return self.variation

		if self.size == 0:
			return None

		if len(self.values) <= 1:
			self.variation = 'Constant'
		elif self.hitpar()[0][0] * 0.005 > sum([h[0] for h in self.hitpar()[1:]]):
			if len(set(self.vect[-20:])) > 3:
				self.variation = 'Recently variable'			
			else:
				self.variation = 'Almost constant'	   
		elif self.hitpar()[0][0] < 1.1 * self.hitpar()[1][0] \
		   or len(self.values) > 15 \
		   or len(self.values) > self.size / 3:
			self.variation = 'Highly variable'
		else:
			self.variation = 'Slightly variable'

		return self.variation

class ExpMatrix(object):
	""" Contains experiment results
		Each line: results of one experiment
	"""

	Default_Title = ['Evolife','Evolution of communication','www.dessalles.fr/Evolife']
	
	def __init__(self, InputMatrix=[], FileName=''):
		if InputMatrix != []:
			self.Names = InputMatrix[0]
			self.Lines = InputMatrix[1:]
			self.Titles = InputMatrix.Titles
		else:
			self.Names = []
			self.Lines = []
			# Titles may contain textual information about the content
			self.Titles = self.Default_Title[:]

		if FileName != '':
			self.File2Table(FileName)
		self.RelevantColumns = []
		self.Parameters = []
		self.DataColumns = []
		self.Update()
		self.Majorities = dict()
	
	def Update(self):
		self.Columns = dict([(N,ExpVector(C)) for (N,C) in zip(self.Names,transpose(self.Lines))])
		self.Height = len(self.Lines)
		self.Width = len(self.Columns)
		
	def ColIndex(self, ColName):
		return self.Names.index(ColName)
	
	def Select(self, Vect, IndexList):
		return [Vect[C] for C in IndexList]
				
	def File2Table(self, Filin):
		""" converts a text file containing a line of value labels
			and then lines of integer values into a table of values
		"""
		Table = open(Filin)
		LinesTxt = Table.readlines()
		Table.close()

		LineOffset = 0
		if re.split("[\t;]+", LinesTxt[0].strip())[0] == 'Evolife':
			LineOffset = 1
			self.Titles = re.split("[\t;]+", LinesTxt[0].strip())
		self.Names = re.split("[\t;]+", LinesTxt[LineOffset].strip())
		self.Lines = [re.split("[\t;]+", L.strip()) for L in LinesTxt[LineOffset+1:]]

	def Export(self, FileName):
		try:
			Filout = open(FileName,"w")
		except IOError:
			print("ERROR: %s in use" % FileName)
			return
		if self.Titles:
			Filout.write(';'.join(self.Titles))
		Filout.write('\n')
		Filout.write(';'.join(self.Names))
		Filout.write('\n')
		Filout.write('\n'.join([str(';'.join(L)) for L in self.Lines]))
		Filout.write('\n')
		Filout.close()
		print('------- %s has been created' % FileName)
		
	def RemoveColumn(self, ColName):
		" Creates a new matrix without the column "

		OutputMatrix = ExpMatrix()  # oops, recursive use of the class
		OutputMatrix.Titles = self.Titles
		OutputMatrix.Names = self.Names
		OutputMatrix.Names.remove(ColName)
		OutputMatrix.Lines = transpose([self.Columns[C].vect for C in OutputMatrix.Names])
		OutputMatrix.Update()
		return OutputMatrix
		
	def ColumnAnalysis(self, Parameter='', DataCol=[], verbose=True):
		" Determines whether columns correspond to parameters, to variables or are constant "

		#print 'Risk:', self.Columns['Risk'].hitpar()
		#print self.Columns['Risk'].size, len(self.Columns['Risk'].values), self.Columns['Risk'].Variation()
		
		# List of variable columns
		print('DATACOL = %s' % str(DataCol))
		self.RelevantColumns = [Col for Col in self.Columns
							if Col in DataCol or self.Columns[Col].Variation()
									in ['Slightly variable','Highly variable']]

		# List of columns which are likely parameters, i.e. have a fixed majority part and a variable part
		self.Parameters =  [Col for Col in self.RelevantColumns
						  if Col not in DataCol and self.Columns[Col].Variation()
									in ['Slightly variable', 'Recently variable']]

		# forcing Parameter among Parameters
		if Parameter is not '':
			self.RelevantColumns = list(set(self.RelevantColumns + [Parameter]))
			self.Parameters = list(set(self.Parameters + [Parameter]))

		self.IrrelevantColumns = [Col for Col in self.Columns
							if Col not in DataCol and self.Columns[Col].Variation()
									in ['Constant','Almost constant']]
		self.IrrelevantColumns = list(set(self.IrrelevantColumns) - set([Parameter]))

		# List of colomns which are likely to contain data: those are highly variable
		DataColumns = set(self.RelevantColumns) - set(self.Parameters)

		# Keeping the original order
		self.DataColumns = [DC for DC in self.Names if DC in DataColumns]
		if verbose:
			print("Data columns:\n\t%s" % ('\n\t'.join(self.DataColumns)))

		AlmostConstant = [C for C in self.Columns if self.Columns[C].Variation() == 'Almost constant']
		if AlmostConstant != [] and verbose:
			print('Warning: those columns are not constant, but almost: %s' % (', '.join(AlmostConstant)))

		RecentlyVariableParameters = [Col for Col in self.Parameters
										if self.Columns[Col].Variation() == 'Recently variable']
		if verbose:
			print("Recently variable parameters: %s" % str(RecentlyVariableParameters))
		
	def selectRelevantColumns(self, Parameter='', DataCol=[], verbose=True):
		""" Eliminates constant or almost constant columns
		"""
		if verbose:
			print('Eliminating constant columns . . .')
			
		self.ColumnAnalysis(Parameter, DataCol, verbose)

		# selecting relevant columns while keeping original order
		SelectedNames = [C for C in self.Names if C in self.RelevantColumns]
		SelectedColumns = [self.Columns[C].vect for C in self.Names if C in self.RelevantColumns]

		OutputMatrix = ExpMatrix()  # oops, recursive use of the class
		OutputMatrix.Titles = self.Titles
		for IrC in sorted(self.IrrelevantColumns):
			OutputMatrix.Titles.append("%s=%s" % (IrC, self.Columns[IrC].Majority()))
		OutputMatrix.Names = SelectedNames
		OutputMatrix.Lines = transpose(SelectedColumns)
		OutputMatrix.Update()
		return OutputMatrix

	def selectRelevantLines(self, X_parameter='', Y_parameter='',
							SideParametersAndValues=[], DataCol=[], verbose=True):
		""" Suppresses lines in which non-relevant parameters vary
			and then columns corresponding to non-relevant parameters
			which are now constant
		"""
		if verbose:
			print('Selecting relevant lines . . .')
			
		if (X_parameter and X_parameter not in self.Names) \
		   or (Y_parameter and Y_parameter not in self.Names):
			print('Available columns: %s' % str(self.Names))
			print("ERROR: missing parameters: %s   %s" % (X_parameter, Y_parameter))
			return [self.Names] + self.Lines

		# updates parameters (columns, etc.)
		self.ColumnAnalysis(Parameter=X_parameter, DataCol=DataCol, verbose=False) 

		# SideParameters are imposed parameters, with imposed value
		SideParameters = dict(SideParametersAndValues)
		
		# Columns which are likely parameters, i.e. have a fixed majority part and a variable part
		UsefulParameters = (set(self.Parameters) \
					 | set(SideParameters.keys())) - set([X_parameter, Y_parameter]+DataCol)

		# displaying the majority column for each parameter
		try:
			self.Majorities = dict([(UP,self.Columns[UP].Majority()) for UP in UsefulParameters])
		except KeyError:
			print('please check parameter spelling: %s %s %s' % (X_parameter,Y_parameter, ' '.join(list(SideParameters.keys()))))
			print('. . . Bye')
			sys.exit()
		for SP in SideParameters:
			if SideParameters[SP] is not None:
				self.Majorities[SP] = SideParameters[SP]
		if verbose:
			print('Detected parameters:')
			if X_parameter:
				print('\t%s (Relevant parameter)' % X_parameter)
			print('\n\t'.join(["%s (majority or chosen value: %s)" % (M,self.Majorities[M])
							 for M in self.Majorities]))

		SelectedLines = []
		for Line in self.Lines:
			Keep = True
			for UP in UsefulParameters:
				if Line[self.ColIndex(UP)] != self.Majorities[UP]:
					Keep = False
					break
				Keep = True
			if Keep:
				SelectedLines.append(Line)

		# sorting lines according to relevant parameters
		if X_parameter and Y_parameter:
			SelectedLines.sort(key=lambda x: (float(x[self.ColIndex(X_parameter)]),
											  float(x[self.ColIndex(Y_parameter)])))
		elif X_parameter:
			SelectedLines.sort(key=lambda x: (float(x[self.ColIndex(X_parameter)])))
							   

		OutputMatrix = ExpMatrix()  # oops, recursive use of the class
		OutputMatrix.Titles = self.Titles
		OutputMatrix.Names = self.Names
		OutputMatrix.Lines = SelectedLines
		OutputMatrix.Update()
		return OutputMatrix
##        return [self.Names] + SelectedLines
	

class Histogram(ExpMatrix):
	""" Computes an histogram from another matrix
	"""

	def __init__(self, FileName='', Matrix=None, X_parameter='', DataCol=[]):
		ExpMatrix.__init__(self)
		if Matrix is not None:
			self.DataMatrix = Matrix
		else:
			self.DataMatrix = ExpMatrix([],FileName)
		# If the first column is 'Date' it should be ignored
		if 'Date' in self.DataMatrix.Names:
			self.DataMatrix = self.DataMatrix.RemoveColumn('Date')
		else:
			self.DataMatrix = Matrix
		# updating parameters
		self.DataMatrix.ColumnAnalysis(Parameter=X_parameter, DataCol=DataCol, verbose=False)
		self.Titles = self.DataMatrix.Titles
		self.x_parameter = X_parameter
		if self.x_parameter == '':
			self.x_parameter = self.DataMatrix.Names[0]
		self.x_values = []
		self.Histogram = [[[]]] 

	def ComputeHistogram(self):
		""" Stores y-values sharing same x-values into lists for each data column
		"""
		self.x_values = list(self.DataMatrix.Columns[self.x_parameter].values)
		self.Histogram = [[[] for y in self.DataMatrix.DataColumns] for x in self.x_values]
		Cx = self.DataMatrix.ColIndex(self.x_parameter)

		print('Computing histogram over %s' % self.x_parameter)
		for x_i in range(len(self.x_values)):
			x_val = self.x_values[x_i]
			print("\n", x_val, '\t', end='')
			for line in self.DataMatrix.Lines:
				if line[Cx] == x_val:
					print('.', end='')
					for col in self.DataMatrix.DataColumns:
						NroCol = self.DataMatrix.DataColumns.index(col) # column in Histogram
						ColInd = self.DataMatrix.ColIndex(col)  # column in DataMatrix
						self.Histogram[x_i][NroCol].append(float(line[ColInd]))
		print()

	def ComputeAvg(self):
		# Mins =  [ [str(min(Col)) for Col in Histogram[val]] for val in range(len(Values))]   
		# Maxs =  [ [str(max(Col)) for Col in Histogram[val]] for val in range(len(Values))]   
##        self.Lines = [ [str(self.x_values[val])] + ["%2.2f" % ((1.0*sum(Col))/len(Col))
##                      for Col in self.Histogram[val]]
##                      for val in range(len(self.x_values))]
		self.Lines = []
		for x_i in range(len(self.x_values)):
			line = [str(self.x_values[x_i])]
			for Col in self.Histogram[x_i]:
				if len(Col):
					line.append("%2.2f" % ((1.0*sum(Col))/len(Col)))
				else:
					line.append("-1")
			self.Lines.append(line)
		self.Names = [self.x_parameter] + self.DataMatrix.DataColumns


class TwoDHistogram(Histogram):
	""" build a matrix from an x-parameter, a y-parameter and a z-data
		containing average results
	"""

	def __init__(self, Matrix, X_parameter, Y_parameter, Z_data, Datacol=[]):
		Histogram.__init__(self, Matrix=Matrix, X_parameter=X_parameter, Datacol=Datacol)
		self.Titles = ExpMatrix.Default_Title \
					  + [X_parameter, Y_parameter, Z_data] \
					  + self.Titles[len(ExpMatrix.Default_Title):]
		self.y_parameter = Y_parameter
		self.y_values = []
		self.z_data = Z_data

	def Compute2DHistogram(self):
		""" Stores z-values sharing same x-values and y-values into lists
		"""
		self.x_values = list(self.DataMatrix.Columns[self.x_parameter].values)
		self.y_values = list(self.DataMatrix.Columns[self.y_parameter].values)
		self.Histogram = [[[] for y in self.y_values] for x in self.x_values]
		self.hitp = []   # number of values for each (x_value,y_value) couple
		Cx = self.DataMatrix.ColIndex(self.x_parameter)
		Cy = self.DataMatrix.ColIndex(self.y_parameter)
		Cz = self.DataMatrix.ColIndex(self.z_data)

		print('Computing 2D-histogram of %s over %s and %s' \
			  % (self.z_data, self.x_parameter, self.y_parameter))
		for x_i in range(len(self.x_values)):
			x_val = self.x_values[x_i]
			print("\n%s\t" % str(x_val), end='')
			for y_j in range(len(self.y_values)):
				y_val = self.y_values[y_j]
				count = 0
				for line in self.DataMatrix.Lines:
					if		    line[Cx] == x_val \
							and line[Cy] == y_val:
						count += 1
						self.Histogram[x_i][y_j].append(float(line[Cz]))
				self.hitp.append((x_val,y_val,count))
				print('%s:%d' % (y_val,count), end='')
		print()

	def ComputeAvg(self):
		Histogram.ComputeAvg(self)
		self.Names = ["%s x %s" % (self.x_parameter, self.y_parameter)] \
					 + self.y_values

	def Representativity(self):
		self.hitp = [p for p in self.hitp if int(p[0]) <= 100 and int(p[1]) <= 100]
		self.hitp.sort(key=lambda x: x[2])
		return self.hitp




def CommandLine(Commandline):

	(ResultFileName, x_parameter, y_parameter, z_Data, SideParameters, SideData) = ('', '', '', '', [], [])

	# Command line analysis
	Options = getopt.getopt(Commandline, 'r:x:y:z:p:d:h')
	if Options[1]:
		raise Exception('surplus argument')
	for (O,A) in Options[0]:
		if O == '-r':
			ResultFileName = A
		if O == '-x':
			x_parameter = A
		if O == '-y':
			y_parameter = A
		if O == '-z':
			z_Data = A
		if O == '-p':
			ParamAndValue = A.split('=')
			if len(ParamAndValue) == 2:
				SideParameters.append(tuple(ParamAndValue))
			elif len(ParamAndValue) == 1:
				SideParameters.append((ParamAndValue[0],None))			  
		if O == '-d':
			SideData.append(A)
		if O == '-h':
			raise ValueError('Help')
	if ResultFileName == '':
		raise ValueError('Absent file name')
	if y_parameter and not z_Data:
		raise ValueError('Need z_data when y_data is present')
	return (ResultFileName, x_parameter, y_parameter, z_Data, SideParameters, SideData)

	
def main():

	ConstantColRemovedFileExt = '_col.csv'
	SelectedLinesFileExt = '_lines.csv'
	HistogramFileExt = '_Histo.csv'
	TwoDHistogramFileExt = '_2DHisto.csv'

	try:
		(ResultFileName, x_parameter, y_parameter, z_Data, SideParameters, SideData) = CommandLine(sys.argv[1:])
	except getopt.GetoptError as err:
		usage(os.path.basename(sys.argv[0]), verbose=False)

		print("erreur dans les options : %s " % err)
		print('. . . Bye')
		sys.exit(2)
##    except ValueError, err:
	except Exception as err:
		if str(err) == 'Help':
			usage(os.path.basename(sys.argv[0]),ConstantColRemovedFileExt,
				  SelectedLinesFileExt,HistogramFileExt,TwoDHistogramFileExt, verbose=True)
		else:
			usage(os.path.basename(sys.argv[0]), verbose=False)
			if str(err):	print('Error: %s' % err)
		print('. . . Bye')
		sys.exit(1)

		
	if '_'+ResultFileName.split('_')[-1] == ConstantColRemovedFileExt:
		# First step (suppression of constant columns) has already been performed
		FileNameRoot = '_'.join(ResultFileName.split('_')[:-1])
		ConstantColRemovedFileName = ResultFileName
	else:
		FileNameRoot = os.path.splitext(ResultFileName)[0]
		ConstantColRemovedFileName = FileNameRoot + ConstantColRemovedFileExt
	SelectedLinesFileName = FileNameRoot + SelectedLinesFileExt
	HistogramFileName = FileNameRoot + HistogramFileExt
	TwoDHistogramFileName = FileNameRoot + TwoDHistogramFileExt

	# processing
	try:
		# retrieve result matrix from file
		RMatrix = ExpMatrix([],ResultFileName)
		if ResultFileName != ConstantColRemovedFileName:
			# starting from raw material - Constant columns have to be removed
			AbridgedMatrix = RMatrix.selectRelevantColumns(x_parameter)
			AbridgedMatrix.Export(ConstantColRemovedFileName)
		else:
			print('Assuming %s is purged from constant columns' % ConstantColRemovedFileName)
			# hoping that x_parameter hasn't changed - The user knows what she's doing
			AbridgedMatrix = RMatrix
	except Exception as err:
##        from sys import excepthook, exc_info
##        excepthook(exc_info()[0],exc_info()[1],exc_info()[2])
		print(err)
		print('Mais tout va bien...')
		sys.exit()

	if x_parameter == '':
		print('Nothing more to do (missing x-parameter)')
		return

	SelectedLines = AbridgedMatrix.selectRelevantLines(X_parameter=x_parameter,
													   SideParametersAndValues=SideParameters,
													   DataCol=SideData)
	if SelectedLines.Height > 0:
		print('Eliminating new constant columns . . .')
		SelectedColumnsInSelectedLines = SelectedLines.selectRelevantColumns(x_parameter,
													   DataCol=SideData, verbose=True)
		SelectedColumnsInSelectedLines.Export(SelectedLinesFileName)
		print('Building an histogram . . .')
		H = Histogram(Matrix=SelectedColumnsInSelectedLines, X_parameter=x_parameter, DataCol=SideData)
		H.ComputeHistogram()
		H.ComputeAvg()
		H.Export(HistogramFileName)
	else:
		print("No lines left in the matrix")

	if y_parameter == '':
		return
	SelectedLines = AbridgedMatrix.selectRelevantLines(X_parameter=x_parameter,
													   Y_parameter=y_parameter,
													   SideParametersAndValues=SideParameters,
													   DataCol=SideData, verbose=False)
	if SelectedLines.Height > 0:
		SelectedColumnsInSelectedLines = SelectedLines.selectRelevantColumns(x_parameter,
													   DataCol=SideData, verbose=False)
		print('Building a 2D-histogram . . .')
		HH = TwoDHistogram(SelectedColumnsInSelectedLines , x_parameter, y_parameter, z_Data, DataCol=SideData)
		HH.Compute2DHistogram()
		HH.ComputeAvg()
		HH.Export(TwoDHistogramFileName)
		print('Least representative points:')
		print(HH.Representativity()[0:8])

if __name__ == "__main__":

	main()
	print('. . . Done')


"""
ctit1 = 'Surface Plot of the Function'
ctit2 = 'F(X,Y) = 2 * SIN(X) * SIN (Y)'

Columns = selectRelevantColumns('Signalling.mem')[1:]

n = len(Columns[0])
m = len(Columns)
zmat = range(n*m)

fpi  = 3.1415927 / 180.
stepx = 360. / (n - 1)
stepy = 360. / (m - 1)

for i in range (0, n):
  x = i * stepx
  for j in range (0, m):
	y = j * stepy
##    zmat[i*m+j] = 2 * math.sin(x * fpi) * math.sin(y * fpi)
	zmat[i*m+j] = float(Columns[j][i])

	
dislin.metafl ('cons')
dislin.setpag ('da4p')
dislin.disini ()
dislin.pagera ()
dislin.hwfont ()

dislin.titlin (ctit1, 2)
dislin.titlin (ctit2, 4)

dislin.axspos (200, 2600)
dislin.axslen (1800, 1800)

dislin.name   ('X-axis', 'X')
dislin.name   ('Y-axis', 'Y')
dislin.name   ('Z-axis', 'Z')

dislin.view3d (-5., -5., 4., 'ABS')
dislin.graf3d  (0., 360., 0., 90., 0., 360., 0., 90.,
				-3., 3., -3., 1.)
dislin.height (50)
dislin.title  ()

dislin.color  ('green')
dislin.surmat (zmat, n, m, 1, 1)
dislin.disfin ()

"""



__author__ = 'Dessalles'
