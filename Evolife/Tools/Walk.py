#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################
"""
	Walks through a file system tree and execute a command on files
"""

import sys
import os
import os.path
import re
import Replace

def Filtered(Name, Filter):
	" checks whether a file Name is Filtered "
	if not isinstance(Filter, list):	
		Filter =  [Filter]
	for Pattern in Filter:
		if re.match(Pattern, Name, re.IGNORECASE) is not None:
			return True
	return False

def Browse(StartDir, Action, SelectFilter=[], AvoidFilter=[], Verbose=True, Recursive=True):
	" Walks through the tree under StartDir and performs Action on files - Filters are lists of regular expressions "
	for (R,D,F) in os.walk(StartDir):
		for Dir in D[:]:
			if Filtered(Dir, AvoidFilter):
				if Verbose:	print('\tPruning {0}'.format(os.path.join(R,Dir)))
				D.remove(Dir)	# don't dig into subtree
		for fich in F:
			if Filtered(fich, AvoidFilter): continue
			if SelectFilter and not Filtered(fich, SelectFilter): continue
			try:
				fname = os.path.abspath(os.path.join(R,fich))
				if Verbose:	print(fname)
				Action(fname)
			except (WindowsError, IOError):
				print("\nXXXXXXX Erreur sur {0}/{1}".format(R,fich))
		if not Recursive:
			break

def SubstituteInTree(StartDir, FilePattern, OldString, NewString, Verbose=True, CommentLineChars=''):
	"""	Replaces OldString by NewString anywhere in all file below 'StartDir' with extension 'Extension'
	"""
	Action = lambda x: Replace.SubstituteInFile(x, OldString, NewString, Verbose=1, CommentLineChars=CommentLineChars)
	Browse(StartDir, Action, FilePattern, Verbose=Verbose)


if __name__ == '__main__':
	# print("Do you want to replace all tabs by spaces in python source files")
	# if vars(__builtins__).get('raw_input',input)('? ').lower().startswith('y'):
		# Detabify
		# SubstituteInTree('.', '.*.py$', '\\t', ' '*4, CommentLineChars='#')
		# ReTabify
		# Walk.SubstituteInTree('.', '.*.py$', ' '*4, '\\t', CommentLineChars='#')
		
	StartDir = None
	if len(sys.argv) == 6 and os.path.exists(sys.argv[4]):	StartDir = sys.argv[4]; CommentLineChars = sys.argv[5]
	elif len(sys.argv) == 5 and os.path.exists(sys.argv[4]):	StartDir = sys.argv[4]; CommentLineChars = ''
	elif len(sys.argv) == 4:	StartDir = '.'; CommentLineChars = ''
	print(StartDir)
	print(len(sys.argv))
	print(sys.argv)
	
	if StartDir:
		SubstituteInTree(StartDir, sys.argv[1], sys.argv[2], sys.argv[3], CommentLineChars=CommentLineChars)
		print('Done')
	else:
		print(\
		"""Usage:
%s <FilePattern> <OldStrPattern> <NewStrPattern> [<StartDir> [CommentChars]] 
Replaces all occurrences of OldStrPattern by NewStrPattern 
in files matching FilePattern in the tree rooted in StartDir (= '.' by default)
except in lines starting with comment chars
If StartDir is made explicit, then Comment chars can be given as a string.
""" % os.path.basename(sys.argv[0]))
		
		

__author__ = 'Dessalles'
