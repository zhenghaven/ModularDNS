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

from typing import Type

from ModularDNS.Downstream.Local.Hosts import Hosts
from ModularDNS.Exceptions import DNSNameNotFoundError


TESTING_HOSTS_CONFIG = {
	'ttl': 3600,
	'records': [
		{
			'domain': 'dns.google',
			'ip': [
				'8.8.8.8', '8.8.4.4',
				'2001:4860:4860::8888', '2001:4860:4860::8844',
			]
		},
		{ 'domain': 'dns.google.com',  'ip': [ '8.8.8.8', '8.8.4.4' ] },

		{ 'domain': 'one.one.one.one', 'ip': [ '1.1.1.1', '1.0.0.1' ] },
		{ 'domain': 'one.one.one.one', 'ip': [ '2606:4700:4700::1111', '2606:4700:4700::1001' ] },

		{ 'domain': 'dns.quad9.net',   'ip': [ '2620:fe::9', '2620:fe::fe' ] },
	]
}


def BuildTestingHosts(cls: Type[Hosts] = Hosts) -> Hosts:
	hosts = cls.FromConfig(
		dCollection=None,
		config=TESTING_HOSTS_CONFIG
	)
	return hosts


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


class TestLocalHosts(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_Downstream_Local_Hosts_1BuildTestingHosts(self):
		hosts = BuildTestingHosts()
		self.assertIsInstance(hosts, Hosts)
		self.assertEqual(hosts.ttl, 3600)
		self.assertEqual(hosts.GetNumDomains(), 4)

	def test_Downstream_Local_Hosts_2Lookup(self):
		hosts = BuildTestingHosts()

		# dns.google
		# both IPv4 and IPv6, prefer IPv4
		ip = hosts.LookupIpAddr(domain='dns.google', preferIPv6=False, recDepthStack=[])
		expIPStrs = TESTING_HOSTS_CONFIG['records'][0]['ip'][:2]
		expIPs = [ipaddress.ip_address(x) for x in expIPStrs]
		assert len(expIPs) == 2
		self.assertIn(ip, expIPs)

		# both IPv4 and IPv6, prefer IPv6
		ip = hosts.LookupIpAddr(domain='dns.google', preferIPv6=True, recDepthStack=[])
		expIPStrs = TESTING_HOSTS_CONFIG['records'][0]['ip'][2:]
		expIPs = [ipaddress.ip_address(x) for x in expIPStrs]
		assert len(expIPs) == 2
		self.assertIn(ip, expIPs)


		# one.one.one.one
		# both IPv4 and IPv6, prefer IPv4
		ip = hosts.LookupIpAddr(domain='one.one.one.one', preferIPv6=False, recDepthStack=[])
		expIPStrs = TESTING_HOSTS_CONFIG['records'][2]['ip']
		expIPs = [ipaddress.ip_address(x) for x in expIPStrs]
		assert len(expIPs) == 2
		self.assertIn(ip, expIPs)

		# both IPv4 and IPv6, prefer IPv6
		ip = hosts.LookupIpAddr(domain='one.one.one.one', preferIPv6=True, recDepthStack=[])
		expIPStrs = TESTING_HOSTS_CONFIG['records'][3]['ip']
		expIPs = [ipaddress.ip_address(x) for x in expIPStrs]
		assert len(expIPs) == 2
		self.assertIn(ip, expIPs)


		# dns.google.com
		# only IPv4, prefer IPv4
		ip = hosts.LookupIpAddr(domain='dns.google.com', preferIPv6=False, recDepthStack=[])
		expIPStrs = TESTING_HOSTS_CONFIG['records'][1]['ip']
		expIPs = [ipaddress.ip_address(x) for x in expIPStrs]
		assert len(expIPs) == 2
		self.assertIn(ip, expIPs)

		# only IPv4, prefer IPv6
		ip = hosts.LookupIpAddr(domain='dns.google.com', preferIPv6=True, recDepthStack=[])
		self.assertIn(ip, expIPs)


		# dns.quad9.net
		# only IPv6, prefer IPv6
		ip = hosts.LookupIpAddr(domain='dns.quad9.net', preferIPv6=True, recDepthStack=[])
		expIPStrs = TESTING_HOSTS_CONFIG['records'][4]['ip']
		expIPs = [ipaddress.ip_address(x) for x in expIPStrs]
		assert len(expIPs) == 2
		self.assertIn(ip, expIPs)

		# only IPv6, prefer IPv4
		ip = hosts.LookupIpAddr(domain='dns.quad9.net', preferIPv6=False, recDepthStack=[])
		self.assertIn(ip, expIPs)

	def test_Downstream_Local_Hosts_3LookupFail(self):
		hosts = BuildTestingHosts()

		# Domain doesn't exist, prefer IPv4
		with self.assertRaises(DNSNameNotFoundError):
			hosts.LookupIpAddr(domain='not.exist', preferIPv6=False, recDepthStack=[])

		# Domain doesn't exist, prefer IPv6
		with self.assertRaises(DNSNameNotFoundError):
			hosts.LookupIpAddr(domain='not.exist', preferIPv6=True, recDepthStack=[])

