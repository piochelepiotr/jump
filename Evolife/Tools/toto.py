#!/usr/bin/env python
import Tools

L = []
for x in range(1000):
	# L.append((x/1000.0, Tools.Polygon(x/1000.0, Points=((0.3,0.7),(0.5,0.1), (0.7,0.9)))))
	L.append((x/10.0, Tools.decrease(x/10.0, 100, 40)))
	
f = open('i:toto.csv', 'w')
f.write('x;y\n')
for p in L:
	f.write('%.03f;%.03f\n' % p)
f.close()
