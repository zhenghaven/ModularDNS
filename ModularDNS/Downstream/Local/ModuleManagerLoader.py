#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


from ...ModuleManager import ModuleManager

from .Cache import Cache
from .Hosts import Hosts


MODULE_MGR = ModuleManager()
MODULE_MGR.RegisterModule('Cache', Cache)
MODULE_MGR.RegisterModule('Hosts', Hosts)

