#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import logging

from typing import List, Tuple

import dns.message
import dns.rcode

from ..Downstream.Handler import DownstreamHandler
from ..Exceptions import(
	DNSException,
	DNSNameNotFoundError,
	DNSZeroAnswerError,
	DNSRequestRefusedError,
)
from ..MsgEntry import QuestionEntry


def CommonDNSMsgHandling(
	dnsMsg: dns.message.Message,
	senderAddr: Tuple[str, int],
	downstreamHdlr: DownstreamHandler,
	logger: logging.Logger,
	recDepthStack: List[ Tuple[ int, str ] ] = [],
) -> dns.message.Message:
	try:
		respMsg = downstreamHdlr.Handle(
			dnsMsg=dnsMsg,
			senderAddr=senderAddr,
			recDepthStack=recDepthStack
		)
		return respMsg
	except DNSRequestRefusedError:
		# the response has been refused, resp with REFUSED error
		respMsg = dns.message.make_response(dnsMsg)
		respMsg.set_rcode(dns.rcode.REFUSED)
		return respMsg
	except DNSNameNotFoundError:
		# there is no such domain, resp with NXDOMAIN error
		respMsg = dns.message.make_response(dnsMsg)
		respMsg.set_rcode(dns.rcode.NXDOMAIN)
		return respMsg
	except DNSZeroAnswerError:
		# the domain exists, but the query has no corresponding answers
		respMsg = dns.message.make_response(dnsMsg)
		return respMsg
	except Exception as e:
		# other server side error
		logFunc = logger.debug \
			if isinstance(e, DNSException) else \
				logger.exception

		logFunc(
			f'The query {QuestionEntry.QuestionEntry.FromRRSetList(dnsMsg.question)} failed with error {e}'
		)
		respMsg = dns.message.make_response(dnsMsg)
		respMsg.set_rcode(dns.rcode.SERVFAIL)
		return respMsg

