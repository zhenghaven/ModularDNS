#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import enum
import logging
import signal

import threading
from typing import Any, Callable, List, Optional


_HANDLER_TYPE = Callable[[int, Any], None]


class SignalHandlerRegister(object):

	def __init__(
		self,
		signals: List[enum.IntEnum],
		handler: _HANDLER_TYPE,
	) -> None:
		super(SignalHandlerRegister, self).__init__()

		self.__signals = signals
		self.__handler = handler

	def Register(self) -> None:
		for sig in self.__signals:
			signal.signal(sig, self.__handler)

	def Unregister(self) -> None:
		for sig in self.__signals:
			signal.signal(sig, signal.SIG_DFL)

	def __enter__(self) -> 'SignalHandlerRegister':
		self.Register()
		return self

	def __exit__(self, exc_type, exc_value, traceback) -> None:
		self.Unregister()


class WaitUntilSignals(object):

	def __init__(
		self,
		signals: List[enum.IntEnum] = [signal.SIGINT, signal.SIGTERM],
		enableLogger: bool = True,
	) -> None:
		super(WaitUntilSignals, self).__init__()

		self.__logger = None
		if enableLogger:
			self.__logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

		self.__signals = signals
		self.__termEvent = threading.Event()

		self.__register = SignalHandlerRegister(
			signals=self.__signals,
			handler=self.__InterruptCallback,
		)

	def __InterruptCallback(self, signum, frame) -> None:
		signame = signal.Signals(signum).name
		if self.__logger is not None:
			self.__logger.info(f'Signal handler called with signal {signame} ({signum})')
		self.__termEvent.set()

	def Wait(self) -> None:
		with self.__register:
			self.__termEvent.wait()

