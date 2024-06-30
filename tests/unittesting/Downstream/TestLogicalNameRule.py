#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Copyright (c) 2024 Haofan Zheng
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.
###


import unittest

import dns.name
import dns.rdataclass
import dns.rdatatype

from ModularDNS.Downstream.Logical import QuestionRule
from ModularDNS.MsgEntry.QuestionEntry import QuestionEntry


class TestLogicalNameRule(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_1ParseRootRule(self):
		ruleType, ruleBody = QuestionRule._ParseRuleStr('sub:->>google.com')
		self.assertEqual(ruleType, 'sub')
		self.assertEqual(ruleBody, 'google.com')

		ruleType, ruleBody = QuestionRule._ParseRuleStr('full:->>dns.google.com')
		self.assertEqual(ruleType, 'full')
		self.assertEqual(ruleBody, 'dns.google.com')

		ruleType, ruleBody = QuestionRule._ParseRuleStr('sub2:->>:->>google.com')
		self.assertEqual(ruleType, 'sub2')
		self.assertEqual(ruleBody, ':->>google.com')

		ruleType, ruleBody = QuestionRule._ParseRuleStr('sub123:->>50:~>>google.com')
		self.assertEqual(ruleType, 'sub123')
		self.assertEqual(ruleBody, '50:~>>google.com')

		ruleType, ruleBody = QuestionRule._ParseRuleStr('sub:->>nfeuwiwY$%$@FG24g90h1fc.;]')
		self.assertEqual(ruleType, 'sub')
		self.assertEqual(ruleBody, 'nfeuwiwY$%$@FG24g90h1fc.;]')

		# invalid separator
		with self.assertRaises(ValueError):
			QuestionRule._ParseRuleStr('sub:->google.com')
		with self.assertRaises(ValueError):
			QuestionRule._ParseRuleStr('sub>>google.com')
		with self.assertRaises(ValueError):
			QuestionRule._ParseRuleStr('sub>google.com')

		# missing rule body
		with self.assertRaises(ValueError):
			QuestionRule._ParseRuleStr('sub:->>')
		with self.assertRaises(ValueError):
			QuestionRule._ParseRuleStr('sub')

		# missing rule type
		with self.assertRaises(ValueError):
			QuestionRule._ParseRuleStr(':->>google.com')
		with self.assertRaises(ValueError):
			QuestionRule._ParseRuleStr('google.com')

		# invalid characters in rule type
		with self.assertRaises(ValueError):
			QuestionRule._ParseRuleStr('2sub:->>google.com')
		with self.assertRaises(ValueError):
			QuestionRule._ParseRuleStr('su&b:->>google.com')

	def test_2ParseConfigurableWeightRule(self):
		rule = QuestionRule.ConfigurableWeightRule(12, '50:~>>dns.google.com')
		self.assertEqual(rule._weight, 50)
		self.assertEqual(type(rule._weight), int)
		self.assertEqual(rule._ruleBody, 'dns.google.com')

		rule = QuestionRule.ConfigurableWeightRule(12, '50:~>>50:~>>dns.google.com')
		self.assertEqual(rule._weight, 50)
		self.assertEqual(type(rule._weight), int)
		self.assertEqual(rule._ruleBody, '50:~>>dns.google.com')

		rule = QuestionRule.ConfigurableWeightRule(12, '05:~>>dns.google.com')
		self.assertEqual(rule._weight, 5)
		self.assertEqual(type(rule._weight), int)
		self.assertEqual(rule._ruleBody, 'dns.google.com')

		# optional weight
		rule = QuestionRule.ConfigurableWeightRule(12, 'google.com')
		self.assertEqual(rule._weight, 12)
		self.assertEqual(type(rule._weight), int)
		self.assertEqual(rule._ruleBody, 'google.com')

		# no separator, but we accept it
		rule = QuestionRule.ConfigurableWeightRule(12, '')
		self.assertEqual(rule._weight, 12)
		self.assertEqual(type(rule._weight), int)
		self.assertEqual(rule._ruleBody, '')
		rule = QuestionRule.ConfigurableWeightRule(12, ':~>')
		self.assertEqual(rule._weight, 12)
		self.assertEqual(type(rule._weight), int)
		self.assertEqual(rule._ruleBody, ':~>')

		# invalid characters in weight
		with self.assertRaises(ValueError):
			QuestionRule.ConfigurableWeightRule(12, ':~>>dns.google.com')
		with self.assertRaises(ValueError):
			QuestionRule.ConfigurableWeightRule(12, ':~>>')
		with self.assertRaises(ValueError):
			QuestionRule.ConfigurableWeightRule(12, '50a:~>>dns.google.com')

	def test_3SubDomainRuleMatch(self):
		rule: QuestionRule.SubDomainRule = QuestionRule.RuleFromStr('sub:->>23:~>>google.com')
		self.assertEqual(rule._weight, 23)
		self.assertEqual(rule._ruleBody, 'google.com')

		# match
		q = QuestionEntry(
			name=dns.name.from_text('dns.google.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
		)
		isMatch, weight = rule.Match(q)
		self.assertTrue(isMatch)
		self.assertEqual(weight, 23)
		q = QuestionEntry(
			name=dns.name.from_text('a.google.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
		)
		isMatch, weight = rule.Match(q)
		self.assertTrue(isMatch)
		self.assertEqual(weight, 23)
		q = QuestionEntry(
			name=dns.name.from_text('google.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
		)
		isMatch, weight = rule.Match(q)
		self.assertTrue(isMatch)
		self.assertEqual(weight, 23)

		# should not match
		q = QuestionEntry(
			name=dns.name.from_text('google.com.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
		)
		isMatch, weight = rule.Match(q)
		self.assertFalse(isMatch)
		self.assertEqual(weight, 23)
		q = QuestionEntry(
			name=dns.name.from_text('dns.google.com.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
		)
		isMatch, weight = rule.Match(q)
		self.assertFalse(isMatch)
		self.assertEqual(weight, 23)
		q = QuestionEntry(
			name=dns.name.from_text('microsoft.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
		)
		isMatch, weight = rule.Match(q)
		self.assertFalse(isMatch)
		self.assertEqual(weight, 23)

	def test_4FullMatchRuleMatch(self):
		rule: QuestionRule.FullMatchRule = QuestionRule.RuleFromStr('full:->>23:~>>google.com')
		self.assertEqual(rule._weight, 23)
		self.assertEqual(rule._ruleBody, 'google.com')

		# match
		q = QuestionEntry(
			name=dns.name.from_text('google.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
		)
		isMatch, weight = rule.Match(q)
		self.assertTrue(isMatch)
		self.assertEqual(weight, 23)

		# should not match
		q = QuestionEntry(
			name=dns.name.from_text('google.com.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
		)
		isMatch, weight = rule.Match(q)
		self.assertFalse(isMatch)
		self.assertEqual(weight, 23)
		q = QuestionEntry(
			name=dns.name.from_text('dns.google.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
		)
		isMatch, weight = rule.Match(q)
		self.assertFalse(isMatch)
		self.assertEqual(weight, 23)
		q = QuestionEntry(
			name=dns.name.from_text('microsoft.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
		)
		isMatch, weight = rule.Match(q)
		self.assertFalse(isMatch)
		self.assertEqual(weight, 23)

