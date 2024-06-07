#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import ipaddress
import re
import uuid

from typing import List, Tuple, Union

from ..QuickLookup import QuickLookup


GENERIC_IP_ADDR = Union[ipaddress.IPv4Address, ipaddress.IPv6Address]


class Endpoint(object):

	DEFAULT_PROTO = 'udp'

	DEFAULT_PORT_LUP = {
		'udp': 53,
		'tcp': 53,
		'tls': 853,
		'https': 443,
	}

	DEFAULT_PREFFER_IPV6 = False

	@classmethod
	def ParseProto(cls, uri: str) -> Tuple[str, str]:
		protoRegex = r'^([a-zA-Z][a-zA-Z0-9]*):\/\/'
		protoMatch = re.match(protoRegex, uri)
		if protoMatch is None:
			return (cls.DEFAULT_PROTO, uri)
		else:
			proto = protoMatch.group(1)
			protoAndSlash = protoMatch.group(0)
			domainAndPort = uri[len(protoAndSlash):]
			return (proto, domainAndPort)

	@classmethod
	def ParseDomainAndPort(
		cls,
		dnp: str
	) -> Tuple[
		Union[str, None],
		Union[str, None],
		Union[int, None]
	]:
		portRegex = r'(?::([0-9]{1,5}))?'
		ipv4Regex = r'^([0-9]{1,3}(?:\.[0-9]{1,3}){3})' + portRegex + '$'
		# a better ipv6 regex could be found at
		# https://stackoverflow.com/questions/53497/regular-expression-that-matches-valid-ipv6-addresses
		ipv6Regex = r'^\[([a-zA-Z0-9:%]+)\]' + portRegex + '$'
		hostNameRegex = r'^([a-zA-Z0-9.-]+)' + portRegex + '$'

		ipv4Match = re.match(ipv4Regex, dnp)
		if ipv4Match is not None:
			ipAddr = ipv4Match.group(1)
			portGroup = ipv4Match.group(2)
			port = int(portGroup) if portGroup is not None else None
			return (None, ipAddr, port)
		ipv6Match = re.match(ipv6Regex, dnp)
		if ipv6Match is not None:
			ipAddr = ipv6Match.group(1)
			portGroup = ipv6Match.group(2)
			port = int(portGroup) if portGroup is not None else None
			return (None, ipAddr, port)
		hostNameMatch = re.match(hostNameRegex, dnp)
		if hostNameMatch is not None:
			hostName = hostNameMatch.group(1)
			portGroup = hostNameMatch.group(2)
			port = int(portGroup) if portGroup is not None else None
			return (hostName, None, port)

		raise ValueError(f'Cannot parse domain and port from: {dnp}')

	@classmethod
	def ParseURI(
		cls,
		uri: str
	) -> Tuple[
		str,
		Union[str, None],
		Union[GENERIC_IP_ADDR, None],
		int,
	]:
		proto, domainAndPort = cls.ParseProto(uri)
		hostName, ipAddr, port = cls.ParseDomainAndPort(domainAndPort)

		if ipAddr is not None:
			ipAddr = ipaddress.ip_address(ipAddr)

		if port is None:
			port = cls.DEFAULT_PORT_LUP.get(proto, None)
			if port is None:
				raise ValueError(
					f'Cannot determine default port for protocol: {proto}'
				)

		return (proto, hostName, ipAddr, port)

	@classmethod
	def FromURI(
		cls,
		uri: str,
		resolver: QuickLookup,
		preferIPv6: bool = DEFAULT_PREFFER_IPV6,
	) -> 'Endpoint':
		proto, hostName, ipAddr, port = cls.ParseURI(uri)
		return cls(
			proto=proto,
			ipAddr=ipAddr,
			hostName=hostName,
			port=port,
			resolver=resolver,
			preferIPv6=preferIPv6,
		)

	def __init__(
		self,
		proto: str,
		ipAddr: Union[GENERIC_IP_ADDR, None],
		hostName: Union[str, None],
		port: int,
		resolver: QuickLookup,
		preferIPv6: bool = DEFAULT_PREFFER_IPV6,
	) -> None:
		super(Endpoint, self).__init__()

		self.proto = proto
		self.ipAddr = ipAddr
		self.hostName = hostName
		self.port = port
		self.resolver = resolver
		self.preferIPv6 = preferIPv6

		self.uuid = uuid.uuid4()

		if (self.ipAddr is None) and (self.hostName is None):
			raise ValueError('Neither IP address nor host name is provided')

	def GetIPAddr(
		self,
		recDepthStack: List[ Tuple[ int, str ] ],
	) -> GENERIC_IP_ADDR:
		if self.ipAddr is not None:
			return self.ipAddr
		else:
			newRecStack = list(recDepthStack) + [
				(self.uuid.int, f'{self.__class__.__name__}.{self.GetIPAddr.__name__}')
			]
			return self.resolver.LookupIpAddr(
				self.hostName,
				preferIPv6=self.preferIPv6,
				recDepthStack=newRecStack,
			)

	def GetHostName(self) -> str:
		if self.hostName is not None:
			return self.hostName
		else:
			return str(self.ipAddr)

