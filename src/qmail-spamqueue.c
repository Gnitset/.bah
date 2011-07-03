#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <sys/wait.h>
#include <stdio.h>
#include <ctype.h>
#include <time.h>
#include "strlcpy.c"

#define REAL_QMAILQUEUE   "/var/qmail/bin/qmail-queue"
#define SPAMC_PATH        "/usr/bin/spamc"
#define EZMLM_ISSUBN_PATH "/usr/bin/ezmlm-issubn"
#define DEFAULT_LIMIT     (512 * 1024)

#define FAIL_DISK     53
#define FAIL_MEM      51
#define FAIL_BUG      81
#define FAIL_SPAM     31
#define FAIL_ENVELOPE 91

static char envelope[4096];
static int  envelope_size = 0;
static char *user = NULL;

static pid_t qqueue_pid = 0;
static int   qq_env [2];
static int   qq_mail[2];

static pid_t spamc_pid;
static int   spamc_in [2] = {0, 0};
static int   spamc_out[2] = {0, 0};

static char *mail;
static int  mail_size = 0;
static int  max_mail_size = DEFAULT_LIMIT;

static int  spamexit = -1;

static void pass_through(const char *reason);

/* Basically stolen from qmail-spamc. */
static void build_spamc_argv(char **options) {
	int  opt = 0;
	char *val;

    /* create the array of options */
    options[opt++] = SPAMC_PATH;            /* set zeroth argument */
    options[opt++] = "-E";	/* We rely on the exit-code */
    if ((val = getenv("SPAMDSOCK")) != NULL) {   /* Unix Domain Socket path */
        options[opt++] = "-U";
        options[opt++] = val;
    }
    if ((val = getenv("SPAMDHOST")) != NULL) {   /* remote spamd host name */
        options[opt++] = "-d";
        options[opt++] = val;
    }
    if ((val = getenv("SPAMDPORT")) != NULL) {   /* remote spamd port number */
        options[opt++] = "-p";
        options[opt++] = val;
    }
    if ((val = getenv("SPAMDSSL")) != NULL) {    /* use ssl for spamc/spamd */
        options[opt++] = "-S";
    }
    if ((val = getenv("SPAMDLIMIT")) != NULL) {  /* message size limit */
        options[opt++] = "-s";
        options[opt++] = val;
    }
    if ((val = getenv("SPAMDUSER")) != NULL) {   /* spamc user configuration */
        if (!user) user = val;
    }
    if (user) {
        options[opt++] = "-u";
        options[opt++] = user;
    }
    options[opt] = NULL;                 /* terminate argument list */
}

/* Like fgets(3), except it discards the rest of the line on overflow,
 * doesn't include the LF and returns the number of characters put into the
 * buffer.
 */
static int better_fgets(char *buf, int len, FILE *fh) {
	char *p = buf;
	while (42) {
		int c = getc(fh);
		if (c == -1) break;
		if (c == '\n') break;
		if (len > 1) {
			*p++ = c;
			len--;
		}
	}
	*p = '\0';
	return p - buf;
}

static int cmpaddr(const char *addr, const char *pat) {
	int a, p;

	while (42) {
		a = *addr++;
		p = *pat++;
		if (p == '*') {
			if (a == '@') {
				addr--;
			} else {
				addr = strchr(addr, '@');
				if (!addr) return *pat == '\0';
			}
		} else {
			if (tolower(p) != tolower(a)) return 0;
		}
		if (!a) return !p;
	}
}

