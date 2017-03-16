#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################
""" Input and Output using SCV files (as the standard 'csv' module does not seem to be reliable) """


import os
import re
#	compatibility with python 2
import sys
Python3 = (sys.version_info >= (3,0))

pyCrypt = None
try:	import pyCrypt
except ImportError:	pass

# MaxRead = 4*4096	# max chars read from a file to get an idea of its structure
MaxRead = 100	# max chars read from a file to get an idea of its structure
PrologPredicate = 'record_'	# for prolog output
ENCODING = 'utf-8'

# ________________________________ #
#                                  #
# csv file format                  #
# ________________________________ #
class Dialect:
	"""	sets delimiter and escape char - Partially mimics standard csv module
	"""
	def __init__(self, delimiter=',', escapechar='\\', quotechar='"', initial='', final='', entete='', fullQuote=False):
		self.delimiter = delimiter
		self.escapechar = escapechar
		self.quotechar = quotechar
		self.initial = initial
		self.final = final
		self.entete = entete
		self.QUOTE_MINIMAL = not fullQuote
		self.fullQuote = fullQuote

	def mostRepresented(self, Chars, Sample):
		Poll = [Sample.count(Char) for Char in Chars]
		Candidate = Poll.index(max(Poll))
		# print(Sample[:100])
		# print Chars, Poll, Candidate
		Poll1 = sorted(Poll)
		if Poll1[-1] > 1.3 * Poll1[-2]: return Chars[Candidate]
		return None
		
	def sniff(self, fileName, verbose=True):
		" Tries to detect delimiter and quote char "
		if os.path.exists(fileName):
			Input = openFile(fileName)
			Sample = ''
			try:
				for nroLine in range(MaxRead):	Sample += next(Input)
			except StopIteration:	pass
			delimiter = self.mostRepresented([',', ';', '\t'], Sample)
			if verbose:	print('candidate delimiter: %s' % delimiter)
			if delimiter is not None:
				# and len(set([Line.count(delimiter) for Line in Sample.split('\n')])) == 1:
				if delimiter != self.delimiter:
					# further test: same number of delimiters per line
					# suppressing dots
					Sample1 = re.sub(r'\\.', '', Sample)	# Note the 'r' which is necessary here
					# suppressing quoted fields
					Sample1 = re.sub('%s.*?%s' % (self.quotechar, self.quotechar), '', Sample1).split('\n')[:-1]
					P = set([Line.count(delimiter) for Line in Sample1])
					self.delimiter = delimiter
					if verbose:	print("Delimiter set to '%s'" % delimiter)
					if len(P) != 1:
						print('warning: candidate delimiter %s seems to fail %s' % (delimiter, str(P)))
						# trying to find faulty lines
						P = list(P)
						LineCounts = [(l[0], l[1].count(delimiter)) for l in enumerate(Sample1)]
						Occurrences = [[l[1] for l in LineCounts].count(n) for n in P]
						print(Occurrences, P)
						Faultyline = LineCounts[[l[1] for l in LineCounts].index(P[Occurrences.index(min(Occurrences))])]
						Msg = '\n********* line %d has %d occurrences of "%c" *********\n' % (Faultyline + (delimiter,))
						Msg += Sample1[Faultyline[0]]
						# raise Exception, Msg
						print(Msg)
						
			# quotechar = self.mostRepresented(['"', "'"], Sample)
			# if quotechar is not None:
				# self.quotechar = quotechar
				# print("Quotechar set to '%s'" % quotechar)
		else:	print('ERROR:	Unable to open %s for sniffing' % fileName)

	def extension(self):
		if self.initial.startswith(PrologPredicate):	return '.pl'
		if self.delimiter in [',', ';']:	return '.csv'
		if self.delimiter in ['\t']:	return '.csv'
		return '.txt'

	def __str__(self):	return 'Delimiter: %s' % self.delimiter
		
