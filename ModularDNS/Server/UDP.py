#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import logging
import socketserver
import threading

from typing import Tuple

import dns.message

from ..Downstream.Handler import DownstreamHandler
from ..Downstream.DownstreamCollection import DownstreamCollection
from .Server import CreateServerBasedOnSocketserver, PySocketServerClass, Server
from .Utils import CommonDNSMsgHandling


class UDPHandler(socketserver.DatagramRequestHandler):

	DOWNSTREAM_HANDLER: DownstreamHandler
	LOGGER: logging.Logger
	IS_TERMINATED: threading.Event

	def handle(self):
		sender = self.client_address
		rawData = self.rfile.read()

		try:
			dnsMsg = dns.message.from_wire(rawData)
		except Exception as e:
			self.LOGGER.debug(f'Failed to parse DNS message with error {e}')
			# the DNS message received is invalid, ignore it
			return

		dnsResp = CommonDNSMsgHandling(
			dnsMsg=dnsMsg,
			senderAddr=sender,
			downstreamHdlr=self.DOWNSTREAM_HANDLER,
			logger=self.LOGGER,
		)
		rawResp = dnsResp.to_wire()
		self.wfile.write(rawResp)


@PySocketServerClass
class UDPServer(socketserver.ThreadingUDPServer, Server):
	pass


class UDP:

	@classmethod
	def CreateServer(
		cls,
		server_address: Tuple[str, int],
		downstreamHdlr: DownstreamHandler
	) -> Server:

		return CreateServerBasedOnSocketserver(
			server_address=server_address,
			downstreamHdlr=downstreamHdlr,
			handlerType=UDPHandler,
			serverType=UDPServer,
		)

	@classmethod
	def FromConfig(
		cls,
		dCollection: DownstreamCollection,
		ip: str,
		port: int,
		downstream: str,
	) -> Server:

		downstreamHdlr = dCollection.GetHandler(downstream)
		serverAddr = (ip, port)

		return cls.CreateServer(
			server_address=serverAddr,
			downstreamHdlr=downstreamHdlr,
		)

