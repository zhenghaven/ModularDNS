#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import base64

from typing import List, Tuple

import dns.message
import requests

from ...MsgEntry import AnsEntry, MsgEntry, QuestionEntry
from ..Utils import CommonDNSRespHandling
from .ConcurrentMgr import ConcurrentMgr
from .Endpoint import Endpoint
from .HTTPSAdapters import SmartAndSecureAdapter
from .Protocol import Protocol, _REMOTE_INFO
from .Remote import DEFAULT_TIMEOUT, Remote


class HTTPSProtocol(Protocol):

	def __init__(self, endpoint: Endpoint, timeout: float) -> None:
		super(HTTPSProtocol, self).__init__(
			endpoint=endpoint,
			timeout=timeout
		)

		self.session = requests.Session()
		self.session.mount('https://', SmartAndSecureAdapter())

	def Query(
		self,
		q: dns.message.Message,
		recDepthStack: List[ Tuple[ int, str ] ],
	) -> Tuple[dns.message.Message, _REMOTE_INFO]:
		with self.lock:
			rawMsg = q.to_wire()
			rawMsgB64 = base64.urlsafe_b64encode(rawMsg)
			rawMsgB64 = rawMsgB64.decode("utf-8").strip("=")
			params = {
				'dns': rawMsgB64,
				'ct': 'application/dns-message',
			}

			ipAddr = self.endpoint.GetIPAddr(recDepthStack=recDepthStack)
			port = self.endpoint.port
			hostname = self.endpoint.GetHostName()

			resp = self.session.get(
				f'https://{ipAddr}:{port}/dns-query',
				headers={
					'Host': hostname,
				},
				params=params,
				timeout=self.timeout,
				verify=True,
			)
			resp.raise_for_status()

			return (
				dns.message.from_wire(resp.content),
				(hostname, str(ipAddr), port)
			)

	def Terminate(self) -> None:
		self.session.close()


class ConcurrentHTTPS(ConcurrentMgr):

	SESSION_CLASS: Protocol = HTTPSProtocol


class HTTPS(Remote):

	def __init__(
		self,
		endpoint: Endpoint,
		timeout: float = DEFAULT_TIMEOUT,
	) -> None:
		super(HTTPS, self).__init__(timeout=timeout)

		self.underlying = ConcurrentHTTPS(
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

