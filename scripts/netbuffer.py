#!/usr/bin/env python

import os, sys, socket, select, collections, time

debug=True

sport=4001
lport=4002
ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ss.bind(("0.0.0.0", sport))
ss.listen(5)
sl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sl.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sl.bind(("0.0.0.0", lport))
sl.listen(5)

read_clients=set([sl,ss])
lclients=set()
socketlist=set([sl,ss])
socketwrite=dict()

while True:
	(read, write, error)=select.select(read_clients, socketwrite.keys(), socketlist, 60)
	if debug: print read, write, error


	for socket_ in write:
		assert socketwrite[socket_]
		try:
			while socketwrite[socket_]:
				send_data=socketwrite[socket_].popleft()
				data_sent=socket_.send(send_data)

				if debug: print time.ctime(), socket_.getpeername(), "out", send_data[:data_sent]

				if len(send_data) > data_sent:
					socketwrite[socket_].appendleft(send_data[data_sent:])
					if debug: print "try again, wrote %s" % data_sent

			del socketwrite[socket_]
		except socket.error, se:
			if se.errno == 11 or se.errno == 32:
				socketwrite[socket_].appendleft(send_data)
				pass
			else:
				raise

	for socket_ in read:
		if socket_ is ss:
			(clientsocket, address) = socket_.accept()
			if debug: print "server",address
			clientsocket.setblocking(False)
			socketlist.add(clientsocket)
			read_clients.add(clientsocket)
			read.remove(socket_)
			continue
		if socket_ is sl:
			(clientsocket, address) = socket_.accept()
			if debug: print "lclient",address
			clientsocket.setblocking(False)
			socketlist.add(clientsocket)
			lclients.add(clientsocket)
			read.remove(socket_)
			continue

		data=socket_.recv(8192)

		if not data:
			try:
				socket_.close()
			finally:
				socketlist.remove(socket_)
				if socket_ in socketwrite: del socketwrite[socket_]
				if socket_ in lclients: lclients.remove(socket_)
				if socket_ in read_clients: read_clients.remove(socket_)
			continue

		if debug:
			print time.ctime(), socket_.getpeername(), "in", data

		for sock in lclients:
			try:
				socketwrite[sock].append(data)
			except:
				socketwrite[sock]=collections.deque([data])


	for socket_ in error:
		try:
			socket_.shutdown(socket.SHUT_RDWR)
			if socket_ in socketwrite: del socketwrite[socket_]
			if socket_ in lclients: lclients.remove(socket_)
			if socket_ in read_clients: read_clients.remove(socket_)
		finally:
			socketlist.remove(socket_)

