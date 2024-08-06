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

from ModularDNS.Downstream.Handler import DownstreamHandler

from ModularDNS.Downstream.Local.Cache import Cache
from ModularDNS.Downstream.Local.Hosts import Hosts
from ModularDNS.Downstream.Logical.Failover import Failover
from ModularDNS.Downstream.Logical.LimitConcurrentReq import LimitConcurrentReq
from ModularDNS.Downstream.Logical.QuestionRuleSet import QuestionRuleSet
from ModularDNS.Downstream.Logical.RaiseExcept import RaiseExcept
from ModularDNS.Downstream.Logical.RandomChoice import RandomChoice
from ModularDNS.Downstream.Remote.ByProtocol import ByProtocol
from ModularDNS.Downstream.Remote.Endpoint import Endpoint, StaticEndpoint
from ModularDNS.Downstream.Remote.HTTPS import HTTPS
from ModularDNS.Downstream.Remote.UDP import UDP


class TestModuleManagerLoaders(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_ModuleManagerLoader_01RegisterAndGetModule(self):
		self.assertEqual(MODULE_MGR.GetModule('Downstream.Local.Cache'), Cache)
		self.assertEqual(MODULE_MGR.GetModule('Downstream.Local.Hosts'), Hosts)
		self.assertEqual(MODULE_MGR.GetModule('Downstream.Logical.Failover'), Failover)
		self.assertEqual(MODULE_MGR.GetModule('Downstream.Logical.LimitConcurrentReq'), LimitConcurrentReq)
		self.assertEqual(MODULE_MGR.GetModule('Downstream.Logical.QuestionRuleSet'), QuestionRuleSet)
		self.assertEqual(MODULE_MGR.GetModule('Downstream.Logical.RaiseExcept'), RaiseExcept)
		self.assertEqual(MODULE_MGR.GetModule('Downstream.Logical.RandomChoice'), RandomChoice)
		self.assertEqual(MODULE_MGR.GetModule('Downstream.Remote.ByProtocol'), ByProtocol)
		self.assertEqual(MODULE_MGR.GetModule('Downstream.Remote.Endpoint'), Endpoint)
		self.assertEqual(MODULE_MGR.GetModule('Downstream.Remote.StaticEndpoint'), StaticEndpoint)
		self.assertEqual(MODULE_MGR.GetModule('Downstream.Remote.HTTPS'), HTTPS)
		self.assertEqual(MODULE_MGR.GetModule('Downstream.Remote.UDP'), UDP)

		self.assertTrue(
			issubclass(
				MODULE_MGR.GetModule('Downstream.Local.Cache'),
				DownstreamHandler
			)
		)
		self.assertTrue(
			issubclass(
				MODULE_MGR.GetModule('Downstream.Local.Hosts'),
				DownstreamHandler
			)
		)
		self.assertTrue(
			issubclass(
				MODULE_MGR.GetModule('Downstream.Logical.Failover'),
				DownstreamHandler
			)
		)
		self.assertTrue(
			issubclass(
				MODULE_MGR.GetModule('Downstream.Logical.LimitConcurrentReq'),
				DownstreamHandler
			)
		)
		self.assertTrue(
			issubclass(
				MODULE_MGR.GetModule('Downstream.Logical.QuestionRuleSet'),
				DownstreamHandler
			)
		)
		self.assertTrue(
			issubclass(
				MODULE_MGR.GetModule('Downstream.Logical.RaiseExcept'),
				DownstreamHandler
			)
		)
		self.assertTrue(
			issubclass(
				MODULE_MGR.GetModule('Downstream.Logical.RandomChoice'),
				DownstreamHandler
			)
		)
		self.assertEqual(
			MODULE_MGR.GetModule('Downstream.Remote.ByProtocol'),
			ByProtocol
		)
		self.assertTrue(
			issubclass(
				MODULE_MGR.GetModule('Downstream.Remote.Endpoint'),
				Endpoint
			)
		)
		self.assertTrue(
			issubclass(
				MODULE_MGR.GetModule('Downstream.Remote.StaticEndpoint'),
				Endpoint
			)
		)
		self.assertTrue(
			issubclass(
				MODULE_MGR.GetModule('Downstream.Remote.HTTPS'),
				DownstreamHandler
			)
		)
		self.assertTrue(
			issubclass(
				MODULE_MGR.GetModule('Downstream.Remote.UDP'),
				DownstreamHandler
			)
		)

		with self.assertRaises(KeyError):
			MODULE_MGR.GetModule('SomethingNotExists')

		with self.assertRaises(KeyError):
			MODULE_MGR.GetModule('Downstream')

		with self.assertRaises(KeyError):
			MODULE_MGR.GetModule('Downstream.')

		with self.assertRaises(KeyError):
			MODULE_MGR.GetModule('Downstream.SomethingNotExists')

