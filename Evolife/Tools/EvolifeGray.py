#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################


##############################################################################
#  Implements a Gray code                                                    #
#  Note: according to Wikipedia, the French engineer Emile Baudot used 'Gray #
#  codes' in telegraphy long before they were 'invented', in 1878.           #
#  http://en.wikipedia.org/wiki/Gray_code                                    #
##############################################################################

""" This module implements a Gray code, using a function
	borrowed from http://www.finalcog.com/python-grey-code-algorithm
	usage:
	G = GrayCode()
	G.Gray2Int(17) = 25
	If you want to visualize the table:
	G = GrayCode(5)
	print G
"""
  
import math

class GrayCode(object):

	def __init__(self, Length=8):	
		self.GrayTable = dict()
		self.InitGrayTable(Length)

	def InitGrayTable(self, Length):
		# print "Initializing a %d-bit long Gray Table" % Length
		self.Length = Length
		for ii in range(2 << (Length-1)):
			self.GrayTable[ii] = self.Int2Gray(ii)
 
	def Int2Gray(self,i):
		"""
		This function returns the i'th Gray Code.
		It is recursive and operates in O(log n) time.
		This function is borrowed from http://www.finalcog.com/python-grey-code-algorithm
		"""
		if i == 0: return 0
		if i == 1: return 1
		ln2 = int(math.log(i,2))
		# the grey code of index i is the same as the gray code of an index an 
		# equal distance on the other side of ln2-0.5, but with bit ln2 set
		pivot = 2**(ln2) - 0.5 # TODO: double everything so that we use no floats
		delta = i - pivot
		mirror = int(pivot - delta)
		x = self.Int2Gray(mirror)	# get the grey code of the 'mirror' value
		x = x + 2**(ln2)	# set the high bit
		return x

	def Gray2Int(self, GrayIndex):
		" converts a coded integer into a decoded integer by using a Gray code "
		try:
			return self.GrayTable[GrayIndex]
		except KeyError:
			self.InitGrayTable(int(math.log(GrayIndex,2))+1)
			return self.GrayTable[GrayIndex]
			
			

	def PaddedGray(self, i):
		" return a padded binary string for i "
		S = '0' * self.Length + bin(i)[2:]
		return S[-self.Length:]
   
	def __repr__(self):
		return '\n'.join([self.PaddedGray(self.GrayTable[ii]) for ii in self.GrayTable])


__author__ = 'Dessalles'
