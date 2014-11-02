#!/usr/bin/env python

from chaos.network.chaos_network import Network
from math import sqrt

#test 1

for nn in range(1, 6):
	n = int(pow(2, 2*nn))
	num=0
	my_n = Network(n, 99, 99)
	for i in range(20):
		my_n.reset()
		converged, num_round = my_n.simulate_simple(200)
		#print str(converged) + "\t" +str(num_round)
		if converged:
			num+=1
	print str(num) +"\t" + str(n)


'''
n = 64
my_n = Network(n, 999, 999)
converged, num_round = my_n.simulate_simple(500)
print str(converged) + "\t" +str(num_round)
'''

#test 2
'''
for nn in range(3, 13):
	n = int(pow(2, nn))
	r = (128.0 * 1.5 / int(sqrt(n)))
	my_n = Network(n, r)
	converged, num_round = my_n.simulate_simple(500)
	print str(n) + "\t" + str(converged) + "\t" +str(num_round)
'''
#test

'''
for nn in range(1, 7):
	n = int(pow(2, 2 * nn))
	r = (128.0 * 2.5 / int(sqrt(n)))
	for cc in range(1, 6):
		c = int(pow(2, 2*cc))
		if c > n / 4:
			continue
		r2 = sqrt(c) * r * 4
		my_n = Network(n, r, r2)
		my_n.cluster(c)
		converged, num_round = my_n.simulate_multi_seq(1200)
		print str(n) + "\t" + str(c) +"\t" + str(converged) + "\t" +str(num_round)
'''

'''
for nn in range(1, 7):
	n = int(pow(2, 2 * nn))
	for cc in range(1, 6):
		c = int(pow(2, 2*cc))
		if c > n / 4:
			continue
		my_n = Network(n, 0, 0)
		my_n.cluster(c)
		converged, num_round = my_n.simulate_seq(1000)
		print str(n) + "\t" + str(c) +"\t" + str(converged) + "\t" +str(num_round)
'''
