#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/time.h>

#define RAND_SIZE 1114113
#define BS 65536
#define RAND_BLOCK (RAND_SIZE / BS)
#define OUT_EVERY_NO_BLOCK 2048

int main(int argc, char **argv) {
	char randdata[RAND_SIZE];
	int fd, i;
	ssize_t res;
	struct timeval start, now, last;

	fd = open("/dev/urandom", O_RDONLY);
	res = read(fd, randdata, RAND_SIZE);
	close(fd);

	if( res != RAND_SIZE || res == -1 ) {
		return 3;
	}

	fd = open("/dev/st0", O_WRONLY);
	i=0;
	gettimeofday(&start, NULL);
	gettimeofday(&last, NULL);

	while(42) {
		res = write(fd, &randdata[ ( i % RAND_BLOCK ) * BS ], BS);
		if( res != BS || res == -1 ) {
			return 4;
		}
		if( ( i % OUT_EVERY_NO_BLOCK ) == OUT_EVERY_NO_BLOCK-1 ) {
			gettimeofday(&now, NULL);
			printf("Tid start: %i:%i. ", (int)start.tv_sec, (int)start.tv_usec );
			fflush(stdout);
			printf("Tid nu: %i:%i. ", (int)now.tv_sec, (int)now.tv_usec );
			fflush(stdout);
			printf("Data överfört: %i block, %li kB. ", i, (long int)(( i * BS ) / 1024) );
			fflush(stdout);
			printf("Diff1: %is. Diff2: %is %i MB. ", ( (int)now.tv_sec - (int)start.tv_sec ), ( (int)now.tv_sec - (int)last.tv_sec ), BS * OUT_EVERY_NO_BLOCK/1024/1024);
			fflush(stdout);
			printf("kB/s1: %i. kB/s2: %i.", (BS*i/1024)/(int)(now.tv_sec-start.tv_sec), (BS*OUT_EVERY_NO_BLOCK/1024)/(int)(now.tv_sec-last.tv_sec) );
//			printf("kB/s1: %i. kB/s2: %i. \n", ((i*BS)/1024/((int)now.tv_sec-(int)start.tv_sec)), ( ( i * BS ) / 1024 / ( (int)now.tv_sec - (int)start.tv_sec ) ) );
			printf("\n");
			fflush(stdout);
			gettimeofday(&last, NULL);
		}
		i++;
	}
}
