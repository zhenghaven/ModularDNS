#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


from ...ModuleManager import ModuleManager

from .Failover import Failover
from .LimitConcurrentReq import LimitConcurrentReq
from .QuestionRuleSet import QuestionRuleSet
from .RaiseExcept import RaiseExcept
from .RandomChoice import RandomChoice


MODULE_MGR = ModuleManager()
MODULE_MGR.RegisterModule('Failover', Failover)
MODULE_MGR.RegisterModule('LimitConcurrentReq', LimitConcurrentReq)
MODULE_MGR.RegisterModule('QuestionRuleSet', QuestionRuleSet)
MODULE_MGR.RegisterModule('RaiseExcept', RaiseExcept)
MODULE_MGR.RegisterModule('RandomChoice', RandomChoice)

