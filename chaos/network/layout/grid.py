from math import sqrt, floor
from random import random
import networkx as nx

class GridLayout(object):

	num_node = 0
	width = 0
	height = 0

	den = 0
	x_step = 0
	y_step = 0

	perturb = 0

	@classmethod
	def set_parameter(cls, num_node, width, height, perturb):
		cls.num_node = num_node
		cls.width = width
		cls.height = height

		cls.den = int(sqrt(cls.num_node))
		cls.x_step = cls.width / cls.den
		cls.y_step = cls.height / cls.den

		cls.perturb = perturb

	@classmethod
	def generate_node(cls, node_id):
		pos_x = int(node_id / cls.den) * cls.x_step + (random() - 1) * cls.perturb * cls.x_step
		pos_y = int(node_id % cls.den) * cls.y_step + (random() - 1) * cls.perturb * cls.x_step
		return pos_x, pos_y

	@classmethod
	def generate_network(cls, node_list):
		for node in node_list:
			node.set_pos(cls.generate_node(node.id))

	@classmethod
	def generate(cls, node_list, width, height, perturb=0):
		cls.set_parameter(			\
			len(node_list), 		\
			width, 					\
			height, 				\
			perturb,				\
			)
		cls.generate_network(node_list)