def openFile(csvFileName, CryptKey=None, Ecoding=ENCODING):
	"	Opens a csv file and returns content line by line "
	if CryptKey is not None:
		try:
			csvString = pyCrypt.p3_decrypt(open(csvFileName, 'rb').read(), CryptKey)
			try:
				print('splitting')
				csvList = csvString.decode(ENCODING).split('\n')
			except UnicodeDecodeError:
				print('*****  mmm...  %s: Not a %s file. *****' % (csvFileName, ENCODING))
				csvList = csvString.decode('latin-1').split('\n')
				# print(len(csvList))
		except (TypeError, pyCrypt.CryptError) as E:
			print(E)
			# Python 2 compatibility
			print('*************** Python2 COMPATIBILITY ****************')
			os.system('cmd /C decrypte -d %s tmpfile000.csv' % csvFileName)
			csvList = open('tmpfile000.csv', 'r').readlines()
			os.system('cmd /C del tmpfile000.csv')
		for L in csvList:	yield L.strip()	# because of trailing \r
	else:
		Line = ''
		nroLine = 0
		if Python3:
			try:
				# read one line at a time
				for Line in open(csvFileName, 'r', encoding=ENCODING, buffering=1, newline='\n'):	
					nroLine += 1
					if Line.endswith('\r'):	yield Line.strip('\r')
					else:	yield Line
			except UnicodeDecodeError:
				print('*****  well...  %s: Not a %s file. *****' % (csvFileName, ENCODING))
				print("Line %d: %s" % (nroLine, Line))
				for Line in open(csvFileName, 'r', encoding='latin-1', buffering=1, newline='\n'):	
					if Line.endswith('\r'):	yield Line.strip('\r')
					yield Line
		else:
			# read one line at a time
			for Line in open(csvFileName, 'r', buffering=1):	yield Line
	# if CryptKey is None:	csvFile.close()
	
	
def reader(csvFileName, dialect=None, CryptKey=None):
	"	Opens a csv file and returns a record generator "
	if dialect is None:	dialect = Dialect()
	FieldNr = 0
	Nroline = 1
	literal = False		# true between quote chars
	currentField = ''	# receives current field as string
	for Line in openFile(csvFileName, CryptKey=CryptKey):
		# try:	print(Line)
		# except Exception as E:
			# print(E)
		# if CryptKey is not None:	print(Line)
		# this loop should be an automaton
		if not Line or Line[-1] != '\n':	Line += '\n'
		if Line == '\n' and not literal:	continue
		if not literal:	Fields = []			# list of fields for the current record (usually read from a single line)
		if dialect.initial and Line.startswith(dialect.initial):
			Line = Line[len(dialect.initial):]
		if dialect.final and Line.endswith(dialect.final):
			Line = Line[:-len(dialect.final)]
		skip = False	# to record char next to escape char
		for c in Line:
			if skip:	
				currentField += c
				skip = False
			else:
				# print c, literal
				if c == dialect.escapechar: skip = True
				elif c == '\r' and not literal:	continue
				elif c == dialect.quotechar:	literal = not literal
				elif c in [dialect.delimiter, '\n'] and not literal and not skip:	
					Fields.append(currentField)
					currentField = ''
				else:	currentField += c
		if FieldNr and FieldNr != len(Fields) and not literal:
			ErrorMsg = '\nUnbalanced line:\nline %d in %s has %d fields instead of %d:\n%s\n%s' \
				% (Nroline, csvFileName, len(Fields), FieldNr, Line, '\n>>>>\n'.join(Fields))
			# if Python3:	input(ErrorMsg) 	# provoque un plantage dans QT
			# else:	raw_input(ErrorMsg)
			raise Exception(ErrorMsg)
			yield []
		if not literal:
			FieldNr = len(Fields)
			Nroline += 1
			yield Fields
	
