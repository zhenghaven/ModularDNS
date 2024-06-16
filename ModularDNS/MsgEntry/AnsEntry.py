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

	def __copy__(self) -> 'AnsEntry':
		return AnsEntry(
			name=copy.copy(self.name),
			rdCls=copy.copy(self.rdCls),
			rdType=copy.copy(self.rdType),
			dataList=copy.copy(self.dataList),
			ttl=self.ttl,
		)

	def __deepcopy__(self, memo) -> 'AnsEntry':
		return AnsEntry(
			name=copy.deepcopy(self.name, memo),
			rdCls=copy.deepcopy(self.rdCls, memo),
			rdType=copy.deepcopy(self.rdType, memo),
			dataList=copy.deepcopy(self.dataList, memo),
			ttl=self.ttl,
		)

	def __eq__(self, other: object) -> bool:
		if isinstance(other, AnsEntry):
			return (
				(self.name == other.name) and
				(self.rdCls == other.rdCls) and
				(self.rdType == other.rdType) and
				(self.dataList == other.dataList) and
				(self.ttl == other.ttl)
			)
		else:
			return False

	def __hash__(self) -> int:
		return hash((
			self.entryType,
			self.name,
			self.rdCls,
			self.rdType,
			tuple(self.dataList),
			self.ttl,
		))

