#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import logging

from tests.unittesting import main


if __name__ == '__main__':
	logging.basicConfig(
		level=logging.DEBUG,
		format='%(asctime)s %(name)s[%(levelname)s]: %(message)s',
	)
	main()

