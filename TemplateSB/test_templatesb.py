"""
Tests for TemplateSB.
1. Handle badly form code better
2. Test for case of no definitions
"""
from templatesb import TemplateSB, Substituter,  \
    LINE_TRAN, LINE_SUBS, ESCAPE_START, ESCAPE_END

import copy
import unittest
import numpy as np


IGNORE_TEST = True
DEFINITIONS = {'a': ['a', 'b', 'c'], 'm': ['1', '2', '3'],
    'c': ['c', '']}
SUBSTITUTION1 = "J1: S1 -> S2; k1*S1"
SUBSTITUTION2 = "J{a}1: S{a}1 -> S{a}2; k1*S{a}1"
SUBSTITUTION3 = "J{c}1: S{c}1 -> S{c}2; k1*S{c}1"
TEMPLATE_INITIAL = '''%s
DEFINITIONS = %s
[api.addDefinition(k,v) for k,v in DEFINITIONS.items()]'''  \
    % (ESCAPE_START, str(DEFINITIONS))
TEMPLATE_EXECUTE = '''%s
%s''' % (TEMPLATE_INITIAL, ESCAPE_END)
TEMPLATE_STG1 = '''
%s
%s
%s
''' % (TEMPLATE_INITIAL, SUBSTITUTION1, ESCAPE_END)
TEMPLATE_STG2 = '''
%s
%s
%s
''' % (TEMPLATE_INITIAL, SUBSTITUTION2, ESCAPE_END)
TEMPLATE_STG2 = '''
%s
%s
%s
''' % (TEMPLATE_INITIAL, SUBSTITUTION3, ESCAPE_END)
# Substitution
# Definition error
TEMPLATE_BAD = '''
{{
DEFINITIONS = {'a': ['a', 'b', 'c'], 'm': ['1', '2', '3'],
    'c': ['c', '']}
[api.addDefinition(k,v) for k,v in DEFINITIONS]
J{z}1: S{z}1 -> S{d}2; k1*S{d}1
}}
'''


def isSubDict(dict_super, dict_sub):
  """
  Tests if the second dictonary is a subset of the first.
  :param dict dict_super:
  :param dict dict_sub:
  :return bool:
  """
  for key in dict_sub.keys():
    if not key in dict_super:
      return False
    if not dict_sub[key] == dict_super[key]:
      return False
  return True


#############################
# Tests
#############################
# pylint: disable=W0212,C0111,R0904
class TestSubtituter(unittest.TestCase):

  def setUp(self):
    self.substituter = Substituter(DEFINITIONS)

  def testMakeSubtitutionList(self):
    if IGNORE_TEST:
      return
    substitution_list = Substituter.makeSubstitutionList(DEFINITIONS)
    expected = np.prod([len(v) for v in DEFINITIONS.values()])
    self.assertEqual(len(substitution_list), expected)
    substitution_list = Substituter.makeSubstitutionList({})
    self.assertEqual(len(substitution_list), 0)
    definitions = dict(DEFINITIONS)
    key = DEFINITIONS.keys()[0]
    del definitions[key]
    substitution_list = Substituter.makeSubstitutionList(definitions)
    expected = np.prod([len(v) for v in definitions.values()])
    self.assertEqual(len(substitution_list), expected)

  def testGetTemplateVariables(self):
    if IGNORE_TEST:
      return
    variables = self.substituter._getTemplateVariables("x{a} -> x + {a}; k*{a}")
    self.assertEqual(variables,["{a}"])
    variables = self.substituter._getTemplateVariables("x{a} -> x + {b}; k*{a}")
    self.assertEqual(variables, ["{a}", "{b}"])
    variables = self.substituter._getTemplateVariables("x{a} -> x + { b }; k*{a}")
    self.assertEqual(variables, ["{a}", "{b}"])
    variables = self.substituter._getTemplateVariables("x{a} -> x + { 1, 2,3 }; k*{a}")
    self.assertEqual(set(variables), set(["{a}", "{1,2,3}"]))
    
  def testReplace(self):
    if IGNORE_TEST:
      return
    substituter = Substituter(DEFINITIONS)
    result = substituter.replace(SUBSTITUTION1)
    self.assertEqual(result[0], SUBSTITUTION1)
    result = substituter.replace(SUBSTITUTION2)
    expected = len(DEFINITIONS['a'])
    self.assertEqual(len(result), expected)
    

