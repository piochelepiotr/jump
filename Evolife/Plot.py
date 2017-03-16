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

sys.path.append('..')
sys.path.append('../..')
sys.path.append('../../..')

import Evolife.QtGraphics.Evolife_Window as EW
import Evolife.Ecology.Observer as EO
import Evolife.Scenarii.Parameters as EP
import Evolife.Tools.Tools as ET
try:	import TableCsv as CSV
except ImportError:	import Evolife.Tools.TableCsv as CSV


class Plot:
	def __init__(self, ExpeFile, Observer, ConstantConfigFileName=None):	
		ExpeFile = os.path.splitext(ExpeFile)[0]
		if ExpeFile.endswith('_res'):	ExpeFile = ExpeFile[:-4]
		self.Dirname, self.ExpeName = os.path.split(ExpeFile)
		self.Obs = Observer
		self.Obs.recordInfo('Title', self.ExpeName)
		PlotFile = ExpeFile + '.csv'
		self.ConfigFileName = ExpeFile + '_res.csv'
		# if not os.path.exists(self.ConfigFileName):	self.ConfigFileName = ExpeFile + '.res'	# backward compatibility
		self.Cfg = self.RetrieveConfig(self.ConfigFileName)	# retrieve parameters 
		self.FieldDisplay = self.Field(self.ConfigFileName)
		self.PlotOrders = CSV.load(PlotFile, sniff=True)	# loading csv file
		try:	self.Legend = next(self.PlotOrders)		# reading first line with curve names
		except StopIteration:	sys.exit(0)
		# declaring curves
		for Curve in range(1, 1+len(self.Legend[1:])):
			print(Curve, self.Legend[Curve])
			self.Obs.curve(Name=self.Legend[Curve], Value=Curve, Color=Curve, Legend=self.Legend[Curve])
		self.Obs.recordInfo('ResultFile', '___Plot_')
		self.Obs.setOutputDir('.')			
		self.RelevantParam = self.RelevantConfig(self.ExpeName, ConstantConfigFileName)	# display parameters 
		
	def one_plot(self):	
		try:	Order = next(self.PlotOrders)
		except StopIteration:	return False
		# print(Order)
		self.Obs.season(int(Order[0]))
		for Curve in range(1, 1+len(Order[1:])):
			self.Obs.curve(Name=self.Legend[Curve], Value=float(Order[Curve]))
		return True

	@classmethod
	def RetrieveConfig(self, ConfigFile):
		" Try to find relevant parameters "
		if os.path.exists(ConfigFile):
			CfgLines = open(ConfigFile).readlines()
			# reading parameters
			Sep = max([';', '\t', ','], key=lambda x: CfgLines[0].count(x))
			if len(CfgLines) > 1:
				Parameters = dict(zip(*map(lambda x: x.strip().split(Sep), CfgLines[:2])))
			return EP.Parameters(ParamDict=Parameters)
		return None
		
	def RelevantConfig(self, ExpeName, ParameterFile):
		" Try to find relevant parameters "
		if self.Cfg is None or not ParameterFile:	return None
		RelevantParameters = {}
		CP = EP.Parameters(ParameterFile)
		# determining relevant parameters
		for p in CP:
			if p in self.Cfg and CP[p] != self.Cfg[p]:
				RelevantParameters[p] = self.Cfg[p]
				# CP.addParameter(p, self.Cfg[p])
		RelevantParameters = EP.Parameters(ParamDict=RelevantParameters)
		return (RelevantParameters)
		
	def Field(self, ConfigFile):
		if not os.path.exists(ConfigFile):	return None
		Result = open(ConfigFile).readlines()
		# reading recorded positions
		FieldPlot = None
		if len(Result) > 3:
			FieldPlot = Result[3].strip().split('\t')[1:]
			NbP = len(FieldPlot)
			self.Obs.record(list(zip(range(NbP), map(float, FieldPlot), [7]*NbP, [6]*NbP)))
			# print(FPlot)
		return FieldPlot
		
	def save(self, OutputDir='.'):
		Prefix = os.path.join(OutputDir, '___%s.png' % self.ExpeName)
		FI = glob.glob('___Field*.png')
		CI = glob.glob('___Curves*.png')
		if len(FI) + len(CI) == 0:	return
		FI.sort(key = lambda f: os.stat(f).st_mtime)
		CI.sort(key = lambda f: os.stat(f).st_mtime)
		FIm = PI.open(FI[-1]).resize((400, 300))
		CIm = PI.open(CI[-1]).resize((400, 300))
		Frame = PI.new("RGB", (800, 300), "#F0B554")	
		Frame.paste(CIm, (0,0))
		Frame.paste(FIm, (400,0))
		Frame.save(Prefix)		
		os.remove(FI[-1])
		os.remove(CI[-1])
		print('%s generated' % Prefix)

def Parse(Args):
	Files = []
	ConstantConfigFileName = None
	if len(Args) < 2:
		# find last file
		CsvFiles = glob.glob('___Results/*.csv')
		if CsvFiles:
			CsvFiles.sort(key=lambda x: os.stat(x).st_mtime)
			Files = [CsvFiles[-1]]
	elif len(Args) > 3:
		print('''Usage:	%s <curve file name> [<constant config file name>]''' % os.path.basename(Args[0]))
	else:
		Files = glob.glob(Args[1])
		ConstantConfigFileName = Args[2] if (len(Args) == 3) else None
	for Argfile in Files:
		yield (Argfile, ConstantConfigFileName)
	
if __name__ == "__main__":
	for (Argfile, ConstantConfigFileName) in Parse(sys.argv):
		if Argfile:
			Observer = EO.Generic_Observer('')
			plot = Plot(Argfile, Observer, ConstantConfigFileName)
			print(plot.RelevantParam if plot.RelevantParam else plot.Cfg)
			Cap = 'CFP' if plot.FieldDisplay else 'CP'	
			EW.Start(plot.one_plot, plot.Obs, Capabilities=Cap, Options=[('Run', 'Yes'), ('ExitOnEnd', 'No')])		# start Evolife display
			if plot.FieldDisplay:	plot.save()

__author__ = 'Dessalles'
