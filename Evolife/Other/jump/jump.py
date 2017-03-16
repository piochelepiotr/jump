import numpy as np

#creates a neural network

W1 = np.random.normal(size=(2,5))
W2 = np.random.normal((5,2))

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
        weight = 0
        for i in x:
            if i:
                weight += 2**i
        weight_list.append(weight)
    return weight_list

def binToInt(bin_list):
    sumInt = sum([x*(2**i) for (i,x) in enumerate(bin_list)])
    n = len(bin_list)
    return sumInt - bin_list[n-1] * (2**n)

print(binToInt([1,0,0,0,1,0]))

display_matrix(W1)
