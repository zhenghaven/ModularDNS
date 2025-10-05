#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import unittest

import dns.name
import dns.rdataclass
import dns.rdatatype

from ModularDNS.Exceptions import DNSNameNotFoundError
from ModularDNS.Downstream.DownstreamCollection import DownstreamCollection
from ModularDNS.Downstream.Logical import ConstAns
from ModularDNS.MsgEntry.AnsEntry import AnsEntry
from ModularDNS.MsgEntry.QuestionEntry import QuestionEntry


class TestLogicalConstAns(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_Downstream_Logical_ConstAns_01GetAns(self):
		# create a handler that raises an exception
		handler1 = ConstAns.ConstAns(
			recDict={
				dns.rdatatype.A: ['127.0.0.1'],
				dns.rdatatype.AAAA: ['::1'],
			}
		)

		test1Name = 'test1.example.com'
		# query for test1.example.com
		question1 = QuestionEntry(
			name=dns.name.from_text(test1Name),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
		)
		ans1 = handler1.HandleQuestion(
			msgEntry=question1,
			senderAddr=('localhost', 0),
			recDepthStack=[],
		)
		self.assertEqual(len(ans1), 1)
		self.assertIsInstance(ans1[0], AnsEntry)
		asnEntry: AnsEntry = ans1[0]
		self.assertEqual(asnEntry.name.to_text(), test1Name + '.')
		self.assertEqual(asnEntry.rdCls, dns.rdataclass.IN)
		self.assertEqual(asnEntry.rdType, dns.rdatatype.A)
		self.assertEqual(len(asnEntry.dataList), 1)
		self.assertEqual(asnEntry.dataList[0].to_text(), '127.0.0.1')

		test2Name = 'test2.example.com'
		# query for test2.example.com
		question2 = QuestionEntry(
			name=dns.name.from_text(test2Name),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
		)
		ans2 = handler1.HandleQuestion(
			msgEntry=question2,
			senderAddr=('localhost', 0),
			recDepthStack=[],
		)
		self.assertEqual(len(ans2), 1)
		self.assertIsInstance(ans2[0], AnsEntry)
		asnEntry: AnsEntry = ans2[0]
		self.assertEqual(asnEntry.name.to_text(), test2Name + '.')
		self.assertEqual(asnEntry.rdCls, dns.rdataclass.IN)
		self.assertEqual(asnEntry.rdType, dns.rdatatype.A)
		self.assertEqual(len(asnEntry.dataList), 1)
		self.assertEqual(asnEntry.dataList[0].to_text(), '127.0.0.1')

		# query for test2.example.com AAAA
		question3 = QuestionEntry(
			name=dns.name.from_text(test2Name),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.AAAA,
		)
		ans3 = handler1.HandleQuestion(
			msgEntry=question3,
			senderAddr=('localhost', 0),
			recDepthStack=[],
		)
		self.assertEqual(len(ans3), 1)
		self.assertIsInstance(ans3[0], AnsEntry)
		asnEntry: AnsEntry = ans3[0]
		self.assertEqual(asnEntry.name.to_text(), test2Name + '.')
		self.assertEqual(asnEntry.rdCls, dns.rdataclass.IN)
		self.assertEqual(asnEntry.rdType, dns.rdatatype.AAAA)
		self.assertEqual(len(asnEntry.dataList), 1)
		self.assertEqual(asnEntry.dataList[0].to_text(), '::1')

	def test_Downstream_Logical_ConstAns_02FromConfig(self):
		dCollection = DownstreamCollection()

		handler1 = ConstAns.ConstAns.FromConfig(
			dCollection=dCollection,
			records=[
				['A', '127.0.0.1'],
				['AAAA', '::1'],
			]
		)
		self.assertIsInstance(handler1, ConstAns.ConstAns)

