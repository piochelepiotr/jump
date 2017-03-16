#!/usr/bin/env python
# life.py simulates John Conway's Game of Life with random initial states
# -----------------------------------------------------------------------------
import sys, random, pygame
from pygame.locals import *
# -----------------------------------------------------------------------------
# GLOBALS
# The title and version of this program
title, version = "The Game of Life", "1.0"

# The dimensions of each cell (in pixels)
cell_dimensions = (5,5)

# The framerate of the game (in milliseconds)
framerate = 1000

# The fraction of the board occupied by cells when randomly generated
occupancy = 0.33

# Colors used to represent the cells
colors = { 0:(0,0,0), 1:(200,0,0), 2:(0,200,0), 3:(0,0,200) }

# -----------------------------------------------------------------------------
# FUNCTIONS
# Main function
def main(args):

	# Get the board dimensions (in cells, not pixels) from command-line input
	if len(args) != 3: sys.exit("USAGE: life.py X_CELLS Y_CELLS")
	board_dimensions = (int(args[1]),int(args[2]))

	# Initialize pygame elements
	screen, bg, clock = init(board_dimensions)

	# Initialize random board
	board, next_board = make_random_board(board_dimensions)

	# Enter the game loop
	quit_game = False
	wave_count = 0
	while not quit_game:

		# Slow things down to match the framerate
		clock.tick(framerate)

		# Update the board
		etat_cell0 = update_board(board, next_board)
		
		if(etat_cell0): #etat_cell0 = 1 si la cellule n'a pas change
			wave_count += 1
		else :
			print "Steps since last change :", wave_count
			wave_count = 0

		# Draw the board on the background
		draw_board(board, bg)

		# Blit bg to the screen, flip display buffers
		screen.blit(bg, (0,0))
		pygame.display.flip()

		# Queue user input to catch QUIT signals
		for e in pygame.event.get():
			if e.type == QUIT: quit_game = True

	# Print farewell message
	print "Thanks for watching!"

# Initialize pygame elements
def init(board_dimensions):

	# Grab hard-coded global values
	global title, version, cell_dimensions

	# Initialize the pygame modules
	pygame.init()

	# Determine and set the screen dimensions
	dimensions = (board_dimensions[0]*cell_dimensions[0],
				  board_dimensions[1]*cell_dimensions[1])
	screen = pygame.display.set_mode(dimensions)

	# Set the title string of the root window
	pygame.display.set_caption(title+" "+version)

	# Grab the background surface of the screen
	bg = screen.convert()

	# Grab the game clock
	clock = pygame.time.Clock()

	# Return the screen, the background surface, and the game clock
	return screen, bg, clock

# Create a "seed" board of given dimensions at random
def make_random_board(board_dimensions):

	# Grab hard-coded global values
	global occupancy
	occ_div = 1
	# Instantiate the board as a dictionary with a fraction occupied
	# 0 indicates an empty cell; 1 indicates an occupied cell
	board = dict()
	for x in range(board_dimensions[0]):
		for y in range(board_dimensions[1]):
			nb_hasard = random.random()
			if nb_hasard < (occupancy /occ_div) : board[(x,y)] = 1
			elif nb_hasard < (2*occupancy/occ_div) : board[(x,y)] = 2
			elif nb_hasard < (3*occupancy/occ_div) : board[(x,y)] = 3
			else: board[(x,y)] = 0
	next_board = dict()
	for x in range(board_dimensions[0]):
		for y in range(board_dimensions[1]):
			next_board[(x,y)] = board[(x,y)]

	# Return the board
	return board, next_board

# Update the board according to the rules of the game
def update_board(board, next_board):

	nb_sup = 2
	# For every cell in the board...
	for cell in board:

		# How many occupied neighbors does this cell have?
		score_type1, score_type2, score_type3 = count_neighbors(cell, board)
		# If the cell is empty and has 3 neighbors, mark it for occupation
		if board[cell] == 1:
			if score_type3 > nb_sup :
				next_board[cell] = 3
		elif board[cell] == 2:
			if score_type1 > nb_sup :
				next_board[cell] = 1
		elif board[cell] == 3:
			if score_type2 > nb_sup :
				next_board[cell] = 2
		else :
			max_score = max(score_type1, score_type2, score_type3)
			if max_score > 5 :
				if max_score == score_type1 :
					next_board[cell] = 1
				if max_score == score_type2 :
					next_board[cell] = 2
				if max_score == score_type3 :
					next_board[cell] = 3


	# Now, go through it again, making all the approved changes
	etat_cell0 = (board[(0,0)] == next_board[(0,0)])
	
	for cell in board:
		board[cell] = next_board[cell]
	return etat_cell0

# Return the number of occupied neighbors this cell has
def count_neighbors(cell, board):

	# Figure out the potential neighboring cells (need to watch the edges)
	neighbors = [ (cell[0]-1,cell[1]), (cell[0]-1,cell[1]-1),
				  (cell[0],cell[1]-1), (cell[0]+1,cell[1]-1),
				  (cell[0]+1,cell[1]), (cell[0]+1,cell[1]+1),
				  (cell[0],cell[1]+1), (cell[0]-1,cell[1]+1) ]

	# For each potential neighbor, if the cell is occupied add one to the score
	score_type1 = 0
	score_type2 = 0
	score_type3 = 0
	for neighbor in neighbors:

		# Is this a real neighbor, or is it out-of-bounds?
		if neighbor in board.keys():
			# Remember that neighbors which are marked for death count, too!
			if board[neighbor] == 1: score_type1 += 1
			if board[neighbor] == 2: score_type2 += 1
			if board[neighbor] == 3: score_type3 += 1
	# Return the score
	return score_type1, score_type2, score_type3

# Draw the board on the background
def draw_board(board, bg):

	# Grab hard-coded global values
	global cell_dimensions

	# Draw every cell in the board as a rectangle on the screen
	for cell in board:
		rectangle = (cell[0]*cell_dimensions[0],cell[1]*cell_dimensions[1],
					 cell_dimensions[0],cell_dimensions[1])
		pygame.draw.rect(bg, colors[board[cell]], rectangle)

# -----------------------------------------------------------------------------
# The following code is executed upon command-line invocation
if __name__ == "__main__": main(sys.argv)

# -----------------------------------------------------------------------------
# EOF


__author__ = 'Dessalles'
