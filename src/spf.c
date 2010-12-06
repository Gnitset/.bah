/*
 * gcc spf.c -o spf -lspf2 -lpthread -lresolv -Wall -I/usr/include/spf2
 *
 * Copyright (C) 2003-2005 Pawel Foremski <pjf@asn.pl>
 *
 * This program is free software; you can redistribute it and/or 
 * modify it under the terms of the GNU General Public License 
 * as published by the Free Software Foundation; either 
 * version 2 of the License, or (at your option) any later 
 * version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software Foundation,
 * Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 *
 */

#include <stdlib.h>
#include <stdio.h>
/* This is needed because libspf2 doesn't include or abstract enough. */
#include <netinet/in.h>
#include "spf.h"

void block(SPF_response_t *spf_response)
{
	const char *explain;
	explain = SPF_response_get_smtp_comment(spf_response);

	if (explain) {
		printf("E550 %s (#5.7.1)\n", explain);
		fprintf(stderr, "spf: blocked with: %s\n", explain);
	} else {
		printf("E550 Blocked with SPF (#5.7.1)\n");
		fprintf(stderr, "spf: WARNING: no explanation for blocked mail!\n");
	}
}

int main()
{
	int spf;
	char *me, *remote, *helo, *sender, *spf_env;
	const char *header;
	SPF_server_t *spf_server;
	SPF_request_t *spf_request;
	SPF_response_t *spf_response;

	/**
	 * env variables
	 **/
	if (getenv("RELAYCLIENT") ||              /* known user */
	    !(spf_env = getenv("SPF"))) return 0; /* plugin disabled */

	spf = atoi(spf_env);
	if (spf < 1 || spf > 6) {
		if (spf > 6)
			fprintf(stderr, "spf: ERROR: invalid value (%d) of SPF variable\n", spf);
		return 0;
	}

	remote  = getenv("TCPREMOTEIP"); 
	me      = getenv("TCPLOCALHOST");
	if (!me) me = getenv("TCPLOCALIP");
	if (!remote || !me) { /* should never happen */
		fprintf(stderr, "spf: ERROR: can't get tcpserver variables\n");
		if(!remote) fprintf(stderr, "spf: can't read TCPREMOTEIP\n");
		else fprintf(stderr, "spf: can't read TCPLOCALHOST nor TCPLOCALIP\n");
		return 0;
	}

	sender = getenv("SMTPMAILFROM");
	if (!sender) { /* should never happen */
		fprintf(stderr, "spf: ERROR: can't get envelope sender address\n");
		fprintf(stderr, "spf: can't read SMTPMAILFROM\n");
		return 0;
	}
	if (!*sender) return 0; /* null sender mail */

	helo = getenv("SMTPHELOHOST");

	/**
	 * SPF
	 **/
	spf_server = SPF_server_new(SPF_DNS_CACHE, 0);
	if (!spf_server) {
		fprintf(stderr, "spf: ERROR: can't initialize libspf2\n");
		return 0;
	}
	spf_request = SPF_request_new(spf_server);
	if (!spf_request) {
		fprintf(stderr, "spf: ERROR: can't initialize libspf2\n");
		return 0;
	}

	if (SPF_request_set_ipv4_str(spf_request, remote)) {
		fprintf(stderr, "spf: can't parse TCPREMOTEIP\n");
		return 0;
	}

	SPF_server_set_rec_dom(spf_server, me);

	if (helo) SPF_request_set_helo_dom(spf_request, helo);
	SPF_request_set_env_from(spf_request, sender);

	/* Perform actual lookup */
	SPF_request_query_mailfrom(spf_request, &spf_response);

	/* check whether mail needn`t to be blocked */
	switch (SPF_response_result(spf_response)) {
		case SPF_RESULT_PASS:      break;
		case SPF_RESULT_FAIL:      if (spf > 0) { block(spf_response); return 0; } break;
		case SPF_RESULT_SOFTFAIL:  if (spf > 1) { block(spf_response); return 0; } break;
		case SPF_RESULT_NEUTRAL:   if (spf > 2) { block(spf_response); return 0; } break;
		case SPF_RESULT_NONE:      if (spf > 3) { block(spf_response); return 0; } break;
		case SPF_RESULT_TEMPERROR:
		case SPF_RESULT_PERMERROR: if (spf > 4) { block(spf_response); return 0; } break;
#if 0
		case SPF_RESULT_UNKNOWN:   if (spf > 5) { block(spf_response); return 0; } break;
		case SPF_RESULT_UNMECH:    break;
#else
					   // FIXME: UNKNOWN and UNMECH above map how?
					   // INVALID should not ever occur, it indicates a bug.
		case SPF_RESULT_INVALID:   if (spf > 5) { block(spf_response); return 0; } break;
#endif
	}

	/* add header */
	header = SPF_response_get_received_spf(spf_response);
	printf("H%s\n", header);

	SPF_response_free(spf_response);
	SPF_request_free(spf_request);
	SPF_server_free(spf_server);

	return 0;
}
