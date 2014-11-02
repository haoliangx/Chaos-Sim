from ..node.node import Node
from layout.grid import GridLayout
from random import randrange, choice, shuffle
from math import sqrt
from itertools import product
from bitarray import bitarray

from .. import config as Const
import logging as log

import networkx as nx
import matplotlib.pyplot as plt

class Network(object):

	def __init__(self, num_nodes, radio, radio2, layout=GridLayout):

		self.node_list = []
		self.cluster_heads = []
		self.num_nodes = num_nodes
		self.den = int(sqrt(self.num_nodes))

		my_radio = {0: radio, 1: radio2}

		for i in range(num_nodes):
			self.node_list.append(				\
				Node(							\
					i, 							\
					self.num_nodes, 			\
					Const.DEFAULT_RADIO,		\
					#my_radio,					\
					)
				)

		layout.generate(						\
			self.node_list, 					\
			Const.LAYOUT_WIDTH,					\
			Const.LAYOUT_HEIGHT,				\
			Const.LAYOUT_PERTURB,				\
			)

	def reset(self):
		for node in self.node_list:
			node.reset()

	def is_connect(self):
		pass

	def draw_graph(self):
		graphs = self.to_graph()
		pos = {}
		for node in self.node_list:
			pos[node.id] = (node.pos_x, node.pos_y)
		nx.draw_networkx_nodes(graphs[0], pos)
		for r_type in graphs:
			G = graphs[r_type]
			nx.draw_networkx_edges(G, pos, edgelist=G.edges(), edge_color=Const.UI_EDGE_COLOR[r_type])
		nx.draw_networkx_labels(G, pos)
		plt.ion()
		plt.show()

	def to_graph(self):

		#TODO
		# temporary
		for ch in self.cluster_heads:
			ch.radios[1].discover(self.cluster_heads)
			for node in ch.children:
				node.radios[0].discover(ch.children)
				node.radios[0].adj.append(ch)
				
		graphs = {}
		for radio_type in Const.DEFAULT_RADIO:
			G = nx.Graph()
			for node in self.node_list:
				G.add_node(node.id)
				#node.radios[radio_type].discover(self.node_list)
			for node in self.node_list:
				for peer in node.radios[radio_type].adj:
					G.add_edge(node.id, peer.id, weight = node - peer)
			graphs[radio_type] = G.to_undirected()
		return graphs

	def cluster(self, cluster_size=16):

		self.cluster_heads[:] = []

		step = int(sqrt(cluster_size))
		n_r = range(0, self.den, step)

		node = lambda x, y: self.node_list[self.den * x + y]
		rand_head = lambda x, y: node(x + randrange(step), y + randrange(step))
		
		for x, y in product(n_r, n_r):
			head = rand_head(x, y)
			head.parent = head
			head.children[:] = []
			self.cluster_heads.append(head)
			for m, n in product(range(step), range(step)):
				if node(x + m, y + n) != head:
					node(x + m, y + n).parent = head
					head.children.append(node(x + m, y + n))

	def check_complete(self, node_list, op=bitarray.__and__):
		tmp = bitarray(node_list[0].array)
		for node in node_list:
			tmp = op(tmp, node.array)
		if tmp.all():
			return True
		else:
			return False
			
	def get_completeness(self, node_list):
		completeness = 0.0
		array = []
		for node in node_list:
			completeness += node.get_completeness()
			array.append(node.get_completeness())
		return completeness / len(node_list), array

	def simulate_chaos(self, node_list, radio, max_round):

		num_round = 0
		converged = False

		choice(node_list).sleep_flag = False

		while not converged:
			for node in node_list:
				node.dispatch(radio)
			for node in node_list:
				node.process(radio)
			converged = self.check_complete(node_list)
			completeness, array = self.get_completeness(node_list)
			log.info("Round # \t%d\t Avrg: \t%f", num_round, completeness)
			num_round += 1
			if num_round > max_round:
				break

		return converged, num_round

	def simulate_simple(self, max_round):

		for node in self.node_list:
			node.radios[0].discover(self.node_list)
			
		return self.simulate_chaos(self.node_list, 0, max_round)

	def simulate_multi(self, max_round):
		
		# Initialization
		for ch in self.cluster_heads:
			# Multi-radio on cluster head
			ch.radios[1].discover(self.cluster_heads)
			ch.radios[0].discover(ch.children)
			for node in ch.children:
				node.radios[0].discover(ch.children)
				node.radios[0].adj.append(ch)

		return self.simulate_chaos(self.node_list, Const.RADIO_ALL, max_round)

	def simulate_seq(self, max_round):

		num_round = 0

		# Initialization
		for ch in self.cluster_heads:
			order = range(0, len(ch.children))
			shuffle(order)
			for node in ch.children:
				node.order = order.pop()
		for ch in self.cluster_heads:
			ch.radios[1].discover(self.cluster_heads)

		# Phase one
		phase_one = False
		while not phase_one:
			for node in self.node_list:
				if node.parent != node and node.order == num_round:
					node.radios[0].transmit(node.parent, node.compose_pkt())
			for ch in self.cluster_heads:
				ch.process()
			phase_one = self.check_complete(self.cluster_heads, bitarray.__or__)
			num_round += 1

		# Phase two
		phase_two, sim_round = self.simulate_chaos(self.cluster_heads, 1, max_round)
		if phase_two:
			num_round += sim_round

		# Phase three
		for ch in self.cluster_heads:
			ch.radios[0].adj = ch.children
			ch.radios[0].broadcast(ch.compose_pkt())

		for node in self.node_list:
			node.process(0)

		num_round += 1
		phase_three = self.check_complete(self.node_list)

		return phase_one & phase_two & phase_three, num_round

	def simulate_multi_seq(self, max_round):

		num_round = 0

		# Initialization
		for ch in self.cluster_heads:
			order = range(0, len(ch.children))
			shuffle(order)
			for node in ch.children:
				node.order = order.pop()

		for ch in self.cluster_heads:
			ch.radios[1].discover(self.cluster_heads)

		converged = False
		while not converged:
			for node in self.node_list:
				if node.parent != node and node.order == num_round:
					node.radios[0].transmit(node.parent, node.compose_pkt())
					node.parent.sleep_flag = False

			for ch in self.cluster_heads:
				ch.dispatch(1)

			for ch in self.cluster_heads:
				ch.process()

			converged = self.check_complete(self.cluster_heads)
			completeness, array = self.get_completeness(self.cluster_heads)
			log.info("Round # \t%d\t Avrg: \t%f", num_round, completeness)
			num_round += 1
			if num_round > max_round:
				break

		for ch in self.cluster_heads:
			ch.radios[0].adj = ch.children
			ch.radios[0].broadcast(ch.compose_pkt())

		for node in self.node_list:
			node.process(0)

		return converged, num_round+1