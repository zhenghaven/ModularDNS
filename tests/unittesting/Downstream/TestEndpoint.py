#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###

import ipaddress
import unittest

from ModularDNS.Downstream.Remote.Endpoint import Endpoint

from .TestHosts import BuildTestingHosts


class TestEndpoint(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_Endpoint_1ParseProto(self):
		self.assertEqual(
			Endpoint.ParseProto(uri='http://'),
			('http', '')
		)
		self.assertEqual(
			Endpoint.ParseProto(uri='https://'),
			('https', '')
		)
		self.assertEqual(
			Endpoint.ParseProto(uri='http://google.com'),
			('http', 'google.com')
		)
		self.assertEqual(
			Endpoint.ParseProto(uri='https://[2001:4860:4860::8888]'),
			('https', '[2001:4860:4860::8888]')
		)
		self.assertEqual(
			Endpoint.ParseProto(uri='https://[2001:4860:4860::8888]:443'),
			('https', '[2001:4860:4860::8888]:443')
		)

		self.assertEqual(
			Endpoint.ParseProto(uri=''),
			(Endpoint.DEFAULT_PROTO, '')
		)

		self.assertEqual(
			Endpoint.ParseProto(uri='[2001:4860:4860::8888]:443'),
			(Endpoint.DEFAULT_PROTO, '[2001:4860:4860::8888]:443')
		)

		# something invalid
		self.assertEqual(
			Endpoint.ParseProto(uri='ht:tp://:'),
			(Endpoint.DEFAULT_PROTO, 'ht:tp://:')
		)

	def test_Endpoint_2ParseDomainAndPort(self):
		# ipv4
		self.assertEqual(
			Endpoint.ParseDomainAndPort(dnp='192.168.1.1'),
			(None, '192.168.1.1', None)
		)
		self.assertEqual(
			Endpoint.ParseDomainAndPort(dnp='10.0.0.1:53'),
			(None, '10.0.0.1', 53)
		)

		# ipv6
		self.assertEqual(
			Endpoint.ParseDomainAndPort(dnp='[2001:4860:4860::8888]'),
			(None, '2001:4860:4860::8888', None)
		)
		self.assertEqual(
			Endpoint.ParseDomainAndPort(dnp='[2001:4860:4860::8888]:443'),
			(None, '2001:4860:4860::8888', 443)
		)
		self.assertEqual(
			Endpoint.ParseDomainAndPort(dnp='[fe80::7:8%eth0]:53'),
			(None, 'fe80::7:8%eth0', 53)
		)
		# invalid but ok
		self.assertEqual(
			Endpoint.ParseDomainAndPort(dnp='[a]'),
			(None, 'a', None)
		)
		# invalid but ok
		self.assertEqual(
			Endpoint.ParseDomainAndPort(dnp='[a:a:a:a:a:a:a:a:a:a:a:a:a:a:a:]'),
			(None, 'a:a:a:a:a:a:a:a:a:a:a:a:a:a:a:', None)
		)
		# invalid but ok
		self.assertEqual(
			Endpoint.ParseDomainAndPort(dnp='[:::::::::::::::::::::::::::::]'),
			(None, ':::::::::::::::::::::::::::::', None)
		)

		# hostname
		self.assertEqual(
			Endpoint.ParseDomainAndPort(dnp='google.com'),
			('google.com', None, None)
		)
		self.assertEqual(
			Endpoint.ParseDomainAndPort(dnp='google.com:443'),
			('google.com', None, 443)
		)
		# invalid but ok
		self.assertEqual(
			Endpoint.ParseDomainAndPort(dnp='1921.68.1.1'),
			('1921.68.1.1', None, None)
		)

		# something invalid
		with self.assertRaises(ValueError):
			Endpoint.ParseDomainAndPort(dnp='')

		with self.assertRaises(ValueError):
			Endpoint.ParseDomainAndPort(dnp='ht:tp://:')

		with self.assertRaises(ValueError):
			Endpoint.ParseDomainAndPort(dnp='ht:tp://')

		with self.assertRaises(ValueError):
			Endpoint.ParseDomainAndPort(dnp='http:/')

		with self.assertRaises(ValueError):
			Endpoint.ParseDomainAndPort(dnp='ht:tp:0')

		with self.assertRaises(ValueError):
			Endpoint.ParseDomainAndPort(dnp='[abcd://]')

	def test_Endpoint_3FromURI(self):
		hosts = BuildTestingHosts()
		# ipv4
		ep = Endpoint.FromURI(uri='https://192.168.1.1', resolver=hosts)
		self.assertEqual(ep.proto, 'https')
		self.assertEqual(ep.GetIPAddr([]), ipaddress.ip_address('192.168.1.1'))
		self.assertEqual(ep.GetHostName(), '192.168.1.1')
		self.assertEqual(ep.port, 443)

		ep = Endpoint.FromURI(uri='tls://10.0.0.1:553', resolver=hosts)
		self.assertEqual(ep.proto, 'tls')
		self.assertEqual(ep.GetIPAddr([]), ipaddress.ip_address('10.0.0.1'))
		self.assertEqual(ep.GetHostName(), '10.0.0.1')
		self.assertEqual(ep.port, 553)

		ep = Endpoint.FromURI(uri='172.16.0.1', resolver=hosts)
		self.assertEqual(ep.proto, 'udp')
		self.assertEqual(ep.GetIPAddr([]), ipaddress.ip_address('172.16.0.1'))
		self.assertEqual(ep.GetHostName(), '172.16.0.1')
		self.assertEqual(ep.port, 53)

		ep = Endpoint.FromURI(uri='tcp://127.0.0.1:12345', resolver=hosts)
		self.assertEqual(ep.proto, 'tcp')
		self.assertEqual(ep.GetIPAddr([]), ipaddress.ip_address('127.0.0.1'))
		self.assertEqual(ep.GetHostName(), '127.0.0.1')
		self.assertEqual(ep.port, 12345)

		# ipv6
		ep = Endpoint.FromURI(uri='https://[2001:4860:4860::8888]:8443', resolver=hosts)
		self.assertEqual(ep.proto, 'https')
		self.assertEqual(ep.GetIPAddr([]), ipaddress.ip_address('2001:4860:4860::8888'))
		self.assertEqual(ep.GetHostName(), '2001:4860:4860::8888')
		self.assertEqual(ep.port, 8443)

		ep = Endpoint.FromURI(uri='tls://[2620:fe::9]', resolver=hosts)
		self.assertEqual(ep.proto, 'tls')
		self.assertEqual(ep.GetIPAddr([]), ipaddress.ip_address('2620:fe::9'))
		self.assertEqual(ep.GetHostName(), '2620:fe::9')
		self.assertEqual(ep.port, 853)

		ep = Endpoint.FromURI(uri='udp://[::1]:5353', resolver=hosts)
		self.assertEqual(ep.proto, 'udp')
		self.assertEqual(ep.GetIPAddr([]), ipaddress.ip_address('::1'))
		self.assertEqual(ep.GetHostName(), '::1')
		self.assertEqual(ep.port, 5353)

		ep = Endpoint.FromURI(uri='tcp://[fe80::7:8%eth0]', resolver=hosts)
		self.assertEqual(ep.proto, 'tcp')
		self.assertEqual(ep.GetIPAddr([]), ipaddress.ip_address('fe80::7:8%eth0'))
		self.assertEqual(ep.GetHostName(), 'fe80::7:8%eth0')
		self.assertEqual(ep.port, 53)

		# hostname
		ep = Endpoint.FromURI(uri='https://dns.google', resolver=hosts)
		self.assertEqual(ep.proto, 'https')
		self.assertIn(
			ep.GetIPAddr([]),
			[
				ipaddress.ip_address('8.8.8.8'),
				ipaddress.ip_address('8.8.4.4'),
			]
		)
		self.assertEqual(ep.GetHostName(), 'dns.google')
		self.assertEqual(ep.port, 443)

		ep = Endpoint.FromURI(
			uri='tls://dns.google:8443',
			resolver=hosts,
			preferIPv6=True
		)
		self.assertEqual(ep.proto, 'tls')
		self.assertIn(
			ep.GetIPAddr([]),
			[
				ipaddress.ip_address('2001:4860:4860::8888'),
				ipaddress.ip_address('2001:4860:4860::8844'),
			]
		)
		self.assertEqual(ep.GetHostName(), 'dns.google')
		self.assertEqual(ep.port, 8443)

		# invalid but ok
		ep = Endpoint.FromURI(uri='abcd://dns.google:1234', resolver=hosts)
		self.assertEqual(ep.proto, 'abcd')
		self.assertIn(
			ep.GetIPAddr([]),
			[
				ipaddress.ip_address('8.8.8.8'),
				ipaddress.ip_address('8.8.4.4'),
			]
		)
		self.assertEqual(ep.GetHostName(), 'dns.google')
		self.assertEqual(ep.port, 1234)

		# something invalid
		with self.assertRaises(ValueError):
			# ipaddress.ip_address does not accept leading zeros
			Endpoint.FromURI(uri='172.016.000.001', resolver=hosts)

		with self.assertRaises(ValueError):
			# invalid ipv6 address
			Endpoint.FromURI(uri='[a:a:a:a:a:a:a:a:a:a:a:a:a]', resolver=hosts)

		with self.assertRaises(ValueError):
			# cannot determine default port for unknown protocol
			Endpoint.FromURI(uri='abcd://dns.google', resolver=hosts)

