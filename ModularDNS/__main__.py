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
from .Service import Resolver


def main() -> None:
	argParser = argparse.ArgumentParser(
		description=PACKAGE_INFO['description'],
		prog='',
	)
	argParser.add_argument(
		'--version',
		action='version', version=PACKAGE_INFO['version'],
	)
	opArgParser = argParser.add_subparsers(
		title='Services',
		dest='service',
	)
	reolveOpArgParser = opArgParser.add_parser(
		'resolve',
		help='Run the DNS resolver service',
	)
	reolveOpArgParser.add_argument(
		'--config', '-c',
		type=str, required=True,
		help='Path to the configuration file',
	)
	args = argParser.parse_args()

	if args.service == 'resolve':
		Resolver.Start(configPath=args.config)
	else:
		raise ValueError(f'Invalid service: {args.service}')


if __name__ == '__main__':
	main()

