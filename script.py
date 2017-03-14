# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 15:38:00 2017

@author: antoi
"""

import numpy as np
import math


######
# Actions : 
#    0 : duck, 1 : do nothing 2 : jump

# constants
n_inputs = 1
n_outputs = 3
n_hidden = 5
path = "01212101210120"

gene_size = 10
dna_size = gene_size * (n_inputs + n_outputs )*n_hidden
mutation_rate = 0.05
crossover_ratio = 0.5
cst_genome = list(range(0,dna_size,gene_size))
number_crossover = 1

#creates a neural network
W1 = np.random.normal(size=(n_inputs, n_hidden))
W2 = np.random.normal(size = (n_hidden,n_outputs))



def sigmoid(x):
  return 1 / (1 + math.exp(-x))
  
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


def predict(arg, W1, W2):
    intermediate = np.fromiter(map(sigmoid, np.dot(arg,W1)), dtype = float)
    print(intermediate)
    for x in map(sigmoid,np.dot(intermediate,W2)):
        print(x)
    return np.argmax(np.fromiter(map(sigmoid,np.dot(intermediate,W2)), dtype = float))

    
# a modifier pour négatifs à virgule 
def binToInt(bin_list):
    sumInt = sum([x*(2**i) for (i,x) in enumerate(bin_list)])
    n = len(bin_list)
    return sumInt - bin_list[n-1] * (2**n)


class Individual:
    def __init__(self, entity_id, dna_size, genome):
        self.entity_id = entity_id
        self.dna_size = dna_size
        self.genome = genome
    
    def generate_random(self):
        self.DNA = np.random.randint(2,size = self.dna_size)
        
    def mutate(self):
        for i in range(len(self.DNA)):
            rand_int = np.random.rand_sample(1)[0]
            if(rand_int < mutation_rate):
                self.DNA[i] = np.random.randint(2)
                
    def crossover(self,mother, father):
        #   computing random crossover points
        Loci_crossover = np.random.sample(range(1,self.dna_size), number_crossover)
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

        
class Population:
    
    runner_list = []
  
    def __init__(self, pop_size):
        self.pop_size = pop_size
        for i in range(pop_size):
            r = Individual(i,dna_size, cst_genome)
            r.generate_random()
            self.runner_list.append(r)
        
    
        
def genome_to_weights(genome):
    return 0
    
    
def score(individual):
    i = 0
    go_on = True
    while(go_on):
        action = predict(int(path[i]), W1, W2)
        if(not(action == path[i] or path[i] == 1)):
            go_on = False
        else:
            i+=1
    return i