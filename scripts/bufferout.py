#!/usr/bin/env python

import sys, subprocess

p=subprocess.Popen(sys.argv[1:], stdout=subprocess.PIPE, close_fds=True, bufsize=-1)

exit=p.wait()

if exit != 0:
	print p.stdout.read(),
