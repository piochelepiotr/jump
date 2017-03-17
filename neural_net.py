# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 15:38:00 2017

@author: antoi and piochelepiotr
"""
import sys
sys.path.append('')

import numpy as np
import time
import random
import math
import Evolife.QtGraphics.Evolife_Window as EW
import Evolife.Ecology.Observer as EO

######
# Actions : 
#    0 : duck, 1 : do nothing 2 : jump


# constants
Obs = EO.Generic_Observer()
pop_size = 100
number_kept = 1
grid_length = 150
big_grid_length = 50
grid_width = 3
turns_predict = 2
n_inputs = grid_width*turns_predict + 1
n_outputs = 3
n_hidden = 10
first_pow = 0
number_grids = 1

gene_size = 3
dna_size = gene_size * (n_inputs + n_outputs )*n_hidden
mutation_rate = 0.005
crossover_ratio = 0.5
cst_genome = list(range(0,dna_size+1,gene_size))
number_crossover = 5

## USER INTERFACE
grid_display = 15
block_size = 100
window_width = grid_display*block_size
window_height = grid_width*block_size
generation = 0

class Grid:
    def __init__(self, grid_width,grid_length):
        self.width = grid_width
        self.length = grid_length
        cells = np.random.randint(1, 2, size = (grid_length, grid_width))
        pos = int(grid_width/2) #start in the middle
        for i in range(grid_length):
            cells[i][pos] = 0
            if(pos==0):
                move = random.randint(0,1) #can only go 
            elif(pos == grid_width-1):
                move = random.randint(-1,0)
            else:
                move = random.randint(-1,1)
            pos += move           
            cells[i][pos] = 0
        self.cells = cells
    def display(self):
        for pos in range(self.width):
            for i in range(self.length):
                print(self.cells[i][pos],end='')
            print()
        print()
            

def print_dna_diff(dna,diff):
    for i in range(150):
        if dna[i] != diff[i]:
            print('\x1b[6;30;42m',end='')
        print(dna[i],end='')
        if dna[i] != diff[i]:
            print('\x1b[0m',end='')

def print_dna(dna):
    for i in range(150):
        print(dna[i],end='')

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def matrix_sigmoid(M):
    try:
        (w,h) = M.shape
        Mp = np.zeros(shape=(w,h))
        for i in range(w):
            for j in range(h):
                Mp[i][j] = sigmoid(M[i][j])
        return Mp
    except:
        return np.array([sigmoid(M[i]) for i in range(len(M))])
  
#function to display a matrix

def display_matrix(M):
    (w,h) = M.shape
    for i in range(w):
        print('|',end="")
        for j in range(h):
            print(M[i][j],end="")
            if j == h-1:
                print('|',end="")
            else:
                print(' ',end="")
        print()

def genome_to_weight(dna,genome,w,h):
    W = np.random.normal(size=(w,h))
    n = 0
    for i in range(w):
        for j in range(h):
            W[i][j] = bin_to_double(dna[genome[n]:genome[n+1]])
            n = n+1
    return W
        
def genome_to_weights(dna,genome):
    #creates a neural network
    W1 = genome_to_weight(dna,genome,n_inputs,n_hidden)
    W2 = genome_to_weight(dna[n_inputs*n_hidden:],genome,n_hidden,n_outputs)
    return (W1,W2)
    


def predict(arg, W1, W2):
    intermediate = matrix_sigmoid(np.dot(arg,W1))
    return np.argmax(matrix_sigmoid(np.dot(intermediate,W2)))

def predict2(arg, W1, W2):
    intermediate = matrix_sigmoid(np.dot(arg,W1))
    return matrix_sigmoid(np.dot(intermediate,W2))

def choose(probas):
    sumDouble = sum(probas)
    rand = random.random()*sumDouble
    for i in range(len(probas)-1,0,-1):
        sumDouble -= probas[i]
        if rand > sumDouble:
            return i
    return 0
    
# a modifier pour négatifs à virgule 
def bin_to_double(bin_list):
    if len(bin_list) == 0:
        return 0
    n = 2**first_pow
    sumDouble = -n*bin_list[0]
    for i in bin_list[1:]:
        n /= 2
        sumDouble += n*i
    return sumDouble

def pop_compare(x,y):
    return x.score > y.score

class Individual:
    def __init__(self, dna_size, genome):
        self.dna_size = dna_size
        self.genome = genome
        self.DNA = None
        self.score = 0
    
    def generate_random(self):
        self.DNA = np.random.randint(2,size = self.dna_size)
        
    def mutate(self):
        for i in range(len(self.DNA)):
            if(random.random() < mutation_rate):
                self.DNA[i] = np.random.randint(2)
                
    def crossover(self,mother, father):
        #   computing random crossover points
        Loci_crossover = random.sample(range(1,self.dna_size), number_crossover)
        Loci_crossover = [0] + sorted(Loci_crossover)
        Loci_crossover.append(self.dna_size)
        # print Loci_crossover
        # the child's DNA will be read alternatively from parent1 and parent2
        parent1 = mother.DNA
        parent2 = father.DNA
        if np.random.randint(0,2):    # starting indifferently from mother or father
            parent1, parent2 = parent2, parent1     # swapping parents
        self.DNA = []
        for cut_point in range(len(Loci_crossover)-1):
            self.DNA += list(parent1[Loci_crossover[cut_point]:Loci_crossover[cut_point+1]])
            parent1, parent2 = parent2, parent1     # swapping parents        
            
    def make_score_one_grid(self,grid,W1=None,W2=None):
        i = 0
        list_pos = []
        pos = int(grid.width/2)
        go_on = True
        if W1 == None or W2 == None:
            (W1,W2) = genome_to_weights(self.DNA,self.genome)
        arg = grid.cells[0]
        for j in range(turns_predict-1):
            arg = np.concatenate([arg,grid.cells[j]])
        while(go_on):
            list_pos += [pos]
            arg = np.concatenate([arg[grid.width:],grid.cells[i+turns_predict-1]])
            action = predict(np.concatenate([arg,np.array([pos])]), W1, W2)-1
            pos = pos + action
            if pos < 0 or pos >= grid.width:
                go_on = False
            elif grid.cells[i][pos] == 1:
                go_on = False
            elif grid.cells[i+1][pos] == 1:
                go_on = False
            if go_on:
                i+=1
                if i >= grid.length-turns_predict:
                    go_on = False
        self.score = i
        return i,list_pos

    def make_score(self,grids):
        (W1,W2) = genome_to_weights(self.DNA,self.genome)
        score = 0
        for grid in grids:
            (sc,L) = self.make_score_one_grid(grid,W1,W2)
            score += sc
        self.score = score
        
class Population:
    
    runner_list = []
  
    def __init__(self, pop_size,grids):
        self.pop_size = pop_size
        for i in range(pop_size):
            r = Individual(dna_size, cst_genome)
            r.generate_random()
            self.runner_list.append(r)
            self.grids = grids
        for i in self.runner_list:
            i.make_score(grids)

    def evolve(self,generation):
        if generation == 0:
            self.runner_list.sort(key = lambda x : x.score,reverse=True)
        new_pop = []
        for i in range(number_kept):
            new_pop.append(self.runner_list[i])
        for i in range(self.pop_size-number_kept):
            new_pop.append(self.tournament(10))
        for i in new_pop:
            i.make_score(self.grids)
        new_pop.sort(key = lambda x : x.score,reverse=True)
        #print_dna_diff(new_pop[0].DNA,self.runner_list[0].DNA)
        #print("     best is : %d / %d" % (self.runner_list[0].score,number_grids*(self.grids[0].length-turns_predict)))
        self.runner_list = new_pop

    def bests(self):
        r = Individual(dna_size,cst_genome)
        r.crossover(self.runner_list[0],self.runner_list[1])
        r.mutate()
        return r
    
    def tournament(self,n):
        a = list(range(self.pop_size))
        selected = []
        for i in range(n):
            i = random.randint(0,len(a)-1)
            b = a[i]
            selected.append(self.runner_list[b])
            a.remove(b)
        selected.sort(key = lambda x : x.score,reverse=True)
        r = Individual(dna_size,cst_genome)
        r.crossover(selected[0],selected[1])
        r.mutate()
        return r

#initiate population
grids = []
big_grid = Grid(grid_width,big_grid_length)
for i in range(number_grids):
    grids += [Grid(grid_width,grid_length)]
pop = Population(pop_size,grids)

def display_result(grid,i,pos):
    pos_player = int(grid_display/2)
    Obs.record(('player', (pos_player*block_size,(pos+1)*block_size, 3, block_size, 'shape=monstre2.png')), Window='Field')
    for j in range(grid_display):
        for k in range(grid.width):
            if j+i-pos_player >= grid.length-turns_predict or j+i-pos_player < 0:
                Obs.record(('obstacle_'+str(j)+'_'+str(k), (j*block_size,(k+1)*block_size, 1, block_size, 'shape=brick.png')), Window='Field')
            elif j == pos_player and k == pos:
                Obs.record(('obstacle_'+str(j)+'_'+str(k), (j*block_size,(k+1)*block_size, -1, block_size, 'shape=rectangle')), Window='Field')
            elif grid.cells[j+i-pos_player][k] == 1:
                Obs.record(('obstacle_'+str(j)+'_'+str(k), (j*block_size,(k+1)*block_size, 1, block_size, 'shape=brick.png')), Window='Field')
            else:
                Obs.record(('obstacle_'+str(j)+'_'+str(k), (j*block_size,(k+1)*block_size, 2, block_size, 'shape=rectangle')), Window='Field')
        

pos_in_solution = 0
solution_pos = []

def one_generation():
    global pos_in_solution
    global generation
    global solution_pos
    global big_grid
    global grid_width
    global grid_length
    if pos_in_solution == 0:
        print("Score : %d" % pop.runner_list[0].score)
        grids[0] = Grid(grid_width,grid_length)
        for i in range(10):
            pop.evolve(generation)
            generation = generation + 1
        (pos_in_solution,solution_pos) = pop.runner_list[0].make_score_one_grid(grids[0])
        return True
    display_result(grids[0],pop.runner_list[0].score - pos_in_solution,solution_pos[pop.runner_list[0].score - pos_in_solution])
    pos_in_solution -= 1
    Obs.StepId += 1
    time.sleep(0.1)
    return True

def Start():
    generation = 0
    pos_in_solution = 0
    Obs.setOutputDir('___Results')    # curves, average values and screenshots will be stored there
    Obs.recordInfo('Background', 'white')    # windows will have this background by default

    Obs.recordInfo('DefaultViews',    [('Field',window_width,window_height)])    # Evolife should start with these windows open
    Obs.record(('point', (window_width,window_height, 2, 1, 'shape=rectangle')), Window='Field')

    EW.Start(
        one_generation, 
        Obs, 
        Capabilities='FG'
    )
Start() 
