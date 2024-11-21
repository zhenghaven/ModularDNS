#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import socket

from typing import List, Tuple

import dns.exception
import dns.message
import dns.query

from ...Exceptions import ServerNetworkError
from ...MsgEntry import AnsEntry, MsgEntry, QuestionEntry
from ..DownstreamCollection import DownstreamCollection
from ..Utils import CommonDNSRespHandling
from .Endpoint import Endpoint
from .Protocol import Protocol, _REMOTE_INFO
from .Remote import DEFAULT_TIMEOUT, Remote


class UDPProtocol(Protocol):

	_IP_VER_MAP = {
		4: socket.AF_INET,
		6: socket.AF_INET6,
	}

	@classmethod
	def _CreateSocket(cls, af: int, sockType: int) -> socket.socket:
		sock = socket.socket(af, sockType)
		sock.setblocking(False)
		return sock

	def __init__(self, endpoint: Endpoint, timeout: float) -> None:
		super(UDPProtocol, self).__init__(
			endpoint=endpoint,
			timeout=timeout
		)

		self.sock = {
			ver: self._CreateSocket(af, socket.SOCK_DGRAM)
			for ver, af in self._IP_VER_MAP.items()
		}

	def Query(
		self,
		q: dns.message.Message,
		recDepthStack: List[ Tuple[ int, str ] ],
	) -> Tuple[dns.message.Message, _REMOTE_INFO]:
		ip = self.endpoint.GetIPAddr(recDepthStack=recDepthStack)
		port = self.endpoint.port

		if ip.version not in self.sock:
			raise ValueError(f'Unsupported IP version: {ip.version}')
		sock = self.sock[ip.version]

		try:
			resp = dns.query.udp(
				q=q,
				where=str(ip),
				port=port,
				timeout=self.timeout,
				sock=sock,
			)
		except (
			dns.query.BadResponse,
			dns.exception.Timeout,
		) as e:
			raise ServerNetworkError(str(e))

		return (
			resp,
			(self.endpoint.GetHostName(), str(ip), port)
		)

	@classmethod
	def _SocketShutdown(cls, sock: socket.socket) -> None:
		try:
			sock.shutdown(socket.SHUT_RDWR)
		except:
			# it may raise an exception if the socket is not connected
			# but we can safely ignore it
			pass
		sock.close()

	def Terminate(self) -> None:
		super(UDPProtocol, self)._Terminate()
		for sock in self.sock.values():
			self._SocketShutdown(sock)


class UDP(Remote):

	@classmethod
	def FromConfig(
		cls,
		dCollection: DownstreamCollection,
		endpoint: str,
		timeout: float = DEFAULT_TIMEOUT,
	) -> 'UDP':
		return cls(
			endpoint=dCollection.GetEndpoint(endpoint),
			timeout=timeout
		)

	def __init__(
		self,
		endpoint: Endpoint,
		timeout: float = DEFAULT_TIMEOUT,
	) -> None:
		super(UDP, self).__init__(timeout=timeout)

		self.underlying = UDPProtocol(
			endpoint=endpoint,
			timeout=timeout
		)

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

		dnsQuery = msgEntry.MakeQuery()

		dnsResp, remote = self.underlying.Query(
			q=dnsQuery,
			recDepthStack=newRecStack
		)

		dnsResp = CommonDNSRespHandling(
			dnsResp,
			remote=remote,
			queryName=msgEntry.GetNameStr(),
			logger=self.logger
		)
		ansEntries = AnsEntry.AnsEntry.FromRRSetList(dnsResp.answer)

		return ansEntries

	def Terminate(self) -> None:
		self.underlying.Terminate()

