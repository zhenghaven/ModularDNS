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

import dns.name
import dns.rdataclass
import dns.rdatatype

from ModularDNS.Downstream.DownstreamCollection import DownstreamCollection
from ModularDNS.Downstream.Logical.Failover import Failover
from ModularDNS.MsgEntry.QuestionEntry import QuestionEntry

from .TestLocalHosts import BuildTestingHosts, CountingHosts


class TestLogicalFailover(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_Downstream_Logical_FailOver_01Failover(self):
		hosts1 = BuildTestingHosts(cls=CountingHosts)
		hosts2 = BuildTestingHosts(cls=CountingHosts)

		# add a record only exists in hosts1
		test1Name = 'test1.example.com'
		test1Addr = ipaddress.ip_address('192.168.1.1')
		hosts1.AddAddrRecord(domain=test1Name, ipAddr=test1Addr)
		# add a record only exists in hosts2
		test2Name = 'test2.example.com'
		test2Addr = ipaddress.ip_address('192.168.1.2')
		hosts2.AddAddrRecord(domain=test2Name, ipAddr=test2Addr)

		# create a failover
		failover = Failover(
			initialHandler=hosts1,
			failoverHandler=hosts2,
		)

		# query for test1.example.com
		question1 = QuestionEntry(
			name=dns.name.from_text(test1Name),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
		)
		ans1 = failover.HandleQuestion(
			msgEntry=question1,
			senderAddr=('localhost', 0),
			recDepthStack=[],
		)
		# test if the initial handler is queried
		self.assertEqual(hosts1.GetCounter(), 1)
		# test if the failover handler is not queried
		self.assertEqual(hosts2.GetCounter(), 0)
		# test if the answer is correct
		self.assertEqual(len(ans1), 1)
		addr1 = ans1[0].GetAddresses()
		self.assertEqual(addr1, [test1Addr])

		# query for test2.example.com
		question2 = QuestionEntry(
			name=dns.name.from_text(test2Name),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
		)
		ans2 = failover.HandleQuestion(
			msgEntry=question2,
			senderAddr=('localhost', 0),
			recDepthStack=[],
		)
		# test if the initial handler is queried
		self.assertEqual(hosts1.GetCounter(), 2)
		# test if the failover handler is queried
		self.assertEqual(hosts2.GetCounter(), 1)
		# test if the answer is correct
		self.assertEqual(len(ans2), 1)
		addr2 = ans2[0].GetAddresses()
		self.assertEqual(addr2, [test2Addr])

	def test_Downstream_Logical_FailOver_02FromConfig(self):
		hosts1 = BuildTestingHosts()
		hosts2 = BuildTestingHosts()
		dCollection = DownstreamCollection()
		dCollection.AddHandler('hosts1', hosts1)
		dCollection.AddHandler('hosts2', hosts2)

		failover = Failover.FromConfig(
			dCollection=dCollection,
			initialHandler='s:hosts1',
			failoverHandler='s:hosts2',
			exceptList=Failover.DEFAULT_EXCEPT_STR_LIST,
		)
		self.assertIsInstance(failover, Failover)