static char *addr2user(const char *addr) {
	FILE        *list;
	static char buf[128];
	const char  *domain;
	int         len;

	domain = strchr(addr, '@');
	if (!domain) domain = addr;
	list = fopen("/var/qmail/users/spam", "r");
	if (!list) return NULL;
	while ((len = better_fgets(buf, sizeof(buf), list))) {
		char *sep = strchr(buf, ':');
		if (buf[0] == '#' || !sep) continue;
		*sep++ = '\0';
		if (cmpaddr(addr, buf)) {
			fclose(list);
			if (*sep == '*') {
				strlcpy(buf, addr, sizeof(buf));
				sep = strchr(buf, '@');
				if (sep) *sep = '\0';
				sep = strchr(buf, '-');
				if (sep) *sep = '\0';
				return strdup(buf);
			}
			return strdup(sep);
		}
	}
	fclose(list);
	return NULL;
}

static void reject_list(char *dir) {
	pid_t pid;
	int   status;

	// fprintf(stderr, "Checking reject in %s\n", dir);
	pid = fork();
	if (pid == -1) _exit(FAIL_MEM);
	if (pid == 0) {
		char *args[] = {EZMLM_ISSUBN_PATH, dir,
		                ".", "digest", "allow", "mod", NULL};
		execv(EZMLM_ISSUBN_PATH, args);
		_exit(111);
	}
	if (waitpid(pid, &status, 0) != pid) _exit(FAIL_BUG);
	if (!WIFEXITED(status)) _exit(FAIL_BUG);
	if (WEXITSTATUS(status) == 99) {
		_exit(spamexit);
	}
}

static void check_list(const char *addr) {
	FILE         *list;
	static char  buf[128];
	const char   *adomain;
	unsigned int alocallen;
	int          len;

	// fprintf(stderr, "Checking list for %s\n", addr);
	adomain = strchr(addr, '@');
	alocallen = adomain - addr;
	if (!adomain || !alocallen) return;
	list = fopen("/var/qmail/users/lists", "r");
	if (!list) return;
	while ((len = better_fgets(buf, sizeof(buf), list))) {
		char *dir = strchr(buf, ':');
		if (buf[0] == '#' || !dir) continue;
		*dir++ = '\0';
		char *domain = strchr(buf, '@');
		if (domain && !strcmp(domain, adomain)) {
			unsigned int locallen = domain - buf;
			if (locallen && locallen <= alocallen
			 && (addr[locallen] == '@' || addr[locallen] == '-')
			 && !memcmp(addr, buf, locallen)) {
				// Domain matches, local part in list is no
				// longer than local part in address, they
				// match up to that length, and the left
				// over part is empty or begins with "-".
				// IOW this will be handled by that list.
				fclose(list);
				const char *rest = addr + locallen;
				if (!memcmp(rest, "-owner@", 7)
				 || !memcmp(rest, "-subscribe", 10)
				 || !memcmp(rest, "-sc.", 4)
				 || !memcmp(rest, "-uc.", 4)
				 || !memcmp(rest, "-help@", 6)
				 || !memcmp(rest, "-info@", 6)
				 || !memcmp(rest, "-faq@", 5)
				 || !memcmp(rest, "-return-", 8)) {
					// Never reject for these
					return;
				}
				reject_list(dir);
				return;
			}
		}
	}
	fclose(list);
}

static void read_envelope(void) {
	char *addrp;
	char *addrp_end;
	int  first = 1;
	int  addrcount = 0;
	char *to_addr = NULL;

	envelope_size = read(1, envelope, sizeof(envelope) - 2);
	if (envelope_size <= 0) _exit(FAIL_ENVELOPE);
	envelope[sizeof(envelope) - 2] = '\0';
	envelope[sizeof(envelope) - 1] = '\0';
	addrp = envelope;
	addrp_end = envelope + envelope_size;
	if (*addrp != 'F') _exit(FAIL_ENVELOPE);
	if (setenv("SENDER", addrp + 1, 1)) _exit(FAIL_MEM);
	addrp += strlen(addrp) + 1;
	if (addrp >= addrp_end) _exit(FAIL_ENVELOPE);
	if (*addrp != 'T') _exit(FAIL_ENVELOPE);

	while (*addrp == 'T') { /* More recipients */
		char *other_user;

		to_addr = addrp + 1;
		addrp += strlen(addrp) + 1;
		if (addrp >= addrp_end) _exit(FAIL_ENVELOPE);
		other_user = addr2user(to_addr);
		if (first) {
			user = other_user;
			first = 0;
		}
		if (!other_user) {
			user = NULL;
		} else if (user) {
			if (strcmp(user, other_user)) user = NULL;
		}
		addrcount++;
	}
	if (*addrp != '\0') {
		_exit(FAIL_ENVELOPE);
	}
	// Only one address, let's check if it's a list.
	if (addrcount == 1 && spamexit != -1) check_list(to_addr);
}

