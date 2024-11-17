#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import logging
import uuid

from typing import Any, Callable, List, Tuple

import dns.message


class RecursionDepthError(Exception):

	def __init__(
		self,
		maxRecDepth: int,
		givenStack: List[ Tuple[ int, str ] ],
	) -> None:
		stackStr = ' --> '.join([f'{x[1]}' for x in givenStack])
		msg = f'The recursion depth (i.e., {len(givenStack)}) ' + \
			f'has reached the maximum value of {maxRecDepth}, ' + \
			f'and the stack is: {stackStr}'
		super(RecursionDepthError, self).__init__(msg)

		self.maxRecDepth = maxRecDepth
		self.givenStack = givenStack


class DownstreamHandler(object):

	DEFAULT_MAX_RECURSION_DEPTH: int = 50

	def __init__(
		self,
		maxRecDepth: int = DEFAULT_MAX_RECURSION_DEPTH
	) -> None:
		super(DownstreamHandler, self).__init__()

		self.instUUID = uuid.uuid4()
		self.instUUIDhex = self.instUUID.hex

		self.maxRecDepth = maxRecDepth

		self._clsName = f'{__name__}.{self.__class__.__name__}'
		self.logger = logging.getLogger(self._clsName)

	def GetTrueClassName(self) -> str:
		return self._clsName

	def CheckRecursionDepth(
		self,
		givenStack: List[ Tuple[ int, str ] ],
		currFunc: Callable[ [ Any ], Any ],
		ignoreIntraInst: bool = False,
	) -> List[ Tuple[ int, str ] ]:
		if (
			ignoreIntraInst and
			(len(givenStack) > 0) and
			(givenStack[-1][0] == self.instUUID.int)
		):
			# the current function is called by the same instance
			# and we want to ignore it
			return list(givenStack)

		# create a new stack with the current function name
		newStack = list(givenStack)
		newStack.append(
			(self.instUUID.int, f'{self.__class__.__name__}.{currFunc.__name__}')
		)

		# check the recursion depth
		if len(newStack) > self.maxRecDepth:
			raise RecursionDepthError(self.maxRecDepth, newStack)

		return newStack

	def Handle(
		self,
		dnsMsg: dns.message.Message,
		senderAddr: Tuple[str, int],
		recDepthStack: List[ Tuple[ int, str ] ],
	) -> dns.message.Message:
		raise NotImplementedError(
			'DownstreamHandler.Handle() is not implemented'
		)

	def Terminate(self) -> None:
		raise NotImplementedError(
			'DownstreamHandler.Terminate() is not implemented'
		)

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.Terminate()

