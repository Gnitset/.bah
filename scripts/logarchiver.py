#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#
# Author: Klas Meder Boqvist <klas.meder.boqvist@bwin.org>
# Last Update: 2010-12-16
# Mission: Archive logfiles that is rolled by applications
# Recomended default flags: -fq

import os
import sys
import gzip
import datetime
import optparse

class ArchiveException:
	def __init__(self, msg, file):
		self.msg=msg
		self.file=file

def archive(filename, archivepath):
	if not os.path.exists(filename):
		raise ArchiveException("source missing", filename)

	head, tail=os.path.split(filename)
	target="%s.gz"%os.path.join(head, archivepath, tail)
	if os.path.exists(target):
		s=os.stat(target)
		if not s.st_size:
			raise ArchiveException("target exists", target)
	
	if not os.path.isdir(os.path.join(head, archivepath)):
		os.mkdir(os.path.join(head, archivepath))

	gzfile=gzip.GzipFile(target, "wb", 6)
	gzfile.writelines(open(filename))
	os.fsync(gzfile.fileno())
	gzfile.close()

	s=os.stat(target)
	if not s.st_size:
		raise ArchiveException("target is empty", target)

	s=os.stat(filename)
	os.utime(target, (s.st_atime, s.st_mtime))
	os.unlink(filename)

def file_opened(path):
	if not os.path.isdir("/proc"):
		return False
	path=os.path.realpath(os.path.normpath(os.path.join(os.getcwd(),path)))
	for p in os.listdir("/proc/"):
		if not p.isdigit(): continue
		d = "/proc/%s/fd/" % p
		try:
			for fd in os.listdir(d):
				f = os.readlink(d+fd)
				if path == f:
					return True
		except OSError:
			pass
	return False

def p_split(path):
	head, tail=os.path.split(path)
	if head and head!=path:
		return p_split(head)+[tail]
	else:
		return [tail]

def f_age(filename):
	now=datetime.datetime.now()
	s=os.stat(filename)
	t=datetime.datetime.fromtimestamp(s.st_mtime)
	delta=now-t
	return (filename, delta.days)

def walk(path, maxdepth=0, archivedir="archive"):
	depth=0
	if maxdepth:
		maxdepth=len(p_split(path))+maxdepth

	logs, archive=list(), list()
	for root, dirs, files in os.walk(path):
		psplit=p_split(root)
		depth=len(psplit)
		files=[f_age(path) for path in [os.path.join(root,f) for f in files]
					if os.path.isfile(path) and not file_opened(path)]
		if psplit[-1] == archivedir:
			archive.extend(files)
		else:
			logs.extend([f for f in files if not f[0].endswith("log") and not f[0].endswith(".gz")])
		if maxdepth and depth >= maxdepth:
			del dirs[:]
	return (logs, archive)

if __name__ == "__main__":
	parser=optparse.OptionParser("usage: %prog [options]")
	parser.add_option("-p", "--logs-path", dest="logspath", default="/var/log/ongame", help="name of the direcory for the logs")
	parser.add_option("-a", "--archive-dir", dest="archivedir", default="archive", help="name of the direcory for the archive")
	parser.add_option("--max-days", dest="maxdays", default=90, type="int", help="max days to keep logs")
	parser.add_option("--min-days", dest="mindays", default=5, type="int", help="min days since modified before compressing")
	parser.add_option("-n", "--dry-run", dest="dryrun", default=False, action="store_true", help="dont move or touch anything")
	parser.add_option("-f", "--force", dest="force", default=False, action="store_true", help="disables questions")
	parser.add_option("-q", "--quiet", dest="verbose", default=True, action="store_false", help="disables output")
	opts, rest=parser.parse_args(sys.argv[1:])

	if opts.verbose:
		print "logs-path=%s\narchive-dir=%s\nmin-days=%s\nmax-days=%s\ndry-run=%s\n"%(opts.logspath, opts.archivedir, opts.maxdays, opts.mindays, opts.dryrun)
	if not opts.force:
		print "OK? [y/N]"
		inp=sys.stdin.readline()
		if inp.lower().strip() != "y":
			sys.exit(3)

	logs, archives=walk(opts.logspath, 0, opts.archivedir)
	logfiles=[log for log in logs if log[1]>=opts.mindays]
	archivedfiles=filter(lambda x: x[1]>=opts.maxdays, archives)

	if opts.verbose: print "files to compress", len(logfiles)
	if opts.verbose: print "files to remove", len(archivedfiles)

	for f,days in logfiles:
		if opts.verbose:
			if opts.dryrun:
				print "NOT",
			print "Archiving %i %s"%(days, f)
		if opts.dryrun:
			continue
		try:
			archive(f, opts.archivedir)
		except ArchiveException, ae:
			print ae.msg

	for f,days in archivedfiles:
		if opts.verbose:
			if opts.dryrun:
				print "NOT",
			print "Removing %i %s"%(days, f)
		if opts.dryrun:
			continue
		if not opts.force:
			print "OK? [y/N]"
			inp=sys.stdin.readline()
			if inp.lower().strip() != "y":
				continue
		os.unlink(f)




