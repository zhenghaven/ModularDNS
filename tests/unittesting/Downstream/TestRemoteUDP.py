#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


from ModularDNS.Downstream.DownstreamCollection import DownstreamCollection
from ModularDNS.Downstream.Logical.RaiseExcept import RaiseExcept
from ModularDNS.Downstream.Remote.ByProtocol import ByProtocol
from ModularDNS.Downstream.Remote.UDP import UDP
from ModularDNS.Downstream.Remote.Endpoint import StaticEndpoint
from ModularDNS.Exceptions import DNSServerFaultError

from .TestLocalHosts import BuildTestingHosts
from .TestRemote import TestRemote


class TestRemoteUDP(TestRemote):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_Downstream_Remote_UDP_01Lookup(self):
		with UDP(
			StaticEndpoint.FromURI(
				uri='udp://8.8.8.8',
				resolver=RaiseExcept(
					exceptToRaise=DNSServerFaultError,
					exceptKwargs={
						'reason': 'Endpoint already knows the IP address',
					}
				)
			),
		) as remote:
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

		with UDP.FromConfig(
			dCollection=dCollection,
			endpoint='udp_google',
			timeout=1.0
		) as remote:
			self.assertIsInstance(remote, UDP)

		with ByProtocol.FromConfig(
			dCollection=dCollection,
			endpoint='udp_google',
			timeout=1.0
		) as remote:
			self.assertIsInstance(remote, UDP)

