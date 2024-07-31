#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


from typing import Any


class DNSNameNotFoundError(Exception):
	def __init__(self, name: str, respServer: str) -> None:
		super(DNSNameNotFoundError, self).__init__(
			f'DNS name "{name}" not found by "{respServer}"'
		)


class DNSZeroAnswerError(Exception):
	def __init__(self, name: str) -> None:
		super(DNSZeroAnswerError, self).__init__(
			f'DNS name "{name}" has zero answer'
		)


class DNSRequestRefusedError(Exception):
	def __init__(self, sendAddr: Any, toAddr: Any) -> None:
		super(DNSRequestRefusedError, self).__init__(
			f'DNS request from "{sendAddr}" to "{toAddr}" has been refused'
		)


class DNSServerFaultError(Exception):
	def __init__(self, reason: str) -> None:
		super(DNSServerFaultError, self).__init__(reason)

