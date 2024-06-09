#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import ipaddress
import threading
import unittest

from ModularDNS.Downstream.Remote.Remote import Remote


class TestRemote(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def StandardLookupTest(self, remote: Remote) -> None:

		ip = remote.LookupIpAddr(domain='dns.google', preferIPv6=False, recDepthStack=[])
		expIPStrs = [ '8.8.8.8', '8.8.4.4' ]
		expIPs = [ipaddress.ip_address(x) for x in expIPStrs]
		self.assertIn(ip, expIPs)

		ip = remote.LookupIpAddr(domain='dns.google', preferIPv6=True, recDepthStack=[])
		expIPStrs = [ '2001:4860:4860::8888', '2001:4860:4860::8844', ]
		expIPs = [ipaddress.ip_address(x) for x in expIPStrs]
		self.assertIn(ip, expIPs)

	def ConcurrentStandardLookupTest(self, remote: Remote, numOfThreads: int) -> None:
		threads = [
			threading.Thread(
				target=self.StandardLookupTest,
				args=(remote, ),
			)
			for _ in range(numOfThreads)
		]
		for t in threads:
			t.start()

		# clean up threads
		for t in threads:
			t.join()

