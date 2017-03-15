# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 15:38:00 2017

@author: antoi
"""

import numpy as np
import random
import math


######
# Actions : 
#    0 : duck, 1 : do nothing 2 : jump

# constants
grid_length = 50
grid_width = 3
turns_predict = 3
n_inputs = grid_width*turns_predict + 1
n_outputs = 3
n_hidden = 15
first_pow = 5

gene_size = 10
dna_size = gene_size * (n_inputs + n_outputs )*n_hidden
mutation_rate = 0.03
crossover_ratio = 0.5
cst_genome = list(range(0,dna_size+1,gene_size))
number_crossover = 24


class Grid:
    def __init__(self, grid_width,grid_length):
        self.width = grid_width
        self.length = grid_length
        cells = np.random.randint(0, 2, size = (grid_length, grid_width))
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
    print()

def print_dna(dna):
    for i in range(150):
        print(dna[i],end='')
    print()

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
        if np.random.randint(0,1):    # starting indifferently from mother or father
            parent1, parent2 = parent2, parent1     # swapping parents
        self.DNA = []
        for cut_point in range(len(Loci_crossover)-1):
            self.DNA += list(parent1[Loci_crossover[cut_point]:Loci_crossover[cut_point+1]])
            parent1, parent2 = parent2, parent1     # swapping parents        
            
    def make_score(self,grid):
        i = 0
        pos = int(grid.width/2)
        go_on = True
        (W1,W2) = genome_to_weights(self.DNA,self.genome)
        arg = grid.cells[i]
        for j in range(turns_predict-1):
            arg = np.concatenate([arg,grid.cells[j]])
        while(go_on):
            arg = np.concatenate([arg[grid.width:],grid.cells[i+turns_predict]])
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
        
class Population:
    
    runner_list = []
  
    def __init__(self, pop_size,grid):
        self.pop_size = pop_size
        for i in range(pop_size):
            r = Individual(dna_size, cst_genome)
            r.generate_random()
            self.runner_list.append(r)
            self.grid = grid
        for i in self.runner_list:
            i.make_score(grid)
        self.runner_list.sort(key = lambda x : x.score,reverse=True)
        print_dna(self.runner_list[0].DNA.tolist())

    def evolve(self):
        new_pop = []
        print("the best is : %d" % self.runner_list[0].score)
        for i in range(self.pop_size):
            #new_pop.append(self.tournament(10))
            new_pop.append(self.bests())
        for i in new_pop:
            i.make_score(grid)
        new_pop.sort(key = lambda x : x.score,reverse=True)
        print_dna_diff(new_pop[0].DNA,self.runner_list[0].DNA)
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

grid = Grid(grid_width,grid_length)
pop = Population(100,grid)
for i in range(50):
    pop.evolve()
grid.display()
        

