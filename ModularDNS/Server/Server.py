#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import ipaddress
import logging
import socketserver
import threading
import uuid

from typing import Any, Dict, Tuple, Type

from ..Downstream.Handler import DownstreamHandler
from .PySocketServer import MitigateServeAndShutdown


class Server:

	def ServerInit(
		self,
		addData: Dict[str, Any] = {},
	) -> None:

		self.serverUUID = uuid.uuid4()
		self.terminateEvent = threading.Event()

		self.stateLock = threading.Lock()
		self.hasServeThreadStarted = False

		self._instName = f'{__name__}.{self.__class__.__name__}.{self.serverUUID.hex[:8]}'
		self._logger = logging.getLogger(self._instName)

		self.handlerName = self.RequestHandlerClass.__name__
		self.handlerLoggerName = f'{self._instName}.{self.handlerName}'
		self.handlerLogger = logging.getLogger(self.handlerLoggerName)

		for addDataKey, addDataVal in addData.items():
			setattr(self, addDataKey, addDataVal)

	def _ServeForever(self) -> None:
		raise NotImplemented(
			f'Server._ServeForever() is not implemented'
		)

	def ServeUntilTerminate(self) -> None:
		self._ServeForever()

	def ThreadedServeUntilTerminate(self) -> None:
		with self.stateLock:
			if self.hasServeThreadStarted:
				# the `ThreadedServeUntilTerminate` method has already started
				# the serve thread, so we should not start another one
				return

			if self.terminateEvent.is_set():
				# the `Terminate` method has already been called
				# so we should not start the serve thread
				return

			# otherwise, the `Terminate` method has not entered the
			# `with self.stateLock:` critical section,
			# so it is safe to start the thread

			self.hasServeThreadStarted = True

			self.serveThread = threading.Thread(
				target=self.ServeUntilTerminate,
				name=f'{self._instName}.ServeUntilTerminate',
			)
			self.serveThread.start()

	def _Shutdown(self) -> None:
		raise NotImplemented(
			f'Server._Shutdown() is not implemented'
		)

	def _CleanUp(self) -> None:
		raise NotImplemented(
			f'Server._CleanUp() is not implemented'
		)

	def Terminate(self) -> None:
		self.terminateEvent.set()

		self._Shutdown()

		with self.stateLock:
			if self.hasServeThreadStarted:
				# the `ThreadedServeUntilTerminate` method has started the serve
				# thread, so we should wait for it to complete
				self.serveThread.join()

		self._CleanUp()

	def GetSrcPort(self) -> int:
		raise NotImplemented(
			f'Server.GetSrcPort() is not implemented'
		)


def FromPySocketServer(oriCls: Type[socketserver.BaseServer]) -> Type[Server]:

	MitigatedCls: Type[socketserver.BaseServer] = MitigateServeAndShutdown(oriCls)

	class __PySocketServerAndServer(MitigatedCls, Server):

		def _ServeForever(self) -> None:
			self.serve_forever()

		def _Shutdown(self) -> None:
			self.shutdown()

		def _CleanUp(self) -> None:
			self.server_close()

		def GetSrcPort(self) -> int:
			return self.server_address[1]

	return __PySocketServerAndServer


def CreateServer(
	server_address: Tuple[str, int],
	downstreamHdlr: DownstreamHandler,
	handlerType: Type[socketserver.BaseRequestHandler],
	serverV4Type: Type[Server],
	serverV6Type: Type[Server],
) -> Server:

	serverIPVer = 6 \
		if len(server_address[0]) == 0 else\
			ipaddress.ip_address(server_address[0]).version
	if serverIPVer == 4:
		serverType = serverV4Type
	elif serverIPVer == 6:
		serverType = serverV6Type
	else:
		raise ValueError(f'Unsupported IP version: {serverIPVer}')

	serverInst = serverType(server_address, handlerType)
	serverInst.ServerInit({
		'downstreamHandler': downstreamHdlr,
	})

	return serverInst

