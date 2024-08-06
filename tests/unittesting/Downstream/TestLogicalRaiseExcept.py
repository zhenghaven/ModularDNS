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
from ModularDNS.Downstream.Logical import RaiseExcept
from ModularDNS.MsgEntry.QuestionEntry import QuestionEntry


class TestLogicalRaiseExcept(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_Downstream_Logical_RaiseExcept_01RaiseExcept(self):
		# create a handler that raises an exception
		raiseExceptHandler1 = RaiseExcept.RaiseExcept(
			exceptToRaise=DNSNameNotFoundError,
			exceptKwargs={
				'name': 'test1.example.com',
				'respServer': 'TestLogicalRaiseExcept',
			}
		)
		raiseExceptHandler2 = RaiseExcept.RaiseExcept(
			exceptToRaise=DNSNameNotFoundError,
			exceptArgs=(
				'test1.example.com',
				'TestLogicalRaiseExcept',
			)
		)

		test1Name = 'test1.example.com'
		# query for test1.example.com
		question1 = QuestionEntry(
			name=dns.name.from_text(test1Name),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
		)

		with self.assertRaises(DNSNameNotFoundError):
			raiseExceptHandler1.HandleQuestion(
				msgEntry=question1,
				senderAddr=('localhost', 0),
				recDepthStack=[],
			)

		with self.assertRaises(DNSNameNotFoundError):
			raiseExceptHandler2.HandleQuestion(
				msgEntry=question1,
				senderAddr=('localhost', 0),
				recDepthStack=[],
			)

	def test_Downstream_Logical_RaiseExcept_02FromConfig(self):
		dCollection = DownstreamCollection()

		raiseExceptHandler1 = RaiseExcept.RaiseExcept.FromConfig(
			dCollection=dCollection,
			exceptToRaise='DNSNameNotFoundError',
			exceptKwargs={
				'name': 'test1.example.com',
				'respServer': 'TestLogicalRaiseExcept',
			}
		)
		self.assertIsInstance(raiseExceptHandler1, RaiseExcept.RaiseExcept)

		raiseExceptHandler2 = RaiseExcept.RaiseExcept.FromConfig(
			dCollection=dCollection,
			exceptToRaise='DNSNameNotFoundError',
			exceptArgs=[
				'test1.example.com',
				'TestLogicalRaiseExcept',
			]
		)
		self.assertIsInstance(raiseExceptHandler2, RaiseExcept.RaiseExcept)

