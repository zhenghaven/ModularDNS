#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


from typing import List, Tuple

import dns.query

from ...MsgEntry import AnsEntry, MsgEntry, QuestionEntry
from ..Utils import CommonDNSRespHandling
from .Remote import DEFAULT_TIMEOUT, Remote
from .Endpoint import Endpoint


class UDP(Remote):

	def __init__(
		self,
		endpoint: Endpoint,
		timeout: float = DEFAULT_TIMEOUT,
	) -> None:
		super(UDP, self).__init__(timeout=timeout)

		self.endpoint = endpoint

	def HandleQuestion(
		self,
		msgEntry: QuestionEntry.QuestionEntry,
		senderAddr: Tuple[str, int],
		recDepthStack: List[ Tuple[ int, str ] ],
	) -> List[ MsgEntry.MsgEntry ]:
		newRecStack = self.CheckRecursionDepth(
			recDepthStack,
			self.HandleQuestion
		)

		dnsQuery = msgEntry.MakeQuery()

		ip = self.endpoint.GetIPAddr(recDepthStack=newRecStack)
		port = self.endpoint.port

		dnsResp = dns.query.udp(
			dnsQuery,
			where=str(ip),
			port=port,
			timeout=self.timeout
		)

		dnsResp = CommonDNSRespHandling(
			dnsResp,
			remote=str((str(ip), port)),
			queryName=msgEntry.GetNameStr(),
			logger=self.logger
		)
		ansEntries = AnsEntry.AnsEntry.FromRRSetList(dnsResp.answer)

		return ansEntries

