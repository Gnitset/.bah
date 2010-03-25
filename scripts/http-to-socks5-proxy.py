#!/usr/bin/env python
# -*- coding: utf8 -*-
#åäö

# This is a mashup built from PythonProxy.py and SocksiPy
# The mashup is created by Klas Meder Boqvist
# I leave no waranty

# -- BEGIN included PythonProxy.py --
# <PythonProxy.py>
#
#Copyright (c) <2009> <Fábio Domingues - fnds3000 in gmail.com>
#
#Permission is hereby granted, free of charge, to any person
#obtaining a copy of this software and associated documentation
#files (the "Software"), to deal in the Software without
#restriction, including without limitation the rights to use,
#copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the
#Software is furnished to do so, subject to the following
#conditions:
#
#The above copyright notice and this permission notice shall be
#included in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#OTHER DEALINGS IN THE SOFTWARE.

PythonProxy_doc="""\
Copyright (c) <2009> <Fábio Domingues - fnds3000 in gmail.com> <MIT Licence>

                  **************************************
                 *** Python Proxy - A Fast HTTP proxy ***
                  **************************************

Neste momento este proxy é um Elie Proxy.

Suporta os métodos HTTP:
 - OPTIONS;
 - GET;
 - HEAD;
 - POST;
 - PUT;
 - DELETE;
 - TRACE;
 - CONENCT.

Suporta:
 - Conexões dos cliente em IPv4 ou IPv6;
 - Conexões ao alvo em IPv4 e IPv6;
 - Conexões todo o tipo de transmissão de dados TCP (CONNECT tunneling),
     p.e. ligações SSL, como é o caso do HTTPS.

A fazer:
 - Verificar se o input vindo do cliente está correcto;
   - Enviar os devidos HTTP erros se não, ou simplesmente quebrar a ligação;
 - Criar um gestor de erros;
 - Criar ficheiro log de erros;
 - Colocar excepções nos sítios onde é previsível a ocorrência de erros,
     p.e.sockets e ficheiros;
 - Rever tudo e melhorar a estrutura do programar e colocar nomes adequados nas
     variáveis e métodos;
 - Comentar o programa decentemente;
 - Doc Strings.

Funcionalidades futuras:
 - Adiconar a funcionalidade de proxy anónimo e transparente;
 - Suportar FTP?.


(!) Atenção o que se segue só tem efeito em conexões não CONNECT, para estas o
 proxy é sempre Elite.

Qual a diferença entre um proxy Elite, Anónimo e Transparente?
 - Um proxy elite é totalmente anónimo, o servidor que o recebe não consegue ter
     conhecimento da existência do proxy e não recebe o endereço IP do cliente;
 - Quando é usado um proxy anónimo o servidor sabe que o cliente está a usar um
     proxy mas não sabe o endereço IP do cliente;
     É enviado o cabeçalho HTTP "Proxy-agent".
 - Um proxy transparente fornece ao servidor o IP do cliente e um informação que
     se está a usar um proxy.
     São enviados os cabeçalhos HTTP "Proxy-agent" e "HTTP_X_FORWARDED_FOR".

"""

import socket, thread, select

__version__ = '0.1.0 Draft 1'
BUFLEN = 8192
VERSION = 'Python Proxy/'+__version__
HTTPVER = 'HTTP/1.1'

