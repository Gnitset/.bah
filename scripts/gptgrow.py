#! /usr/bin/env python

# Program to grow a single EFI GPT partition (i.e. totally alone) to fill the disk.
# Only moves the end, this will not copy all your data.
# Will update beginning and end table(s) of given files.

from struct import pack, unpack
from binascii import crc32

class Gpt:
  def __init__(self, filename):
    self.file=file(filename, "rb+")
    self.file.seek(512)
    if self.file.read(8) == "EFI PART":
      self.headeroffset=512
      self.parseheader()
      assert self.tableoffset==1024
      print "GPT for beginning of disk found."
    else:
      self.file.seek(-512,2)
      self.headeroffset=self.file.tell()
      self.parseheader()
      print "Backup GPT for end of disk found."
    self.readpartitions()
    self.checkcrcs()
    #print "CRC check passed!"

  def parseheader(self):
    self.file.seek(self.headeroffset)
    header=self.file.read(512)
    signature, revision, headersize, headercrc, primaryheaderlba, backupheaderlba, \
	    firstdatalba, lastdatalba, diskguid, partitiontablelba, partitionentrycount, \
	    partitionentrysize, partitionarraycrc = unpack(
	    "<8sIIi4xQQ" +
	    "QQ16sQI" +
	    "Ii",  header[:92])
    assert signature=="EFI PART"
    assert revision==0x00010000
    assert headersize==92
    assert partitionentrysize==128
    #print primaryheaderlba, backupheaderlba, lastdatalba, partitiontablelba
    # For locating partition entries
    self.headersize=headersize
    self.primaryheaderlba=primaryheaderlba
    self.backupheaderlba=backupheaderlba
    self.partitiontablelba=partitiontablelba
    # Turns out we can figure that out here.
    self.tableoffset=self.headeroffset+512*(self.partitiontablelba-self.primaryheaderlba)
    # For knowing their size
    self.partitionentrysize=partitionentrysize
    self.partitionentrycount=partitionentrycount
    # For doing our work
    self.lastdatalba=lastdatalba
    self.header=header
    self.headercrc=headercrc
    self.partitionarraycrc=partitionarraycrc

  def readpartitions(self):
    self.file.seek(self.tableoffset)
    self.partitiontable=self.file.read(self.partitionentrysize*self.partitionentrycount)

  def checkcrcs(self):
    assert self.partitionarraycrc == crc32(self.partitiontable), "Partition array CRC does not match."
    assert self.headercrc == crc32(self.header[:16]+'\0\0\0\0'+self.header[20:self.headersize]), "GPT header CRC does not match."

  def fixcrcs(self):
    self.partitionarraycrc = crc32(self.partitiontable)
    self.header = self.header[:88] + pack('<i', self.partitionarraycrc) + self.header[88+4:]
    self.headercrc = crc32(self.header[:16]+'\0\0\0\0'+self.header[16+4:self.headersize])
    self.header = self.header[:16] + pack('<i', self.headercrc) + self.header[16+4:]
    self.checkcrcs()

  def save(self):
    assert len(self.header)==512
    self.file.seek(self.headeroffset)
    self.file.write(self.header)
    self.file.seek(self.tableoffset)
    self.file.write(self.partitiontable)

  def growpartition(self):
    partcount=0
    for partoffset in range(0, len(self.partitiontable), self.partitionentrysize):
      part=self.partitiontable[partoffset:partoffset+self.partitionentrysize]
      typeguid, partitionguid, startlba, endlba, attributes, name = unpack(
           "<16s16sQQQ72s", part)
      if typeguid=='\0'*16:
        # Unused partition entry, skip it
	continue
      assert endlba<=self.lastdatalba
      partcount+=1
      foundpart=partoffset
    assert partcount==1
    # foundpart now has the offset of the only partition
    part=self.partitiontable[foundpart:foundpart+self.partitionentrysize]
    typeguid, partitionguid, startlba, endlba, attributes, name = unpack(
         "<16s16sQQQ72s", part)
    print "Found exactly one partition, size %s GB."%((endlba-startlba+1)*512/1000000000.)
    newendlba=self.lastdatalba
    print "Growing to %s GB."%((newendlba-startlba+1)*512/1000000000.)
    # Edit it in
    newpart = part[:40] + pack('<Q', newendlba) + part[40+8:]
    assert len(newpart)==len(part)
    # And store it in the table
    self.partitiontable = self.partitiontable[:foundpart] + newpart + \
          self.partitiontable[foundpart+self.partitionentrysize:]
    # Fix up the CRCs
    self.fixcrcs()

if __name__=='__main__':
  from sys import argv
  for arg in argv[1:]:
    gpt=Gpt(arg)
    gpt.growpartition()
    gpt.save()

