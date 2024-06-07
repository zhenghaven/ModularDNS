#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import ssl

from requests.adapters import HTTPAdapter


class SmartAdapter(HTTPAdapter):

	def build_connection_pool_key_attributes(self, request, verify, cert=None):
		base: HTTPAdapter = super(SmartAdapter, self)

		host_params, pool_kwargs = base.build_connection_pool_key_attributes(
			request,
			verify,
			cert
		)

		for key, header in request.headers.items():
			if key.lower() == 'host':
				pool_kwargs['server_hostname'] = header

		return (host_params, pool_kwargs)

class SmartAndSecureAdapter(SmartAdapter):

	TLS_MIN_VERSION = ssl.TLSVersion.TLSv1_2

	def build_connection_pool_key_attributes(self, request, verify, cert=None):
		base: SmartAdapter = super(SmartAndSecureAdapter, self)

		host_params, pool_kwargs = base.build_connection_pool_key_attributes(
			request,
			verify,
			cert
		)

		tlsMin = pool_kwargs.get('ssl_minimum_version', self.TLS_MIN_VERSION)
		if tlsMin == ssl.TLSVersion.TLSv1_3:
			# the requested min version is already higher than our minimum
			pass
		else:
			# the requested min version is either not set, lower, or equal to our minimum
			pool_kwargs['ssl_minimum_version'] = self.TLS_MIN_VERSION

		return (host_params, pool_kwargs)

