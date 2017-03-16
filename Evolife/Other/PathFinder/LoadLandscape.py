#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################


#########################################################################
# recupere une matrice a partir d'une image                             #
#   Jean-Louis Dessalles 08.2013                                        #
#########################################################################
"""	
	Loads an image and saves it as an integer list	
"""

import os.path as op
from PIL import Image

# LandscapeOriginal = 'landscape_orig.png'
LandscapeOriginal = 'landscape_3.png'	# original image
Landscape = 'landscape_3a.png'		# zoomed copy generated by the program
OutputFile = op.splitext(Landscape)[0] + '.dat'
LevelCompression = 2	# compression of the number of grey values
ZOOM = 0.5	# size change factor

def ImageToList(ImgName, zoomFactor=1.0):
	" returns image as a list of lists of integers "
	
	I = Image.open(ImgName)	# load image
	(w,h) = I.size	# image dimensions
	I = I.resize((int(w*zoomFactor), int(h*zoomFactor)))	# resizing
	I.save(Landscape)
	
	(w,h) = I.size	# image dimensions
	print(w,h)
	ImageAsIntegers = list(I.getdata())	# converting image to string
	# dividing all values by 2
	ImageAsIntegers = map(lambda x: x//LevelCompression, ImageAsIntegers)
	return [ImageAsIntegers[row*w:row*w+w] for row in range(h) ]	# array of integers


if __name__ == "__main__":
	print __doc__
	print('Loading %s' % LandscapeOriginal)
	IntegerArray = ImageToList(LandscapeOriginal, zoomFactor = ZOOM)
	print('Saving image as integer array with level compression %d into %s' % (LevelCompression, OutputFile))
	Output = open(OutputFile, 'w')
	for row in IntegerArray:
		Output.write(' '.join(map(str, row)))
		Output.write('\n')
	Output.close()
	

__author__ = 'Dessalles'
