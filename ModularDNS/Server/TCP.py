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
import socketserver

from typing import Tuple

import dns.message

from ..Exceptions import ServerNetworkError
from ..Downstream.Handler import DownstreamHandler
from ..Downstream.DownstreamCollection import DownstreamCollection
from .Server import (
	CreateServer as _CreateServerFromPySocketServer,
	FromPySocketServer,
	Server
)
from .Utils import CommonDNSMsgHandling


class TCPHandler(socketserver.StreamRequestHandler):

	server: Server

	def ReadBytes(self, numBytes: int) -> bytes:
		res = b''
		while len(res) < numBytes:
			bytesLeft = numBytes - len(res)
			inBytes = self.rfile.read(bytesLeft)
			if len(inBytes) == 0:
				raise ServerNetworkError('Client disconnected')
			else:
				res += inBytes
		return res

	def ProcessOneRequest(self) -> None:
		sender = self.client_address

		lenBytes = self.ReadBytes(2)
		msgLen = int.from_bytes(lenBytes, byteorder='big')
		rawData = self.ReadBytes(msgLen)

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
		rawRespLenBytes = len(rawResp).to_bytes(2, byteorder='big')
		self.wfile.write(rawRespLenBytes)
		self.wfile.write(rawResp)

	def handle(self):
		pollInterval = 0.5

		# set socket to no-delay mode
		self.request.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

		with selectors.DefaultSelector() as selector:
			selector.register(self.rfile, selectors.EVENT_READ)

			try:
				while not self.server.terminateEvent.is_set():
					for key, events in selector.select(pollInterval):
						if key.fileobj == self.rfile:
							self.ProcessOneRequest()
						else:
							self.server.handlerLogger.error(
								'Unknown file object in selector'
							)
			except Exception as e:
				self.server.handlerLogger.debug(
					f'Handler failed with error {e}'
				)
				pass


@FromPySocketServer
class TCPServerV4(socketserver.ThreadingTCPServer):
	address_family = socket.AF_INET


@FromPySocketServer
class TCPServerV6(socketserver.ThreadingTCPServer):
	address_family = socket.AF_INET6


class TCP:

	@classmethod
	def CreateServer(
		cls,
		server_address: Tuple[str, int],
		downstreamHdlr: DownstreamHandler
	) -> Server:

		return _CreateServerFromPySocketServer(
			server_address=server_address,
			downstreamHdlr=downstreamHdlr,
			handlerType=TCPHandler,
			serverV4Type=TCPServerV4,
			serverV6Type=TCPServerV6,
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

