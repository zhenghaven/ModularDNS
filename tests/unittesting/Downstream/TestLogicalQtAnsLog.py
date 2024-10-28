#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import os
import unittest
import uuid

import dns.name
import dns.rdataclass
import dns.rdatatype

from ModularDNS.Downstream.DownstreamCollection import DownstreamCollection
from ModularDNS.Downstream.Logical.QtAnsLog import QtAnsLog
from ModularDNS.MsgEntry.QuestionEntry import QuestionEntry

from .TestLocalHosts import BuildTestingHosts, CountingHosts


class TestLogicalQtAnsLog(unittest.TestCase):

	def setUp(self):
		# generate an uuid for log
		self.logUUID = uuid.uuid4()
		self.loggerName = f'QtAnsLog-{str(self.logUUID)}'
		self.logFilename = f'QtAnsLog-{self.logUUID.hex}.log'

	def tearDown(self):
		# remove the log file if exists
		if os.path.exists(self.logFilename):
			os.remove(self.logFilename)
			pass

	def test_Downstream_Logical_QtAnsLog_01Log(self):
		hosts1 = BuildTestingHosts(cls=CountingHosts)

		# create a logger for testing
		logHandler = QtAnsLog(
			qtHandler=hosts1,
			logPath=self.logFilename,
			loggerName=self.loggerName,
			logMode='w',
			cleanLogHandler=True,
			qtNameRegexExpr='^.*$',
			qtCls=dns.rdataclass.ANY,
			qtType=dns.rdatatype.ANY,
		)

		# query for google.com
		question1 = QuestionEntry(
			name=dns.name.from_text('dns.google.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
		)
		ans1 = logHandler.HandleQuestion(
			msgEntry=question1,
			senderAddr=('localhost', 0),
			recDepthStack=[],
		)
		# test if the answer is correct
		self.assertEqual(len(ans1), 1)
		addr1 = ans1[0].GetAddresses()
		self.assertIn('8.8.8.8', [ str(x) for x in addr1 ])

		# query for non-existing.com
		question2 = QuestionEntry(
			name=dns.name.from_text('non-existing.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
		)
		with self.assertRaises(Exception):
			logHandler.HandleQuestion(
				msgEntry=question2,
				senderAddr=('localhost', 0),
				recDepthStack=[],
			)

	def test_Downstream_Logical_QtAnsLog_02FromConfig(self):
		hosts1 = BuildTestingHosts()
		dCollection = DownstreamCollection()
		dCollection.AddHandler('hosts1', hosts1)

		failover = QtAnsLog.FromConfig(
			dCollection=dCollection,
			qtHandler='s:hosts1',
			logPath=self.logFilename,
			loggerName=self.loggerName,
			logMode='w',
			cleanLogHandler=True,
			qtNameRegexExpr='^.*$',
			qtCls='ANY',
			qtType='ANY',
		)
		self.assertIsInstance(failover, QtAnsLog)

