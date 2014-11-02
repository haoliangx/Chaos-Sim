from .... import config as Const
from random import random

class RandomLayout(object):

	num_node = 0
	width = 0
	height = 0

	@classmethod
	def set_parameter(cls, num_node, width, height):
		cls.num_node = num_node
		cls.width = width
		cls.height = height

	@classmethod
	def generate_node(cls, node_id):
		pos_x = int(random() * cls.width)
		pos_y = int(random() * cls.height)
		return pos_x, pos_y

	@classmethod
	def generate_network(cls, node_list):
		for node in node_list:
			node.set_pos(cls.generate_node(node.id))

	@classmethod
	def generate(cls, node_list, width, height):
		cls.set_parameter(len(node_list), width, height)
		cls.generate_network(node_list)