#############################
# Tests
#############################
# pylint: disable=W0212,C0111,R0904
class TestTemplateSB(unittest.TestCase):

  def setUp(self):
    self.templatesb = TemplateSB(TEMPLATE_STG2)

  def testConstructor(self):
    if IGNORE_TEST:
      return
    self.assertTrue(len(self.templatesb._lines) > 0)

  def testClassifyLine(self):
    if IGNORE_TEST:
      return
    self.templatesb._current_line = SUBSTITUTION1
    self.assertEqual(self.templatesb._classifyLine(), LINE_TRAN)
    self.templatesb._current_line = DEFINITIONS_LINE
    self.assertEqual(self.templatesb._classifyLine(), LINE_DEFN)
    self.templatesb._current_line = SUBSTITUTION2
    self.assertEqual(self.templatesb._classifyLine(), LINE_SUBS)

  def testErrorMsg(self):
    if IGNORE_TEST:
      return
    with self.assertRaises(ValueError):
      self.templatesb._errorMsg("")

  def testGetNextLine(self):
    if IGNORE_TEST:
      return
    templatesb = TemplateSB(TEMPLATE_STG2)
    line = templatesb._getNextLine()
    lines = []
    idx = 0
    expecteds = TEMPLATE_STG2.split('\n')
    while line is not None:
      expected = expecteds[idx]
      idx += 1
      lines.append(line)
      self.assertEqual(line, expected)
      line = templatesb._getNextLine()
    expected = len(expecteds)
    self.assertEqual(expected, len(lines))

  def testGetNextLineContinuation(self):
    if IGNORE_TEST:
      return
    stg = '''this \
    is a \
    continuation.'''
    templatesb = TemplateSB(stg)
    line = templatesb._getNextLine()
    self.assertTrue("is a" in line)
    self.assertTrue("continuation" in line)
    line = templatesb._getNextLine()
    self.assertIsNone(line)

  def testExecuteStatements(self):
    #if IGNORE_TEST:
    #  return
    template = TemplateSB(TEMPLATE_EXECUTE)
    self.assertEqual(len(template._definitions.keys()), 0)
    result = template.expand()
    self.assertEqual(result.count('\n'), TEMPLATE_EXECUTE.count('\n'))
    import pdb; pdb.set_trace()

  def testExpand(self):
    if IGNORE_TEST:
      return
    lines = self.templatesb.expand()
    for val in DEFINITIONS['{a}']:
      self.assertTrue("J%s1:" % val in lines)

  def testExpandWithAndWIthoutDefinition(self):
    if IGNORE_TEST:
      return
    definitions = {'{a}': ['a', 'b', 'c'], '{m}': ['1', '2', '3'],
        '{c}': ['c', '']}
    definition_line = "%s %s Version 1.0 %s" %  \
        (ESCAPE_STG, PROCESSOR_NAME, str(definitions))
    template_reaction = "J{c}1: S{c}1 -> S{c}2; k1*S{c}1"
    template_lines = '''%s
    %s''' % (definition_line, template_reaction)
    templatesb1 = TemplateSB(template_lines)
    result1 = templatesb1.expand()
    templatesb2 = TemplateSB(template_reaction)
    result2 = templatesb2.expand()
    self.assertTrue(result1.index(result2) > 0)

  def testExpandErrorInDefinition(self):
    if IGNORE_TEST:
      return
    for template in [BAD_TEMPLATE1]:
      with self.assertRaises(ValueError):
        templatesb = TemplateSB(template)
        result = templatesb.expand()

  def testCase1(self):
    if IGNORE_TEST:
      return
    template_reaction = '''
    J{x,y,z}: S3{x,y,z} -> S4{x,y,z}; k2{x,y,z}*S3{x,y,z}
    '''
    templatesb = TemplateSB(template_reaction)
    result = templatesb.expand()

  def testFile(self):
    if IGNORE_TEST:
      return
    TemplateSB.processFile("../Example/sample.tmpl", "/tmp/out.mdl")


if __name__ == '__main__':
  unittest.main()
