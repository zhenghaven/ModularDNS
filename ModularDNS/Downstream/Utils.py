#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import logging

from typing import Any

import dns.message
import dns.rcode

from ..Exceptions import(
	DNSNameNotFoundError,
	DNSRequestRefusedError,
	DNSServerFaultError,
)


def CommonDNSRespHandling(
	dnsMsg: dns.message.Message,
	remote: Any,
	queryName: str,
	logger: logging.Logger,
) -> dns.message.Message:
	if dnsMsg.rcode() == dns.rcode.NOERROR:
		return dnsMsg
	if dnsMsg.rcode() == dns.rcode.REFUSED:
		e = DNSRequestRefusedError('local', remote)
		logger.debug(str(e))
		raise e
	if dnsMsg.rcode() == dns.rcode.SERVFAIL:
		errMsg = f'The remote server {remote} failed to process the request' \
			f' for name {queryName}'
		raise DNSServerFaultError(errMsg)
	if dnsMsg.rcode() == dns.rcode.NXDOMAIN:
		raise DNSNameNotFoundError(queryName, remote)
	else:
		errMsg = f'The remote server {remote} returned' \
			f' unsupported error code {dnsMsg.rcode()}' \
			f' for name {queryName}'
		raise DNSServerFaultError(errMsg)

