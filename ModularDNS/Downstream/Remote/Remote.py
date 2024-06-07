#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


from ..QuickLookup import QuickLookup


DEFAULT_TIMEOUT: float = 2.0


class Remote(QuickLookup):

	def __init__(self, timeout: float = DEFAULT_TIMEOUT) -> None:
		super(Remote, self).__init__()

		self.timeout = timeout

