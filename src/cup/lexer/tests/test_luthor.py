import unittest
from cup.lexer.luthor import LexLuthor, CodeSegment, LuthorFile, LuthorREPattern
from cup.lexer.metatoken import (StringToken, IntToken, CodeToken, ClassToken,
                                 NameToken, SectionToken, EqToken)

p1 = r'''
{%
    tokens_matched = 0
%}

int_pattern "\d+"
{-
    RESULT = IntToken(MATCHED)
    tokens_matched += 1
-}
'''

p2 = r'''
{% 
    # GLOBAL CONFIGURATION 
    tokens_matched  = 0    # A normal python variable
%}

int_pattern "\d+"
{- 
    RESULT = IntToken(MATCHED) 
    tokens_matched += 1
-}

str_pattern "([\"]|[^\"])+"
{-
    RESULT = StrToken(MATCHED)
    tokens_matched += 1
-}

ws_pattern "\s"

{%  
    # Program Suffix
    print( "Total tokens matched: {}".format(tokens_matched))
%}
'''

goodcode1 = '''x = 1
y = 2
if x == 1:
    y = 3
'''

goodcode2 = '''
for i in range(10):
    for j in range(10);
        print (i,j)
for i in range(10):
    for j in range(10):
        print (j,i)
'''

goodcode3 = '''
x = 2
if x == 2:
    print(x)
    y = x ** 3
    if y < 100:
        x = 1
        if x == 2 or y < 11:
            print ("Hello world!!!")
    for i in range(100):
        print("This is a test")
        for j in range(100):
            pass
        pass
else:
    print("Nope!")

'''

goodcode4 = '''

x = 1
y = 0
for i in range(100):
    x += i

    if x % 3 == 0:
        y += 1

for i in range(100):
    



    x += i
    if x % 2 == 0:
      y += 2
      if y > i:
                                print("This is an indentation test")
      print("Success!")
'''

badcode1 = '''if True:
    if True:
        print("True")
      print("This should fail!!!")
    else:
        print("This should never be reached!")
'''

