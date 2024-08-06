#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import itertools
import random

from typing import List, Optional, Tuple

from ...MsgEntry import MsgEntry, QuestionEntry
from ..DownstreamCollection import DownstreamCollection
from ..QuickLookup import QuickLookup
from ..HandlerByQuestion import HandlerByQuestion


class RandomChoice(QuickLookup):

	@classmethod
	def FromConfig(
		cls,
		dCollection: DownstreamCollection,
		handlerList: List[str],
		weightList: Optional[List[int]] = None,
	) -> 'RandomChoice':
		return cls(
			handlerList=[
				dCollection.GetHandlerByQuestion(handlerStr)
				for handlerStr in handlerList
			],
			weightList=weightList,
		)

	def __init__(
		self,
		handlerList: List[HandlerByQuestion],
		weightList: Optional[List[int]] = None,
	) -> None:
		super(RandomChoice, self).__init__()

		if len(handlerList) == 0:
			raise ValueError('There must be at least one handler')

		self.handlerList = handlerList

		if weightList is None:
			weightList = [1] * len(handlerList)

		if len(weightList) != len(handlerList):
			raise ValueError(
				'Length of weightList does not match length of handlerList'
			)

		self.accWeightList = list(itertools.accumulate(weightList))

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

		# randomly choose a handler
		handler = random.choices(
			self.handlerList,
			cum_weights=self.accWeightList,
			k=1,
		)[0]

		return handler.HandleQuestion(
			msgEntry,
			senderAddr,
			newRecStack,
		)

