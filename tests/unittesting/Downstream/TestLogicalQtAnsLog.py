#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import logging
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

			# remove the log file
			os.remove(self.logFilename)
			pass

	def LogLogFileContent(self, expectContent: bool):
		# log the file content
		logger = logging.getLogger('Test-' + self.loggerName)
		logger.info('Log file containing following content:')
		with open(self.logFilename, 'r') as f:
			fileContent = f.read()
		logger.info(
			'#################### BEGIN ####################\n' +
			fileContent
		)
		logger.info('####################  END  ####################')
		if expectContent:
			self.assertGreater(len(fileContent), 0)

	def test_Downstream_Logical_QtAnsLog_01Log(self):
		logging.getLogger().info('')

		hosts1 = BuildTestingHosts(cls=CountingHosts)

		# create a logger for testing
		logHandler = QtAnsLog(
			qtHandler=hosts1,
			logPath=self.logFilename,
			loggerName=self.loggerName,
			logMode='w',
			logOnRoot=False,
			qtNameRegexExpr='^.+[.]com$',
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

		# query for dns.google
		question3 = QuestionEntry(
			name=dns.name.from_text('dns.google'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
		)
		ans3 = logHandler.HandleQuestion(
			msgEntry=question3,
			senderAddr=('localhost', 0),
			recDepthStack=[],
		)
		# test if the answer is correct
		self.assertEqual(len(ans3), 1)
		addr3 = ans3[0].GetAddresses()
		self.assertIn('8.8.8.8', [ str(x) for x in addr1 ])

		# make sure there are content in the log file
		self.assertTrue(os.path.exists(self.logFilename))
		self.LogLogFileContent(expectContent=True)

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
			logOnRoot=False,
			qtNameRegexExpr='^.*$',
			qtCls='ANY',
			qtType='ANY',
		)
		self.assertIsInstance(failover, QtAnsLog)

