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

from typing import List

import dns.name
import dns.rdataclass
import dns.rdatatype

from ModularDNS.Exceptions import DNSRequestRefusedError
from ModularDNS.Downstream.Logical import LimitConcurrentReq
from ModularDNS.MsgEntry.QuestionEntry import QuestionEntry

from .BlockingHandler import BlockingHandler
from .TestLocalHosts import BuildTestingHosts, CountingHosts


class TestLogicalLimitConcurrentReq(unittest.TestCase):

	def setUp(self):
		self._rejected = []

	def tearDown(self):
		pass

	def ConcurrentReqThread(self, handler, question, startEvent) -> None:
		startEvent.wait()
		try:
			handler.HandleQuestion(
				msgEntry=question,
				senderAddr=('localhost', 0),
				recDepthStack=[],
			)
			self._rejected.append(0)
		except DNSRequestRefusedError:
			self._rejected.append(1)

	def test_Downstream_Logical_LimitConcurrentReq_01LimitConcurrentReq(self):
		limitNum = 2
		numOfThreads = 10

		hosts1 = BuildTestingHosts(cls=CountingHosts)
		startEvent = threading.Event()
		releaseEvent = threading.Event()
		blocking = BlockingHandler(targetHandler=hosts1, releaseEvent=releaseEvent)
		limitHandler = LimitConcurrentReq.LimitConcurrentReq(
			targetHandler=blocking,
			maxNumConcurrentReq=limitNum,
			blocking=False,
		)

		# query for dns.google.com
		test1Name = 'dns.google.com'
		question1 = QuestionEntry(
			name=dns.name.from_text(test1Name),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
		)

		# set up threads
		threads: List[threading.Thread] = []
		for _ in range(numOfThreads):
			thread = threading.Thread(
				target=self.ConcurrentReqThread,
				args=(limitHandler, question1, startEvent),
			)
			thread.start()
			threads.append(thread)

		startEvent.set()

		startTime = time.time()
		# we expect that the first `limitNum` threads will be accepted
		# and the rest (i.e., `numOfThreads - limitNum`) will be rejected
		while len(self._rejected) < numOfThreads - limitNum:
			if time.time() - startTime > 5:
				raise RuntimeError('Timeout')
			time.sleep(0.1)

		releaseEvent.set()

		for thread in threads:
			thread.join()

		# there should be total of `numOfThreads` threads that appended a number
		# to the list
		self.assertEqual(len(self._rejected), numOfThreads)
		# and among them, `numOfThreads - limitNum` will be rejected and
		# appended with 1
		self.assertEqual(sum(self._rejected), numOfThreads - limitNum)

