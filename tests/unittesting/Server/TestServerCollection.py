#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import unittest

from ModularDNS.ModuleManagerLoader import MODULE_MGR
from ModularDNS.Downstream.DownstreamCollection import DownstreamCollection
from ModularDNS.Server.ServerCollection import ServerCollection

from ..Downstream.TestLocalHosts import BuildTestingHosts, TESTING_HOSTS_CONFIG


class TestServerCollection(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_Server_ServerCollection_01Server(self):
		downConfig = {
			'items': [
				{
					'module': 'Downstream.Local.Hosts',
					'name': 'hosts',
					'config': {
						'config': TESTING_HOSTS_CONFIG
					}
				},
			]
		}

		svrConfig = {
			'items': [
				{
					'module': 'Server.UDP',
					'name': 'server_udp',
					'config': {
						'ip': '127.0.0.1',
						'port': 0,
						'downstream': 's:hosts',
					}
				},
			]
		}

		with DownstreamCollection.FromConfig(
			moduleMgr=MODULE_MGR,
			config=downConfig
		) as dCollection:
			with ServerCollection.FromConfig(
				moduleMgr=MODULE_MGR,
				dCollection=dCollection,
				config=svrConfig,
			) as sCollection:
				self.assertIsInstance(sCollection, ServerCollection)
				self.assertEqual(sCollection.GetNumOfServers(), 1)
				sCollection.ThreadedServeUntilTerminate()

