#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import heapq

from typing import Dict, List, Tuple

from .QuestionRule import Rule, RuleFromStr
from ..DownstreamCollection import DownstreamCollection
from ..QuickLookup import QuickLookup
from ..HandlerByQuestion import HandlerByQuestion

from ...MsgEntry import MsgEntry, QuestionEntry


class QuestionRuleSet(QuickLookup):

	@classmethod
	def FromConfig(
		cls,
		dCollection: DownstreamCollection,
		ruleAndHandlers: Dict[str, str],
	) -> 'QuestionRuleSet':
		return cls(
			ruleAndHandlers={
				ruleStr: dCollection.GetHandlerByQuestion(handlerStr)
				for ruleStr, handlerStr in ruleAndHandlers.items()
			}
		)

	def __init__(
		self,
		ruleAndHandlers: Dict[str, HandlerByQuestion],
	) -> None:
		super(QuestionRuleSet, self).__init__()

		self.lut: Dict[Rule, HandlerByQuestion] = {}
		for ruleStr, handler in ruleAndHandlers.items():
			rule = RuleFromStr(ruleStr)
			if rule in self.lut:
				raise ValueError(
					f'Question rule "{rule}" (from "{ruleStr}") already exists'
				)
			self.lut[rule] = handler

	def MatchHandler(
		self,
		msgEntry: QuestionEntry.QuestionEntry,
	) -> HandlerByQuestion:
		# match with all rules
		q: List[Tuple[int, HandlerByQuestion]] = []
		for rule, handler in self.lut.items():
			isMatch, weight = rule.Match(msgEntry)
			if isMatch:
				# `-weight` is used to make the heap a max-heap
				heapq.heappush(q, (-weight, handler))

		# get the handler with the highest weight
		if len(q) == 0:
			raise RuntimeError(
				f'No handler found for question {msgEntry}'
			)
		_, handler = heapq.heappop(q)

		return handler

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

		handler = self.MatchHandler(msgEntry=msgEntry)

		return handler.HandleQuestion(
			msgEntry=msgEntry,
			senderAddr=senderAddr,
			recDepthStack=newRecStack,
		)

	def Terminate(self) -> None:
		for handler in self.lut.values():
			handler.Terminate()
		self.lut.clear()

