#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import ipaddress
import random

from typing import List, Tuple, Union

import dns.name
import dns.rdataclass
import dns.rdatatype

from ..Exceptions import DNSNameNotFoundError, DNSZeroAnswerError
from ..MsgEntry import AnsEntry, MsgEntry, QuestionEntry
from .HandlerByQuestion import HandlerByQuestion


class QuickLookup(HandlerByQuestion):

	def __init__(self) -> None:
		super(HandlerByQuestion, self).__init__()

	@classmethod
	def SelectOneAddress(
		self,
		domain: str,
		entries: List[ MsgEntry.MsgEntry ],
	) -> Union[ipaddress.IPv4Address, ipaddress.IPv6Address]:
		res = []
		for entry in entries:
			if entry.entryType == 'ANS':
				ans: AnsEntry.AnsEntry = entry
				# ans.rdType could be CNAME, which we should ignore
				if ans.rdType in [dns.rdatatype.A, dns.rdatatype.AAAA]:
					res += ans.GetAddresses()

		if len(res) == 0:
			raise DNSZeroAnswerError(domain)
		else:
			return random.choice(res)

	def LookupIpAddr(
		self,
		domain: str,
		recDepthStack: List[ Tuple[ int, str ] ],
		preferIPv6: bool = False,
		requester: Tuple[str, int] = ('localhost', 0),
	) -> Union[ipaddress.IPv4Address, ipaddress.IPv6Address]:
		newRecStack = self.CheckRecursionDepth(
			recDepthStack,
			self.LookupIpAddr
		)

		questionEntry = QuestionEntry.QuestionEntry(
			name=dns.name.from_text(domain),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.AAAA if preferIPv6 else dns.rdatatype.A,
		)

		try:
			resps = self.HandleQuestion(
				msgEntry=questionEntry,
				senderAddr=requester,
				recDepthStack=newRecStack,
			)
			return self.SelectOneAddress(domain=domain, entries=resps)
		except (DNSNameNotFoundError, DNSZeroAnswerError):
			# the preferred type is not found, try the other type
			pass

		# NOTE: if preferIPv6, then now try A
		questionEntry = QuestionEntry.QuestionEntry(
			name=dns.name.from_text(domain),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A if preferIPv6 else dns.rdatatype.AAAA,
		)
		resps = self.HandleQuestion(
			msgEntry=questionEntry,
			senderAddr=requester,
			recDepthStack=newRecStack,
		)
		return self.SelectOneAddress(domain=domain, entries=resps)