class ConnectionHandler:
    def __init__(self, connection, address, timeout):
        self.client = connection
        self.client_buffer = ''
        self.timeout = timeout
        self.method, self.path, self.protocol = self.get_base_header()
        if self.method=='CONNECT':
            self.method_CONNECT()
        elif self.method in ('OPTIONS', 'GET', 'HEAD', 'POST', 'PUT',
                             'DELETE', 'TRACE'):
            self.method_others()
        self.client.close()
        self.target.close()

    def get_base_header(self):
        while 1:
            self.client_buffer += self.client.recv(BUFLEN)
            end = self.client_buffer.find('\n')
            if end!=-1:
                break
        print '%s'%self.client_buffer[:end]#debug
        data = (self.client_buffer[:end+1]).split()
        self.client_buffer = self.client_buffer[end+1:]
        return data

    def method_CONNECT(self):
        self._connect_target(self.path)
        self.client.send(HTTPVER+' 200 Connection established\n'+
                         'Proxy-agent: %s\n\n'%VERSION)
        self.client_buffer = ''
        self._read_write()        

    def method_others(self):
        self.path = self.path[7:]
        i = self.path.find('/')
        host = self.path[:i]        
        path = self.path[i:]
        self._connect_target(host)
        self.target.send('%s %s %s\n'%(self.method, path, self.protocol)+
                         self.client_buffer)
        self.client_buffer = ''
        self._read_write()

    def _connect_target(self, host):
        i = host.find(':')
        if i!=-1:
            port = int(host[i+1:])
            host = host[:i]
        else:
            port = 80
        (soc_family, _, _, _, address) = socket.getaddrinfo(host, port)[0]
        self.target = socket.socket(soc_family)
        self.target.connect(address)

    def _read_write(self):
        time_out_max = self.timeout/3
        socs = [self.client, self.target]
        count = 0
        while 1:
            count += 1
            (recv, _, error) = select.select(socs, [], socs, 3)
            if error:
                break
            if recv:
                for in_ in recv:
                    data = in_.recv(BUFLEN)
                    if in_ is self.client:
                        out = self.target
                    else:
                        out = self.client
                    if data:
                        out.send(data)
                        count = 0
            if count == time_out_max:
                break

def start_server(host='localhost', port=8080, IPv6=False, timeout=60,
                  handler=ConnectionHandler):
    if IPv6==True:
        soc_type=socket.AF_INET6
    else:
        soc_type=socket.AF_INET
    soc = socket.socket(soc_type)
    soc.bind((host, port))
    print "Serving on %s:%d."%(host, port)#debug
    soc.listen(0)
    while 1:
        thread.start_new_thread(handler, soc.accept()+(timeout,))

#if __name__ == '__main__':
#    start_server()

# -- BEGIN included socks.py --

socks_doc="""SocksiPy - Python SOCKS module.
Version 1.00

Copyright 2006 Dan-Haim. All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
3. Neither the name of Dan Haim nor the names of his contributors may be used
   to endorse or promote products derived from this software without specific
   prior written permission.
   
THIS SOFTWARE IS PROVIDED BY DAN HAIM "AS IS" AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
EVENT SHALL DAN HAIM OR HIS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA
OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMANGE.


This module provides a standard socket-like interface for Python
for tunneling connections through SOCKS proxies.

"""

import socket
import struct

PROXY_TYPE_SOCKS4 = 1
PROXY_TYPE_SOCKS5 = 2
PROXY_TYPE_HTTP = 3

_defaultproxy = None
_orgsocket = socket.socket

class ProxyError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class GeneralProxyError(ProxyError):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class Socks5AuthError(ProxyError):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class Socks5Error(ProxyError):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class Socks4Error(ProxyError):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class HTTPError(ProxyError):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

_generalerrors = ("success",
		   "invalid data",
		   "not connected",
		   "not available",
		   "bad proxy type",
		   "bad input")

_socks5errors = ("succeeded",
		  "general SOCKS server failure",
		  "connection not allowed by ruleset",
		  "Network unreachable",
		  "Host unreachable",
		  "Connection refused",
		  "TTL expired",
		  "Command not supported",
		  "Address type not supported",
		  "Unknown error")

_socks5autherrors = ("succeeded",
		      "authentication is required",
		      "all offered authentication methods were rejected",
		      "unknown username or invalid password",
		      "unknown error")

_socks4errors = ("request granted",
		  "request rejected or failed",
		  "request rejected because SOCKS server cannot connect to identd on the client",
		  "request rejected because the client program and identd report different user-ids",
		  "unknown error")

