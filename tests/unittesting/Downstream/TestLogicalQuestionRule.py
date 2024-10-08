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


class TestLogicalQuestionRule(unittest.TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_Downstream_Logical_QuestionRule_1ParseRootRule(self):
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
		# it is valid to only have the rule type
		# with self.assertRaises(ValueError):
		# 	QuestionRule._ParseRuleStr('sub')

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

	def test_Downstream_Logical_QuestionRule_2ParseConfigurableWeightRule(self):
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

	def test_Downstream_Logical_QuestionRule_3SubDomainRuleMatch(self):
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

	def test_Downstream_Logical_QuestionRule_4FullMatchRuleMatch(self):
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

	def test_Downstream_Logical_QuestionRule_5DefaultRuleMatch(self):
		rule: QuestionRule.DefaultRule = QuestionRule.RuleFromStr('default')
		self.assertEqual(rule._weight, QuestionRule.DefaultRule.DEFAULT_WEIGHT)
		self.assertEqual(rule._ruleBody, '')

		# match
		q = QuestionEntry(
			name=dns.name.from_text('google.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
		)
		isMatch, weight = rule.Match(q)
		self.assertTrue(isMatch)
		self.assertEqual(weight, QuestionRule.DefaultRule.DEFAULT_WEIGHT)

		# match
		q = QuestionEntry(
			name=dns.name.from_text('microsoft.com'),
			rdCls=dns.rdataclass.IN,
			rdType=dns.rdatatype.A,
		)
		isMatch, weight = rule.Match(q)
		self.assertTrue(isMatch)
		self.assertEqual(weight, QuestionRule.DefaultRule.DEFAULT_WEIGHT)

	def test_Downstream_Logical_QuestionRule_6SubDomainRuleHashable(self):
		rule1: QuestionRule.SubDomainRule = QuestionRule.RuleFromStr('sub:->>23:~>>google.com')
		self.assertEqual(rule1.RULE_TYPE_LABEL, 'sub')
		self.assertEqual(rule1._weight, 23)
		self.assertEqual(rule1._ruleBody, 'google.com')
		self.assertEqual(str(rule1), 'sub:->>23:~>>google.com')

		rule2: QuestionRule.SubDomainRule = QuestionRule.RuleFromStr('sub:->>0023:~>>google.com')
		self.assertEqual(rule2.RULE_TYPE_LABEL, 'sub')
		self.assertEqual(rule2._weight, 23)
		self.assertEqual(rule2._ruleBody, 'google.com')
		self.assertEqual(str(rule2), 'sub:->>23:~>>google.com')

		self.assertEqual(rule1, rule2)
		self.assertEqual(hash(rule1), hash(rule2))

		rule3: QuestionRule.SubDomainRule = QuestionRule.RuleFromStr('sub:->>67:~>>google.com')
		self.assertEqual(rule3.RULE_TYPE_LABEL, 'sub')
		self.assertEqual(rule3._weight, 67)
		self.assertEqual(rule3._ruleBody, 'google.com')
		self.assertEqual(str(rule3), 'sub:->>67:~>>google.com')

		self.assertNotEqual(rule1, rule3)
		self.assertNotEqual(hash(rule1), hash(rule3))

		rule4: QuestionRule.SubDomainRule = QuestionRule.RuleFromStr('sub:->>23:~>>a.google.com')
		self.assertEqual(rule4.RULE_TYPE_LABEL, 'sub')
		self.assertEqual(rule4._weight, 23)
		self.assertEqual(rule4._ruleBody, 'a.google.com')
		self.assertEqual(str(rule4), 'sub:->>23:~>>a.google.com')

		self.assertNotEqual(rule1, rule4)
		self.assertNotEqual(hash(rule1), hash(rule4))

		rule5: QuestionRule.SubDomainRule = QuestionRule.RuleFromStr('sub:->>google.com')
		self.assertEqual(rule5.RULE_TYPE_LABEL, 'sub')
		self.assertEqual(rule5._weight, QuestionRule.SubDomainRule.DEFAULT_WEIGHT)
		self.assertEqual(rule5._ruleBody, 'google.com')
		self.assertEqual(str(rule5), 'sub:->>50:~>>google.com')

		self.assertNotEqual(rule1, rule5)
		self.assertNotEqual(hash(rule1), hash(rule5))

	def test_Downstream_Logical_QuestionRule_7FullMatchRuleHashable(self):
		rule1: QuestionRule.FullMatchRule = QuestionRule.RuleFromStr('full:->>23:~>>google.com')
		self.assertEqual(rule1.RULE_TYPE_LABEL, 'full')
		self.assertEqual(rule1._weight, 23)
		self.assertEqual(rule1._ruleBody, 'google.com')
		self.assertEqual(str(rule1), 'full:->>23:~>>google.com')

		rule2: QuestionRule.FullMatchRule = QuestionRule.RuleFromStr('full:->>0023:~>>google.com')
		self.assertEqual(rule2.RULE_TYPE_LABEL, 'full')
		self.assertEqual(rule2._weight, 23)
		self.assertEqual(rule2._ruleBody, 'google.com')
		self.assertEqual(str(rule2), 'full:->>23:~>>google.com')

		self.assertEqual(rule1, rule2)
		self.assertEqual(hash(rule1), hash(rule2))

		rule3: QuestionRule.FullMatchRule = QuestionRule.RuleFromStr('full:->>67:~>>google.com')
		self.assertEqual(rule3.RULE_TYPE_LABEL, 'full')
		self.assertEqual(rule3._weight, 67)
		self.assertEqual(rule3._ruleBody, 'google.com')
		self.assertEqual(str(rule3), 'full:->>67:~>>google.com')

		self.assertNotEqual(rule1, rule3)
		self.assertNotEqual(hash(rule1), hash(rule3))

		rule4: QuestionRule.FullMatchRule = QuestionRule.RuleFromStr('full:->>23:~>>a.google.com')
		self.assertEqual(rule4.RULE_TYPE_LABEL, 'full')
		self.assertEqual(rule4._weight, 23)
		self.assertEqual(rule4._ruleBody, 'a.google.com')
		self.assertEqual(str(rule4), 'full:->>23:~>>a.google.com')

		self.assertNotEqual(rule1, rule4)
		self.assertNotEqual(hash(rule1), hash(rule4))

		rule5: QuestionRule.FullMatchRule = QuestionRule.RuleFromStr('full:->>google.com')
		self.assertEqual(rule5.RULE_TYPE_LABEL, 'full')
		self.assertEqual(rule5._weight, QuestionRule.FullMatchRule.DEFAULT_WEIGHT)
		self.assertEqual(rule5._ruleBody, 'google.com')
		self.assertEqual(str(rule5), 'full:->>90:~>>google.com')

		self.assertNotEqual(rule1, rule5)
		self.assertNotEqual(hash(rule1), hash(rule5))

	def test_Downstream_Logical_QuestionRule_8DefaultRuleHashable(self):
		rule1: QuestionRule.DefaultRule = QuestionRule.RuleFromStr('default')
		self.assertEqual(rule1.RULE_TYPE_LABEL, 'default')
		self.assertEqual(rule1._weight, QuestionRule.DefaultRule.DEFAULT_WEIGHT)
		self.assertEqual(rule1._ruleBody, '')
		self.assertEqual(str(rule1), 'default:->>10:~>>')

		rule2: QuestionRule.DefaultRule = QuestionRule.RuleFromStr('default:->>0010')
		self.assertEqual(rule2.RULE_TYPE_LABEL, 'default')
		self.assertEqual(rule2._weight, 10)
		self.assertEqual(rule2._ruleBody, '')
		self.assertEqual(str(rule2), 'default:->>10:~>>')

		self.assertEqual(rule1, rule2)
		self.assertEqual(hash(rule1), hash(rule2))

		rule3: QuestionRule.DefaultRule = QuestionRule.RuleFromStr('default:->>10:~>>')
		self.assertEqual(rule3.RULE_TYPE_LABEL, 'default')
		self.assertEqual(rule3._weight, 10)
		self.assertEqual(rule3._ruleBody, '')
		self.assertEqual(str(rule3), 'default:->>10:~>>')

		self.assertEqual(rule1, rule3)
		self.assertEqual(hash(rule1), hash(rule3))

		rule4: QuestionRule.DefaultRule = QuestionRule.RuleFromStr('default:->>0')
		self.assertEqual(rule4.RULE_TYPE_LABEL, 'default')
		self.assertEqual(rule4._weight, 0)
		self.assertEqual(rule4._ruleBody, '')
		self.assertEqual(str(rule4), 'default:->>0:~>>')

		self.assertNotEqual(rule1, rule4)
		self.assertNotEqual(hash(rule1), hash(rule4))

		rule5: QuestionRule.DefaultRule = QuestionRule.RuleFromStr('default:->>56')
		self.assertEqual(rule5.RULE_TYPE_LABEL, 'default')
		self.assertEqual(rule5._weight, 56)
		self.assertEqual(rule5._ruleBody, '')
		self.assertEqual(str(rule5), 'default:->>56:~>>')

		self.assertNotEqual(rule1, rule5)
		self.assertNotEqual(hash(rule1), hash(rule5))

		# full rule is not equal to default rule
		rule6: QuestionRule.FullMatchRule = QuestionRule.RuleFromStr('full:->>10:~>>google.com')
		self.assertEqual(rule6.RULE_TYPE_LABEL, 'full')
		self.assertEqual(rule6._weight, 10)
		self.assertEqual(rule6._ruleBody, 'google.com')
		self.assertEqual(str(rule6), 'full:->>10:~>>google.com')

		self.assertNotEqual(rule1, rule6)
		self.assertNotEqual(hash(rule1), hash(rule6))

	def test_Downstream_Logical_QuestionRule_9RuleHashable(self):
		rule1: QuestionRule.SubDomainRule = QuestionRule.RuleFromStr('sub:->>23:~>>google.com')
		self.assertEqual(rule1.RULE_TYPE_LABEL, 'sub')
		self.assertEqual(rule1._weight, 23)
		self.assertEqual(rule1._ruleBody, 'google.com')

		rule2: QuestionRule.FullMatchRule = QuestionRule.RuleFromStr('full:->>23:~>>google.com')
		self.assertEqual(rule2.RULE_TYPE_LABEL, 'full')
		self.assertEqual(rule2._weight, 23)
		self.assertEqual(rule2._ruleBody, 'google.com')

		self.assertNotEqual(rule1, rule2)
		self.assertNotEqual(hash(rule1), hash(rule2))

