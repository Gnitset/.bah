#! /usr/bin/env python

import rfc822
import os
import re
import anydbm
import sys

# maildir subdirectory, spamassassin name, contents
# contents holds dictionaries of username:[mailfile, mailfile...]
sorts=(	("cur", "ham", {}),
	(".Junk/cur", "spam", {}))
learned=anydbm.open("/mail/db/learned_mail", "c")
re_readmail=re.compile("^(.*):2,[A-R]*S[^T]*$")

def spamd_user(mailfile):
	"""Function to determine which userdb let this email thru"""
	mail=rfc822.Message(open(mailfile))
	try:
		return mail['X-Spam-Queue'][mail['X-Spam-Queue'].index("<")+1:mail['X-Spam-Queue'].index(">")]
	except:
		return None

def learn_mail(name):
	"""Should we learn from this mail"""
	match= re_readmail.match(name)
	if match == None:
		return False
	elif match.groups()[0] in learned:
		learned[match.groups()[0]]="still here"
		return False
	else:
		return True

def sa_learn(type, user, mailarray):
	"""Call sa-learn for mailarray and learn them as typ in user's db"""
	for part in range(0,len(mailarray),50):
		os.spawnvp(os.P_WAIT, "sa-learn", ["sa-learn", "-u "+user, "--dbpath="+os.path.join("/mail", user, ".spamassassin"), \
			"--"+type, "--no-sync"]+mailarray[part:part+50])
		#print "sa-learn", ["sa-learn", "-u "+user, "--dbpath="+os.path.join("/mail", user, ".spamassassin"), "--"+type, "--no-sync"]+mailarray[part:part+50]
	os.spawnvp(os.P_WAIT, "sa-learn", ["sa-learn", "-u "+user, "--dbpath="+os.path.join("/mail", user, ".spamassassin"), "--sync"])

for usermaildir in filter(os.path.isdir, [os.path.join("/mail", namn, ".maildir") for namn in os.listdir("/mail")]):
	for subdir,name,kind in sorts:
		subpath=os.path.join(usermaildir, subdir)
		if os.path.isdir(subpath):
			for mail in filter(learn_mail, \
				[os.path.join(subpath,mailfile) for mailfile in os.listdir(subpath)]):
				user=spamd_user(mail)
				try:
					kind[user].append(mail)
				except:
					kind[user]=[mail]

for user in [namn for namn in os.listdir("/mail") if os.path.isdir(os.path.join("/mail", namn, ".spamassassin"))]:
	for subdir,name,kind in sorts:
		if user in kind:
			sys.stdout.write("%s:\n" % user)
			sys.stdout.flush()
			sa_learn(name, user, kind[user])
			learned.update([(mail[:mail.index(":")],"new") for mail in kind[user]])

for subdir,name,kind in sorts:
	for index in (None, "m"):
		if index in kind:
			learned.update([(mail[:mail.index(":")],"new") for mail in kind[index]])

for mail in learned.keys():
	if learned[mail] == "":
		print "del %s" % mail
		del learned[mail]
		continue
	learned[mail]=""
