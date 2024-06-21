#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import copy

from typing import List, Tuple, Union

from CacheLib.TTL import Interfaces as _CLTTLInterfaces
from CacheLib.TTL import MultiKeyMultiTTLValueCache

from ...MsgEntry import AnsEntry, MsgEntry, QuestionEntry
from ..HandlerByQuestion import HandlerByQuestion
from ..QuickLookup import QuickLookup


class CacheItem(_CLTTLInterfaces.KeyValueItem):
	'''
	# CacheItem

	This is a wrapper class for items being stored in the cache.

	Each cache item should consist of:
	- A single key, which is the question of the DNS query.
	- A list of `MsgEntry` objects, which should be the response to the DNS query.
	- A TTL value, which should be derived from the (shortest) TTL value of the
	  `MsgEntry` objects.
	  - If none of the `MsgEntry` objects have a TTL value, the default TTL
	    value will be used.
	'''

	DEFAULT_TTL = 3600.0

	def __init__(
		self,
		question: QuestionEntry.QuestionEntry,
		resps: List[MsgEntry.MsgEntry],
		defaultTTL: float = DEFAULT_TTL,
	) -> None:
		super(CacheItem, self).__init__()

		self._question = question
		self._resps = resps
		self._defaultTTL = defaultTTL

		# calculate the TTL value
		self._ttl = None
		for resp in resps:
			if resp.entryType == 'ANS':
				resp: AnsEntry.AnsEntry = resp
				self._ttl = resp.ttl if (self._ttl is None) else min(self._ttl, resp.ttl)
		if self._ttl is None:
			self._ttl = self._defaultTTL

	def GetKeys(self) -> List[_CLTTLInterfaces.KeyValueKey]:
		return [self._question]

	def GetTTL(self) -> float:
		return self._ttl

	def Terminate(self) -> None:
		# nothing to do in this case
		pass

	def GetResp(self) -> List[MsgEntry.MsgEntry]:
		return [ copy.copy(x) for x in self._resps ]


class Cache(QuickLookup):

	DEFAULT_TTL = CacheItem.DEFAULT_TTL

	def __init__(
		self,
		fallback: HandlerByQuestion,
		defaultTTL: float = DEFAULT_TTL,
	) -> None:
		super(QuickLookup, self).__init__()

		self._fallback = fallback
		self._defaultTTL = defaultTTL

		self._cache = MultiKeyMultiTTLValueCache.MultiKeyMultiTTLValueCache()

	def HandleQuestion(
		self,
		msgEntry: QuestionEntry.QuestionEntry,
		senderAddr: Tuple[str, int],
		recDepthStack: List[ Tuple[ int, str ] ],
	) -> List[ MsgEntry.MsgEntry ]:

		cachedItem: Union[CacheItem, None] = self._cache.Get(msgEntry)
		if cachedItem is not None:
			return cachedItem.GetResp()
		else:
			# cache miss
			newRecStack = self.CheckRecursionDepth(
				recDepthStack,
				self.HandleQuestion
			)
			respEntries = self._fallback.HandleQuestion(
				msgEntry=msgEntry,
				senderAddr=senderAddr,
				recDepthStack=newRecStack,
			)

			# cache the response
			cachedItem = CacheItem(
				question=msgEntry,
				resps=respEntries,
				defaultTTL=self._defaultTTL,
			)
			self._cache.Put(
				cachedItem,
				# it's fine that another thread already cached the item
				raiseIfKeyExist=False,
			)

			return cachedItem.GetResp()

