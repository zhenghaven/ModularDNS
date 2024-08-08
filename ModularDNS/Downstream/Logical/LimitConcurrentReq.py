#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import threading

from typing import List, Tuple

from ... import Exceptions as _ModularDNSExceptions
from ...MsgEntry import MsgEntry, QuestionEntry
from ..DownstreamCollection import DownstreamCollection
from ..QuickLookup import QuickLookup
from ..HandlerByQuestion import HandlerByQuestion


class LimitConcurrentReq(QuickLookup):

	@classmethod
	def FromConfig(
		cls,
		dCollection: DownstreamCollection,
		targetHandler: str,
		maxNumConcurrentReq: int,
		blocking: bool = False,
	) -> 'LimitConcurrentReq':
		return cls(
			targetHandler=dCollection.GetHandlerByQuestion(targetHandler),
			maxNumConcurrentReq=maxNumConcurrentReq,
			blocking=blocking,
		)

	def __init__(
		self,
		targetHandler: HandlerByQuestion,
		maxNumConcurrentReq: int,
		blocking: bool = False,
	) -> None:
		super(LimitConcurrentReq, self).__init__()

		self.targetHandler = targetHandler
		self.maxNumConcurrentReq = maxNumConcurrentReq
		self.blocking = blocking

		self.semaphore = threading.Semaphore(self.maxNumConcurrentReq)

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

		hasAcquired = self.semaphore.acquire(blocking=self.blocking)
		if not hasAcquired:
			raise _ModularDNSExceptions.DNSRequestRefusedError(
				sendAddr=senderAddr,
				toAddr=self._clsName,
			)

		try:
			return self.targetHandler.HandleQuestion(
				msgEntry,
				senderAddr,
				newRecStack,
			)
		finally:
			self.semaphore.release()

	def Terminate(self) -> None:
		self.targetHandler.Terminate()

