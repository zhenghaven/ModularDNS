#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import re

from typing import Tuple

from ...MsgEntry import QuestionEntry


class Rule(object):
	def __init__(self) -> None:
		super(Rule, self).__init__()

	def Match(self, question: QuestionEntry.QuestionEntry) -> Tuple[bool, int]:
		'''
		# Match
		Match the question with this rule.

		## Parameters
		- `question`: The question to be matched.

		## Returns
		- bool: Whether the question matches this rule.
		- int: The weight of this matching.
		'''
		raise NotImplementedError(
			f'{self.__class__.__name__}.Match() is not implemented'
		)

	def __hash__(self) -> int:
		raise NotImplementedError(
			f'{self.__class__.__name__}.__hash__() is not implemented'
		)

	def __eq__(self, other: object) -> bool:
		raise NotImplementedError(
			f'{self.__class__.__name__}.__eq__() is not implemented'
		)


class ConfigurableWeightRule(Rule):

	RULE_TYPE_LABEL = None

	def __init__(
		self,
		defaultWeight: int,
		ruleStr: str,
		noSepAsWeight: bool = False,
	) -> None:
		super(ConfigurableWeightRule, self).__init__()

		if ruleStr == '':
			self._weight = defaultWeight
			self._ruleBody = ''
		else:
			cmps = ruleStr.split(':~>>', maxsplit=1)
			if len(cmps) == 1:
				if noSepAsWeight:
					self._weight = int(cmps[0])
					self._ruleBody = ''
				else:
					self._weight = defaultWeight
					self._ruleBody = cmps[0]
			elif len(cmps) == 2:
				self._weight = int(cmps[0])
				self._ruleBody = cmps[1]
			else:
				raise ValueError(f'Invalid rule format: {ruleStr}')

	def __hash__(self) -> int:
		return hash((self.RULE_TYPE_LABEL, self._weight, self._ruleBody))

	def __eq__(self, other: object) -> bool:
		if not isinstance(other, ConfigurableWeightRule):
			return False
		else:
			return (
				(self.RULE_TYPE_LABEL == other.RULE_TYPE_LABEL) and
				(self._weight == other._weight) and
				(self._ruleBody == other._ruleBody)
			)

	def __str__(self) -> str:
		return f'{self.RULE_TYPE_LABEL}:->>{self._weight}:~>>{self._ruleBody}'


class SubDomainRule(ConfigurableWeightRule):

	RULE_TYPE_LABEL = 'sub'
	DEFAULT_WEIGHT = 50

	def __init__(self, ruleStr: str) -> None:
		super(SubDomainRule, self).__init__(self.DEFAULT_WEIGHT, ruleStr)

	def Match(self, question: QuestionEntry.QuestionEntry) -> Tuple[bool, int]:
		if question.GetNameStr(omitFinalDot=True).endswith(self._ruleBody):
			return (True, self._weight)
		else:
			return (False, self._weight)


class FullMatchRule(ConfigurableWeightRule):

	RULE_TYPE_LABEL = 'full'
	DEFAULT_WEIGHT = 90

	def __init__(self, ruleStr: str) -> None:
		super(FullMatchRule, self).__init__(self.DEFAULT_WEIGHT, ruleStr)

	def Match(self, question: QuestionEntry.QuestionEntry) -> Tuple[bool, int]:
		if question.GetNameStr(omitFinalDot=True) == self._ruleBody:
			return (True, self._weight)
		else:
			return (False, self._weight)


class DefaultRule(ConfigurableWeightRule):

	RULE_TYPE_LABEL = 'default'
	DEFAULT_WEIGHT = 10

	def __init__(self, ruleStr: str) -> None:
		super(DefaultRule, self).__init__(
			self.DEFAULT_WEIGHT,
			ruleStr,
			noSepAsWeight=True,
		)

	def Match(self, question: QuestionEntry.QuestionEntry) -> Tuple[bool, int]:
		return (True, self._weight)


RULE_TYPE_MAP = {
	DefaultRule.RULE_TYPE_LABEL:        DefaultRule,
	SubDomainRule.RULE_TYPE_LABEL:      SubDomainRule,
	FullMatchRule.RULE_TYPE_LABEL:      FullMatchRule,
	# 'regex':    RegexRule, # plan for future support
}


_ROOT_RULE_FORMAT = r'^([a-zA-Z][a-zA-Z0-9]+)(?:\:\-\>\>(.+))?$'
_ROOT_RULE_RE = re.compile(_ROOT_RULE_FORMAT)


def _ParseRuleStr(ruleStr: str) -> Tuple[str, str]:
	m = _ROOT_RULE_RE.match(ruleStr)
	if m is None:
		raise ValueError(f'Invalid rule format: {ruleStr}')
	else:
		ruleType = m.group(1)
		ruleBody = m.group(2) if m.group(2) is not None else ''

		return (ruleType, ruleBody)


def RuleFromStr(ruleStr: str) -> Rule:
	'''
	# RuleFromStr
	Parse a rule from a string.

	## Parameters
	- `ruleStr`: The string to be parsed.

	## Returns
	- Rule: The rule parsed.
	'''
	ruleType, ruleBody = _ParseRuleStr(ruleStr)

	if ruleType not in RULE_TYPE_MAP:
		raise ValueError(f'Invalid rule type: {ruleType} given in {ruleStr}')

	return RULE_TYPE_MAP[ruleType](ruleBody)

