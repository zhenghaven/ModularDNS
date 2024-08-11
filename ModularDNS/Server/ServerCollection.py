#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import re
import threading

from typing import Dict

from ..Downstream.DownstreamCollection import DownstreamCollection
from ..ModuleManager import ModuleManager
from .Server import Server


_OBJ_NAME_PATTERN = re.compile(r'^[a-zA-Z][a-zA-Z0-9_-]+$')


class ServerCollection(object):

	__serverStore: Dict[str, Server]

	@classmethod
	def FromConfig(
		cls,
		moduleMgr: ModuleManager,
		dCollection: DownstreamCollection,
		config: dict,
	) -> 'ServerCollection':
		sCollection = cls()

		for item in config['items']:
			modCls = moduleMgr.GetModule(item['module'])
			modName = item['name']
			modConfig: dict = item['config']

			modInst = modCls.FromConfig(
				dCollection=dCollection,
				**modConfig
			)

			if isinstance(modInst, Server):
				sCollection.AddServer(modName, modInst)
			else:
				raise TypeError(
					f'Unsupported module type "{modInst.__class__.__name__}"'
				)

		return sCollection

	def __init__(self) -> None:
		self.__serverStore = {}

		self.__stateLock = threading.Lock()
		self.__hasStartServe = False

	def GetNumOfServers(self) -> int:
		return len(self.__serverStore)

	def AddServer(self, name: str, server: Server) -> None:
		if not _OBJ_NAME_PATTERN.match(name):
			raise ValueError('Invalid server name')

		if name in self.__serverStore:
			raise KeyError(f'Server "{name}" already exists')

		if isinstance(server, Server):
			self.__serverStore[name] = server
		else:
			raise TypeError('Invalid server type')

	def Terminate(self) -> None:
		for server in self.__serverStore.values():
			server.Terminate()
		self.__serverStore.clear()

	def ThreadedServeUntilTerminate(self) -> None:
		with self.__stateLock:
			if self.__hasStartServe:
				raise RuntimeError('The servers have already started')
			self.__hasStartServe = True

		for server in self.__serverStore.values():
			server.ThreadedServeUntilTerminate()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.Terminate()

