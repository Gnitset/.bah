#!/usr/bin/env python

import sys, time, re, os, socket, base64, md5#, bcrypt

DEBUG = False
if DEBUG:
	IN = open("IN", "w")
	OUT = open("OUT", "w")

class state: pass
state = state()
def reset(all):
	if all:
		state.auth = ()
		state.username = ""
		state.mailname = ""
		state.hostname = ""
		state.auth_id = ""
	state.to = []
	state.sender = ""
reset(True)
state.helo_name = ""

def get_line(f = sys.stdin):
	line = f.readline()
	if DEBUG and f == sys.stdin: IN.write(line)
	while line and (line[-1] == "\n" or line[-1] == "\r"):
		line = line[:-1]
	return line

def put_line(l):
	if DEBUG: OUT.write(l + "\r\n")
	sys.stdout.write(l + "\r\n")
	sys.stdout.flush()

def need_auth(args, current):
	put_line("503 Authentication first")
	return current

def c_quit(args, current):
	put_line("221 " + hostname)

def c_helo(args, current):
	reset(True)
	state.helo_name = args
	put_line("250 " + hostname)
	return {"MAIL": need_auth}

def c_ehlo(args, current):
	reset(True)
	state.helo_name = args
	put_line("250-" + hostname)
	put_line("250-PIPELINING")
	put_line("250-AUTH PLAIN LOGIN")
	put_line("250 8BITMIME")
	return {"MAIL": need_auth}

def c_auth(args, current):
	args = args.split()
	type = args[0].upper()
	if type == "PLAIN" and len(args) == 2:
		auth = b64dec(args[1])
		if len(auth) > 0:
			auth = auth[1:].split(auth[0])
			if len(auth) == 2 or (len(auth) == 3 and not auth[2]):
				return check_auth(auth[0], auth[1], current)
	elif type == "LOGIN":
		put_line("334 VXNlcm5hbWU6")
		username = b64dec(get_line())
		put_line("334 UGFzc3dvcmQ6")
		password = b64dec(get_line())
		return check_auth(username, password, current)
	put_line("504 Bad AUTH")
	return current

def check_auth(username, password, current):
	users = open("/var/qmail/users/smtpd", "r")
	line = get_line(users)
	while line:
		if line[0] != "#":
			if line == username + ":":
				check_password = get_line(users)
				if cmp_password(password, check_password):
					state.auth_id = get_line(users)
					state.mailname = get_line(users)
					state.auth = get_line(users).split()
					put_line("235 auth ok")
					return {"MAIL": c_mail}
		line = get_line(users)
	put_line("535 Failed")
	return current

def b64dec(str):
	try:
		return base64.decodestring(str)
	except:
		return ""

def c_mail(args, current):
	if len(args) < 6 or args[:5].upper() != "FROM:":
		put_line("550 Bad MAIL")
		return current
	addr = fix_addr(args[5:])
	if addr_allowed(addr):
		state.sender = addr
		put_line("250 ok")
	else:
		put_line("550 Not permitted")
		return current
	return {"RCPT": c_rcpt, "DATA": c_data}

def c_rcpt(args, current):
	if len(args) < 5 or args[:3].upper() != "TO:":
		put_line("550 Bad RCPT")
		return current
	addr = fix_addr(args[3:])
	s = addr.split("@")
	if len(s) < 2 or s[-1].find(".") == -1:
		put_line("550 Bad address")
		return current
	state.to.append(addr)
	put_line("250 ok")
	return current

def c_data(args, current):
	if not state.to:
		put_line("503 No recipients")
		return current
	in_progress = True
	in_headers = True
	prev_crlf = True
	data = []
	put_line("354 go ahead")
	while in_progress:
		line = sys.stdin.readline()
		if line == ".\r\n" and prev_crlf:
			in_progress = False
		else:
			if line[0] == ".":
				line = line[1:]
			if line[-2:] == "\r\n":
				prev_crlf = True
				line = line[:-2] + "\n"
			data.append(line)
	(read_fd, write_fd) = os.pipe()
	pid = os.fork()
	if pid:
		os.close(read_fd)
		os.write(write_fd, "Received: from " + state.auth_id + " (" + sanitize(state.helo_name) + ")\n")
		os.write(write_fd, "  by " + hostname + " with SMTP; " + time.strftime("%d %b %Y %T %z") + "\n")
		for line in data:
			os.write(write_fd, line)
		os.close(write_fd)
		(epid, status) = os.wait()
		if epid != pid or status != 0:
			put_line("X Error, ("+ str(epid) + ", " + str(pid) + ") " + str(status))
		else:
			put_line("250 ok queued")
	else:
		os.dup2(read_fd, 0)
		os.close(read_fd)
		os.close(write_fd)
		args = ["qmail-inject", "-a", "-f" + state.sender]
		os.putenv("QMAILNAME", state.mailname)
		sender = state.sender.split("@")
		os.putenv("QMAILUSER", "@".join(sender[:-1]))
		os.putenv("QMAILHOST", sender[-1])
		os.execv("/var/qmail/bin/qmail-inject", args + state.to)
		os._exit(99)
	reset(False)
	return {"MAIL": c_mail}

