#!/usr/bin/env python
##############################################################################
# EVOLIFE  http://evolife.telecom-paristech.fr         Jean-Louis Dessalles  #
# Telecom ParisTech  2017                                  www.dessalles.fr  #
# -------------------------------------------------------------------------- #
# License:  Creative Commons BY-NC-SA                                        #
##############################################################################


##############################################################################
#  Simulation thread                                                         #
##############################################################################


""" EVOLIFE: Simulation thread """

from sys import excepthook, exc_info
from threading import Thread
from time import sleep


##################################################
# Simulation Thread                              #
##################################################

class Simulation(Thread):
	""" Thread triggered by the "Step" and "Run" buttons
		of the Evolife window system
	"""
	def __init__(self, OneStep, funcmode, ReturnFromThread):
		Thread.__init__(self)
		self.Back = ReturnFromThread
		self.Continuous = funcmode
		self.Running = False
		self.BusyDisplay = False   # indicates that display needs time to update
		self.OneStep = OneStep	  # function that runs one simulation step

	def stop(self):
		""" stops the thread """
		if self.Running:
			self.Running = False
		if self.BusyDisplay:
			while self.Back('Busy?'):
				sleep(0.1)
			# print "stopping the process"
			self.join()

	def run(self):
		""" launched by start() """
		self.Running = True
		while self.Running:
			try:
				ReturnFromDisplay = self.Back(self.OneStep())
				if ReturnFromDisplay < 0:
					# We have to stop
					self.running = False
					break
				elif ReturnFromDisplay > 0:
					# Display is jammed - We have to wait
					self.BusyDisplay = True
					while self.Back('Busy?'):
						sleep(0.1)
					self.BusyDisplay = False
			except:
					self.running = False
					excepthook(exc_info()[0],exc_info()[1],exc_info()[2])
					break
			if not self.Continuous:
				break



#################################
# Test                          #
#################################

if __name__ == "__main__":
	print(__doc__ + '\n')
	print(Simulation.__doc__ + '\n')
	raw_input('[Return]')


__author__ = 'Dessalles'
