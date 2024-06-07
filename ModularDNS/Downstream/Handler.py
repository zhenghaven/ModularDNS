#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import logging
import uuid

from typing import Tuple

import dns.message


class DownstreamHandler(object):

	def __init__(self) -> None:
		super(DownstreamHandler, self).__init__()

		self.instUUID = uuid.uuid4()
		self.instUUIDhex = self.instUUID.hex

		self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

	def Handle(
		self,
		dnsMsg: dns.message.Message,
		senderAddr: Tuple[str, int],
	) -> dns.message.Message:
		raise NotImplementedError(
			'DownstreamHandler.Handle() is not implemented'
		)

