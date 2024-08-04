#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


from typing import Callable, Dict, TypeVar


_ModT = TypeVar('_ModT')
ModuleGetter = Callable[[str, str], _ModT]


class ModuleManager(object):

	__modLut: Dict[str, ModuleGetter]

	def __init__(self) -> None:
		super(ModuleManager, self).__init__()

		self.__modLut = {}

	def RegisterModule(self, modName: str, modObj: _ModT) -> None:
		if '.' in modName:
			raise ValueError(
				'Invalid module name, module name should not contain "."'
			)
		if modName in self.__modLut:
			raise KeyError(
				f'Module "{modName}" already registered'
			)

		self.__modLut[modName] = lambda fullName, relName: modObj

	def RegisterSubModuleManager(self, modName: str, modMgr: 'ModuleManager') -> None:
		if '.' in modName:
			raise ValueError(
				'Invalid module name, module name should not contain "."'
			)
		if modName in self.__modLut:
			raise KeyError(
				f'Module "{modName}" already registered'
			)

		self.__modLut[modName] = \
			lambda fullName, relName: modMgr._GetModule(fullName, relName)

	def _GetModule(self, fullName: str, relName: str) -> _ModT:
		if '.' not in relName:
			modName, subModName = relName, ''
		else:
			modName, subModName = relName.split('.', maxsplit=1)

		if modName not in self.__modLut:
			raise KeyError(f'Module "{fullName}" not found')

		return self.__modLut[modName](fullName, subModName)

	def GetModule(self, modName: str) -> _ModT:
		return self._GetModule(modName, modName)

