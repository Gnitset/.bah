#! /usr/bin/env python
#coding: utf-8
# едц

import socket
import select
import threading
import signal
import sys

class Listner(threading.Thread):
	def __init__(self, socket, socketlist):
		threading.Thread.__init__(self)
		self._socket = socket
		self._socketlist = socketlist

	def run(self):
		assert self._socket
		print self._socket

		while True:
			(clientsocket, address) = self._socket.accept()
			print address
			self._socketlist.append(clientsocket)

class ServerSocket:
	def __init__(self):
		signal.signal(signal.SIGINT,self.quit)

		self._socketlist=[]
		self._socketwrite=[]

		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._socket.bind((socket.gethostname(), 1234))
		self._socket.listen(5)

		self._listner=Listner(self._socket, self._socketlist)
		self._listner.start()

		while True:
			(read, write, error)=select.select(self._socketlist, self._socketwrite, self._socketlist, 30)
			print read, write, error
			for socket_ in read:
				socket_.recv(8192)

	def quit(self, signr, frame):
		for socket_ in self._socketlist:
			socket_.shutdown(socket.SHUT_RDWR)
			socket_.close()
		self._socket.close()
		sys.exit()

s=ServerSocket()
