#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


from ...ModuleManager import ModuleManager

from .ByProtocol import ByProtocol
from .Endpoint import Endpoint, StaticEndpoint
from .HTTPS import HTTPS
from .TCP import TCP
from .UDP import UDP


MODULE_MGR = ModuleManager()
MODULE_MGR.RegisterModule('ByProtocol', ByProtocol)
MODULE_MGR.RegisterModule('Endpoint', Endpoint)
MODULE_MGR.RegisterModule('StaticEndpoint', StaticEndpoint)
MODULE_MGR.RegisterModule('HTTPS', HTTPS)
MODULE_MGR.RegisterModule('TCP', TCP)
MODULE_MGR.RegisterModule('UDP', UDP)

