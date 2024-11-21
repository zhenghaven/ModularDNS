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
import socketserver
import threading

from typing import Tuple

import dns.message

from ..Downstream.Handler import DownstreamHandler
from ..Downstream.DownstreamCollection import DownstreamCollection
from .Server import (
	CreateServer as _CreateServerFromPySocketServer,
	FromPySocketServer,
	Server
)
from .Utils import CommonDNSMsgHandling


class UDPHandler(socketserver.DatagramRequestHandler):

	server: Server

	def handle(self):
		sender = self.client_address
		rawData = self.rfile.read()

		try:
			dnsMsg = dns.message.from_wire(rawData)
		except Exception as e:
			self.server.handlerLogger.debug(
				f'Failed to parse DNS message with error {e}'
			)
			# the DNS message received is invalid, ignore it
			return

		dnsResp = CommonDNSMsgHandling(
			dnsMsg=dnsMsg,
			senderAddr=sender,
			downstreamHdlr=self.server.downstreamHandler,
			logger=self.server.handlerLogger,
		)
		rawResp = dnsResp.to_wire()
		self.wfile.write(rawResp)


@FromPySocketServer
class UDPServerV4(socketserver.ThreadingUDPServer):
	address_family = socket.AF_INET

@FromPySocketServer
class UDPServerV6(socketserver.ThreadingUDPServer):
	address_family = socket.AF_INET6


class UDP:

	@classmethod
	def CreateServer(
		cls,
		server_address: Tuple[str, int],
		downstreamHdlr: DownstreamHandler
	) -> Server:

		return _CreateServerFromPySocketServer(
			server_address=server_address,
			downstreamHdlr=downstreamHdlr,
			handlerType=UDPHandler,
			serverV4Type=UDPServerV4,
			serverV6Type=UDPServerV6,
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

