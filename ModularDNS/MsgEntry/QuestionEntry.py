#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import dns.message
import dns.name
import dns.rdataclass
import dns.rdatatype
import dns.rrset

from .MsgEntry import MsgEntry


class QuestionEntry(MsgEntry):
	@classmethod
	def FromRRSet(cls, rrset: dns.rrset.RRset) -> 'QuestionEntry':
		return cls(
			name=rrset.name,
			rdCls=rrset.rdclass,
			rdType=rrset.rdtype,
		)

	def __init__(
		self,
		name: dns.name.Name,
		rdCls: dns.rdataclass.RdataClass,
		rdType: dns.rdatatype.RdataType,
	) -> None:
		super(QuestionEntry, self).__init__(entryType='QUEST')

		self.name = name
		self.rdCls = rdCls
		self.rdType = rdType

	def ToRRSet(self) -> dns.rrset.RRset:
		rrset = dns.rrset.RRset(
			name=self.name,
			rdclass=self.rdCls,
			rdtype=self.rdType,
		)

		return rrset

	def ToValDict(self) -> dict:
		return {
			'name': str(self.name.to_text()),
			'class': str(self.rdCls.to_text()),
			'type': str(self.rdType.to_text()),
		}

	def GetNameStr(self, omitFinalDot: bool = True) -> str:
		return self.name.to_text(omit_final_dot=omitFinalDot)

	def MakeQuery(self) -> dns.message.Message:
		msg = dns.message.make_query(
			qname=self.name,
			rdclass=self.rdCls,
			rdtype=self.rdType,
		)

		return msg

