#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import unittest

from ModularDNS import Exceptions


class TestExceptions(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_Exceptions_01NameToClass(self):
		self.assertEqual(
			Exceptions.GetExceptionByName('DNSException'),
			Exceptions.DNSException
		)
		self.assertEqual(
			Exceptions.GetExceptionByName('DNSNameNotFoundError'),
			Exceptions.DNSNameNotFoundError
		)
		self.assertEqual(
			Exceptions.GetExceptionByName('DNSZeroAnswerError'),
			Exceptions.DNSZeroAnswerError
		)
		self.assertEqual(
			Exceptions.GetExceptionByName('DNSRequestRefusedError'),
			Exceptions.DNSRequestRefusedError
		)
		self.assertEqual(
			Exceptions.GetExceptionByName('DNSServerFaultError'),
			Exceptions.DNSServerFaultError
		)

