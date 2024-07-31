#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import logging

from ModularDNS.Downstream.Remote.HTTPS import HTTPS
from ModularDNS.Downstream.Remote.Endpoint import StaticEndpoint

from .TestLocalHosts import BuildTestingHosts
from .TestRemote import TestRemote


class TestRemoteHTTPS(TestRemote):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_Downstream_Remote_HTTPS_1Lookup(self):
		logging.getLogger().info('')

		hosts = BuildTestingHosts()
		remote = HTTPS(
			StaticEndpoint.FromURI(uri='https://dns.google', resolver=hosts),
		)
		self.StandardLookupTest(remote=remote)

	def test_Downstream_Remote_HTTPS_2Concurrent(self):
		logging.getLogger().info('')

		hosts = BuildTestingHosts()
		remote = HTTPS(
			StaticEndpoint.FromURI(uri='https://dns.google', resolver=hosts),
		)

		self.assertEqual(len(remote.underlying.cache), 0)

		self.ConcurrentStandardLookupTest(remote=remote, numOfThreads=10)

		self.assertGreater(len(remote.underlying.cache), 2)
		self.assertGreater(remote.underlying.cache.NumberOfIdle(), 2)

		self.ConcurrentStandardLookupTest(remote=remote, numOfThreads=5)

