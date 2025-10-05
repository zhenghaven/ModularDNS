#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2025 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import ipaddress

import dns.name
import dns.rdata
import dns.rdataclass
import dns.rdatatype

from ...MsgEntry import AnsEntry, MsgEntry, QuestionEntry
from ..DownstreamCollection import DownstreamCollection
from ..QuickLookup import QuickLookup


class ConstAns(QuickLookup):

	@classmethod
	def FromConfig(
		cls,
		dCollection: DownstreamCollection,
		records: list[tuple[str, str]],
	) -> 'ConstAns':
		recDict = {}
		def addRec(recType: dns.rdatatype.RdataType, value: str) -> None:
			if recType not in recDict:
				recDict[recType] = []
			recDict[recType].append(value)

		for tpy, val in records:
			if tpy.lower() == 'a':
				ipVal = ipaddress.ip_address(val)
				assert ipVal.version == 4, f'Invalid A record value: {val}'
				addRec(dns.rdatatype.A, str(ipVal))
			elif tpy.lower() == 'aaaa':
				ipVal = ipaddress.ip_address(val)
				assert ipVal.version == 6, f'Invalid AAAA record value: {val}'
				addRec(dns.rdatatype.AAAA, str(ipVal))
			elif tpy.lower() == 'cname':
				addRec(dns.rdatatype.CNAME, val)
			elif tpy.lower() == 'mx':
				addRec(dns.rdatatype.MX, val)
			else:
				raise ValueError(f'Unsupported record type: {tpy}')

		return cls(
			recDict=recDict,
		)

	def __init__(
		self,
		recDict: dict[dns.rdatatype.RdataType, list[str]] = {},
	) -> None:
		super(ConstAns, self).__init__()

		self._recDict = recDict

	def HandleQuestion(
		self,
		msgEntry: QuestionEntry.QuestionEntry,
		senderAddr: tuple[str, int],
		recDepthStack: list[ tuple[ int, str ] ],
	) -> list[ MsgEntry.MsgEntry ]:
		qType = msgEntry.rdType
		rdCls = msgEntry.rdCls

		if rdCls != dns.rdataclass.IN:
			# no answer
			return []

		if qType not in self._recDict:
			# no answer
			return []

		domain = msgEntry.GetNameStr(omitFinalDot=True)
		name = dns.name.from_text(domain)

		rdataList: list[dns.rdata.Rdata] = []
		for rdataText in self._recDict[qType]:
			rdata = dns.rdata.from_text(
				rdclass=rdCls,
				rdtype=qType,
				tok=rdataText
			)
			rdataList.append(rdata)

		return [
			AnsEntry.AnsEntry(
				name=name,
				rdCls=rdCls,
				rdType=qType,
				dataList=rdataList,
				ttl=300,
			)
		]

	def Terminate(self) -> None:
		# nothing to terminate/cleanup
		pass

