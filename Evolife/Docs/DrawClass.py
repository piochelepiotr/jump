#!/usr/bin/env python




import sys
sys.path.append('e://Prog//Python')
sys.path.append('.//Genetics')
sys.path.append('.//Scenarii')

from draw_classes import MROgraph

from Individual import Individual
from Observer import *

##class toto(Individual, object): pass

g1 = MROgraph(Individual,filename="Individual.png",setup='size="5,5"; ')
g2 = MROgraph(Observer,filename="Observer.png",setup='size="5,5"; ')


__author__ = 'Dessalles'
