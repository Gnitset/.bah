#!/usr/bin/env python

from sys import argv

for ip in argv[1:]:
	groups=ip.split(":")
	missing0=8-len(groups)
	ipv6=[]

	for group in groups:
		if len(group) == 0:
			group="0000"+"0000"*missing0
		ipv6=ipv6+[Z for Z in group.zfill(4)]

	ipv6.reverse()

	print "%s.ip6.arpa"%(".".join(ipv6))
