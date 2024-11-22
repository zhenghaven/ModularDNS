#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import copy

import dns.rrset

from .MsgEntry import MsgEntry


class AddEntry(MsgEntry):
	@classmethod
	def FromRRSet(cls, rrset: dns.rrset.RRset) -> 'AddEntry':
		return cls(
			rawSet=rrset,
		)

	@classmethod
	def FromMsgEntry(cls, entry: MsgEntry) -> 'AddEntry':
		return cls(
			rawSet=entry.ToRRSet(),
		)

	def __init__(
		self,
		rawSet: dns.rrset.RRset,
	) -> None:
		super(AddEntry, self).__init__(entryType='ADD')

		self._rawSet = rawSet

	def ToRRSet(self) -> dns.rrset.RRset:
		rrset = copy.deepcopy(self._rawSet)

		return rrset

	def ToValDict(self) -> dict:
		return {
			'rrset': str(self._rawSet.to_text()),
		}

	def __copy__(self) -> 'AddEntry':
		return AddEntry(
			rawSet=copy.copy(self._rawSet),
		)

	def __deepcopy__(self, memo) -> 'AddEntry':
		return AddEntry(
			rawSet=copy.deepcopy(self._rawSet, memo),
		)

	def __eq__(self, other: object) -> bool:
		if isinstance(other, AddEntry):
			return (
				(self._rawSet == other._rawSet)
			)
		else:
			return False

	def __hash__(self) -> int:
		return hash(self._rawSet.to_text())

