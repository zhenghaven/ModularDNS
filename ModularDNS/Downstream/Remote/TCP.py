#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import selectors
import socket
import threading

from typing import List, Tuple

import dns.message

from ...Exceptions import ServerNetworkError
from ..DownstreamCollection import DownstreamCollection
from .ConcurrentMgr import ConcurrentMgr
from .Endpoint import Endpoint
from .Protocol import Protocol, _REMOTE_INFO
from .Remote import DEFAULT_TIMEOUT, Remote


class TCPProtocol(Protocol):

	'''
	Implementation of DNS-over-TCP protocol
	'''

	def __init__(self, endpoint: Endpoint, timeout: float) -> None:
		super(TCPProtocol, self).__init__(
			endpoint=endpoint.FromCopy(endpoint),
			timeout=timeout
		)

		self.isTerminated = threading.Event()

		self.sockAndSelector = None

	def _CreateSocket(
		self,
		recDepthStack: List[ Tuple[ int, str ] ],
	) -> None:
		hostName = self.endpoint.GetHostName()
		ip = self.endpoint.GetIPAddr(recDepthStack=recDepthStack)
		port = self.endpoint.port
		self.peername = (ip, port)

		af = self.IP_VER_TO_AF_MAP[ip.version]

		sock = self.SysSocketCreate(
			af,
			socket.SOCK_STREAM,
			timeout=self.timeout,
		)
		# set the socket to no-delay mode
		sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

		self._logger.debug(f'Connecting to {hostName} ({ip}) on port {port}')
		sock.connect((str(ip), port))

		selector = selectors.DefaultSelector()
		selector.register(sock, selectors.EVENT_READ)

		self.sockAndSelector = (sock, selector)

	def _DestroySocket(self) -> None:
		if self.sockAndSelector is not None:
			sock, selector = self.sockAndSelector
			self.SysSocketShutdown(sock)
			selector.close()
			self.sockAndSelector = None

	def _ReadBytes(self, sock: socket.socket, numBytes: int) -> bytes:
		res = b''
		while len(res) < numBytes:
			bytesLeft = numBytes - len(res)
			inBytes = sock.recv(bytesLeft)
			if len(inBytes) == 0:
				raise ServerNetworkError('Client disconnected')
			else:
				res += inBytes
		return res

	def _WaitForResponse(
		self,
		sock: socket.socket,
		selector: selectors.DefaultSelector,
		pollInterval: float = 0.5,
	) -> bytes:
		lenBytes = self._ReadBytes(sock, 2)
		msgLen = int.from_bytes(lenBytes, byteorder='big')
		return self._ReadBytes(sock, msgLen)

	def Query(
		self,
		q: dns.message.Message,
		recDepthStack: List[ Tuple[ int, str ] ],
	) -> Tuple[dns.message.Message, _REMOTE_INFO]:
		rawMsg = q.to_wire()
		rawMsgLenBytes = len(rawMsg).to_bytes(2, byteorder='big')

		with self.lock:
			try:
				def _IOSteps():
					# create connection if not exists
					if self.sockAndSelector is None:
						self._CreateSocket(recDepthStack)

					sock, selector = self.sockAndSelector

					# send query
					sock.sendall(rawMsgLenBytes)
					sock.sendall(rawMsg)

					# wait for response
					rawResp = self._WaitForResponse(sock, selector)
					return rawResp

				rawResp = self.SysIOExceptionToServerNetworkError(
					_IOSteps,
					'System IO error during TCP query'
				)
			except ServerNetworkError:
				# known network error, terminate the connection
				self._DestroySocket()
				raise
			except Exception as e:
				# unknown error, terminate the connection
				self._DestroySocket()
				raise
		# IO operation finished, release the lock

		respMsg = dns.message.from_wire(rawResp)

		return (
			respMsg,
			(self.endpoint.GetHostName(), self.peername[0], self.peername[1])
		)

	def Terminate(self) -> None:
		super(TCPProtocol, self)._Terminate()
		self.isTerminated.set()
		self._DestroySocket()


class ConcurrentTCP(ConcurrentMgr):

	SESSION_CLASS: Protocol = TCPProtocol


class TCP(Remote):

	@classmethod
	def FromConfig(
		cls,
		dCollection: DownstreamCollection,
		endpoint: str,
		timeout: float = DEFAULT_TIMEOUT,
	) -> 'TCP':
		return cls(
			endpoint=dCollection.GetEndpoint(endpoint),
			timeout=timeout
		)

	def __init__(
		self,
		endpoint: Endpoint,
		timeout: float = DEFAULT_TIMEOUT,
	) -> None:
		super(TCP, self).__init__(timeout=timeout)

		self.underlying = ConcurrentTCP(
			endpoint=endpoint,
			timeout=timeout
		)