def c_noop(args, current):
	put_line("250 ok")
	return current

def c_rset(args, current):
	reset(True)
	put_line("250 ok")
	return initial_commands

def sanitize(str):
	res = ""
	for c in str:
		if ord(c) >= 32 and ord(c) < 128:
			res += c
	if len(res) > 51: return res[:48] + "..."
	return res

def fix_addr(addr):
	if addr[-14:] == " BODY=8BITMIME": # YAM
		addr = addr[:-14]
	if addr[-1] == ">":
		addr = addr.split("<")[-1][:-1]
	for c in addr:
		if ord(c) <= 32 and ord(c) >= 128: return ""
	return addr

def addr_allowed(addr):
	for pat in state.auth:
		if re.match("^" + pat + "$", addr, re.I): return True

known_commands = ("HELO", "EHLO", "MAIL", "RCPT", "DATA", "QUIT", "NOOP", "RSET")
initial_commands = {"MAIL": need_auth}
always_commands = {"HELO": c_helo, "EHLO": c_ehlo, "AUTH": c_auth, "QUIT": c_quit, "NOOP": c_noop, "RSET": c_rset}

def smtp():
	put_line("220 " + hostname + " ESMTP")
	commands = initial_commands
	while commands != None:
		line = get_line()
		ok = False
		cmd = line[:4].upper()
		if len(line) < 5 or line[4] == " ":
			for cmds in commands, always_commands:
				for c, func in cmds.items():
					if c == cmd:
						commands = func(line[5:], commands)
						ok = True
		if not ok:
			if cmd in known_commands:
				put_line("503 Command " + cmd + " not appropriate here")
			else:
				put_line("500 Command not recognized")

def cmp_password(password, hashed):
	if hashed[:3] == "$1$":
		return md5_password(password, hashed) == hashed
#	if hashed[:4] == "$2a$":
#		return bcrypt.hashpw(password, hashed) == hashed
	return False

def to64(v, l):
	a = "./0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
	r = ""
	while l:
		r += a[v & 0x3f]
		v >>= 6
		l -= 1
	return r

def md5_password(password, salt = ""):
	if salt[:3] == "$1$":
		(salt, crypt) = salt[3:].split("$")
	if not salt:
		return None
	ctx = md5.md5()
	ctx.update(password)
	ctx.update("$1$")
	ctx.update(salt)
	ctx1 = md5.md5()
	ctx1.update(password)
	ctx1.update(salt)
	ctx1.update(password)
	final = ctx1.digest()
	pl = len(password)
	while pl > 0:
		ctx.update(final[:pl])
		pl -= 16
	i = len(password)
	while i:
		if i & 1: ctx.update("\x00")
		else:     ctx.update(password[0])
		i >>= 1
	final = ctx.digest()
	for i in range(0, 1000):
		ctx1 = md5.md5()
		if i & 1: ctx1.update(password)
		else:     ctx1.update(final)
		if i % 3: ctx1.update(salt)
		if i % 7: ctx1.update(password)
		if i & 1: ctx1.update(final)
		else:     ctx1.update(password)
		final = ctx1.digest()
	p = ""
	p += to64(ord(final[0]) << 16 | ord(final[6]) << 8 | ord(final[12]), 4)
	p += to64(ord(final[1]) << 16 | ord(final[7]) << 8 | ord(final[13]), 4)
	p += to64(ord(final[2]) << 16 | ord(final[8]) << 8 | ord(final[14]), 4)
	p += to64(ord(final[3]) << 16 | ord(final[9]) << 8 | ord(final[15]), 4)
	p += to64(ord(final[4]) << 16 | ord(final[10]) << 8 | ord(final[5]), 4)
	p += to64(ord(final[11]), 2)
	return "$1$" + salt + "$" + p

# Remote IP is useless with stunnel. ("transparent" option doesn't work.)
#remote_ip = "REMOTE"
#try:
#	sock = socket.fromfd(0, socket.AF_INET, socket.SOCK_STREAM)
#	remote_ip = sock.getpeername()[0]
#except: pass
if os.getenv("TCPREMOTEHOST"):
	remote_ip = os.getenv("TCPREMOTEHOST")
else:
	remote_ip = os.getenv("TCPREMOTEIP")

hostname = socket.gethostname()
smtp()

