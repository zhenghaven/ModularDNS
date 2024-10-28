#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


from typing import List, Tuple

import dns.message

from CacheLib.TTL import Interfaces, ObjFactoryCache

from .Endpoint import Endpoint
from .Protocol import Protocol, _REMOTE_INFO


class ConcurrentMgrCache(ObjFactoryCache.ObjFactoryCache):

	WARNING_SIZE_LIMIT: int = 500

	def Get(self, trackInUse: bool = ...) -> Interfaces.Terminable:
		obj = super(ConcurrentMgrCache, self).Get(trackInUse)

		sizeCount = len(self)
		if sizeCount >= self.WARNING_SIZE_LIMIT:
			self.logger.warning(
				f'Number of session, {sizeCount}, '
				f'exceeds warning limit {self.WARNING_SIZE_LIMIT}'
			)

		return obj


class ConcurrentMgr(Protocol):

	MAX_SESSION_TTL: float = 600.0
	'''
	Keep the underlying protocol session object for 10 minutes
	'''

	SESSION_CLASS: Protocol = None
	'''
	The class of the underlying protocol session object

	This MUST be overridden by the subclass and it MUST be a subclass of `Protocol`
	'''

	def __init__(self, endpoint: Endpoint, timeout: float) -> None:
		super(ConcurrentMgr, self).__init__(
			endpoint=endpoint,
			timeout=timeout
		)

		self.cache = ConcurrentMgrCache(
			ttl=self.MAX_SESSION_TTL,
			objCls=self.SESSION_CLASS,
			objKwargs={
				'endpoint': self.endpoint,
				'timeout': self.timeout,
			}
		)

	def Query(
		self,
		q: dns.message.Message,
		recDepthStack: List[ Tuple[ int, str ] ],
	) -> Tuple[dns.message.Message, _REMOTE_INFO]:

		# Get a session object from the cache
		# and remember to put it back after use
		# even if an exception is raised
		session: Protocol = self.cache.Get()
		try:
			resp = session.Query(
				q=q,
				recDepthStack=recDepthStack
			)
		finally:
			self.cache.Put(session)

		return resp

	def Terminate(self) -> None:
		self.cache.Terminate()

