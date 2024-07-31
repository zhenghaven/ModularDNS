#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


from typing import List, Tuple, Type

from ... import Exceptions as _ModularDNSExceptions
from ...MsgEntry import MsgEntry, QuestionEntry
from ..QuickLookup import QuickLookup
from ..HandlerByQuestion import HandlerByQuestion


class Failover(QuickLookup):

	def __init__(
		self,
		initialHandler: HandlerByQuestion,
		failoverHandler: HandlerByQuestion,
		exceptList: List[Type[Exception]] = [
			_ModularDNSExceptions.DNSNameNotFoundError,
			_ModularDNSExceptions.DNSRequestRefusedError,
			_ModularDNSExceptions.DNSServerFaultError,
			_ModularDNSExceptions.DNSZeroAnswerError,
		]
	) -> None:
		super(Failover, self).__init__()

		self.initialHandler = initialHandler
		self.failoverHandler = failoverHandler
		self.exceptList = exceptList

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

		try:
			return self.initialHandler.HandleQuestion(
				msgEntry,
				senderAddr,
				newRecStack,
			)
		except tuple(self.exceptList):
			return self.failoverHandler.HandleQuestion(
				msgEntry,
				senderAddr,
				newRecStack,
			)

