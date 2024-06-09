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

from CacheLib import LockwSLD
from CacheLib.TTL import Interfaces

from .Endpoint import Endpoint


_REMOTE_INFO = Tuple[str, str, int]


class Protocol(Interfaces.Terminable):

	def __init__(self, endpoint: Endpoint, timeout: float) -> None:
		super(Protocol, self).__init__()

		self.endpoint = endpoint
		self.timeout = timeout

		# we assume that this object will only be used by one thread
		# at a time, and the upper layer should handle this properly
		# but we still add a lock here to prevent potential issues
		self.lock = LockwSLD.LockwSLD()

	def Query(
		self,
		q: dns.message.Message,
		recDepthStack: List[ Tuple[ int, str ] ],
	) -> Tuple[dns.message.Message, _REMOTE_INFO]:
		raise NotImplementedError('Protocol.Query() is not implemented')

	def Terminate(self) -> None:
		raise NotImplementedError('Protocol.Terminate() is not implemented')

