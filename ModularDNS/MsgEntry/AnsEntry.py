#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import ipaddress

from typing import List, Union

import dns.name
import dns.rdata
import dns.rdataclass
import dns.rdatatype
import dns.rrset

from .MsgEntry import MsgEntry


class AnsEntry(MsgEntry):
	@classmethod
	def FromRRSet(cls, rrset: dns.rrset.RRset) -> 'AnsEntry':
		return cls(
			name=rrset.name,
			rdCls=rrset.rdclass,
			rdType=rrset.rdtype,
			dataList=[ x for x in rrset.items ],
			ttl=rrset.ttl,
		)

	def __init__(
		self,
		name: dns.name.Name,
		rdCls: dns.rdataclass.RdataClass,
		rdType: dns.rdatatype.RdataType,
		dataList: List[ dns.rdata.Rdata ],
		ttl: int = 3600,
	) -> None:
		super(AnsEntry, self).__init__(entryType='ANS')

		self.name = name
		self.rdCls = rdCls
		self.rdType = rdType
		self.dataList = dataList
		self.ttl = ttl

		# check if rdclass and rdtype are consistent
		for d in dataList:
			if d.rdclass != self.rdCls:
				lName = dns.rdataclass.RdataClass.to_text(d.rdclass)
				rName = dns.rdataclass.RdataClass.to_text(self.rdCls)
				raise ValueError(f'Inconsistent rdclass: {lName} != {rName}')
			if d.rdtype != self.rdType:
				lName = dns.rdatatype.RdataType.to_text(d.rdtype)
				rName = dns.rdatatype.RdataType.to_text(self.rdType)
				raise ValueError(f'Inconsistent rdtype: {lName} != {rName}')

	def ToRRSet(self) -> dns.rrset.RRset:
		rrset = dns.rrset.from_rdata_list(
			name=self.name,
			ttl=self.ttl,
			rdatas=self.dataList,
		)

		return rrset

	def ToValDict(self) -> dict:
		return {
			'name': str(self.name.to_text()),
			'class': str(self.rdCls.to_text()),
			'type': str(self.rdType.to_text()),
			'data': [ str(x) for x in self.dataList ],
			'ttl': self.ttl,
		}

	def GetAddresses(
		self
	) -> List[Union[ipaddress.IPv4Address, ipaddress.IPv6Address]]:
		return [ ipaddress.ip_address(x.address) for x in self.dataList ]

