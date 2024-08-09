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
		self.hasServeLoopStarted = False
		self.hasServeThreadStarted = False

	def _ServeForever(self) -> None:
		raise NotImplemented(
			f'Server._ServeForever() is not implemented'
		)

	def ServeUntilTerminate(self) -> None:
		startServing = False

		with self.stateLock:
			if not self.terminateEvent.is_set():
				# the `Terminate` method has not completed the first line of
				# `self.terminateEvent.set()`, so it is safe to start serving
				self.hasServeLoopStarted = True
				startServing = True

		# we have set the state to start serving, so we have to start serving now
		if startServing:
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

		with self.stateLock:
			if self.hasServeLoopStarted:
				# the `ServeUntilTerminate` method has started the serve loop
				# so it is eventually going to start serving
				# so it's safe to call `shutdown` method
				self._Shutdown()

			if self.hasServeThreadStarted:
				# the `ThreadedServeUntilTerminate` method has started the serve
				# thread, so we should wait for it to complete
				self.serveThread.join()

		self._CleanUp()

	def GetSrcPort(self) -> int:
		raise NotImplemented(
			f'Server.GetSrcPort() is not implemented'
		)


class _SocketServerAndServer(socketserver.BaseServer, Server):
	pass


def PySocketServerClass(oriCls: Type[_SocketServerAndServer]):

	def _ServeForever(self: _SocketServerAndServer) -> None:
		self.serve_forever()

	def _Shutdown(self: _SocketServerAndServer) -> None:
		self.shutdown()

	def _CleanUp(self: _SocketServerAndServer) -> None:
		self.server_close()

	def GetSrcPort(self: _SocketServerAndServer) -> int:
		return self.server_address[1]

	setattr(oriCls, '_ServeForever', _ServeForever)
	setattr(oriCls, '_Shutdown', _Shutdown)
	setattr(oriCls, '_CleanUp', _CleanUp)
	setattr(oriCls, 'GetSrcPort', GetSrcPort)

	return oriCls


def CreateServerBasedOnSocketserver(
	server_address: Tuple[str, int],
	downstreamHdlr: DownstreamHandler,
	handlerType: Type[socketserver.BaseRequestHandler],
	serverType: Type[_SocketServerAndServer],
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

