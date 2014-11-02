#!/usr/bin/env python

from chaos.network.chaos_network import Network

all_mode = ["simple", "seq", "multi"]
max_round = 1000
mode = 0


my_n = Network(256)
my_n.cluster(16)
my_n.draw_graph()

converged, num_round = getattr(my_n, 		\
	"simulate_" + all_mode[mode])(max_round)
#my_n.reset()

if converged:
	print all_mode[mode] + " - Converged in " + str(num_round)
else:
	print all_mode[mode] + " - Not converged"

raw_input("")
