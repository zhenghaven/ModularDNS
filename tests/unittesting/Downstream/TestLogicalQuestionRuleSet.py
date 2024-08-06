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
from ModularDNS.Downstream.Logical import QuestionRuleSet
from ModularDNS.MsgEntry.QuestionEntry import QuestionEntry

from .TestLocalHosts import BuildTestingHosts, CountingHosts


class TestLogicalQuestionRuleSet(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_Downstream_Logical_QuestionRuleSet_01RuleMatching(self):
		hosts1 = BuildTestingHosts(cls=CountingHosts)
		hosts2 = BuildTestingHosts(cls=CountingHosts)

		ruleSet = QuestionRuleSet.QuestionRuleSet(
			ruleAndHandlers={
				'sub:->>google.com': hosts1,
				'full:->>google.com': hosts2,
			}
		)

		question1 = QuestionEntry(
			name=dns.name.from_text('dns.google.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
		)
		matchedHandler = ruleSet.MatchHandler(question1)
		# only the sub rule should match
		self.assertEqual(matchedHandler, hosts1)

		question2 = QuestionEntry(
			name=dns.name.from_text('google.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
		)
		matchedHandler = ruleSet.MatchHandler(question2)
		# both rules should match, but the full rule should have higher priority
		self.assertEqual(matchedHandler, hosts2)

		question3 = QuestionEntry(
			name=dns.name.from_text('microsoft.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
		)
		# no rule should match
		with self.assertRaises(RuntimeError):
			matchedHandler = ruleSet.MatchHandler(question3)

	def test_Downstream_Logical_QuestionRuleSet_02QuestionHandling(self):
		hosts1 = BuildTestingHosts(cls=CountingHosts)
		hosts2 = BuildTestingHosts(cls=CountingHosts)

		ruleSet = QuestionRuleSet.QuestionRuleSet(
			ruleAndHandlers={
				'sub:->>google.com': hosts1,
				'full:->>google.com': hosts2,
			}
		)
		hosts2.AddAddrRecord(
			domain='google.com',
			ipAddr=ipaddress.ip_address('123.132.213.231')
		)

		question1 = QuestionEntry(
			name=dns.name.from_text('dns.google.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
		)
		self.assertEqual(hosts1.GetCounter(), 0)
		# only the sub rule should match
		ans = ruleSet.HandleQuestion(
			msgEntry=question1,
			senderAddr=('localhost', 53),
			recDepthStack=[],
		)
		self.assertEqual(len(ans), 1)
		addr = ans[0].GetAddresses()
		addr = [str(x) for x in addr]
		self.assertIn('8.8.8.8', addr)
		self.assertEqual(hosts1.GetCounter(), 1)

		question2 = QuestionEntry(
			name=dns.name.from_text('google.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
		)
		self.assertEqual(hosts2.GetCounter(), 0)
		# both rules should match, but the full rule should have higher priority
		ans = ruleSet.HandleQuestion(
			msgEntry=question2,
			senderAddr=('localhost', 53),
			recDepthStack=[],
		)
		self.assertEqual(len(ans), 1)
		addr = ans[0].GetAddresses()
		addr = [str(x) for x in addr]
		self.assertIn('123.132.213.231', addr)
		self.assertEqual(hosts2.GetCounter(), 1)

	def test_Downstream_Logical_QuestionRuleSet_03FromConfig(self):
		hosts1 = BuildTestingHosts(cls=CountingHosts)
		hosts2 = BuildTestingHosts(cls=CountingHosts)
		dCollection = DownstreamCollection()
		dCollection.AddHandler('hosts1', hosts1)
		dCollection.AddHandler('hosts2', hosts2)

		ruleSet = QuestionRuleSet.QuestionRuleSet.FromConfig(
			dCollection=dCollection,
			ruleAndHandlers={
				'sub:->>google.com':  's:hosts1',
				'full:->>google.com': 's:hosts2',
			}
		)
		self.assertIsInstance(ruleSet, QuestionRuleSet.QuestionRuleSet)

