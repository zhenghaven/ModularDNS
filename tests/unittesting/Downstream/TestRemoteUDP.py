#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


from ModularDNS.Downstream.DownstreamCollection import DownstreamCollection
from ModularDNS.Downstream.Remote.ByProtocol import ByProtocol
from ModularDNS.Downstream.Remote.UDP import UDP
from ModularDNS.Downstream.Remote.Endpoint import StaticEndpoint

from .TestLocalHosts import BuildTestingHosts
from .TestRemote import TestRemote


class TestRemoteUDP(TestRemote):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_Downstream_Remote_UDP_01Lookup(self):
		remote = UDP(
			StaticEndpoint.FromURI(uri='udp://8.8.8.8', resolver=None),
		)

		self.StandardLookupTest(remote=remote)

	def test_Downstream_Remote_UDP_02FromConfig(self):
		hosts = BuildTestingHosts()
		dCollection = DownstreamCollection()
		dCollection.AddHandler('hosts', hosts)
		dCollection.AddEndpoint(
			'udp_google',
			StaticEndpoint.FromConfig(
				dCollection=dCollection,
				uri='udp://dns.google',
				resolver='s:hosts',
				preferIPv6=False
			)
		)

		remote = UDP.FromConfig(
			dCollection=dCollection,
			endpoint='udp_google',
			timeout=1.0
		)

		remote = ByProtocol.FromConfig(
			dCollection=dCollection,
			endpoint='udp_google',
			timeout=1.0
		)
		self.assertIsInstance(remote, UDP)

