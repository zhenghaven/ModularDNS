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
import uuid

from typing import Tuple, Type

from ..Downstream.Handler import DownstreamHandler
from .PySocketServer import MitigateServeAndShutdown


class Server:

	def ServerInit(
		self,
		serverUUID: uuid.UUID,
		terminateEvent: threading.Event,
	) -> None:

		self._instName = f'{__name__}.{self.__class__.__name__}.{serverUUID.hex[:8]}'
		self._logger = logging.getLogger(self._instName)

		self.serverUUID = serverUUID
		self.terminateEvent = terminateEvent

		self.stateLock = threading.Lock()
		self.hasServeThreadStarted = False

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
	serverType: Type[Server],
) -> Server:

	serverUUID = uuid.uuid4()
	terminateEvent = threading.Event()

	handlerName = \
		f'{handlerType.__name__}_D{downstreamHdlr.instUUIDhex[:8]}_S{serverUUID.hex[:8]}'
	loggerName = f'{__name__}.{handlerName}'

	logger = logging.getLogger(loggerName)

	derivedHandlerType = type(
		handlerName,
		(handlerType, ),
		{
			'DOWNSTREAM_HANDLER': downstreamHdlr,
			'LOGGER': logger,
			'IS_TERMINATED': terminateEvent,
		}
	)

	serverInst = serverType(server_address, derivedHandlerType)
	serverInst.ServerInit(serverUUID, terminateEvent)

	return serverInst

