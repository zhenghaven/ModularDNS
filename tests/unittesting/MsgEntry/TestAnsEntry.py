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
import dns.rdata
import dns.rdataclass
import dns.rdatatype

from ModularDNS.MsgEntry.AnsEntry import AnsEntry, MsgEntry


class TestAnsEntry(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_MsgEntry_AnsEntry_1Equal(self):
		ansEntry1 = AnsEntry(
			name=dns.name.from_text('dns.google.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
			ttl=300,
			dataList=[
				dns.rdata.from_text(dns.rdataclass.IN, dns.rdatatype.A, '8.8.8.8'),
				dns.rdata.from_text(dns.rdataclass.IN, dns.rdatatype.A, '8.8.4.4'),
			],
		)
		self.assertEqual(ansEntry1.entryType, 'ANS')

		ansEntry2 = AnsEntry(
			name=dns.name.from_text('dns.google.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
			ttl=300,
			dataList=[
				dns.rdata.from_text(dns.rdataclass.IN, dns.rdatatype.A, '8.8.8.8'),
				dns.rdata.from_text(dns.rdataclass.IN, dns.rdatatype.A, '8.8.4.4'),
			],
		)
		self.assertEqual(ansEntry2.entryType, 'ANS')

		self.assertEqual(ansEntry1, ansEntry2)
		self.assertEqual(hash(ansEntry1), hash(ansEntry2))

		# a AnsEntry has a empty dataList
		ansEntryEmpty = AnsEntry(
			name=dns.name.from_text('dns.google.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
			ttl=300,
			dataList=[],
		)

		# Different name
		ansEntry3 = AnsEntry(
			name=dns.name.from_text('dns.google'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
			ttl=300,
			dataList=[
				dns.rdata.from_text(dns.rdataclass.IN, dns.rdatatype.A, '8.8.8.8'),
				dns.rdata.from_text(dns.rdataclass.IN, dns.rdatatype.A, '8.8.4.4'),
			],
		)

		self.assertNotEqual(ansEntry1, ansEntry3)
		self.assertNotEqual(hash(ansEntry1), hash(ansEntry3))

		# Different rdCls
		ansEntry4 = AnsEntry(
			name=dns.name.from_text('dns.google.com'),
			rdCls=dns.rdataclass.ANY,
			rdType=dns.rdatatype.A,
			ttl=300,
			dataList=[],
		)

		self.assertNotEqual(ansEntryEmpty, ansEntry4)
		self.assertNotEqual(hash(ansEntryEmpty), hash(ansEntry4))

		# Different rdType
		ansEntry5 = AnsEntry(
			name=dns.name.from_text('dns.google.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.AAAA,
			ttl=300,
			dataList=[],
		)

		self.assertNotEqual(ansEntryEmpty, ansEntry5)
		self.assertNotEqual(hash(ansEntryEmpty), hash(ansEntry5))

		# Different ttl
		ansEntry6 = AnsEntry(
			name=dns.name.from_text('dns.google.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
			ttl=3600,
			dataList=[
				dns.rdata.from_text(dns.rdataclass.IN, dns.rdatatype.A, '8.8.8.8'),
				dns.rdata.from_text(dns.rdataclass.IN, dns.rdatatype.A, '8.8.4.4'),
			],
		)

		self.assertNotEqual(ansEntry1, ansEntry6)
		self.assertNotEqual(hash(ansEntry1), hash(ansEntry6))

		# Different dataList
		ansEntry7 = AnsEntry(
			name=dns.name.from_text('dns.google.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
			ttl=300,
			dataList=[
				dns.rdata.from_text(dns.rdataclass.IN, dns.rdatatype.A, '8.8.8.8'),
			],
		)

		# Different classes
		msgEntry = MsgEntry(entryType=ansEntry1.entryType)
		self.assertNotEqual(ansEntry1, msgEntry)

	def test_MsgEntry_AnsEntry_2Copy(self):
		ansEntry1 = AnsEntry(
			name=dns.name.from_text('dns.google.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
			ttl=300,
			dataList=[
				dns.rdata.from_text(dns.rdataclass.IN, dns.rdatatype.A, '8.8.8.8'),
				dns.rdata.from_text(dns.rdataclass.IN, dns.rdatatype.A, '8.8.4.4'),
			],
		)

		ansEntryCopy = copy.copy(ansEntry1)
		self.assertEqual(ansEntry1, ansEntryCopy)
		self.assertEqual(ansEntry1.name, ansEntryCopy.name)
		self.assertEqual(ansEntry1.rdCls, ansEntryCopy.rdCls)
		self.assertEqual(ansEntry1.rdType, ansEntryCopy.rdType)
		self.assertEqual(ansEntry1.ttl, ansEntryCopy.ttl)
		self.assertEqual(ansEntry1.dataList, ansEntryCopy.dataList)

		# Change the name of the copy
		ansEntryCopy.name = dns.name.from_text('dns.google')
		self.assertNotEqual(ansEntry1, ansEntryCopy)
		self.assertNotEqual(ansEntry1.name, ansEntryCopy.name)
		self.assertEqual(ansEntry1.rdCls, ansEntryCopy.rdCls)
		self.assertEqual(ansEntry1.rdType, ansEntryCopy.rdType)
		self.assertEqual(ansEntry1.ttl, ansEntryCopy.ttl)
		self.assertEqual(ansEntry1.dataList, ansEntryCopy.dataList)

		ansEntryCopy = copy.copy(ansEntry1)
		self.assertEqual(ansEntry1, ansEntryCopy)

		# Change the dataList of the copy
		ansEntryCopy.dataList.pop()
		self.assertNotEqual(ansEntry1, ansEntryCopy)
		self.assertEqual(ansEntry1.name, ansEntryCopy.name)
		self.assertEqual(ansEntry1.rdCls, ansEntryCopy.rdCls)
		self.assertEqual(ansEntry1.rdType, ansEntryCopy.rdType)
		self.assertEqual(ansEntry1.ttl, ansEntryCopy.ttl)
		self.assertNotEqual(ansEntry1.dataList, ansEntryCopy.dataList)

	def test_MsgEntry_AnsEntry_3DeepCopy(self):
		ansEntry1 = AnsEntry(
			name=dns.name.from_text('dns.google.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
			ttl=300,
			dataList=[
				dns.rdata.from_text(dns.rdataclass.IN, dns.rdatatype.A, '8.8.8.8'),
				dns.rdata.from_text(dns.rdataclass.IN, dns.rdatatype.A, '8.8.4.4'),
			],
		)

		ansEntryCopy = copy.deepcopy(ansEntry1)
		self.assertEqual(ansEntry1, ansEntryCopy)
		self.assertEqual(ansEntry1.name, ansEntryCopy.name)
		self.assertEqual(ansEntry1.rdCls, ansEntryCopy.rdCls)
		self.assertEqual(ansEntry1.rdType, ansEntryCopy.rdType)
		self.assertEqual(ansEntry1.ttl, ansEntryCopy.ttl)
		self.assertEqual(ansEntry1.dataList, ansEntryCopy.dataList)

		# Change the name of the copy
		ansEntryCopy.name = dns.name.from_text('dns.google')
		self.assertNotEqual(ansEntry1, ansEntryCopy)
		self.assertNotEqual(ansEntry1.name, ansEntryCopy.name)
		self.assertEqual(ansEntry1.rdCls, ansEntryCopy.rdCls)
		self.assertEqual(ansEntry1.rdType, ansEntryCopy.rdType)
		self.assertEqual(ansEntry1.ttl, ansEntryCopy.ttl)
		self.assertEqual(ansEntry1.dataList, ansEntryCopy.dataList)

		ansEntryCopy = copy.deepcopy(ansEntry1)
		self.assertEqual(ansEntry1, ansEntryCopy)

		# Change the dataList of the copy
		ansEntryCopy.dataList.pop()
		self.assertNotEqual(ansEntry1, ansEntryCopy)
		self.assertEqual(ansEntry1.name, ansEntryCopy.name)
		self.assertEqual(ansEntry1.rdCls, ansEntryCopy.rdCls)
		self.assertEqual(ansEntry1.rdType, ansEntryCopy.rdType)
		self.assertEqual(ansEntry1.ttl, ansEntryCopy.ttl)
		self.assertNotEqual(ansEntry1.dataList, ansEntryCopy.dataList)

