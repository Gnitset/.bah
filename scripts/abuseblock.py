#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#
# Last Update: 2011-02-07
# Mission: Block abusing ips in iptables

import os
import sys
import time

d=dict()		# a dictionary with ipadresses and number of rows in the file
blocked=set()		# set of adresses blocked
f=open(sys.argv[1])	# file to read (sys.argv[1] is the first argument)
norowstoblock=1000	# block ip after this many accesses

blocked.add("127.0.0.1") # add addresses that should not ever be blocked

class IptablesException(Exception):
	pass

def iptables(*args):
	if os.spawnv(os.P_WAIT, '/sbin/iptables', ('iptables',)+args)!=0:
		raise IptablesException()

def block(ip):
	if ip in blocked:
		return
	blocked.add(ip)
#	print "blocked", ip
	iptables("-A", "INPUT", "-s", ip, "-j", "DROP")

def gettime_line(line,now):
	ip, b1, b2, timestamp, rest=line.split(" ", 4)
	try:
		unixtime=int(time.mktime(time.strptime(timestamp[1:], "%d/%b/%Y:%H:%M:%S")))
	except:
		unixtime=now

	return ip, unixtime

def gettime_now(line, now):
	ip, rest=line.split(" ", 1)
	return ip, now

gettime=gettime_line

while True:
#	print "loop"
	line=f.readline()
	if not line:
		time.sleep(1)
		f.seek(f.tell())
#		print "eof"
		continue

	now=int(time.time())
	removetime=now-(60*60)
	ip, unixtime=gettime(line, now)
	if ip in blocked:
#		print "already blocked"
		continue
	if removetime > unixtime:
#		print "too old"
		continue
	if gettime == gettime_line and (unixtime+300)>now:
		gettime=gettime_now
#		print "switch parser"
	if "/games/handhistory" not in line:
#		print "not handhistory"
		continue

	ip_d=d.get(ip, dict())	
#	print ip_d
	ip_d[unixtime]=ip_d.get(unixtime, 0)+1
#	print ip_d
	d[ip]=ip_d

	nr_access=0
	for timestamp, value in ip_d.items():
#		print timestamp, value
		if timestamp < removetime:
			del ip_d[timestamp]
		else:
			nr_access=nr_access+value

#	print nr_access
	if nr_access > norowstoblock:
		block(ip)
