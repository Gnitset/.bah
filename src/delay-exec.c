#include <unistd.h>
#include <stdlib.h>

int main(int argc, char **argv) {
	if (argc < 3) return 100;
	sleep((unsigned int)atoi(argv[1]));
	execv(argv[2], argv + 2);
	return 111;
}
