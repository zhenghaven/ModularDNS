#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import threading
import time
import unittest

import dns.name
import dns.rdataclass
import dns.rdatatype

from ModularDNS.Downstream.Local.Hosts import Hosts
from ModularDNS.Downstream.Local.Cache import Cache
from ModularDNS.MsgEntry.AnsEntry import AnsEntry
from ModularDNS.MsgEntry.QuestionEntry import QuestionEntry

from .TestHosts import BuildTestingHosts


class CountingHosts(Hosts):


	def __init__(self, ttl: int = Hosts.DEFAULT_TTL) -> None:
		super(CountingHosts, self).__init__(ttl=ttl)

		self.__counter = 0

	def HandleQuestion(
		self,
		msgEntry,
		senderAddr,
		recDepthStack,
	):
		self.__counter += 1

		return super(CountingHosts, self).HandleQuestion(
			msgEntry=msgEntry,
			senderAddr=senderAddr,
			recDepthStack=recDepthStack,
		)

	def GetCounter(self):
		return self.__counter


class TestLocalCache(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_LocalCache_1Basic(self):
		hosts: CountingHosts = BuildTestingHosts(cls=CountingHosts)
		self.assertEqual(hosts.GetCounter(), 0)

		cache = Cache(fallback=hosts)

		# test lookup
		## A lookup that is going to miss
		question1 = QuestionEntry(
			name=dns.name.from_text('dns.google.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
		)
		resp1 = cache.HandleQuestion(
			msgEntry=question1,
			senderAddr=('localhost', 0),
			recDepthStack=[],
		)
		self.assertEqual(hosts.GetCounter(), 1)
		self.assertEqual(len(resp1), 1)
		resp1: AnsEntry = resp1[0]
		self.assertEqual(resp1.entryType, 'ANS')
		self.assertEqual(resp1.name, question1.name)
		self.assertEqual(resp1.rdCls, question1.rdCls)
		self.assertEqual(resp1.rdType, question1.rdType)
		self.assertEqual(len(resp1.dataList), 2)
		self.assertEqual(resp1.ttl, hosts.ttl)
		## A lookup that is going to hit
		question1 = QuestionEntry(
			name=dns.name.from_text('dns.google.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
		)
		resp1Cached = cache.HandleQuestion(
			msgEntry=question1,
			senderAddr=('localhost', 0),
			recDepthStack=[],
		)
		self.assertEqual(hosts.GetCounter(), 1)
		self.assertEqual(len(resp1Cached), 1)
		resp1Cached: AnsEntry = resp1Cached[0]
		self.assertEqual(resp1, resp1Cached)

	def __ATestingThread(self, cache, expTTL, startEvent, outHasError):
		try:
			startEvent.wait()

			# test lookup
			## A lookup that might be going to miss
			question1 = QuestionEntry(
				name=dns.name.from_text('dns.google.com'),
				rdCls=dns.rdataclass.IN,
				rdType=dns.rdatatype.A,
			)
			resp1 = cache.HandleQuestion(
				msgEntry=question1,
				senderAddr=('localhost', 0),
				recDepthStack=[],
			)
			self.assertEqual(len(resp1), 1)
			resp1: AnsEntry = resp1[0]
			self.assertEqual(resp1.entryType, 'ANS')
			self.assertEqual(resp1.name, question1.name)
			self.assertEqual(resp1.rdCls, question1.rdCls)
			self.assertEqual(resp1.rdType, question1.rdType)
			self.assertEqual(len(resp1.dataList), 2)
			self.assertEqual(resp1.ttl, expTTL)

			repeatHitTimes = 100
			for _ in range(repeatHitTimes):
				question1 = QuestionEntry(
					name=dns.name.from_text('dns.google.com'),
					rdCls=dns.rdataclass.IN,
					rdType=dns.rdatatype.A,
				)
				resp1Cached = cache.HandleQuestion(
					msgEntry=question1,
					senderAddr=('localhost', 0),
					recDepthStack=[],
				)
				self.assertEqual(len(resp1Cached), 1)
				resp1Cached: AnsEntry = resp1Cached[0]
				self.assertEqual(resp1, resp1Cached)
		except Exception as e:
			outHasError.set()
			raise e

	def test_LocalCache_2Threading(self):
		hosts = BuildTestingHosts(cls=CountingHosts)
		self.assertEqual(hosts.GetCounter(), 0)

		cache = Cache(fallback=hosts)

		startEvent = threading.Event()
		self.assertFalse(startEvent.is_set())
		hasError = threading.Event()
		self.assertFalse(hasError.is_set())

		numOfThreads = 5

		# making threads
		threads = [
			threading.Thread(
				target=self.__ATestingThread,
				args=(cache, hosts.ttl, startEvent, hasError),
			)
			for _ in range(numOfThreads)
		]
		# starting threads
		for thread in threads:
			thread.start()
		startTime = time.time()
		# start testing
		startEvent.set()
		# waiting for threads to finish
		for thread in threads:
			thread.join()
		endTime = time.time()

		elapsedTimeMs = (endTime - startTime) * 1000
		print(f"\n\tTime elapsed: {elapsedTimeMs:.6f}ms")

		self.assertFalse(hasError.is_set())

		# in worst case, all `numOfThreads` threads begin to lookup at the same
		# time and they all miss the cache.
		# But that's it, all other lookups are going to hit the cache.
		self.assertLessEqual(hosts.GetCounter(), numOfThreads)

