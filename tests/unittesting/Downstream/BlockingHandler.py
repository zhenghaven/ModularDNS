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

from ModularDNS.MsgEntry import MsgEntry, QuestionEntry
from ModularDNS.Downstream.QuickLookup import QuickLookup
from ModularDNS.Downstream.HandlerByQuestion import HandlerByQuestion


class BlockingHandler(QuickLookup):

	def __init__(
		self,
		targetHandler: HandlerByQuestion,
		releaseEvent: threading.Event,
	) -> None:
		super(BlockingHandler, self).__init__()

		self.targetHandler = targetHandler
		self.releaseEvent = releaseEvent

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

		self.releaseEvent.wait()

		return self.targetHandler.HandleQuestion(
			msgEntry,
			senderAddr,
			newRecStack,
		)

