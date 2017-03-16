#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################
"""
	Walking through a file system tree to modify file headers
"""

import sys
import os
import re
import Walk
import datetime

Header = None

	
def ChangeHeader(PythonProgam):
	global Header
	if Header is None:
		Header = open('Header.txt').read().replace('0000', str(datetime.datetime.now().year))
	ProgramContent = open(PythonProgam).read()
	(NewProgramContent, count) = re.subn(r'(?m)^##+\s*(?:^#\s.*#\s*)+^##+[ \t]*$', Header, ProgramContent, 1)
	if count:
		open(PythonProgam, 'w').write(NewProgramContent)
		# print('Header of %s changed' % PythonProgam)
	
if __name__ == "__main__":
	print(__doc__)
	if len(sys.argv) == 2 and os.path.isdir(sys.argv[1]):
		Walk.Browse(sys.argv[1], ChangeHeader, '.*\.py$', Verbose=False)
	else:
		print('Usage: %s <Startdir>\nUpdates header in python files' % os.path.basename(sys.argv[0]))

