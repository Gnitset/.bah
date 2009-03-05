#! /usr/bin/env python2.5

import os, sys, time

root="/a/backup/kbackup"
lockfile=".kbackup.lock"
sources={}

sources["doija.int.ladan.se"]={ "interval": "d", "keep": 30, "user": "backup", "password": "ChangeMe" }
sources["mail.oijk.net"]={ "interval": "h", "keep": 30, "user": "backup", "password": "ChangeMe" }

def main():
	try:
		os.stat(os.path.join(root,lockfile))
		print "lockfile exists"
		sys.exit(1)
	except: pass

	for host in sources:
		kb=KBackup(root, host, sources[host])
		kb.rotate()
		kb.sync()
		print host, "completed"

class KBackup():
	root=""
	host=""
	keep="7"
	sourcename="backup"
	user="backup"
	password=""

	def __init__(self, root, host, conf):
		self.root=root
		self.host=host
		try:
			assert conf["keep"]
			self.keep=conf["keep"]
		except: pass
		try:
			self.user=conf["user"]
		except: pass
		try:
			self.password=conf["password"]
		except: pass
		try:
			self.sourcename=conf["sourcename"]
		except: pass

	def rotate(self):
		now=time.time()
		bort=[]

		for dir in os.listdir(os.path.join(self.root, self.host)):
			try:
				s=os.stat(os.path.join(self.root, self.host, dir))
			except: continue
			try:
				if s[-1] < (now-(self.keep*24*60*60)) and dir != "current" \
				   and os.path.join(self.root, self.host, dir) != os.readlink(os.path.join(self.root, self.host, "current")):
					bort.append(os.path.join(self.root, self.host, dir))
			except: pass
		
		print '\n'.join(bort)

		return False

	def sync(self):
		new=os.path.join(self.root, self.host, "new")
		current=os.path.join(self.root, self.host, "current")

		print "running rsync on host", self.host, "with sourcename", self.sourcename
		ret_val=os.spawnvpe(os.P_WAIT, "rsync", ["rsync", "--archive", "--delete", "--numeric-ids", "--hard-links", "--sparse", "--link-dest="+current, self.host+"::"+self.sourcename+"/", new], { "USER": self.user, "RSYNC_PASSWORD": self.password } )

		if ret_val < 0:
			print "cleanup"
			os.spawnvp(os.P_WAIT, "rm", ["rm", "-r", new])
			sys.exit(2)

		stime=time.time()
		os.utime(new, (stime, stime))
		os.rename(new, os.path.join(self.root, self.host, time.asctime(time.localtime(stime))))
		try:
			os.remove(current)
		except: pass
		os.symlink(time.asctime(time.localtime(stime)), current)


if __name__ == "__main__":
	main()
