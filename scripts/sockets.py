#! /usr/bin/env python
#coding: utf-8
# едц

import socket
import select
import threading
import signal
import sys
import time

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
			clientsocket.setblocking(False)
			self._socketlist.append(clientsocket)

class ServerSocket:
	def __init__(self, host, port, timeout=30, split="\n"):
		signal.signal(signal.SIGINT,self.quit)
		self._timeout=timeout
		self._split=split

		self._socketlist=[]
		self._socketwrite={}
		self._socketinbuf={}

		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self._socket.bind((host, port))
		self._socket.listen(5)

		self._listner=Listner(self._socket, self._socketlist)
		self._listner.start()


	def main(self):
		while True:
			(read, write, error)=select.select(self._socketlist, self._socketwrite.keys(), self._socketlist, self._timeout)
			print read, write, error

			for socket_ in write:
				assert self._socketwrite[socket_]		
				try:
					while self._socketwrite[socket_]:
						socket_.send(self._socketwrite[socket_].pop(0))
					del self._socketwrite[socket_]
				except: pass

			for socket_ in read:
				try:
					data=self._socketinbuf[socket_]+socket_.recv(8192)
				except:
					self._socketinbuf[socket_]=""
					data=socket_.recv(8192)

				if not data:
					try:
						socket_.close()
					finally:
						self._socketlist.remove(socket_)
					continue

				if data[-len(self._split):] != self._split:
					split_data=data.split(self._split)
					self._socketinbuf[socket_]=split_data[-1]
					lines=split_data[:-1]
					print ">>> halva rader"
				else:
					lines=data[:-len(self._split)].split(self._split)
					self._socketinbuf[socket_]=""
					print ">>> hela rader"

				self.readCall(socket_, lines)

			for socket_ in error:
				try:
					socket_.shutdown(socket.SHUT_RDWR)
				finally:
					self._socketlist.remove(socket_)

	def readCall(self, clientsocket, lines):
		return

	def write(self, target, lines):
		if not self._socketwrite.has_key(target):
			self._socketwrite[target]=[]

		if not self._socketwrite[target]:
			self._socketwrite[target]=lines
		else:
			self._socketwrite[target].extend(lines)

	def quit(self, signr, frame):
		for socket_ in self._socketlist:
			try:
				socket_.shutdown(socket.SHUT_RDWR)
			except: pass
			try:
				socket_.close()
			except: pass
		try:
			self._socket.close()
		except: pass
		sys.exit()

class Foo(ServerSocket):
	def readCall(self, clientsocket, lines):
		print clientsocket, lines
		self.write(clientsocket, [a+self._split for a in lines])

if __name__ == "__main__":
	s=Foo("0.0.0.0", 1234, 5)
	s.main()
