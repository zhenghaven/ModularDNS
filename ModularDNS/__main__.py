#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import argparse

from . import PACKAGE_INFO


def main() -> None:
	argParser = argparse.ArgumentParser(
		description=PACKAGE_INFO['description'],
		prog='',
	)
	argParser.add_argument(
		'--version',
		action='version', version=PACKAGE_INFO['version'],
	)
	args = argParser.parse_args()


if __name__ == '__main__':
	main()

