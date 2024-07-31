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

from typing import List, Tuple, Union

from ...MsgEntry import MsgEntry, QuestionEntry
from ..QuickLookup import QuickLookup
from ..HandlerByQuestion import HandlerByQuestion


class RandomChoice(QuickLookup):

	def __init__(
		self,
		handlerList: List[HandlerByQuestion],
		weightList: Union[List[int], None] = None,
	) -> None:
		super(RandomChoice, self).__init__()

		if len(handlerList) == 0:
			raise ValueError('There must be at least one handler')

		self.handlerList = handlerList

		if weightList is None:
			self.weightList = [1] * len(handlerList)

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

