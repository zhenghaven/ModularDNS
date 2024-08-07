#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


from setuptools import setup
from setuptools import find_packages

from ModularDNS import PACKAGE_INFO


setup(
	name        = PACKAGE_INFO['name'],
	description = PACKAGE_INFO['description'],
	version     = PACKAGE_INFO['version'],
	author      = PACKAGE_INFO['author'],
	url         = PACKAGE_INFO['url'],
	license     = PACKAGE_INFO['license'],

	packages    = find_packages(
		where='.',
		exclude=[
			'setup.py',
			'run_unittest.py',
			'test*',
		]
	),

	python_requires  = '>=3.9',
	install_requires = [
		'dnspython>=2.6.0,<3.0.0',
		'requests>=2.32.0,<3.0.0',
		'CacheLib @ git+https://github.com/zhenghaven/PyCacheLib.git@v0.1.3'
	],

	entry_points     = {
		'console_scripts': [
			'{pkgName}={pkgName}.__main__:main'.format(pkgName=PACKAGE_INFO['name']),
		]
	},
)

