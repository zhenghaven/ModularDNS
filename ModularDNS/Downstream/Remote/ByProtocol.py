#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###



from ..DownstreamCollection import DownstreamCollection
from .Remote import DEFAULT_TIMEOUT

from .HTTPS import HTTPS
from .UDP import UDP


REMOTE_HANDLER_MAP = {
	'https': HTTPS,
	'udp': UDP,
}


class ByProtocol:

	@classmethod
	def FromConfig(
		cls,
		dCollection: DownstreamCollection,
		endpoint: str,
		timeout: float = DEFAULT_TIMEOUT,
	) -> 'HTTPS':
		endpointObj = dCollection.GetEndpoint(endpoint)
		proto = endpointObj.proto

		if proto not in REMOTE_HANDLER_MAP:
			raise ValueError(f'Unsupported protocol: {proto}')

		remoteCls = REMOTE_HANDLER_MAP[proto]

		return remoteCls(
			endpoint=endpointObj,
			timeout=timeout
		)

