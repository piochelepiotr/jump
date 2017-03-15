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
n_inputs = 1
n_outputs = 3
n_hidden = 5
path = "012121012101200120001212002010102010200100200102001000012121020001021020120102"
first_pow = 5

gene_size = 10
dna_size = gene_size * (n_inputs + n_outputs )*n_hidden
mutation_rate = 0.05
crossover_ratio = 0.5
cst_genome = list(range(0,dna_size+1,gene_size))
number_crossover = 1




def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def matrix_sigmoid(M):
    (w,h) = M.shape
    Mp = np.zeros(shape=(w,h))
    for i in range(w):
        for j in range(h):
            Mp[i][j] = sigmoid(M[i][j])
    return Mp
  
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
            
    def make_score(self):
        i = 0
        go_on = True
        (W1,W2) = genome_to_weights(self.DNA,self.genome)
        arg = np.zeros(shape=(1,1))
        while(go_on):
            arg[0][0] = int(path[i])
            action = predict(arg, W1, W2)
            if(not(action == int(path[i]) or int(path[i]) == 1)):
                go_on = False
            else:
                i+=1
                if i == len(path):
                    go_on = False
        self.score = i
        
class Population:
    
    runner_list = []
  
    def __init__(self, pop_size):
        self.pop_size = pop_size
        for i in range(pop_size):
            r = Individual(dna_size, cst_genome)
            r.generate_random()
            self.runner_list.append(r)

    def evolve(self):
        new_pop = []
        for i in self.runner_list:
            i.make_score()
        self.runner_list.sort(key = lambda x : x.score,reverse=True)
        print("the best is : %d" % self.runner_list[0].score)
        for i in range(self.pop_size):
            new_pop.append(self.tournament(10))
        self.runner_list = new_pop
    
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

pop = Population(10)
for i in range(100):
    pop.evolve()

        

