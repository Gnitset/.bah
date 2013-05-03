/*
 * -----------------------------------------------------------------------------
 * "THE BEER-WARE LICENSE" (Revision 42):
 * <gnitset@servern.info> wrote this file. As long as you retain this notice you
 * can do whatever you want with this stuff. If we meet some day, and you think
 * this stuff is worth it, you can buy me a beer in return - Klas Meder Boqvist
 * -----------------------------------------------------------------------------
 */

#include <sys/time.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>

char **args;

void sigalrm(int signum) {
        int cpid;
        cpid = fork();
        if(cpid == -1) { // fork failed
                exit(3);
        } else if(cpid == 0) { // child
                execv(args[2], args+2);
        }
}

int main(int argc, char **argv) {
        struct itimerval a;
        int tbe;

        args = argv; // save argv for signal handler
        tbe = atoi(argv[1]); // get interval from args
        a.it_interval.tv_sec = tbe; // set interval
        a.it_interval.tv_usec = 0;
        a.it_value.tv_sec = 1; // run the program the first time after 1s
        a.it_value.tv_usec = 0;

        if(argc <= 1 || tbe <= 0) { // verify that we have a valid interval and know what program to run
                printf("%s <time between execution in s> <full path to cmd> <args to cmd>...\n", argv[0]);
                return 1;
        }

        signal(SIGALRM, sigalrm); // enable signal handler
        setitimer(ITIMER_REAL, &a, NULL); // request signal at the specified interval

        while(pause()); // wait for signals forever

        printf("BUG\n"); // this shouldn't happen
        return 2;
}
