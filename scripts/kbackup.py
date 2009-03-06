#! /usr/bin/env python2.5

import os, sys, time

root="/a/backup/kbackup"
lockfile=".kbackup.lock"
sources={}

sources["doija.int.ladan.se"]={ "interval": "d", "keep": 30, "user": "backup", "password": "ChangeMe" }
sources["web.ladan.se"]={ "interval": "d", "keep": 30, "user": "backup", "password": "ChangeMe" }
sources["mail.oijk.net"]={ "interval": "h", "keep": 30, "user": "backup", "password": "ChangeMe" }

def main():
	print time.asctime(time.localtime())
	try:
		os.stat(os.path.join(root,lockfile))
		print "lockfile exists"
		sys.exit(1)
	except: pass

	open(os.path.join(root, lockfile), "w").write(str(os.getpid()))

	for host in sources:
		kb=KBackup(root, host, sources[host])
		kb.rotate()
		kb.sync()
		print host, "completed"
	print time.asctime(time.localtime())

	os.remove(os.path.join(root,lockfile))

class KBackup():
	root=""
	host=""
	keep="7"
	sourcename="backup"
	user="backup"
	password=""
	now=0

	def __init__(self, root, host, conf):
		self.now=time.time()
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
		try:
			os.mkdir(os.path.join(self.root, self.host))
		except OSError, oe:
			if oe.errno != 17:
				raise


	def rotate(self):
		bort=[]

		ldir_year=os.listdir(os.path.join(self.root, self.host))
		ldir_year.sort()

		for dir_year in ldir_year:
			if dir_year=="current" or dir_year=="new": continue
			ldir_month=os.listdir(os.path.join(self.root, self.host, dir_year))
			ldir_month.sort()
			for dir_month in ldir_month:
				ldir_day=os.listdir(os.path.join(self.root, self.host, dir_year, dir_month))
				ldir_day.sort()
				for dir_day in ldir_day:
					ldir=os.listdir(os.path.join(self.root, self.host, dir_year, dir_month, dir_day))
					ldir.sort()
					for dir in ldir:
						try:
							print os.path.join([dir_year, dir_month, dir_day, dir]), os.readlink(os.path.join(self.root, self.host, "current"))
							if os.path.join([dir_year, dir_month, dir_day, dir]) == os.readlink(os.path.join(self.root, self.host, "current")):
								print "x",os.path.join([dir_year, dir_month, dir_day, dir])
								continue
						except: continue

						try:
							s=os.stat(os.path.join(self.root, self.host, dir_year, dir_month, dir_day, dir))
							if s[-2] < (self.now-(self.keep*24*60*60)):
								print "b",os.path.join(self.root, self.host, dir_year, dir_month, dir_day, dir)
								bort.append(os.path.join(self.root, self.host, dir_year, dir_month, dir_day, dir))
							else:
								print "k",os.path.join(self.root, self.host, dir_year, dir_month, dir_day, dir)
						except: pass
		
		if len(bort) > 0:
			if os.spawnvp(os.P_WAIT, "rm", ["rm", "-r"]+bort):
				print "error deleting,", bort

		return True

	def sync(self):
		new=os.path.join(self.root, self.host, "new")
		current=os.path.join(self.root, self.host, "current")

		print "running rsync on host", self.host, "with sourcename", self.sourcename
		try:
			ret_val=os.spawnvpe(os.P_WAIT, "rsync", ["rsync", "--archive", "--delete", "--numeric-ids", "--hard-links", "--sparse", "--link-dest="+current, self.host+"::"+self.sourcename+"/", new], { "USER": self.user, "RSYNC_PASSWORD": self.password } )
		except:
			ret_val=1

		if ret_val > 0:
			print "cleanup"
			os.spawnvp(os.P_WAIT, "rm", ["rm", "-r", new])
			sys.exit(2)

		stime=time.time()
		dirbase='/'.join([str(de).zfill(2) for de in time.localtime(stime)[0:3]])
		dir=':'.join([str(de).zfill(2) for de in time.localtime(stime)[3:6]])

		try:
			os.makedirs(os.path.join(self.root, self.host, dirbase))
		except OSError, oe:
			if oe.errno != 17:
				raise

		os.utime(new, (stime, stime))
		os.rename(new, os.path.join(self.root, self.host, dirbase, dir))

		try:
			os.remove(current)
		except: pass
		os.symlink(os.path.join(dirbase, dir), current)


if __name__ == "__main__":
	main()
