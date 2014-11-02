from bitarray import bitarray
from random import random
from copy import copy
from math import sqrt
import logging as log

from .. import config as Const

class Node(object):
	
	# Initialization
	def __init__(self, node_id, num_nodes, radio_ranges):

		# Basic
		self.id = node_id
		self.pos_x, self.pos_y = random(), random()
		self.num_nodes = num_nodes
		self.data = int(random() * Const.NODE_DATA_MAX)
		
		# Multi-radio
		self.radios = []
		self.install_radio(radio_ranges)

		self.reset()

		# Clustering
		self.parent = self
		self.children = []

	def install_radio(self, radio_ranges):
		for radio_type in radio_ranges:
			radio = Radio(radio_type, radio_ranges[radio_type], self)
			self.radios.append(radio)

	# Re-initialization
	def reset(self):
		
		# Basic
		self.array = bitarray('0' * self.id + '1' + '0' * (self.num_nodes-self.id-1))
		
		self.sleep_flag = True
		self.sleep_cnt = 0
		
		self.complete_flag = False
		self.complete_cnt = 0

		# Multi-radio
		for radio in self.radios:
			radio.reset()

		# Clustering
		self.order = 0
	
	# Set the position of the node
	def set_pos(self, pos):
		self.pos_x, self.pos_y = pos
		
	def get_completeness(self):
		return float(self.array.count(1)) / float(self.num_nodes)

	# Calculate Euclidean Distance
	def __sub__(self, other):
		delta_x, delta_y = self.pos_x - other.pos_x, self.pos_y - other.pos_y
		return sqrt(pow(delta_x, 2) + pow(delta_y, 2))

	# Transmit Messages
	def dispatch(self, radio_type=Const.RADIO_ALL):

		if self.complete_flag | self.sleep_flag:
			self.sleep()
		else:
			pkt = self.compose_pkt()
			log.debug("node %d radio %d sending", self.id, radio_type)
			if radio_type == Const.RADIO_ALL:
				# Broadcast on all radios
				for radio in self.radios:
					radio.broadcast(pkt)
			else:
				self.radios[radio_type].broadcast(pkt)

	# Process received messages     
	def process(self, radio_type=Const.RADIO_ALL):

		default_pkt = self.compose_pkt()
		pkt_recv = None

		if radio_type == Const.RADIO_ALL:
			pkt_recv = []
			for radio in self.radios:
				pkt = radio.extract(default_pkt)
				if self.array | pkt['flag'] != self.array:
					pkt_recv.append(pkt)
		else:
			radio = self.radios[radio_type]
			pkt = radio.extract(default_pkt)
			if self.array | pkt['flag'] != self.array:
				pkt_recv = pkt

		if pkt_recv != None and len(pkt_recv) != 0:
			if type(pkt_recv) == list:
				# Multiple packets
				log.debug("node %d received %d packets", self.id, len(pkt_recv))
				for pkt in pkt_recv:
					self.merge(pkt)
			elif type(pkt_recv) == dict:
				log.debug("node %d received 1 packets", self.id)
				# Single packets
				self.merge(pkt_recv)
			self.sleep_flag = False
		else:
			log.debug("node %d received no packets", self.id)
			# No new packets
			self.sleep()

		self.check_complete()

	# Merge Operator
	def merge(self, pkt):

		self.array |= pkt['flag']
		if self.data < pkt['payload']:
			self.data = pkt['payload']

	def sleep(self):

		if not self.sleep_flag or self.complete_flag:
			self.sleep_flag = True
			self.sleep_cnt = 0
		else:
			self.sleep_cnt += 1
			if self.sleep_cnt > Const.ALGORITHM_TIMEOUT_THRESHOLD:
				# Random timeout
				thres = self.sleep_cnt - Const.ALGORITHM_TIMEOUT_THRESHOLD
				if random() * Const.ALGORITHM_TIMEOUT_THRESHOLD < thres:
					self.sleep_flag = False
					self.sleep_cnt = 0
				# Little tweak to increase reliability in multi radio mode
				if len(self.children) != 0:
					self.sleep_flag = False
					self.sleep_cnt = 0
	
	def check_complete(self):

		if self.array == bitarray('1' * Const.NETWORK_NUM_NODE):
			self.complete_cnt += 1
			if self.complete_cnt > Const.ALGORITHM_MAX_COMPLETION:
				self.complete_flag = True
		else:
			self.complete_cnt = 0

	def compose_pkt(self):
		pkt = {							\
			'node':self,				\
			'payload':copy(self.data),	\
			'flag':copy(self.array),	\
		}
		return pkt


class Radio(object):

	# Initialization
	def __init__(self, type, radio_range, node):
		self.radio_type = type
		self.radio_range = radio_range
		self.state = Const.RADIO_ON
		self.node = node
		self.adj = []
		self.buffer = []

	# Re-initialization
	def reset(self):
		self.state = Const.RADIO_ON
		self.adj[:] = []
		self.buffer[:] = []

	# Find adjacent nodes
	def discover(self, node_list):
		self.adj[:] = []
		for node in node_list:
			if self.node - node < self.radio_range and self.node != node:
				self.adj.append(node)

	# Broadcast Packet
	def broadcast(self, pkt):
		for node in self.adj:
			self.transmit(node, pkt)

	# Send Packet
	def transmit(self, dest, pkt):
		dest_radio = dest.radios[self.radio_type]
		dest_radio.receive(pkt)

	# Receive Packet
	def receive(self, pkt):
		if self.state != Const.RADIO_OFF:
			self.buffer.append(pkt)

	# Message Extraction
	def extract(self, default_pkt):
		
		self.buffer.sort(key = lambda x: self.node - x['node'])

		if len(self.buffer) > 1:
			if self.buffer[1]['node'] - \
				self.buffer[0]['node'] < Const.NETWORK_MIN_RANGE:
				# No Packet decoded due to interference
				pkt_recv = default_pkt
			else:
				pkt_recv = self.buffer[0]
		elif len(self.buffer) == 1:
			pkt_recv = self.buffer[0]
		else:
			# No packet received = received its own message
			pkt_recv = default_pkt

		self.buffer[:] = []
			
		return pkt_recv
