#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import ipaddress
import unittest

from ModularDNS.Downstream.Remote.UDP import UDP
from ModularDNS.Downstream.Remote.Endpoint import Endpoint


class TestRemoteUDP(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_Remote_UDP_1Lookup(self):
		udp = UDP(
			Endpoint.FromURI(uri='udp://8.8.8.8', resolver=None),
		)

		ip = udp.LookupIpAddr(domain='dns.google', preferIPv6=False, recDepthStack=[])
		expIPStrs = [ '8.8.8.8', '8.8.4.4' ]
		expIPs = [ipaddress.ip_address(x) for x in expIPStrs]
		self.assertIn(ip, expIPs)

		ip = udp.LookupIpAddr(domain='dns.google', preferIPv6=True, recDepthStack=[])
		expIPStrs = [ '2001:4860:4860::8888', '2001:4860:4860::8844', ]
		expIPs = [ipaddress.ip_address(x) for x in expIPStrs]
		self.assertIn(ip, expIPs)

