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

from typing import List, Type

import dns.message
import dns.rcode
import dns.rdata
import dns.rdataclass
import dns.rdatatype

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

		{ 'domain': 'cname.dns.google.com',  'cname': [ 'dns.google.com.' ] },
		{ 'domain': 'cname.cname.dns.google.com',  'cname': [ 'cname.dns.google.com.' ] },
	],

	'map': {
		'cname.test_not_dot.example': {
			'ip': [ '192.168.1.1' ]
		},
		'test_not_dot.example': {
			'cname': [ 'cname' ]
		},
	}
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

	def test_Downstream_Local_Hosts_01BuildTestingHosts(self):
		hosts = BuildTestingHosts()
		self.assertIsInstance(hosts, Hosts)
		self.assertEqual(hosts.ttl, 3600)
		self.assertEqual(hosts.GetNumDomains(), 8)

	def test_Downstream_Local_Hosts_02Lookup(self):
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

	def test_Downstream_Local_Hosts_03LookupFail(self):
		hosts = BuildTestingHosts()

		# Domain doesn't exist, prefer IPv4
		with self.assertRaises(DNSNameNotFoundError):
			hosts.LookupIpAddr(domain='not.exist', preferIPv6=False, recDepthStack=[])

		# Domain doesn't exist, prefer IPv6
		with self.assertRaises(DNSNameNotFoundError):
			hosts.LookupIpAddr(domain='not.exist', preferIPv6=True, recDepthStack=[])

	def test_Downstream_Local_Hosts_04CNameWithDot(self):
		hosts = BuildTestingHosts()

		# cname.dns.google.com CNAME
		question = dns.message.make_query(
			qname='cname.dns.google.com',
			rdclass=dns.rdataclass.IN,
			rdtype=dns.rdatatype.CNAME,
		)
		answer = hosts.Handle(
			dnsMsg=question,
			senderAddr=('127.0.0.1', 0),
			recDepthStack=[]
		)
		self.assertIsInstance(answer, dns.message.Message)
		self.assertEqual(answer.rcode(), dns.rcode.NOERROR)
		self.assertEqual(len(answer.answer), 1)
		# The answer is a CNAME record
		cnameAns = answer.answer[0]
		self.assertEqual(cnameAns.name.to_text(), 'cname.dns.google.com.')
		self.assertEqual(cnameAns.rdtype, dns.rdatatype.CNAME)
		self.assertEqual(len(cnameAns), 1)
		cnameAnsData: List[dns.rdata.Rdata] = [ x for x in cnameAns ]
		cnameAnsDataStr: List[str] = [ x.to_text() for x in cnameAnsData ]
		self.assertEqual(cnameAnsDataStr, [ 'dns.google.com.' ])

		# cname.dns.google.com A
		question = dns.message.make_query(
			qname='cname.dns.google.com',
			rdclass=dns.rdataclass.IN,
			rdtype=dns.rdatatype.A,
		)
		answer = hosts.Handle(
			dnsMsg=question,
			senderAddr=('127.0.0.1', 0),
			recDepthStack=[]
		)
		self.assertIsInstance(answer, dns.message.Message)
		self.assertEqual(answer.rcode(), dns.rcode.NOERROR)
		self.assertEqual(len(answer.answer), 2)
		# The first answer is a CNAME record
		cnameAns = answer.answer[0]
		self.assertEqual(cnameAns.name.to_text(), 'cname.dns.google.com.')
		self.assertEqual(cnameAns.rdtype, dns.rdatatype.CNAME)
		self.assertEqual(len(cnameAns), 1)
		cnameAnsData: List[dns.rdata.Rdata] = [ x for x in cnameAns ]
		cnameAnsDataStr: List[str] = [ x.to_text() for x in cnameAnsData ]
		self.assertEqual(cnameAnsDataStr, [ 'dns.google.com.' ])
		# The second answer is an A record
		aAns = answer.answer[1]
		self.assertEqual(aAns.name.to_text(), 'dns.google.com.')
		self.assertEqual(aAns.rdtype, dns.rdatatype.A)
		self.assertEqual(len(aAns), 2)
		aAnsData: List[dns.rdata.Rdata] = [ x for x in aAns ]
		aAnsDataStr: List[str] = [ x.to_text() for x in aAnsData ]
		self.assertEqual(
			sorted(aAnsDataStr),
			sorted(TESTING_HOSTS_CONFIG['records'][1]['ip'])
		)
		# quick lookup
		ip = hosts.LookupIpAddr(
			domain='cname.dns.google.com',
			preferIPv6=False,
			recDepthStack=[]
		)
		self.assertIn(str(ip), aAnsDataStr)

		# cname.cname.dns.google.com CNAME
		question = dns.message.make_query(
			qname='cname.cname.dns.google.com',
			rdclass=dns.rdataclass.IN,
			rdtype=dns.rdatatype.CNAME,
		)
		answer = hosts.Handle(
			dnsMsg=question,
			senderAddr=('127.0.0.1', 0),
			recDepthStack=[]
		)
		self.assertIsInstance(answer, dns.message.Message)
		self.assertEqual(answer.rcode(), dns.rcode.NOERROR)
		self.assertEqual(len(answer.answer), 1)
		# The first answer is a CNAME record
		cnameAns = answer.answer[0]
		self.assertEqual(cnameAns.name.to_text(), 'cname.cname.dns.google.com.')
		self.assertEqual(cnameAns.rdtype, dns.rdatatype.CNAME)
		self.assertEqual(len(cnameAns), 1)
		cnameAnsData: List[dns.rdata.Rdata] = [ x for x in cnameAns ]
		cnameAnsDataStr: List[str] = [ x.to_text() for x in cnameAnsData ]
		self.assertEqual(cnameAnsDataStr, [ 'cname.dns.google.com.' ])

		# cname.cname.dns.google.com A
		question = dns.message.make_query(
			qname='cname.cname.dns.google.com',
			rdclass=dns.rdataclass.IN,
			rdtype=dns.rdatatype.A,
		)
		answer = hosts.Handle(
			dnsMsg=question,
			senderAddr=('127.0.0.1', 0),
			recDepthStack=[]
		)
		self.assertIsInstance(answer, dns.message.Message)
		self.assertEqual(answer.rcode(), dns.rcode.NOERROR)
		self.assertEqual(len(answer.answer), 3)
		# The first answer is a CNAME record
		cnameAns = answer.answer[0]
		self.assertEqual(cnameAns.name.to_text(), 'cname.cname.dns.google.com.')
		self.assertEqual(cnameAns.rdtype, dns.rdatatype.CNAME)
		self.assertEqual(len(cnameAns), 1)
		cnameAnsData: List[dns.rdata.Rdata] = [ x for x in cnameAns ]
		cnameAnsDataStr: List[str] = [ x.to_text() for x in cnameAnsData ]
		self.assertEqual(cnameAnsDataStr, [ 'cname.dns.google.com.' ])
		# The second answer is a CNAME record
		cnameAns = answer.answer[1]
		self.assertEqual(cnameAns.name.to_text(), 'cname.dns.google.com.')
		self.assertEqual(cnameAns.rdtype, dns.rdatatype.CNAME)
		self.assertEqual(len(cnameAns), 1)
		cnameAnsData: List[dns.rdata.Rdata] = [ x for x in cnameAns ]
		cnameAnsDataStr: List[str] = [ x.to_text() for x in cnameAnsData ]
		self.assertEqual(cnameAnsDataStr, [ 'dns.google.com.' ])
		# The third answer is an A record
		aAns = answer.answer[2]
		self.assertEqual(aAns.name.to_text(), 'dns.google.com.')
		self.assertEqual(aAns.rdtype, dns.rdatatype.A)
		self.assertEqual(len(aAns), 2)
		aAnsData: List[dns.rdata.Rdata] = [ x for x in aAns ]
		aAnsDataStr: List[str] = [ x.to_text() for x in aAnsData ]
		self.assertEqual(
			sorted(aAnsDataStr),
			sorted(TESTING_HOSTS_CONFIG['records'][1]['ip'])
		)
		# quick lookup
		ip = hosts.LookupIpAddr(
			domain='cname.cname.dns.google.com',
			preferIPv6=False,
			recDepthStack=[]
		)
		self.assertIn(str(ip), aAnsDataStr)

	def test_Downstream_Local_Hosts_05CNameWithoutDot(self):
		hosts = BuildTestingHosts()

		# test_not_dot.example
		question = dns.message.make_query(
			qname='test_not_dot.example',
			rdclass=dns.rdataclass.IN,
			rdtype=dns.rdatatype.A,
		)
		answer = hosts.Handle(
			dnsMsg=question,
			senderAddr=('127.0.0.1', 0),
			recDepthStack=[]
		)
		self.assertIsInstance(answer, dns.message.Message)
		self.assertEqual(answer.rcode(), dns.rcode.NOERROR)
		self.assertEqual(len(answer.answer), 2)
		# The first answer is a CNAME record
		cnameAns = answer.answer[0]
		self.assertEqual(cnameAns.name.to_text(), 'test_not_dot.example.')
		self.assertEqual(cnameAns.rdtype, dns.rdatatype.CNAME)
		self.assertEqual(len(cnameAns), 1)
		cnameAnsData: List[dns.rdata.Rdata] = [ x for x in cnameAns ]
		cnameAnsDataStr: List[str] = [ x.to_text() for x in cnameAnsData ]
		self.assertEqual(cnameAnsDataStr, [ 'cname.test_not_dot.example.' ])
		# The second answer is an A record
		aAns = answer.answer[1]
		self.assertEqual(aAns.name.to_text(), 'cname.test_not_dot.example.')
		self.assertEqual(aAns.rdtype, dns.rdatatype.A)
		self.assertEqual(len(aAns), 1)
		aAnsData: List[dns.rdata.Rdata] = [ x for x in aAns ]
		aAnsDataStr: List[str] = [ x.to_text() for x in aAnsData ]
		self.assertEqual(aAnsDataStr, [ '192.168.1.1' ])
		# quick lookup
		ip = hosts.LookupIpAddr(
			domain='test_not_dot.example',
			preferIPv6=False,
			recDepthStack=[]
		)
		self.assertIn(str(ip), aAnsDataStr)

