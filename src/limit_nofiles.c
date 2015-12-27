/*
 * Simple program to check ulimit nofile on a running process in OpenBSD
 *
 * gcc -O2 -pipe -lkvm -o limit_nofiles limit_nofiles.c
 *
 */

#include <sys/param.h>
#include <sys/sysctl.h>
#include <sys/user.h>
#include <kvm.h>
#include <fcntl.h>

int main(int argc, char **argv) {
	if(argc != 2) {
		printf("Usage: %s <pid>\n", argv[0]);
		return 1;
	}

	struct kinfo_proc *kp;
	struct plimit pl;
	kvm_t *kt;
	int foo=0;

	kt = kvm_open(NULL, NULL, NULL, O_RDONLY, "Error: ");

	kp = kvm_getprocs(kt, KERN_PROC_PID, atoi(argv[1]), sizeof(*kp), &foo);

	kvm_read(kt, kp->p_limit, &pl, sizeof(pl));

	printf("Current limit: %i\nHard limit: %i\n",
		pl.pl_rlimit[RLIMIT_NOFILE].rlim_cur,
		pl.pl_rlimit[RLIMIT_NOFILE].rlim_max);
	return 0;
}
