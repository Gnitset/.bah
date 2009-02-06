#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char **argv) {
	int i;
	long blocks=17, blocksize=65536;
	char *endptr;
        char *randdata;
        ssize_t res=0;

	/* Check that stdin and stdout are not terminals */
	if (isatty(fileno(stdin)) || isatty(fileno(stdout))) res=1;
	/* Read block size and count arguments */
	if (argc>=2) {
	  blocksize=strtol(argv[1], &endptr, 0);
	  if (argv[1]==endptr || endptr[0]!=0) res=1;
	}
	if (argc>=3) {
	  blocks=strtol(argv[2], &endptr, 0);
	  if (argv[2]==endptr || endptr[0]!=0) res=1;
	}
	/* Check for unknown arguments */
	if (argc>3) res=1;
	if (res) {
	  fprintf(stderr, "Usage: %s [blocksize {blockcount]] < /dev/urandom > /dev/st0\n",
	      argv[0]);
	  return 1;
	}
	randdata=malloc(blocks*blocksize);
	if (randdata==0) {
	  perror(NULL);
	  return 2;
	}
	if (setvbuf(stdout, NULL, _IONBF, 0)) {
	  perror("Couldn't set stdout nonbuffered");
	  return 2;
	}
	res=fread(randdata, blocksize, blocks, stdin);
	if (res != blocks) {
	  perror("Reading random data");
	  return 2;
	}

	fprintf(stderr, "%s: Repeating %ld blocks of %ld bytes\n",
	    argv[0], blocks, blocksize);

	i=0;
	do {
	  res = fwrite(randdata+(blocksize*i), blocksize, 1, stdout);
	  i=(i+1)%blocks;
        } while (res==1);
	perror("Writing data");
	return 0;
}
