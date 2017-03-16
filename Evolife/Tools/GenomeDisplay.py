#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################
"""
Shows genome images in a suitable form to observe evolution      
"""

import glob
import os.path 
import re

# Python Imaging Library - http://www.pythonware.com/products/pil/
from PIL import Image	  # to interface Python Imaging Library with Tkinter


# images to be treated (as a function of frame number)
Prefix = '___Genome_'
FileName = lambda N: '%s%s.png' % (Prefix, str(N).rjust(6, '0'))

# No of lines to keep in each image
NoLines = 5
# No of images to sample
NoImages = 600//NoLines

# Output file
ResultFile = 'Result.png'


def usage():
	print """
		Usage: %s 
		""" % (sys.argv[0])
	raw_input('\n[Entree]')
	

if __name__ == "__main__":
					
	print __doc__
	
	# How many input images 
	Inputs = glob.glob(FileName(999999).replace('999999', '*'))
	First = int(re.findall('(\d+)', Inputs[0])[0])
	Last = int(re.findall('(\d+)', Inputs[-1])[0])
	
	# Building blank image that will receive slices of input images
	FirstImage = Image.open(FileName(First))
	Width = FirstImage.size[0]
	Box = (0, 1, Width, 1+NoLines)
	ResultImage = Image.new(FirstImage.mode, (Width, NoLines * NoImages))
	
	Frame = 0
	# for No in range(First,1087, 2):
	for No in range(First, Last, len(Inputs)//NoImages):
		G = FileName(No)
		Genome = Image.open(G)
		print(G)
		Genome = Genome.crop(Box)
		# Genome = Genome.transpose(Image.ROTATE_90)
		# Genome.save(os.path.splitext(G)[0] + '.jpg')
		ResultImage.paste(Genome, (0, Frame * NoLines, Width, (Frame+1) * NoLines))
		Frame += 1
	ResultImage = ResultImage.transpose(Image.ROTATE_90)
	ResultImage.save(ResultFile)
	print('Output sent to %s' % ResultFile)



__author__ = 'Dessalles'
