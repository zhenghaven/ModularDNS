#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import logging
import socket

from typing import Any, List, Tuple, Union

import dns.message

from CacheLib import LockwSLD
from CacheLib.TTL import Interfaces

from ...Exceptions import ServerNetworkError
from .Endpoint import Endpoint


_REMOTE_INFO = Tuple[str, str, int]


class Protocol(Interfaces.Terminable):

	IP_VER_TO_AF_MAP = {
		4: socket.AF_INET,
		6: socket.AF_INET6,
	}

	@classmethod
	def SysSocketCreate(
		cls,
		af: int,
		sockType: int,
		timeout: Union[float, None] = None,
	) -> socket.socket:
		sock = socket.socket(af, sockType)
		sock.settimeout(timeout)
		return sock

	@classmethod
	def SysSocketShutdown(
		cls,
		sock: socket.socket
	) -> None:
		try:
			sock.shutdown(socket.SHUT_RDWR)
		except:
			# it may raise an exception if the socket is not connected
			# but we can safely ignore it
			pass
		sock.close()

	@classmethod
	def SysIOExceptionToServerNetworkError(
		cls,
		f: callable,
		msg: str,
	) -> Any:
		try:
			return f()
		except (
			OSError,
			TimeoutError,
			ConnectionError,
			ConnectionResetError,
		):
			raise ServerNetworkError(msg)

	def __init__(self, endpoint: Endpoint, timeout: float) -> None:
		super(Protocol, self).__init__()

		self.endpoint = endpoint
		self.timeout = timeout

		# we assume that this object will only be used by one thread
		# at a time, and the upper layer should handle this properly
		# but we still add a lock here to prevent potential issues
		self.lock = LockwSLD.LockwSLD()

		self._logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

	def Query(
		self,
		q: dns.message.Message,
		recDepthStack: List[ Tuple[ int, str ] ],
	) -> Tuple[dns.message.Message, _REMOTE_INFO]:
		raise NotImplementedError('Protocol.Query() is not implemented')

	def _Terminate(self) -> None:
		self.endpoint.Terminate()

	def Terminate(self) -> None:
		raise NotImplementedError('Protocol.Terminate() is not implemented')

