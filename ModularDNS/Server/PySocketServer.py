#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###

# The original implementation of socketserver suffers from the race condition
# issue when one thread is trying to start the server while another thread is
# trying to stop the server.
# The replacement implementation here is based on the original implementation
# with the necessary mitigation


import selectors
import socketserver
import threading


# poll/select have the advantage of not requiring any extra file descriptor,
# contrarily to epoll/kqueue (also, they require a single syscall).
if hasattr(selectors, 'PollSelector'):
	_ServerSelector = selectors.PollSelector
else:
	_ServerSelector = selectors.SelectSelector


def MitigateServeAndShutdown(oriCls: socketserver.BaseServer):

	class __MitigatedServer(oriCls):

		def __init__(self, *args, **kwargs):
			super().__init__(*args, **kwargs)
			self.__hasShutdownRequest = threading.Event()

		def serve_forever(self, poll_interval=0.5):

			with _ServerSelector() as selector:
				selector.register(self, selectors.EVENT_READ)

				while not self.__hasShutdownRequest.is_set():
					ready = selector.select(poll_interval)
					if self.__hasShutdownRequest.is_set():
						break
					if ready:
						self._handle_request_noblock()

					self.service_actions()

		def shutdown(self):
			self.__hasShutdownRequest.set()

	return __MitigatedServer

