#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################
"""	 Removes CR chars introduced by MsWindows
"""

import sys
import os.path

sys.path.append('Tools')

import Walk

if __name__ == '__main__':
	print(__doc__)
	print("Do you want to remove all CR in python source files")
	if input('? ').lower().startswith('y'):
		# Walk.Browse('.', print, '.*.pyw?$', Verbose=False)
		Walk.SubstituteInTree('.', '.*.pyw?$', '\\r', '', Verbose=False)
		print('Done')
	else:
		print ('Nothing done')

__author__ = 'Dessalles'
