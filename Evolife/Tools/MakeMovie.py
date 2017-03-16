#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################


##############################################################################
#  MakeMovie: puts Evolife screen shots side by side                         #
##############################################################################


import os
import PIL.Image as PI
import re
from collections import OrderedDict

GifFileName = 'EvolifeMovie.gif'
WindowSize = (480,320)
# WindowSize = (300,225)



# convert -size 1200x800 xc:white _
# __Curves__000001.png -geometry 500x300 -composite ___Field___000001.png -geometr
# y 200x150+30+20 -composite -append abc.gif


import sys
import glob

def sideBYside(imNames, ResultName, size=None, Layout="1234"):
	# Layout indicate how images are laid out
	# images are numbered as in a four-image comics
	# the last image adapts its size

	Images = {}
	Sizes = {}
	
	for (imNro, imName) in enumerate(imNames):
		Images[imNro] = PI.open(imName)
		
	Frame = None

	if len(imNames) == 1 and size:	
		Frame = Images[0].resize(size)


	if len(imNames) == 2:
		if size: 
			for im in Images: Images[im] = Images[im].resize(size)
		for im in Images: Sizes[im] = Images[im].size
		if Layout == '12':
			Frame = PI.new("RGB", (Sizes[0][0]+Sizes[1][0], max(Sizes[0][1], Sizes[1][1])), "#F0B554")	
			Frame.paste(Images[0], (0,0))
			Frame.paste(Images[1], (Sizes[0][0],0))
		elif Layout == '13':
			Frame = PI.new("RGB", (max(Sizes[0][0], Sizes[1][0]), Sizes[0][1]+Sizes[1][1]), "#F0B554")	
			Frame.paste(Images[0], (0,0))
			Frame.paste(Images[1], (0, Sizes[0][1]))
		else:	print('Incorrect layout %s for %d images' % (Layout, len(imNames)))
	elif len(imNames) == 3:
		if Layout == '122':		# three images side by side
			if size: 
				for im in Images: Images[im] = Images[im].resize(size)
			for im in Images: Sizes[im] = Images[im].size
			Frame = PI.new("RGB", (Sizes[0][0]+Sizes[1][0]+Sizes[2][0], max(Sizes[0][1], Sizes[1][1], Sizes[2][1])), "#F0B554")	
			Frame.paste(Images[0], (0,0))
			Frame.paste(Images[1], (Sizes[0][0],0))
			Frame.paste(Images[2], (Sizes[0][0] + Sizes[1][0],0))
		elif Layout == '134':
			if size: 
				size2 = (size[0]//2, size[1]//2)
				Images[0] = Images[0].resize(size2)
				Images[1] = Images[1].resize(size2)
				Images[2] = Images[2].resize(size)
			for im in Images: Sizes[im] = Images[im].size
			Frame = PI.new("RGB", (Sizes[0][0] + Sizes[2][0], max(Sizes[0][1]+Sizes[1][1],Sizes[2][1])), "#F0B554")	
			Frame.paste(Images[0], (0,0))
			Frame.paste(Images[1], (0, Sizes[0][1]))
			Frame.paste(Images[2], (Sizes[0][0], 0))
		else:	print('Incorrect layout %s for %d images' % (Layout, len(imNames)))
	elif len(imNames) == 4:
		if size: 
			for im in Images: Images[im] = Images[im].resize(size)
		for im in Images: Sizes[im] = Images[im].size
		Frame = PI.new("RGB", (Sizes[0][0]+Sizes[1][0], Sizes[0][1]+Sizes[2][1]), "#F0B554")	
		Frame.paste(Images[0], (0,0))
		Frame.paste(Images[1], (Sizes[0][0],0))
		Frame.paste(Images[2], (0, Sizes[0][1]))
		Frame.paste(Images[3], (Sizes[0][0],Sizes[0][1]))
	
	if Frame:	Frame.save(ResultName)
			

# # Prefixes = OrderedDict(
			# # 'Curves'= '___Curves_',
			# # 'Networks'= '___Network_',
			# # 'Fields'= '___Field_',
			# # 'Trajectories'= '___Traj_',
			# # 'Genomes': '___Genome_',
			# # )
# # print(list(Prefixes.values()))
# # print([Prefixes[P] for P in Prefixes])
Prefixes = [
			'___Curves_', 
			'___Network_', 
			'___Field_', 
			'___Traj_', 
			'___Genome_', 
			]
Extensions = ['.png', '.jpg']

Images = {}
Frames = []

if __name__ == "__main__":
			
	for ImType  in Prefixes:
		Ims = glob.glob('%s*' % ImType)
		print('%d images of type %s found' % (len(Ims), ImType))
		if Ims:
			Images[ImType] = Ims
			if not Frames:
				Frames = [re.search('\d+', Image).group(0) for Image in Ims]
			
	LayoutSize = len(Images)
	Layout = [None, '1', '12', '134', '1234'][LayoutSize]	# default layouts
	# Layout = [None, '1', '12', '122', '1234'][LayoutSize]	
	for F in Frames:
		for ext in Extensions:
			imageNames = [N for N in glob.glob('*%s*%s' % (F,ext)) if N.split('0')[0] in Prefixes]
			imageNames.sort(key = lambda N: Prefixes.index(N.split('0')[0]))	
			if imageNames:
				print(' '.join(imageNames))
				sideBYside(imageNames, '___CF_%s.png' % F, WindowSize, Layout)

	# preparing a last blank image, just in case (good for looping Gifs)
	PI.new("RGB", PI.open('___CF_%s.png' % F).size, "#F0B554").save('___CF_Last.png')
			
			
	# for curve in glob.glob('___Curves*'):
		# NroFrame = re.search('\d+', curve).group(0)
		# for field in glob.glob('___Field___%s*' % NroFrame):
			# print NroFrame
			# sideBYside(curve, field, '___CF_%s.png' % NroFrame, WindowSize)


	print('Making animated Gif %s using ImageMagick' % GifFileName)
	# os.system('convert.bat -delay 2 ___CF_0*.png -loop 1 %s' % GifFileName)
	os.system('convert.bat -delay 12 ___CF_0*.png -loop 0 %s' % GifFileName)



__author__ = 'Dessalles'
