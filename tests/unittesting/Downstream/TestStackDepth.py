#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import unittest

from ModularDNS.Downstream.DownstreamCollection import StaticSharedQuickLookup
from ModularDNS.Downstream.Remote.UDP import UDP
from ModularDNS.Downstream.Remote.Endpoint import Endpoint
from ModularDNS.Downstream.Handler import RecursionDepthError


class TestStackDepth(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_StackDepth_1ExceedMaxDepth(self):
		with UDP(
			Endpoint.FromURI(uri='udp://dns.google', resolver=None),
		) as remote:

			sharedRemote = StaticSharedQuickLookup(handler=remote)

			# make the endpoint of the udp object point to udp
			# so a recursive loop will be created
			remote.underlying.endpoint.resolver = sharedRemote

			with self.assertRaises(RecursionDepthError):
				remote.LookupIpAddr(domain='dns.google', preferIPv6=False, recDepthStack=[])

