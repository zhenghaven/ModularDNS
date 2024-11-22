#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


from typing import List, Tuple

from ...MsgEntry import AddEntry, AnsEntry, MsgEntry, QuestionEntry
from ..QuickLookup import QuickLookup
from ..Utils import CommonDNSRespHandling
from .Protocol import Protocol


DEFAULT_TIMEOUT: float = 2.0


class Remote(QuickLookup):

	def __init__(self, timeout: float = DEFAULT_TIMEOUT) -> None:
		super(Remote, self).__init__()

		self.timeout = timeout

	def HandleQuestion(
		self,
		msgEntry: QuestionEntry.QuestionEntry,
		senderAddr: Tuple[str, int],
		recDepthStack: List[ Tuple[ int, str ] ],
	) -> List[ MsgEntry.MsgEntry ]:
		self.underlying: Protocol

		newRecStack = self.CheckRecursionDepth(
			recDepthStack,
			self.HandleQuestion
		)

		dnsQuery = msgEntry.MakeQuery()

		dnsResp, remote = self.underlying.Query(
			q=dnsQuery,
			recDepthStack=newRecStack
		)

		dnsResp = CommonDNSRespHandling(
			dnsResp,
			remote=remote,
			queryName=msgEntry.GetNameStr(),
			logger=self.logger
		)
		ansEntries = []
		ansEntries += AnsEntry.AnsEntry.FromRRSetList(dnsResp.answer)
		ansEntries += AddEntry.AddEntry.FromRRSetList(dnsResp.additional)

		return ansEntries

	def Terminate(self) -> None:
		self.underlying: Protocol

		self.underlying.Terminate()

