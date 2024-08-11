#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import json
import logging
import os

from typing import Optional, Union

from .. import Logger
from ..Downstream.DownstreamCollection import DownstreamCollection
from ..ModuleManagerLoader import MODULE_MGR as ROOT_MODULE_MGR
from ..Server.ServerCollection import ServerCollection
from ..SignalHandler import WaitUntilSignals


def Start(
	config: Optional[dict] = None,
	configPath: Optional[Union[str, os.PathLike]] = None,
) -> None:

	if config is None and configPath is None:
		raise ValueError('No configuration provided.')

	if config is not None and configPath is not None:
		raise ValueError(
			'Both configuration and configuration file path are provided.'
		)

	if config is None:
		with open(configPath, 'r') as configFile:
			config = json.load(configFile)

	Logger.InitializeFromConfig(config.get('logger', {}))

	logger = logging.getLogger(f'{__name__}.{Start.__name__}')

	logger.info('Starting Resolver service...')

	with DownstreamCollection.FromConfig(
		moduleMgr=ROOT_MODULE_MGR,
		config=config['downstream'],
	) as dCollection:
		with ServerCollection.FromConfig(
			moduleMgr=ROOT_MODULE_MGR,
			dCollection=dCollection,
			config=config['server'],
		) as sCollection:
			sCollection.ThreadedServeUntilTerminate()

			WaitUntilSignals().Wait()

	logger.info('Resolver service terminated.')

