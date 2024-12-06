#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


from typing import Any, Type


class DNSException(Exception):
	def __init__(self, reason: str) -> None:
		super(DNSException, self).__init__(reason)


class DNSNameNotFoundError(DNSException):
	def __init__(self, name: str, respServer: str) -> None:
		super(DNSNameNotFoundError, self).__init__(
			f'DNS name "{name}" not found by "{respServer}"'
		)


class DNSZeroAnswerError(DNSException):
	def __init__(self, name: str) -> None:
		super(DNSZeroAnswerError, self).__init__(
			f'DNS name "{name}" has zero answer'
		)


class DNSRequestRefusedError(DNSException):
	def __init__(self, sendAddr: Any, toAddr: Any) -> None:
		super(DNSRequestRefusedError, self).__init__(
			f'DNS request from "{sendAddr}" to "{toAddr}" has been refused'
		)


class DNSServerFaultError(DNSException):
	def __init__(self, reason: str) -> None:
		super(DNSServerFaultError, self).__init__(reason)


class ServerNetworkError(DNSServerFaultError):
	def __init__(self, reason: str) -> None:
		super(ServerNetworkError, self).__init__(reason)


EXCEPTION_MAP = {
	DNSException.__name__:           DNSException,
	DNSNameNotFoundError.__name__:   DNSNameNotFoundError,
	DNSZeroAnswerError.__name__:     DNSZeroAnswerError,
	DNSRequestRefusedError.__name__: DNSRequestRefusedError,
	DNSServerFaultError.__name__:    DNSServerFaultError,
	ServerNetworkError.__name__:     ServerNetworkError,
}


def GetExceptionByName(name: str) -> Type[DNSException]:
	if name not in EXCEPTION_MAP:
		raise KeyError(f'No such exception "{name}"')
	else:
		return EXCEPTION_MAP[name]

