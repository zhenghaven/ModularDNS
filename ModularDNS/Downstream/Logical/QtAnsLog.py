#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import logging
import re

from typing import List, Tuple

import dns.rdataclass
import dns.rdatatype

from ... import Logger
from ...MsgEntry import MsgEntry, QuestionEntry
from ..DownstreamCollection import DownstreamCollection
from ..QuickLookup import QuickLookup
from ..HandlerByQuestion import HandlerByQuestion


class QtAnsLog(QuickLookup):

	_DEFAULT_LOGGER_NAME = 'QtAnsLog'
	_DEFAULT_LOG_MODE = 'w'
	_DEFAULT_CLEAN_LOG_HANDLER = True
	_DEFAULT_QT_NAME_REGEX_EXPR = r'^.*$'
	_DEFAULT_QT_CLS  = dns.rdataclass.ANY
	_DEFAULT_QT_TYPE = dns.rdatatype.ANY
	_DEFAULT_QT_CLS_STR = dns.rdataclass.to_text(dns.rdataclass.ANY)
	_DEFAULT_QT_TYPE_STR = dns.rdatatype.to_text(dns.rdatatype.ANY)

	@classmethod
	def FromConfig(
		cls,
		dCollection: DownstreamCollection,
		qtHandler: str,
		logPath: str,
		loggerName: str = _DEFAULT_LOGGER_NAME,
		logMode: str = _DEFAULT_LOG_MODE,
		cleanLogHandler: bool = _DEFAULT_CLEAN_LOG_HANDLER,
		qtNameRegexExpr: str = _DEFAULT_QT_NAME_REGEX_EXPR,
		qtCls: str = _DEFAULT_QT_CLS_STR,
		qtType: str = _DEFAULT_QT_TYPE_STR,
	) -> 'QtAnsLog':
		return cls(
			qtHandler=dCollection.GetHandlerByQuestion(qtHandler),
			logPath=logPath,
			loggerName=loggerName,
			logMode=logMode,
			cleanLogHandler=cleanLogHandler,
			qtNameRegexExpr=qtNameRegexExpr,
			qtCls=dns.rdataclass.from_text(qtCls),
			qtType=dns.rdatatype.from_text(qtType),
		)

	def __init__(
		self,
		qtHandler: HandlerByQuestion,
		logPath: str,
		loggerName: str = _DEFAULT_LOGGER_NAME,
		logMode: str = _DEFAULT_LOG_MODE,
		cleanLogHandler: bool = _DEFAULT_CLEAN_LOG_HANDLER,
		qtNameRegexExpr: str = _DEFAULT_QT_NAME_REGEX_EXPR,
		qtCls: dns.rdataclass.RdataClass = _DEFAULT_QT_CLS,
		qtType: dns.rdatatype.RdataType = _DEFAULT_QT_TYPE,
	) -> None:
		super(QtAnsLog, self).__init__()

		self.qtHandler = qtHandler
		self.logPath = logPath
		self.loggerName = loggerName
		self.logMode = logMode
		self.qtNameRegexExpr = qtNameRegexExpr
		self.qtCls = qtCls
		self.qtType = qtType

		self.qtNameRegex = re.compile(self.qtNameRegexExpr)

		self.QtAnsLogger = logging.getLogger(self.loggerName)
		if cleanLogHandler:
			existHdlrs = [ x for x in self.QtAnsLogger.handlers ]
			for hdlr in existHdlrs:
				self.QtAnsLogger.removeHandler(hdlr)
		self.logHandler = logging.FileHandler(self.logPath, mode=self.logMode)
		self.logHandler.setFormatter(logging.Formatter(fmt=Logger.DEFAULT_FMT))
		self.logHandler.setLevel(logging.INFO)
		self.QtAnsLogger.addHandler(self.logHandler)

	def _MatchQtCls(self, qtCls: dns.rdataclass.RdataClass) -> bool:
		return (
			(self.qtCls == dns.rdataclass.ANY) or
			(self.qtCls == qtCls)
		)

	def _MatchQtType(self, qtType: dns.rdatatype.RdataType) -> bool:
		return (
			(self.qtType == dns.rdatatype.ANY) or
			(self.qtType == qtType)
		)

	def _MatchQtName(self, qtName: str) -> bool:
		return self.qtNameRegex.match(qtName) is not None

	def _MatchQuestion(self, msgEntry: QuestionEntry.QuestionEntry) -> bool:
		return (
			self._MatchQtCls(msgEntry.rdCls) and
			self._MatchQtType(msgEntry.rdType) and
			self._MatchQtName(msgEntry.GetNameStr())
		)

	def HandleQuestion(
		self,
		msgEntry: QuestionEntry.QuestionEntry,
		senderAddr: Tuple[str, int],
		recDepthStack: List[ Tuple[ int, str ] ],
	) -> List[ MsgEntry.MsgEntry ]:
		newRecStack = self.CheckRecursionDepth(
			recDepthStack,
			self.HandleQuestion
		)

		if self._MatchQuestion(msgEntry):
			try:
				resp = self.qtHandler.HandleQuestion(
					msgEntry,
					senderAddr,
					newRecStack,
				)

				self.QtAnsLogger.info(
					f'Question, {msgEntry}, received answer, {resp}'
				)

				return resp
			except Exception as e:
				self.QtAnsLogger.exception(
					f'Question, {msgEntry}, got exception, {e}'
				)
				raise

	def Terminate(self) -> None:
		self.qtHandler.Terminate()

