#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import logging

from ModularDNS.Downstream.DownstreamCollection import DownstreamCollection
from ModularDNS.Downstream.Remote.ByProtocol import ByProtocol
from ModularDNS.Downstream.Remote.TCP import TCP
from ModularDNS.Downstream.Remote.Endpoint import StaticEndpoint

from .TestLocalHosts import BuildTestingHosts
from .TestRemote import TestRemote


class TestRemoteTCP(TestRemote):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_Downstream_Remote_TCP_01Lookup(self):
		logging.getLogger().info('')

		hosts = BuildTestingHosts()
		with TCP(
			StaticEndpoint.FromURI(uri='tcp://dns.google', resolver=hosts),
		) as remote:
			self.StandardLookupTest(remote=remote)

	def test_Downstream_Remote_TCP_02Concurrent(self):
		logging.getLogger().info('')

		hosts = BuildTestingHosts()
		with TCP(
			StaticEndpoint.FromURI(uri='tcp://dns.google', resolver=hosts),
		) as remote:

			self.assertEqual(len(remote.underlying.cache), 0)

			self.ConcurrentStandardLookupTest(remote=remote, numOfThreads=10)

			self.assertGreater(len(remote.underlying.cache), 2)
			self.assertGreater(remote.underlying.cache.NumberOfIdle(), 2)

			self.ConcurrentStandardLookupTest(remote=remote, numOfThreads=5)

	def test_Downstream_Remote_TCP_03FromConfig(self):
		hosts = BuildTestingHosts()
		dCollection = DownstreamCollection()
		dCollection.AddHandler('hosts', hosts)
		dCollection.AddEndpoint(
			'tcp_google',
			StaticEndpoint.FromConfig(
				dCollection=dCollection,
				uri='tcp://dns.google',
				resolver='s:hosts',
				preferIPv6=False
			)
		)

		with TCP.FromConfig(
			dCollection=dCollection,
			endpoint='tcp_google',
			timeout=1.0
		) as remote:
			self.assertIsInstance(remote, TCP)

		with ByProtocol.FromConfig(
			dCollection=dCollection,
			endpoint='tcp_google',
			timeout=1.0
		) as remote:
			self.assertIsInstance(remote, TCP)