class TestLuthor(unittest.TestCase):
    def test_constructor(self):
        luthor = LexLuthor(p1)
        self.assertEqual(luthor._program, p1)

    def test_token_length_1(self):
        luthor = LexLuthor(p1)
        expect = [SectionToken, NameToken, StringToken, CodeToken]
        actual = list(iter(luthor))
        self.assertEqual(len(expect), len(actual))

    def test_token_length_2(self):
        luthor = LexLuthor(p2)
        expect = [SectionToken, NameToken, StringToken, CodeToken, 
                                NameToken, StringToken, CodeToken,
                                NameToken, StringToken, CodeToken]
        actual = list(iter(luthor))
        self.assertEqual(len(expect), len(actual))

    def test_token_types_1(self):
        luthor = LexLuthor(p1)
        expect = [SectionToken, NameToken, StringToken, CodeToken]
        actual = list(iter(luthor))
        for e, a in zip(expect, actual):
            self.assertTrue(isinstance(a,e))

    def test_token_types_2(self):
        luthor = LexLuthor(p2)
        actual = list(iter(luthor))
        expect = [SectionToken, NameToken, StringToken, CodeToken, 
                                NameToken, StringToken, CodeToken,
                                NameToken, StringToken, SectionToken]
        for a,e in zip(actual, expect):
            self.assertTrue(isinstance(a,e), '{} is not an instance of {}'.format(a, e))

    def test_code_segment_indentation_1(self):
        cs = CodeSegment(goodcode1)
        actuals  = cs._indents
        expected = [0,0,0,1]
        for a,e in zip(actuals, expected):
            self.assertEqual(a, e)

    def test_code_segment_indentation_2(self):
        cs = CodeSegment(goodcode2)
        actuals  = cs._indents
        expected = [0,1,2,0,1,2]
        for a,e in zip(actuals, expected):
            self.assertEqual(a, e)

    def test_code_segment_indentation_3(self):
        cs = CodeSegment(goodcode3)
        actuals  = cs._indents
        expected = [0,0,1,1,1,2,2,3,1,2,2,3,2,0,1]
        for a,e in zip(actuals, expected):
            self.assertEqual(a, e)

    
    def test_code_segment_indentation_4(self):
        cs = CodeSegment(goodcode4)
        actuals  = cs._indents
        expected = [0,0,0, 1, 1, 2, 0, 1, 1, 2, 2, 3, 2]
        for a,e in zip(actuals, expected):
            self.assertEqual(a, e)

    def test_code_segment_indentation_5(self):
        def make_codeseg():
            return CodeSegment(badcode1)
        self.assertRaises(RuntimeError, make_codeseg)

    def test_luthorFile1_setup(self):
        lfile = LuthorFile(p1)
        lfile.parse()

        expected_setup = CodeSegment('''tokens_matched = 0''')
        actual_setup   = lfile.setup

        self.assertEqual(actual_setup, expected_setup)

    def test_luthorFile1_teardown(self):
        lfile = LuthorFile(p1)
        lfile.parse()

        expected_teardown = CodeSegment('')
        actual_teardown   = lfile.teardown

        self.assertEqual(actual_teardown, expected_teardown)


    def test_luthorFile1_patterns1(self):
        lfile = LuthorFile(p1)
        lfile.parse()

        expected_patterns = [LuthorREPattern('int_pattern', r'''\d+''',
        CodeSegment(''' 
        RESULT = IntToken(MATCHED)
        tokens_matched += 1'''))]
        actual_patterns   = lfile.patterns

        self.assertEqual(len(actual_patterns), len(expected_patterns))

    def test_luthorFile1_patterns2(self):
        lfile = LuthorFile(p1)
        lfile.parse()

        expected_patterns = [LuthorREPattern('int_pattern', r'''\d+''',
        CodeSegment(''' 
        RESULT = IntToken(MATCHED)
        tokens_matched += 1'''))]
        actual_patterns   = lfile.patterns

        for exp, act in zip(expected_patterns, actual_patterns):
            self.assertEqual(act, exp, 
"""
'{}' == '{}': {}, 
'{}' == '{}': {},
'{}' == '{}': {}""".format( act.name, exp.name, act.name == exp.name, 
                        act.pattern, exp.pattern, act.pattern == exp.pattern, 
                        act.code, exp.code, act.code == exp.code))

    def test_luthorFile2_setup(self):
        lfile = LuthorFile(p2)
        lfile.parse()

        expected_setup = CodeSegment('''
            # GLOBAL CONFIGURATION 
            tokens_matched  = 0    # A normal python variable
            ''')

        actual_setup   = lfile.setup

        self.assertEqual(actual_setup, expected_setup)

    def test_luthorFile2_teardown(self):
        lfile = LuthorFile(p2)
        lfile.parse()

        expected_teardown = CodeSegment('''
            # Program Suffix
            print( "Total tokens matched: {}".format(tokens_matched))''')
        actual_teardown   = lfile.teardown

        self.assertEqual(actual_teardown, expected_teardown)


    def test_luthorFile2_patterns1(self):
        lfile = LuthorFile(p2)
        lfile.parse()

        expected_patterns = [
            LuthorREPattern('int_pattern', r'''\d+''',
                CodeSegment(''' 
                    RESULT = IntToken(MATCHED)
                    tokens_matched += 1''')
            ),
            LuthorREPattern('str_pattern', r'''([\"]|[^\"])+''',
                CodeSegment('''
                    RESULT = StrToken(MATCHED)
                    tokens_matched += 1
                ''')
            ),
            LuthorREPattern('ws_pattern', r'''\s''', None)
            ]
        actual_patterns   = lfile.patterns

        self.assertEqual(len(actual_patterns), len(expected_patterns))

    def test_luthorFile2_patterns2(self):
        lfile = LuthorFile(p2)
        lfile.parse()

        expected_patterns = [LuthorREPattern('int_pattern', r'''\d+''',
        CodeSegment(''' 
        RESULT = IntToken(MATCHED)
        tokens_matched += 1'''))]
        actual_patterns   = lfile.patterns

        for exp, act in zip(expected_patterns, actual_patterns):
            self.assertEqual(act, exp, 
"""
'{}' == '{}': {}, 
'{}' == '{}': {},
'{}' == '{}': {}""".format( act.name, exp.name, act.name == exp.name, 
                        act.pattern, exp.pattern, act.pattern == exp.pattern, 
                        act.code, exp.code, act.code == exp.code))

    def test_LuthorREPattern__eq__1(self):
        rep1 = LuthorREPattern('testname', 'testpattern', CodeSegment(''))
        self.assertEqual(rep1, rep1)

    def test_LuthorREPattern__eq__2(self):
        rep1 = LuthorREPattern('testname', 'testpattern', CodeSegment(''))
        rep2 = LuthorREPattern('testname', 'testpattern', CodeSegment(''))
        self.assertEqual(rep1, rep2)

    def test_LuthorREPattern__eq__3(self):
        rep1 = LuthorREPattern('testname', 'testpattern', CodeSegment(
        '''
for i in range(10):
    print(i)
'''))
        rep2 = LuthorREPattern('testname', 'testpattern', CodeSegment('''
        
    for i in range(10):
        print(i)'''))
        self.assertEqual(rep1, rep2)

