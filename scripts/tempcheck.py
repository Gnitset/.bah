#! /usr/bin/env python

import socket
import re
import sys

exit_code=0
r=re.compile("(/dev/sd[a-z])\|[^\|]*\|([0-9]*)\|C")
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect(("127.0.0.1", 7634))
tempdata=s.recv(8192)

for disk,temp in r.findall(tempdata):
	if int(temp) > 44:
		sys.stderr.write(disk+": "+temp+"\n")
		exit_code=1

sys.exit(exit_code)
