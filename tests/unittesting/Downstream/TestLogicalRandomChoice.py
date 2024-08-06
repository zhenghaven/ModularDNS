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
from ModularDNS.Downstream.Logical.RandomChoice import RandomChoice
from ModularDNS.MsgEntry.QuestionEntry import QuestionEntry

from .TestLocalHosts import BuildTestingHosts, CountingHosts


class TestLogicalRandomChoice(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_Downstream_Logical_RandomChoice_01RandomChoice(self):
		hosts1 = BuildTestingHosts(cls=CountingHosts)
		hosts2 = BuildTestingHosts(cls=CountingHosts)

		# add a testing record to both hosts1 and hosts2
		test1Name = 'test1.example.com'
		test1Addr = ipaddress.ip_address('192.168.1.1')
		hosts1.AddAddrRecord(domain=test1Name, ipAddr=test1Addr)
		hosts2.AddAddrRecord(domain=test1Name, ipAddr=test1Addr)

		# create a question for repeated testing
		question1 = QuestionEntry(
			name=dns.name.from_text(test1Name),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
		)

		# create a random choice, with
		#   - 70% chance to choose hosts1,
		#   - 30% chance to choose hosts2
		randomChoice = RandomChoice(
			handlerList=[hosts1, hosts2],
			weightList=[70, 30],
		)

		# test the random choice
		testRepeatTimes = 1000
		for _ in range(testRepeatTimes):
			ans = randomChoice.HandleQuestion(
				msgEntry=question1,
				senderAddr=('localhost', 0),
				recDepthStack=[],
			)
			# test if the answer is correct
			self.assertEqual(len(ans), 1)
			addr1 = ans[0].GetAddresses()
			self.assertEqual(addr1, [test1Addr])

		# test if the random choice is random enough
		# test if the number of times hosts1 is chosen
		# is within the range of [70% - 15%, 70% + 15%]
		hosts1Counter = hosts1.GetCounter()
		hosts1CounterLowerBound = testRepeatTimes * 0.70 - testRepeatTimes * 0.15
		hosts1CounterUpperBound = testRepeatTimes * 0.70 + testRepeatTimes * 0.15
		self.assertGreaterEqual(hosts1Counter, hosts1CounterLowerBound)
		self.assertLessEqual(hosts1Counter, hosts1CounterUpperBound)
		# test if the number of times hosts2 is chosen
		# is within the range of [30% - 15%, 30% + 15%]
		hosts2Counter = hosts2.GetCounter()
		hosts2CounterLowerBound = testRepeatTimes * 0.30 - testRepeatTimes * 0.15
		hosts2CounterUpperBound = testRepeatTimes * 0.30 + testRepeatTimes * 0.15
		self.assertGreaterEqual(hosts2Counter, hosts2CounterLowerBound)
		self.assertLessEqual(hosts2Counter, hosts2CounterUpperBound)

	def test_Downstream_Logical_RandomChoice_02FromConfig(self):
		hosts1 = BuildTestingHosts(cls=CountingHosts)
		hosts2 = BuildTestingHosts(cls=CountingHosts)
		dCollection = DownstreamCollection()
		dCollection.AddHandler('hosts1', hosts1)
		dCollection.AddHandler('hosts2', hosts2)

		randomChoice1 = RandomChoice.FromConfig(
			dCollection=dCollection,
			handlerList=['s:hosts1', 's:hosts2'],
		)
		self.assertIsInstance(randomChoice1, RandomChoice)

		randomChoice2 = RandomChoice.FromConfig(
			dCollection=dCollection,
			handlerList=['s:hosts1', 's:hosts2'],
			weightList=[70, 30],
		)
		self.assertIsInstance(randomChoice2, RandomChoice)

