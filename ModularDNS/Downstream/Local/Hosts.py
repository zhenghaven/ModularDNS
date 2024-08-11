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

from typing import Dict, List, Set, Tuple, Union

import dns.rdata
import dns.rdataclass
import dns.rdatatype

from ...Exceptions import DNSNameNotFoundError, DNSZeroAnswerError
from ...MsgEntry import AnsEntry, MsgEntry, QuestionEntry
from ..DownstreamCollection import DownstreamCollection
from ..QuickLookup import QuickLookup


GENERIC_IP_ADDR = Union[ipaddress.IPv4Address, ipaddress.IPv6Address]


def _DottedName(name: str) -> str:
	return (name + '.') \
		if (name[-1] != '.') \
			else name


class Hosts(QuickLookup):

	DEFAULT_TTL = 3600

	@classmethod
	def FromConfig(
		cls,
		dCollection: DownstreamCollection,
		config: dict
	) -> 'Hosts':
		ttl = config.get('ttl', cls.DEFAULT_TTL)
		records: List[ dict ] = config.get('records', list())
		inst = cls(ttl=ttl)
		for record in records:
			domain = record.get('domain', '')
			recWoDomain: Dict[str, list] = {
				k: v for k, v in record.items()
				if k != 'domain'
			}
			for recType, recData in recWoDomain.items():
				if recType.lower() == 'ip':
					ipList = recData
					for ipAddrStr in ipList:
						ipAddr = ipaddress.ip_address(ipAddrStr)
						inst.AddAddrRecord(domain=domain, ipAddr=ipAddr)
				elif recType.lower() == 'cname':
					for cname in recData:
						inst.AddCNameRecord(domain=domain, cname=cname)
				else:
					raise ValueError('Unsupported record type')

		return inst

	def __init__(self, ttl: int = DEFAULT_TTL) -> None:
		super(Hosts, self).__init__()

		self.lutLock = threading.Lock()
		self.lut = {}
		self.ttl = ttl

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

			# As per CNAME restrictions, A CNAME record cannot co-exist with
			# another record for the same name.
			if (
				(dns.rdatatype.CNAME in rdClsLut) or
				# We are adding a record, but a CNAME record is already present, OR
				((rdType == dns.rdatatype.CNAME) and (len(rdClsLut) > 0))
				# We are adding a CNAME record, but some other record is already present
			):
				raise TypeError('CNAME record cannot co-exist with other records')

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

	def AddCNameRecord(
		self,
		domain: str,
		cname: str
	) -> None:
		rdCls = dns.rdataclass.IN
		rdType = dns.rdatatype.CNAME
		rdata = dns.rdata.from_text(
			rdclass=rdCls,
			rdtype=rdType,
			tok=cname
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

	def _LookupLocked(
		self,
		domain: str,
		rdCls: dns.rdataclass.RdataClass,
		rdType: dns.rdatatype.RdataType,
		throwWhenNoDomain: bool = True,
		throwWhenNoAns: bool = True,
	) -> List[ AnsEntry.AnsEntry ]:
		if domain not in self.lut:
			if throwWhenNoDomain:
				raise DNSNameNotFoundError(name=domain, respServer=self._clsName)
			else:
				return []

		domainLut: dict = self.lut.get(domain, dict())
		rdClsLut: dict = domainLut.get(rdCls, dict())

		if (
			(rdType != dns.rdatatype.CNAME) and
			(dns.rdatatype.CNAME in rdClsLut)
		):
			# As per CNAME restrictions, A CNAME record cannot co-exist with
			# another record for the same name.
			recSet: Set[dns.rdata.Rdata] = rdClsLut[dns.rdatatype.CNAME]
			cnameDomain: dns.rdata.Rdata = next(iter(recSet))
			cnameDomainStr = cnameDomain.to_text()
			if cnameDomainStr.endswith('.'):
				cnameDomainStr = cnameDomainStr[:-1]
			else:
				cnameDomainStr = cnameDomainStr + '.' + domain

			return [
				AnsEntry.AnsEntry(
					name=dns.name.from_text(domain),
					rdCls=rdCls,
					rdType=dns.rdatatype.CNAME,
					dataList=[
						dns.rdata.from_text(
							rdclass=rdCls,
							rdtype=dns.rdatatype.CNAME,
							tok=_DottedName(cnameDomainStr),
						)
					],
					ttl=self.ttl,
				)
			 ] + self._LookupLocked(
				domain=cnameDomainStr,
				rdCls=rdCls,
				rdType=rdType,
				throwWhenNoDomain=False,
				throwWhenNoAns=False,
			)
		else:
			recSet: Set[dns.rdata.Rdata] = rdClsLut.get(rdType, set())
			if len(recSet) == 0:
				if throwWhenNoAns:
					raise DNSZeroAnswerError(name=domain)
				else:
					return []

			dataList = [ copy.deepcopy(rec) for rec in recSet ]

			return [
				AnsEntry.AnsEntry(
					name=dns.name.from_text(domain),
					rdCls=rdCls,
					rdType=rdType,
					dataList=dataList,
					ttl=self.ttl,
				)
			]

	def Lookup(
		self,
		domain: str,
		rdCls: dns.rdataclass.RdataClass,
		rdType: dns.rdatatype.RdataType,
		throwWhenNoDomain: bool = True,
		throwWhenNoAns: bool = True,
	) -> List[dns.rdata.Rdata]:
		with self.lutLock:
			return self._LookupLocked(
				domain=domain,
				rdCls=rdCls,
				rdType=rdType,
				throwWhenNoDomain=throwWhenNoDomain,
				throwWhenNoAns=throwWhenNoAns,
			)

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

		return self.Lookup(
			domain=domain,
			rdCls=msgEntry.rdCls,
			rdType=msgEntry.rdType,
			throwWhenNoDomain=True,
			throwWhenNoAns=True,
		)

	def Terminate(self) -> None:
		# nothing to terminate/close
		pass

