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
from ..DownstreamCollection import DownstreamCollection
from ..QuickLookup import QuickLookup


class RaiseExcept(QuickLookup):

	@classmethod
	def FromConfig(
		cls,
		dCollection: DownstreamCollection,
		exceptToRaise: str,
		exceptArgs: List = [],
		exceptKwargs: dict = {},
	) -> 'RaiseExcept':
		return cls(
			exceptToRaise=_ModularDNSExceptions.GetExceptionByName(exceptToRaise),
			exceptArgs=tuple(exceptArgs),
			exceptKwargs=exceptKwargs,
		)

	def __init__(
		self,
		exceptToRaise: Type[_ModularDNSExceptions.DNSException],
		exceptArgs: Tuple = (),
		exceptKwargs: dict = {},
	) -> None:
		super(RaiseExcept, self).__init__()

		self.exceptToRaise = exceptToRaise
		self.exceptArgs = exceptArgs
		self.exceptKwargs = exceptKwargs

	def HandleQuestion(
		self,
		msgEntry: QuestionEntry.QuestionEntry,
		senderAddr: Tuple[str, int],
		recDepthStack: List[ Tuple[ int, str ] ],
	) -> List[ MsgEntry.MsgEntry ]:

		raise self.exceptToRaise(*self.exceptArgs, **self.exceptKwargs)

