#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, time

try:
	from kbackup_conf import root, lockfile, sources, debug
except:
	print """Unable to import required conf parameters from kbackup_conf.py

examplefile:
#! /usr/bin/env python
# -*- coding: utf-8 -*-

root="/backup/data"
lockfile=".kbackup.lock"
sources={}

sources["host.domain.tld"]={ "interval": "h", "keep": 30, "user": "backup", "password": "ChangeMe", "map-uid": True }"""
	sys.exit(1)

if "--force" in sys.argv:
	for host in sources:
		sources[host]['interval']="f"

def main():
	retcode=0
	print time.asctime(time.localtime())
	try:
		os.stat(os.path.join(root,lockfile))
		print "lockfile exists"
		os.kill(int(open(os.path.join(root,lockfile)).read()), 0)
		print "and kbackup is still running"
		sys.exit(1)
	except OSError, e:
		if e.errno==3:
			print "but the process seems to be dead, removing pidfile"
			os.remove(os.path.join(root,lockfile))

	open(os.path.join(root, lockfile), "w").write(str(os.getpid()))

	for host in sources:
		try:
			print "starting backup of %s"%host
			kb=KBackup(root, host, sources[host], debug)
			if kb.eligable():
				kb.rotate()
				kb.sync()
				if debug:
					print host,"completed"
			else:
				print host,"not eligable"
		except e:
			print "Exception: %s"%str(e)
			retcode=1
		print time.asctime(time.localtime())

	os.remove(os.path.join(root,lockfile))
	sys.exit(retcode)

class KBackup():
	root=""
	host=""
	keep="7"
	user="backup"
	password=""
	now=0
	debug=False

	def __init__(self, root, host, conf, debug=False):
		self.now=time.time()
		self.root=root
		self.host=host
		self.debug=debug
		self.conf=conf
		try:
			assert conf["keep"] > 0
			self.keep=conf["keep"]
		except: pass
		try:
			self.user=conf["user"]
		except: pass
		try:
			self.password=conf["password"]
		except: pass
		try:
			self.last_backup=time.mktime(time.strptime(os.readlink(os.path.join(self.root, self.host, "current")), "%Y/%m/%d/%H:%M:%S"))
		except:
			self.last_backup=0
		try:
			os.mkdir(os.path.join(self.root, self.host))
		except OSError, oe:
			if oe.errno != 17:
				raise

	def eligable(self):
		now=time.time()
		if self.conf['interval'] == 'd':
			diff=((23*60)+30)*60			# sync after 23h and 30min
		elif self.conf['interval'] == 'h':
			diff=50*60				# sync after 50min
		else:
			diff=0					# always sync
		if self.last_backup+diff < now:
			return True
		else:
			return False

	def walkrm(self, dir, maxdepth=3, depth=0):
		for file in os.listdir(dir):
			path=os.path.join(dir,file)
			if os.path.isdir(path):
				if depth < maxdepth:
					self.walkrm(path, maxdepth, depth+1)
				try:
					os.rmdir(path)
				except OSError: pass

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
							if os.path.join(dir_year, dir_month, dir_day, dir) == os.readlink(os.path.join(self.root, self.host, "current")):
								if self.debug:
									print "x",os.path.join(self.root, self.host, dir_year, dir_month, dir_day, dir)
								continue
						# bug
						except: continue

						try:
							s=os.stat(os.path.join(self.root, self.host, dir_year, dir_month, dir_day, dir))
							if s.st_mtime < (self.now-(self.keep*24*60*60)):
								if self.debug:
									print "b",os.path.join(self.root, self.host, dir_year, dir_month, dir_day, dir)
								bort.append(os.path.join(self.root, self.host, dir_year, dir_month, dir_day, dir))
							else:
								if self.debug:
									print "k",os.path.join(self.root, self.host, dir_year, dir_month, dir_day, dir)
						except: pass
		
		if len(bort) > 0:
			if os.spawnvp(os.P_WAIT, "rm", ["rm", "-r"]+bort):
				sys.stderr.write("error deleting, %s\n"%bort)

		self.walkrm(os.path.join(self.root, self.host))

		return True

	def sync(self):
		new=os.path.join(self.root, self.host, "new")
		current=os.path.join(self.root, self.host, "current")

		if self.debug:
			print "running rsync on host", self.host
		try:
			if self.conf['map-uid']:
				ret_val=os.spawnvpe(os.P_WAIT, "rsync", ["rsync", "--archive", "--delete", "--numeric-ids", "--hard-links", "--sparse", "--link-dest="+current, self.host+"::backup/", new], { "USER": self.user, "RSYNC_PASSWORD": self.password } )
			else:
				ret_val=os.spawnvpe(os.P_WAIT, "rsync", ["rsync", "--archive", "--delete", "--hard-links", "--sparse", "--link-dest="+current, self.host+"::backup/", new], { "USER": self.user, "RSYNC_PASSWORD": self.password } )
		except:
			ret_val=1

		if ret_val > 0:
			print "cleanup"
			os.spawnvp(os.P_WAIT, "rm", ["rm", "-r", new])
			print self.host,"failed"

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

##for dirpath, dirnames, filenames in os.walk(rootdir):
##	try:
##		dirnames.remove('new')
##	except:	pass
##	dirnames.sort()
##	level=dirpath.count('/')-rootdir.count('/')
##	if level==3:
##		for dir in dirnames:
##			# do something to os.join(dirpath,dir) here
##		dirnames[:]=[]	# stop the walk