class writer:
	" Writes records to an opened csv file "
	def __init__(self, csvFile, dialect=None):
		self.dialect = dialect
		if self.dialect is None:	self.dialect = Dialect()
		self.csvFile = csvFile

	def field2Str(self, Field):
		Field = str(Field).replace(self.dialect.escapechar, '%s%s' % (self.dialect.escapechar, self.dialect.escapechar))	
		Field = Field.replace(self.dialect.quotechar, '%s%s' % (self.dialect.escapechar, self.dialect.quotechar))
		if not self.dialect.fullQuote:
			Field = Field.replace(self.dialect.delimiter, '%s%s' % (self.dialect.escapechar, self.dialect.delimiter))
		if Field.find('\n') >= 0 or Field.find('\r') >= 0 or self.dialect.fullQuote: 
			Field = '%s%s%s' % (self.dialect.quotechar, Field, self.dialect.quotechar)
		return Field
		
	def writerow(self, Fields):
		" Saves tuple into csv file "
		Line = self.dialect.initial + (self.dialect.delimiter).join(map(self.field2Str, Fields)) + self.dialect.final + '\n'
		if self.csvFile:	self.csvFile.write(Line)
		return Line

def load(csvFileName, dialect=None, sniff=False):
	" Loads data from a csv file "
	if dialect is None:	dialect = Dialect()
	if sniff:	dialect.sniff(csvFileName, verbose=False)
	return reader(csvFileName, dialect)
	# return [R for R in Reader]
	
def loadTable(csvFileName, dialect=None, sniff=True):
	" Loads table from a csv file (first line expected to be header) and returns list of dicts "
	T = list(load(csvFileName, dialect=dialect, sniff=sniff))
	if T:
		return [dict(zip(T[0], R)) for R in T[1:]]
	return []


def save(Data, csvFileName, dialect=None, CryptKey=None, verbose=False, Encoding=None):
	" Saves data to a csv file "
	if dialect is None:	dialect = Dialect()
	# Determining file extension
	if os.path.splitext(csvFileName)[1] == '':	csvFileName += dialect.extension()
	try:
		if CryptKey is not None:
			CryptingOK = True
			csvFile = open(csvFileName, 'wb')
			try:
				if dialect.entete:	
					csvFile.write(pyCrypt.p3_encrypt(dialect.entete + '\n', CryptKey))
				W = writer(None, dialect)
				csvStr = ''
				# Compatibility:	provisoire
				Data1 = [d for d in Data]
				for D in Data1:	csvStr += W.writerow(D)
				csvFile.write(pyCrypt.p3_encrypt(csvStr.encode(ENCODING), CryptKey))
			except (TypeError, pyCrypt.CryptError) as E:	
				####### Provisoire
				print(E)
				print('*************** Python2 COMPATIBILITY ****************')
				CryptingOK = False
				tmpFile = open('tmpfile000.csv', 'w')
				if dialect.entete:	tmpFile.write(dialect.entete + '\n')
				W = writer(tmpFile, dialect)
				for D in Data1:	W.writerow(D)
				tmpFile.close()
			csvFile.close()	
		else:
			if Encoding is None: Encoding = ENCODING
			if Python3:	csvFile = open(csvFileName, 'w', encoding=Encoding, errors='replace', newline='\r\n')
			else:	csvFile = open(csvFileName, 'w')
			if dialect.entete:	csvFile.write(dialect.entete + '\n')
			W = writer(csvFile, dialect)
			for D in Data:	W.writerow(D)
			csvFile.close()
		if CryptKey and not CryptingOK:
			####### Provisoire
			os.system('cmd /C decrypte -e tmpfile000.csv %s' % csvFileName)
			os.system('cmd /C del tmpfile000.csv')
			
		if verbose:	print('%s created' % csvFileName)
	except IOError:
			print('*************** ERROR *******************')
			print('* Unable to open %s for writing' % csvFileName)
			print('*****************************************')
	
	
if __name__ == "__main__":
	print(__doc__)


__author__ = 'Dessalles'
