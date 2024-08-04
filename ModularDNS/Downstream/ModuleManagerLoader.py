#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


from ..ModuleManager import ModuleManager

from .Local.ModuleManagerLoader   import MODULE_MGR as LOCAL_MODULE_MGR
from .Logical.ModuleManagerLoader import MODULE_MGR as LOGICAL_MODULE_MGR
from .Remote.ModuleManagerLoader  import MODULE_MGR as REMOTE_MODULE_MGR


MODULE_MGR = ModuleManager()
MODULE_MGR.RegisterSubModuleManager('Local',   LOCAL_MODULE_MGR)
MODULE_MGR.RegisterSubModuleManager('Logical', LOGICAL_MODULE_MGR)
MODULE_MGR.RegisterSubModuleManager('Remote',  REMOTE_MODULE_MGR)

