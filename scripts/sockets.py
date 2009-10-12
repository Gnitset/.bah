#! /usr/bin/env python
#coding: utf-8
# едц

import socket
import select
import threading
import signal
import sys
import time
import collections

class ServerSocket:
	def __init__(self, host, port, timeout=30, split="\n", debug=False):
		signal.signal(signal.SIGINT,self.quit)
		self._timeout=timeout
		self._split=split
		self._debug = debug

		self._socketlist=set()
		self._socketwrite=dict()
		self._socketinbuf=dict()

		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self._socket.bind((host, port))
		self._socket.listen(5)
		self._socketlist.add(self._socket)


	def main(self):
		while True:
			(read, write, error)=select.select(self._socketlist, self._socketwrite.keys(), self._socketlist, self._timeout)
			if self._debug: print read, write, error

			if self._socket in read:
				(clientsocket, address) = self._socket.accept()
				if self._debug: print address
				clientsocket.setblocking(False)
				self._socketlist.add(clientsocket)
				read.remove(self._socket)

			for socket_ in write:
				assert self._socketwrite[socket_]		
				try:
					while self._socketwrite[socket_]:
						send_data=self._socketwrite[socket_].popleft()
						data_sent=socket_.send(send_data)

						if self._debug: print time.ctime(), socket_.getpeername(), "out", send_data[:data_sent]

						if len(send_data) > data_sent:
							self._socketwrite[socket_].appendleft(send_data[data_sent:])
							if self._debug: print "try again, wrote %s" % data_sent

					del self._socketwrite[socket_]
				except socket.error, se:
					if se.errno == 11:
						self._socketwrite[socket_].appendleft(send_data)
						pass
					else:
						raise

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

				split_data=data.split(self._split)
				self._socketinbuf[socket_]=split_data[-1]
				lines=split_data[:-1]
				if self._debug:
					if self._socketinbuf[socket_]:
						print ">>> halva rader"
					else:
						print ">>> hela rader"

				if self._debug:
					for line in lines:
						print time.ctime(), socket_.getpeername(), "in", line.strip()

				if lines: self.readCall(socket_, lines)

			for socket_ in error:
				try:
					socket_.shutdown(socket.SHUT_RDWR)
				finally:
					self._socketlist.remove(socket_)

	def readCall(self, clientsocket, lines):
		raise NotImplemented

	def write(self, target, lines):
		if target != "all":
			recipients=[target]
		else:
			recipients=self._socketlist ^ set([self._socket])
			
		for recipient in recipients:
			if not self._socketwrite.has_key(recipient):
				self._socketwrite[recipient]=collections.deque()
			self._socketwrite[recipient].extend(lines)

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

if __name__ == "__main__":
	class EchoServer(ServerSocket):
		def readCall(self, clientsocket, lines):
			if self._debug: print clientsocket, lines
			self.write(clientsocket, [a+self._split for a in lines])

	s=EchoServer("0.0.0.0", 1234, 5, debug=True)
	s.main()
