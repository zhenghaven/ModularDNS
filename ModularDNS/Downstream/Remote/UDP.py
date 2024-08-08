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

import dns.message
import dns.query

from ...MsgEntry import AnsEntry, MsgEntry, QuestionEntry
from ..DownstreamCollection import DownstreamCollection
from ..Utils import CommonDNSRespHandling
from .Endpoint import Endpoint
from .Protocol import Protocol, _REMOTE_INFO
from .Remote import DEFAULT_TIMEOUT, Remote


class UDPProtocol(Protocol):

	def __init__(self, endpoint: Endpoint, timeout: float) -> None:
		super(UDPProtocol, self).__init__(
			endpoint=endpoint,
			timeout=timeout
		)

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.setblocking(False)
		self.sock.settimeout(timeout)

	def Query(
		self,
		q: dns.message.Message,
		recDepthStack: List[ Tuple[ int, str ] ],
	) -> Tuple[dns.message.Message, _REMOTE_INFO]:
		ip = self.endpoint.GetIPAddr(recDepthStack=recDepthStack)
		port = self.endpoint.port

		resp = dns.query.udp(
			q=q,
			where=str(ip),
			port=port,
			timeout=self.timeout,
			sock=self.sock,
		)

		return (
			resp,
			(self.endpoint.GetHostName(), str(ip), port)
		)

	def Terminate(self) -> None:
		super(UDPProtocol, self)._Terminate()
		try:
			self.sock.shutdown(socket.SHUT_RDWR)
		except:
			# it may raise an exception if the socket is not connected
			# but we can safely ignore it
			pass
		self.sock.close()


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

