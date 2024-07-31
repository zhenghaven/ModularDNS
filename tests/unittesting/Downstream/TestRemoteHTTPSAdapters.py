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

from ModularDNS.Downstream.Remote.UDP import UDP
from ModularDNS.Downstream.Remote.Endpoint import Endpoint
from ModularDNS.Downstream.Remote.HTTPSAdapters import SmartAndSecureAdapter


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

		udp = UDP(
			Endpoint.FromURI(uri='udp://8.8.8.8', resolver=None),
		)

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

