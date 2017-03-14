# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 15:38:00 2017

@author: antoi
"""

import numpy as np

#creates a neural network

n_inputs = 3
n_outputs = 2
n_hidden = 3
W1 = np.random.normal(size=(n_inputs, n_hidden))
W2 = np.random.normal((n_hidden,n_outputs))

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

def predict(arg):
    return np.dot(arg,np.dot(W1,W2))

def get_weights_from_genome(genome, gene_size):
    n_gene = len(genome)/gene_size
    gene_list = []
    for i in range(n_gene):
        gene_list.append(genome[i*gene_size: (i+1)*gene_size])
    weight_list = []
    for x in gene_list:
        weight = binToInt(x)
        weight_list.append(weight)
    return weight_list

def binToInt(bin_list):
    sumInt = sum([x*(2**i) for (i,x) in enumerate(bin_list)])
    n = len(bin_list)
    return sumInt - bin_list[n-1] * (2**n)

print(binToInt([1,0,0,0,1,0]))
display_matrix(W1)

class Runner:
  def __init__(self, entity_id):
    	self.entity_id = entity_id
      
  def fill_DNA(DNA):
    self.DNA = DNA
    
    
class Population:
  runner_list = []
  def __init__(self, pop_size):
    self.pop_size = pop_size
    for i in range(pop_size):
		r = Runner(i)
      	#r.fill_DNA(np.random.randint(2,size = ))
      	self.runner_list.append(r)
        
        
def genome_to_weights(genome):
  return weights