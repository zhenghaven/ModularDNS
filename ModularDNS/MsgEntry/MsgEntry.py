#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


from typing import List

import dns.message
import dns.rrset


class MsgEntry(object):
	@classmethod
	def FromRRSet(cls, rrset: dns.rrset.RRset) -> 'MsgEntry':
		raise NotImplementedError(
			'MsgEntry.FromRRSet() is not implemented'
		)

	@classmethod
	def FromRRSetList(cls, rrsetList: List[dns.rrset.RRset]) -> List['MsgEntry']:
		return [cls.FromRRSet(x) for x in rrsetList]

	def __init__(self, entryType: str) -> None:
		super(MsgEntry, self).__init__()

		self.entryType = entryType

	def ToRRSet(self) -> dns.rrset.RRset:
		raise NotImplementedError(
			'MsgEntry.ToRRSet() is not implemented'
		)

	def ToValDict(self) -> dict:
		raise NotImplementedError(
			'MsgEntry.ToValDict() is not implemented'
		)

	def ToDict(self) -> dict:
		return {
			'dns_entry': self.entryType,
			'entry': self.ToValDict(),
		}

	def __str__(self) -> str:
		return f'{self.ToDict()}'


def AppendToDNSMsg(dnsMsg: dns.message.Message, entry: MsgEntry,) -> None:
	if entry.entryType == 'ANS':
		dnsMsg.answer.append(entry.ToRRSet())
	elif entry.entryType == 'AUTH':
		dnsMsg.authority.append(entry.ToRRSet())
	elif entry.entryType == 'ADD':
		dnsMsg.additional.append(entry.ToRRSet())
	elif entry.entryType == 'QUEST':
		dnsMsg.question.append(entry.ToRRSet())
	else:
		raise TypeError(f'Unknown MsgEntry type {entry.entryType}')


def ConcatDNSMsg(dnsMsg: dns.message.Message, entries: List[MsgEntry],) -> None:
	for entry in entries:
		AppendToDNSMsg(dnsMsg, entry)