/* Fork off qmail-queue */
static void run_qqueue(void) {
	if (pipe(qq_env)) _exit(FAIL_MEM);
	if (pipe(qq_mail)) _exit(FAIL_MEM);
	qqueue_pid = fork();
	if (qqueue_pid == -1) _exit(FAIL_MEM);
	if (qqueue_pid == 0) {
		char *options[] = {REAL_QMAILQUEUE, 0};

		if (dup2(qq_mail[0], 0) == -1) _exit(FAIL_BUG);
		if (dup2(qq_env [0], 1) == -1) _exit(FAIL_BUG);
		close(qq_mail[0]);
		close(qq_mail[1]);
		close(qq_env [0]);
		close(qq_env [1]);
		if (spamc_in [1]) close(spamc_in [1]);
		if (spamc_out[0]) close(spamc_out[0]);
		execv(options[0], options);
		_exit(FAIL_BUG);
	}
	close(qq_mail[0]);
	close(qq_env [0]);
}

/* Fork off spamc */
static void run_spamc(void) {
	if (pipe(spamc_in)) _exit(FAIL_MEM);
	if (pipe(spamc_out)) _exit(FAIL_MEM);
	spamc_pid = fork();
	if (spamc_pid == -1) pass_through("failed to fork spamc");
	if (spamc_pid == 0) {
		char *options[16];

		build_spamc_argv(options);
		if (dup2(spamc_in [0], 0) == -1) _exit(FAIL_BUG);
		if (dup2(spamc_out[1], 1) == -1) _exit(FAIL_BUG);
		close(spamc_in [0]);
		close(spamc_in [1]);
		close(spamc_out[0]);
		close(spamc_out[1]);
		execv(options[0], options);
		_exit(FAIL_BUG);
	}
	close(spamc_in [0]);
	close(spamc_out[1]);
}

static void qq_done(void) {
	int status;

	close(qq_mail[1]);
	close(qq_env [1]);
	if (waitpid(qqueue_pid, &status, 0) != qqueue_pid) _exit(FAIL_BUG);
	if (!WIFEXITED(status)) _exit(FAIL_BUG);
	_exit(WEXITSTATUS(status));
}

static void qq_write_envelope(void) {
	int  len;
	char buf[4096];

	close(qq_mail[1]);
	len = write(qq_env[1], envelope, (size_t)envelope_size);
	if (len != envelope_size) qq_done();
	while ((len = read(1, buf, sizeof(buf))) > 0) {
		if (write(qq_env[1], buf, (size_t)len) != len) qq_done();
	}
	if (len < 0) qq_done();
}

static void write_header(const char *fmt, const char *reason, int extra_fields) {
	char   buf[1024];
	int    len;

	if (extra_fields) {
		char   hostname[256];
		char   date[256];
		time_t t;
		FILE   *me;

		*hostname = '\0';
		if ((me = fopen("/var/qmail/control/me", "r"))) {
			len = better_fgets(hostname, sizeof(hostname), me);
			fclose(me);
		}
		if (!*hostname) strcpy(hostname, "UNKNOWN");
		t = time(NULL);
		if (!strftime(date, sizeof(date), "%F %T -0000", gmtime(&t))) *date = '\0';
		snprintf(buf, sizeof(buf), fmt, hostname, date, reason);
	} else {
		snprintf(buf, sizeof(buf), fmt, reason);
	}
	len = strlen(buf);
	if (write(qq_mail[1], buf, (size_t)len) != len) qq_done();
}

