#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import logging
import time
import unittest

import dns.message
import dns.query
import dns.rcode
import dns.rdataclass
import dns.rdatatype

from ModularDNS.Downstream.DownstreamCollection import DownstreamCollection
from ModularDNS.Server import UDP

from ..Downstream.TestLocalHosts import BuildTestingHosts


class TestUDP(unittest.TestCase):

	def setUp(self):
		self.logger = logging.getLogger(f'{__name__}.{self.__class__.__name__}')

		self.suitStartTime = time.time()

		hosts = BuildTestingHosts()
		self.dCollection = DownstreamCollection()
		self.dCollection.AddHandler('hosts', hosts)

		self.srcAddr = '127.0.0.1'
		self.server = UDP.UDP.FromConfig(
			dCollection=self.dCollection,
			ip=self.srcAddr,
			port=0,
			downstream='s:hosts',
		)
		self.srcPort = self.server.GetSrcPort()

		self.logger.info(f'UDP server is listening on {self.srcAddr}:{self.srcPort}')

		self.server.ThreadedServeUntilTerminate()

	def tearDown(self):
		self.server.Terminate()

		elapseTime = time.time() - self.suitStartTime
		self.logger.info(f'Test suite took {elapseTime:.3f} seconds')

	def test_Server_UDP_01MsgHandling(self):
		queryName = 'dns.google.com'
		dnsMsg = dns.message.make_query(
			queryName,
			rdclass=dns.rdataclass.IN,
			rdtype=dns.rdatatype.A,
		)

		startTime = time.time()
		resp = dns.query.udp(
			q=dnsMsg,
			where=self.srcAddr,
			port=self.srcPort,
			timeout=1,
		)
		elapseTime = time.time() - startTime

		self.assertIsInstance(resp, dns.message.Message)
		self.assertEqual(resp.rcode(), dns.rcode.NOERROR)
		self.assertGreaterEqual(len(resp.answer), 1)
		self.assertIn('8.8.8.8', [r.address for r in resp.answer[0].items])

		self.logger.info(f'Query {queryName} took {elapseTime:.3f} seconds')

