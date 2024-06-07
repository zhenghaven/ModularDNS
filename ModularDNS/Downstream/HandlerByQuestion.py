#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


from typing import List, Tuple

import dns.message

from ..MsgEntry import MsgEntry, QuestionEntry
from .Handler import DownstreamHandler


class HandlerByQuestion(DownstreamHandler):

	def __init__(self) -> None:
		super(HandlerByQuestion, self).__init__()

	def HandleQuestion(
		self,
		msgEntry: QuestionEntry.QuestionEntry,
		senderAddr: Tuple[str, int],
		recDepthStack: List[ Tuple[ int, str ] ],
	) -> List[ MsgEntry.MsgEntry ]:
		raise NotImplementedError(
			'HandlerByQuestion.Handle() is not implemented'
		)

	def Handle(
		self,
		dnsMsg: dns.message.Message,
		senderAddr: Tuple[str, int],
		recDepthStack: List[ Tuple[ int, str ] ],
	) -> dns.message.Message:
		newRecStack = self.CheckRecursionDepth(
			recDepthStack,
			self.Handle
		)

		questionList = QuestionEntry.QuestionEntry.FromRRSetList(dnsMsg.question)

		respEntries = []
		for q in questionList:
			respEntries += self.HandleQuestion(
				msgEntry=q,
				senderAddr=senderAddr,
				recDepthStack=newRecStack
			)

		respMsg = dns.message.make_response(dnsMsg)
		MsgEntry.ConcatDNSMsg(respMsg, respEntries)
		return respMsg

