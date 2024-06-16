#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import copy
import unittest

import dns.name
import dns.rdataclass
import dns.rdatatype

from ModularDNS.MsgEntry.QuestionEntry import QuestionEntry, MsgEntry


class TestQuestionEntry(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_QuestionEntry_1Hashable(self):
		questionEntry1 = QuestionEntry(
			name=dns.name.from_text('google.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
		)

		questionEntry2 = QuestionEntry(
			name=dns.name.from_text('google.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
		)

		self.assertEqual(questionEntry1, questionEntry2)
		self.assertEqual(hash(questionEntry1), hash(questionEntry2))

		# Different name
		questionEntry3 = QuestionEntry(
			name=dns.name.from_text('www.google.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.AAAA,
		)

		self.assertNotEqual(questionEntry1, questionEntry3)
		self.assertNotEqual(hash(questionEntry1), hash(questionEntry3))

		# Different rdCls
		questionEntry4 = QuestionEntry(
			name=dns.name.from_text('google.com'),
			rdCls=dns.rdataclass.CH,
			rdType=dns.rdatatype.A,
		)
		self.assertNotEqual(questionEntry1, questionEntry4)
		self.assertNotEqual(hash(questionEntry1), hash(questionEntry4))

		# Different rdType
		questionEntry5 = QuestionEntry(
			name=dns.name.from_text('google.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.AAAA,
		)
		self.assertNotEqual(questionEntry1, questionEntry5)
		self.assertNotEqual(hash(questionEntry1), hash(questionEntry5))

		# Different classes
		msgEntry = MsgEntry(entryType=questionEntry1.entryType)
		self.assertNotEqual(questionEntry1, msgEntry)

	def test_QuestionEntry_2Copy(self):
		questionEntry = QuestionEntry(
			name=dns.name.from_text('google.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
		)

		questionEntryCopy = copy.copy(questionEntry)

		self.assertEqual(questionEntry, questionEntryCopy)
		self.assertEqual(questionEntry.name, questionEntryCopy.name)
		self.assertEqual(questionEntry.rdCls, questionEntryCopy.rdCls)
		self.assertEqual(questionEntry.rdType, questionEntryCopy.rdType)

		questionEntryCopy.name = dns.name.from_text('www.google.com')

		self.assertNotEqual(questionEntry, questionEntryCopy)
		self.assertNotEqual(questionEntry.name, questionEntryCopy.name)
		self.assertEqual(questionEntry.rdCls, questionEntryCopy.rdCls)
		self.assertEqual(questionEntry.rdType, questionEntryCopy.rdType)

	def test_QuestionEntry_3DeepCopy(self):
		questionEntry = QuestionEntry(
			name=dns.name.from_text('google.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
		)

		questionEntryCopy = copy.deepcopy(questionEntry)

		self.assertEqual(questionEntry, questionEntryCopy)
		self.assertEqual(questionEntry.name, questionEntryCopy.name)
		self.assertEqual(questionEntry.rdCls, questionEntryCopy.rdCls)
		self.assertEqual(questionEntry.rdType, questionEntryCopy.rdType)

		questionEntryCopy.name = dns.name.from_text('www.google.com')

		self.assertNotEqual(questionEntry, questionEntryCopy)
		self.assertNotEqual(questionEntry.name, questionEntryCopy.name)
		self.assertEqual(questionEntry.rdCls, questionEntryCopy.rdCls)
		self.assertEqual(questionEntry.rdType, questionEntryCopy.rdType)

