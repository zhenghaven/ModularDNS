#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import copy
import ipaddress
import threading

from typing import List, Tuple, Union

import dns.rdata
import dns.rdataclass
import dns.rdatatype

from ...Exceptions import DNSNameNotFoundError, DNSZeroAnswerError
from ...MsgEntry import AnsEntry, MsgEntry, QuestionEntry
from ..QuickLookup import QuickLookup


GENERIC_IP_ADDR = Union[ipaddress.IPv4Address, ipaddress.IPv6Address]


class Hosts(QuickLookup):

	DEFAULT_TTL = 3600

	@classmethod
	def FromConfig(cls, config: dict) -> 'Hosts':
		ttl = config.get('ttl', cls.DEFAULT_TTL)
		records: List[ dict ] = config.get('records', list())
		inst = cls(ttl=ttl)
		for record in records:
			domain = record.get('domain', '')
			if 'ip' in record:
				ipList = record.get('ip', list())
				for ipAddrStr in ipList:
					ipAddr = ipaddress.ip_address(ipAddrStr)
					inst.AddAddrRecord(domain=domain, ipAddr=ipAddr)
			else:
				raise ValueError('Unsupported record type')

		return inst

	def __init__(self, ttl: int = DEFAULT_TTL) -> None:
		super(Hosts, self).__init__()

		self.lutLock = threading.Lock()
		self.lut = {}
		self.ttl = ttl

		self._clsName = f'{__name__}.{self.__class__.__name__}'

	def AddRecord(
		self,
		domain: str,
		rdCls: dns.rdataclass.RdataClass,
		rdType: dns.rdatatype.RdataType,
		rdata: dns.rdata.Rdata
	) -> None:
		# remove the final dot if exists
		if domain[-1] == '.':
			domain = domain[:-1]

		with self.lutLock:
			if domain not in self.lut:
				self.lut[domain] = dict()
			domainLut: dict = self.lut[domain]

			if rdCls not in domainLut:
				domainLut[rdCls] = dict()
			rdClsLut: dict = domainLut[rdCls]

			if rdType not in rdClsLut:
				rdClsLut[rdType] = set()
			recSet: set = rdClsLut[rdType]

			if rdata not in recSet:
				recSet.add(rdata)

	def AddAddrRecord(
		self,
		domain: str,
		ipAddr: GENERIC_IP_ADDR
	) -> None:
		rdCls = dns.rdataclass.IN

		if ipAddr.version == 4:
			rdType = dns.rdatatype.A
		elif ipAddr.version == 6:
			rdType = dns.rdatatype.AAAA
		else:
			raise ValueError(f'Unsupported IP version: {ipAddr.version}')

		rdata = dns.rdata.from_text(
			rdclass=rdCls,
			rdtype=rdType,
			tok=str(ipAddr)
		)

		self.AddRecord(
			domain=domain,
			rdCls=rdCls,
			rdType=rdType,
			rdata=rdata
		)

	def GetNumDomains(self) -> int:
		with self.lutLock:
			return len(self.lut)

	def HandleQuestion(
		self,
		msgEntry: QuestionEntry.QuestionEntry,
		senderAddr: Tuple[str, int],
		recDepthStack: List[ Tuple[ int, str ] ],
	) -> List[ MsgEntry.MsgEntry ]:
		newRecStack = self.CheckRecursionDepth(
			recDepthStack,
			self.HandleQuestion
		)

		domain = msgEntry.GetNameStr(omitFinalDot=True)

		with self.lutLock:
			if domain not in self.lut:
				raise DNSNameNotFoundError(name=domain, respServer=self._clsName)

			domainLut: dict = self.lut.get(domain, dict())
			rdClsLut: dict = domainLut.get(msgEntry.rdCls, dict())
			recSet: List[dns.rdata.Rdata] = rdClsLut.get(msgEntry.rdType, set())

			if len(recSet) == 0:
				raise DNSZeroAnswerError(name=domain)

			dataList = [ copy.deepcopy(rec) for rec in recSet ]

			return [
				AnsEntry.AnsEntry(
					name=msgEntry.name,
					rdCls=msgEntry.rdCls,
					rdType=msgEntry.rdType,
					dataList=dataList,
					ttl=self.ttl,
				)
			]

