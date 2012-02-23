#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <signal.h>

int cpid;

void sighandler(int signum) {
	kill(cpid, SIGKILL);
	exit(1);
}

int main(int argc, char** argv) {
	int timeout=10;
	int cret=0;

	cpid=fork();
	if(cpid==-1) { // fork failed
		exit(3);
	} else if(cpid==0) { // child
		execl("/bin/bash", "bash", (char *) NULL);
	} else { // mother
		signal(SIGALRM, sighandler);
		signal(SIGTERM, sighandler);
		signal(SIGKILL, sighandler);
		alarm(timeout); // ask for SIGALRM after timeout seconds
		waitpid(cpid, &cret, 0); // wait and see if child exits early
		exit(2);
	}
	exit(4);
}
