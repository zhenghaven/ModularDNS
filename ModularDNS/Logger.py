#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import logging
import os

from typing import Optional, Union


_DEFAULT_FMT = '[%(asctime)s](%(levelname)s)[%(name)s]:%(message)s'
_DEFAULT_LVL = 'INFO'


def Initialize(
	fmt: str = _DEFAULT_FMT,
	logLevel: str = _DEFAULT_LVL,
	enableConsole: bool = True,
	logFilePath: Optional[Union[str, os.PathLike]] = None,
) -> None:

	formatter = logging.Formatter(fmt=fmt)
	rootLogger = logging.root

	logLevel = getattr(logging, logLevel.upper())

	rootLogger.setLevel(logLevel)

	if enableConsole:
		consoleHandler = logging.StreamHandler()
		consoleHandler.setFormatter(formatter)
		consoleHandler.setLevel(logLevel)
		rootLogger.addHandler(consoleHandler)

	if logFilePath is not None:
		fileHandler = logging.FileHandler(logFilePath)
		fileHandler.setFormatter(formatter)
		fileHandler.setLevel(logLevel)
		rootLogger.addHandler(fileHandler)


def InitializeFromConfig(config: dict) -> None:
	Initialize(
		fmt=config.get('fmt', _DEFAULT_FMT),
		logLevel=config.get('level', _DEFAULT_LVL),
		enableConsole=config.get('console', True),
		logFilePath=config.get('file', None),
	)

