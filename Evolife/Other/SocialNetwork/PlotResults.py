#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################

##############################################################################
# Draw curves offline                                                        #
##############################################################################

""" Draw curves offline.
	Takes a csv file as input and draws curves.
"""


import sys
import os
import re
import glob
import PIL.Image as PI
from time import sleep

sys.path.append('..')
sys.path.append('../..')
sys.path.append('../../..')
sys.path.append('e:\\recherch\\evolife')

import Evolife.QtGraphics.Evolife_Window as EW
import Evolife.Ecology.Observer as EO
import Evolife.Scenarii.Parameters as EP
import Evolife.Tools.Tools as ET
import TableCsv as CSV
import Plot as DefPlot

# sys.path.append('../SocialNetwork')
import SocialRunaway as EN

class Plot(DefPlot.Plot):
		
	def Field(self, ConfigFile):
		if not os.path.exists(ConfigFile):	return None
		Result = open(ConfigFile).readlines()
		SI = [L for L in Result if L.startswith('SignalInvestment\t')]
		FieldPlot = None
		if len(SI) >= 1:
			# reading recorded positions
			FieldPlot = SI[-1].strip().split('\t')[1:]
			NbP = len(FieldPlot)
			CompetenceThreshold = self.Cfg['CompetenceThreshold']
			CompetenceMin = self.Cfg['CompetenceMin']
			vertices = self.Cfg['CompetenceVertices']
			vertices = eval(vertices)
			L = lambda qsi: ET.Polygon(qsi[0], vertices) * float(qsi[1]) / 100.0			
			self.Obs.record(list(zip(range(NbP), map(L, enumerate(FieldPlot)), [7]*NbP, [6]*NbP)))
		elif ConfigFile.find('_res') > 0:	
			# second try for backward compatibility
			CfgFile2 = os.path.splitext(ConfigFile)[0][:-4] + '.res'
			print('second chance %s' % CfgFile2)
			return self.Field(CfgFile2)
		return FieldPlot
		
	def save(self, OutputDir='.'):
		if self.FieldDisplay:
			for prm in ['BatchMode', 'TimeLimit', 'DumpStart']:
				if self.RelevantParam:	self.RelevantParam.pop(prm, None)	# ignore difference concerning that parameter
			if self.RelevantParam and len(self.RelevantParam) == 1:	
				Param = list(self.RelevantParam.keys())[0]
				Prefix = '___%s_%s_%s.png' % (Param, str(self.RelevantParam[Param]), self.ExpeName)
			else:
				Prefix = '___%s.png' % self.ExpeName
			Prefix = os.path.join(OutputDir, Prefix)

			# FI = glob.glob(os.path.join(self.Dirname, '___Field*.png'))
			# CI = glob.glob(os.path.join(self.Dirname, '___Curves*.png'))
			FI = glob.glob('___Field*.png')
			CI = glob.glob('___Curves*.png')
			if len(FI) + len(CI) == 0:	return
			FI.sort(key = lambda f: os.stat(f).st_mtime)
			CI.sort(key = lambda f: os.stat(f).st_mtime)
			if len(FI) > 1 or len(CI) > 1:	
				print('WARNING: ambiguous input images')
				print('no image generated')
				os.remove(FI[0])
				os.remove(CI[0])
			else:
				FIm = PI.open(FI[-1]).resize((400, 300))
				CIm = PI.open(CI[-1]).resize((400, 300))
				Frame = PI.new("RGB", (800, 300), "#F0B554")	
				Frame.paste(CIm, (0,0))
				Frame.paste(FIm, (400,0))
				Frame.save(Prefix)		
				os.remove(FI[-1])
				os.remove(CI[-1])
				print('%s generated' % Prefix)
			


if __name__ == "__main__":
	for (Argfile, ConstantConfigFileName) in DefPlot.Parse(sys.argv):
		print('file: %s ...' % Argfile, end=" ")
		try:	Timestamp = re.search('(\d{12})', Argfile).group(1)
		except AttributeError:	Timestamp = 'dummy'
		if len(glob.glob(os.path.join(os.path.dirname(Argfile), '*%s.png' % Timestamp))) > 0: 
			print('already treated')
			sleep(1)
			continue
		if Argfile:
			ConfigFileName = os.path.splitext(Argfile)[0] + '_res.csv'
			Cfg = Plot.RetrieveConfig(ConfigFileName)
			if Cfg:
				Obs = EN.Observer(Cfg)
				plot = Plot(Argfile, Obs, ConstantConfigFileName)
				print()
				print(plot.RelevantParam if ConstantConfigFileName else plot.Cfg)
				Cap = 'CFP' if plot.FieldDisplay else 'CP'	
				Term = 'Yes' if plot.FieldDisplay else 'No'
				EW.Start(plot.one_plot, Obs, Capabilities=Cap, Options=[('Run', 'Yes'), ('ExitOnEnd', Term), ('Background', 'lightblue')])		# start Evolife display
				if plot.FieldDisplay:	plot.save(os.path.dirname(Argfile))
			else:	print('%s absent ou incorrect' % ConfigFileName)
			


__author__ = 'Dessalles'
