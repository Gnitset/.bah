#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import bcrypt
import anydbm
from struct import *

#	 That script is supposed to do theses actions, in an infinite loop:
#	 
#	 read from stdin: AABBBBBBBBB.....
#	   A: 2 bytes of length data (a short in network byte order)
#	   B: a string of length found in A that contains operation in plain text operation are as follows:
#		 auth:User:Server:Password (check if a username/password pair is correct)
#		 isuser:User:Server (check if it’s a valid user)
#		 setpass:User:Server:Password (set user’s password)
#		 tryregister:User:Server:Password (try to register an account)
#		 removeuser:User:Server (remove this account)
#		 removeuser3:User:Server:Password (remove this account if the password is correct)
#	 write to stdout: AABB
#	   A: the number 2 (coded as a short, which is bytes length of following result)
#	   B: the result code (coded as a short), should be 1 for success/valid, or 0 for failure/invalid
#	 Example python script

db=anydbm.open("/tmp/ejabberd.pwdb", "c")

def from_ejabberd():
	input_length = sys.stdin.read(2)
	(size,) = unpack('>h', input_length)
	return sys.stdin.read(size).split(':')

def to_ejabberd(bool):
	answer = 0
	if bool:
		answer = 1
	token = pack('>hh', 2, answer)
	sys.stdout.write(token)
	sys.stdout.flush()

def auth(username, server, password):
	hash=db["%s@%s"%(username, server)]
	if bcrypt.hashpw(password, hash) == hash:
		return True
	else:
		return False

def isuser(username, server):
	if "%s@%s"%(username, server) in db:
		return True
	else:
		return False

def setpass(username, server, password):
	db["%s@%s"%(username, server)]=bcrypt.hashpw(password, bcrypt.gensalt())
	return True

while True:
	data = from_ejabberd()
	success = False
	if data[0] == "auth":
		success = auth(data[1], data[2], data[3])
	elif data[0] == "isuser":
		success = isuser(data[1], data[2])
	elif data[0] == "setpass":
		success = setpass(data[1], data[2], data[3])
	elif data[0] == "tryregister":
		success = setpass(data[1], data[2], data[3])
	to_ejabberd(success)
