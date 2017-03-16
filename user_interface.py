#!/usr/bin/env python
from time import sleep
from random import randint

import sys
sys.path.append('')

import Evolife.QtGraphics.Evolife_Window as EW
import Evolife.Ecology.Observer as EO



class Observer(EO.Generic_Observer):
    """ Stores all values that should be displayed
        May also store general information
    """

    def __init__(self, TimeLimit):
        EO.Generic_Observer.__init__(self)
        self.TimeLimit = TimeLimit
        self.curve(Name='Time', Color='blue', Legend='time step + noise')    # declaration of a curve
        # Then, to add a point to the curve, call:
        # curve('Time', y)
        # This adds a point (t, y) to the curve, where t is the current time step
        
        # the following information will be displayed in the "Legend" window
        self.recordInfo('WindowLegends', """The "field" window shows moving vectors.<br>The "Trajectories" window shows one rotating segment""")

    def Field_grid(self):
        return []
                # to draw lines with various dot sizes and segment thickness, name the segments
                # [(segm1, (5, 5, 'green', 8, 95, 5, 'green', 2)),
                #  (segm2, (95, 5, 'green', 5, 95, 95, 'green', 3),]
                # and be sure to use 'Region' instead of 'Field' when calling Evolife 'Start'
        
    def get_data(self, Slot):

        # This function is called each time the window wants to update display
        
        #--------------------------------------------------------------------------#
        # Displaying genomes    (option G when starting Evolife)                   #
        #--------------------------------------------------------------------------#
        if Slot == 'DNA':
            # Should return a list (or tuple) of genomes
            # Each genome is a tuple like (0,1,1,0,1,...)
            # All genomes should have same length
            pass
            
        #--------------------------------------------------------------------------#
        # Displaying social links    (option N (== network) when starting Evolife)  #
        #--------------------------------------------------------------------------#
        elif Slot == 'Network':
            # Should return a list (or tuple) of friends
            #     ((Agent1Id, Friends1), (Agent2Id, Friends2), ...)
            # Agents' Ids should be consistent with agents' positions sent to 'Field'
            # Friends = list of agents Ids to which the agent is connected
            # Currently, only links to best friends are displayed
            pass
            
        return EO.Generic_Observer.get_data(self, Slot)    # default behaviour 

        #--------------------------------------------------------------------------#
        # Displaying images    (option F when starting Evolife)                       #
        #--------------------------------------------------------------------------#
        if Slot == 'Image':
            # Should return the path to an image file
            return default

        #--------------------------------------------------------------------------#
        # Displaying patterns (option T when starting Evolife)                     #
        # (same as slot 'Image', but for the 'Trajectories' window)                  #
        #--------------------------------------------------------------------------#
        elif Slot == 'Pattern':
            # Should return the path to an image file
            return default
            
        else:   return EO.Generic_Observer.get_info(self, Slot, default=default)    # basic behaviour


class Agent:
    "   class Agent: defines what an individual consists of "
    def __init__(self, IdNb):
        self.id = "A%d" % IdNb    # Identity number
        if IdNb % 2:    self.colour = 'red'
        else:            self.colour = 'blue'    # available colours are displayed at the right of Evolife curve display, from bottom up.
        self.Location = (IdNb, randint(0, IdNb), self.colour, 5)    #  (x, y, colour, size)
    
    def move(self):    
        pass
        # Just a brownian vertical movement
        # print('.', end="", flush=True),
        # Coordinates:  (x, y, colour, size, toX, toY, segmentColour, segmentThickness)
        #self.Location = (self.Location[0], max(10, self.Location[1] + randint(-1, 1)), self.colour, 5, 50, 10, 'grey', 1)    # 5 == size of blobs
        
class Population:
    " defines the population of agents "

    def __init__(self, NbAgents, Observer):
        " creates a population of agents "
        self.Pop = []
        self.Obs = Observer
        self.Obs.Positions = self.positions()
                 
    def __iter__(self):    return iter(self.Pop)    # allows to loop over Population
    
    def positions(self):
        return dict([(A.id, A.Location) for A in self.Pop])
        
        



Obs = Observer(TimeLimit=1000)   # Observer stores graphic orders and performs statistics
Pop = Population(NbAgents=100, Observer=Obs)   # population of agents
        
################################################      
# This function is run at each simulation step #    
################################################      
def one_year():
    Obs.StepId += 1    # udates simulation step in Observer
    for agent in Pop:    agent.move()        # whatever behaviour one wants to simulate
    
    # Storing agents' positions for display
    #Obs.record(list(Pop.positions().items()), Window='Field', Reset=True)    # let Observer know position changes
    # Storing the ant's position for display
    #Obs.record(('obstacle0', (0, 0, 2, 100, 'shape=rectangle')), Window='Field')
    Obs.record(('obstacle0', (200,200, 2, 100, 'shape=rectangle')), Window='Field')
    Obs.record(('uhsqif', (10, 0, 1, 100, 'shape=rectangle')), Window='Field')
    return True


    
def Start():
    Obs.setOutputDir('___Results')    # curves, average values and screenshots will be stored there
    Obs.recordInfo('Background', 'grey')    # windows will have this background by default
                                            # Background could be 'yellow' or 'toto.jpg' or '11' or '#F0B554'
    #Obs.recordInfo('CurvesWallpaper', '../QtGraphics/EvolifeBG.png')
    #Obs.recordInfo('TrajectoriesWallpaper', '../QtGraphics/EvolifeBG.png')
    Obs.recordInfo('DefaultViews',    [('Field',500,500)])    # Evolife should start with these windows open
    Obs.record(('obsta', (500,500, 2, 1, 'shape=rectangle')), Window='Field')

    #--------------------------------------------------------------------------#
    # Start: launching Evolife window system                                   #
    #--------------------------------------------------------------------------#
    # Start(Callback function, Observer, Capabilities, Options)
    # Callback function:    this locally defined function is called by Evolife at each time step
    # Observer:    locally defined 
    # Capabilities: string containing any of the following letters
    #    C = Curves 
    #    F = Field (2D seasonal display) (excludes R)
    #    G = Genome display
    #    L = Log Terminal (not implemented)
    #    N = social network display
    #    P = Photo (screenshot)
    #    R = Region (2D ongoing display) (excludes F)
    #    T = Trajectory display (requires additional implementation in each case)

    EW.Start(
        one_year, 
        Obs, 
        Capabilities='FG'
        )
    


if __name__ == "__main__":
        print(__doc__)
        Start()
        print("Bye.......")
        sleep(1.1)    


__author__ = 'Dessalles'