static void pass_through(const char *reason) {
	/* If qmail-queue is already started, we stop that one
	 * (it may have gotten a partial mail as input) */
	if (qqueue_pid) {
		int status;
		close(qq_mail[1]);
		close(qq_env [1]);
		if (waitpid(qqueue_pid, &status, 0) != qqueue_pid) _exit(FAIL_BUG);
	}

	run_qqueue();
	/* Add a header saying that we passed it through */
	write_header("X-Spam-Queue-Fail: Passed through without filtering on\n  %s %s\n  (%s)\n", reason, 1);
	/* Write the mail we have read */
	if (mail_size) {
		if (write(qq_mail[1], mail, (size_t)mail_size) != mail_size) qq_done();
	}
	/* If we haven't read the whole mail, continue copying from fd 0 */
	if (!mail || (mail_size == max_mail_size)) {
		char buf[4096];
		int  len;

		while ((len = read(0, buf, sizeof(buf))) > 0) {
			if (write(qq_mail[1], buf, (size_t)len) != len) qq_done();
		}
	}
	qq_write_envelope();
	qq_done();
}

int main(void) {
	int     spamc_out_len = 0;
	char    buf[4096];
	ssize_t len;
	int     status;
	char    *val;

	if ((val = getenv("SPAMDLIMIT"))) {
		max_mail_size = atoi(val);
		if (max_mail_size <= 0) max_mail_size = DEFAULT_LIMIT;
	}
	if ((val = getenv("QSPAMEXIT"))) {
		spamexit = atoi(val);
	}

	mail = malloc((size_t)max_mail_size);
	/* Pass it through if we're low on memory */
	if (!mail) pass_through("out of mem");
	while ((len = read(0, mail + mail_size, (size_t)(max_mail_size - mail_size))) > 0) {
		mail_size += len;
		/* Pass it through if it's too big */
		if (mail_size == max_mail_size) pass_through("mail too big");
	}
	/* Fail if there was a problem reading the mail */
	if (len < 0) _exit(FAIL_BUG);
	if (!mail_size) _exit(FAIL_BUG);

	read_envelope();
	run_spamc();
	run_qqueue();

	/* Feed the mail to spamc */
	len = write(spamc_in[1], mail, (size_t)mail_size);
	/* Pass the mail through if this fails */
	if (len != mail_size) pass_through("spamc write failure");
	close(spamc_in[1]);

	write_header("X-Spam-Queue: Filtered for <%s>\n", user ? user : "DEFAULT", 0);
	/* Copy the mail from spamc to qmail-queue */
	while ((len = read(spamc_out[0], buf, sizeof(buf))) > 0) {
		spamc_out_len += len;
		if (write(qq_mail[1], buf, (size_t)len) != len) {
			/* Problem writing to spamc -> pass original through */
			pass_through("spamc read failure");
		}
	}
	/* Pass the original message through if we had a read error from spamc. */
	if (len < 0) pass_through("spamc returned incomplete mail");
	/* Or if we didn't get at least as much back from spamc as we put in */
	if (spamc_out_len < mail_size) pass_through("spamc returned short mail");

	if (waitpid(spamc_pid, &status, 0) != spamc_pid) _exit(FAIL_BUG);
	if (!WIFEXITED(status)) _exit(FAIL_BUG);
	switch (WEXITSTATUS(status)) {
		case 1:
			if (spamexit != -1) _exit(spamexit);
			break;
		case 0:
			break;
		default:
			_exit(FAIL_BUG);
			break;
	}

	/* Ok, this is not spam, and we have copied the message to qmail-queue without problems */
	/* Now we transfer the envelope */
	qq_write_envelope();
	/* And we're done. */
	qq_done();
}
