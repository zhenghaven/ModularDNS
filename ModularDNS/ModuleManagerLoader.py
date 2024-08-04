#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


from .ModuleManager import ModuleManager

from .Downstream.ModuleManagerLoader import MODULE_MGR as DOWNSTREAM_MODULE_MGR


MODULE_MGR = ModuleManager()
MODULE_MGR.RegisterSubModuleManager('Downstream', DOWNSTREAM_MODULE_MGR)

