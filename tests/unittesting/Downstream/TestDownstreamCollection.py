#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import unittest

from ModularDNS.Downstream.Remote.Endpoint import StaticEndpoint
from ModularDNS.Downstream.DownstreamCollection import (
	DownstreamCollection,
	StaticSharedHandler,
	StaticSharedQuickLookup,
)

from .TestLocalHosts import BuildTestingHosts


class TestDownstreamCollection(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_Downstream_DownstreamCollection_01Handler(self):
		hosts = BuildTestingHosts()

		collection = DownstreamCollection()

		# add handler with invalid name
		with self.assertRaises(ValueError):
			collection.AddHandler('local.cache', None)

		# add handler with invalid type
		with self.assertRaises(TypeError):
			collection.AddHandler('none', None)

		# add handler with valid name
		collection.AddHandler('local-hosts', hosts)
		collection.AddHandler('local_hosts', hosts)
		collection.AddHandler('hosts', hosts)

		# add handler with duplicate name
		with self.assertRaises(KeyError):
			collection.AddHandler('hosts', hosts)


		# get handler with invalid name
		with self.assertRaises(ValueError):
			collection.GetHandler('none')
		with self.assertRaises(ValueError):
			collection.GetHandler('local.cache')

		# get handler with non-exist name
		with self.assertRaises(KeyError):
			collection.GetHandler('s:none')
		with self.assertRaises(KeyError):
			collection.GetHandlerByQuestion('s:none')
		with self.assertRaises(KeyError):
			collection.GetQuickLookup('s:none')
		with self.assertRaises(KeyError):
			collection.GetHandler('s:local.cache')
		with self.assertRaises(KeyError):
			collection.GetHandlerByQuestion('s:local.cache')
		with self.assertRaises(KeyError):
			collection.GetQuickLookup('s:local.cache')

		# get handler with valid name
		print(collection.GetHandler('s:local-hosts'))
		self.assertTrue(
			isinstance(
				collection.GetHandler('s:local-hosts'),
				StaticSharedQuickLookup
			)
		)
		self.assertEqual(
			collection.GetHandler('s:local-hosts').handler,
			hosts
		)

		self.assertTrue(
			isinstance(
				collection.GetHandlerByQuestion('s:local_hosts'),
				StaticSharedQuickLookup
			)
		)
		self.assertEqual(
			collection.GetHandlerByQuestion('s:local_hosts').handler,
			hosts
		)

		self.assertTrue(
			isinstance(
				collection.GetQuickLookup('s:hosts'),
				StaticSharedQuickLookup
			)
		)
		self.assertEqual(
			collection.GetQuickLookup('s:hosts').handler,
			hosts
		)

	def test_Downstream_DownstreamCollection_02Endpoint(self):
		hosts = BuildTestingHosts()
		endpoint = StaticEndpoint.FromURI(uri='https://dns.google', resolver=hosts)

		collection = DownstreamCollection()

		# add endpoint with invalid name
		with self.assertRaises(ValueError):
			collection.AddEndpoint('dns.google', None)

		# add endpoint with invalid type
		with self.assertRaises(TypeError):
			collection.AddEndpoint('none', None)

		# add endpoint with valid name
		collection.AddEndpoint('dns-google', endpoint)
		collection.AddEndpoint('dns_google', endpoint)
		collection.AddEndpoint('google', endpoint)

		# add endpoint with duplicate name
		with self.assertRaises(KeyError):
			collection.AddEndpoint('google', endpoint)


		# get endpoint with non-exist name
		with self.assertRaises(KeyError):
			collection.GetEndpoint('none')
		with self.assertRaises(KeyError):
			collection.GetEndpoint('dns.google')

		# get endpoint with valid name
		print(collection.GetEndpoint('dns-google'))
		self.assertTrue(
			isinstance(collection.GetEndpoint('dns-google'), StaticEndpoint)
		)
		self.assertEqual(collection.GetEndpoint('dns-google'), endpoint)

