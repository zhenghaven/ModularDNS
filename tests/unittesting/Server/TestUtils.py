#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import logging
import unittest

import dns.message
import dns.rcode
import dns.rdataclass
import dns.rdatatype

from ModularDNS.Downstream.Logical.RaiseExcept import RaiseExcept
from ModularDNS.Exceptions import (
	DNSException,
	DNSNameNotFoundError,
	DNSRequestRefusedError,
	DNSServerFaultError,
	DNSZeroAnswerError,
)
from ModularDNS.Server import Utils

from ..Downstream.TestLocalHosts import BuildTestingHosts


class TestUtils(unittest.TestCase):

	def setUp(self):
		self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

	def tearDown(self):
		pass

	def test_Server_Utils_01CommonDNSMsgHandling(self):
		self.logger.info('')

		queryName = 'dns.google.com'
		dnsMsg = dns.message.make_query(
			queryName,
			rdclass=dns.rdataclass.IN,
			rdtype=dns.rdatatype.A,
		)
		senderAddr = ('127.0.0.1', 12345)
		toAddr = ('127.0.0.1', 53)

		# normal case it should return a dns.message.Message object containing
		# valid answers
		with BuildTestingHosts() as hosts:
			dnsMsgAns = Utils.CommonDNSMsgHandling(
				dnsMsg=dnsMsg,
				senderAddr=senderAddr,
				downstreamHdlr=hosts,
				logger=self.logger,
			)
			self.assertIsInstance(dnsMsgAns, dns.message.Message)
			self.assertEqual(dnsMsgAns.rcode(), dns.rcode.NOERROR)
			self.assertGreaterEqual(len(dnsMsgAns.answer), 1)

		# case that the server refuses the query
		with RaiseExcept(
			exceptToRaise=DNSRequestRefusedError,
			exceptKwargs={
				'sendAddr': senderAddr,
				'toAddr': toAddr,
			}
		) as exceptHdlr:
			dnsMsgAns = Utils.CommonDNSMsgHandling(
				dnsMsg=dnsMsg,
				senderAddr=senderAddr,
				downstreamHdlr=exceptHdlr,
				logger=self.logger,
			)
			self.assertIsInstance(dnsMsgAns, dns.message.Message)
			self.assertEqual(dnsMsgAns.rcode(), dns.rcode.REFUSED)

		# case that the domain name is not found
		with RaiseExcept(
			exceptToRaise=DNSNameNotFoundError,
			exceptKwargs={
				'name': queryName,
				'respServer': str(senderAddr),
			}
		) as exceptHdlr:
			dnsMsgAns = Utils.CommonDNSMsgHandling(
				dnsMsg=dnsMsg,
				senderAddr=senderAddr,
				downstreamHdlr=exceptHdlr,
				logger=self.logger,
			)
			self.assertIsInstance(dnsMsgAns, dns.message.Message)
			self.assertEqual(dnsMsgAns.rcode(), dns.rcode.NXDOMAIN)

		# case that the domain name exists but the query has no corresponding
		# answers
		with RaiseExcept(
			exceptToRaise=DNSZeroAnswerError,
			exceptKwargs={
				'name': queryName,
			}
		) as exceptHdlr:
			dnsMsgAns = Utils.CommonDNSMsgHandling(
				dnsMsg=dnsMsg,
				senderAddr=senderAddr,
				downstreamHdlr=exceptHdlr,
				logger=self.logger,
			)
			self.assertIsInstance(dnsMsgAns, dns.message.Message)
			self.assertEqual(dnsMsgAns.rcode(), dns.rcode.NOERROR)
			self.assertEqual(len(dnsMsgAns.answer), 0)

		# case that the server has internal error
		with RaiseExcept(
			exceptToRaise=DNSServerFaultError,
			exceptKwargs={
				'reason': 'Test that intentionally raise DNSServerFaultError',
			}
		) as exceptHdlr:
			dnsMsgAns = Utils.CommonDNSMsgHandling(
				dnsMsg=dnsMsg,
				senderAddr=senderAddr,
				downstreamHdlr=exceptHdlr,
				logger=self.logger,
			)
			self.assertIsInstance(dnsMsgAns, dns.message.Message)
			self.assertEqual(dnsMsgAns.rcode(), dns.rcode.SERVFAIL)

		# case that the server has unknown error
		with RaiseExcept(
			exceptToRaise=DNSException,
			exceptKwargs={
				'reason': 'Test that intentionally raise DNSException',
			}
		) as exceptHdlr:
			dnsMsgAns = Utils.CommonDNSMsgHandling(
				dnsMsg=dnsMsg,
				senderAddr=senderAddr,
				downstreamHdlr=exceptHdlr,
				logger=self.logger,
			)
			self.assertIsInstance(dnsMsgAns, dns.message.Message)
			self.assertEqual(dnsMsgAns.rcode(), dns.rcode.SERVFAIL)

