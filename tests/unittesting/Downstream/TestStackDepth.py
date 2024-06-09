#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import unittest

from ModularDNS.Downstream.Remote.UDP import UDP
from ModularDNS.Downstream.Remote.Endpoint import Endpoint
from ModularDNS.Downstream.Handler import RecursionDepthError


class TestStackDepth(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_StackDepth_1ExceedMaxDepth(self):
		udp = UDP(
			Endpoint.FromURI(uri='udp://dns.google', resolver=None),
		)

		# make the endpoint of the udp object point to udp
		# so a recursive loop will be created
		udp.underlying.endpoint.resolver = udp

		with self.assertRaises(RecursionDepthError):
			udp.LookupIpAddr(domain='dns.google', preferIPv6=False, recDepthStack=[])

		# remove the circular reference
		udp.underlying.endpoint.resolver = None

