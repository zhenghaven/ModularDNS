#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import logging
import unittest

import requests

from ModularDNS.Downstream.Logical.RaiseExcept import RaiseExcept
from ModularDNS.Downstream.Remote.UDP import UDP
from ModularDNS.Downstream.Remote.Endpoint import Endpoint
from ModularDNS.Downstream.Remote.HTTPSAdapters import SmartAndSecureAdapter
from ModularDNS.Exceptions import DNSServerFaultError


class TestRemoteHTTPSAdapters(unittest.TestCase):

	def setUp(self):
		self.logger = logging.getLogger(
			f'{__name__}.{self.__class__.__name__}'
		)

	def tearDown(self):
		pass

	def AccessViaIP(self, session: requests.Session, ip: str, testDomain: str):
		resp = session.get(
			f'https://{ip}:443/',
			headers={
				'Host': testDomain,
			},
			timeout=2.0,
			allow_redirects=False,
			verify=True,
		)

		self.logger.debug(f'Response status code: {resp.status_code}')
		resp.raise_for_status()

	def test_Downstream_Remote_HTTPSAdapters_1AccessViaIP(self):
		logging.getLogger().info('')

		testDomain = 'www.google.com'

		with UDP(
			Endpoint.FromURI(
				uri='udp://8.8.8.8',
				resolver=RaiseExcept(
					exceptToRaise=DNSServerFaultError,
					exceptKwargs={
						'reason': 'Endpoint already knows the IP address',
					}
				)
			),
		) as udp:

			self.logger.debug(f'Looking up IP for domain: {testDomain}')
			ip = udp.LookupIpAddr(domain=testDomain, preferIPv6=False, recDepthStack=[])
			self.logger.debug(f'IP for domain: {testDomain} is {ip}')

		session = requests.Session()

		# without using our smart adapter, the HTTPS request will fail
		try:
			self.AccessViaIP(session, ip, testDomain)
			self.fail('Expected HTTPS request to fail without using smart adapter')
		except Exception as e:
			self.logger.info(f'Failed to access {testDomain} via IP {ip} as expected: {e}')
			pass

		# now we use our smart adapter, the HTTPS request should succeed
		session.mount('https://', SmartAndSecureAdapter())
		self.AccessViaIP(session, ip, testDomain)

		# it should raise exception if we try to access it with a different domain
		testDomain2 = 'www.microsoft.com'
		try:
			self.AccessViaIP(session, ip, testDomain2)
			self.fail('Expected HTTPS request to fail with different domain')
		except Exception as e:
			self.logger.info(f'Failed to access {testDomain2} via IP {ip} as expected: {e}')
			pass

		# it should also raise exception if we try to access it with a different IP
		ip2 = '1.1.1.1'
		try:
			self.AccessViaIP(session, ip2, testDomain)
			self.fail('Expected HTTPS request to fail with different IP')
		except Exception as e:
			self.logger.info(f'Failed to access {testDomain} via IP {ip2} as expected: {e}')
			pass

