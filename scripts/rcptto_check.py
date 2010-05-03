#!/usr/bin/env python

import os
import sys
import sqlite3

db_file="/mail/db/rcptto.db"
email=os.environ['SMTPRCPTTO']

conn = sqlite3.connect(db_file)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS mail (address TEXT PRIMARY KEY, occurrences INTEGER DEFAULT 1, status INTEGER DEFAULT 0)")
conn.commit()

matches=c.execute("SELECT COUNT(*) FROM mail WHERE address=?", (email,)).fetchall()[0][0]

if matches:
	res=c.execute("UPDATE mail SET occurrences=occurrences+1 WHERE address=?", (email,))
	conn.commit()
	status=c.execute("SELECT status FROM mail WHERE address=?", (email,)).fetchall()[0][0]
	if status==-1:
		sys.stderr.write("rcptto: rejected mail to <%s>\n"%email)
		sys.stdout.write("R550 Blocked email address <%s>.\n"%email)
	elif status==1:
		sys.stderr.write("rcptto: accepted mail to <%s>\n"%email)
		sys.stdout.write("N\n")
	else:
		sys.stderr.write("rcptto: let mail to <%s> through\n"%email)
else:
	res=c.execute("INSERT INTO mail (address) VALUES (?)", (email,))
	conn.commit()
	sys.stderr.write("rcptto: let mail to <%s> through\n"%email)
