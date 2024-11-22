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
import dns.rrset

from ModularDNS.MsgEntry.AddEntry import AddEntry, MsgEntry


class TestAddEntry(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_MsgEntry_AddEntry_1Equal(self):
		testRRset1 = dns.rrset.from_text_list(
			name='dns.google.com',
			ttl=300,
			rdclass=dns.rdataclass.IN,
			rdtype=dns.rdatatype.A,
			text_rdatas=[ '8.8.8.8', '8.8.4.4' ]
		)
		addEntry1 = AddEntry(
			rawSet=testRRset1,
		)
		self.assertEqual(addEntry1.entryType, 'ADD')

		testRRset2 = dns.rrset.from_text_list(
			name='dns.google.com',
			ttl=300,
			rdclass=dns.rdataclass.IN,
			rdtype=dns.rdatatype.A,
			text_rdatas=[ '8.8.8.8', '8.8.4.4' ]
		)
		addEntry2 = AddEntry(
			rawSet=testRRset2,
		)
		self.assertEqual(addEntry2.entryType, 'ADD')

		self.assertEqual(addEntry1, addEntry2)
		self.assertEqual(hash(addEntry1), hash(addEntry2))

		# a AddEntry has a empty dataList
		testRRsetEmpty = dns.rrset.from_text_list(
			name='dns.google.com',
			ttl=300,
			rdclass=dns.rdataclass.IN,
			rdtype=dns.rdatatype.A,
			text_rdatas=[ ]
		)
		addEntryEmpty = AddEntry(
			rawSet=testRRsetEmpty,
		)

		self.assertNotEqual(addEntry1, addEntryEmpty)
		self.assertNotEqual(hash(addEntry1), hash(addEntryEmpty))

		# Different name
		testRRset3 = dns.rrset.from_text_list(
			name='dns.google',
			ttl=300,
			rdclass=dns.rdataclass.IN,
			rdtype=dns.rdatatype.A,
			text_rdatas=[ '8.8.8.8', '8.8.4.4' ]
		)
		addEntry3 = AddEntry(
			rawSet=testRRset3,
		)

		self.assertNotEqual(addEntry1, addEntry3)
		self.assertNotEqual(hash(addEntry1), hash(addEntry3))

		# Different rdCls
		testRRset4 = dns.rrset.from_text_list(
			name='dns.google.com',
			ttl=300,
			rdclass=dns.rdataclass.ANY,
			rdtype=dns.rdatatype.A,
			text_rdatas=[ ]
		)
		addEntry4 = AddEntry(
			rawSet=testRRset4,
		)

		self.assertNotEqual(addEntryEmpty, addEntry4)
		self.assertNotEqual(hash(addEntryEmpty), hash(addEntry4))

		# Different rdType
		testRRset5 = dns.rrset.from_text_list(
			name='dns.google.com',
			ttl=300,
			rdclass=dns.rdataclass.IN,
			rdtype=dns.rdatatype.AAAA,
			text_rdatas=[ ]
		)
		addEntry5 = AddEntry(
			rawSet=testRRset5,
		)

		self.assertNotEqual(addEntryEmpty, addEntry5)
		self.assertNotEqual(hash(addEntryEmpty), hash(addEntry5))

		# Different classes
		msgEntry = MsgEntry(entryType=addEntry1.entryType)
		self.assertNotEqual(addEntry1, msgEntry)

	def test_MsgEntry_AddEntry_2Copy(self):
		testRRset1 = dns.rrset.from_text_list(
			name='dns.google.com',
			ttl=300,
			rdclass=dns.rdataclass.IN,
			rdtype=dns.rdatatype.A,
			text_rdatas=[ '8.8.8.8', '8.8.4.4' ]
		)
		addEntry1 = AddEntry(
			rawSet=testRRset1,
		)

		addEntryCopy = copy.copy(addEntry1)
		self.assertEqual(addEntry1, addEntryCopy)
		self.assertEqual(addEntry1._rawSet, addEntryCopy._rawSet)

		# Change the a member of the copy
		testRRset2 = dns.rrset.from_text_list(
			name='dns.google',
			ttl=300,
			rdclass=dns.rdataclass.IN,
			rdtype=dns.rdatatype.A,
			text_rdatas=[ '8.8.8.8', '8.8.4.4' ]
		)
		addEntryCopy._rawSet = testRRset2
		self.assertNotEqual(addEntry1, addEntryCopy)
		self.assertNotEqual(addEntry1._rawSet, addEntryCopy._rawSet)

		addEntryCopy = copy.copy(addEntry1)
		self.assertEqual(addEntry1, addEntryCopy)

	def test_MsgEntry_AddEntry_3DeepCopy(self):
		testRRset1 = dns.rrset.from_text_list(
			name='dns.google.com',
			ttl=300,
			rdclass=dns.rdataclass.IN,
			rdtype=dns.rdatatype.A,
			text_rdatas=[ '8.8.8.8', '8.8.4.4' ]
		)
		addEntry1 = AddEntry(
			rawSet=testRRset1,
		)

		addEntryCopy = copy.deepcopy(addEntry1)
		self.assertEqual(addEntry1, addEntryCopy)
		self.assertEqual(addEntry1._rawSet, addEntryCopy._rawSet)

		# Change the a member of the copy
		testRRset2 = dns.rrset.from_text_list(
			name='dns.google',
			ttl=300,
			rdclass=dns.rdataclass.IN,
			rdtype=dns.rdatatype.A,
			text_rdatas=[ '8.8.8.8', '8.8.4.4' ]
		)
		addEntryCopy._rawSet = testRRset2
		self.assertNotEqual(addEntry1, addEntryCopy)
		self.assertNotEqual(addEntry1._rawSet, addEntryCopy._rawSet)

		addEntryCopy = copy.deepcopy(addEntry1)
		self.assertEqual(addEntry1, addEntryCopy)