def setdefaultproxy(proxytype=None,addr=None,port=None,rdns=True,username=None,password=None):
	"""setdefaultproxy(proxytype, addr[, port[, rdns[, username[, password]]]])
	Sets a default proxy which all further socksocket objects will use,
	unless explicitly changed.
	"""
	global _defaultproxy
	_defaultproxy = (proxytype,addr,port,rdns,username,password)
	
class socksocket(socket.socket):
	"""socksocket([family[, type[, proto]]]) -> socket object
	
	Open a SOCKS enabled socket. The parameters are the same as
	those of the standard socket init. In order for SOCKS to work,
	you must specify family=AF_INET, type=SOCK_STREAM and proto=0.
	"""
	
	def __init__(self, family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, _sock=None):
		_orgsocket.__init__(self,family,type,proto,_sock)
		if _defaultproxy != None:
			self.__proxy = _defaultproxy
		else:
			self.__proxy = (None, None, None, None, None, None)
		self.__proxysockname = None
		self.__proxypeername = None
	
	def __recvall(self, bytes):
		"""__recvall(bytes) -> data
		Receive EXACTLY the number of bytes requested from the socket.
		Blocks until the required number of bytes have been received.
		"""
		data = ""
		while len(data) < bytes:
			data = data + self.recv(bytes-len(data))
		return data
	
	def setproxy(self,proxytype=None,addr=None,port=None,rdns=True,username=None,password=None):
		"""setproxy(proxytype, addr[, port[, rdns[, username[, password]]]])
		Sets the proxy to be used.
		proxytype -	The type of the proxy to be used. Three types
				are supported: PROXY_TYPE_SOCKS4 (including socks4a),
				PROXY_TYPE_SOCKS5 and PROXY_TYPE_HTTP
		addr -		The address of the server (IP or DNS).
		port -		The port of the server. Defaults to 1080 for SOCKS
				servers and 8080 for HTTP proxy servers.
		rdns -		Should DNS queries be preformed on the remote side
				(rather than the local side). The default is True.
				Note: This has no effect with SOCKS4 servers.
		username -	Username to authenticate with to the server.
				The default is no authentication.
		password -	Password to authenticate with to the server.
				Only relevant when username is also provided.
		"""
		self.__proxy = (proxytype,addr,port,rdns,username,password)
	
	def __negotiatesocks5(self,destaddr,destport):
		"""__negotiatesocks5(self,destaddr,destport)
		Negotiates a connection through a SOCKS5 server.
		"""
		# First we'll send the authentication packages we support.
		if (self.__proxy[4]!=None) and (self.__proxy[5]!=None):
			# The username/password details were supplied to the
			# setproxy method so we support the USERNAME/PASSWORD
			# authentication (in addition to the standard none).
			self.sendall("\x05\x02\x00\x02")
		else:
			# No username/password were entered, therefore we
			# only support connections with no authentication.
			self.sendall("\x05\x01\x00")
		# We'll receive the server's response to determine which
		# method was selected
		chosenauth = self.__recvall(2)
		if chosenauth[0] != "\x05":
			self.close()
			raise GeneralProxyError((1,_generalerrors[1]))
		# Check the chosen authentication method
		if chosenauth[1] == "\x00":
			# No authentication is required
			pass
		elif chosenauth[1] == "\x02":
			# Okay, we need to perform a basic username/password
			# authentication.
			self.sendall("\x01" + chr(len(self.__proxy[4])) + self.__proxy[4] + chr(len(self.proxy[5])) + self.__proxy[5])
			authstat = self.__recvall(2)
			if authstat[0] != "\x01":
				# Bad response
				self.close()
				raise GeneralProxyError((1,_generalerrors[1]))
			if authstat[1] != "\x00":
				# Authentication failed
				self.close()
				raise Socks5AuthError,((3,_socks5autherrors[3]))
			# Authentication succeeded
		else:
			# Reaching here is always bad
			self.close()
			if chosenauth[1] == "\xFF":
				raise Socks5AuthError((2,_socks5autherrors[2]))
			else:
				raise GeneralProxyError((1,_generalerrors[1]))
		# Now we can request the actual connection
		req = "\x05\x01\x00"
		# If the given destination address is an IP address, we'll
		# use the IPv4 address request even if remote resolving was specified.
		try:
			ipaddr = socket.inet_aton(destaddr)
			req = req + "\x01" + ipaddr
		except socket.error:
			# Well it's not an IP number,  so it's probably a DNS name.
			if self.__proxy[3]==True:
				# Resolve remotely
				ipaddr = None
				req = req + "\x03" + chr(len(destaddr)) + destaddr
			else:
				# Resolve locally
				ipaddr = socket.inet_aton(socket.gethostbyname(destaddr))
				req = req + "\x01" + ipaddr
		req = req + struct.pack(">H",destport)
		self.sendall(req)
		# Get the response
		resp = self.__recvall(4)
		if resp[0] != "\x05":
			self.close()
			raise GeneralProxyError((1,_generalerrors[1]))
		elif resp[1] != "\x00":
			# Connection failed
			self.close()
			if ord(resp[1])<=8:
				raise Socks5Error(ord(resp[1]),_generalerrors[ord(resp[1])])
			else:
				raise Socks5Error(9,_generalerrors[9])
		# Get the bound address/port
		elif resp[3] == "\x01":
			boundaddr = self.__recvall(4)
		elif resp[3] == "\x03":
			resp = resp + self.recv(1)
			boundaddr = self.__recvall(resp[4])
		else:
			self.close()
			raise GeneralProxyError((1,_generalerrors[1]))
		boundport = struct.unpack(">H",self.__recvall(2))[0]
		self.__proxysockname = (boundaddr,boundport)
		if ipaddr != None:
			self.__proxypeername = (socket.inet_ntoa(ipaddr),destport)
		else:
			self.__proxypeername = (destaddr,destport)
	
	def getproxysockname(self):
		"""getsockname() -> address info
		Returns the bound IP address and port number at the proxy.
		"""
		return self.__proxysockname
	
	def getproxypeername(self):
		"""getproxypeername() -> address info
		Returns the IP and port number of the proxy.
		"""
		return _orgsocket.getpeername(self)
	
	def getpeername(self):
		"""getpeername() -> address info
		Returns the IP address and port number of the destination
		machine (note: getproxypeername returns the proxy)
		"""
		return self.__proxypeername
	
	def __negotiatesocks4(self,destaddr,destport):
		"""__negotiatesocks4(self,destaddr,destport)
		Negotiates a connection through a SOCKS4 server.
		"""
		# Check if the destination address provided is an IP address
		rmtrslv = False
		try:
			ipaddr = socket.inet_aton(destaddr)
		except socket.error:
			# It's a DNS name. Check where it should be resolved.
			if self.__proxy[3]==True:
				ipaddr = "\x00\x00\x00\x01"
				rmtrslv = True
			else:
				ipaddr = socket.inet_aton(socket.gethostbyname(destaddr))
		# Construct the request packet
		req = "\x04\x01" + struct.pack(">H",destport) + ipaddr
		# The username parameter is considered userid for SOCKS4
		if self.__proxy[4] != None:
			req = req + self.__proxy[4]
		req = req + "\x00"
		# DNS name if remote resolving is required
		# NOTE: This is actually an extension to the SOCKS4 protocol
		# called SOCKS4A and may not be supported in all cases.
		if rmtrslv==True:
			req = req + destaddr + "\x00"
		self.sendall(req)
		# Get the response from the server
		resp = self.__recvall(8)
		if resp[0] != "\x00":
			# Bad data
			self.close()
			raise GeneralProxyError((1,_generalerrors[1]))
		if resp[1] != "\x5A":
			# Server returned an error
			self.close()
			if ord(resp[1]) in (91,92,93):
				self.close()
				raise Socks4Error((ord(resp[1]),_socks4errors[ord(resp[1])-90]))
			else:
				raise Socks4Error((94,_socks4errors[4]))
		# Get the bound address/port
		self.__proxysockname = (socket.inet_ntoa(resp[4:]),struct.unpack(">H",resp[2:4])[0])
		if rmtrslv != None:
			self.__proxypeername = (socket.inet_ntoa(ipaddr),destport)
		else:
			self.__proxypeername = (destaddr,destport)
	
	def __negotiatehttp(self,destaddr,destport):
		"""__negotiatehttp(self,destaddr,destport)
		Negotiates a connection through an HTTP server.
		"""
		# If we need to resolve locally, we do this now
		if self.__proxy[3] == False:
			addr = socket.gethostbyname(destaddr)
		else:
			addr = destaddr
		self.sendall("CONNECT " + addr + ":" + str(destport) + " HTTP/1.1\r\n" + "Host: " + destaddr + "\r\n\r\n")
		# We read the response until we get the string "\r\n\r\n"
		resp = self.recv(1)
		while resp.find("\r\n\r\n")==-1:
			resp = resp + self.recv(1)
		# We just need the first line to check if the connection
		# was successful
		statusline = resp.splitlines()[0].split(" ",2)
		if statusline[0] not in ("HTTP/1.0","HTTP/1.1"):
			self.close()
			raise GeneralProxyError((1,_generalerrors[1]))
		try:
			statuscode = int(statusline[1])
		except ValueError:
			self.close()
			raise GeneralProxyError((1,_generalerrors[1]))
		if statuscode != 200:
			self.close()
			raise HTTPError((statuscode,statusline[2]))
		self.__proxysockname = ("0.0.0.0",0)
		self.__proxypeername = (addr,destport)
	
	def connect(self,destpair):
		"""connect(self,despair)
		Connects to the specified destination through a proxy.
		destpar - A tuple of the IP/DNS address and the port number.
		(identical to socket's connect).
		To select the proxy server use setproxy().
		"""
		# Do a minimal input check first
		if (type(destpair) in (list,tuple)==False) or (len(destpair)<2) or (type(destpair[0])!=str) or (type(destpair[1])!=int):
			raise GeneralProxyError((5,_generalerrors[5]))
		if self.__proxy[0] == PROXY_TYPE_SOCKS5:
			if self.__proxy[2] != None:
				portnum = self.__proxy[2]
			else:
				portnum = 1080
			_orgsocket.connect(self,(self.__proxy[1],portnum))
			self.__negotiatesocks5(destpair[0],destpair[1])
		elif self.__proxy[0] == PROXY_TYPE_SOCKS4:
			if self.__proxy[2] != None:
				portnum = self.__proxy[2]
			else:
				portnum = 1080
			_orgsocket.connect(self,(self.__proxy[1],portnum))
			self.__negotiatesocks4(destpair[0],destpair[1])
		elif self.__proxy[0] == PROXY_TYPE_HTTP:
			if self.__proxy[2] != None:
				portnum = self.__proxy[2]
			else:
				portnum = 8080
			_orgsocket.connect(self,(self.__proxy[1],portnum))
			self.__negotiatehttp(destpair[0],destpair[1])
		elif self.__proxy[0] == None:
			_orgsocket.connect(self,(destpair[0],destpair[1]))
		else:
			raise GeneralProxyError((4,_generalerrors[4]))

# -- BEGIN the code i actually wrote --

if __name__ == '__main__':
    bind_host='localhost'
    bind_port=8080
    socks_host='localhost'
    socks_port=1080
    timeout=60

    setdefaultproxy(PROXY_TYPE_SOCKS5, socks_host, socks_port)
    socket.socket = socksocket

    soc = socket.socket()
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    soc.bind((bind_host, bind_port))
    print "Serving on %s:%d."%(bind_host, bind_port)#debug
    soc.listen(0)
    while 1:
        thread.start_new_thread(ConnectionHandler, soc.accept()+(timeout,))
