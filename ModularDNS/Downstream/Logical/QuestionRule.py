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


class ConfigurableWeightRule(Rule):
	def __init__(self, defaultWeight: int, ruleStr: str) -> None:
		super(ConfigurableWeightRule, self).__init__()

		cmps = ruleStr.split(':~>>', maxsplit=1)
		if len(cmps) == 1:
			self._weight = defaultWeight
			self._ruleBody = cmps[0]
		elif len(cmps) == 2:
			self._weight = int(cmps[0])
			self._ruleBody = cmps[1]
		else:
			raise ValueError(f'Invalid rule format: {ruleStr}')


class SubDomainRule(ConfigurableWeightRule):

	DEFAULT_WEIGHT = 50

	def __init__(self, ruleStr: str) -> None:
		super(SubDomainRule, self).__init__(self.DEFAULT_WEIGHT, ruleStr)

	def Match(self, question: QuestionEntry.QuestionEntry) -> Tuple[bool, int]:
		if question.GetNameStr(omitFinalDot=True).endswith(self._ruleBody):
			return (True, self._weight)
		else:
			return (False, self._weight)


class FullMatchRule(ConfigurableWeightRule):

	DEFAULT_WEIGHT = 90

	def __init__(self, ruleStr: str) -> None:
		super(FullMatchRule, self).__init__(self.DEFAULT_WEIGHT, ruleStr)

	def Match(self, question: QuestionEntry.QuestionEntry) -> Tuple[bool, int]:
		if question.GetNameStr(omitFinalDot=True) == self._ruleBody:
			return (True, self._weight)
		else:
			return (False, self._weight)


RULE_TYPE_MAP = {
	'sub':      SubDomainRule,
	'full':     FullMatchRule,
	# 'regex':    RegexRule, # plan for future support
}


def _ParseRuleStr(ruleStr: str) -> Tuple[str, str]:
	RULE_FORMAT = r'^([a-zA-Z][a-zA-Z0-9]+)\:\-\>\>(.+)$'

	r = re.compile(RULE_FORMAT)
	m = r.match(ruleStr)
	if m is None:
		raise ValueError(f'Invalid rule format: {ruleStr}')
	else:
		ruleType = m.group(1)
		ruleBody = m.group(2)

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

