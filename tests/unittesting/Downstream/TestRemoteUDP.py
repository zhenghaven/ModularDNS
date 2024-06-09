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

from ModularDNS.Downstream.Remote.UDP import UDP
from ModularDNS.Downstream.Remote.Endpoint import Endpoint

from .TestRemote import TestRemote


class TestRemoteUDP(TestRemote):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_Remote_UDP_1Lookup(self):
		remote = UDP(
			Endpoint.FromURI(uri='udp://8.8.8.8', resolver=None),
		)

		self.StandardLookupTest(remote=remote)

