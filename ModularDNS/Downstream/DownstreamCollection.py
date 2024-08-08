#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import re

from typing import Dict, List, Tuple, Union

import dns.message

from ..ModuleManager import ModuleManager
from ..MsgEntry import MsgEntry, QuestionEntry
from .Handler import DownstreamHandler
from .HandlerByQuestion import HandlerByQuestion
from .QuickLookup import QuickLookup
from .Remote.Endpoint import Endpoint


class StaticSharedHandler(DownstreamHandler):

	def __init__(self, handler: DownstreamHandler) -> None:
		super(StaticSharedHandler, self).__init__(
			maxRecDepth=handler.maxRecDepth
		)

		self.handler = handler

	def Handle(
		self,
		dnsMsg: dns.message.Message,
		senderAddr: Tuple[str, int],
		recDepthStack: List[ Tuple[ int, str ] ],
	) -> dns.message.Message:
		return self.handler.Handle(
			dnsMsg,
			senderAddr,
			recDepthStack,
		)

	def Terminate(self) -> None:
		# the underlying handler is shared,
		# thus, the true owner should be responsible for terminating it
		pass


class StaticSharedQuickLookup(QuickLookup):
	'''
	Since `QuickLookup` only depends on the `HandlerByQuestion` interface,
	thus, both instance of `HandlerByQuestion` and `QuickLookup` can use this
	class.
	'''

	def __init__(self, handler: HandlerByQuestion) -> None:
		super(StaticSharedQuickLookup, self).__init__()

		self.handler = handler

	def HandleQuestion(
		self,
		msgEntry: QuestionEntry.QuestionEntry,
		senderAddr: Tuple[str, int],
		recDepthStack: List[ Tuple[ int, str ] ],
	) -> List[ MsgEntry.MsgEntry ]:
		return self.handler.HandleQuestion(
			msgEntry,
			senderAddr,
			recDepthStack,
		)

	def Terminate(self) -> None:
		# the underlying handler is shared,
		# thus, the true owner should be responsible for terminating it
		pass


_OBJ_NAME_PATTERN = re.compile(r'^[a-zA-Z][a-zA-Z0-9_-]+$')


class DownstreamCollection(object):

	__handlerStore: Dict[
		str,
		Union[DownstreamHandler, HandlerByQuestion, QuickLookup]
	]

	__stHandlerLut: Dict[str, StaticSharedHandler]
	__stQuickLookupLut: Dict[str, StaticSharedQuickLookup]

	__endpointStore: Dict[str, Endpoint]

	@classmethod
	def FromConfig(
		cls,
		moduleMgr: ModuleManager,
		config: dict
	) -> 'DownstreamCollection':
		dCollection = cls()

		for item in config['items']:
			modCls = moduleMgr.GetModule(item['module'])
			modName = item['name']
			modConfig: dict = item['config']

			modInst = modCls.FromConfig(
				dCollection=dCollection,
				**modConfig
			)

			if isinstance(modInst, Endpoint):
				dCollection.AddEndpoint(modName, modInst)
			elif isinstance(modInst, DownstreamHandler):
				dCollection.AddHandler(modName, modInst)
			else:
				raise TypeError(
					f'Unsupported module type "{modInst.__class__.__name__}"'
				)

		return dCollection

	def __init__(self) -> None:
		super(DownstreamCollection, self).__init__()

		self.__handlerStore = {}

		self.__stHandlerLut = {}
		self.__stQuickLookupLut = {}

		self.__endpointStore = {}

	def GetNumOfHandlers(self) -> int:
		return len(self.__handlerStore)

	def GetNumOfEndpoints(self) -> int:
		return len(self.__endpointStore)

	def AddHandler(
		self,
		handlerName: str,
		handler: Union[DownstreamHandler, HandlerByQuestion, QuickLookup],
	) -> None:
		if not _OBJ_NAME_PATTERN.match(handlerName):
			raise ValueError('Invalid handler name')

		if handlerName in self.__handlerStore:
			raise KeyError(f'Handler "{handlerName}" already exists')

		if isinstance(handler, QuickLookup):
			stShared = StaticSharedQuickLookup(handler)
			self.__stHandlerLut[handlerName] = stShared
			self.__stQuickLookupLut[handlerName] = stShared
		elif isinstance(handler, HandlerByQuestion):
			stShared = StaticSharedQuickLookup(handler)
			self.__stHandlerLut[handlerName] = stShared
			self.__stQuickLookupLut[handlerName] = stShared
		elif isinstance(handler, DownstreamHandler):
			stShared = StaticSharedHandler(handler)
			self.__stHandlerLut[handlerName] = stShared
		else:
			raise TypeError('Invalid handler type')

		self.__handlerStore[handlerName] = handler

	@classmethod
	def _ParseHandlerRef(cls, refTypeAndHdlrName: str,) -> Tuple[str, str]:
		if ':' not in refTypeAndHdlrName:
			raise ValueError('Invalid handler reference format')

		refType, hdlrName = refTypeAndHdlrName.split(':', maxsplit=1)

		return refType, hdlrName

	def GetStaticSharedHandler(self, hdlrName: str) -> StaticSharedHandler:
		if hdlrName not in self.__stHandlerLut:
			raise KeyError(f'Handler named "{hdlrName}" not found')
		return self.__stHandlerLut[hdlrName]

	def GetStaticSharedQuickLookup(self, hdlrName: str) -> StaticSharedQuickLookup:
		if hdlrName not in self.__stQuickLookupLut:
			raise KeyError(f'QuickLookup Handler named "{hdlrName}" not found')
		return self.__stQuickLookupLut[hdlrName]

	def GetHandler(self, refTypeAndHdlrName: str,) -> DownstreamHandler:
		refType, hdlrName = self._ParseHandlerRef(refTypeAndHdlrName)

		if refType == 's':
			return self.GetStaticSharedHandler(hdlrName)
		else:
			raise ValueError('Unsupported handler reference type')

	def GetHandlerByQuestion(self, refTypeAndHdlrName: str,) -> HandlerByQuestion:
		refType, hdlrName = self._ParseHandlerRef(refTypeAndHdlrName)

		if refType == 's':
			return self.GetStaticSharedQuickLookup(hdlrName)
		else:
			raise ValueError('Unsupported handler reference type')

	def GetQuickLookup(self, refTypeAndHdlrName: str,) -> QuickLookup:
		refType, hdlrName = self._ParseHandlerRef(refTypeAndHdlrName)

		if refType == 's':
			return self.GetStaticSharedQuickLookup(hdlrName)
		else:
			raise ValueError('Unsupported handler reference type')

	def AddEndpoint(self, endpointName: str, endpoint: Endpoint) -> None:
		if not _OBJ_NAME_PATTERN.match(endpointName):
			raise ValueError('Invalid endpoint name')

		if endpointName in self.__endpointStore:
			raise KeyError(f'Endpoint "{endpointName}" already exists')

		if not isinstance(endpoint, Endpoint):
			raise TypeError('Unsupported endpoint type')

		self.__endpointStore[endpointName] = endpoint

	def GetEndpoint(self, endpointName: str) -> Endpoint:
		if endpointName not in self.__endpointStore:
			raise KeyError(f'Endpoint "{endpointName}" not found')
		return self.__endpointStore[endpointName]

	def Terminate(self) -> None:
		self.__stHandlerLut.clear()
		self.__stQuickLookupLut.clear()
		for handler in self.__handlerStore.values():
			handler.Terminate()
		self.__handlerStore.clear()

		for endpoint in self.__endpointStore.values():
			endpoint.Terminate()
		self.__endpointStore.clear()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.Terminate()

