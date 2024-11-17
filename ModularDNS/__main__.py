#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import argparse

from .Service import Resolver


def GetPackageInfo() -> dict:
	import os

	thisDir = os.path.dirname(os.path.abspath(__file__))
	possibleRepoDir = os.path.dirname(thisDir)
	possibleTomlPath = os.path.join(possibleRepoDir, 'pyproject.toml')

	pkgInfo = {
		'name': __package__ or __name__,
	}

	if os.path.exists(possibleTomlPath):
		import tomllib
		with open(possibleTomlPath, 'rb') as file:
			tomlData = tomllib.load(file)
		if (
			('project' in tomlData) and
			('name' in tomlData['project']) and
			(tomlData['project']['name'] == pkgInfo['name'])
		):
			pkgInfo['description'] = tomlData['project']['description']
			pkgInfo['version'] = tomlData['project']['version']
			return pkgInfo

	import importlib
	pkgInfo['version'] = importlib.metadata.version(pkgInfo['name'])
	pkgInfo['description'] = importlib.metadata.metadata(pkgInfo['name'])['Summary']
	return pkgInfo



def main() -> None:
	pkgInfo = GetPackageInfo()

	argParser = argparse.ArgumentParser(
		description=pkgInfo['description'],
		prog='',
	)
	argParser.add_argument(
		'--version',
		action='version', version=pkgInfo['version'],
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

